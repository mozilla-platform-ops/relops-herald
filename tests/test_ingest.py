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
    classify_oses,
    ingest_event,
    load_schema,
    validate_event,
    worker_pool_ids,
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


class GroupingTests(unittest.TestCase):
    """OS derivation and worker-pool grouping (pure functions, no I/O)."""

    def _event(self, entities: list[dict]) -> dict:
        ev = _load("event-example-success.json")
        ev["entities"] = entities
        return ev

    def test_os_derived_from_role_name(self) -> None:
        self.assertEqual(
            classify_oses(self._event([{"type": "role", "id": "gecko_t_linux_2404_talos", "files": ["a"]}])),
            ["linux"],
        )
        self.assertEqual(
            classify_oses(self._event([{"type": "role", "id": "gecko_1_b_osx_1015", "files": ["a"]}])),
            ["macos"],
        )
        self.assertEqual(
            classify_oses(self._event([{"type": "role", "id": "win116424h2hw", "files": ["a"]}])),
            ["windows"],
        )

    def test_os_data_ids_classify(self) -> None:
        self.assertEqual(
            classify_oses(self._event([{"type": "os-data", "id": "Darwin", "files": ["a"]}])),
            ["macos"],
        )

    def test_no_os_signal_fans_out_to_all(self) -> None:
        # A shared module change has no OS in its id → all three OS logs.
        self.assertEqual(
            classify_oses(self._event([{"type": "module", "id": "generic_worker", "files": ["a"]}])),
            ["macos", "linux", "windows"],
        )

    def test_darwin_not_misread_as_windows(self) -> None:
        # "darwin" contains "win" but must not classify as windows.
        self.assertNotIn("windows", classify_oses(self._event([{"type": "os-data", "id": "Darwin", "files": ["a"]}])))

    def test_worker_pool_ids_merge_role_and_hiera(self) -> None:
        ev = self._event([
            {"type": "role", "id": "gecko_1_b_osx_1015", "files": ["r.pp"]},
            {"type": "role-hiera", "id": "gecko_1_b_osx_1015", "files": ["h.yaml"]},
            {"type": "module", "id": "generic_worker", "files": ["m.pp"]},
        ])
        self.assertEqual(worker_pool_ids(ev), ["gecko_1_b_osx_1015"])


class IngestTests(unittest.TestCase):
    """Rendering into an isolated temp tree."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "schema").mkdir()
        shutil.copy(
            REPO_ROOT / "schema/event.schema.json", self.tmp / "schema" / "event.schema.json"
        )
        self.addCleanup(shutil.rmtree, self.tmp)

    def _read(self, rel: str) -> str:
        return (self.tmp / rel).read_text("utf-8")

    def _exists(self, rel: str) -> bool:
        return (self.tmp / rel).exists()

    def test_success_event_fans_out_to_all_views(self) -> None:
        event = _load("event-example-success.json")  # role, profile, module (linux/talos)
        result = ingest_event(event, self.tmp)
        self.assertFalse(result.skipped_duplicate)
        self.assertTrue(result.activity_written)

        # Per-entity: profile + module get files; role/role-hiera do NOT.
        self.assertTrue(self._exists("changelogs/module/generic_worker.md"))
        self.assertTrue(self._exists("changelogs/profile/gecko_t_linux_2404_talos_generic_worker.md"))
        self.assertFalse(self._exists("changelogs/role/gecko_t_linux_2404_talos.md"))

        # Worker-pool view exists for the role.
        pool = self._read("changelogs/worker-pools/gecko_t_linux_2404_talos.md")
        self.assertIn("# worker pool: gecko_t_linux_2404_talos", pool)
        self.assertIn(event["ai_summary"]["description"], pool)

        # OS rollup: linux only (talos role has a linux signal).
        self.assertTrue(self._exists("changelogs/by-os/linux.md"))
        self.assertFalse(self._exists("changelogs/by-os/windows.md"))
        os_log = self._read("changelogs/by-os/linux.md")
        self.assertIn("Entities:", os_log)  # event-scoped entry lists entities

        # relops-all firehose.
        activity = self._read("activity.md")
        self.assertIn(event["ai_summary"]["headline"], activity)

    def test_no_os_change_fans_out_to_three_os_logs(self) -> None:
        event = _load("event-example-success.json")
        event["entities"] = [{"type": "module", "id": "generic_worker", "files": ["modules/generic_worker/manifests/init.pp"]}]
        ingest_event(event, self.tmp)
        for os_name in ("macos", "linux", "windows"):
            self.assertTrue(self._exists(f"changelogs/by-os/{os_name}.md"), os_name)
        # No worker pool for a module-only change.
        self.assertFalse((self.tmp / "changelogs/worker-pools").exists())

    def test_ai_failure_event_renders_stub(self) -> None:
        event = _load("event-example-ai-failure.json")  # module macos_ntp
        ingest_event(event, self.tmp)
        entry = self._read("changelogs/module/macos_ntp.md")
        self.assertIn("AI summary unavailable", entry)
        self.assertIn(event["ai_summary"]["error"], entry)

    def test_ingest_is_idempotent_per_commit(self) -> None:
        event = _load("event-example-success.json")
        ingest_event(event, self.tmp)
        before = self._read("activity.md")
        second = ingest_event(event, self.tmp)
        self.assertTrue(second.skipped_duplicate)
        self.assertEqual(before, self._read("activity.md"))

    def test_newest_entry_is_inserted_first(self) -> None:
        older = _load("event-example-success.json")
        newer = copy.deepcopy(older)
        newer["commit_sha"] = "1111111111111111111111111111111111111111"
        newer["commit_url"] = older["commit_url"].replace(older["commit_sha"], newer["commit_sha"])
        newer["commit_subject"] = "A newer change"
        ingest_event(older, self.tmp)
        ingest_event(newer, self.tmp)
        pool = self._read("changelogs/worker-pools/gecko_t_linux_2404_talos.md")
        self.assertLess(
            pool.index("A newer change"),
            pool.index(older["commit_subject"]),
            "newer entry should appear above the older one",
        )


if __name__ == "__main__":
    unittest.main()
