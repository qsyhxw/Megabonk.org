import importlib.util
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "check_leaderboard_entities.py"
)
SPEC = importlib.util.spec_from_file_location("check_leaderboard_entities", MODULE_PATH)
CHECK = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(CHECK)


class LeaderboardEntityCheckTests(unittest.TestCase):
    def setUp(self):
        self._original_root = CHECK.ROOT
        self.temp_dir = tempfile.TemporaryDirectory()
        CHECK.ROOT = Path(self.temp_dir.name)

    def tearDown(self):
        CHECK.ROOT = self._original_root
        self.temp_dir.cleanup()

    def make_page(self, relative_path, anchor=None):
        path = CHECK.ROOT / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        anchor_html = f'<section id="{anchor}"></section>' if anchor else ""
        path.write_text(f"<html>{anchor_html}</html>", encoding="utf-8")

    def make_image(self, relative_path):
        path = CHECK.ROOT / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"image")

    def empty_catalog(self):
        return {
            "entities": {
                "characters": [],
                "weapons": [],
                "tomes": [],
                "items": [],
                "runObjectives": [],
            }
        }

    def test_registered_entities_with_assets_pass(self):
        self.make_page("database/items/clover.html")
        self.make_image("images/Items/Item_Clover.png")
        catalog = self.empty_catalog()
        catalog["entities"]["items"].append(
            {
                "id": "clover",
                "name": "Clover",
                "aliases": [],
                "page": "/database/items/clover",
                "image": "/images/Items/Item_Clover.png",
            }
        )
        report = CHECK.check_entities(
            {"data": [{"items": ["clover"]}]}, catalog
        )
        self.assertEqual(report["gapCount"], 0)

    def test_unknown_entity_fails(self):
        report = CHECK.check_entities(
            {"data": [{"items": ["newitem"]}]}, self.empty_catalog()
        )
        self.assertEqual(report["gapCount"], 1)
        self.assertEqual(report["gaps"][0]["reason"], "unregistered entity")

    def test_missing_image_and_page_are_reported(self):
        catalog = self.empty_catalog()
        catalog["entities"]["weapons"].append(
            {
                "id": "newweapon",
                "name": "New Weapon",
                "aliases": [],
                "page": "/database/weapons/new-weapon",
                "image": "/images/database/weapons/New_Weapon.png",
            }
        )
        report = CHECK.check_entities(
            {"data": [{"weapons": ["newweapon"]}]}, catalog
        )
        self.assertEqual(report["gapCount"], 1)
        self.assertIn("page file not found", report["gaps"][0]["reason"])
        self.assertIn("image file not found", report["gaps"][0]["reason"])

    def test_known_field_gap_warns_without_blocking(self):
        self.make_page("database/weapons/scythe.html")
        catalog = self.empty_catalog()
        catalog["entities"]["weapons"].append(
            {
                "id": "scythe",
                "name": "Scythe",
                "aliases": [],
                "page": "/database/weapons/scythe",
                "image": None,
            }
        )
        config = {
            "knownGaps": [
                {
                    "sourceType": "weapons",
                    "id": "scythe",
                    "allow": ["asset"],
                }
            ]
        }
        report = CHECK.check_entities(
            {"data": [{"weapons": ["scythe"]}]}, catalog, config
        )
        self.assertEqual(report["gapCount"], 0)
        self.assertEqual(report["knownGapCount"], 1)
    def test_run_objective_accepts_page_anchor_and_icon(self):
        self.make_page("guides/maps/graveyard/index.html", "crypt-keys")
        catalog = self.empty_catalog()
        catalog["entities"]["runObjectives"].append(
            {
                "id": "cryptkey",
                "name": "Crypt Key",
                "aliases": ["crypt key"],
                "page": "/guides/maps/graveyard/#crypt-keys",
                "image": None,
                "icon": "🔑",
            }
        )
        report = CHECK.check_entities(
            {"data": [{"items": ["cryptkey"]}]}, catalog
        )
        self.assertEqual(report["gapCount"], 0)


if __name__ == "__main__":
    unittest.main()
