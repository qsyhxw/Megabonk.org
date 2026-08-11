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

    def test_local_browser_routes_resolve_static_html_files(self):
        self.assertEqual(
            check_production_health.browser_path(
                "/guides/builds/dicehead-best-build", local_html=True
            ),
            "/guides/builds/dicehead-best-build.html",
        )
        self.assertEqual(
            check_production_health.browser_path(
                "/guides/builds/roberto-best-build/", local_html=True
            ),
            "/guides/builds/roberto-best-build/index.html",
        )

    def test_health_workflow_has_failure_test_and_heartbeat_routes(self):
        source = (ROOT / ".github" / "workflows" / "production-health.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("check_production_health.py", source)
        self.assertIn("needs.production-health.result != 'success'", source)
        self.assertIn("send_test_email", source)
        self.assertIn("heartbeat", source)
        self.assertIn("send_automation_alert.py failure", source)
        self.assertIn("python -m http.server 4173", source)
        self.assertIn("--browser-base-url http://127.0.0.1:4173", source)
        self.assertIn("--local-html", source)
        self.assertIn("actions/checkout@v5", source)
        self.assertIn("actions/setup-python@v6", source)
        self.assertNotIn("actions/checkout@v4", source)
        self.assertNotIn("actions/setup-python@v5", source)

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

    def test_build_hub_is_connected_to_patch_and_entity_automations(self):
        patch = (ROOT / ".github" / "workflows" / "update-patch-notes.yml").read_text(encoding="utf-8")
        leaderboard = (ROOT / ".github" / "workflows" / "daily_scrape.yml").read_text(encoding="utf-8")
        entities = (ROOT / ".github" / "workflows" / "monitor-wiki-entities.yml").read_text(encoding="utf-8")
        self.assertIn("guides/builds/index.html", patch)
        self.assertIn("data-build-game-version", patch)
        self.assertIn("python scripts/build_builds_hub.py", leaderboard)
        self.assertIn("python scripts/build_builds_hub.py", entities)


    def test_legacy_leaderboard_workflow_is_removed(self):
        self.assertFalse(
            (ROOT / ".github" / "workflows" / "fetch-leaderboard.yml").exists()
        )


if __name__ == "__main__":
    unittest.main()
