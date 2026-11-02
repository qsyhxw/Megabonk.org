"""Accept validated data domains; keep editorial review separate from source observation."""
from pathlib import Path
from copy import deepcopy
import argparse,json,re,math,os
from datetime import date,datetime,timezone
from azeroth_sync_source import digest,LANGS
ROOT=Path(__file__).resolve().parents[1]
HEX=re.compile(r'[a-f0-9]{64}')

def routes():
 return sorted('/'+str(p.relative_to(ROOT)).replace('\\','/').replace('index.html','') for p in (ROOT/'azeroth-survivors').rglob('index.html') if p.parent.name!='play')

def validate(c,old,config):
 if c.get('schema')!=1 or type(c.get('unchanged')) is not bool:raise ValueError('Unknown sync candidate schema')
 o=c.get('observed',{})
 if not re.fullmatch(r'0\.\d{1,4}\.\d{1,4}',o.get('version','')) or not HEX.fullmatch(o.get('client_sha256','')):raise ValueError('Invalid source identity')
 if tuple(map(int,o['version'].split('.')))<tuple(map(int,old['observed']['version'].split('.'))):raise ValueError('Source version regressed')
 if not re.fullmatch(r'[a-f0-9]{9}',o.get('build','')) or not re.fullmatch(r'[a-f0-9]{8,64}',o.get('stamp','')) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}',o.get('date','')):raise ValueError('Invalid capture metadata')
 if date.fromisoformat(o['date'])>datetime.now(timezone.utc).date():raise ValueError('Capture date is in the future')
 if not isinstance(o.get('etag'),str) or len(o['etag'])>200 or any(x in o['etag'] for x in '\r\n'):raise ValueError('Invalid HTTP validator')
 info=o.get('launcher',{})
 if set(info)!={'stamp','windows','discord'} or info['stamp']!=o['stamp'] or not re.fullmatch(r'https://wow\.aethus\.pl/download/[A-Za-z0-9_.-]+\.(?:rar|zip)',info['windows']) or not re.fullmatch(r'https://discord\.gg/[A-Za-z0-9-]+',info['discord']):raise ValueError('Untrusted official action link')
 if c['unchanged']:
  if o!=old['observed']:raise ValueError('Unchanged candidate does not match the stored source')
  return
 f=c.get('fingerprints',{});h=c.get('hints',{})
 if not isinstance(f,dict) or not 2500<=len(f)<=12000 or len(f)<len(old['fingerprints'])*.9 or any(not HEX.fullmatch(k) or not isinstance(v,str) or not HEX.fullmatch(v) for k,v in f.items()):raise ValueError('Invalid localized fingerprints')
 if not isinstance(h,dict) or not set(h)<=set(f) or any(not isinstance(v,str) or len(v)>100 or '<' in v or '\n' in v for v in h.values()):raise ValueError('Invalid source hints')
 domains=c.get('domains',{});errors=c.get('domain_errors',{})
 if set(domains)|set(errors)!={'names','races'} or set(domains)&set(errors) or any(not isinstance(v,str) or len(v)>300 for v in errors.values()):raise ValueError('Incomplete domain validation result')
 if 'names' in domains:
  n=domains['names'];ss=n.get('spells',[]);expected=config['spell_classes']
  if len(ss)!=len(expected) or {s['key'] for s in ss}!=set(expected):raise ValueError('Unreviewed spell inventory')
  for s in ss:
   if s['class']!=expected[s['key']]:raise ValueError('Spell class grouping changed')
  values=[s['names'] for s in ss]+n.get('talent_spell_names',[])
  if len(values)!=len(expected)+len(config['extra_spell_keys']):raise ValueError('Missing talent-learned names')
  if any(set(v)!=set(LANGS) or any(not isinstance(t,str) or not 1<=len(t)<=100 or any(k in t for k in '<>{}\r\n') for t in v.values()) for v in values):raise ValueError('Invalid language/name values')
 if 'races' in domains:
  rr=domains['races']
  if set(rr)!=set(config['racial_rules']):raise ValueError('Unreviewed race trait inventory')
  for key,values in rr.items():
   if not isinstance(values,list) or len(values)!=re.compile(config['racial_rules'][key]['pattern']).groups or any(type(v) not in (int,float) or not math.isfinite(v) or not 0<v<=1000 for v in values):raise ValueError('Invalid race trait values')
 if o['client_sha256']==old['observed']['client_sha256'] and (o['version']!=old['observed']['version'] or f!=old['fingerprints']):raise ValueError('Source content contradicts its unchanged cryptographic hash')

