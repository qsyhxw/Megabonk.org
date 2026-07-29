import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOME_PAGE = (ROOT / "index.html").read_text(encoding="utf-8")
DATABASE_PAGE = (ROOT / "database" / "index.html").read_text(encoding="utf-8")
GUIDES_PAGE = (ROOT / "guides" / "index.html").read_text(encoding="utf-8")
SITEMAP = (ROOT / "sitemap.xml").read_text(encoding="utf-8")


def root_schema(source, schema_type):
    for block in re.findall(
        r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>',
        source,
        flags=re.S,
    ):
        data = json.loads(block)
        if data.get("@type") == schema_type:
            return data
    raise AssertionError(f"Missing {schema_type} schema")


class BrandWikiArchitectureTests(unittest.TestCase):
    def test_homepage_brand_tdk_is_preserved(self):
        self.assertIn(
            "<title>Megabonk Wiki & Guides 2026 - Builds, Tier Lists, Weapons</title>",
            HOME_PAGE,
        )
        self.assertIn(
            'content="Complete Megabonk guide: character tier lists, best builds, weapon database, boss strategies. Free comprehensive wiki trusted by 500K+ players. Updated daily.">',
            HOME_PAGE,
        )
        self.assertIn("<h1>Megabonk Wiki 2026</h1>", HOME_PAGE)

    def test_homepage_answers_brand_and_developer_intent(self):
        for phrase in (
            "What Is Megabonk?",
            "Megabonk is a 3D roguelike survival game",
            "Megabonk Game Facts",
            "vedinad",
            "September 18, 2025",
            "Windows and Linux",
            "independent player Wiki",
        ):
            self.assertIn(phrase, HOME_PAGE)

    def test_homepage_keeps_five_primary_routes(self):
        hero = re.search(r'<nav class="hero-paths".*?</nav>', HOME_PAGE, re.S).group(0)
        for url in (
            "/guides/builds/",
            "/tier-lists/",
            "/leaderboard/",
            "/database/weapons/",
            "/guides/unlocks/",
        ):
            self.assertIn(f'href="{url}"', hero)
        self.assertEqual(hero.count('class="hero-path"'), 5)

    def test_hubs_use_qualified_h1s_without_wiki_competition(self):
        database_h1 = re.search(r'<h1[^>]*>(.*?)</h1>', DATABASE_PAGE, re.S).group(1)
        guides_h1 = re.search(r'<h1[^>]*>(.*?)</h1>', GUIDES_PAGE, re.S).group(1)
        self.assertIn("Megabonk Game Database", database_h1)
        self.assertNotIn("Wiki", database_h1)
        self.assertIn("Megabonk Gameplay Guides", guides_h1)
        self.assertNotIn("Wiki", guides_h1)

    def test_entity_schemas_are_linked_and_patch_safe(self):
        game = root_schema(HOME_PAGE, "VideoGame")
        organization = root_schema(HOME_PAGE, "Organization")
        website = root_schema(HOME_PAGE, "WebSite")
        faq = root_schema(HOME_PAGE, "FAQPage")
        self.assertEqual(game["author"]["name"], "vedinad")
        self.assertEqual(game["publisher"]["name"], "vedinad")
        self.assertEqual(game["datePublished"], "2025-09-18")
        self.assertNotIn("aggregateRating", game)
        self.assertNotIn("offers", game)
        self.assertEqual(organization["@id"], "https://megabonk.org/#organization")
        self.assertEqual(website["name"], "Megabonk Wiki")
        self.assertEqual(website["about"]["@id"], game["@id"])
        self.assertEqual(website["publisher"]["@id"], organization["@id"])
        self.assertEqual(len(faq["mainEntity"]), 4)
        self.assertIn("data-home-patch-version", HOME_PAGE)
        self.assertIn("data-home-patch-synced", HOME_PAGE)

    def test_stale_dynamic_claims_are_removed_from_visible_content(self):
        self.assertNotIn("$8.49", HOME_PAGE)
        self.assertNotIn("Game data accurate as of January 2026", HOME_PAGE)
        self.assertNotIn("70+ weapons", HOME_PAGE)

    def test_modified_hubs_have_current_sitemap_dates(self):
        for url in (
            "https://megabonk.org/",
            "https://megabonk.org/database/",
            "https://megabonk.org/guides/",
        ):
            self.assertRegex(
                SITEMAP,
                rf"<loc>{re.escape(url)}</loc>\s*<lastmod>2026-07-29</lastmod>",
            )


if __name__ == "__main__":
    unittest.main()