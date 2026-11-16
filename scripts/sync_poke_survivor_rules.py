#!/usr/bin/env python3
"""AUTO_SYNC of PokéSurvivor game rules from the creator's own pages (SOP 05 §2.9; contract in SITE_PROFILE).

  python scripts/sync_poke_survivor_rules.py [--dry-run] [--offline DIR] [--no-build]

Sources (pokesurvivor.com, robots: Allow /):
  /en/bosses/    calendar boss minutes, Eternatus minute and coin reward, Arceus minute, item-break minutes, touch damage
  /en/upgrades/  upgrade table (effect, max level, first/last price, total) and the maxing total
  /en/guide/     co-op player cap; evolution levels only as a fallback
  /en/news/      dated changelog: the newest entry that states evolution levels or rift minutes wins
                 (the guide page can lag behind the changelog, e.g. levels 12/24 vs 20/40 on 2026-11-16)
Writes only data/poke-survivor-rules.json, then rebuilds /poke-survivor/ with build_poke_survivor.py.
Any parse failure, implausible value or missing upgrade that a page depends on rejects the whole run
(exit 1, nothing written); the workflow then emails the failure.
--offline DIR reads bosses.txt, upgrades.txt, guide.txt, news.txt (saved pages) from DIR (tests and fixtures).
"""
import argparse
import html as H
import json
import re
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/poke-survivor-rules.json'
BASE = 'https://pokesurvivor.com/en/'
PAGES = ('bosses', 'upgrades', 'guide', 'news')
UA = 'megabonk-rules-sync/1.0 (+https://megabonk.org/poke-survivor/)'
NEEDED_UPGRADES = ('Vitality', 'Strength', 'Stride', 'Magnet', 'Repertoire', 'Starting move', 'Card reroll', 'Ban', 'Second item', 'Third item')
NUM = r'\d+(?:,\s*\d+)*(?:,?\s*and\s*\d+)?'


class Reject(Exception):
    pass


