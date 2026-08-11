import html
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGES = {
    "hub": ROOT / "leaderboard" / "index.html",
    "today": ROOT / "leaderboard" / "today.html",
    "recent": ROOT / "leaderboard" / "recent.html",
    "official": ROOT / "leaderboard" / "official.html",
    "builds": ROOT / "leaderboard" / "builds.html",
    "verified": ROOT / "leaderboard" / "verified.html",
}

INTENT_TABS = (
    ("/leaderboard/", "Global Rankings"),
    ("/leaderboard/today", "Today's Rankings"),
    ("/leaderboard/recent", "Recent Submissions"),
    ("/leaderboard/official", "Official Status & Submit"),
    ("/leaderboard/builds", "Ranked Build Data"),
    ("/leaderboard/verified", "Verification Rules"),
)

PRESERVED_TITLES = {
    "hub": "Megabonk Fun: Best Builds & Leaderboard Rankings",
    "today": "Today's Megabonk Leaderboard - Updated Daily Rankings & Trends",
    "recent": "Recent Activity - Latest Megabonk Submissions & Trending Builds",
    "official": "Megabonk.fun Leaderboard Website & Official Leaderboard",
    "builds": "Megabonk Leaderboard Builds – Top 100 Meta Picks",
    "verified": "Megabonk: Legit Leaderboard vs Verified Leaderboard",
}

PRESERVED_META_DESCRIPTIONS = {
    "hub": "Discover the most fun Megabonk builds and compete on our leaderboard! View top player rankings, world records, and meta strategies to dominate.",
    "today": "View today's Megabonk leaderboard with live rankings, daily top scores, trending builds, and recent player achievements. Updated every 5 minutes with real-time data.",
    "recent": "View the latest Megabonk player submissions from the last 7 days. See recent high scores, trending builds, and active players updated every 5 minutes.",
    "official": "Compare Steam's official leaderboard with the VOD-verified megabonk.fun leaderboard. Rules, submission, and verification on the leaderboard website.",
    "builds": "Explore Megabonk leaderboard builds from the top 100. See current meta weapons, tomes, and items, with quick links to character build guides.",
    "verified": "Compare the official Steam legit leaderboard to the community VOD verified leaderboard. Rules, anti-cheat, video proof, and how to submit runs.",
}

PRESERVED_H1 = {
    "hub": "🏆 Global Leaderboard",
    "today": "📅 Today's Leaderboard",
    "recent": "🔥 Recent Activity",
    "official": "🏆 Megabonk Leaderboards &amp; Submission Guide",
    "builds": "🏗️ Leaderboard Builds",
    "verified": "✅ How Verified Megabonk Leaderboard Runs Work",
}


class AnchorParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.current = None
        self.anchors = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.current = {"href": dict(attrs).get("href", ""), "text": []}

    def handle_data(self, data):
        if self.current is not None:
            self.current["text"].append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self.current is not None:
            self.current["text"] = " ".join("".join(self.current["text"]).split())
            self.anchors.append(self.current)
            self.current = None


class LeaderboardIntentArchitectureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = {name: path.read_text(encoding="utf-8") for name, path in PAGES.items()}

    def test_tdk_is_unchanged_during_low_risk_phase(self):
        for name, title in PRESERVED_TITLES.items():
            with self.subTest(page=name):
                self.assertIn(f"<title>{title}</title>", self.sources[name])
                self.assertIn(
                    f'<meta name="description" content="{PRESERVED_META_DESCRIPTIONS[name]}">',
                    self.sources[name],
                )
                self.assertIn(f"<h1>{PRESERVED_H1[name]}</h1>", self.sources[name])

    def test_all_pages_use_the_same_intent_labeled_tabs(self):
        for name, source in self.sources.items():
            with self.subTest(page=name):
                match = re.search(
                    r'<nav class="lb-intent-tabs"[^>]*>(.*?)</nav>', source, re.DOTALL
                )
                self.assertIsNotNone(match)
                tabs = [
                    (href, html.unescape(re.sub(r"<[^>]+>", "", label)).strip())
                    for href, label in re.findall(
                        r'<a href="([^"]+)"[^>]*>(.*?)</a>', match.group(1), re.DOTALL
                    )
                ]
                self.assertEqual(tabs, list(INTENT_TABS))

    def test_visible_internal_links_are_root_relative(self):
        for name, source in self.sources.items():
            with self.subTest(page=name):
                self.assertNotRegex(source, r'<a\b[^>]*href="https://megabonk\.org(?:/|\")')
                self.assertNotRegex(source, r'<a\b[^>]*href="\.\.?/')
                self.assertRegex(source, r'<link rel="canonical" href="https://megabonk\.org/')

    def test_subpages_do_not_repeat_bare_leaderboard_anchors(self):
        for name, source in self.sources.items():
            parser = AnchorParser()
            parser.feed(source)
            bare = [
                anchor for anchor in parser.anchors
                if anchor["text"] in {"Leaderboard", "Megabonk Leaderboard"}
            ]
            with self.subTest(page=name):
                # One global-header navigation label is intentional.
                self.assertLessEqual(len(bare), 1)

    def test_each_surface_states_its_unique_role(self):
        expected = {
            "hub": "All-time global rankings and the main entry point",
            "today": "New records first seen during the rolling past 24 hours",
            "recent": "Newest community submissions by source time",
            "official": "This page explains the official Steam status and where community runs are actually submitted.",
            "verified": "This page explains evidence rules and what verified status means.",
            "builds": "Weapons, Tomes and item patterns found in ranked runs",
        }
        for name, text in expected.items():
            with self.subTest(page=name):
                self.assertIn(text, self.sources[name])

    def test_official_and_verified_handoff_instead_of_competing(self):
        official = self.sources["official"]
        verified = self.sources["verified"]
        self.assertIn(
            '<a href="/leaderboard/verified">Verification Rules</a>', official
        )
        self.assertIn(
            '<a href="/leaderboard/official">Official Status &amp; Submit</a>', verified
        )
        self.assertIn("Find Submission Destination", verified)
        self.assertNotIn(
            'href="https://megabonk.leaderboard.gg/" target="_blank" rel="noopener noreferrer" class="cta-button"',
            verified,
        )

    def test_ranked_build_page_hands_off_character_intent(self):
        builds = self.sources["builds"]
        self.assertIn("buildUrl: shared.buildPage", builds)
        self.assertIn('href="${buildUrl}" class="btn-build"', builds)
        self.assertIn("Full ${escapeHtml(char.name)} Build Guide", builds)
        self.assertIn("use each character's Best Build page", builds)
        self.assertIn("View Global Rankings", builds)


if __name__ == "__main__":
    unittest.main()
