import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "guides" / "achievements" / "collection-secrets.html"
TR_PAGE = ROOT / "tr" / "index.html"
CATALOG = ROOT / "data" / "entity-catalog.json"


class CollectionChecklistAccuracyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = PAGE.read_text(encoding="utf-8")
        cls.tr_html = TR_PAGE.read_text(encoding="utf-8")
        cls.catalog = json.loads(CATALOG.read_text(encoding="utf-8"))["entities"]

    def test_collection_counts_match_shared_entity_catalog(self):
        expected = {
            "weapons": 30,
            "items": 85,
            "tomes": 23,
            "characters": 21,
        }
        for entity_type, count in expected.items():
            self.assertEqual(len(self.catalog[entity_type]), count)

        for text in (
            "30 currently documented weapons",
            "85 currently documented items",
            "23 currently documented Tomes",
            "Track all 21 current characters",
        ):
            self.assertIn(text, self.html)

    def test_weapon_collection_is_not_presented_as_a_steam_achievement(self):
        self.assertIn(
            "This is a site completion checklist, not a standalone Steam achievement.",
            self.html,
        )
        for stale_claim in (
            "Unlock all 29 weapons",
            "Complete Weapon Collection",
            "Weapon Collector",
            "Verified Count",
            "~30% Unlocked",
        ):
            self.assertNotIn(stale_claim, self.html)
            self.assertNotIn(stale_claim, self.tr_html)

    def test_current_steam_achievement_total_and_scythe_are_explicit(self):
        achievement_hub = (ROOT / "guides" / "achievements" / "index.html").read_text(
            encoding="utf-8"
        )
        self.assertIn("139 current Steam achievements", self.html)
        self.assertIn("139 current Steam achievements", achievement_hub)
        self.assertIn("including Scythe", self.html)
        self.assertNotIn("102 achievements", self.html)
        self.assertNotIn("102 Steam achievements", self.html)
        self.assertNotIn("102 achievements", achievement_hub)
        self.assertNotIn("102 Steam achievements", achievement_hub)
        self.assertIn("Achievement Index (139 Total)", self.tr_html)

    def test_collection_pages_use_current_neutral_labels(self):
        self.assertIn("Current Weapon Collection", self.html)
        self.assertIn("Current Item Collection", self.html)
        self.assertIn("Current Tome Collection", self.html)
        self.assertIn("Weapon Collection:", self.tr_html)
        self.assertNotIn("Item Master:", self.tr_html)
        self.assertNotIn("Tome Scholar:", self.tr_html)


if __name__ == "__main__":
    unittest.main()
