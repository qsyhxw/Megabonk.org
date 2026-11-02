"""Dated primary-client changes and individually credited reference icons."""
from pathlib import Path
import json,re
from azeroth_survivors_content import SOURCES,a,ext,ref,para,steps,table
ROOT=Path(__file__).resolve().parents[1]
NOTE='2 November 2026 · Selected original-client v0.139.0 strings rechecked; earlier sections retain their dated scope · Source research, not a gameplay or all-rank test'

def checked(text):
 return para(text+ref('nov2'))

def refresh(pages):
 SOURCES['nov2']=('https://wow.aethus.pl/','Aethus · original client, 2 November','Original launcher stamp f339dd20e0fe; downloaded client embeds v0.139.0. Localized strings checked 2 November 2026. Client SHA-256 71a44d44a91245aa0a4db4171b5893e4343ba84c3699f7fa87dafc2856973299. Selected text comparisons with the 30 October v0.130 snapshot; not a complete release history, numeric talent export or gameplay test.')
 for d in pages:
  slug=d['slug']
  if slug=='builds/shaman/':
   d['parts']=[(i,t,h) for i,t,h in d['parts'] if i!='third-route']
   revised=[]
   for i,t,h in d['parts']:
    if i=='choose':h=h.replace('splitting every choice among lightning, wolves and fire totems','splitting every choice among unrelated damage engines')
    if i=='talents':
     h=re.sub(r'<tr><td>Enhancement</td>.*?</tr>','',h,flags=re.S)
     h=checked('Enhancement changed in v0.139. Do not reuse the earlier Windfury / Maelstrom Weapon / Feral Spirit checkpoints. '+a('builds/shaman/#third-route','Use the Rockbiter / Stormstrike checks below')+'. The Elemental and Restoration rows retained here describe the dated v0.130 snapshot, not newly verified v0.139 allocations.')+h
     t='Earlier Elemental and Restoration checkpoints'
    revised.append((i,t,h))
   d['parts']=revised
   d['parts'].append(('third-route','Enhancement in v0.139: Rockbiter into Stormstrike',checked('The older Windfury-and-wolves summary no longer describes this client’s Enhancement wording. Rockbiter Initiation changes the starter from Lightning Bolt to Rockbiter Weapon; the new capstone text changes it again to Stormstrike. Read your allocated endpoint before choosing support cards.')+table(['Verified interaction','What to do with it'],[
    ['Windfury Weapon names Rockbiter and Stormstrike; its chance remains a rank placeholder.','Support these attacks when allocated; do not assume the old Lightning Bolt/Shock repeat trigger.'],
    ['Elemental Sunder makes enemies hit by Rockbiter or Stormstrike take 10% more Fire and Nature damage for 4 seconds.','Keep the triggering attack working before relying on that damage window.'],
    ['Stormguard reduces damage while Lightning Shield is active; rank value unresolved.','Check shield uptime before treating it as permanent defence.'],
    ['Shattering Elements rewards the next different Shock within 6 seconds.','Read which Shock spells you actually have; repeated identical casts do not satisfy that wording.'],
    ['The capstone describes extra Enhancement proc triggers and healing for 1% of damage dealt.','Do not spend a full point plan from this guide: exact rank chances and prerequisites are not exported here.']])+checked('These are original string-level checks, not measured proc rates or a proven optimal order. Earlier totem/lightning sections and the game screenshot keep their older capture dates. '+a('abilities/#talent-names','Find the two talent-learned spell names')+' · '+a('talents/','Point-budget checks'))))
   d['review_note']=NOTE
  if slug=='abilities/':
   d['answer']='Search the 103-name baseline in any listed client language, then open its class route. These names were rechecked against original v0.139.0 on 2 November. The original class grouping remains a dated picker/Codex snapshot; it does not prove the complete current selectable pool. Two newly checked talent-learned Shaman names are listed separately below.'+ref('nov2')
   d['parts']=[(i,t,h.replace('The name set is a preserved 30 October snapshot, re-read on 1 November.','The original 103-name baseline was rechecked in the 2 November v0.139 client; class grouping remains from 30 October.')) for i,t,h in d['parts']]
   d['parts'].insert(1,('talent-names','Shaman names learned through talents',checked('Rockbiter Weapon and Stormstrike are not added to the 103-row ordinary baseline. The current client associates the changed starting attacks with Enhancement milestones/capstone; a name in the client is not proof of an ordinary upgrade-card offer.')+table(['English name','简体中文 client name','Use'],[[s['en'],s['zh'],a('builds/shaman/#third-route','Read the updated Enhancement route')] for s in json.loads((ROOT/'data/azeroth-current-review.json').read_text(encoding='utf8'))['talent_spell_names']])) )
   d['review_note']=NOTE
  if slug=='co-op/':
   d['parts'].append(('ready-check','Read a ready check before changing zones',checked('The v0.139 client includes a host-requested zone ready check with ready, not ready, no answer and called off states. A pending answer is different from a network refusal; a cancelled check is not proof that your save is broken.')+steps(['Read the named host and destination before responding.','If you are not prepared to leave, choose not ready rather than relying on silence.','If the check is called off, ask the host whether to try again; use the connection-error table above only when that error actually appears.'])+checked('This verifies the client’s prompts, not a completed multiplayer session, permission rules or reconnect behaviour in v0.139.')))
   d['review_note']=NOTE
  if slug=='best-race/':
   d['parts'].insert(0,('nov2-races','Two racial values to recheck in v0.139',checked('The original client now describes Human as +20% experience, versus +10% in the earlier snapshot. Dwarf now describes a shield every 30 seconds worth 45% of maximum health, versus every 45 seconds and 30% before. These are displayed text comparisons, not measured damage reduction or a universal race ranking. Read the current race panel before spending a permanent unlock.')))
   d['parts']=[(i,t,h.replace('+10% XP','+20% XP').replace('30% max HP shield every 45s','45% max HP shield every 30s')) for i,t,h in d['parts']]
   d['review_note']=NOTE
  if slug=='patch-notes/':
   d['answer']='The original client downloaded on 2 November embeds v0.139.0. Compare the selected verified text changes with our 30 October v0.130 snapshot before copying an older route. This page connects those differences to practical guide sections; it is not the creator’s full release log.'+ref('nov2')
   d['parts'].insert(0,('nov2','2 November client comparison: v0.130 → v0.139',checked('The original launcher served a client embedding v0.139.0 on 2 November. This is a comparison with our 30 October capture, not a dated release-by-release changelog. The most consequential verified text changes are the Enhancement starter/trigger rewrite, Human experience and Dwarf shield wording.')+para(a('builds/shaman/#third-route','Updated Enhancement decisions')+' · '+a('best-race/#nov2-races','Exact racial text differences')+' · '+a('co-op/#ready-check','Ready-check states')+' · '+a('abilities/#talent-names','Talent-learned Shaman names'))+checked('New UI strings also describe a local clock under the minimap, stacking or overlapping nameplates, and an update check with success/failure states. A string’s presence does not establish that every feature succeeds on every host. No full 355-node rank table or combat benchmark is inferred from localized text.')))
   d['review_note']=NOTE
  if slug=='troubleshooting/':
   d['parts'].append(('client-update','When the client says an update is waiting',checked('The v0.139 text distinguishes an up-to-date result, an update check failure, a download in progress and a newer version waiting in the hero picker. Record the exact result and displayed version. A failed update check alone does not establish a GPU failure; preserve a save export before changing client or host. These prompts were checked in client strings, not by completing the update flow.')))
   d['review_note']=NOTE
 return pages
