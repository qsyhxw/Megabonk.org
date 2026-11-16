"""PokéSurvivor rules AUTO_SYNC: parsing, rejection and propagation (scripts/sync_poke_survivor_rules.py)."""
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import sync_poke_survivor_rules as S  # noqa: E402
from poke_survivor_rules import fill, tokens  # noqa: E402

LIVE = ROOT / 'tests/fixtures/poke-survivor-rules/live'


class Rules(unittest.TestCase):
    def variant(self, **edits):
        """Copy the live snapshot and apply {page: (old, new)} text edits."""
        d = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, d)
        for p in S.PAGES:
            shutil.copy(LIVE / f'{p}.txt', d / f'{p}.txt')
        for page, (old, new) in edits.items():
            f = d / f'{page}.txt'
            s = f.read_text(encoding='utf8')
            self.assertIn(old, s, f'{page}: fixture anchor missing')
            f.write_text(s.replace(old, new), encoding='utf8')
        return str(d)

    def test_live_snapshot(self):
        r = S.collect(str(LIVE))
        self.assertEqual(r['evolution_levels'], [20, 40])           # changelog 2026-11-14 beats the stale guide (12/24)
        self.assertEqual(r['evolution_source'], 'news 2026-11-14')
        self.assertEqual(r['calendar_boss_minutes'], [2, 6, 10, 14, 18])
        self.assertEqual(r['rift_minutes'], [4, 8, 12, 16, 25])
        self.assertEqual((r['eternatus_minute'], r['arceus_minute'], r['arceus_item_breaks']), (20, 30, [2, 4, 6]))
        self.assertEqual(r['upgrades']['Magnet']['first'], 50)
        self.assertEqual(r['upgrades_total'], 93470)
        self.assertEqual(r['coop_max'], 4)

    def test_newer_changelog_entry_wins_and_renders(self):
        entry = ('<article class="news"><time datetime="2026-12-01">2026-12-01</time><h2>Test</h2><ul><li>'
                 'Mid-run evolution moves to levels 25 and 50 (it was 20 and 40).</li></ul></article>')
        a = '<article class="news"><time datetime="2026-11-15">'
        d = self.variant(news=(a, entry + a))
        r = S.collect(d)
        self.assertEqual(r['evolution_levels'], [25, 50])
        self.assertEqual(fill('At levels [[evo]] you choose', r), 'At levels 25 and 50 you choose')
        self.assertEqual(tokens(r)['evo2'], '50')

    def test_rejections(self):
        cases = {
            'boss order': dict(bosses=('Eternamax Eternatus at minute 20', 'Eternamax Eternatus at minute 12')),
            'missing upgrade used on pages': dict(upgrades=('<b>Magnet</b>', '<b>Magnetism</b>')),
            'calendar wording changed': dict(bosses=('At minutes', 'From minute')),
            'implausible co-op': dict(guide=('co-op for up to 4', 'co-op for up to 40')),
            'rift after Judgment': dict(news=('rifts at 4, 8, 12, 16 and 25', 'rifts at 4, 8, 12, 16 and 45')),
            'changelog layout': dict(news=('<article class="news">', '<article class="entry">')),
        }
        for name, edits in cases.items():
            with self.subTest(name):
                with self.assertRaises(S.Reject):
                    S.collect(self.variant(**edits))

    def test_pages_have_no_unfilled_tokens(self):
        for f in (ROOT / 'poke-survivor').rglob('*.html'):
            self.assertNotIn('[[', f.read_text(encoding='utf8'), str(f))

    def test_page_numbers_follow_the_data(self):
        import json
        r = json.loads((ROOT / 'data/poke-survivor-rules.json').read_text(encoding='utf8'))
        hub = (ROOT / 'poke-survivor/index.html').read_text(encoding='utf8')
        lv = r['evolution_levels']
        self.assertIn(f'Level {lv[0]} &amp; {lv[1]}', hub)
        self.assertIn(f'At levels {lv[0]} and {lv[1]} the game asks', hub)
        rifts = (ROOT / 'poke-survivor/rifts/index.html').read_text(encoding='utf8')
        for m in r['rift_minutes']:
            self.assertIn(f'<td>{m}:00</td>', rifts)
        beginner = (ROOT / 'poke-survivor/beginners-guide/index.html').read_text(encoding='utf8')
        self.assertIn(f"<td>Magnet</td><td>{r['upgrades']['Magnet']['first']:,}</td>", beginner)


if __name__ == '__main__':
    unittest.main()
