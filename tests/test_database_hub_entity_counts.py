import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data" / "entity-catalog.json"
DATABASE = ROOT / "database" / "index.html"
WEAPONS = ROOT / "database" / "weapons" / "index.html"
CHARACTERS = ROOT / "guides" / "characters" / "index.html"
ITEMS = ROOT / "database" / "items" / "index.html"
TR_HOME = ROOT / "tr" / "index.html"
SITEMAP = ROOT / "sitemap.xml"


class DatabaseHubEntityCountTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads(CATALOG.read_text(encoding="utf-8"))["entities"]
        cls.database = DATABASE.read_text(encoding="utf-8")
        cls.weapons = WEAPONS.read_text(encoding="utf-8")
        cls.characters = CHARACTERS.read_text(encoding="utf-8")
        cls.items = ITEMS.read_text(encoding="utf-8")
        cls.tr_home = TR_HOME.read_text(encoding="utf-8")
        cls.sitemap = SITEMAP.read_text(encoding="utf-8")
        cls.counts = {
            "weapons": len(cls.catalog["weapons"]),
            "characters": len(cls.catalog["characters"]),
            "items": len(cls.catalog["items"]),
            "tomes": len(cls.catalog["tomes"]),
        }

    def test_reviewed_catalog_has_expected_current_roster(self):
        self.assertEqual(
            {"weapons": 30, "characters": 21, "items": 85, "tomes": 23},
            self.counts,
        )

    def test_database_top_stats_match_the_entity_catalog(self):
        labels = {
            "weapons": "Total Weapons",
            "characters": "Playable Characters",
            "items": "Items & Upgrades",
            "tomes": "Tomes",
        }
        for entity_type, label in labels.items():
            with self.subTest(entity_type=entity_type):
                self.assertRegex(
                    self.database,
                    rf'<span class="stat-number">{self.counts[entity_type]}</span>\s*'
                    rf'<span class="stat-label">{re.escape(label)}</span>',
                )

    def test_database_schema_and_category_copy_use_current_counts(self):
        schema = json.loads(
            re.search(
                r'<script type="application/ld\+json">\s*(.*?)\s*</script>',
                self.database,
                re.S,
            ).group(1)
        )
        descriptions = " ".join(
            entry["description"]
            for entry in schema["mainEntity"]["itemListElement"]
        )
        self.assertIn(f'all {self.counts["weapons"]} weapons', descriptions)
        self.assertIn(f'All {self.counts["characters"]} playable characters', descriptions)

        for current in (
            "Completed: 30/30 guides",
            "Completed: 21/21 character guides",
            "Available: 85 documented items",
            "Rankings of all 21 characters",
        ):
            self.assertIn(current, self.database)
        for stale in (
            "29 Total Weapons",
            "All 20 playable characters",
            "20/20 characters",
            "70+ items",
            "Rankings of all 20 characters",
        ):
            self.assertNotIn(stale, self.database)

    def test_database_counts_agree_with_owned_entity_hubs(self):
        self.assertIn("30 Total Weapons", self._visible_text(self.weapons))
        character_item_list = next(
            json.loads(block)
            for block in re.findall(
                r'<script type="application/ld\+json">\s*(.*?)\s*</script>',
                self.characters,
                re.S,
            )
            if '"@type":"ItemList"' in block
        )
        self.assertEqual(self.counts["characters"], character_item_list["numberOfItems"])
        self.assertEqual(self.counts["items"], self.items.count('class="item-card"'))

    def test_language_home_no_longer_publishes_old_roster_totals(self):
        for current in (
            "21 Playable Characters",
            "all 21 playable characters",
            "all 21 character rankings",
            "Each of the 30 weapons",
            "85 Items &amp; Synergies",
        ):
            self.assertIn(current, self.tr_home)
        for stale in (
            "20 Unique Characters",
            "All 20 Characters",
            "all 20 playable characters",
            "all 20 character rankings",
            "All 20 Character Guides",
            "Each of the 70+ weapons",
        ):
            self.assertNotIn(stale, self.tr_home)

    def test_modified_hubs_have_current_sitemap_dates(self):
        for url in ("https://megabonk.org/database/", "https://megabonk.org/tr/"):
            with self.subTest(url=url):
                entry = re.search(
                    rf"<loc>{re.escape(url)}</loc>\s*<lastmod>([^<]+)</lastmod>",
                    self.sitemap,
                )
                self.assertIsNotNone(entry)
                self.assertEqual("2026-08-11", entry.group(1))

    @staticmethod
    def _visible_text(source: str) -> str:
        return " ".join(re.sub(r"<[^>]+>", " ", source).split())


if __name__ == "__main__":
    unittest.main()
