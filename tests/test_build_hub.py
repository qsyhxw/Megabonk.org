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
        rows = re.findall(r'<tr data-character="[^"]+">', self.source)
        cards = re.findall(r'<article class="character-quick-card" data-character="[^"]+">', self.source)
        self.assertEqual(len(rows), 21)
        self.assertEqual(len(cards), 21)
        self.assertNotIn("all 20 Megabonk characters", self.source)
        self.assertNotIn("Showing all 20 character builds", self.source)
        self.assertIn('<div class="stat-number">21</div>', self.source)
        self.assertIn('<div class="stat-number">21/21</div>', self.source)

    def test_roberto_is_available_in_every_hub_surface(self):
        self.assertIn("<option>Roberto</option>", self.source)
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
        self.assertLess(len(self.source.encode("utf-8")), 125000)

    def test_version_date_and_leaderboard_signal_are_explicit(self):
        self.assertIn('data-editorial-version="1.0.69"', self.source)
        self.assertIn('"dateModified": "2026-08-11"', self.source)
        self.assertIn('article:modified_time" content="2026-08-11T00:00:00+08:00', self.source)
        self.assertIn("Build recommendations reviewed: July 29, 2026", self.source)
        self.assertIn("latest synchronized Top 100 sample", self.source)
        self.assertIn("MegabonkLeaderboardData.load('/data/leaderboard-meta.json'", self.source)
        self.assertIn("leaderboard-data-loader.js", self.source)
        self.assertIn("Latest Synchronized Leaderboard Build Lab", self.source)
        self.assertIn('id="leaderboardSignalCoverage"', self.source)
        self.assertIn("characters with repeated evidence", self.source)
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
