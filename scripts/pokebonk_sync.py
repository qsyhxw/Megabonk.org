"""Validate public candidates and retain the last accepted values per domain."""
from pathlib import Path
from copy import deepcopy
import argparse,hashlib,json,math,re
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
STATE=ROOT/'data/pokebonk-sync.json'
def read(name):return json.loads((ROOT/'data'/name).read_text(encoding='utf8'))
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def indexed(xs,key):
 if not isinstance(xs,list)or not xs:raise ValueError('Missing data collection')
 result={x[key]:x for x in xs}
 if len(result)!=len(xs):raise ValueError('Duplicate entity ID')
 return result
def finite_tree(x):
 if isinstance(x,float)and not math.isfinite(x):raise ValueError('Non-finite number')
 if isinstance(x,dict):
  if any(k in ['__proto__','constructor','prototype']for k in x):raise ValueError('Unsafe data key')
  for v in x.values():finite_tree(v)
 elif isinstance(x,list):
  for v in x:finite_tree(v)
 elif isinstance(x,str)and len(x)>120000:raise ValueError('Oversized source text')
def assess(candidate,previous=None):
 c=deepcopy(candidate);finite_tree(c)
 if c.get('schema')!=1 or not re.fullmatch(r'\d+\.\d+\.\d+',c.get('observed',{}).get('version','')):raise ValueError('Invalid version record')
 for k in ['client','config']:
  if not re.fullmatch(r'https://pokebonk\.com/assets/[\w.-]+\.js',c.get(k,'')):raise ValueError('Untrusted source URL')
 for k in ['client_sha256','config_sha256']:
  if not re.fullmatch('[a-f0-9]{64}',c.get(k,'')):raise ValueError('Invalid source hash')
 tool=read('pokebonk-tools-reference.json');prog=read('pokebonk-progression-reference.json');accepted=deepcopy((previous or {}).get('accepted',{}));pending=[];changes=[]
 domains={};lab=indexed(c.get('lab'),'id');oldlab=indexed(tool['lab'],'id')
 if lab.keys()!=oldlab.keys():raise ValueError('Lab inventory changed; preserve cached data')
 for key,x in lab.items():
  if type(x.get('max'))is not int or x['max']!=oldlab[key]['max']or len(x.get('costs',[]))!=x['max']:raise ValueError('Lab schedule shape changed')
  if any(type(v)is not int or v<=0 or v>100000000 for v in x['costs']):raise ValueError('Invalid Lab price')
 domains['lab']=c['lab']
 if c.get('adapter_ok')and c.get('arches')!=prog['arches']:
  c['adapter_ok']=False;c['adapter_error']='Move archetype upgrade fields changed; combat data requires review.'
 items=indexed(c.get('items'),'key');olditems=indexed(tool['items'],'key')
 if items.keys()!=olditems.keys():pending.append('Item inventory changed; new or removed entries require review.')
 if c.get('adapter_ok'):
  if items.keys()==olditems.keys():
   for x in items.values():
    if not isinstance(x.get('mods'),list)or not isinstance(x.get('desc'),str)or not 0<=x.get('rarity',-1)<=4:raise ValueError('Invalid item card')
   domains['items']=c['items']
  moves=indexed(c.get('moves'),'key');oldmoves=indexed(prog['moves'],'key');roles=indexed(c.get('league'),'id');oldroles=indexed(tool['league'],'id');species=indexed(c.get('species'),'id')
  if moves.keys()!=oldmoves.keys():pending.append('Move inventory changed; kit and template synchronization paused.')
  else:
   for k,x in moves.items():
    if x.get('arch')not in prog['arches']or any(not isinstance(x.get(n),(int,float))for n in ['dmg','cd','count','area','dur','speed'])or x['cd']<=0:raise ValueError('Invalid move runtime')
   domains['moves']=c['moves']
  if roles.keys()!=oldroles.keys():pending.append('League inventory changed; partner synchronization paused.')
  elif 'moves'in domains:
   baseline=json.loads((ROOT/'config/pokebonk-sync.json').read_text(encoding='utf8'))
   if any(r.get('challenge')!=baseline['challenges'].get(str(k))for k,r in roles.items()):pending.append('Capture prerequisites changed; partner synchronization requires review.')
   else:
    merged=deepcopy(tool['league'])
    for row in merged:
     r=roles[row['id']];row.update(role=r['role'],rank=r['rank'],start=r.get('start',False));oldkit=indexed(row['kit'],'key');row['kit']=[]
     for key in r['kit']:
      m=moves[key];row['kit'].append(dict(key=key,name=m['name'],type=m['type'],cls=next((move['cls']for partner in tool['league']for move in partner['kit']if move['key']==key),m['cls']),fusionEligible=oldkit.get(key,{}).get('fusionEligible',True),runtime={k:m[k]for k in ['cls','arch','dmg','cd','count','area','dur','status','statusChance','desc']}))
     if r['passive']not in c['passives']:raise ValueError('Missing passive')
     row['passive']=deepcopy(c['passives'][r['passive']]);row['passive'].setdefault('mods',[])
     for form in row['forms']:
      raw=species[form['id']]['stats']
      if set(raw)!={'hp','atk','def','spa','spd','spe'}or any(type(v)is not int or not 1<=v<=1000 for v in raw.values()):raise ValueError('Invalid species baseline')
      form['raw']=raw;form['types']=species[form['id']]['types']
     row['types']=species[row['id']]['types']
    domains['league']=merged
  alpha=c.get('alpha')
  if not isinstance(alpha,dict)or set(alpha)!=set(prog['alphaTypes']):raise ValueError('Alpha inventory changed')
  domains['alpha']=alpha
 else:pending.append(c.get('adapter_error')or'Client mechanics require review; retain previous combat/partner snapshots.')
 for domain,value in domains.items():
  base={'lab':tool['lab'],'items':tool['items'],'league':tool['league'],'moves':prog['moves'],'alpha':prog['alphaTypes']}[domain]
  prior=accepted.get(domain,{}).get('data',base)
  if digest(value)!=digest(prior):changes.append(domain)
  # Do not rewrite domain verification dates when the values are unchanged.
  if domain not in accepted or digest(value)!=digest(prior):accepted[domain]={'version':c['observed']['version'],'client':c['client'],'config':c['config'],'data':value}
 news=[]
 for row in c.get('news',[]):
  if row.get('title')is None:row['title']='Project update'
  if not isinstance(row.get('title'),str)or not isinstance(row.get('version'),str):raise ValueError('Invalid release note')
  news.append({'version':row['version'],'title':row['title'][:180],'notes_sha256':digest(row.get('notes'))})
 if not news:raise ValueError('Missing release notes')
 if previous and (c['client_sha256']!=previous['source']['client_sha256']or c['config_sha256']!=previous['source']['config_sha256']):pending.append('Source changed: route, capture, mode, conditional effects and editorial recommendations retain their dated review until rechecked.')
 # Preserve an unresolved prose review across subsequent identical checks.
 if previous and previous.get('pending')and c['client_sha256']==previous['source']['client_sha256']and c['config_sha256']==previous['source']['config_sha256']:pending=list(dict.fromkeys(previous['pending']+pending))
 result={'schema':1,'observed':c['observed'],'source':{k:c[k]for k in ['client','config','client_sha256','config_sha256']},'accepted':accepted,'news':news,'pending':pending}
 if not previous or digest(result)!=digest({k:v for k,v in previous.items()if k!='changed_at'}):result['changed_at']=datetime.now(timezone.utc).isoformat(timespec='seconds')
 else:result['changed_at']=previous['changed_at']
 return result,changes
