import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGE_PATH = ROOT / "database" / "tomes" / "golden-tome.html"
HUB_PATH = ROOT / "database" / "tomes" / "index.html"
SITEMAP_PATH = ROOT / "sitemap.xml"

TITLE = "Golden Tome (Gold Gain) – Effects, Unlock & Farming"
URL = "https://megabonk.org/database/tomes/golden-tome"
IMAGE_URL = "https://megabonk.org/images/Tomes/Golden_Tome.png"


class GoldenTomeMetadataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = PAGE_PATH.read_text(encoding="utf-8")
        cls.hub = HUB_PATH.read_text(encoding="utf-8")
        cls.sitemap = SITEMAP_PATH.read_text(encoding="utf-8")

    def test_title_h1_and_canonical_use_complete_name(self):
        self.assertIn(f"<title>{TITLE}</title>", self.page)
        self.assertNotIn("<title>olden Tome", self.page)
        self.assertRegex(self.page, r"<h1[^>]*>[^<]*Golden Tome</h1>")
        self.assertIn(f'<link rel="canonical" href="{URL}">', self.page)

    def test_open_graph_metadata_matches_page(self):
        self.assertIn(f'<meta property="og:title" content="{TITLE}">', self.page)
        self.assertIn(f'<meta property="og:url" content="{URL}">', self.page)
        self.assertIn(f'<meta property="og:image" content="{IMAGE_URL}">', self.page)
        self.assertTrue((ROOT / "images" / "Tomes" / "Golden_Tome.png").is_file())

    def test_article_schema_uses_complete_name_and_current_date(self):
        blocks = re.findall(
            r'<script type="application/ld\+json">\s*(.*?)\s*</script>',
            self.page,
            re.S,
        )
        self.assertTrue(blocks)
        graphs = [json.loads(block) for block in blocks]
        entities = []
        for graph in graphs:
            entities.extend(graph.get("@graph", [graph]))

        article = next(entity for entity in entities if entity.get("@type") == "Article")
        self.assertEqual(article["headline"], TITLE)
        self.assertEqual(article["name"], "Golden Tome")
        self.assertEqual(article["mainEntityOfPage"], URL)
        self.assertEqual(article["dateModified"], "2026-07-29")

        breadcrumbs = next(
            entity for entity in entities if entity.get("@type") == "BreadcrumbList"
        )
        self.assertEqual(breadcrumbs["itemListElement"][-1]["name"], "Golden Tome")
        self.assertEqual(breadcrumbs["itemListElement"][-1]["item"], URL)

    def test_hub_link_and_sitemap_follow_url_policy(self):
        self.assertIn(f'href="{URL}" class="tome-card"', self.hub)
        self.assertNotIn(f'href="{URL}/"', self.hub)
        entry = re.search(
            rf"<url>\s*<loc>{re.escape(URL)}</loc>\s*"
            r"<lastmod>([^<]+)</lastmod>",
            self.sitemap,
        )
        self.assertIsNotNone(entry)
        self.assertEqual(entry.group(1), "2026-07-29")


if __name__ == "__main__":
    unittest.main()
