import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WEAPON_PAGE = ROOT / "database" / "weapons" / "dexecutioner.html"
BUILD_PAGE = ROOT / "guides" / "builds" / "katana-dexecutioner-execute-melee.html"
SITEMAP = ROOT / "sitemap.xml"


class DexecutionerIntentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.weapon = WEAPON_PAGE.read_text(encoding="utf-8")
        cls.build = BUILD_PAGE.read_text(encoding="utf-8")
        cls.sitemap = SITEMAP.read_text(encoding="utf-8")

    def test_existing_metadata_stays_stable(self):
        title = re.search(r"<title>(.*?)</title>", self.weapon, re.S).group(1)
        self.assertEqual("Dexecutioner Guide – Unlock, Mechanics & Builds | Megabonk", title)
        self.assertIn('<div class="weapon-title">⚡ DEXECUTIONER</div>', self.weapon)
        self.assertIn('rel="canonical" href="https://megabonk.org/database/weapons/dexecutioner"', self.weapon)

    def test_quick_answer_precedes_stats_and_unlock(self):
        answer = self.weapon.index('id="execute-quick-answer"')
        stats = self.weapon.index('class="quick-stats"', answer)
        unlock = self.weapon.index("How to Unlock Dexectioner", stats)
        self.assertLess(answer, stats)
        self.assertLess(stats, unlock)
        self.assertIn("No, not in normal play.", self.weapon)

    def test_current_execute_rules_are_explicit(self):
        self.assertIn("2% Execute chance on each valid hit", self.weapon)
        self.assertIn("Bosses and Mini Bosses are immune", self.weapon)
        self.assertIn("no fixed Execute trigger cap", self.weapon)
        self.assertIn("The base chance remains 2% per valid hit", self.weapon)

    def test_troubleshooting_test_and_history_are_present(self):
        self.assertIn('id="execute-troubleshooting"', self.weapon)
        self.assertIn('id="execute-test"', self.weapon)
        self.assertIn('id="version-history"', self.weapon)
        self.assertIn("current v1.0.69 baseline", self.weapon)
        self.assertIn("v1.0.12", self.weapon)
        self.assertIn("Final Swarm", self.weapon)
        self.assertIn("official notes do not document a global 2% Execute-proc fix", self.weapon)

    def test_faq_covers_search_intent(self):
        questions = (
            "Is Execute bugged in Megabonk?",
            "Can Dexecutioner execute Bosses?",
            "Can Dexecutioner execute Mini Bosses?",
            "What is Dexecutioner's Execute chance?",
            "Do Quantity or Cooldown increase Execute chance?",
            "Why does Execute stop working in Final Swarm?",
            "How do I unlock Dexecutioner?",
        )
        for question in questions:
            self.assertIn(question, self.weapon)

    def test_weapon_and_build_pages_link_both_ways(self):
        self.assertIn('href="/guides/builds/katana-dexecutioner-execute-melee"', self.weapon)
        self.assertIn('href="/database/weapons/dexecutioner"', self.build)

    def test_sitemap_dates_are_current(self):
        for url in (
            "https://megabonk.org/database/weapons/dexecutioner.html",
            "https://megabonk.org/guides/builds/katana-dexecutioner-execute-melee.html",
        ):
            marker = f"<loc>{url}</loc>"
            start = self.sitemap.index(marker)
            self.assertIn("<lastmod>2026-07-29</lastmod>", self.sitemap[start:start + 180])


if __name__ == "__main__":
    unittest.main()