def atomic(path,data):
 tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');tmp.replace(path)
def main():
 parser=argparse.ArgumentParser();parser.add_argument('candidate',type=Path);parser.add_argument('--dry-run',action='store_true');args=parser.parse_args();raw=args.candidate.read_bytes()
 if len(raw)>2000000:raise ValueError('Candidate exceeds size limit')
 previous=json.loads(STATE.read_text(encoding='utf8'))if STATE.exists()else None;state,domains=assess(json.loads(raw),previous);changed=previous!=state
 if changed and not args.dry_run:atomic(STATE,state)
 text=f"PokeBonk {state['observed']['version']}: {'changed'if changed else'unchanged'}; data domains: {', '.join(domains)or'none'}; pending checks: {len(state['pending'])}."
 print(text)
 import os
 if os.environ.get('GITHUB_STEP_SUMMARY'):
  with open(os.environ['GITHUB_STEP_SUMMARY'],'a',encoding='utf8')as f:f.write(text+'\n\n'+'\n'.join('- '+x for x in state['pending'])+'\n')
 if os.environ.get('GITHUB_OUTPUT'):
  with open(os.environ['GITHUB_OUTPUT'],'a',encoding='utf8')as f:f.write('changed='+str(changed).lower()+'\n')
if __name__=='__main__':main()
