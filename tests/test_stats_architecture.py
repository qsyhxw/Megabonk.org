import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATS = ROOT / "guides" / "stats" / "index.html"
TOMES = ROOT / "database" / "tomes"
SITEMAP = ROOT / "sitemap.xml"

class StatsArchitectureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stats = STATS.read_text(encoding="utf-8")
        cls.sitemap = SITEMAP.read_text(encoding="utf-8")

    def test_stats_hub_owns_generic_stat_intent(self):
        title = re.search(r"<title>(.*?)</title>", self.stats, re.S).group(1)
        self.assertIn("Megabonk Stats", title)
        self.assertIn('href="https://megabonk.org/guides/stats/"', self.stats)
        self.assertEqual(1, len(re.findall(r"<h1\b", self.stats)))

    def test_deep_dive_anchors_and_navigation_exist(self):
        for anchor in ("stat-formulas", "size", "knockback", "difficulty", "luck"):
            self.assertEqual(1, self.stats.count(f'id="{anchor}"'), anchor)
            self.assertIn(f'href="#{anchor}"', self.stats)

    def test_formulas_and_marginal_return_guidance_exist(self):
        for text in (
            "Effective attack size",
            "Effective push",
            "XP/min",
            "Difficulty raises enemy HP",
            "Marginal return",
            "When to skip it",
        ):
            self.assertIn(text, self.stats)

    def test_stats_and_tome_pages_link_both_directions(self):
        mapping = {
            "size-tome.html": ("/database/tomes/size-tome", "/guides/stats/#size"),
            "knockback-tome.html": ("/database/tomes/knockback-tome", "/guides/stats/#knockback"),
            "cursed-tome.html": ("/database/tomes/cursed-tome", "/guides/stats/#difficulty"),
        }
        for filename, (tome_link, stats_link) in mapping.items():
            self.assertIn(tome_link, self.stats)
            self.assertIn(stats_link, (TOMES / filename).read_text(encoding="utf-8"))

    def test_faq_schema_covers_priority_queries(self):
        schemas = [json.loads(raw) for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', self.stats, re.S)]
        faq = next(schema for schema in schemas if schema.get("@type") == "FAQPage")
        questions = {item["name"] for item in faq["mainEntity"]}
        self.assertIn("What does Difficulty do in Megabonk?", questions)
        self.assertIn("What does Size do in Megabonk?", questions)
        self.assertIn("What is the Knockback Tome for in Megabonk?", questions)

    def test_sitemap_dates_are_current(self):
        for url in (
            "https://megabonk.org/guides/stats/",
            "https://megabonk.org/database/tomes/size-tome.html",
            "https://megabonk.org/database/tomes/knockback-tome.html",
            "https://megabonk.org/database/tomes/cursed-tome.html",
        ):
            pattern = rf"<loc>{re.escape(url)}</loc>\s*<lastmod>2026-07-28</lastmod>"
            self.assertRegex(self.sitemap, pattern)

if __name__ == "__main__":
    unittest.main()
