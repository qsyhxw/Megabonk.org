import importlib.util
import unittest
from unittest import mock
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "sync_leaderboard.py"
SPEC = importlib.util.spec_from_file_location("sync_leaderboard", MODULE_PATH)
SYNC = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(SYNC)


class LeaderboardBuildSignalsTests(unittest.TestCase):
    def make_run(self, character, rank, kills, created, weapons, tomes):
        return {
            "character": character,
            "rank": rank,
            "kills": kills,
            "playerName": f"Player {rank}",
            "weapons": weapons,
            "tomes": tomes,
            "items": ["clover", "battery"],
            "map": "graveyard",
            "videoURL": f"https://example.com/{rank}",
            "submissionId": f"submission-{rank}",
            "createdAtIso": created,
            "updatedAtIso": created,
            "buildVersionLabel": "1.0.69",
        }

    def test_character_signals_use_independent_character_samples(self):
        runs = [
            self.make_run("fox", 1, 1000, "2026-07-01T00:00:00Z", ["bow"], ["luck"]),
            self.make_run("fox", 2, 900, "2026-07-02T00:00:00Z", ["bow"], ["luck"]),
            self.make_run("fox", 3, 800, "2026-07-03T00:00:00Z", ["revolver"], ["luck"]),
            self.make_run("calcium", 100, 700, "2026-07-04T00:00:00Z", ["bone"], ["xp"]),
            self.make_run("calcium", 101, 600, "2026-07-05T00:00:00Z", ["bone"], ["xp"]),
        ]
        signals = {entry["character"]: entry for entry in SYNC.build_character_signals(runs)}

        self.assertEqual(signals["fox"]["sampleSize"], 3)
        self.assertEqual(signals["fox"]["popularLoadouts"][0]["runs"], 2)
        self.assertEqual(signals["fox"]["mostRecentRun"]["rank"], 3)
        self.assertEqual(signals["calcium"]["sampleSize"], 2)
        self.assertEqual(signals["calcium"]["confidence"], "limited")

    def test_character_sample_is_capped(self):
        runs = [
            self.make_run("dicehead", rank, 1000 - rank, f"2026-07-{(rank % 28) + 1:02d}T00:00:00Z", ["dice"], ["luck"])
            for rank in range(1, 41)
        ]
        signal = SYNC.build_character_signals(runs)[0]
        self.assertEqual(signal["sampleSize"], SYNC.CHARACTER_SAMPLE_LIMIT)
        self.assertEqual(signal["availableRuns"], 40)
        self.assertEqual(signal["confidence"], "strong")

    def make_valid_records(self, count):
        return [
            {
                "rank": rank,
                "submissionId": f"submission-{rank}",
                "playerName": f"Player {rank}",
                "character": "fox",
                "kills": 1000 - rank,
                "createdAt": {"_seconds": 1_700_000_000 + rank},
            }
            for rank in range(1, count + 1)
        ]

    def test_same_version_rejects_more_than_thirty_percent_record_loss(self):
        previous = {
            "active_version": "1.0.65",
            "data": self.make_valid_records(652),
        }
        with self.assertRaisesRegex(ValueError, "minimum safe count is 457"):
            SYNC.validate(
                self.make_valid_records(456), previous, "1.0.65"
            )

    def test_same_version_accepts_exact_seventy_percent_ceiling(self):
        previous = {
            "active_version": "1.0.65",
            "data": self.make_valid_records(652),
        }
        SYNC.validate(self.make_valid_records(457), previous, "1.0.65")

    def test_version_change_uses_absolute_minimum_not_old_record_ratio(self):
        previous = {
            "active_version": "1.0.65",
            "data": self.make_valid_records(652),
        }
        SYNC.validate(self.make_valid_records(100), previous, "1.0.70")

    def test_unknown_version_is_treated_conservatively(self):
        previous = {
            "active_version": "1.0.65",
            "data": self.make_valid_records(652),
        }
        with self.assertRaisesRegex(ValueError, "Refusing to replace known-good data"):
            SYNC.validate(self.make_valid_records(456), previous, None)
    def test_top_values_breaks_ties_deterministically(self):
        records = [
            {"items": ["zeta", "alpha"]},
            {"items": ["alpha", "zeta"]},
        ]
        values = SYNC.top_values(records, "items")
        self.assertEqual([entry["id"] for entry in values], ["alpha", "zeta"])

    def test_crypt_key_is_excluded_from_build_item_signals(self):
        records = [
            {"items": ["cryptkey", "clover"]},
            {"items": ["cryptkey", "battery"]},
        ]
        values = SYNC.top_values(records, "items")
        self.assertEqual(
            [entry["id"] for entry in values],
            ["battery", "clover"],
        )
        summary = SYNC.summarize_run(
            {
                "items": ["cryptkey", "clover"],
                "weapons": [],
                "tomes": [],
            }
        )
        self.assertEqual(summary["items"], ["clover"])

    def test_http_fetch_retries_before_browser_fallback(self):
        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def read(self):
                return b"<html>leaderboard</html>"

        with mock.patch.object(
            SYNC.urllib.request,
            "urlopen",
            side_effect=[TimeoutError("temporary timeout"), FakeResponse()],
        ) as urlopen, mock.patch.object(SYNC.time, "sleep") as sleep:
            html = SYNC.fetch_source_html()

        self.assertEqual(html, "<html>leaderboard</html>")
        self.assertEqual(urlopen.call_count, 2)
        self.assertEqual(
            [call.kwargs["timeout"] for call in urlopen.call_args_list],
            [SYNC.HTTP_TIMEOUT_SECONDS, SYNC.HTTP_TIMEOUT_SECONDS],
        )
        sleep.assert_called_once_with(2)

    def test_browser_fallback_uses_bounded_payload_readiness(self):
        source = MODULE_PATH.read_text(encoding="utf-8")
        self.assertEqual(SYNC.HTTP_ATTEMPTS, 3)
        self.assertEqual(SYNC.HTTP_TIMEOUT_SECONDS, 25)
        self.assertEqual(SYNC.BROWSER_ATTEMPTS, 2)
        self.assertIn('wait_until="commit"', source)
        self.assertIn('page.wait_for_selector(', source)
        self.assertIn('{"image", "media", "font", "stylesheet"}', source)

    def test_workflow_installs_browser_fallback(self):
        workflow = (
            MODULE_PATH.parents[1] / ".github" / "workflows" / "daily_scrape.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("playwright==1.54.0", workflow)
        self.assertIn("playwright install --with-deps chromium", workflow)

if __name__ == "__main__":
    unittest.main()
