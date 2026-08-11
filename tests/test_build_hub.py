import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HUB = ROOT / "guides" / "builds" / "index.html"
CATALOG = ROOT / "data" / "entity-catalog.json"


def resolve_page(url):
    relative = url.split("#", 1)[0].split("?", 1)[0].strip("/")
    candidates = [ROOT / f"{relative}.html", ROOT / relative / "index.html"]
    return next((path for path in candidates if path.exists()), None)


class BuildHubTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = HUB.read_text(encoding="utf-8")

    def test_existing_general_build_tdk_is_preserved(self):
        self.assertIn(
            "<title>Megabonk Best Builds Guide 2026 - Top Meta Builds & Strategies</title>",
            self.source,
        )
        self.assertIn(
            '<meta name="description" content="Master Megabonk with popular character builds, weapon combos, and effective strategies. Complete guide to powerful builds and playstyles.">',
            self.source,
        )
        self.assertIn("<h1>🏆 Best Megabonk Build 2026</h1>", self.source)

    def test_hub_lists_all_21_character_builds(self):
        catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        characters = catalog["entities"]["characters"]
        rows = re.findall(r'<tr data-character="[^"]+">', self.source)
        cards = re.findall(r'<article class="character-quick-card" data-character="[^"]+">', self.source)
        self.assertEqual(len(rows), len(characters))
        self.assertEqual(len(cards), len(characters))
        self.assertIn('.character-quick-card[hidden]', self.source)
        self.assertIn('.leaderboard-signal-card[hidden]', self.source)
        self.assertIn('display: none !important;', self.source)
        self.assertNotIn("all 20 Megabonk characters", self.source)
        self.assertNotIn("Showing all 20 character builds", self.source)
        self.assertIn('<div class="stat-number">21</div>', self.source)
        self.assertIn('<div class="stat-number">21/21</div>', self.source)

    def test_character_surfaces_are_generated_from_shared_catalog(self):
        catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        for entity in catalog["entities"]["characters"]:
            with self.subTest(character=entity["id"]):
                self.assertIn(
                    f'<option value="{entity["id"]}">{entity["name"]}</option>',
                    self.source,
                )
                self.assertIn(
                    f'<article class="character-quick-card" data-character="{entity["id"]}">',
                    self.source,
                )
                self.assertIn(f'src="{entity["image"]}"', self.source)
                self.assertIn(f'href="{entity["buildPage"]}"', self.source)
                self.assertIn(f'href="{entity["page"]}"', self.source)
                self.assertIn(
                    f'<tr data-character="{entity["id"]}">',
                    self.source,
                )
        for marker in (
            "BUILD_HUB_CHARACTER_OPTIONS_START",
            "BUILD_HUB_CHARACTER_CARDS_START",
            "BUILD_HUB_CHARACTER_ROWS_START",
            "BUILD_HUB_ITEMLIST_START",
        ):
            self.assertIn(marker, self.source)
        self.assertNotIn("const leaderboardBuildRoutes =", self.source)
        self.assertNotIn("const leaderboardCharacterImages =", self.source)
        self.assertIn("window.MegabonkEntities?.get('characters', entry.character)", self.source)

    def test_build_hub_structured_data_matches_visible_architecture(self):
        schemas = [
            json.loads(raw)
            for raw in re.findall(
                r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>',
                self.source,
                re.DOTALL,
            )
        ]
        by_type = {schema.get("@type"): schema for schema in schemas}
        catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        characters = catalog["entities"]["characters"]

        item_list = by_type["ItemList"]
        self.assertEqual(item_list["numberOfItems"], len(characters))
        self.assertEqual(len(item_list["itemListElement"]), len(characters))
        for position, (item, character) in enumerate(
            zip(item_list["itemListElement"], characters), start=1
        ):
            self.assertEqual(item["position"], position)
            self.assertEqual(item["name"], f'{character["name"]} Best Build')
            self.assertEqual(item["url"], f'https://megabonk.org{character["buildPage"]}')

        breadcrumbs = by_type["BreadcrumbList"]["itemListElement"]
        self.assertEqual([item["position"] for item in breadcrumbs], [1, 2, 3])
        self.assertEqual(
            [item["item"] for item in breadcrumbs],
            [
                "https://megabonk.org/",
                "https://megabonk.org/guides/",
                "https://megabonk.org/guides/builds/",
            ],
        )

        questions = by_type["FAQPage"]["mainEntity"]
        expected_questions = (
            "What is the best Megabonk Build?",
            "Are leaderboard Builds always current?",
            "How do I find a Build for my character?",
            "Why is the leaderboard version different?",
        )
        self.assertEqual(tuple(question["name"] for question in questions), expected_questions)
        for question in questions:
            self.assertIn(f'<h3>{question["name"]}</h3>', self.source)
            self.assertIn(f'<p>{question["acceptedAnswer"]["text"]}</p>', self.source)

    def test_roberto_is_available_in_every_hub_surface(self):
        self.assertIn('<option value="roberto">Roberto</option>', self.source)
        self.assertIn('<tr data-character="roberto">', self.source)
        self.assertIn(
            'href="/guides/builds/roberto-best-build/"',
            self.source,
        )
        self.assertIn('href="/guides/characters/roberto-guide"', self.source)

    def test_filter_total_comes_from_rendered_cards(self):
        self.assertIn("const totalCharacterBuilds = characterCards.length;", self.source)
        self.assertIn(
            "Showing ${visibleCards} of ${totalCharacterBuilds} character builds.",
            self.source,
        )
        self.assertIn('id="characterBuildSearch"', self.source)
        self.assertIn('id="characterBuildSelect"', self.source)
        self.assertIn('id="characterBuildRows"', self.source)
        self.assertIn("applyLeaderboardSignalFilter(query);", self.source)

    def test_character_discovery_precedes_ranked_evidence(self):
        quick = self.source.index('id="characterQuickGrid"')
        comparison = self.source.index('id="character-build-comparison-title"')
        leaderboard = self.source.index('id="leaderboard-signals-title"')
        self.assertLess(quick, comparison)
        self.assertLess(comparison, leaderboard)
        self.assertNotIn('class="build-card-compact"', self.source)
        # Keep the Hub lean while allowing the generated 21-entry ItemList and FAQ schemas.
        self.assertLess(len(self.source.encode("utf-8")), 128000)

    def test_version_date_and_leaderboard_signal_are_explicit(self):
        self.assertIn('data-editorial-version="1.0.69"', self.source)
        self.assertIn('<meta name="game-version" content="1.0.69">', self.source)
        self.assertIn('data-build-game-version>Latest game version: v1.0.69</span>', self.source)
        self.assertIn('data-build-manual-review>Build recommendations reviewed for v1.0.69: July 29, 2026</span>', self.source)
        self.assertIn('"dateModified": "2026-08-11"', self.source)
        self.assertIn('article:modified_time" content="2026-08-11T00:00:00+08:00', self.source)
        self.assertIn("latest synchronized Top 100 sample", self.source)
        self.assertIn("MegabonkLeaderboardData.load('/data/leaderboard-meta.json'", self.source)
        self.assertIn("leaderboard-data-loader.js", self.source)
        self.assertIn("Latest Synchronized Leaderboard Build Lab", self.source)
        self.assertIn('id="leaderboardSignalCoverage"', self.source)
        self.assertIn('id="leaderboardSignalUpdated"', self.source)
        self.assertIn('id="leaderboardSignalCache"', self.source)
        self.assertIn("Cache: last-known-good snapshot", self.source)
        self.assertIn("Cache: live synchronized JSON", self.source)
        self.assertIn("Coverage:", self.source)
        self.assertIn("characters · ${supported.length} repeated", self.source)
        self.assertIn('id="leaderboardFilterEmpty"', self.source)
        self.assertIn("Version guard:", self.source)
        self.assertNotIn("current-version Top 100", self.source)

    def test_priority_goal_routes_are_present(self):
        for url in (
            "/leaderboard/builds",
            "/guides/megabonk-beginners-guide",
            "/guides/achievements/300k-kills/",
            "/guides/challenges/afk-challenge/",
        ):
            self.assertIn(f'href="{url}"', self.source)
        self.assertIn("Builds for a Specific Goal", self.source)
        self.assertIn("Build by Playstyle", self.source)

    def test_ranking_intents_are_handed_to_dedicated_pages(self):
        for url in (
            "/tier-lists/weapons/",
            "/tier-lists/tomes/",
            "/tier-lists/items/",
            "/guides/characters/character-tier-list/",
        ):
            self.assertIn(f'href="{url}"', self.source)
        self.assertNotIn('<h2 class="section-title">⚔️ Weapon Tier List</h2>', self.source)
        self.assertNotIn('<h2 class="section-title">📚 Tome Tier List</h2>', self.source)

    def test_stale_meta_claims_and_injected_scripts_are_removed(self):
        self.assertNotIn("Kevin + Mirror Immortality", self.source)
        self.assertNotIn("Holy Trinity", self.source)
        self.assertNotIn("literally immortal", self.source)
        self.assertNotIn("static.cloudflareinsights.com/beacon.min.js", self.source)
        self.assertNotIn("challenge-platform/scripts/jsd/main.js", self.source)
        self.assertNotIn("megabonk.leaderboard.gg/builds", self.source)

    def test_character_guides_and_build_pages_link_both_ways(self):
        catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        for entity in catalog["entities"]["characters"]:
            with self.subTest(character=entity["name"]):
                guide = resolve_page(entity["page"])
                build = resolve_page(entity["buildPage"])
                self.assertIsNotNone(guide)
                self.assertIsNotNone(build)
                self.assertIn(entity["buildPage"], guide.read_text(encoding="utf-8"))
                self.assertIn(entity["page"], build.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
