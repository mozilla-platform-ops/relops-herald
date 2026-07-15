"""Herald ingester / renderer.

Turns a validated change event (see ``schema/event.schema.json``) into Markdown,
fanning each event out into several views:

* ``activity.md`` — the relops-all firehose (one table row per change)
* ``changelogs/worker-pools/<id>.md`` — per worker pool (the *role level*):
  merges the ``role`` and ``role-hiera`` entities that share an id
* ``changelogs/by-os/<macos|linux|windows>.md`` — per-OS rollup. OS is derived
  from entity ids; a change with no OS-specific entity fans out to all three.
* ``changelogs/<type>/<id>.md`` — per-entity changelog for the remaining entity
  types (``module``, ``profile``, ``os-data``, ``common-data``)

All outputs are **newest-first** and **idempotent**: re-ingesting the same
commit is a no-op (each entry carries a ``<!-- herald:commit=<sha> -->`` anchor,
which we check before writing).

The module has no dependency on GitHub Actions; a workflow just needs to hand
the ``client_payload`` to :func:`ingest_event`. It is also runnable as a CLI:

    python -m herald --event examples/event-example-success.json --root .
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator
except ImportError as exc:  # pragma: no cover - dependency guard
    raise ImportError(
        "herald requires the 'jsonschema' package (pip install jsonschema)"
    ) from exc

# Repo layout, relative to the repo root passed into ingest_event().
SCHEMA_REL = Path("schema/event.schema.json")
CHANGELOGS_DIR = Path("changelogs")
OS_DIR = CHANGELOGS_DIR / "by-os"
WORKER_POOL_DIR = CHANGELOGS_DIR / "worker-pools"
ACTIVITY_FILE = "activity.md"

# Entity types that get their own per-entity changelog. role / role-hiera are
# excluded because they roll up into the per-worker-pool view instead.
PER_ENTITY_TYPES = {"module", "profile", "os-data", "common-data"}
# Entity types that identify a worker pool (the "role level").
WORKER_POOL_TYPES = {"role", "role-hiera"}

# OS logs, in a stable order. A change with no OS-specific entity fans out to all.
ALL_OSES = ("macos", "linux", "windows")

# Sentinel comments marking where new content is inserted (newest-first).
ENTRIES_MARKER = "<!-- HERALD:ENTRIES -->"
ROWS_MARKER = "<!-- HERALD:ROWS -->"


class HeraldError(Exception):
    """Base class for Herald errors."""


class ValidationFailed(HeraldError):
    """Raised when an event does not satisfy the schema."""


@dataclass
class IngestResult:
    """What a single ingest touched."""

    entity_logs: list[Path] = field(default_factory=list)
    worker_pool_logs: list[Path] = field(default_factory=list)
    os_logs: list[Path] = field(default_factory=list)
    activity_written: bool = False
    skipped_duplicate: bool = False

    @property
    def all_written(self) -> list[Path]:
        return self.entity_logs + self.worker_pool_logs + self.os_logs


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


# --- OS classification & grouping ----------------------------------------


def _oses_for_id(entity_id: str) -> set[str]:
    """Derive the OS(es) an entity id implies from its naming (best effort)."""
    s = entity_id.lower()
    oses: set[str] = set()
    if "osx" in s or "mac" in s or "darwin" in s:
        oses.add("macos")
    if "linux" in s or "debian" in s or "ubuntu" in s:
        oses.add("linux")
    if s.startswith("win") or "windows" in s:
        oses.add("windows")
    return oses


def classify_oses(event: dict[str, Any]) -> list[str]:
    """OS logs this event belongs in. No OS signal → all three (fan out)."""
    found: set[str] = set()
    for entity in event["entities"]:
        found |= _oses_for_id(entity["id"])
    return [os_name for os_name in ALL_OSES if os_name in found] or list(ALL_OSES)


def worker_pool_ids(event: dict[str, Any]) -> list[str]:
    """The worker pools (role level) this event touches, sorted and deduped."""
    return sorted(
        {e["id"] for e in event["entities"] if e["type"] in WORKER_POOL_TYPES}
    )


def _files_for(event: dict[str, Any], predicate) -> list[str]:
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


def _entry(event: dict[str, Any], files: list[str], *, show_entities: bool) -> str:
    """Core changelog entry: heading, meta, summary, (entities,) files, tags."""
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
    if show_entities:
        lines.append("Entities:")
        lines += [f"  - {e['type']}: `{e['id']}`" for e in event["entities"]]
        lines.append("")
    lines.append("Files:")
    lines += [f"  - `{f}`" for f in files]
    tags = ai.get("tags") or []
    if tags:
        lines += ["", "Tags: " + " ".join(f"`{t}`" for t in tags)]
    return "\n".join(lines) + "\n"


def render_entity_entry(event: dict[str, Any], entity: dict[str, Any]) -> str:
    """Per-entity entry, scoped to that entity's files."""
    return _entry(event, sorted(entity["files"]), show_entities=False)


