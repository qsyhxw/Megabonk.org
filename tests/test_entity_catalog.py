import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


class EntityCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads(
            (ROOT / "data" / "entity-catalog.json").read_text(encoding="utf-8")
        )
        cls.leaderboard = json.loads(
            (ROOT / "leaderboard-data.json").read_text(encoding="utf-8")
        )
        cls.leaderboard_page = (
            ROOT / "leaderboard" / "index.html"
        ).read_text(encoding="utf-8")
        cls.catalog_script = (
            ROOT / "js" / "entity-catalog.js"
        ).read_text(encoding="utf-8")
        cls.check_config = json.loads(
            (ROOT / "data" / "leaderboard-entity-check-config.json").read_text(
                encoding="utf-8"
            )
        )

    def test_declared_local_files_exist(self):
        for entries in self.catalog["entities"].values():
            for entry in entries:
                for field in ("page", "image", "buildPage"):
                    value = entry.get(field)
                    if not value:
                        continue
                    relative = value.lstrip("/").split("#", 1)[0]
                    candidates = [
                        ROOT / relative,
                        ROOT / f"{relative}.html",
                        ROOT / relative / "index.html",
                    ]
                    self.assertTrue(
                        any(path.exists() for path in candidates),
                        f"{entry['id']} has missing {field}: {value}",
                    )

    def test_characters_share_one_complete_reviewed_entity_source(self):
        reviewed = json.loads(
            (ROOT / "data/characters.json").read_text(encoding="utf-8")
        )["characters"]
        catalog_characters = self.catalog["entities"]["characters"]
        self.assertEqual(len(reviewed), 21)
        self.assertEqual(
            {entry["id"]: entry for entry in reviewed},
            {entry["id"]: entry for entry in catalog_characters},
        )
        for entry in catalog_characters:
            with self.subTest(character=entry["id"]):
                self.assertIn(entry["difficulty"], {"beginner", "intermediate", "advanced"})
                self.assertTrue(entry["role"])
                self.assertTrue(entry["unlock"])
                self.assertTrue(entry["passive"])
                self.assertTrue(entry["startingWeapon"]["name"])
                self.assertTrue(entry["startingWeapon"]["page"])

    def test_current_leaderboard_ids_resolve_or_are_reported_gaps(self):
        indexes = {}
        for entity_type, entries in self.catalog["entities"].items():
            index = {}
            for entry in entries:
                for key in (entry["id"], entry["name"], *entry.get("aliases", [])):
                    index[normalize(key)] = entry
            indexes[entity_type] = index

        fields = {
            "characters": "character",
            "weapons": "weapons",
            "tomes": "tomes",
            "items": "items",
        }
        unresolved = {}
        for entity_type, field in fields.items():
            values = set()
            for run in self.leaderboard["data"]:
                raw = run.get(field)
                values.update(raw if isinstance(raw, list) else [raw])
            unresolved[entity_type] = sorted(
                value
                for value in values
                if value and normalize(value) not in indexes[entity_type]
            )

        self.assertEqual(unresolved["characters"], [])
        self.assertEqual(unresolved["weapons"], [])
        self.assertEqual(unresolved["tomes"], [])
        run_objectives = {
            normalize(entry["id"])
            for entry in self.catalog["entities"]["runObjectives"]
        }
        unresolved_build_items = sorted(
            value
            for value in unresolved["items"]
            if normalize(value) not in run_objectives
        )
        self.assertEqual(unresolved_build_items, [])

    def test_crypt_key_is_a_run_objective_not_an_item(self):
        item_ids = {
            normalize(entry["id"])
            for entry in self.catalog["entities"]["items"]
        }
        objectives = {
            normalize(entry["id"]): entry
            for entry in self.catalog["entities"]["runObjectives"]
        }
        self.assertNotIn("cryptkey", item_ids)
        self.assertEqual(
            objectives["cryptkey"]["page"],
            "/guides/maps/graveyard/#crypt-keys",
        )


    def test_reported_leaderboard_item_images_are_declared(self):
        item_index = {
            normalize(entry["id"]): entry
            for entry in self.catalog["entities"]["items"]
        }
        for entity_id in ("bobslight", "oldmask", "pot", "wizardshat"):
            with self.subTest(entity_id=entity_id):
                entry = item_index[entity_id]
                self.assertTrue(entry.get("image"))
                self.assertTrue(entry.get("page"))

    def test_scythe_has_a_local_image_without_a_gap_exemption(self):
        weapon_index = {
            normalize(entry["id"]): entry
            for entry in self.catalog["entities"]["weapons"]
        }
        scythe = weapon_index["scythe"]
        self.assertEqual(
            scythe["image"], "/images/database/weapons/Scythe.png"
        )
        image = ROOT / scythe["image"].lstrip("/")
        self.assertTrue(image.is_file())
        self.assertEqual(image.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
        self.assertEqual(self.check_config["knownGaps"], [])

    def test_global_leaderboard_modal_uses_shared_entity_catalog(self):
        page = self.leaderboard_page
        self.assertIn("/js/entity-catalog.js?v=20260730", page)
        self.assertIn("window.MegabonkEntities?.get(catalogType, name)", page)
        self.assertIn("await window.MegabonkEntities?.ready", page)
        self.assertIn("getDisplayName(i, 'item')", page)
        self.assertIn("getDisplayName(w, 'weapon')", page)
        self.assertIn("getDisplayName(t, 'tome')", page)
        self.assertNotIn("content: 'Click to view';", page)

    def test_entity_catalog_revalidates_automated_updates(self):
        self.assertIn(
            "fetch('/data/entity-catalog.json', { cache: 'no-cache' })",
            self.catalog_script,
        )
if __name__ == "__main__":
    unittest.main()
