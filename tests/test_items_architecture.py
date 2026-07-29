import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HUB = ROOT / "database" / "items" / "index.html"
ANVIL = ROOT / "database" / "items" / "anvil.html"
KEVIN = ROOT / "database" / "items" / "kevin.html"
GOLDEN_RING = ROOT / "database" / "items" / "golden-ring.html"
TIER = ROOT / "tier-lists" / "items" / "index.html"
ACHIEVEMENTS = ROOT / "guides" / "achievements" / "index.html"
STORY_MILESTONES = ROOT / "guides" / "achievements" / "story-milestones.html"
SITEMAP = ROOT / "sitemap.xml"

class ItemArchitectureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hub = HUB.read_text(encoding="utf-8")
        cls.anvil = ANVIL.read_text(encoding="utf-8")
        cls.kevin = KEVIN.read_text(encoding="utf-8")
        cls.golden_ring = GOLDEN_RING.read_text(encoding="utf-8")
        cls.tier = TIER.read_text(encoding="utf-8")
        cls.achievements = ACHIEVEMENTS.read_text(encoding="utf-8")
        cls.story_milestones = STORY_MILESTONES.read_text(encoding="utf-8")
        cls.sitemap = SITEMAP.read_text(encoding="utf-8")

    def test_database_owns_item_data_not_tier_list_intent(self):
        title = re.search(r"<title>(.*?)</title>", self.hub, re.S).group(1)
        h1 = re.search(r"<h1[^>]*>(.*?)</h1>", self.hub, re.S).group(1)
        self.assertNotIn("tier list", title.lower())
        self.assertNotIn("tier list", h1.lower())
        self.assertIn('href="/tier-lists/items/"', self.hub)
        self.assertIn("Current Effect", self.hub)
        self.assertIn("Best Build Use", self.hub)

    def test_current_roster_and_rarity_totals(self):
        self.assertIn("85 Items", self.hub)
        self.assertEqual(85, self.hub.count('class="item-card"'))
        for rarity, count in {"Legendary": 15, "Epic": 13, "Rare": 29, "Common": 28}.items():
            self.assertEqual(count, len(re.findall(rf'data-rarity="{rarity}"', self.hub)), rarity)

    def test_every_card_has_a_local_detail_page(self):
        hrefs = re.findall(r'<a href="([^"]+)" class="item-card" data-rarity=', self.hub)
        self.assertEqual(85, len(hrefs))
        self.assertEqual(85, len(set(hrefs)))
        for href in hrefs:
            path = ROOT / href.lstrip("/") if href.startswith("/") else HUB.parent / href
            candidates = (path, path.with_suffix(".html"), path / "index.html")
            self.assertTrue(any(candidate.is_file() for candidate in candidates), href)

    def test_ranked_items_use_local_icons_and_linked_names(self):
        table = re.search(
            r'<table class="rank-table">.*?<tbody>(.*?)</tbody>',
            self.tier,
            re.S,
        ).group(1)
        entities = re.findall(
            r'<a class="entity-name-with-icon" href="/database/items/([^"]+)"><img src="(/images/Items/[^"]+)"',
            table,
        )
        self.assertEqual(20, len(entities))
        self.assertEqual(20, len({href for href, _ in entities}))
        for _, src in entities:
            self.assertTrue((ROOT / src.lstrip("/")).is_file(), src)
    def test_missing_hub_entities_are_restored(self):
        for name, href in (("Golden Ring", "golden-ring"), ("Quin's Mask", "quins-mask"), ("Snek", "snek")):
            self.assertIn(name, self.hub)
            self.assertIn(f'href="{href}"', self.hub)

    def test_corrected_high_interest_item_data(self):
        self.assertRegex(self.hub, r'href="overpowered-lamp" class="item-card" data-rarity="Legendary"')
        self.assertRegex(self.hub, r'href="kevin" class="item-card" data-rarity="Epic"')
        self.assertIn("Complete 3 Challenges", self.anvil)
        self.assertIn("LEGENDARY ITEM", self.anvil)
        self.assertIn("Epic specialist item", self.kevin)
        self.assertIn("No dependable gameplay effect", self.hub)
        self.assertIn("reviewed again July 28, 2026", self.golden_ring)

    def test_anvil_unlock_is_consistent_across_owned_pages(self):
        self.assertIn("<title>Megabonk Anvil: Effect, Unlock & Best Builds</title>", self.anvil)
        hero = re.search(r'<div class="item-hero">(.*?)</div>\s*</div>\s*</div>', self.anvil, re.S).group(1)
        self.assertIn("Complete any 3 Challenges", hero)
        self.assertIn("Last verified July 29, 2026", hero)
        self.assertNotIn("Defeat the Final Boss twice", self.anvil)

        expected_sources = (
            self.hub,
            self.tier,
            self.achievements,
            self.story_milestones,
        )
        for source in expected_sources:
            self.assertIn("Complete 3 Challenges", source)

        for source in (self.hub, self.tier, self.achievements, self.story_milestones):
            self.assertIn('href="/database/items/anvil"', source)

    def test_anvil_schema_encodes_current_unlock(self):
        blocks = re.findall(
            r'<script type="application/ld\+json">\s*(.*?)\s*</script>',
            self.anvil,
            re.S,
        )
        self.assertTrue(blocks)
        entities = []
        for block in blocks:
            graph = json.loads(block)
            entities.extend(graph.get("@graph", [graph]))

        article = next(entity for entity in entities if entity.get("@type") == "Article")
        self.assertEqual(article["headline"], "Megabonk Anvil: Effect, Unlock & Best Builds")
        self.assertEqual(article["mainEntityOfPage"], "https://megabonk.org/database/items/anvil")
        self.assertEqual(article["dateModified"], "2026-07-29")
        properties = {
            prop["name"]: prop["value"]
            for prop in article["about"]["additionalProperty"]
        }
        self.assertEqual(properties["Unlock requirement"], "Complete 3 Challenges")
        self.assertEqual(properties["Rarity"], "Legendary")

        breadcrumb = next(entity for entity in entities if entity.get("@type") == "BreadcrumbList")
        self.assertEqual(breadcrumb["itemListElement"][-1]["name"], "Anvil")
        self.assertEqual(
            breadcrumb["itemListElement"][-1]["item"],
            "https://megabonk.org/database/items/anvil",
        )

    def test_anvil_sitemap_date_is_current(self):
        self.assertRegex(
            self.sitemap,
            r"<loc>https://megabonk\.org/database/items/anvil</loc>\s*"
            r"<lastmod>2026-07-29</lastmod>",
        )

    def test_search_and_rarity_controls_are_present(self):
        self.assertIn('id="itemSearch"', self.hub)
        self.assertIn('id="itemResultCount"', self.hub)
        self.assertEqual(5, self.hub.count("data-rarity-filter="))
        self.assertIn("function applyItemFilters()", self.hub)
        self.assertIn("button.dataset.rarityFilter", self.hub)

if __name__ == "__main__":
    unittest.main()