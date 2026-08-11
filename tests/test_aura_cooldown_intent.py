from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
PAGES = {
    "aura": ROOT / "database" / "weapons" / "aura.html",
    "cooldown": ROOT / "database" / "tomes" / "cooldown-tome.html",
    "stats": ROOT / "guides" / "stats" / "index.html",
}


class AuraCooldownIntentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = {name: path.read_text(encoding="utf-8") for name, path in PAGES.items()}

    def test_all_three_pages_give_the_same_direct_answer(self):
        required = (
            "Does Cooldown Tome Work with Aura?",
            "global Attack Speed stat",
            "damage ticks more often",
            "Size",
            "Quantity",
        )
        for name, source in self.sources.items():
            with self.subTest(page=name):
                for text in required:
                    self.assertIn(text, source)

    def test_answer_appears_before_long_form_detail(self):
        aura = self.sources["aura"]
        self.assertLess(aura.index('id="cooldown-tome"'), aura.index('class="quick-stats"'))
        cooldown = self.sources["cooldown"]
        self.assertLess(cooldown.index('id="aura-synergy"'), cooldown.index('class="content-grid"'))
        stats = self.sources["stats"]
        self.assertLess(stats.index('id="attack-speed"'), stats.index('id="stat-formulas"'))

    def test_pages_link_both_directions(self):
        self.assertIn('href="/database/tomes/cooldown-tome"', self.sources["aura"])
        self.assertIn('href="/guides/stats/#attack-speed"', self.sources["aura"])
        self.assertIn('href="/database/weapons/aura"', self.sources["cooldown"])
        self.assertIn('href="/guides/stats/#attack-speed"', self.sources["cooldown"])
        self.assertIn('href="/database/tomes/cooldown-tome"', self.sources["stats"])
        self.assertIn('href="/database/weapons/aura"', self.sources["stats"])

    def test_existing_tdk_is_preserved(self):
        expected_titles = {
            "aura": "Aura Weapon Guide - Unlock, Mechanics & Builds | Megabonk",
            "cooldown": "Cooldown Tome (Attack Speed) – Megabonk Guide",
            "stats": "Megabonk Stats – All Character, Weapon & Build Data",
        }
        for name, title in expected_titles.items():
            self.assertIn(f"<title>{title}</title>", self.sources[name])

    def test_sitemap_dates_cover_changed_pages(self):
        sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
        for url in (
            "https://megabonk.org/database/weapons/aura",
            "https://megabonk.org/database/tomes/cooldown-tome",
            "https://megabonk.org/guides/stats/",
        ):
            self.assertRegex(
                sitemap,
                rf"<loc>{re.escape(url)}</loc>\s*<lastmod>2026-08-11</lastmod>",
            )


if __name__ == "__main__":
    unittest.main()
