import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HUB = ROOT / "database" / "weapons" / "index.html"
TIER = ROOT / "tier-lists" / "weapons" / "index.html"
REDIRECTS = ROOT / "_redirects"
SITEMAP = ROOT / "sitemap.xml"


class WeaponArchitectureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hub = HUB.read_text(encoding="utf-8")
        cls.tier = TIER.read_text(encoding="utf-8")
        cls.redirects = REDIRECTS.read_text(encoding="utf-8")
        cls.sitemap = SITEMAP.read_text(encoding="utf-8")

    def test_database_owns_effect_and_unlock_intent(self):
        title = re.search(r"<title>(.*?)</title>", self.hub, re.S).group(1)
        h1 = re.search(r"<h1[^>]*>(.*?)</h1>", self.hub, re.S).group(1)
        self.assertNotRegex(title.lower(), r"tier list|best weapons")
        self.assertNotRegex(h1.lower(), r"tier list|best weapons")
        self.assertIn("Current effect", self.hub)
        self.assertIn("Unlock requirement", self.hub)
        self.assertIn("Build fit", self.hub)

    def test_all_current_weapons_have_rows_cards_and_detail_pages(self):
        rows = re.findall(
            r'<a class="weapon-table-name" href="/database/weapons/([^"]+)">',
            self.hub,
        )
        self.assertEqual(30, len(rows))
        self.assertEqual(30, len(set(rows)))
        self.assertEqual(30, len(re.findall(r'class="weapon-card"', self.hub)))
        for slug in rows:
            self.assertTrue(
                (ROOT / "database" / "weapons" / f"{slug}.html").exists(),
                slug,
            )

    def test_database_does_not_publish_tier_blocks(self):
        self.assertNotIn('class="weapon-tier ', self.hub)
        self.assertNotIn('class="tier-overview"', self.hub)
        self.assertNotIn('data-filter="s-tier"', self.hub)
        self.assertIn("filter === 'unlock-required'", self.hub)
        self.assertNotIn("const tierWeapons", self.hub)
        self.assertIn('href="/tier-lists/weapons/"', self.hub)
        self.assertIn('href="/database/weapons/"', self.tier)

    def test_schema_and_scythe_use_current_roster(self):
        schemas = re.findall(
            r'<script type="application/ld\+json">(.*?)</script>',
            self.hub,
            re.S,
        )
        collection = next(
            json.loads(raw) for raw in schemas if '"CollectionPage"' in raw
        )
        self.assertEqual(30, collection["mainEntity"]["numberOfItems"])
        self.assertIn('/database/weapons/scythe', self.hub)
        self.assertIn('/database/weapons/scythe', self.tier)
        self.assertIn('All 30 Weapons Ranked', self.tier)

    def test_corrected_unlocks_are_consistent(self):
        expected = {
            "Tornado": "Charge a Charge Shrine 5 times during Desert Sandstorms",
            "Space Noodle": "Complete Desert Tier 2 as Tony McZoom",
            "Slutty Rocket": "Kill 15,000 enemies as CL4NK",
            "Mines": "Kill 7,500 enemies with Slutty Rocket",
            "Black Hole": "Get Knockback Tome to Level 10",
        }
        for weapon, unlock in expected.items():
            self.assertIn(weapon, self.hub)
            self.assertIn(unlock, self.hub)
        for stale in (
            "Get Wind Tome to Level 8",
            "Get Energy Tome to Level 10",
            "Deal 50,000 explosive damage",
            "Kill 250 enemies with traps",
            "Get Gravity Tome to Level 12",
        ):
            self.assertNotIn(stale, self.hub)

    def test_old_best_weapons_url_consolidates_to_tier_page(self):
        self.assertIn(
            "/guides/best-weapons /tier-lists/weapons/ 301",
            self.redirects,
        )
        self.assertNotIn(
            "<loc>https://megabonk.org/guides/best-weapons/</loc>",
            self.sitemap,
        )


if __name__ == "__main__":
    unittest.main()
