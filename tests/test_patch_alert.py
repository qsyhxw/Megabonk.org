import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "patch_alert", ROOT / "scripts" / "send_patch_alert.py"
)
patch_alert = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = patch_alert
SPEC.loader.exec_module(patch_alert)


class PatchAlertTests(unittest.TestCase):
    def test_update_email_contains_version_sources_and_checklist(self):
        state = {
            "latest_version": "1.0.70",
            "versions": {
                "1.0.70": {
                    "title": "Megabonk V1.0.70",
                    "release_date": "2026-08-02",
                    "source_url": "https://store.steampowered.com/news/example",
                    "bullets": ["Fox Luck increased", "Added a new item"],
                }
            },
        }
        environment = {
            "PATCH_NEW_VERSIONS": "1.0.70",
            "PATCH_COMMIT_SHA": "abc123",
            "GITHUB_REPOSITORY": "qsyhxw/Megabonk.org",
            "GITHUB_RUN_ID": "42",
        }

        subject, body = patch_alert.build_update_email(state, environment)

        self.assertIn("V1.0.70", subject)
        self.assertIn("新版本", body)
        self.assertIn("Fox Luck increased", body)
        self.assertIn("/commit/abc123", body)
        self.assertIn("角色、被动与基础属性", body)

    def test_failure_email_links_to_workflow_run(self):
        subject, body = patch_alert.build_failure_email(
            {
                "GITHUB_REPOSITORY": "qsyhxw/Megabonk.org",
                "GITHUB_RUN_ID": "99",
            }
        )

        self.assertIn("失败", subject)
        self.assertIn("/actions/runs/99", body)

    def test_manual_test_email_confirms_configuration(self):
        subject, body = patch_alert.build_test_email(
            {"GITHUB_REPOSITORY": "qsyhxw/Megabonk.org", "GITHUB_RUN_ID": "101"}
        )
        self.assertIn("测试成功", subject)
        self.assertIn("/actions/runs/101", body)

    def test_missing_secrets_skips_without_smtp_connection(self):
        self.assertFalse(patch_alert.send_email("Subject", "Body", {}))


if __name__ == "__main__":
    unittest.main()
