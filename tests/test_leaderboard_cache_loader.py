from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
LOADER = '/js/leaderboard-data-loader.js?v=20260804'


class LeaderboardCacheLoaderIntegrationTests(unittest.TestCase):
    def test_primary_leaderboard_consumers_use_shared_loader(self):
        pages = [
            'leaderboard/index.html',
            'leaderboard/builds.html',
            'leaderboard/today.html',
            'leaderboard/recent.html',
            'leaderboard/official.html',
            'leaderboard/verified.html',
            'guides/builds/index.html',
            'guides/characters/character-tier-list/index.html',
        ]
        for page in pages:
            with self.subTest(page=page):
                html = (ROOT / page).read_text(encoding='utf-8')
                self.assertIn(LOADER, html)
                self.assertIn('MegabonkLeaderboardData.load', html)

    def test_every_character_signal_page_loads_cache_loader_first(self):
        pages = []
        for path in (ROOT / 'guides' / 'builds').rglob('*.html'):
            html = path.read_text(encoding='utf-8')
            if '/js/character-build-signals.js' in html:
                pages.append(path)
                self.assertIn(LOADER, html)
                self.assertLess(html.index(LOADER), html.index('/js/character-build-signals.js'))
        self.assertEqual(len(pages), 21)

    def test_shared_character_signal_module_uses_loader_and_cache_notice(self):
        script = (ROOT / 'js' / 'character-build-signals.js').read_text(encoding='utf-8')
        self.assertIn("MegabonkLeaderboardData.load('/data/character-build-signals.json'", script)
        self.assertIn('MegabonkLeaderboardData.cachedStatus(loadResult)', script)
        self.assertNotIn('fetch(`/data/character-build-signals.json', script)

    def test_pages_do_not_bypass_loader_for_guarded_json(self):
        roots = [ROOT / 'leaderboard', ROOT / 'guides' / 'builds', ROOT / 'guides' / 'characters' / 'character-tier-list']
        guarded = ('leaderboard-data.json', 'leaderboard-meta.json', 'character-build-signals.json')
        for folder in roots:
            for path in folder.rglob('*.html'):
                html = path.read_text(encoding='utf-8')
                for filename in guarded:
                    with self.subTest(page=str(path.relative_to(ROOT)), filename=filename):
                        self.assertNotRegex(html, rf'fetch\([^\n]*{filename}')


if __name__ == '__main__':
    unittest.main()