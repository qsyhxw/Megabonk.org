from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PRIMARY_ROUTE = "/guides/builds/bow-pierce-arc"
TYPO_ROUTE = "/guides/builds/ow-pierce-arc"


class BowBuildConsolidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.redirects = (ROOT / "_redirects").read_text(encoding="utf-8")
        cls.sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
        cls.pages = (ROOT / "pages_list.txt").read_text(encoding="utf-8")
        cls.fallback = (ROOT / "guides" / "builds" / "ow-pierce-arc.html").read_text(encoding="utf-8")
        cls.primary = (ROOT / "guides" / "builds" / "bow-pierce-arc.html").read_text(encoding="utf-8")

    def test_typo_routes_redirect_to_primary_clean_url(self):
        for source in (TYPO_ROUTE, f"{TYPO_ROUTE}.html"):
            self.assertIn(f"{source} {PRIMARY_ROUTE} 301", self.redirects)

    def test_typo_route_is_not_submitted(self):
        self.assertNotIn(TYPO_ROUTE, self.sitemap)
        self.assertNotIn(TYPO_ROUTE, self.pages)
        self.assertIn(f"https://megabonk.org{PRIMARY_ROUTE}", self.sitemap)

    def test_internal_links_do_not_target_typo_route(self):
        fallback_path = ROOT / "guides" / "builds" / "ow-pierce-arc.html"
        for path in ROOT.rglob("*.html"):
            if path == fallback_path:
                continue
            with self.subTest(page=str(path.relative_to(ROOT))):
                self.assertNotIn(TYPO_ROUTE, path.read_text(encoding="utf-8"))
    def test_typo_file_is_only_a_safe_redirect_fallback(self):
        self.assertIn('<meta name="robots" content="noindex, follow">', self.fallback)
        self.assertIn(f'<link rel="canonical" href="https://megabonk.org{PRIMARY_ROUTE}">', self.fallback)
        self.assertIn(f'content="0; url={PRIMARY_ROUTE}"', self.fallback)
        self.assertNotIn("Live reload enabled", self.fallback)
        self.assertNotIn("Build Overview", self.fallback)

    def test_primary_page_metadata_is_unchanged(self):
        self.assertIn("<title>Megabonk Bow Build 2026: Piercing & Revolver Combo</title>", self.primary)
        self.assertIn(f'<link rel="canonical" href="https://megabonk.org{PRIMARY_ROUTE}"', self.primary)


if __name__ == "__main__":
    unittest.main()
