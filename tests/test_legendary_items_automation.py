import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_legendary_items_page.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("legendary_builder", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


class LegendaryItemsAutomationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.builder = load_builder()
        cls.page = cls.builder.PAGE.read_text(encoding="utf-8")
        cls.catalog = json.loads(cls.builder.CATALOG.read_text(encoding="utf-8"))
        cls.rankings = json.loads(cls.builder.RANKINGS.read_text(encoding="utf-8"))["rankings"]

    def test_generated_page_is_committed_and_current(self):
        self.assertEqual(self.builder.render(self.page), self.page)

    def test_catalog_and_editorial_rosters_match_exactly(self):
        legendary_ids = {
            entry["id"]
            for entry in self.catalog["entities"]["items"]
            if entry.get("rarity") == "Legendary"
        }
        ranked_ids = [entry["id"] for entry in self.rankings]
        self.assertEqual(22, len(legendary_ids))
        self.assertEqual(legendary_ids, set(ranked_ids))
        self.assertEqual(len(ranked_ids), len(set(ranked_ids)))
        self.assertNotIn("kevin", legendary_ids)

    def test_rankings_only_own_editorial_fields(self):
        allowed = {"id", "tier", "reason", "buildUse"}
        for entry in self.rankings:
            self.assertEqual(set(entry), allowed)
            self.assertIn(entry["tier"], {"S", "A", "B", "C", "U"})
            self.assertTrue(entry["reason"])
            self.assertTrue(entry["buildUse"])

    def test_every_generated_entity_has_local_page_and_image(self):
        items, _ = self.builder.load_inputs()
        for entity_id, item in items.items():
            with self.subTest(entity_id=entity_id):
                self.assertTrue((ROOT / f"{item['page'].lstrip('/')}.html").is_file())
                self.assertTrue((ROOT / item["image"].lstrip("/")).is_file())


if __name__ == "__main__":
    unittest.main()
