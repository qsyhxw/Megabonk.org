import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TIER = ROOT / "guides/characters/character-tier-list/index.html"
HUB = ROOT / "guides/characters/index.html"
LEGACY_KNIGHT = ROOT / "guides/characters/knight-beginner-guide.html"
SITEMAP = ROOT / "sitemap.xml"


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.h1 = 0
        self.cards = []
        self.actions = {}
        self.current_card = None
        self.canonical = []

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        classes = set(data.get("class", "").split())
        if tag == "h1":
            self.h1 += 1
        if tag == "link" and data.get("rel") == "canonical":
            self.canonical.append(data.get("href"))
        if tag == "div" and "character-card" in classes:
            self.current_card = data.get("id")
            self.cards.append(self.current_card)
            self.actions[self.current_card] = []
        if tag == "a" and self.current_card and "character-action" in classes:
            self.actions[self.current_card].append(data.get("href"))


def local_target(href):
    path = href.split("?", 1)[0].split("#", 1)[0]
    if path.startswith("https://megabonk.org"):
        path = path[len("https://megabonk.org"):]
    candidate = ROOT / path.lstrip("/")
    options = [candidate, candidate.with_suffix(".html"), candidate / "index.html"]
    return next((item for item in options if item.is_file()), None)


class CharacterTierArchitectureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tier = TIER.read_text(encoding="utf-8")
        cls.hub = HUB.read_text(encoding="utf-8")
        cls.parser = PageParser()
        cls.parser.feed(cls.tier)

    def test_hub_owns_character_directory_intent(self):
        title = re.search(r"<title>(.*?)</title>", self.hub, re.S).group(1)
        h1 = re.search(r"<h1>(.*?)</h1>", self.hub, re.S).group(1)
        description = re.search(r'<meta name="description" content="(.*?)">', self.hub, re.S).group(1)
        self.assertEqual(title, "Megabonk Characters 2026 – Unlocks, Passives & Guides")
        self.assertEqual(description, "Browse Megabonk characters with unlock requirements, starting weapons, passives, individual guides and build links for every playable character.")
        self.assertEqual(h1, "🎮 Megabonk Characters, Unlocks & Guides")
        self.assertNotIn("Tier List", title)
        self.assertNotIn("Tier List", h1)
        self.assertIn('id="characterTableBody"', self.hub)
        self.assertIn('of <strong>21</strong> characters in both the directory and guide cards', self.hub)
        self.assertNotIn('data-filter="tier"', self.hub)
        self.assertNotIn('tierBadge', self.hub)
        self.assertIn("id: 'roberto'", self.hub)
        self.assertIn("aliases: ['robong']", self.hub)
        self.assertNotIn("createCharacterTable", self.hub)
        self.assertLess(self.hub.index('id="searchInput"'), self.hub.index('id="characterTableBody"'))
        self.assertIn("document.querySelectorAll('#characterTableBody tr')", self.hub)
        self.assertIn("Warrior: +1.5% Damage per level", self.hub)

    def test_hub_table_has_complete_guide_build_and_weapon_targets(self):
        tbody = re.search(r'<tbody id="characterTableBody">(.*?)</tbody>', self.hub, re.S).group(1)
        rows = re.findall(r'<tr data-character-id="([^"]+)"', tbody)
        self.assertEqual(len(rows), 21)
        self.assertEqual(len(set(rows)), 21)
        guide_links = re.findall(r'<a class="table-action" href="([^"]+)">Character Guide</a>', tbody)
        build_links = re.findall(r'<a class="table-action" href="([^"]+)">Best Build</a>', tbody)
        weapon_links = re.findall(r'<td><a href="([^"]+)">[^<]+</a></td>', tbody)
        self.assertEqual(len(guide_links), 21)
        self.assertEqual(len(build_links), 21)
        self.assertEqual(len(weapon_links), 21)
        for href in [*guide_links, *build_links, *weapon_links]:
            self.assertTrue(href.startswith("/"), href)
            self.assertNotIn(".html", href)
            self.assertIsNotNone(local_target(href), href)

    def test_hub_table_is_crawlable_and_current(self):
        tbody = re.search(r'<tbody id="characterTableBody">(.*?)</tbody>', self.hub, re.S).group(1)
        self.assertEqual(tbody.count('data-difficulty="'), 21)
        self.assertEqual(tbody.count('data-search="'), 21)
        self.assertEqual(tbody.count('loading="lazy"'), 21)
        self.assertEqual(tbody.count('decoding="async"'), 21)
        self.assertNotIn('alt=""', tbody)
        self.assertIn('Last reviewed: August 11, 2026', self.hub)
        self.assertIn('Verified through Game Version 1.0.69', self.hub)
        sitemap = SITEMAP.read_text(encoding="utf-8")
        marker = '<loc>https://megabonk.org/guides/characters/</loc>'
        block = sitemap[sitemap.index(marker):sitemap.index('</url>', sitemap.index(marker))]
        self.assertIn('<lastmod>2026-08-11</lastmod>', block)

    def test_legacy_knight_page_does_not_compete_with_sir_oofie(self):
        legacy = LEGACY_KNIGHT.read_text(encoding="utf-8")
        sitemap = SITEMAP.read_text(encoding="utf-8")
        self.assertIn('<meta name="robots" content="noindex, follow">', legacy)
        self.assertIn('href="https://megabonk.org/guides/characters/sir-oofie-guide"', legacy)
        self.assertNotIn('/guides/characters/knight-beginner-guide.html</loc>', sitemap)

    def test_tier_page_has_21_characters_and_current_baseline(self):
        self.assertEqual(self.parser.h1, 1)
        self.assertEqual(len(self.parser.cards), 21)
        self.assertEqual(len(set(self.parser.cards)), 21)
        self.assertIn("roberto", self.parser.cards)
        self.assertNotIn("v1.0.64", self.tier)
        self.assertIn("Patch baseline v1.0.69", self.tier)
        self.assertEqual(self.parser.canonical, ["https://megabonk.org/guides/characters/character-tier-list/"])

    def test_each_ranked_character_links_to_guide_and_build(self):
        for card, hrefs in self.parser.actions.items():
            self.assertEqual(len(hrefs), 2, card)
            for href in hrefs:
                self.assertIsNotNone(local_target(href), f"{card}: {href}")

    def test_metadata_and_jsonld(self):
        title = re.search(r"<title>(.*?)</title>", self.tier, re.S).group(1)
        description = re.search(r'<meta name="description" content="(.*?)">', self.tier, re.S).group(1)
        self.assertLessEqual(len(title), 60)
        self.assertLessEqual(len(description), 155)
        blocks = re.findall(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', self.tier, re.S)
        parsed = [json.loads(block) for block in blocks]
        item_list = next(item for item in parsed if item.get("@type") == "ItemList")
        self.assertEqual(item_list["numberOfItems"], 21)
        positions = [item["position"] for item in item_list["itemListElement"]]
        self.assertEqual(positions, list(range(1, 22)))

    def test_mode_and_live_evidence_sections(self):
        self.assertIn('id="mode-guide-title"', self.tier)
        self.assertIn('id="characterSignalGrid"', self.tier)
        self.assertIn("/data/character-build-signals.json", self.tier)
        self.assertIn("/data/entity-catalog.json", self.tier)
        self.assertIn("This is supporting evidence, not an automatic tier list", self.tier)


if __name__ == "__main__":
    unittest.main()
