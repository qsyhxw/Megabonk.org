import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ComponentRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.redirects = (ROOT / "_redirects").read_text(encoding="utf-8")
        cls.headers = (ROOT / "_headers").read_text(encoding="utf-8")
        cls.aura = (ROOT / "database" / "weapons" / "aura.html").read_text(
            encoding="utf-8"
        )
        cls.sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
        cls.pages = (ROOT / "pages_list.txt").read_text(encoding="utf-8")

    def test_old_component_pages_are_not_deployable_html_files(self):
        self.assertFalse(
            (ROOT / "components" / "top-runs-section-horizontal.html").exists()
        )
        self.assertFalse((ROOT / "components" / "top-runs-sidebar.html").exists())
        self.assertTrue(
            (
                ROOT
                / "components"
                / "top-runs-section-horizontal.fragment.txt"
            ).exists()
        )
        self.assertTrue(
            (ROOT / "components" / "top-runs-sidebar.fragment.txt").exists()
        )

    def test_public_component_urls_redirect_to_leaderboard(self):
        for slug in ("top-runs-section-horizontal", "top-runs-sidebar"):
            for suffix in ("", "/", ".html"):
                rule = f"/components/{slug}{suffix} /leaderboard/ 301"
                self.assertIn(rule, self.redirects)

    def test_aura_fetches_fragment_not_public_page_route(self):
        self.assertIn(
            "fetch('/components/top-runs-section-horizontal.fragment.txt')",
            self.aura,
        )
        self.assertNotIn(
            "fetch('/components/top-runs-section-horizontal.html')", self.aura
        )

    def test_component_assets_remain_noindex_and_out_of_sitemap(self):
        self.assertIn("/components/*", self.headers)
        self.assertIn("X-Robots-Tag: noindex", self.headers)
        self.assertNotIn("https://megabonk.org/components/", self.sitemap)
        self.assertNotIn("https://megabonk.org/components/", self.pages)


if __name__ == "__main__":
    unittest.main()
