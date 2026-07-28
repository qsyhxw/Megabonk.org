import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TIER = ROOT / "guides/characters/character-tier-list/index.html"
HUB = ROOT / "guides/characters/index.html"


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
        self.assertNotIn("Tier List", title)
        self.assertNotIn("Tier List", h1)
        self.assertIn("21 characters + tier list", self.hub)
        self.assertIn("id: 'roberto'", self.hub)

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
