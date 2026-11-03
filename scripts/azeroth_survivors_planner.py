"""Original editorial planner page, examples and scoped links for B1–B6."""
from html import escape
from pathlib import Path
import json
from azeroth_survivors_content import P,SOURCES,a,ref,para,steps,table
from azeroth_planner_reference import reference,SOURCE_SHA

ROOT=Path(__file__).resolve().parents[1]
DATA=reference()
REVIEW='Reviewed 3 November 2026 · Original v0.139.2 / 5cb6deb36 · Mage/Warlock talent UI and source text checked; older sections retain their dates · No completed-run or damage test'

def register_source():
 SOURCES['planner139']=('https://wow.aethus.pl/','Aethus · original v0.139.2',
  'Original v0.139.2 / 5cb6deb36 read 3 November 2026; client SHA-256 '+SOURCE_SHA+'. All 79 Mage/Warlock talent tooltips were visually inspected: rank caps, same-tree row gates, named prerequisites and the two Warlock exclusion pairs. The original screen shows 51 points maximum. Mage/Warlock Collection panels name the two example head pieces and Kurinnaxx. Source-based menu research on a fresh 0-point profile; no allocation spent in the game, boss kill, full-run test, drop-rate experiment or best-build benchmark.')

def cited(text):return para(text+ref('planner139'))

def example_table(key):
 item=DATA['examples'][key];nodes={n['id']:n for t in DATA['classes'][item['classId']]['trees'] for n in t['nodes']}
 groups=[];ranks={}
 for i,id in enumerate(item['sequence'],1):
  ranks[id]=ranks.get(id,0)+1
  if groups and groups[-1]['id']==id:groups[-1].update(end=i,rank=ranks[id])
  else:groups.append(dict(id=id,start=i,end=i,rank=ranks[id]))
 return table(['Points in this sequence','Talent','Rank reached'],[
  [str(g['start']) if g['start']==g['end'] else f"{g['start']}–{g['end']}",escape(nodes[g['id']]['name']),f"{g['rank']}/{nodes[g['id']]['max']}"] for g in groups])

def example_section(cls):
 key='mage-fire' if cls=='mage' else 'warlock-affliction';item=DATA['examples'][key]
 text=cited('This is our editable '+('Fire' if cls=='mage' else 'Affliction')+' example, built around the inspected original tree. The sequence spends 31 points, satisfies the recorded rank caps and prerequisites, and leaves 20 points unallocated. It is a practical core to examine, not a measured best build or proof that your character has earned the points.')
 if cls=='mage':text+=para('Use this example when you want to develop Fire. If you prefer the Frost control route described above, keep that choice and build your own plan in its checked tree.')
 text+=example_table(key)+para(escape(item['skills']))+para(escape(item['gear']))+para(escape(item['notes']))
 text+=para(a('build-planner/#example='+key,'Open and adapt this example')+' · '+a('talents/#budgets','Check the point gates'))
 return ('allocation-example','A 31-point example you can edit',text)