def dependencies(hint,config,allroutes):
 home='/azeroth-survivors/';base={home+'patch-notes/'}
 if hint.startswith('race.'):
  return base|{home+'best-race/',home+'best-class/',home+'builds/'}|{home+'builds/'+c+'/' for c in config['classes']}
 if hint.startswith('ability.'):
  cls=config['spell_classes'].get(hint)
  if hint in config['extra_spell_keys']:cls='shaman'
  return base|{home+'abilities/',home+'builds/',home+'best-class/',home+'talents/'}|({home+'builds/'+cls+'/'} if cls else {home+'builds/'+c+'/' for c in config['classes']})
 if hint.startswith('class.'):
  cls=hint.split('.')[1]
  return base|{home,home+'best-class/',home+'builds/',home+'builds/'+cls+'/'}
 if hint.startswith('opt.'):
  return base|{home+'beginners-guide/',home+'troubleshooting/',home+'mobile/',home+'save-backup/',home+'addons/',home+'damage-meter/'}
 # An unclassified mechanic string can affect any original-game decision.
 return set(allroutes)

def clear_reviewed(state,config):
 for route,review in config.get('editorial_reviews',{}).items():
  if review.get('client_sha256')==state['observed']['client_sha256'] and len(review.get('note','').strip())>=10:state['pending'].pop(route,None)

def assess(c,old,config,allroutes=None):
 validate(c,old,config);state=deepcopy(old);allroutes=allroutes or routes()
 if c['unchanged']:
  clear_reviewed(state,config);return state,{'unchanged':state==old,'domains':[],'affected_pages':[],'pending_pages':sorted(state['pending'])}
 before=old['fingerprints'];after=c['fingerprints'];added=set(after)-set(before);removed=set(before)-set(after);changed={k for k in set(before)&set(after) if before[k]!=after[k]};affected=set();hints={**old['hints'],**c['hints']};reasons={}
 for key in added|removed|changed:
  for route in dependencies(hints.get(key,''),config,allroutes):affected.add(route);reasons.setdefault(route,set()).add(key)
 observed=deepcopy(c['observed'])
 if observed['client_sha256']==old['observed']['client_sha256'] and observed['launcher']==old['observed']['launcher']:observed['date']=old['observed']['date']
 if observed['client_sha256']==old['observed']['client_sha256'] and observed['launcher']==old['observed']['launcher'] and after==before and c['domain_errors']==old['domain_errors'] and all(data==old['accepted'][key]['data'] for key,data in c['domains'].items()):
  # A forced read of identical bytes must not erase the last meaningful comparison.
  state['observed']=observed;state['hints']=c['hints'];clear_reviewed(state,config)
  return state,{'unchanged':state==old,'domains':[],'affected_pages':[],'pending_pages':sorted(state['pending'])}
 if observed['client_sha256']!=old['observed']['client_sha256'] and not (added|removed|changed):affected.update(allroutes)
 state.update(observed=observed,fingerprints=after,hints=c['hints'],domain_errors=deepcopy(c['domain_errors']))
 domains=deepcopy(c['domains']);data_changes=[]
 if 'names' in domains:
  previous={s['key']:s['names'] for s in old['accepted']['names']['data']['spells']};new=domains['names']['spells']
  english=sum(s['names']['en']!=previous[s['key']]['en'] for s in new)
  translations=sum(s['names'][l]!=previous[s['key']][l] for s in new for l in LANGS)
  if english>10 or translations>len(new)*len(LANGS)*.2:
   domains.pop('names');state['domain_errors']['names']='Large naming change requires review; the previous name lookup is retained.'
 for domain,data in domains.items():
  prior=old['accepted'][domain]
  if digest(prior['data'])!=digest(data):data_changes.append(domain)
  state['accepted'][domain]={'version':observed['version'],'sha256':observed['client_sha256'],'date':observed['date'],'data':data}
 if 'names' in data_changes:
  affected.add('/azeroth-survivors/abilities/')
  oldnames={s['key']:s['names']['en'] for s in old['accepted']['names']['data']['spells']}
  for s in state['accepted']['names']['data']['spells']:
   if s['names']['en']!=oldnames[s['key']]:affected.add('/azeroth-survivors/builds/'+s['class']+'/')
 if 'races' in data_changes:affected|=dependencies('race.',config,allroutes)
 if observed['launcher']!=old['observed']['launcher']:
  if any(observed['launcher'][k]!=old['observed']['launcher'][k] for k in ['windows','discord']):data_changes.append('links')
  affected.update(allroutes)
 for domain in state['domain_errors']:affected.add('/azeroth-survivors/'+('abilities/' if domain=='names' else 'best-race/'))
 affected&=set(allroutes)
 for route in affected:
  previous=state['pending'].get(route,{})
  ids=sorted(set(previous.get('key_ids',[]))|reasons.get(route,set()))[:50]
  state['pending'][route]={'since':previous.get('since',observed['date']),'version':observed['version'],'reason':'Original source changed. Generated references may be updated; editorial guidance needs review.','key_ids':ids,'source_keys':[hints.get(k,'unclassified:'+k[:16]) for k in ids[:12]]}
 clear_reviewed(state,config)
 state['last_changes']={'added':len(added),'removed':len(removed),'changed':len(changed),'data_domains':data_changes,'affected_pages':sorted(affected)}
 diffs={}
 for domain in data_changes:
  if domain=='races':diffs[domain]={k:{'before':v,'after':state['accepted']['races']['data'][k]} for k,v in old['accepted']['races']['data'].items() if v!=state['accepted']['races']['data'][k]}
  elif domain=='names':
   oldnames={s['key']:s['names'] for s in old['accepted']['names']['data']['spells']};diffs[domain]={s['key']:{'before':oldnames[s['key']],'after':s['names']} for s in state['accepted']['names']['data']['spells'] if oldnames[s['key']]!=s['names']}
  elif domain=='links':diffs[domain]={'before':old['observed']['launcher'],'after':state['observed']['launcher']}
 report={'unchanged':state==old,'domains':data_changes,'domain_diffs':diffs,'affected_pages':sorted(affected),'pending_pages':sorted(state['pending']),'domain_errors':state['domain_errors'],'source_changes':state['last_changes'],'examples':c.get('examples',[]),'examples_truncated':c.get('examples_truncated',False)}
 return state,report

