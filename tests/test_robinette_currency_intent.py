import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "guides" / "characters" / "robinette-guide.html"
SITEMAP = ROOT / "sitemap.xml"

class RobinetteCurrencyIntentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = PAGE.read_text(encoding="utf-8")
        cls.sitemap = SITEMAP.read_text(encoding="utf-8")

    def test_existing_character_intent_metadata_stays_stable(self):
        title = re.search(r"<title>(.*?)</title>", self.page, re.S).group(1)
        h1 = re.search(r"<h1[^>]*>(.*?)</h1>", self.page, re.S).group(1)
        self.assertEqual("Robinette Guide: Unlock, Passive &amp; Starting Weapon", title)
        self.assertEqual(title, h1)
        self.assertIn('rel="canonical" href="https://megabonk.org/guides/characters/robinette-guide"', self.page)

    def test_quick_answer_is_in_the_first_screen_content(self):
        quick = self.page.index('id="money-quick-answer"')
        overview = self.page.index('id="overview"')
        self.assertLess(quick, overview)
        hero_answer = self.page.index('class="hero-money-answer"')
        header_end = self.page.index("</header>")
        self.assertLess(hero_answer, header_end)
        self.assertIn("No, not between runs.", self.page)
        self.assertIn("starting a new run resets Gold", self.page)

    def test_gold_and_silver_lifecycles_are_explicit(self):
        self.assertIn('id="money"', self.page)
        self.assertIn("Boss Portal / next stage in the same run", self.page)
        self.assertIn("Gold does not carry into the new attempt", self.page)
        self.assertIn("Silver is retained on the account", self.page)
        self.assertIn("Silver is not counted by Stonks", self.page)

    def test_faq_and_build_handoff_cover_the_query(self):
        self.assertIn("Does Robinette keep Gold between runs?", self.page)
        self.assertIn("Does Robinette keep Gold when entering the next stage?", self.page)
        self.assertIn("Does Silver count toward Robinette's Stonks passive?", self.page)
        self.assertIn('href="/guides/builds/robinette-best-build"', self.page)

    def test_sitemap_date_is_current(self):
        marker = "<loc>https://megabonk.org/guides/characters/robinette-guide</loc>"
        start = self.sitemap.index(marker)
        self.assertIn("<lastmod>2026-07-29</lastmod>", self.sitemap[start:start + 160])

if __name__ == "__main__":
    unittest.main()