from pokebonk_sync_reference import load_reference
"""Regression checks for source-derived forms, baselines and current task data."""
import json,math
from pathlib import Path
from pokebonk_depth import baseline
ROOT=Path(__file__).resolve().parents[1]
d=load_reference('pokebonk-tools-reference.json')
p=json.loads((ROOT/'data/pokebonk-depth-sources.json').read_text(encoding='utf8'))
assert len(d['league'])==79 and len({x['id']for x in d['league']})==79
assert len(d['fusions'])==106 and len({x['key']for x in d['fusions']})==106
for x in d['league']:
 assert x['forms'] and x['ultimate']['names'] and len(x['ultimate']['names'])==len(x['ultimate']['descs'])
 assert all(f['id']<=151 for f in x['forms'])
 assert all(m['runtime']and m['runtime']['cd']>0 for m in x['kit'])
# Historical engine fixtures keep their original inputs; live baselines are validated by the source adapter.
historical=json.loads((ROOT/'data/pokebonk-tools-reference.json').read_text(encoding='utf8'))
forms={f['id']:f for x in historical['league']for f in x['forms']}
for fixture in p['baselineEngineFixtures']:
 f=forms[fixture['id']];actual=baseline(f['raw'],fixture['stage'])
 for k,value in fixture['expected'].items():assert math.isclose(actual[k],value,rel_tol=1e-12),(fixture['id'],k)
eevee=next(x for x in d['league']if x['id']==133)
assert eevee['evolution'][0]['names']==['Vaporeon','Jolteon','Flareon']
assert len(d['typeChart']['types'])==18 and all(len(row)==18 for row in d['typeChart']['chart'])
assert all(len(x['thresholds'])==3 and all(len(v)==4 for v in x['thresholds'])for x in d['medals'])
print('PASS: 79 season-filtered partners, engine baseline fixtures, 106 recipes, 18-type chart and all medal schedules')
