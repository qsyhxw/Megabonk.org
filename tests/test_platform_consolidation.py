import json
import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLATFORMS = ROOT / "faq" / "megabonk-platforms.html"
CONSOLE = ROOT / "faq" / "is-megabonk-on-console.html"


class PlatformConsolidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.platforms = PLATFORMS.read_text(encoding="utf-8")
        cls.console = CONSOLE.read_text(encoding="utf-8")
        cls.redirects = (ROOT / "_redirects").read_text(encoding="utf-8")
        cls.sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
        cls.pages = (ROOT / "pages_list.txt").read_text(encoding="utf-8")
        cls.generator = (ROOT / "generate_sitemap.py").read_text(encoding="utf-8")

    def test_ranking_tdk_and_primary_url_are_preserved(self):
        self.assertIn(
            "<title>Megabonk Platforms 2026: Is it on Switch, Xbox, or PS5?</title>",
            self.platforms,
        )
        self.assertIn(
            "Looking to play Megabonk on console? Here is the latest 2026 update",
            self.platforms,
        )
        self.assertIn("<h1>Megabonk Platforms Guide</h1>", self.platforms)
        self.assertIn(
            '<link rel="canonical" href="https://megabonk.org/faq/megabonk-platforms">',
            self.platforms,
        )

    def test_platform_table_answers_all_target_intents(self):
        for platform in (
            "Windows PC",
            "Linux",
            "Steam Deck",
            "macOS",
            "PS5 / PS4",
            "Xbox Series X|S / Xbox One",
            "Nintendo Switch",
            "Nintendo Switch 2",
            "Android",
            "iOS / iPadOS",
        ):
            self.assertIn(platform, self.platforms)
        self.assertIn("Last verified: July 29, 2026", self.platforms)
        self.assertGreaterEqual(self.platforms.count('datetime="2026-07-29"'), 10)

    def test_page_uses_current_factual_status_without_predictions(self):
        self.assertIn("Steam Deck Verified", self.platforms)
        self.assertIn("full controller support", self.platforms)
        self.assertNotIn("Optimistic scenario", self.platforms)
        self.assertNotIn("Vampire Survivors", self.platforms)
        self.assertNotIn("$50,000", self.platforms)

    def test_structured_data_is_valid(self):
        blocks = re.findall(
            r'<script type="application/ld\+json">\s*(.*?)\s*</script>',
            self.platforms,
            flags=re.DOTALL,
        )
        self.assertEqual(len(blocks), 1)
        graph = json.loads(blocks[0])["@graph"]
        types = {entry["@type"] for entry in graph}
        self.assertEqual(types, {"WebPage", "BreadcrumbList", "FAQPage"})

    def test_broken_turkish_hreflang_is_removed(self):
        self.assertIn('hreflang="en"', self.platforms)
        self.assertIn('hreflang="x-default"', self.platforms)
        self.assertNotIn('hreflang="tr"', self.platforms)

    def test_console_page_is_only_a_noindex_fallback(self):
        self.assertIn('<meta name="robots" content="noindex, follow">', self.console)
        self.assertIn('url=/faq/megabonk-platforms', self.console)
        self.assertNotIn("Why Isn't Megabonk on Consoles Yet?", self.console)

    def test_all_console_variants_redirect_to_primary_page(self):
        for source in (
            "/faq/is-megabonk-on-console",
            "/faq/is-megabonk-on-console/",
            "/faq/is-megabonk-on-console.html",
            "/faq/is-megabonk-on-console/*",
        ):
            self.assertIn(f"{source} /faq/megabonk-platforms 301", self.redirects)
        self.assertIn(
            "/faq/megabonk-platforms.html /faq/megabonk-platforms 301",
            self.redirects,
        )

    def test_sitemap_is_well_formed_xml(self):
        ET.parse(ROOT / "sitemap.xml")
    def test_sitemap_and_page_list_only_submit_primary_url(self):
        primary = "https://megabonk.org/faq/megabonk-platforms"
        self.assertIn(f"<loc>{primary}</loc>", self.sitemap)
        self.assertIn(primary, self.pages)
        for retired in (
            "https://megabonk.org/faq/is-megabonk-on-console.html",
            "https://megabonk.org/faq/megabonk-platforms.html",
        ):
            self.assertNotIn(retired, self.sitemap)
            self.assertNotIn(retired, self.pages)

    def test_sitemap_generator_keeps_consolidation(self):
        self.assertIn("'faq/is-megabonk-on-console.html',", self.generator)
        self.assertIn(
            "'faq/megabonk-platforms.html': '/faq/megabonk-platforms',",
            self.generator,
        )

    def test_internal_platform_link_uses_canonical_url(self):
        download = (ROOT / "download" / "megabonk.html").read_text(encoding="utf-8")
        self.assertIn('href="/faq/megabonk-platforms"', download)
        self.assertNotIn('href="/faq/megabonk-platforms.html"', download)


if __name__ == "__main__":
    unittest.main()