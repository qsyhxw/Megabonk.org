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
        checks_all = [s for s in steps if not S.is_rebuild(s)]
        checks_kept = [s for s in kept if not S.is_rebuild(s)]
        self.assertEqual(len(checks_all), len(checks_kept))
        self.assertIn('Rebuild Risk of Rain 2 lightweight tasks', names(kept))

    def test_registered_scripts_exist(self):
        for game, spec in S.GAMES.items():
            for sc in spec['scripts']:
                self.assertTrue((ROOT / 'scripts' / sc).exists(), f'{game}: {sc}')


if __name__ == '__main__':
    unittest.main()