def render_worker_pool_entry(event: dict[str, Any], pool_id: str) -> str:
    """Per-worker-pool entry: files from role/role-hiera entities for this id."""
    files = _files_for(
        event, lambda e: e["type"] in WORKER_POOL_TYPES and e["id"] == pool_id
    )
    return _entry(event, files, show_entities=False)


def render_event_entry(event: dict[str, Any]) -> str:
    """Commit-scoped entry (all entities + files) for the OS rollups."""
    files = _files_for(event, lambda e: True)
    return _entry(event, files, show_entities=True)


def render_activity_row(event: dict[str, Any]) -> str:
    """Render one central-activity table row for the whole event."""
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
    # The commit cell carries a hidden anchor so activity rows are idempotent
    # per commit, just like the changelog entries. The comment renders invisibly.
    commit_cell = f"{_commit_link(event)}<!-- herald:commit={event['commit_sha']} -->"
    return (
        f"| {event['timestamp']} | {event['source_repo']} | {entities} "
        f"| {change} | {commit_cell} |\n"
    )


# --- file headers ---------------------------------------------------------


def _entity_file_header(entity: dict[str, Any]) -> str:
    return (
        f"# {entity['type']}: {entity['id']}\n\n"
        f"Changelog for `{entity['id']}` ({entity['type']}), maintained by "
        f"RelOps Herald. Newest entries first.\n\n"
        f"{ENTRIES_MARKER}\n"
    )


def _worker_pool_header(pool_id: str) -> str:
    return (
        f"# worker pool: {pool_id}\n\n"
        f"Changelog for the `{pool_id}` worker pool (role + role Hiera), "
        f"maintained by RelOps Herald. Newest entries first.\n\n"
        f"{ENTRIES_MARKER}\n"
    )


def _os_file_header(os_name: str) -> str:
    return (
        f"# OS activity: {os_name}\n\n"
        f"All changes affecting {os_name} workers, maintained by RelOps Herald. "
        f"Newest first. Changes with no OS-specific entity appear in every OS "
        f"log.\n\n{ENTRIES_MARKER}\n"
    )


def _activity_header() -> str:
    return (
        "# Activity (relops-all)\n\n"
        "Every change across all reporter repos, maintained by RelOps Herald. "
        "Newest first.\n\n"
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

    Fans out into per-entity, per-worker-pool, per-OS, and relops-all views.
    Idempotent per ``commit_sha``.
    """
    root = Path(root)
    if validate:
        validate_event(event, load_schema(root))

    sha = event["commit_sha"]
    result = IngestResult()

    # Per-entity changelogs (module / profile / os-data / common-data).
    for entity in event["entities"]:
        if entity["type"] not in PER_ENTITY_TYPES:
            continue
        path = root / CHANGELOGS_DIR / entity["type"] / f"{entity['id']}.md"
        if _write_newest_first(
            path,
            _entity_file_header(entity),
            ENTRIES_MARKER,
            render_entity_entry(event, entity),
            sha,
        ):
            result.entity_logs.append(path)

    # Per-worker-pool (role level): role + role-hiera merged by id.
    for pool_id in worker_pool_ids(event):
        path = root / WORKER_POOL_DIR / f"{pool_id}.md"
        if _write_newest_first(
            path,
            _worker_pool_header(pool_id),
            ENTRIES_MARKER,
            render_worker_pool_entry(event, pool_id),
            sha,
        ):
            result.worker_pool_logs.append(path)

    # Per-OS rollups.
    for os_name in classify_oses(event):
        path = root / OS_DIR / f"{os_name}.md"
        if _write_newest_first(
            path,
            _os_file_header(os_name),
            ENTRIES_MARKER,
            render_event_entry(event),
            sha,
        ):
            result.os_logs.append(path)

    # relops-all firehose.
    result.activity_written = _write_newest_first(
        root / ACTIVITY_FILE,
        _activity_header(),
        ROWS_MARKER,
        render_activity_row(event),
        sha,
    )

    # If nothing was written, this commit was already ingested everywhere.
    result.skipped_duplicate = not result.all_written and not result.activity_written
    return result
