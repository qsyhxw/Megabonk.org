"""按改动范围选择重建步骤的自测（scripts/prepush_scope.py）。

运行：python -m unittest tests.test_prepush_scope
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import prepush_scope as S  # noqa: E402


def step(name, run=''):
    return {'name': name, 'run': run or f'echo {name}'}


def fake_steps():
    return [
        step('Verify guard rejects integration defects', 'python scripts/test_integration_guard.py'),
        step('Rebuild PokeBonk from versioned source',
             'python scripts/derive_pokebonk_evolution.py\npython scripts/build_pokebonk.py'),
        step('Rebuild PokeRogue decision guides', 'python scripts/build_pokerogue.py'),
        step('Rebuild Risk of Rain 2 lightweight tasks',
             'python scripts/build_risk_of_rain_2.py\nnode scripts/test_ror2_compatibility.cjs'),
        step('Rebuild main-site longtail guides', 'python scripts/build_longtail_main.py'),
        step('Rebuild PokeDive lightweight tasks', 'python scripts/build_pokedive.py'),
        step('Build and verify game-scoped discovery', 'python scripts/build_game_discovery.py'),
        step('Verify page-specific game images', 'python scripts/check_guide_images.py'),
        step('Verify clean URLs and matching sitemap and page inventories',
             'python -m unittest tests.test_url_suffix_policy'),
    ]


def names(steps):
    return [s['name'] for s in steps]


class SelectTests(unittest.TestCase):
    def test_empty_or_unknown_runs_full(self):
        kept, _ = S.select_steps([], fake_steps())
        self.assertEqual(len(kept), len(fake_steps()))
        kept, _ = S.select_steps(['*'], fake_steps())
        self.assertEqual(len(kept), len(fake_steps()))

    def test_single_game_keeps_only_that_rebuild(self):
        kept, note = S.select_steps(['risk-of-rain-2/index.html', 'assets/risk-of-rain-2/hub.css'], fake_steps())
        n = names(kept)
        self.assertIn('Rebuild Risk of Rain 2 lightweight tasks', n)
        self.assertNotIn('Rebuild PokeRogue decision guides', n)
        self.assertNotIn('Rebuild PokeBonk from versioned source', n)
        # 校验步骤、主站长尾（写共享目录）、发现页始终保留
        self.assertIn('Verify page-specific game images', n)
        self.assertIn('Rebuild main-site longtail guides', n)
        self.assertIn('Rebuild PokeDive lightweight tasks', n)
        self.assertIn('Build and verify game-scoped discovery', n)
        self.assertIn('跳过 2 个', note)

    def test_data_file_owned_by_game(self):
        kept, _ = S.select_steps(['data/pokebonk-evolution.json'], fake_steps())
        n = names(kept)
        self.assertIn('Rebuild PokeBonk from versioned source', n)
        self.assertNotIn('Rebuild PokeRogue decision guides', n)

    def test_two_games_keep_both(self):
        kept, _ = S.select_steps(['pokerogue/index.html', 'risk-of-rain-2/index.html'], fake_steps())
        n = names(kept)
        self.assertIn('Rebuild PokeRogue decision guides', n)
        self.assertIn('Rebuild Risk of Rain 2 lightweight tasks', n)
        self.assertNotIn('Rebuild PokeBonk from versioned source', n)

    def test_shared_paths_force_full(self):
        for path in ['scripts/prepush_scope.py', 'scripts/register_page.py', 'index.html', 'sitemap.xml',
                     'pages_list.txt', 'guides/builds/x.html', 'config/integrations.json',
                     'data/game-seo.json', 'tests/test_x.py', '.githooks/pre-push']:
            kept, note = S.select_steps(['risk-of-rain-2/index.html', path], fake_steps())
            self.assertEqual(len(kept), len(fake_steps()), path)
            self.assertIn('全量', note, path)

    def test_unknown_new_directory_forces_full(self):
        kept, _ = S.select_steps(['newgame/index.html'], fake_steps())
        self.assertEqual(len(kept), len(fake_steps()))

    def test_unknown_rebuild_step_is_always_kept(self):
        steps = fake_steps() + [step('Rebuild Future Game', 'python scripts/build_future_game.py')]
        kept, _ = S.select_steps(['pokerogue/index.html'], steps)
        self.assertIn('Rebuild Future Game', names(kept))

    def test_check_steps_are_never_dropped(self):
        steps = fake_steps()
        checks = [s['name'] for s in steps if not S.is_rebuild(s)]
        kept, _ = S.select_steps(['risk-of-rain-2/index.html'], steps)
        for c in checks:
            self.assertIn(c, names(kept))


class RealWorkflowTests(unittest.TestCase):
    def test_real_workflow_single_game_keeps_all_checks(self):
        import yaml
        data = yaml.safe_load((ROOT / '.github/workflows/validate-integrations.yml').read_text(encoding='utf-8'))
        steps = []
        for job in data['jobs'].values():
            steps += [s for s in job['steps'] if 'run' in s and 'ci_summary.py' not in s['run']]
        kept, note = S.select_steps(['risk-of-rain-2/crossplay/index.html'], steps)
        self.assertLess(len(kept), len(steps))
        checks_all = [s for s in steps if not S.is_rebuild(s)
                      and not any(k in s['name'] for k in S.SYNC_STEPS)]  # 同步测试按专区跳过
        checks_kept = [s for s in kept if not S.is_rebuild(s)]
        self.assertEqual(len(checks_all), len(checks_kept))
        self.assertIn('Rebuild Risk of Rain 2 lightweight tasks', names(kept))

    def test_registered_scripts_exist(self):
        for game, spec in S.GAMES.items():
            for sc in spec['scripts']:
                self.assertTrue((ROOT / 'scripts' / sc).exists(), f'{game}: {sc}')


class RegistryTests(unittest.TestCase):
    """登记文件（pages_list/sitemap/content-dates/game-seo）按条目归属。"""

    def expand(self, path, old, new):
        return S.expand_registry([path], lambda p: old, lambda p: new)

    def test_pages_list_new_game_line_is_scoped(self):
        out = self.expand('pages_list.txt', 'https://megabonk.org/a/\n',
                          'https://megabonk.org/a/\nhttps://megabonk.org/risk-of-rain-2/x/\n')
        self.assertEqual(out, ['risk-of-rain-2/x/'])
        self.assertEqual(S.owner_of(out[0]), 'risk-of-rain-2')

    def test_pages_list_other_area_stays_shared(self):
        out = self.expand('pages_list.txt', 'https://megabonk.org/a/\n',
                          'https://megabonk.org/a/\nhttps://megabonk.org/guides/new/\n')
        self.assertIsNone(S.owner_of(out[0]))

    def test_content_dates_changed_keys_only(self):
        old = '{"https://megabonk.org/pokepath/": "1", "https://megabonk.org/risk-of-rain-2/": "1"}'
        new = '{"https://megabonk.org/pokepath/": "1", "https://megabonk.org/risk-of-rain-2/": "2"}'
        self.assertEqual(self.expand('data/content-dates.json', old, new), ['risk-of-rain-2/'])

    def test_game_seo_pages_only(self):
        old = '{"pages": {"risk-of-rain-2/index.html": {"q": 1}, "brotato/index.html": {"q": 1}}}'
        new = '{"pages": {"risk-of-rain-2/index.html": {"q": 2}, "brotato/index.html": {"q": 1}}}'
        self.assertEqual(self.expand('data/game-seo.json', old, new), ['risk-of-rain-2/index.html'])
        self.assertEqual(self.expand('data/game-seo.json', '{"pages": {}, "x": 0}', '{"pages": {}, "x": 1}'),
                         ['data/game-seo.json'])

    def test_sitemap_added_url_block(self):
        base = '<urlset>\n<url><loc>https://megabonk.org/a/</loc></url>\n'
        new = base + '<url><loc>https://megabonk.org/brotato/z/</loc><lastmod>d</lastmod></url>\n'
        self.assertEqual(self.expand('sitemap.xml', base + '</urlset>', new + '</urlset>'), ['brotato/z/'])
        self.assertEqual(self.expand('sitemap.xml', base + '</urlset>',
                                     new.replace('<urlset>', '<urlset x="1">') + '</urlset>'), ['sitemap.xml'])

    def test_unparseable_or_missing_stays_shared(self):
        self.assertEqual(self.expand('data/content-dates.json', '{', '{}'), ['data/content-dates.json'])
        self.assertEqual(self.expand('pages_list.txt', None, 'x'), ['pages_list.txt'])

    def test_end_to_end_single_game_with_registry(self):
        changed = ['risk-of-rain-2/index.html', 'assets/risk-of-rain-2/hub.css', 'pages_list.txt']
        scoped = S.expand_registry(changed, lambda p: 'https://megabonk.org/a/\n',
                                   lambda p: 'https://megabonk.org/a/\nhttps://megabonk.org/risk-of-rain-2/n/\n')
        kept, note = S.select_steps(scoped, fake_steps())
        self.assertIn('Rebuild Risk of Rain 2 lightweight tasks', names(kept))
        self.assertNotIn('Rebuild PokeBonk from versioned source', names(kept))


class CheckScopeTests(unittest.TestCase):
    def test_touched_games(self):
        self.assertEqual(S.touched_games(['risk-of-rain-2/a/index.html', 'assets/risk-of-rain-2/x.css']), {'risk-of-rain-2'})
        self.assertIsNone(S.touched_games(['risk-of-rain-2/a.html', 'scripts/x.py']))
        self.assertIsNone(S.touched_games([]))
        self.assertIsNone(S.touched_games(['*']))

    def test_env_and_route_filter(self):
        import os
        import check_scope as C
        old = os.environ.pop('PREPUSH_GAMES', None)
        try:
            self.assertIsNone(C.scoped_games())
            self.assertTrue(C.route_in_scope('/anything/x/', None))
            os.environ['PREPUSH_GAMES'] = 'pokepath, brotato'
            g = C.scoped_games()
            self.assertEqual(g, {'pokepath', 'brotato'})
            self.assertTrue(C.route_in_scope('/pokepath/x/', g))
            self.assertTrue(C.route_in_scope('brotato/index.html', g))
            self.assertFalse(C.route_in_scope('/pokerogue/x/', g))
        finally:
            os.environ.pop('PREPUSH_GAMES', None)
            if old is not None:
                os.environ['PREPUSH_GAMES'] = old


class SyncStepAndFileScopeTests(unittest.TestCase):
    SYNC = {'name': 'Verify public-source sync rejects unsafe updates', 'run': 'python scripts/test_pokebonk_sync.py'}

    def test_sync_step_skipped_for_unrelated_game(self):
        kept, _ = S.select_steps(['risk-of-rain-2/a/index.html'], [self.SYNC])
        self.assertEqual(kept, [])

    def test_sync_step_kept_for_pokebonk_and_full(self):
        kept, _ = S.select_steps(['pokebonk/index.html'], [self.SYNC])
        self.assertEqual(kept, [self.SYNC])
        kept, _ = S.select_steps(['scripts/x.py'], [self.SYNC])
        self.assertEqual(kept, [self.SYNC])

    def test_file_in_scope(self):
        import check_scope as C
        g = {'risk-of-rain-2'}
        self.assertTrue(C.file_in_scope('index.html', g))
        self.assertTrue(C.file_in_scope('risk-of-rain-2/a/index.html', g))
        self.assertFalse(C.file_in_scope('pokepath/index.html', g))
        self.assertTrue(C.file_in_scope('pokepath/index.html', None))


if __name__ == '__main__':
    unittest.main()
