import json
import importlib.util
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TIER = ROOT / "guides/characters/character-tier-list/index.html"
HUB = ROOT / "guides/characters/index.html"
LEGACY_KNIGHT = ROOT / "guides/characters/knight-beginner-guide.html"
SITEMAP = ROOT / "sitemap.xml"
CATALOG = ROOT / "data/entity-catalog.json"
CHARACTER_SOURCE = ROOT / "data/characters.json"
GENERATOR = ROOT / "scripts/build_characters_hub.py"


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
        self.assertIn('data-character-id="roberto"', self.hub)
        self.assertIn('data-search="roberto robong', self.hub)
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

    def test_hub_cards_are_neutral_and_have_two_clear_routes(self):
        card_template = re.search(r"card\.innerHTML = `(.*?)`;", self.hub, re.S).group(1)
        self.assertIn('Character Profile', card_template)
        self.assertIn('class="character-role"', card_template)
        self.assertIn('<dt>Passive</dt>', card_template)
        self.assertIn('<dt>Starting Weapon</dt>', card_template)
        self.assertIn('<dt>How to Unlock</dt>', card_template)
        self.assertIn('card-action-guide">Character Guide</a>', card_template)
        self.assertIn('card-action-build">Best Build</a>', card_template)
        self.assertNotIn('tier-badge', card_template)
        self.assertNotIn('radar', card_template.lower())
        self.assertNotIn('compare-btn', card_template)
        self.assertNotIn('char.description', card_template)
        self.assertNotIn('char.features', card_template)

    def test_hub_card_images_and_mobile_table_are_resilient(self):
        self.assertIn("sourceImage.getAttribute('src')", self.hub)
        self.assertIn('width="120" height="120" loading="lazy" decoding="async"', self.hub)
        self.assertIn('.character-table th:first-child,', self.hub)
        self.assertIn('position: sticky;', self.hub)
        self.assertIn('left: 0;', self.hub)

    def test_hub_supports_shareable_character_and_difficulty_filters(self):
        self.assertIn("initialParams.get('character')", self.hub)
        self.assertIn("initialParams.get('difficulty')", self.hub)
        self.assertIn("params.set('character', currentFilters.search)", self.hub)
        self.assertIn("params.set('difficulty', currentFilters.difficulty)", self.hub)
        self.assertIn("history.replaceState", self.hub)
        self.assertIn("applyFilters({ updateUrl: false })", self.hub)

    def test_hub_structured_data_matches_21_character_guides(self):
        blocks = re.findall(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', self.hub, re.S)
        schemas = [json.loads(block) for block in blocks]
        item_list = next(item for item in schemas if item.get("@type") == "ItemList")
        breadcrumb = next(item for item in schemas if item.get("@type") == "BreadcrumbList")
        faq = next(item for item in schemas if item.get("@type") == "FAQPage")
        catalog = json.loads(CATALOG.read_text(encoding="utf-8"))["entities"]["characters"]

        self.assertEqual(item_list["numberOfItems"], 21)
        self.assertEqual(len(item_list["itemListElement"]), 21)
        self.assertEqual(
            [item["url"] for item in item_list["itemListElement"]],
            [f'https://megabonk.org{entry["page"]}' for entry in catalog],
        )
        self.assertEqual([item["position"] for item in breadcrumb["itemListElement"]], [1, 2, 3])
        self.assertEqual(len(faq["mainEntity"]), 4)

    def test_hub_faq_is_visible_and_keeps_guide_build_intents_separate(self):
        questions = (
            "How many characters are in Megabonk?",
            "Which characters are available immediately?",
            "How do I unlock more characters?",
            "What is the difference between a Character Guide and Best Build?",
        )
        for question in questions:
            self.assertGreaterEqual(self.hub.count(question), 2)
        self.assertIn("A Character Guide explains unlocks, the passive and starting weapon", self.hub)
        self.assertIn("A Best Build page focuses on Weapons, Tomes, Items", self.hub)

    def test_characters_hub_is_reproducible_from_one_reviewed_entity_source(self):
        source = json.loads(CHARACTER_SOURCE.read_text(encoding="utf-8"))["characters"]
        catalog = json.loads(CATALOG.read_text(encoding="utf-8"))["entities"]["characters"]
        self.assertEqual(len(source), 21)
        self.assertEqual(
            {entry["id"]: entry for entry in source},
            {entry["id"]: entry for entry in catalog},
        )

        spec = importlib.util.spec_from_file_location("build_characters_hub", GENERATOR)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        characters = module.load_characters(CATALOG)
        self.assertEqual(module.render(self.hub, characters), self.hub)
        self.assertIn("<!-- CHARACTER_HUB_ROWS_START -->", self.hub)
        self.assertIn("<!-- CHARACTER_HUB_ITEMLIST_START -->", self.hub)

        for workflow_name in ("daily_scrape.yml", "monitor-wiki-entities.yml"):
            workflow = (ROOT / ".github/workflows" / workflow_name).read_text(encoding="utf-8")
            self.assertIn("python scripts/build_characters_hub.py", workflow)
            self.assertIn("python -m py_compile scripts/build_characters_hub.py", workflow)
            self.assertIn("guides/characters/index.html", workflow)

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
