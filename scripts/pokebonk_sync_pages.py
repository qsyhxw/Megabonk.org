"""Publish source freshness separately from dated editorial review."""
from pathlib import Path
from html import escape as e
import json,re
ROOT=Path(__file__).resolve().parents[1]
TOOLS=['pokemon','build-planner','moves','lab','items-vitamins','starters','tier-list','alpha-support','builds','unlocks','ultimates','evolution','time-attack','type-chart','reactions','move-fusions']
def apply_sync_pages(ctx):
 path=ROOT/'data/pokebonk-sync.json'
 if not path.exists():return
 state=json.loads(path.read_text(encoding='utf8'));version=e(state['observed']['version']);pending=state['pending'];P,pages=ctx['P'],ctx['PAGES']
 def cite(p):
  s=p['html'];url=state['source']['config']
  old=[int(n)for n,body in re.findall(r'<li id="source-(\d+)">(.*?)</li>',s,re.S)if url in body]
  if old:return ctx['ref'](old[0])
  n=max(map(int,re.findall(r'id="source-(\d+)"',s)),default=0)+1
  if '<section class="sources"'not in s:return ''
  i=s.index('</ol>',s.index('<section class="sources"'));p['html']=s[:i]+f'<li id="source-{n}">'+ctx['ext'](url,'pokebonk.com — automatically observed public configuration')+' — Source version '+version+'; observation '+e(state['changed_at'])+'. Automated extraction is not a gameplay test or a new review of every paragraph.</li>'+s[i:];return ctx['ref'](n)
 for slug in ['',*TOOLS,'updates']:
  p=pages[P+(slug+'/'if slug else'')];c=cite(p)
  warning=' <strong>Review pending:</strong> '+e(' '.join(pending))if pending else' Routes, conditional effects, capture instructions and recommendations retain their own dated editorial review.'
  names={'lab':'Lab prices','items':'item cards','moves':'move templates','league':'partner data','alpha':'Alpha bonuses'}
  note='<aside id="source-sync" class="note"><details><summary><strong>Source version v'+version+'</strong> · '+('Changes need review · 'if pending else'')+'View data dates and limits</summary><p>Source observation '+e(state['changed_at'][:10])+'. Data snapshots: '+e(', '.join(names[k]+' (v'+v['version']+')'for k,v in state['accepted'].items()))+'. A source version is separate from a gameplay review.'+warning+' <a href="/pokebonk/updates/#source-monitor">See automatic update scope →</a>'+c+'</p></details></aside>'
  if slug=='':
   p['html']=p['html'].replace('<section class="section" id="guides">',note+'<section class="section" id="guides">',1).replace('Version checked October 29, 2026 · Original v0.8.75','Gameplay rules reviewed October 29, 2026 · Original v0.8.75')
  else:p['html']=re.sub(r'(<p class="meta">.*?</p>)',lambda m:m[1]+note,p['html'],count=1,flags=re.S)
 p=pages[P+'updates/'];c=cite(p)
 rows=[[e(x['version']),e(x['title'])]for x in state['news']]
 text='<p>The original host reports v'+version+'. The record below is collected from public project definitions. Release statements describe intended behavior; they are not reproduced game results.</p>'+ctx['table'](['Source release','Project heading'],rows)
 text+='<p><strong>Automatic scope:</strong> checked Lab schedules; existing item cards, League kits, fixed passives, species baselines, move templates and Alpha definitions when the source adapter and validation pass. Formula changes, new or removed entities, capture prerequisites, routes, mode rules and build recommendations require another review. The separately hosted Play edition is not updated by this process.</p><p>Checks run about every six hours. An unchanged source makes no commit and does not refresh guide dates. On collection or validation failure the last accepted data stays online; the failed run is recorded in GitHub Actions. The source-observation date above records a changed snapshot, not a guaranteed service-availability check.</p>'
 if pending:text+='<p><strong>Pending review:</strong></p><ul>'+''.join('<li>'+e(x)+'</li>'for x in pending)+'</ul>'
 text+='<p>'+ctx['ext']('https://github.com/qsyhxw/Megabonk.org/actions/workflows/sync-pokebonk.yml','GitHub — PokeBonk source sync runs')+'</p>'+c
 p['html']=p['html'].replace('<section class="sources"',ctx['section']('source-monitor','Automatic source updates and review scope',text)+'<section class="sources"',1).replace('<strong>On this page</strong>','<strong>On this page</strong><a href="#source-monitor">Automatic source updates and review scope</a>',1)
 p['html']=re.sub(r'<p class="answer">.*?</p>','<p class="answer">Original pokebonk.com currently reports v'+version+'. Automatic data checks and the pending-review list are available below; the manually reviewed .75 gameplay notes remain dated and are not presented as a new full-run test.'+c+' Earlier mechanism snapshots: '+ctx['ref'](1)+ctx['ref'](2)+'</p>',p['html'],count=1,flags=re.S)
