import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HUB = ROOT / "database" / "tomes" / "index.html"
TIER = ROOT / "tier-lists" / "tomes" / "index.html"
REDIRECTS = ROOT / "_redirects"
SITEMAP = ROOT / "sitemap.xml"


class TomeArchitectureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hub = HUB.read_text(encoding="utf-8")
        cls.tier = TIER.read_text(encoding="utf-8")
        cls.redirects = REDIRECTS.read_text(encoding="utf-8")
        cls.sitemap = SITEMAP.read_text(encoding="utf-8")

    def test_database_owns_effect_and_unlock_intent(self):
        title = re.search(r"<title>(.*?)</title>", self.hub, re.S).group(1)
        h1 = re.search(r"<h1[^>]*>(.*?)</h1>", self.hub, re.S).group(1)
        self.assertNotRegex(title.lower(), r"tier list|best tomes")
        self.assertNotRegex(h1.lower(), r"tier list|best tomes")
        self.assertIn("Effect per level", self.hub)
        self.assertIn("Unlock requirement", self.hub)
        schema = re.search(r'<script type="application/ld\+json">(.*?)</script>', self.hub, re.S)
        self.assertIsNotNone(schema)
        import json
        self.assertEqual(23, json.loads(schema.group(1))["mainEntity"]["numberOfItems"])

    def test_all_tomes_have_table_rows_and_detail_links(self):
        rows = re.findall(
            r'<a class="tome-table-name" href="/database/tomes/([^"]+)">',
            self.hub,
        )
        self.assertEqual(23, len(rows))
        self.assertEqual(23, len(set(rows)))
        for slug in rows:
            self.assertTrue(
                (ROOT / "database" / "tomes" / f"{slug}.html").exists(),
                slug,
            )

    def test_database_cards_do_not_publish_rankings(self):
        self.assertNotRegex(self.hub, r'class="tome-tier')
        self.assertIn('href="/tier-lists/tomes/"', self.hub)
        self.assertIn('href="/database/tomes/"', self.tier)

    def test_old_best_tomes_url_consolidates_to_tier_page(self):
        self.assertIn(
            "/guides/best-tomes /tier-lists/tomes/ 301",
            self.redirects,
        )
        self.assertNotIn(
            "<loc>https://megabonk.org/guides/best-tomes/</loc>",
            self.sitemap,
        )

    def test_current_luck_value_is_consistent(self):
        luck = (ROOT / "database" / "tomes" / "luck-tome.html").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("+8% Luck", self.hub)
        self.assertNotIn("+8% Luck", self.tier)
        self.assertNotIn("+8% Luck", luck)
        self.assertIn("+7% Luck", self.hub)
        self.assertIn("+7% Luck", self.tier)
        self.assertIn("+7% Luck", luck)
        self.assertIn("Kill 5,000 enemies as Sir Oofie", self.hub)
        self.assertNotIn("Kill 12,500 enemies as Sir Oofie", self.hub)


if __name__ == "__main__":
    unittest.main()
