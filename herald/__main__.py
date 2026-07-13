"""CLI entrypoint: ``python -m herald --event <file> [--root .]``.

Reads a change event from a file (or stdin with ``--event -``), validates it,
and renders the changelog + activity outputs into the repo at ``--root``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .ingest import HeraldError, ingest_event


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="herald", description=__doc__)
    parser.add_argument(
        "--event",
        required=True,
        help="Path to the event JSON, or '-' to read from stdin.",
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Repo root containing schema/ and changelogs/ (default: cwd).",
    )
    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="Skip schema validation (not recommended).",
    )
    args = parser.parse_args(argv)

    raw = sys.stdin.read() if args.event == "-" else Path(args.event).read_text("utf-8")
    try:
        event = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"herald: invalid JSON: {exc}", file=sys.stderr)
        return 2

    try:
        result = ingest_event(event, Path(args.root), validate=not args.no_validate)
    except HeraldError as exc:
        print(f"herald: {exc}", file=sys.stderr)
        return 1

    if result.skipped_duplicate:
        print(f"herald: commit {event['commit_sha'][:12]} already ingested; nothing to do.")
    else:
        for path in result.changelogs_written:
            print(f"herald: wrote {path}")
        if result.activity_written:
            print("herald: updated activity.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
