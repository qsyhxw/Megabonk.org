"""Render auto-accepted references and explicit editorial review boundaries."""
from pathlib import Path
from functools import lru_cache
from html import escape
import json,re
from azeroth_sync_source import digest
from azeroth_survivors_content import P,SOURCES,ref,a,para,table
ROOT=Path(__file__).resolve().parents[1]

@lru_cache(maxsize=1)
def state():return json.loads((ROOT/'data/azeroth-sync.json').read_text(encoding='utf8'))

def apply_sync(pages):
 s=state();config=json.loads((ROOT/'config/azeroth-sync.json').read_text(encoding='utf8'))
 o=s['observed'];SOURCES['sync_observed']=('https://wow.aethus.pl/','Aethus · monitored original source',f"Original v{o['version']} / {o['build']}, launcher stamp {o['stamp']}, observed {o['date']}; client SHA-256 {o['client_sha256']}. Read as data without executing the game. Source observation is separate from editorial review and gameplay testing.")
 for key in ['names','races']:
  v=s['accepted'][key]
  SOURCES['sync_'+key]=('https://wow.aethus.pl/','Aethus · automatically checked '+key,f"Original v{v['version']} strings captured {v['date']}; client SHA-256 {v['sha256']}. Only the validated {key} reference domain is accepted automatically; this does not verify full builds, combat code or a completed run.")
 for d in pages:
  if P+d['slug'] in s['pending'] and (d['slug']=='best-class/' or (d['slug'].startswith('builds/') and d['slug']!='builds/')):
   d['answer']='<strong>Source changes detected: this editorial route needs review against the latest client.</strong> '+d['answer']
  if d['slug']=='abilities/':
   n=s['accepted']['names'];data=n['data']
   d['answer']=f"Search the 103-name baseline in the listed client languages. Name labels were read from original v{n['version']} on {n['date']}; class grouping retains the 30 October picker/Codex snapshot. This is a name reference, not a complete current card pool or a damage ranking."+ref('sync_names')
   revised=[]
   for i,t,h in d['parts']:
    if i=='scope':h=para('Labels can update automatically only when all 14 language columns and the recorded entries validate. A missing entry or changed source format retains the previous reference. Starting spells, point gates and numerical rank effects require separate verification.'+ref('sync_names'))
    if i=='talent-names':h=para('These two additional Shaman labels are kept separate from the ordinary 103-key baseline. A localized name does not establish its current unlock or starting-spell rule.'+ref('sync_names'))+table(['English name','简体中文 client name','Guide'],[[escape(x['en']),escape(x['zh']),a('builds/shaman/','Read the dated Shaman route')] for x in data['talent_spell_names']])
    revised.append((i,t,h))
   d['parts']=revised
  if d['slug']=='best-race/':
   accepted=s['accepted']['races'];groups={}
   for key,rule in config['racial_rules'].items():groups.setdefault(rule['race'],[]).append(rule['summary'].format(*accepted['data'][key]))
   d['parts'].insert(0,('live-races','Automatically checked racial values',para(f"Original v{accepted['version']} · captured {accepted['date']}. These values are parsed only while the original wording matches the reviewed rules. They describe racial text, not a measured best race, eligibility for every class or guaranteed encounter immunity."+ref('sync_races'))+table(['Race','Source-described benefits'],[[escape(name),'<br>'.join(escape(t) for t in texts)] for name,texts in groups.items()])))
  if d['slug']=='patch-notes/':
   c=s['last_changes'];pending=s['pending']
   text=para(f"Latest original client detected: v{s['observed']['version']} on {s['observed']['date']}. The automatic comparison checks localized strings and constrained reference fields. A client binary can change combat behaviour without changing its text; older guide sections keep their own verification dates."+ref('sync_observed'))
   text+=table(['Comparison result','Count / scope'],[['Added / removed / changed English strings',f"{c['added']} / {c['removed']} / {c['changed']}"],['Automatically changed reference domains',escape(', '.join(c['data_domains']) or 'None in the last comparison')],['Editorial pages awaiting review',str(len(pending))]])
   if pending:text+='<ul>'+''.join('<li>'+a(path[len(P):],path[len(P):].strip('/') or 'Guide home')+'</li>' for path in sorted(pending))+'</ul>'
   else:text+=para('No new editorial review flags are pending in the monitored comparison. This does not upgrade older sections to a current-version playtest.')
   d['parts'].insert(0,('source-monitor','Official-source comparison and review status',text))
 return pages

def decorate_sync(path,html):
 if path.endswith('404.html') or path==P+'play/':return html
 s=state();o=s['observed'];pending=path in s['pending'];ru='/ru/' in path
 heading=('Последний исходный клиент' if ru else 'Latest original source')+': v'+o['version']
 scope=('Обнаружен '+o['date']+'. Разделы руководства сохраняют собственные даты проверки.' if ru else 'Detected '+o['date']+'. Individual guide sections retain their own verification dates; automatic checks do not validate every combat mechanic.')
 if pending:scope+=(' Исходные данные изменились; рекомендации ожидают редакционной проверки.' if ru else ' Source changes may affect this guide; editorial recommendations are awaiting review.')
 errors=s.get('domain_errors',{})
 if path==P+'abilities/' and 'names' in errors:scope+=' Name validation did not pass; the previous name reference is retained.'
 if path==P+'best-race/' and 'races' in errors:scope+=' Race validation did not pass; the previous numeric reference is retained.'
 badge=f'<aside class="source-status{" source-review" if pending else ""}" id="source-sync" data-source-revision="{digest(s)}" data-review-pending="{str(pending).lower()}"><strong>{escape(heading)}</strong><p>{escape(scope)} <a href="{P}patch-notes/#source-monitor">'+('Статус сравнения →' if ru else 'Comparison status →')+'</a></p></aside>'
 if path==P:
  html=html.replace('<section class="section" id="launch">',badge+'<section class="section" id="launch">',1)
  html=re.sub(r'<small>Latest text check</small><strong>[^<]*</strong>',lambda m:'<small>Latest original source</small><strong>v'+o['version']+'</strong>',html)
  html=re.sub(r'<small>Checked</small><strong>[^<]*</strong>',lambda m:'<small>Source observed</small><strong>'+o['date']+'</strong>',html)
 else:html=re.sub(r'(<header class="article-head".*?</header>)',lambda m:m[1]+badge,html,count=1,flags=re.S)
 # Only already-approved original-host download and creator Discord links are replaceable.
 html=re.sub(r'href="https://wow\.aethus\.pl/download/[A-Za-z0-9_.-]+\.(?:rar|zip)"',lambda m:'href="'+escape(o['launcher']['windows'],quote=True)+'"',html)
 html=re.sub(r'href="https://discord\.gg/[A-Za-z0-9-]+"',lambda m:'href="'+escape(o['launcher']['discord'],quote=True)+'"',html)
 return html
