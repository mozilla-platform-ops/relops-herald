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
    _event_date,
    _event_time,
    _where_summary,
    ingest_event,
    load_schema,
    route_pool,
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


class RoutingTests(unittest.TestCase):
    """Worker-pool routing and grouping (pure functions, no I/O)."""

    def _event(self, entities: list[dict]) -> dict:
        ev = _load("event-example-success.json")
        ev["entities"] = entities
        return ev

    def test_mac_role_routes_to_mac(self) -> None:
        route = route_pool("gecko_1_b_osx_1015")
        self.assertEqual(route.directory, Path("changelogs/worker-pool/mac"))
        self.assertEqual(route.rollup, "all-mac.md")

    def test_linux_role_routes_to_linux_hardware(self) -> None:
        route = route_pool("gecko_t_linux_2404_talos")
        self.assertEqual(
            route.directory, Path("changelogs/worker-pool/linux/hardware")
        )
        self.assertEqual(route.rollup, "all-linux.md")

    def test_windows_role_routes_to_windows_hardware(self) -> None:
        route = route_pool("gecko_1_b_win2022_hw")
        self.assertEqual(
            route.directory, Path("changelogs/worker-pool/windows/hardware")
        )
        self.assertEqual(route.rollup, "all-windows.md")

    def test_windows_azure_role_routes_to_azure(self) -> None:
        route = route_pool("gecko_1_b_win2022_azure")
        self.assertEqual(
            route.directory, Path("changelogs/worker-pool/windows/azure")
        )
        self.assertEqual(route.rollup, "all-windows-azure.md")

    def test_darwin_not_misread_as_windows(self) -> None:
        # "darwin" contains "win" but must classify as mac, not windows.
        route = route_pool("gecko_t_osx_darwin")
        self.assertEqual(route.directory, Path("changelogs/worker-pool/mac"))

    def test_no_os_signal_is_unroutable(self) -> None:
        self.assertIsNone(route_pool("generic_worker"))

    def test_event_date_and_time(self) -> None:
        self.assertEqual(_event_date("2026-07-16T10:16:36-07:00"), "Jul 16, 2026")
        self.assertEqual(_event_time("2026-07-16T10:16:36-07:00"), "10:16")
        self.assertEqual(_event_date("2026-05-21T15:00:00Z"), "May 21, 2026")
        # Unparseable input falls back gracefully to substrings, never raises.
        self.assertEqual(_event_date("2026-13-99T99:99:99"), "2026-13-99")
        self.assertEqual(_event_time("2026-13-99T99:99:99"), "99:99")

    def test_where_summary_badges_and_count(self) -> None:
        ev = self._event([
            {"type": "role", "id": "gecko_1_b_osx_1015", "files": ["a"]},
            {"type": "module", "id": "linux_packages", "files": ["b"]},
        ])
        # Platforms derived from all entity ids, in mac/linux/windows order.
        self.assertEqual(_where_summary(ev), "🍎 mac · 🐧 linux · 2")
        # No OS signal anywhere -> "shared".
        shared = self._event([{"type": "module", "id": "worker_runner", "files": ["c"]}])
        self.assertEqual(_where_summary(shared), "shared · 1")

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

    def test_success_event_routes_to_linux_hardware(self) -> None:
        event = _load("event-example-success.json")  # role, profile, module (linux talos)
        result = ingest_event(event, self.tmp)
        self.assertFalse(result.skipped_duplicate)
        self.assertTrue(result.all_events_written)

        # Per-pool changelog for the role, under linux/hardware.
        pool = self._read(
            "changelogs/worker-pool/linux/hardware/gecko_t_linux_2404_talos.md"
        )
        self.assertIn("# worker pool: gecko_t_linux_2404_talos", pool)
        self.assertIn(event["ai_summary"]["description"], pool)

        # Per-class rollup beside it.
        rollup = self._read("changelogs/worker-pool/linux/hardware/all-linux.md")
        self.assertIn("all linux hardware worker pools", rollup)
        # Rollup lists only the pool entity, not the module/profile entities
        # or their files (the module name still appears in the AI prose).
        self.assertIn("role: `gecko_t_linux_2404_talos`", rollup)
        self.assertNotIn("module: `generic_worker`", rollup)
        self.assertNotIn("modules/generic_worker/manifests/init.pp", rollup)

        # All-events firehose (a dir under changelogs/).
        firehose = self._read("changelogs/all-events/changelog.md")
        self.assertIn(event["ai_summary"]["headline"], firehose)

        # Non-pool entities get no dedicated changelog; other platforms untouched.
        self.assertFalse(self._exists("changelogs/module"))
        self.assertFalse(self._exists("changelogs/worker-pool/mac"))
        self.assertFalse(self._exists("changelogs/worker-pool/windows"))

    def test_module_only_change_lands_in_firehose_only(self) -> None:
        event = _load("event-example-success.json")
        event["entities"] = [
            {"type": "module", "id": "generic_worker",
             "files": ["modules/generic_worker/manifests/init.pp"]}
        ]
        result = ingest_event(event, self.tmp)
        self.assertTrue(result.all_events_written)
        self.assertEqual(result.all_written, [])  # no pool/rollup logs
        self.assertTrue(self._exists("changelogs/all-events/changelog.md"))
        self.assertFalse(self._exists("changelogs/worker-pool"))

    def test_ai_failure_event_renders_stub(self) -> None:
        event = _load("event-example-ai-failure.json")  # error-shaped ai_summary
        event["entities"] = [
            {"type": "role", "id": "gecko_1_b_osx_1015", "files": ["r.pp"]}
        ]
        ingest_event(event, self.tmp)
        entry = self._read("changelogs/worker-pool/mac/gecko_1_b_osx_1015.md")
        self.assertIn("AI summary unavailable", entry)
        self.assertIn(event["ai_summary"]["error"], entry)

    def test_role_and_hiera_merge_into_one_pool_changelog(self) -> None:
        event = _load("event-example-success.json")
        event["entities"] = [
            {"type": "role", "id": "gecko_1_b_osx_1015", "files": ["role.pp"]},
            {"type": "role-hiera", "id": "gecko_1_b_osx_1015", "files": ["hiera.yaml"]},
        ]
        result = ingest_event(event, self.tmp)
        # A single per-pool file, holding both files.
        self.assertEqual(len(result.pool_logs), 1)
        pool = self._read("changelogs/worker-pool/mac/gecko_1_b_osx_1015.md")
        self.assertIn("`role.pp`", pool)
        self.assertIn("`hiera.yaml`", pool)

    def test_firehose_groups_by_day(self) -> None:
        e1 = _load("event-example-success.json")
        e1["timestamp"] = "2026-07-16T09:00:00Z"
        e2 = copy.deepcopy(e1)
        e2["commit_sha"] = "1" * 40
        e2["commit_url"] = e1["commit_url"].replace(e1["commit_sha"], e2["commit_sha"])
        e2["timestamp"] = "2026-07-16T11:30:00Z"  # same day, later
        e3 = copy.deepcopy(e1)
        e3["commit_sha"] = "2" * 40
        e3["commit_url"] = e1["commit_url"].replace(e1["commit_sha"], e3["commit_sha"])
        e3["timestamp"] = "2026-07-17T08:00:00Z"  # next day
        for e in (e1, e2, e3):
            ingest_event(e, self.tmp)

        log = self._read("changelogs/all-events/changelog.md")
        # Two day headers, newest day on top.
        self.assertEqual(log.count("## Jul 16, 2026"), 1)
        self.assertEqual(log.count("## Jul 17, 2026"), 1)
        self.assertLess(log.index("## Jul 17, 2026"), log.index("## Jul 16, 2026"))
        # Same-day rows share one section; times only (no date) in the row.
        self.assertIn("| 09:00 |", log)
        self.assertIn("| 11:30 |", log)
        # Within the day, the later event is inserted above the earlier one.
        self.assertLess(log.index("| 11:30 |"), log.index("| 09:00 |"))

    def test_ingest_is_idempotent_per_commit(self) -> None:
        event = _load("event-example-success.json")
        ingest_event(event, self.tmp)
        before = self._read("changelogs/all-events/changelog.md")
        second = ingest_event(event, self.tmp)
        self.assertTrue(second.skipped_duplicate)
        self.assertEqual(before, self._read("changelogs/all-events/changelog.md"))

    def test_newest_entry_is_inserted_first(self) -> None:
        older = _load("event-example-success.json")
        newer = copy.deepcopy(older)
        newer["commit_sha"] = "1111111111111111111111111111111111111111"
        newer["commit_url"] = older["commit_url"].replace(older["commit_sha"], newer["commit_sha"])
        newer["commit_subject"] = "A newer change"
        ingest_event(older, self.tmp)
        ingest_event(newer, self.tmp)
        pool = self._read(
            "changelogs/worker-pool/linux/hardware/gecko_t_linux_2404_talos.md"
        )
        self.assertLess(
            pool.index("A newer change"),
            pool.index(older["commit_subject"]),
            "newer entry should appear above the older one",
        )


if __name__ == "__main__":
    unittest.main()
