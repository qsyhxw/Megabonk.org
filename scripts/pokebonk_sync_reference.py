"""Overlay accepted domains, preserving all independently reviewed mechanisms."""
from pathlib import Path
from copy import deepcopy
import json
ROOT=Path(__file__).resolve().parents[1]
def load_reference(name):
 data=json.loads((ROOT/'data'/name).read_text(encoding='utf8'));path=ROOT/'data/pokebonk-sync.json'
 if not path.exists():return data
 accepted=json.loads(path.read_text(encoding='utf8'))['accepted']
 def get(domain):return deepcopy(accepted.get(domain,{}).get('data'))
 if name in ['pokebonk-tools-reference.json','pokebonk-reference.json']:
  for domain in ['lab','items','league']:
   if domain in accepted:data[domain]=get(domain)
 if name=='pokebonk-progression-reference.json':
  for domain,key in [('lab','lab'),('moves','moves'),('alpha','alphaTypes')]:
   if domain in accepted:data[key]=get(domain)
 if name=='pokebonk-decisions-reference.json':
  if 'alpha'in accepted:data['alphaTypes']=get('alpha')
  if 'lab'in accepted:data['lab']=get('lab')
  if 'moves'in accepted and'league'in accepted:
   templates={m['key']:m for m in get('moves')};roles=get('league')
   for m in data['moves']:
    source=templates[m['key']]
    for key in ['name','type','cls','dmg','cd','status','statusChance','desc','arch','drain']:m[key]=source[key]
    m['owners']=[r['id']for r in roles if any(k['key']==m['key']for k in r['kit'])]
 if name=='pokebonk-compare-reference.json'and'league'in accepted:
  roles=get('league');data['passives']={str(r['id']):r['passive']for r in roles};data['formTypes'].update({str(f['id']):f.get('types',r['types'])for r in roles for f in r['forms']})
 return data
