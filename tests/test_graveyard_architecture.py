import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "guides" / "maps" / "graveyard" / "index.html"


class GraveyardArchitectureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = PAGE.read_text(encoding="utf-8")

    def test_existing_tdk_is_preserved(self):
        self.assertIn("<title>Megabonk Graveyard Guide: Crypt Keys & Big Bob</title>", self.html)
        self.assertIn("<h1>Graveyard Map Guide</h1>", self.html)

    def test_high_intent_sections_and_toc_anchors_exist(self):
        for anchor in ("tier-2", "crypt", "crypt-escape", "crypt-keys", "big-bob", "secret-room", "stuck"):
            self.assertIn(f'id="{anchor}"', self.html)
            self.assertIn(f'href="#{anchor}"', self.html)

    def test_tier_two_query_gets_a_direct_answer(self):
        self.assertIn("Graveyard does not currently have a separate Tier 2 or Tier 3 option", self.html)
        self.assertIn("Graveyard has no separate Tier 2/3 selector", self.html)

    def test_big_bob_strategy_covers_fight_mechanics(self):
        for phrase in ("Charge the arena shrines", "Use the protected area", "Keep moving above the lava", "Keep a shrine in reserve"):
            self.assertIn(phrase, self.html)

    def test_faq_schema_matches_new_questions(self):
        scripts = re.findall(r'<script type="application/ld\+json">(.*?)</script>', self.html, re.S)
        graph = json.loads(scripts[0])["@graph"]
        faq = next(node for node in graph if node.get("@type") == "FAQPage")
        questions = {entry["name"] for entry in faq["mainEntity"]}
        self.assertIn("How do you unlock Graveyard Tier 2 in Megabonk?", questions)
        self.assertIn("How do you survive Big Bob's lethal attack?", questions)


if __name__ == "__main__":
    unittest.main()