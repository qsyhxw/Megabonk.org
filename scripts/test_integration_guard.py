import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import check_integrations as guard


SCRIPT = '<script defer src="https://metrics.example.invalid/script.js" data-website-id="test-id"></script>'


def page(script=SCRIPT):
    return '<!doctype html><html><head>' + script + '</head><body><h1>Test</h1></body></html>'


class GuardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / 'public'
        self.root.mkdir()
        self.config = {'version': 1, 'site': 'test.example.invalid', 'reviewed': True,
                       'integrations': [{'id': 'analytics', 'kind': 'analytics', 'enabled': True,
                                         'authorization': 'offline test fixture',
                                         'include': ['**/*.html'], 'exclude': [],
                                         'checks': [{'tag': 'script', 'attrs': {'src': 'https://metrics.example.invalid/script.js', 'data-website-id': 'test-id'},
                                                     'boolean_attrs': ['defer'], 'location': 'head', 'count': 1}]}]}
        self.write('index.html', page())

    def write(self, path, text):
        file = self.root / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(text, encoding='utf-8')

    def errors(self):
        return guard.check(self.root, self.config)[0]

    def test_valid_root_nested_trust_and_404(self):
        for name in ('new/deep/index.html', 'privacy/index.html', '404.html'):
            self.write(name, page())
        self.assertEqual(guard.check(self.root, self.config), ([], 4))

    def test_new_nested_page_missing_script_fails(self):
        self.write('not-in-sitemap/new/index.html', page(''))
        self.assertTrue(any('not-in-sitemap/new/index.html' in e for e in self.errors()))

    def test_duplicate_fails(self):
        self.write('index.html', page(SCRIPT * 2))
        self.assertTrue(self.errors())

    def test_wrong_id_fails(self):
        self.write('index.html', page(SCRIPT.replace('test-id', 'other-site')))
        self.assertTrue(self.errors())

    def test_wrong_src_fails(self):
        self.write('index.html', page(SCRIPT.replace('/script.js', '/another.js')))
        self.assertTrue(self.errors())

    def test_missing_boolean_attribute_fails(self):
        self.write('index.html', page(SCRIPT.replace(' defer', '')))
        self.assertTrue(self.errors())

    def test_wrong_location_fails(self):
        self.write('index.html', '<html><head></head><body>' + SCRIPT + '</body></html>')
        self.assertTrue(self.errors())

    def test_excluded_page_residual_fails(self):
        self.config['integrations'][0]['exclude'] = ['privacy/**', '404.html']
        self.write('privacy/index.html', page())
        self.write('404.html', page())
        self.assertTrue(self.errors())

    def test_excluded_page_clean_passes(self):
        self.config['integrations'][0]['exclude'] = ['privacy/**', '404.html']
        self.write('privacy/index.html', page(''))
        self.write('404.html', page(''))
        self.assertEqual(self.errors(), [])

    def test_disabled_residual_fails(self):
        self.config['integrations'][0]['enabled'] = False
        self.assertTrue(self.errors())

    def test_disabled_clean_passes(self):
        self.config['integrations'][0]['enabled'] = False
        self.write('index.html', page(''))
        self.assertEqual(self.errors(), [])

    def test_unregistered_external_and_local_scripts_fail(self):
        for extra in ('<script src="/assets/menu.js"></script>', '<script src="https://other.example.invalid/a.js"></script>', '<script>doSomething()</script>'):
            with self.subTest(extra=extra):
                self.write('index.html', page(SCRIPT + extra))
                self.assertTrue(self.errors())

    def test_jsonld_is_data(self):
        self.write('index.html', page(SCRIPT + '<script type="application/ld+json">{"name":"test"}</script>'))
        self.assertEqual(self.errors(), [])

    def test_inline_fingerprint_changes_fail(self):
        text = 'window.menu = true;'
        self.config['integrations'][0]['checks'].append({'tag': 'script', 'text_sha256': hashlib.sha256(text.encode()).hexdigest(), 'count': 1, 'location': 'head'})
        self.write('index.html', page(SCRIPT + '<script> ' + text + ' </script>'))
        self.assertEqual(self.errors(), [])
        self.write('index.html', page(SCRIPT + '<script>window.menu = false;</script>'))
        self.assertTrue(self.errors())

    def test_empty_inline_hash_does_not_approve_external_script(self):
        self.config['integrations'][0]['checks'].append({'tag': 'script', 'text_sha256': hashlib.sha256(b'').hexdigest(), 'count': 1})
        self.write('index.html', page(SCRIPT + '<script src="https://unexpected.example.invalid/a.js"></script>'))
        self.assertTrue(any('unregistered script' in e for e in self.errors()))

    def test_ad_container_counts(self):
        ad = {'id': 'ads', 'kind': 'ad', 'enabled': True, 'authorization': 'fixture', 'include': ['**/*.html'], 'exclude': ['404.html'],
              'checks': [{'tag': 'div', 'attrs': {'id': 'container-this-site'}, 'location': 'body', 'count': 1}]}
        self.config['integrations'].append(ad)
        self.assertTrue(self.errors())
        self.write('index.html', page().replace('</body>', '<div id="container-this-site"></div></body>'))
        self.write('404.html', page())
        self.assertEqual(self.errors(), [])
        self.write('404.html', page().replace('</body>', '<div id="container-this-site"></div></body>'))
        self.assertTrue(self.errors())

    def test_enabled_zero_coverage_fails(self):
        self.config['integrations'][0]['include'] = ['missing/**']
        self.assertTrue(any('matches no HTML' in e for e in self.errors()))

    def test_htm_and_uppercase_extension_enumerated(self):
        self.config['integrations'][0]['include'] += ['**/*.htm', '**/*.HTML']
        self.write('legacy/a.htm', page())
        self.write('b.HTML', page())
        self.assertEqual(guard.check(self.root, self.config), ([], 3))

    def test_no_html_fails(self):
        (self.root / 'index.html').unlink()
        self.assertTrue(self.errors())

    def test_unreviewed_and_broad_script_rule_rejected(self):
        self.config['reviewed'] = False
        with self.assertRaises(ValueError):
            self.errors()
        self.config['reviewed'] = True
        self.config['integrations'][0]['checks'][0]['attrs'] = {}
        with self.assertRaises(ValueError):
            self.errors()

    def test_real_cli_baseline_and_exit_codes(self):
        config_file = self.base / 'config.json'
        baseline_file = self.base / 'before.json'
        baseline_file.write_text(json.dumps(self.config), encoding='utf-8')
        config_file.write_text(json.dumps(self.config), encoding='utf-8')
        command = [sys.executable, str(Path(guard.__file__)), '--root', str(self.root), '--config', str(config_file), '--baseline', str(baseline_file)]
        def run(extra=()):
            return subprocess.run(command + list(extra), capture_output=True, text=True)
        self.assertEqual(run().returncode, 0)
        modified = copy.deepcopy(self.config)
        modified['integrations'][0]['authorization'] += ' changed'
        config_file.write_text(json.dumps(modified), encoding='utf-8')
        self.assertNotEqual(run().returncode, 0)
        self.assertEqual(run(['--change-note', 'documented fixture authorization']).returncode, 0)
        # Permission to change config cannot waive missing required code.
        self.write('index.html', page(''))
        self.assertNotEqual(run(['--change-note', 'fixture']).returncode, 0)

    def test_cli_requires_baseline_or_explicit_first_inventory(self):
        config_file = self.base / 'config.json'
        config_file.write_text(json.dumps(self.config), encoding='utf-8')
        command = [sys.executable, str(Path(guard.__file__)), '--root', str(self.root), '--config', str(config_file)]
        missing = subprocess.run(command, capture_output=True, text=True)
        self.assertNotEqual(missing.returncode, 0)
        first = subprocess.run(command + ['--first-inventory'], capture_output=True, text=True)
        self.assertEqual(first.returncode, 0)
        self.assertIn('BASELINE_NOT_CHECKED', first.stdout)


if __name__ == '__main__':
    unittest.main(verbosity=2)
