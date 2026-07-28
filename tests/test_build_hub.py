import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HUB = ROOT / "guides" / "builds" / "index.html"


class BuildHubTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = HUB.read_text(encoding="utf-8")

    def test_hub_lists_all_21_character_builds(self):
        rows = re.findall(r'<tr data-character="[^"]+">', self.source)
        cards = re.findall(r'<p class="build-card-character">Best for:', self.source)
        self.assertEqual(len(rows), 21)
        self.assertEqual(len(cards), 21)
        self.assertNotIn("all 20 Megabonk characters", self.source)
        self.assertNotIn("Showing all 20 character builds", self.source)
        self.assertIn('<div class="stat-number">21</div>', self.source)
        self.assertIn('<div class="stat-number">21/21</div>', self.source)

    def test_roberto_is_available_in_every_hub_surface(self):
        self.assertIn("<option>Roberto</option>", self.source)
        self.assertIn('<tr data-character="roberto">', self.source)
        self.assertIn(
            'href="https://megabonk.org/guides/builds/roberto-best-build/"',
            self.source,
        )
        self.assertIn(
            'href="/guides/characters/roberto-guide"',
            self.source,
        )

    def test_filter_total_comes_from_rendered_cards(self):
        self.assertIn(
            "const totalCharacterBuilds = characterCards.length;",
            self.source,
        )
        self.assertIn(
            "Showing ${visibleCards} of ${totalCharacterBuilds} character builds.",
            self.source,
        )


if __name__ == "__main__":
    unittest.main()
