"""Season 3 tier list for all 138 League partners.

Signals on the S=4…D=0 scale:
1. Lorepond's Season 3 list (weight 0.7; the only public list covering all 138 —
   pokebonk.co republishes the same text, so it is counted once).
2. For the 79 Kanto partners, the Season 2 three-list consensus (weight 0.3) as a
   tie-breaker; Johto partners use signal 1 alone.
A stat-formula score was tested (data_score) but is not used: it correlated at -0.07
with the community list because it cannot model passives, fusions or Ultimates.
Output: data/pokebonk-consensus-tier.json (same shape the page modules read).
"""
from pathlib import Path
import json
import math
import re

ROOT = Path(__file__).resolve().parents[1]
REF = json.loads((ROOT / 'data/pokebonk-s3-reference.json').read_text(encoding='utf8'))
S3 = json.loads((ROOT / '_private/pb-s3.json').read_text(encoding='utf8'))
VAL = {'S': 4, 'A': 3, 'B': 2, 'C': 1, 'D': 0}
SPECIES = {x['id']: x for x in S3['species']}
CHILDREN = {}
for x in S3['species']:
    if x.get('evoFrom'):
        CHILDREN.setdefault(x['evoFrom'], []).append(x['id'])


def final_form(pid):
    seen = pid
    while CHILDREN.get(seen):
        seen = max(CHILDREN[seen], key=lambda c: sum(SPECIES[c]['stats'].values()))
    return seen


def stage_count(pid):
    n = 0
    cur = pid
    while CHILDREN.get(cur):
        cur = CHILDREN[cur][0]
        n += 1
    return n


def lN(st, v):  # Season 3 attack scaling
    total = sum(st.values())
    return max(.85, 1.02 + .3 * (v / total * 6 - 1))


def data_score(member):
    st = SPECIES[final_form(member['id'])]['stats']
    total = sum(st.values())
    share = lambda v: v / total * 6
    stages = stage_count(member['id'])
    grow = 1 + stages * .12
    dps = {'physical': 0.0, 'special': 0.0}
    for mv in member['kit']:
        rt = mv['runtime']
        if mv['cls'] in dps and rt.get('dmg'):
            dps[mv['cls']] += rt['dmg'] * max(rt.get('count') or 1, 1) / max(rt.get('cd') or 1, .2)
    mult = {'physical': lN(st, st['atk']), 'special': lN(st, st['spa'])}
    offence = max(dps[c] * mult[c] for c in dps) * grow
    max_hp = (70 + 45 * share(st['hp'])) * grow
    armor = 6 * share(st['def']) + 3 * share(st['spd'])
    survival = max_hp * (1 + armor / 45) + 40 * (.25 + .25 * share(st['hp']))
    return math.log(offence + 1) * 0.6 + math.log(survival) * 0.4


def lorepond():
    t = (ROOT / '_private/s3t_pokebonk_lorepond_com_tier-list_md.html').read_text(encoding='utf8', errors='ignore')
    return {n.strip(): tier for n, tier in re.findall(r'#### ([^\n]+)\n+Types:[^\n]*\n+Tier: ([SABCD])', t)}


def build():
    lp = lorepond()
    league = REF['league']
    missing = [m['name'] for m in league if m['name'] not in lp]
    if missing:
        raise SystemExit('Lorepond list missing: ' + ', '.join(missing))
    s2 = {r['name']: r['score'] for r in json.loads((ROOT / 'data/pokebonk-consensus-tier.s2.json').read_text(encoding='utf8'))['rows']}
    rows = []
    for m in league:
        a = VAL[lp[m['name']]]
        b = s2.get(m['name'])
        score = round(a * .7 + b * .3, 2) if b is not None else float(a)
        votes = {'Lorepond (Season 3)': lp[m['name']]}
        if b is not None:
            votes['Season 2 consensus'] = round(b, 2)
        rows.append({'name': m['name'], 'id': m['id'], 'score': score, 'spread': 0 if b is None else abs(a - b),
                     'votes': votes, 'types': m['types'], 'role': m['role'], 'passive': m['passive']['name'],
                     'region': m['region']})
    rows.sort(key=lambda r: (-r['score'], r['spread'], r['name']))
    cuts = [('S', 14), ('A', 34), ('B', 50), ('C', len(rows))]
    i = 0
    for t, n in cuts:
        for r in rows[i:i + n]:
            r['tier'] = t
        i += n
    out = {'version': f'Season 3 (v{REF["version"]})', 'checked': REF['checked'],
           'method': 'Lorepond Season 3 list (0.7) with the Season 2 three-list consensus as a 0.3 tie-breaker for Kanto partners.',
           'sources': ['https://pokebonk.lorepond.com/tier-list', REF['source_client']], 'rows': rows}
    (ROOT / 'data/pokebonk-consensus-tier.json').write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n', encoding='utf8')
    return out


if __name__ == '__main__':
    o = build()
    for t in 'SABC':
        print(t, [r['name'] for r in o['rows'] if r['tier'] == t])
