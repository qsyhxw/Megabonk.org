import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAPS = ROOT / "guides/maps/index.html"
SHRINES = ROOT / "guides/mechanics/shrines/index.html"
WRENCH = ROOT / "database/items/wrench.html"
BEACON = ROOT / "database/items/beacon.html"
SITEMAP = ROOT / "sitemap.xml"


class H1Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.h1 = 0

    def handle_starttag(self, tag, attrs):
        if tag == "h1":
            self.h1 += 1


def page_meta(html):
    title = re.search(r"<title>(.*?)</title>", html, re.S).group(1)
    description = re.search(r'<meta name="description" content="(.*?)"\s*/?>', html, re.S).group(1)
    return title, description


def assert_jsonld(testcase, html):
    blocks = re.findall(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', html, re.S)
    testcase.assertTrue(blocks)
    for block in blocks:
        json.loads(block)


class MapsShrinesArchitectureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.maps = MAPS.read_text(encoding="utf-8")
        cls.shrines = SHRINES.read_text(encoding="utf-8")
        cls.wrench = WRENCH.read_text(encoding="utf-8")
        cls.beacon = BEACON.read_text(encoding="utf-8")
        cls.sitemap = SITEMAP.read_text(encoding="utf-8")

    def test_titles_and_h1s_remain_stable(self):
        self.assertEqual(page_meta(self.maps)[0], "Megabonk Maps Guide – Forest & Desert Tiers and Bosses")
        self.assertEqual(page_meta(self.shrines)[0], "Megabonk Shrines Guide: Charge, Greed & Boss Curse")
        for html in (self.maps, self.shrines):
            parser = H1Parser()
            parser.feed(html)
            self.assertEqual(parser.h1, 1)
        for html in (self.maps, self.shrines, self.wrench, self.beacon):
            title, description = page_meta(html)
            self.assertLessEqual(len(title), 60)
            self.assertLessEqual(len(description), 155)

    def test_maps_owns_distribution_and_links_to_mechanics(self):
        self.assertIn('<h2>Shrine Distribution by Map</h2>', self.maps)
        self.assertIn('/guides/mechanics/shrines/', self.maps)
        self.assertIn('Forest</strong>', self.maps)
        self.assertIn('Desert</strong>', self.maps)
        self.assertIn('Graveyard / Crypt route', self.maps)
        self.assertNotIn('Every stage contains exactly', self.maps)
        self.assertNotIn('Each stage has exactly 15', self.maps)
        self.assertNotIn('Shrines Per Stage', self.maps)
        self.assertIn('Shrine Layout', self.maps)
        self.assertNotIn('<h3>Shrine Types</h3>', self.maps)

    def test_shrines_owns_types_rewards_unlocks_and_related_links(self):
        for fragment in ('Charge vs Greed vs Boss Curse', 'Shrine-Related Unlocks', 'Beacon and Wrench', 'Shrines FAQ'):
            self.assertIn(fragment, self.shrines)
        for href in ('/guides/maps/', '/guides/maps/graveyard/', '/guides/bosses/boss-curse-explained.html', '/database/items/beacon.html', '/database/items/wrench.html', '/guides/mechanics/'):
            self.assertIn(f'href="{href}"', self.shrines)
        self.assertIn('Shrine Distribution and Map Routing', self.shrines)
        self.assertIn('dateModified": "2026-07-28"', self.shrines)

    def test_wrench_value_is_consistent(self):
        combined = "\n".join((self.shrines, self.wrench, self.beacon))
        self.assertNotRegex(combined, r"4 seconds|four seconds|4s faster|-4s")
        self.assertIn('Charge Shrines charge 4% faster', self.wrench)
        self.assertIn('<div class="stat-value">+4%</div>', self.wrench)
        self.assertIn('+7.5%', self.wrench)

    def test_jsonld_and_sitemap_dates(self):
        assert_jsonld(self, self.maps)
        assert_jsonld(self, self.shrines)
        assert_jsonld(self, self.wrench)
        for url in ('database/items/beacon.html', 'database/items/wrench.html', 'guides/maps/', 'guides/mechanics/shrines/'):
            pattern = rf'<loc>https://megabonk.org/{re.escape(url)}</loc>\s*<lastmod>2026-07-28</lastmod>'
            self.assertRegex(self.sitemap, pattern)


if __name__ == "__main__":
    unittest.main()
