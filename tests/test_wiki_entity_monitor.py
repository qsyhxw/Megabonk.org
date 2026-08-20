import json
import unittest
from unittest import mock

from scripts import check_wiki_entities as monitor


class WikiEntityMonitorTests(unittest.TestCase):
    def test_request_json_retries_before_success(self):
        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def read(self, *_args):
                return json.dumps({"query": {"categorymembers": []}}).encode()

        with mock.patch.object(
            monitor.urllib.request,
            "urlopen",
            side_effect=[TimeoutError("slow"), FakeResponse()],
        ) as urlopen, mock.patch.object(monitor.time, "sleep") as sleep:
            payload = monitor.request_json({"action": "query"})

        self.assertIn("query", payload)
        self.assertEqual(urlopen.call_count, 2)
        sleep.assert_called_once_with(2)

    def test_complete_snapshot_allows_safe_source_fallback(self):
        snapshot = {
            "checkedAt": "2026-07-28T05:33:30Z",
            "entities": {
                entity_type: [f"sample-{entity_type}"]
                for entity_type in monitor.CATEGORIES
            },
        }
        result = monitor.unavailable_source_result(snapshot)
        self.assertFalse(result["files_changed"])
        self.assertFalse(result["source_available"])
        self.assertEqual(result["snapshot_checked_at"], snapshot["checkedAt"])

    def test_incomplete_snapshot_cannot_hide_source_failure(self):
        with self.assertRaisesRegex(
            monitor.SourceUnavailableError, "no complete previous snapshot"
        ):
            monitor.unavailable_source_result({"entities": {"characters": ["Fox"]}})


if __name__ == "__main__":
    unittest.main()