def planner_page():
 register_source()
 controls=f'''<div class="planner-intro"><strong>Two classes, six checked trees.</strong><p>Plan Mage or Warlock talents against the original v0.139.2 snapshot. Other classes remain in the <a href="{P}builds/">class route index</a>. Use your earned budget; the planner cannot read your game.</p></div>
<div id="planner-load-status" role="status">Loading the checked reference…</div><div id="planner-editor" hidden>
<div class="planner-controls"><label>Class<select id="plan-class"><option value="mage">Mage</option><option value="warlock">Warlock</option></select></label><label>Points available<input id="plan-budget" type="number" min="0" max="51" step="1" value="51"></label><label>Plan name<input id="plan-name" maxlength="100" autocomplete="off" placeholder="A plan for my next run"></label></div>
<div class="planner-actions"><button type="button" data-example="mage-fire">Load Fire example · 31 points</button><button type="button" data-example="warlock-affliction">Load Affliction example · 31 points</button><button type="button" id="plan-reset">Clear this class draft</button></div>
<p>Add one point at a time. A row gate counts points already in that tree; its node costs another point. Refund removes the latest point in that talent and is blocked if it would break a later step.</p>
<div id="planner-trees" class="planner-trees"></div>
<div class="planner-notes"><label>Skill priorities<textarea id="plan-skills" maxlength="800" placeholder="Record which offers support this plan."></textarea></label><label>Equipment checks<textarea id="plan-gear" maxlength="800" placeholder="Record worn gear, a missing piece or an alternative."></textarea></label><label>Run notes<textarea id="plan-notes" maxlength="1600" placeholder="Version, zone, difficulty and the problem to solve. Avoid personal information."></textarea></label></div>
<div class="planner-actions"><button id="plan-save" type="button">Save browser draft</button><button id="plan-load" type="button">Load browser draft</button><button id="plan-forget" type="button">Remove saved draft</button><label>Import planner JSON <input id="plan-upload" type="file" accept="application/json,.json"></label></div>
<p>Saving keeps one draft in this browser. Import accepts a planner export, not a game save, and reads it locally. A share link includes your notes; keep private information out. <a href="/privacy-policy#azeroth-build-planner">Planner privacy details →</a></p></div>
<noscript><p>JavaScript is required to edit a plan. The two examples below and the gate rules remain readable. No game files are loaded by this tool.</p></noscript>
<div id="plan-tray" class="plan-tray" hidden><div class="tray-copy"><strong id="plan-count">0 / 51 points</strong><p id="plan-message" role="status" aria-live="polite"></p></div><button id="plan-open" type="button">View plan &amp; share</button></div>
<dialog id="plan-dialog" aria-labelledby="plan-dialog-title"><h2 id="plan-dialog-title">Your talent plan</h2><button type="button" id="plan-close">Close plan</button><div id="plan-result"></div><div class="plan-share"><label for="plan-link">Plan link</label><input id="plan-link" readonly><div class="planner-actions"><button id="plan-copy" type="button">Copy plan link</button><button id="plan-download" type="button">Download planner JSON</button></div><p id="plan-share-status" role="status"></p></div></dialog>'''
 examples=''
 for key,item in DATA['examples'].items():
  examples+='<div class="planner-example"><h3>'+escape(item['name'])+'</h3>'+example_table(key)+para(escape(item['notes']))+para(a('builds/'+item['classId']+'/#allocation-example','Read the example in context'))+'</div>'
 observed=json.loads((ROOT/'data/azeroth-sync.json').read_text(encoding='utf8'))['observed']
 warning=para('Needs verification: the monitored original has changed since this planner snapshot. The tool still edits the dated v0.139.2 rules; recheck the current game before applying a plan.') if observed['client_sha256']!=SOURCE_SHA else ''
 return dict(id='AZB01',slug='build-planner/',title='Azeroth Survivors Build Planner & Talent Calculator',h1='Plan your Azeroth Survivors build',
  desc='Plan Mage and Warlock talents with checked gates, editable 31-point examples and share links. Keep skill and gear notes together without a game account.',
  answer='Choose Mage or Warlock, set your earned point budget and build a talent route one point at a time. Review the order, save a browser draft or share a link. The tool checks recorded talent rules; it does not predict damage or edit your game save.'+ref('planner139'),
  review_note=REVIEW,
  parts=[('planner-workbench','Build your talent route',warning+controls),
   ('examples','Two editable starting examples',cited('Both examples are editorial 31-point cores checked against the recorded v0.139.2 rules. Neither spends your last 20 points or claims a guaranteed card sequence.')+examples),
   ('rules','What the calculator checks',table(['Check','How to use it'],[
    ['Budget','Set 0–51 points, matching what your character has earned. The cap is shared across the three trees.'],
    ['Row gates','Spend within the same tree first. A gate at 10, 20 or 30 does not include the additional point buying its node.'],
    ['Named prerequisites','The checked rank is required, not just an earlier node name. Legion Gate needs Soul Devourer 3/3 or Soul Link 3/3.'],
    ['Exclusions','Soul Devourer and Soul Link cannot coexist. Pact of the Nathrezim and Butcher cannot coexist.'],
    ['Refunds','A point can be removed only if every later step remains valid. Remove dependent steps first.']])+cited('These are original-menu rules observed on 3 November. A valid sequence means the recorded rules passed; it is not a test of actual combat, gear unlocks or every later patch.')),
   ('scope','Versions, saves and next checks',steps(['Compare the version in your game with the planner snapshot. A newer source needs verification before applying an old allocation.','Use the skill and equipment notes to record choices; they do not grant cards, gear or achievements.','Keep a game-save export separately. A planner JSON file cannot be imported as a game save.','Use the original client to inspect your actual ranks and starter after allocating.'])+para(a('abilities/','Look up a spell')+' · '+a('armory/#build-loot','Find a missing equipment piece')+' · '+a('items/','Compare in-run jewelry')))],
  related=[('builds/','Compare class routes'),('talents/','Read talent gates'),('save-backup/','Keep a game-save export')])