def fetch(name, offline):
    if offline:
        return (Path(offline) / f'{name}.txt').read_text(encoding='utf8')
    req = urllib.request.Request(BASE + name + '/', headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        if r.status != 200:
            raise Reject(f'{name}: HTTP {r.status}')
        return r.read().decode('utf8')


def text(markup):
    markup = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', markup, flags=re.S)
    return re.sub(r'\s+', ' ', H.unescape(re.sub(r'<[^>]+>', ' ', markup))).strip()


def nums(s):
    return [int(x) for x in re.findall(r'\d+', s)]


def find(pattern, s, what):
    m = re.search(pattern, s)
    if not m:
        raise Reject(f'{what}: pattern not found (page wording changed?)')
    return m


def ascending(xs, lo, hi, n_lo, n_hi, what):
    if not (n_lo <= len(xs) <= n_hi) or xs != sorted(set(xs)) or not all(lo <= x <= hi for x in xs):
        raise Reject(f'{what}: implausible values {xs}')
    return xs


def parse_bosses(markup):
    t = text(markup)
    out = {
        'calendar_boss_minutes': nums(find(r'At minutes (' + NUM + r') a strong', t, 'calendar bosses')[1]),
        'eternatus_minute': int(find(r'Eternamax Eternatus at minute (\d+)', t, 'Eternatus minute')[1]),
        'arceus_minute': int(find(r'Judgment of Arceus at minute (\d+)', t, 'Arceus minute')[1]),
        'arceus_item_breaks': nums(find(r'Broken items At (' + NUM + r') minutes', t, 'Arceus item breaks')[1]),
        'arceus_touch_pct': int(find(r'Touching it takes (\d+)\s*%', t, 'Arceus touch')[1]),
        'eternatus_coins': int(find(r'\+([\d,]+) Pok[ée]coins', t, 'Eternatus coins')[1].replace(',', '')),
    }
    return out


def parse_upgrades(markup):
    table = find(r'<table[^>]*>(.*?)</table>', markup, 'upgrade table')[1]
    rows = {}
    for tr in re.findall(r'<tr>(.*?)</tr>', table, re.S):
        cells = [text(c) for c in re.findall(r'<td[^>]*>(.*?)</td>', tr, re.S)]
        if len(cells) != 5:
            continue
        name, effect, mx, price, total = cells
        p = [int(x.replace(',', '')) for x in re.findall(r'[\d,]+\d|\d', price)]
        if not name or not p or not mx.isdigit():
            raise Reject(f'upgrade row unreadable: {cells}')
        rows[name] = {'effect': effect, 'max': int(mx), 'first': p[0], 'last': p[-1], 'total': int(total.replace(',', ''))}
    if len(rows) < 12:
        raise Reject(f'upgrade table has only {len(rows)} rows')
    missing = [n for n in NEEDED_UPGRADES if n not in rows]
    if missing:
        raise Reject(f'upgrades used on our pages are missing: {missing}')
    total = int(find(r'Maxing everything costs ([\d,]+)', text(markup), 'upgrade total')[1].replace(',', ''))
    return {'upgrades': rows, 'upgrades_total': total}


def parse_news(markup):
    """Newest dated statement of evolution levels and rift minutes."""
    out = {}
    for date, body in re.findall(r'<article class="news"><time datetime="(\d{4}-\d\d-\d\d)">.*?</time>(.*?)</article>', markup, re.S):
        t = text(body)
        if 'evolution_levels' not in out:
            m = (re.search(r'evolution moves to levels (\d+) and (\d+)', t, re.I)
                 or re.search(r'[Ee]volution mid-run: at levels (\d+) and (\d+)', t))
            if m:
                out['evolution_levels'] = [int(m[1]), int(m[2])]
                out['evolution_source'] = f'news {date}'
        if 'rift_minutes' not in out:
            m = re.search(r'rifts at (' + NUM + r')', t)
            if m:
                out['rift_minutes'] = nums(m[1])
                out['rift_source'] = f'news {date}'
    if 'rift_minutes' not in out:
        raise Reject('no changelog entry states rift minutes')
    if not re.search(r'<article class="news">', markup):
        raise Reject('changelog layout changed')
    return out


def parse_guide(markup, news):
    t = text(markup)
    out = {'coop_max': int(find(r'co-op for up to (\d+)', t, 'co-op cap')[1])}
    if 'evolution_levels' not in news:
        m = find(r'At levels (\d+) and (\d+) you choose', t, 'evolution levels')
        out['evolution_levels'] = [int(m[1]), int(m[2])]
        out['evolution_source'] = 'guide'
    return out


def collect(offline=None):
    raw = {n: fetch(n, offline) for n in PAGES}
    news = parse_news(raw['news'])
    r = {}
    r.update(parse_bosses(raw['bosses']))
    r.update(parse_upgrades(raw['upgrades']))
    r.update(news)
    r.update(parse_guide(raw['guide'], news))
    # plausibility: every rule is checked before anything is written
    ascending(r['evolution_levels'], 2, 100, 2, 2, 'evolution levels')
    ascending(r['calendar_boss_minutes'], 1, 59, 3, 10, 'calendar bosses')
    ascending(r['rift_minutes'], 1, 59, 3, 10, 'rift minutes')
    ascending(r['arceus_item_breaks'], 1, 20, 2, 6, 'Arceus item breaks')
    if not (r['calendar_boss_minutes'][-1] < r['eternatus_minute'] < r['arceus_minute'] <= 60):
        raise Reject(f"boss order broken: calendar {r['calendar_boss_minutes']}, Eternatus {r['eternatus_minute']}, Arceus {r['arceus_minute']}")
    if r['rift_minutes'][-1] >= r['arceus_minute']:
        raise Reject(f"rift after the Judgment: {r['rift_minutes']}")
    if not (2 <= r['coop_max'] <= 8 and 1 <= r['arceus_touch_pct'] <= 100 and 1 <= r['eternatus_coins'] <= 100000):
        raise Reject(f"implausible scalar: co-op {r['coop_max']}, touch {r['arceus_touch_pct']}, coins {r['eternatus_coins']}")
    for n, u in r['upgrades'].items():
        if not (1 <= u['max'] <= 50 and 0 < u['first'] <= u['last'] <= u['total']):
            raise Reject(f'upgrade {n} implausible: {u}')
    return r


RULE_KEYS = ('evolution_levels', 'calendar_boss_minutes', 'rift_minutes', 'eternatus_minute', 'eternatus_coins', 'arceus_minute',
             'arceus_item_breaks', 'arceus_touch_pct', 'coop_max', 'upgrades', 'upgrades_total')


def diff(old, new):
    return [f'{k}: {old.get(k)!r} -> {new[k]!r}' for k in RULE_KEYS if old.get(k) != new[k]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--offline')
    ap.add_argument('--no-build', action='store_true')
    a = ap.parse_args()
    try:
        new = collect(a.offline)
    except (Reject, OSError, ValueError) as e:
        print(f'REJECTED: {e}', file=sys.stderr)
        sys.exit(1)
    old = json.loads(DATA.read_text(encoding='utf8')) if DATA.exists() else {}
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    changes = diff(old, new)
    for c in changes:
        print('CHANGE', c)
    if not changes:
        print('No rule changes.')
        return
    if a.dry_run:
        print('dry run: nothing written')
        return
    out = {'_note': 'Written by scripts/sync_poke_survivor_rules.py from pokesurvivor.com (bosses, upgrades, guide, news). Do not hand-edit without re-running the build.',
           'changed': today, **{k: new[k] for k in RULE_KEYS}, 'evolution_source': new['evolution_source'], 'rift_source': new['rift_source']}
    with open(DATA, 'w', encoding='utf8', newline='\n') as f:  # same bytes on Windows and the Linux runner
        f.write(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
    print(f'wrote {DATA.relative_to(ROOT)} ({len(changes)} changes)')
    if not a.no_build:
        subprocess.run([sys.executable, str(ROOT / 'scripts/build_poke_survivor.py')], check=True, stdout=subprocess.DEVNULL)
        crlf()
        print('rebuilt /poke-survivor/')


def crlf():
    """The section's HTML is committed with CRLF; a Linux rebuild writes LF. Keep the repository convention."""
    for f in (ROOT / 'poke-survivor').rglob('*.html'):
        b = f.read_bytes()
        n = b.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')
        if n != b:
            f.write_bytes(n)


if __name__ == '__main__':
    main()
