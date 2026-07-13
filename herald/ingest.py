"""Herald ingester / renderer.

Turns a validated change event (see ``schema/event.schema.json``) into Markdown:

* one changelog file per entity at ``changelogs/<type>/<id>.md``
* a row in the central ``activity.md`` stream

Both outputs are **newest-first** and **idempotent**: re-ingesting the same
commit is a no-op (each entry carries a ``<!-- herald:commit=<sha> -->`` anchor,
which we check before writing).

The module has no dependency on GitHub Actions; a workflow just needs to hand
the ``client_payload`` to :func:`ingest_event`. It is also runnable as a CLI:

    python -m herald --event examples/event-example-success.json --root .
"""

from __future__ import annotations

import json
from dataclasses import dataclass
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
CHANGELOGS_DIR = "changelogs"
ACTIVITY_FILE = "activity.md"

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

    changelogs_written: list[Path]
    activity_written: bool
    skipped_duplicate: bool


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


def render_entity_entry(event: dict[str, Any], entity: dict[str, Any]) -> str:
    """Render one changelog entry for a single entity."""
    ai = event["ai_summary"]
    meta_bits = [_commit_link(event), event["timestamp"], f"@{event['actor']}"]
    if event.get("pr_number"):
        meta_bits.append(f"[PR #{event['pr_number']}]({event['pr_url']})")

    files = "\n".join(f"  - `{f}`" for f in entity["files"])
    lines = [
        f"<!-- herald:commit={event['commit_sha']} -->",
        f"## {event['commit_subject']}",
        "",
        " · ".join(meta_bits),
        "",
        _summary_text(ai),
        "",
        "Files:",
        files,
    ]
    tags = ai.get("tags") or []
    if tags:
        lines += ["", "Tags: " + " ".join(f"`{t}`" for t in tags)]
    return "\n".join(lines) + "\n"


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


def _entity_file_header(entity: dict[str, Any]) -> str:
    return (
        f"# {entity['type']}: {entity['id']}\n\n"
        f"Changelog for `{entity['id']}` ({entity['type']}), maintained by "
        f"RelOps Herald. Newest entries first.\n\n"
        f"{ENTRIES_MARKER}\n"
    )


def _activity_header() -> str:
    return (
        "# Activity\n\n"
        "Central activity log across all reporter repos, maintained by RelOps "
        "Herald. Newest first.\n\n"
        "| When (UTC) | Repo | Entities | Change | Commit |\n"
        "|---|---|---|---|---|\n"
        f"{ROWS_MARKER}\n"
    )


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

    Writes/updates one changelog per entity plus the central activity log.
    Idempotent per ``commit_sha``.
    """
    root = Path(root)
    if validate:
        validate_event(event, load_schema(root))

    sha = event["commit_sha"]
    changelogs_written: list[Path] = []
    for entity in event["entities"]:
        path = root / CHANGELOGS_DIR / entity["type"] / f"{entity['id']}.md"
        if _write_newest_first(
            path,
            _entity_file_header(entity),
            ENTRIES_MARKER,
            render_entity_entry(event, entity),
            sha,
        ):
            changelogs_written.append(path)

    activity_written = _write_newest_first(
        root / ACTIVITY_FILE,
        _activity_header(),
        ROWS_MARKER,
        render_activity_row(event),
        sha,
    )

    return IngestResult(
        changelogs_written=changelogs_written,
        activity_written=activity_written,
        # If nothing was written, this commit was already ingested everywhere.
        skipped_duplicate=not changelogs_written and not activity_written,
    )
