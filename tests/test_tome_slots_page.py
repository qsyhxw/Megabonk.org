import json
import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "guides" / "unlocks" / "tome-slots" / "index.html"
URL = "https://megabonk.org/guides/unlocks/tome-slots/"


class TomeSlotsPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = PAGE.read_text(encoding="utf-8")
        cls.unlock_hub = (ROOT / "guides" / "unlocks" / "index.html").read_text(
            encoding="utf-8"
        )
        cls.weapon_slots = (
            ROOT / "guides" / "unlocks" / "weapon-slots" / "index.html"
        ).read_text(encoding="utf-8")
        cls.achievements = (
            ROOT / "guides" / "achievements" / "collection-secrets.html"
        ).read_text(encoding="utf-8")

    def test_metadata_owns_tome_slot_intent(self):
        self.assertIn(
            "<title>Megabonk Tome Slots: Unlock the 3rd &amp; 4th Slot</title>",
            self.html,
        )
        self.assertIn(f'<link rel="canonical" href="{URL}">', self.html)
        self.assertIn('<meta name="robots" content="index, follow', self.html)
        self.assertIn("How to Unlock More Tome Slots in Megabonk", self.html)

    def test_current_milestones_and_purchase_boundary_are_explicit(self):
        self.assertIn("Complete <strong>35 Quests</strong>", self.html)
        self.assertIn("Complete <strong>55 Quests</strong>", self.html)
        self.assertIn("does not add the slot immediately", self.html)
        self.assertIn("must still purchase it with Silver", self.html)
        self.assertNotIn("Complete 60 Quests", self.html)
        self.assertNotIn("135 Silver", self.html)

    def test_player_value_modules_are_present(self):
        for anchor in (
            'id="answer"',
            'id="requirements"',
            'id="steps"',
            'id="quest-count"',
            'id="builds"',
            'id="fixes"',
            'id="comparison"',
            'id="faq"',
        ):
            self.assertIn(anchor, self.html)
        self.assertGreaterEqual(self.html.count("<details>"), 6)

    def test_jsonld_contains_article_howto_faq_and_breadcrumbs(self):
        match = re.search(
            r'<script type="application/ld\+json">\s*([\s\S]*?)\s*</script>',
            self.html,
        )
        self.assertIsNotNone(match)
        graph = json.loads(match.group(1))["@graph"]
        types = {node["@type"] for node in graph}
        self.assertTrue(
            {"Article", "WebPage", "HowTo", "FAQPage", "BreadcrumbList"}.issubset(types)
        )
        howto = next(node for node in graph if node["@type"] == "HowTo")
        self.assertEqual(len(howto["step"]), 4)

    def test_tracking_and_ads_match_site_requirements(self):
        self.assertIn("ca-pub-8830315294299920", self.html)
        self.assertIn("G-V5X87M8JFL", self.html)

    def test_related_pages_link_both_ways(self):
        route = 'href="/guides/unlocks/tome-slots/"'
        self.assertIn(route, self.unlock_hub)
        self.assertIn(route, self.weapon_slots)
        self.assertIn(route, self.achievements)
        self.assertIn('href="/guides/unlocks/weapon-slots/"', self.html)
        self.assertIn('href="/guides/unlocks/"', self.html)

    def test_sitemap_and_page_list_include_only_clean_route(self):
        tree = ET.parse(ROOT / "sitemap.xml")
        namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = [node.text for node in tree.findall(".//sm:loc", namespace)]
        self.assertEqual(urls.count(URL), 1)
        self.assertNotIn(f"{URL}index.html", urls)
        pages = (ROOT / "pages_list.txt").read_text(encoding="utf-8").splitlines()
        self.assertEqual(pages.count(URL), 1)


if __name__ == "__main__":
    unittest.main()
