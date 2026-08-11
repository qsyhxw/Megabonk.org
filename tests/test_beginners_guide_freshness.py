import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "guides" / "megabonk-beginners-guide.html"
SITEMAP = ROOT / "sitemap.xml"


class BeginnersGuideFreshnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = PAGE.read_text(encoding="utf-8")
        cls.sitemap = SITEMAP.read_text(encoding="utf-8")

    def test_existing_search_metadata_and_h1_stay_stable(self):
        self.assertIn(
            "<title>Megabonk Beginners Guide 2026 – Tips, Builds &amp; First Wins</title>".replace("&amp;", "&"),
            self.source,
        )
        self.assertIn(
            '<meta name="description" content="New to Megabonk? This complete beginners guide explains core mechanics, best starter characters, simple builds, and step-by-step tips to survive your first runs and achieve victory.">',
            self.source,
        )
        self.assertRegex(
            self.source,
            r"<h1>Megabonk Beginners Guide 2026 .+ Start Winning Your First Runs</h1>",
        )

    def test_publication_timeline_matches_repository_history(self):
        self.assertNotIn("January 2025", self.source)
        self.assertNotIn('"datePublished": "2025-01-15"', self.source)
        self.assertIn("originally published on November 14, 2025", self.source)
        self.assertIn(
            '<meta property="article:published_time" content="2025-11-14T11:51:12+08:00">',
            self.source,
        )

        schemas = [
            json.loads(block)
            for block in re.findall(
                r'<script type="application/ld\+json">\s*(.*?)\s*</script>',
                self.source,
                re.S,
            )
        ]
        graph = next(schema["@graph"] for schema in schemas if "@graph" in schema)
        article = next(entity for entity in graph if entity.get("@type") == "Article")
        self.assertEqual("2025-11-14", article["datePublished"])
        self.assertEqual("2026-08-11", article["dateModified"])

    def test_current_roster_counts_and_review_date_are_visible(self):
        for current in ("21 playable characters", "30 weapons", "85 items"):
            self.assertIn(current, self.source)
        for stale in (
            "20 playable characters",
            "29 weapons",
            "around 29",
            "over 70 items",
            "78+",
            "late 2025",
        ):
            self.assertNotIn(stale, self.source)
        self.assertIn("manually reviewed for v1.0.69 on August 11, 2026", self.source)
        self.assertIn(
            '<meta property="article:modified_time" content="2026-08-11T00:00:00+08:00">',
            self.source,
        )

    def test_sitemap_lastmod_matches_review(self):
        entry = re.search(
            r"<loc>https://megabonk\.org/guides/megabonk-beginners-guide</loc>\s*"
            r"<lastmod>([^<]+)</lastmod>",
            self.sitemap,
        )
        self.assertIsNotNone(entry)
        self.assertEqual("2026-08-11", entry.group(1))


if __name__ == "__main__":
    unittest.main()
