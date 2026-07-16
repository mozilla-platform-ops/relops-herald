"""Herald ingester / renderer.

Turns a validated change event (see ``schema/event.schema.json``) into Markdown,
fanning each event out into a small set of views under ``changelogs/``:

* ``changelogs/all-events/changelog.md`` — the firehose: one table row per
  change we collect, across every reporter repo.
* ``changelogs/worker-pool/<platform>/[<class>/]<pool>.md`` — one changelog per
  worker pool. A *worker pool* is the role name; ``role`` and ``role-hiera``
  entities that share an id are merged into it. Pools are routed by platform:
    - ``mac/`` — mac is all hardware, so no class subdir.
    - ``linux/hardware/`` — ronin_puppet linux workers are all hardware for now
      (``linux/gcp/`` is reserved for a future cloud reporter).
    - ``windows/hardware/`` — windows workers, unless the role name contains
      ``azure`` → ``windows/azure/``.
* ``changelogs/worker-pool/<platform>/[<class>/]all-<...>.md`` — a per-class
  rollup ("all mac", "all linux", ...) sitting beside that class's pools.

Changes that don't name a worker pool (module / profile / os-data / common-data)
are recorded in the all-events firehose only, for now.

All outputs are **newest-first** and **idempotent**: re-ingesting the same
commit is a no-op (each entry carries a ``<!-- herald:commit=<sha> -->`` anchor,
which we check before writing).

The module has no dependency on GitHub Actions; a workflow just needs to hand
the ``client_payload`` to :func:`ingest_event`. It is also runnable as a CLI:

    python -m herald --event examples/event-example-success.json --root .
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

try:
    from jsonschema import Draft202012Validator
except ImportError as exc:  # pragma: no cover - dependency guard
    raise ImportError(
        "herald requires the 'jsonschema' package (pip install jsonschema)"
    ) from exc

# Repo layout, relative to the repo root passed into ingest_event().
SCHEMA_REL = Path("schema/event.schema.json")
CHANGELOGS_DIR = Path("changelogs")
WORKER_POOL_DIR = CHANGELOGS_DIR / "worker-pool"
ALL_EVENTS_FILE = CHANGELOGS_DIR / "all-events" / "changelog.md"

# Entity types that identify a worker pool (the "role level"). role + role-hiera
# sharing an id merge into a single per-pool changelog.
WORKER_POOL_TYPES = {"role", "role-hiera"}

# Sentinel comments marking where new content is inserted (newest-first).
ENTRIES_MARKER = "<!-- HERALD:ENTRIES -->"
ROWS_MARKER = "<!-- HERALD:ROWS -->"


class HeraldError(Exception):
    """Base class for Herald errors."""


class ValidationFailed(HeraldError):
    """Raised when an event does not satisfy the schema."""


@dataclass(frozen=True)
class PoolRoute:
    """Where a worker pool's changelogs live, and how to label them.

    ``directory`` is relative to the repo root; ``rollup`` is the filename of the
    per-class "all-*" rollup that sits beside the pools in that directory.
    """

    directory: Path
    rollup: str
    label: str


@dataclass
class IngestResult:
    """What a single ingest touched."""

    pool_logs: list[Path] = field(default_factory=list)
    rollup_logs: list[Path] = field(default_factory=list)
    all_events_written: bool = False
    skipped_duplicate: bool = False

    @property
    def all_written(self) -> list[Path]:
        return self.pool_logs + self.rollup_logs


def load_schema(root: Path) -> dict[str, Any]:
    """Load the event JSON Schema from ``<root>/schema/event.schema.json``."""
    return json.loads((root / SCHEMA_REL).read_text(encoding="utf-8"))


def validate_event(event: dict[str, Any], schema: dict[str, Any]) -> None:
    """Validate ``event`` against ``schema``; raise ValidationFailed on error.

    All schema errors are collected and reported together so a bad event
    surfaces every problem at once rather than one-at-a-time.
    """
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(event), key=lambda e: list(e.path))
    if errors:
        detail = "\n".join(
            f"  - {'/'.join(str(p) for p in e.path) or '<root>'}: {e.message}"
            for e in errors
        )
        raise ValidationFailed(f"event failed schema validation:\n{detail}")


# --- OS classification & worker-pool routing ------------------------------


# "win" as a delimited token (start or after a non-letter): matches win2022,
# win10, win_hw, win116424h2hw — but NOT "darwin", where 'win' follows a letter.
_WIN_TOKEN = re.compile(r"(?:^|[^a-z])win")


def _oses_for_id(entity_id: str) -> set[str]:
    """Derive the OS(es) an entity id implies from its naming (best effort)."""
    s = entity_id.lower()
    oses: set[str] = set()
    if "osx" in s or "mac" in s or "darwin" in s:
        oses.add("macos")
    if "linux" in s or "debian" in s or "ubuntu" in s:
        oses.add("linux")
    if "windows" in s or _WIN_TOKEN.search(s):
        oses.add("windows")
    return oses


def route_pool(pool_id: str) -> PoolRoute | None:
    """Route a worker-pool id to its platform/class directory + rollup.

    Returns ``None`` when the id carries no OS signal (we can't place it, so it
    lives in the all-events firehose only). Precedence mac > linux > windows for
    the (rare) case an id matches more than one.
    """
    s = pool_id.lower()
    oses = _oses_for_id(pool_id)
    if "macos" in oses:
        # mac is all hardware — no class subdir.
        return PoolRoute(WORKER_POOL_DIR / "mac", "all-mac.md", "mac")
    if "linux" in oses:
        # ronin_puppet linux workers are all hardware for now; gcp reserved.
        return PoolRoute(
            WORKER_POOL_DIR / "linux" / "hardware", "all-linux.md", "linux hardware"
        )
    if "windows" in oses:
        if "azure" in s:
            return PoolRoute(
                WORKER_POOL_DIR / "windows" / "azure",
                "all-windows-azure.md",
                "windows Azure",
            )
        return PoolRoute(
            WORKER_POOL_DIR / "windows" / "hardware",
            "all-windows.md",
            "windows hardware",
        )
    return None


def worker_pool_ids(event: dict[str, Any]) -> list[str]:
    """The worker pools (role level) this event touches, sorted and deduped."""
    return sorted(
        {e["id"] for e in event["entities"] if e["type"] in WORKER_POOL_TYPES}
    )


def _files_for(event: dict[str, Any], predicate: Callable) -> list[str]:
    return sorted(
        {f for e in event["entities"] if predicate(e) for f in e["files"]}
    )


# --- rendering ------------------------------------------------------------


def _short_sha(sha: str) -> str:
    return sha[:12]


def _commit_link(event: dict[str, Any]) -> str:
    return f"[`{_short_sha(event['commit_sha'])}`]({event['commit_url']})"


def _summary_text(ai: dict[str, Any]) -> str:
    """The narrative body for an entry, handling the AI-failure case."""
    if ai.get("description"):
        return ai["description"]
    return f"_AI summary unavailable: {ai.get('error') or 'unknown error'}_"


def _entry(
    event: dict[str, Any],
    files: list[str],
    *,
    entities: list[dict[str, Any]] | None = None,
) -> str:
    """Core changelog entry: heading, meta, summary, (entities,) files, tags.

    ``entities`` lists the entities to show under an "Entities:" section; pass
    ``None`` to omit that section (per-pool entries don't need it).
    """
    ai = event["ai_summary"]
    meta = [_commit_link(event), event["timestamp"], f"@{event['actor']}"]
    if event.get("pr_number"):
        meta.append(f"[PR #{event['pr_number']}]({event['pr_url']})")

    lines = [
        f"<!-- herald:commit={event['commit_sha']} -->",
        f"## {event['commit_subject']}",
        "",
        " · ".join(meta),
        "",
        _summary_text(ai),
        "",
    ]
    if entities is not None:
        lines.append("Entities:")
        lines += [f"  - {e['type']}: `{e['id']}`" for e in entities]
        lines.append("")
    lines.append("Files:")
    lines += [f"  - `{f}`" for f in files]
    tags = ai.get("tags") or []
    if tags:
        lines += ["", "Tags: " + " ".join(f"`{t}`" for t in tags)]
    return "\n".join(lines) + "\n"


def render_pool_entry(event: dict[str, Any], pool_id: str) -> str:
    """Per-worker-pool entry: files from role/role-hiera entities for this id."""
    files = _files_for(
        event, lambda e: e["type"] in WORKER_POOL_TYPES and e["id"] == pool_id
    )
    return _entry(event, files)


def render_rollup_entry(event: dict[str, Any], pool_ids: list[str]) -> str:
    """Per-class rollup entry, scoped to the pools in that class."""
    ids = set(pool_ids)
    pred = lambda e: e["type"] in WORKER_POOL_TYPES and e["id"] in ids
    files = _files_for(event, pred)
    entities = [e for e in event["entities"] if pred(e)]
    return _entry(event, files, entities=entities)


def render_all_events_row(event: dict[str, Any]) -> str:
    """Render one all-events firehose table row for the whole event."""
    ai = event["ai_summary"]
    entities = ", ".join(f"{e['type']}:{e['id']}" for e in event["entities"])
    if ai.get("headline"):
        change = ai["headline"]
    elif ai.get("description"):
        change = event["commit_subject"]
    else:
        change = f"⚠️ {event['commit_subject']} (AI summary unavailable)"
    # Escape pipes so cell content can't break the table.
    change = change.replace("|", "\\|")
    entities = entities.replace("|", "\\|")
    # The commit cell carries a hidden anchor so rows are idempotent per commit,
    # just like the changelog entries. The comment renders invisibly.
    commit_cell = f"{_commit_link(event)}<!-- herald:commit={event['commit_sha']} -->"
    return (
        f"| {event['timestamp']} | {event['source_repo']} | {entities} "
        f"| {change} | {commit_cell} |\n"
    )


# --- file headers ---------------------------------------------------------


def _pool_header(pool_id: str, label: str) -> str:
    return (
        f"# worker pool: {pool_id}\n\n"
        f"Changelog for the `{pool_id}` {label} worker pool (role + role Hiera), "
        f"maintained by RelOps Herald. Newest entries first.\n\n"
        f"{ENTRIES_MARKER}\n"
    )


def _rollup_header(label: str) -> str:
    return (
        f"# all {label} worker pools\n\n"
        f"Every change across all {label} worker pools, maintained by RelOps "
        f"Herald. Newest first.\n\n"
        f"{ENTRIES_MARKER}\n"
    )


def _all_events_header() -> str:
    return (
        "# All events\n\n"
        "Every change we collect across all reporter repos, maintained by "
        "RelOps Herald. Newest first.\n\n"
        "| When (UTC) | Repo | Entities | Change | Commit |\n"
        "|---|---|---|---|---|\n"
        f"{ROWS_MARKER}\n"
    )


# --- writing --------------------------------------------------------------


def _insert_after_marker(existing: str, marker: str, block: str) -> str:
    """Insert ``block`` immediately after the line containing ``marker``."""
    idx = existing.index(marker) + len(marker)
    # Skip the newline that follows the marker so the block lands on its own line.
    if idx < len(existing) and existing[idx] == "\n":
        idx += 1
    return existing[:idx] + block + existing[idx:]


def _write_newest_first(
    path: Path, header: str, marker: str, block: str, commit_sha: str
) -> bool:
    """Insert ``block`` newest-first into ``path``; create it from ``header`` if
    missing. Returns False (no write) if ``commit_sha`` is already recorded.
    """
    if path.exists():
        existing = path.read_text(encoding="utf-8")
        if f"herald:commit={commit_sha}" in existing:
            return False
        if marker not in existing:
            raise HeraldError(f"{path} is missing the {marker} marker")
    else:
        existing = header
        path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(_insert_after_marker(existing, marker, block), encoding="utf-8")
    return True


def ingest_event(
    event: dict[str, Any], root: Path, *, validate: bool = True
) -> IngestResult:
    """Validate and render one change event into the tree at ``root``.

    Fans out into per-worker-pool changelogs, per-class rollups, and the
    all-events firehose. Idempotent per ``commit_sha``.
    """
    root = Path(root)
    if validate:
        validate_event(event, load_schema(root))

    sha = event["commit_sha"]
    result = IngestResult()

    # Group the touched worker pools by the class directory they route to, so
    # each class's per-pool logs and its rollup are written together. Pools with
    # no OS signal are skipped here (they still land in the all-events firehose).
    by_route: dict[PoolRoute, list[str]] = {}
    for pool_id in worker_pool_ids(event):
        route = route_pool(pool_id)
        if route is not None:
            by_route.setdefault(route, []).append(pool_id)

    for route, pool_ids in by_route.items():
        for pool_id in pool_ids:
            path = root / route.directory / f"{pool_id}.md"
            if _write_newest_first(
                path,
                _pool_header(pool_id, route.label),
                ENTRIES_MARKER,
                render_pool_entry(event, pool_id),
                sha,
            ):
                result.pool_logs.append(path)

        rollup_path = root / route.directory / route.rollup
        if _write_newest_first(
            rollup_path,
            _rollup_header(route.label),
            ENTRIES_MARKER,
            render_rollup_entry(event, pool_ids),
            sha,
        ):
            result.rollup_logs.append(rollup_path)

    # All-events firehose.
    result.all_events_written = _write_newest_first(
        root / ALL_EVENTS_FILE,
        _all_events_header(),
        ROWS_MARKER,
        render_all_events_row(event),
        sha,
    )

    # If nothing was written, this commit was already ingested everywhere.
    result.skipped_duplicate = (
        not result.all_written and not result.all_events_written
    )
    return result