def apply_planner(pages):
 register_source()
 for d in pages:
  slug=d['slug']
  if slug in ['builds/mage/','builds/warlock/']:
   cls=slug.split('/')[1];d['parts'].insert(1,example_section(cls));d['review_note']=REVIEW
   updated=[]
   for i,t,h in d['parts']:
    if cls=='mage' and i=='arcane-plan':
     h+=cited('The current Arcane Power tooltip adds a bounded cascade: a spell that strikes twice can roll to strike again, up to three further strikes in a row. Arcane Reach and the capstone are not an unlimited repeat loop. The amount of damage gained has not been benchmarked here.')
    if cls=='warlock' and i=='current-demonology':
     t='v0.139.2 Demonology: choose the summon system first'
     h=cited('Soul Devourer and Soul Link each require Demonic Familiar 5/5 and exclude one another. Legion Gate needs three ranks in either branch; the names alone do not satisfy it. Its normal lesser-demon behaviour changes when Demonic Supremacy makes Infernal and Doomguard permanent and prevents lesser summons.')
     h+=cited('Pact of the Nathrezim and Butcher both require Legion Gate and exclude each other. The observed tooltip shows a 20-second Dread Lord or Felguard duration, a 30-second base interval and a 13-second cooldown-reduced floor, with up to two active. Felseeker explicitly inherits Searing Pain upgrades; that link is not a general rule for the Felguard. These are tooltip observations, not a summon-duration or damage test.')
    if i=='gear-picks':
     piece='Frostfire Circlet' if cls=='mage' else 'Plagueheart Circlet'
     h+=cited('For a concrete later-game lookup, the inspected '+cls.title()+' Collection panel lists '+piece+' from Kurinnaxx in Gates of Ahn’Qiraj. This is a location example, not a required item for the talent core or a verified farming rate. Keep useful worn gear while access is locked. '+a('armory/#build-loot','Follow the equipment lookup')+' · '+a('zones-bosses/#aq-targets','Check the encounter target'))
    updated.append((i,t,h))
   d['parts']=updated
  if slug=='talents/':
   d['parts'].insert(0,('plan-entry','Find a rule or record a route',para('For the point arithmetic, use the budget table below. For a named node, inspect its rank cap and prerequisites in your game. To keep an ordered Mage or Warlock allocation, '+a('build-planner/','open the checked planner')+'. It starts from a blank draft or one of two editable 31-point examples.')))
   d['review_note']=REVIEW.replace('Mage/Warlock talent UI','Talent budget and Mage/Warlock UI')
   d['parts']=[(i,t,h.replace('these guides do not supply a complete legal 51-point recipe.','the planner supplies two rule-checked 31-point examples, not a verified optimal 51-point recipe.')) for i,t,h in d['parts']]
  if slug=='builds/':
   d['parts'].insert(0,('planner','Record a build instead of keeping it in your head',para(a('build-planner/','Mage &amp; Warlock build planner and talent calculator')+' checks a dated set of rank caps, row gates and exclusions. Start from your earned budget, inspect an editable 31-point core, then keep the talent order with skill and gear notes. For other classes, use the route table below and check the current tree in the game.')))
  if slug=='armory/':
   d['review_note']=d.get('review_note','Reviewed 30 October 2026 · Original v0.130.0')+' · The equipment-source examples were checked in the v0.139.2 Collection menu on 3 November; earlier sections retain their dates.'
   d['parts']=[(i,t,h.replace('The captured fresh Shaman collection is empty; it documents where to inspect items, not a successful loot or upgrade test.','The current Warlock capture below shows an uncollected piece and its source panel. It documents a menu lookup, not a successful loot or upgrade test.')) for i,t,h in d['parts']]
   d['parts'].insert(1,('build-loot','From a build idea to a specific missing piece',cited('Choose the class in the original client, open Collection and select a piece. Read its own Drops from panel before repeating a zone. Two panels inspected on 3 November give concrete examples:')+table(['Class','Piece shown','Encounter listed','Continue'],[
    ['Mage','Frostfire Circlet','Kurinnaxx · Gates of Ahn’Qiraj',a('builds/mage/#allocation-example','Keep the talent core separate')],
    ['Warlock','Plagueheart Circlet','Kurinnaxx · Gates of Ahn’Qiraj',a('builds/warlock/#allocation-example','Keep the talent core separate')]])+para('A listed source is not ownership or an unlocked star cap. Check access with '+a('zones-bosses/#aq-targets','the encounter checklist')+', then compare the worn piece and upgrade permission. These menu observations do not establish a drop rate or best-in-slot set.')))
  if slug=='zones-bosses/':
   d['review_note']=d.get('review_note','Reviewed 30 October 2026 · Original v0.130.0')+' · The Kurinnaxx equipment-source examples were checked in v0.139.2 on 3 November; no new encounter test.'
   d['parts'].append(('aq-targets','An equipment target in Gates of Ahn’Qiraj',cited('The Mage Frostfire Circlet and Warlock Plagueheart Circlet panels inspected in original v0.139.2 both list Kurinnaxx in Gates of Ahn’Qiraj. Use the class-specific Collection or Drop Tables panel to confirm your target and access before starting. This lookup does not establish that the piece will drop on your next run.')+para(a('armory/#build-loot','Inspect the equipment lookup')+' · '+a('builds/mage/#allocation-example','Mage example')+' · '+a('builds/warlock/#allocation-example','Warlock example'))))
 return pages+[planner_page()]

def home_entry(html):
 needle='<section class="section" id="guides"><h2>The guide index</h2>'
 return html.replace(needle,needle+para(a('build-planner/','Build planner: Mage &amp; Warlock talent routes')+' — record point order, check prerequisites and share a plan.'),1)

def planner_assets(path,html):
 if path!=P+'build-planner/':return html
 html=html.replace('<body class="az guide-layout">','<body class="az guide-layout planner-page">')
 html=html.replace('<section id="planner-workbench">','<section id="planner-workbench" data-source="'+SOURCE_SHA+'">')
 return html.replace('</head>','<link rel="stylesheet" href="/assets/azeroth-survivors/planner.css"><script defer src="/assets/azeroth-survivors/planner-core.js"></script><script defer src="/assets/azeroth-survivors/planner.js"></script></head>')
