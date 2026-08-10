import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "tr" / "guides" / "characters" / "fox-kitsune-guide.html"


class TurkishFoxLocalizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = PAGE.read_text(encoding="utf-8")
        visible = re.sub(r"<script\b[\s\S]*?</script>", "", cls.html, flags=re.I)
        visible = re.sub(r"<style\b[\s\S]*?</style>", "", visible, flags=re.I)
        cls.visible = re.sub(r"<[^>]+>", " ", visible)

    def test_language_and_hreflang_are_consistent(self):
        self.assertIn('<html lang="tr">', self.html)
        self.assertNotIn('<html lang="zh-CN">', self.html)
        self.assertIn(
            '<link rel="canonical" href="https://megabonk.org/tr/guides/characters/fox-kitsune-guide">',
            self.html,
        )
        self.assertIn('hreflang="en"', self.html)
        self.assertIn('hreflang="tr"', self.html)
        self.assertIn('hreflang="x-default"', self.html)

    def test_tdk_and_visible_copy_are_turkish(self):
        self.assertIn(
            "<title>Fox (Kitsune) Rehberi: Pasif, Silah ve Kilit Açma</title>",
            self.html,
        )
        self.assertIn("Hızlı Cevap", self.visible)
        self.assertIn("Sık Sorulan Sorular", self.visible)
        self.assertIn("Fox'un Şans Pasifi Nasıl Çalışır?", self.visible)
        self.assertNotIn("The Best Starting Character for Beginners", self.visible)
        self.assertNotIn(">Home<", self.html)

    def test_schema_declares_turkish_article_and_faq(self):
        match = re.search(
            r'<script type="application/ld\+json">\s*([\s\S]*?)\s*</script>',
            self.html,
        )
        self.assertIsNotNone(match)
        data = json.loads(match.group(1))
        graph = data["@graph"]
        article = next(node for node in graph if node["@type"] == "Article")
        faq = next(node for node in graph if node["@type"] == "FAQPage")
        self.assertEqual(article["inLanguage"], "tr")
        self.assertEqual(len(faq["mainEntity"]), 4)

    def test_uses_local_character_image_and_single_beacon(self):
        self.assertIn('src="/images/guides/characters/Fox.png"', self.html)
        self.assertEqual(self.html.count("static.cloudflareinsights.com/beacon"), 1)


if __name__ == "__main__":
    unittest.main()