def apply(c,root=ROOT,report_path=None):
 config=json.loads((root/'config/azeroth-sync.json').read_text(encoding='utf8'));path=root/'data/azeroth-sync.json';old=json.loads(path.read_text(encoding='utf8'));state,report=assess(c,old,config)
 if state!=old:
  path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
  accepted=state['accepted']['names'];namepath=root/'data/azeroth-spell-names.json';names=json.loads(namepath.read_text(encoding='utf8'))
  names.update(version=accepted['version'],captured=accepted['date'],reviewed=accepted['date'],sha256=accepted['sha256'],spells=accepted['data']['spells'])
  names['scope']='Frozen 103-key class grouping from the original 30 October picker/Codex snapshot; localized labels rechecked separately. Extra talent-learned names remain separate. Not a complete current card pool or damage ranking.'
  namepath.write_text(json.dumps(names,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 if report_path:report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 summary=f"Azeroth source: {state['observed']['version']}; changed domains: {', '.join(report['domains']) or 'none'}; editorial pages pending: {len(state['pending'])}."
 if os.environ.get('GITHUB_STEP_SUMMARY'):
  with open(os.environ['GITHUB_STEP_SUMMARY'],'a',encoding='utf8') as f:f.write('\n'+summary+'\n\n'+''.join('- `'+p+'`\n' for p in sorted(state['pending'])))
 if os.environ.get('GITHUB_OUTPUT'):
  with open(os.environ['GITHUB_OUTPUT'],'a',encoding='utf8') as f:f.write('changed='+str(state!=old).lower()+'\n')
 print(summary)
 return report

def main():
 p=argparse.ArgumentParser();p.add_argument('candidate',type=Path);p.add_argument('--report',type=Path);a=p.parse_args();apply(json.loads(a.candidate.read_text(encoding='utf8')),report_path=a.report)
if __name__=='__main__':main()
