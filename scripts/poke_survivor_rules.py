"""PokéSurvivor game rules shared by every generated page (single source of truth).

data/poke-survivor-rules.json is written only by scripts/sync_poke_survivor_rules.py (AUTO_SYNC from the
creator's guides and dated news at pokesurvivor.com) or by hand. Generators read it through load() so a
rule change is one data edit followed by build_poke_survivor.py.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/poke-survivor-rules.json'
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']


def load():
    return json.loads(DATA.read_text(encoding='utf8'))


def words(nums, conj='and'):
    """[2, 6, 10] -> '2, 6 and 10'."""
    nums = [str(n) for n in nums]
    return nums[0] if len(nums) == 1 else ', '.join(nums[:-1]) + f' {conj} ' + nums[-1]


def zh(nums):
    return '、'.join(str(n) for n in nums)


def es(nums):
    return words(nums, 'y')


def clock(m):
    return f'{m}:00'


def money(n):
    return f'{n:,}'


def long_date(iso):
    y, m, d = iso.split('-')
    return f'{MONTHS[int(m) - 1]} {int(d)}, {y}'


def up(r, name, field='first'):
    return r['upgrades'][name][field]


NUMBER_WORDS = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']


def tokens(r):
    """[[token]] values used in page text (scripts/poke_survivor_v320.py, hub FAQ in data/poke-survivor-pages.json)."""
    rifts = r['rift_minutes']
    main, last = rifts[:-1], rifts[-1]
    t = {
        'evo': words(r['evolution_levels']), 'evo1': str(r['evolution_levels'][0]), 'evo2': str(r['evolution_levels'][1]),
        'cal': words(r['calendar_boss_minutes']), 'cal_list': ', '.join(map(str, r['calendar_boss_minutes'])),
        'cal_zh': zh(r['calendar_boss_minutes']), 'cal_es': es(r['calendar_boss_minutes']),
        'cal_clock': ', '.join(clock(m) for m in r['calendar_boss_minutes']),
        'rift_all': words(rifts), 'rift_main': words(main), 'rift_main_list': ', '.join(map(str, main)),
        'rift_main_zh': zh(main), 'rift_main_clock': ', '.join(clock(m) for m in main), 'rift_last': str(last),
        'rift_main_n': NUMBER_WORDS[len(main)] if len(main) < len(NUMBER_WORDS) else str(len(main)),
        'et': str(r['eternatus_minute']), 'ar': str(r['arceus_minute']), 'ar10': str(r['arceus_minute'] + 10),
        'brk': words(r['arceus_item_breaks']), 'touch': str(r['arceus_touch_pct']), 'coins': money(r['eternatus_coins']),
        'coop': str(r['coop_max']), 'coop_others': NUMBER_WORDS[r['coop_max'] - 1], 'uptotal': money(r['upgrades_total']),
    }
    return t


def fill(s, r, _cache={}):
    """Replace [[token]], [[up:Name]] (first-level price) and [[eff:Name]] (effect) from the rules."""
    import re
    key = id(r)
    if _cache.get('key') != key:
        _cache.update(key=key, t=tokens(r))
    t = _cache['t']

    def sub(m):
        name, arg = m[1], m[2]
        if name == 'up':
            return money(r['upgrades'][arg]['first'])
        if name == 'eff':
            return r['upgrades'][arg]['effect']
        return t[name]
    out = re.sub(r'\[\[(\w+)(?::([^\]]+))?\]\]', sub, s)
    assert '[[' not in out, out[:200]
    return out
