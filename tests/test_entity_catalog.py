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

    def test_declared_local_files_exist(self):
        for entries in self.catalog["entities"].values():
            for entry in entries:
                for field in ("page", "image", "buildPage"):
                    value = entry.get(field)
                    if not value:
                        continue
                    relative = value.lstrip("/")
                    candidates = [
                        ROOT / relative,
                        ROOT / f"{relative}.html",
                        ROOT / relative / "index.html",
                    ]
                    self.assertTrue(
                        any(path.exists() for path in candidates),
                        f"{entry['id']} has missing {field}: {value}",
                    )

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
        self.assertEqual(
            unresolved["items"],
            ["bobslight", "cryptkey", "oldmask", "pumpkin"],
        )


if __name__ == "__main__":
    unittest.main()
