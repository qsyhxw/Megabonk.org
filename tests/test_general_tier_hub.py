import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HUB_PATH = ROOT / "tier-lists" / "index.html"


class GeneralTierHubTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = HUB_PATH.read_text(encoding="utf-8")

    def test_general_intent_tdk_is_preserved(self):
        self.assertIn("<title>Megabonk Tier List 2026 – Complete Rankings</title>", self.html)
        self.assertIn(
            '<meta name="description" content="Megabonk tier list hub for character, weapon, item and tome rankings. Compare each category, its coverage notes and related builds.">',
            self.html,
        )
        self.assertIn("<h1>🏆 Megabonk Tier List 2026</h1>", self.html)

    def test_four_qualified_rankings_have_canonical_destinations(self):
        destinations = {
            "Character Tier List": "/guides/characters/character-tier-list/",
            "Weapon Tier List": "/tier-lists/weapons/",
            "Item Tier List": "/tier-lists/items/",
            "Tome Tier List": "/tier-lists/tomes/",
        }
        for label, url in destinations.items():
            self.assertRegex(
                self.html,
                rf'(?s)<a[^>]+href="{re.escape(url)}"[^>]*>.*?<h2 class="category-title">{re.escape(label)}</h2>',
            )

    def test_structured_data_points_weapon_ranking_to_tier_page(self):
        schemas = [
            json.loads(block)
            for block in re.findall(
                r'<script type="application/ld\+json">\s*(.*?)\s*</script>',
                self.html,
                flags=re.DOTALL,
            )
        ]
        item_list = next(schema for schema in schemas if schema.get("@type") == "ItemList")
        urls = {entry["name"]: entry["url"] for entry in item_list["itemListElement"]}
        self.assertEqual(
            urls["Megabonk Weapon Tier List"],
            "https://megabonk.org/tier-lists/weapons/",
        )

    def test_current_patch_and_automated_usage_signal_are_separate(self):
        self.assertIn("Latest official patch: V1.0.69", self.html)
        self.assertIn("fetch('/data/leaderboard-meta.json'", self.html)
        self.assertIn("fetch('/data/entity-catalog.json'", self.html)
        self.assertIn("Version guard", self.html)
        self.assertIn("supporting evidence rather than an automatic tier", self.html)
        self.assertIn('id="meta-weapons-list"', self.html)
        self.assertIn('id="meta-tomes-list"', self.html)
        self.assertIn('id="meta-items-list"', self.html)

    def test_stale_snapshot_claims_are_removed(self):
        self.assertNotIn("v1.0.17", self.html.lower())
        self.assertNotIn("version 1.0.17", self.html.lower())
        self.assertNotIn("Holy Trinity", self.html)
        self.assertNotIn("Latest patch tracked: Version 1.0.64", self.html)
        self.assertNotIn("Competitive Performance (40%)", self.html)

    def test_review_metadata_is_current(self):
        self.assertIn('article:modified_time" content="2026-07-29T00:00:00+08:00', self.html)
        self.assertIn('"dateModified": "2026-07-29"', self.html)
        self.assertIn('<time datetime="2026-07-29">July 29, 2026</time>', self.html)


if __name__ == "__main__":
    unittest.main()