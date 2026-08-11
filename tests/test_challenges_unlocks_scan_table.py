from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
CHALLENGES = ROOT / "guides" / "challenges" / "index.html"
UNLOCKS = ROOT / "guides" / "unlocks" / "index.html"


class ChallengesUnlocksScanTableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.challenges = CHALLENGES.read_text(encoding="utf-8")
        cls.unlocks = UNLOCKS.read_text(encoding="utf-8")

    def test_popular_table_is_near_the_top_and_has_required_columns(self):
        table_start = self.challenges.index('id="popular-challenges"')
        forest_start = self.challenges.index('id="forest"')
        self.assertLess(table_start, forest_start)
        table = self.challenges[table_start:forest_start]
        self.assertIn(
            "<thead><tr><th>Challenge</th><th>Condition</th><th>Reward</th><th>Guide</th></tr></thead>",
            table,
        )
        self.assertEqual(table.count("<tr>"), 9)  # header + eight intent rows

    def test_high_interest_challenges_have_conditions_rewards_and_links(self):
        table = self.challenges.split('id="popular-challenges"', 1)[1].split(
            '<section id="forest">', 1
        )[0]
        expected = {
            "AFK Gaming": "/guides/challenges/afk-challenge/",
            "Pacifist": "/guides/challenges/pacifist/",
            "Fragile": "#fragile-strategy",
            "Speedrunner": "#speed-strategy",
            "Speedrunner+": "#speed-strategy",
            "Sticks and stones": "#core-strategy",
            "The Floor is Lava": "#desert",
            "Ignore Offers": "#ignore-offers",
        }
        for challenge, guide in expected.items():
            with self.subTest(challenge=challenge):
                row = next(
                    row for row in re.findall(r"<tr>(.*?)</tr>", table, re.S)
                    if challenge in row
                )
                self.assertGreaterEqual(row.count("<td>"), 4)
                self.assertIn(f'href="{guide}"', row)
        self.assertIn("first-clear +1%", table)
        self.assertIn("No Challenge completion or Silver bonus", table)

    def test_unlocks_hub_hands_challenge_intent_to_the_scan_table(self):
        self.assertIn(
            'href="/guides/challenges/#popular-challenges"', self.unlocks
        )
        self.assertNotIn('id="popular-challenges"', self.unlocks)

    def test_existing_tdk_is_preserved(self):
        self.assertIn(
            "<title>Megabonk Challenges Guide: Rules, Rewards & Builds</title>",
            self.challenges,
        )
        self.assertIn("<h1>Megabonk Challenges Guide</h1>", self.challenges)

    def test_modified_date_and_sitemap_are_current(self):
        self.assertIn('"dateModified":"2026-08-11"', self.challenges)
        self.assertIn("Last verified: August 11, 2026", self.challenges)
        sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
        self.assertRegex(
            sitemap,
            r"<loc>https://megabonk\.org/guides/challenges/</loc>\s*<lastmod>2026-08-11</lastmod>",
        )


if __name__ == "__main__":
    unittest.main()
