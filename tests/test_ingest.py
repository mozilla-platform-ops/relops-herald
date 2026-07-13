"""Tests for the Herald ingester and the schema/example contract.

Run with:  python -m unittest discover -s tests
(no third-party test runner required; only 'jsonschema' is needed).
"""

from __future__ import annotations

import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from herald.ingest import (
    ValidationFailed,
    ingest_event,
    load_schema,
    validate_event,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = REPO_ROOT / "examples"


def _load(name: str) -> dict:
    return json.loads((EXAMPLES / name).read_text("utf-8"))


class SchemaContractTests(unittest.TestCase):
    """Both shipped examples must satisfy the schema; bad events must not."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = load_schema(REPO_ROOT)

    def test_success_example_validates(self) -> None:
        validate_event(_load("event-example-success.json"), self.schema)

    def test_ai_failure_example_validates(self) -> None:
        validate_event(_load("event-example-ai-failure.json"), self.schema)

    def test_both_description_and_error_null_is_rejected(self) -> None:
        bad = _load("event-example-success.json")
        bad["ai_summary"]["description"] = None
        bad["ai_summary"]["error"] = None
        with self.assertRaises(ValidationFailed):
            validate_event(bad, self.schema)

    def test_both_description_and_error_set_is_rejected(self) -> None:
        bad = _load("event-example-ai-failure.json")
        bad["ai_summary"]["description"] = "now set"
        bad["ai_summary"]["error"] = "also set"
        with self.assertRaises(ValidationFailed):
            validate_event(bad, self.schema)

    def test_missing_required_field_is_rejected(self) -> None:
        bad = _load("event-example-success.json")
        del bad["commit_sha"]
        with self.assertRaises(ValidationFailed):
            validate_event(bad, self.schema)

    def test_bad_entity_type_is_rejected(self) -> None:
        bad = _load("event-example-success.json")
        bad["entities"][0]["type"] = "not-a-real-type"
        with self.assertRaises(ValidationFailed):
            validate_event(bad, self.schema)


class IngestTests(unittest.TestCase):
    """Rendering into an isolated temp tree."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        # Only the schema needs to exist for validation; outputs are created.
        (self.tmp / "schema").mkdir()
        shutil.copy(
            REPO_ROOT / "schema/event.schema.json", self.tmp / "schema" / "event.schema.json"
        )
        self.addCleanup(shutil.rmtree, self.tmp)

    def _read(self, rel: str) -> str:
        return (self.tmp / rel).read_text("utf-8")

    def test_success_event_writes_all_entities_and_activity(self) -> None:
        event = _load("event-example-success.json")
        result = ingest_event(event, self.tmp)

        self.assertEqual(len(result.changelogs_written), len(event["entities"]))
        self.assertTrue(result.activity_written)
        self.assertFalse(result.skipped_duplicate)

        # One changelog file per entity, at the expected path.
        role = self._read("changelogs/role/gecko_t_linux_2404_talos.md")
        self.assertIn("# role: gecko_t_linux_2404_talos", role)
        self.assertIn(event["ai_summary"]["description"], role)
        self.assertIn(event["commit_sha"], role)  # anchor present

        activity = self._read("activity.md")
        self.assertIn(event["ai_summary"]["headline"], activity)
        self.assertIn(event["source_repo"], activity)

    def test_ai_failure_event_renders_stub(self) -> None:
        event = _load("event-example-ai-failure.json")
        ingest_event(event, self.tmp)

        entry = self._read("changelogs/module/macos_ntp.md")
        self.assertIn("AI summary unavailable", entry)
        self.assertIn(event["ai_summary"]["error"], entry)

        activity = self._read("activity.md")
        self.assertIn("AI summary unavailable", activity)

    def test_ingest_is_idempotent_per_commit(self) -> None:
        event = _load("event-example-success.json")
        ingest_event(event, self.tmp)
        first = self._read("activity.md")

        second_result = ingest_event(event, self.tmp)
        self.assertTrue(second_result.skipped_duplicate)
        self.assertEqual(first, self._read("activity.md"))  # unchanged

    def test_newest_entry_is_inserted_first(self) -> None:
        older = _load("event-example-success.json")
        newer = copy.deepcopy(older)
        newer["commit_sha"] = "1111111111111111111111111111111111111111"
        newer["commit_url"] = older["commit_url"].replace(older["commit_sha"], newer["commit_sha"])
        newer["commit_subject"] = "A newer change"
        newer["timestamp"] = "2026-06-01T00:00:00Z"

        ingest_event(older, self.tmp)
        ingest_event(newer, self.tmp)

        # commit_subject is the changelog entry heading; assert order there.
        entries = self._read("changelogs/role/gecko_t_linux_2404_talos.md")
        self.assertLess(
            entries.index("A newer change"),
            entries.index(older["commit_subject"]),
            "newer entry should appear above the older one",
        )


if __name__ == "__main__":
    unittest.main()
