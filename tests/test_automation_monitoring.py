import unittest
from pathlib import Path
from unittest import mock

from scripts import check_production_health
from scripts import send_automation_alert


ROOT = Path(__file__).resolve().parents[1]


class AutomationAlertTests(unittest.TestCase):
    def test_missing_email_secrets_are_a_hard_failure(self):
        with self.assertRaisesRegex(RuntimeError, "Missing required GitHub Secrets"):
            send_automation_alert.send_email("subject", "body", {})

    def test_failure_email_contains_workflow_and_run(self):
        environment = {
            "GITHUB_SERVER_URL": "https://github.com",
            "GITHUB_REPOSITORY": "qsyhxw/Megabonk.org",
            "GITHUB_RUN_ID": "123",
            "AUTOMATION_DETAILS": "Production Build signals failed.",
        }
        subject, body = send_automation_alert.build_message(
            "failure", "Production Site Health", environment
        )
        self.assertIn("Production Site Health", subject)
        self.assertIn("actions/runs/123", body)
        self.assertIn("Production Build signals failed", body)

    @mock.patch("scripts.send_automation_alert.smtplib.SMTP_SSL")
    def test_configured_email_logs_in_and_sends(self, smtp_ssl):
        environment = {
            "GMAIL_USERNAME": "qsyhxw@gmail.com",
            "GMAIL_APP_PASSWORD": "abcd efgh",
            "PATCH_ALERT_EMAIL": "qsyhxw@gmail.com",
        }
        send_automation_alert.send_email("subject", "body", environment)
        smtp = smtp_ssl.return_value.__enter__.return_value
        smtp.login.assert_called_once_with("qsyhxw@gmail.com", "abcdefgh")
        smtp.send_message.assert_called_once()


class ProductionHealthTests(unittest.TestCase):
    def test_monitor_covers_all_21_canonical_build_pages(self):
        paths = check_production_health.canonical_build_paths()
        self.assertEqual(len(paths), 21)
        self.assertEqual(len(paths), len(set(paths)))
        self.assertIn("/guides/builds/dicehead-best-build", paths)
        self.assertIn("/guides/builds/roberto-best-build/", paths)

    def test_health_workflow_has_failure_test_and_heartbeat_routes(self):
        source = (ROOT / ".github" / "workflows" / "production-health.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("check_production_health.py", source)
        self.assertIn("needs.production-health.result != 'success'", source)
        self.assertIn("send_test_email", source)
        self.assertIn("heartbeat", source)
        self.assertIn("send_automation_alert.py failure", source)

    def test_all_automations_have_independent_failure_email_jobs(self):
        workflows = (
            "daily_scrape.yml",
            "update-player-count.yml",
            "update-patch-notes.yml",
            "monitor-wiki-entities.yml",
            "build_tr.yml",
        )
        for workflow in workflows:
            with self.subTest(workflow=workflow):
                source = (ROOT / ".github" / "workflows" / workflow).read_text(
                    encoding="utf-8"
                )
                self.assertIn("notify-failure:", source)
                self.assertIn("always()", source)
                self.assertIn("send_automation_alert.py failure", source)

    def test_legacy_leaderboard_workflow_is_removed(self):
        self.assertFalse(
            (ROOT / ".github" / "workflows" / "fetch-leaderboard.yml").exists()
        )


if __name__ == "__main__":
    unittest.main()
