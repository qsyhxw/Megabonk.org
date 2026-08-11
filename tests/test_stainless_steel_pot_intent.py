from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "database" / "items" / "pot-stainless-steel.html"


class StainlessSteelPotIntentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = PAGE.read_text(encoding="utf-8")

    def test_exact_entity_name_leads_title_h1_and_social_metadata(self):
        self.assertIn(
            "<title>Pot (Stainless Steel) Megabonk Guide: Effect & Unlock</title>",
            self.source,
        )
        self.assertIn("<h1>Pot (Stainless Steel) Megabonk Guide</h1>", self.source)
        self.assertIn(
            'content="Pot (Stainless Steel) Megabonk Guide: Effect & Unlock"',
            self.source,
        )
        self.assertIn(
            '"headline": "Pot (Stainless Steel) Megabonk Guide: Effect and Unlock"',
            self.source,
        )

    def test_first_screen_answers_effect_and_unlock_with_local_image(self):
        hero = self.source.split('<div class="item-hero">', 1)[1].split(
            '<div class="quick-stats">', 1
        )[0]
        self.assertIn("+10 weapon levels", hero)
        self.assertIn("every chest and pot in Graveyard's first Crypt", hero)
        self.assertIn('/images/Items/Item_Pot_Stainless_Steel.png', hero)
        self.assertIn('width="32" height="32"', hero)
        self.assertTrue((ROOT / "images" / "Items" / "Item_Pot_Stainless_Steel.png").is_file())

    def test_current_effect_and_unlock_are_consistent_with_item_index(self):
        index = (ROOT / "database" / "items" / "index.html").read_text(encoding="utf-8")
        for fact in (
            "First copy adds +10 weapon level cap",
            "Open every chest and pot in Graveyard's first Crypt",
        ):
            self.assertIn(fact, index)
        self.assertIn("only affects weapons", self.source)
        self.assertIn("minimum +2", self.source)

    def test_modified_dates_are_current(self):
        self.assertIn('"dateModified": "2026-08-11"', self.source)
        sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
        entry = sitemap.split(
            "https://megabonk.org/database/items/pot-stainless-steel", 1
        )[1].split("</url>", 1)[0]
        self.assertIn("<lastmod>2026-08-11</lastmod>", entry)


if __name__ == "__main__":
    unittest.main()
