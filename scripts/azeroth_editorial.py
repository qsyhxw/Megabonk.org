"""Page-scoped editorial presentation; retain raw evidence in source modules."""
from pathlib import Path
from html import escape
import json,re
ROOT=Path(__file__).resolve().parents[1]
REF=re.compile(r'<sup class="ref"><a href="#source-(\d+)"[^>]*>.*?</a></sup>')
NATURAL={'','beginners-guide','play','ru/play','de/play','zh-hant/play'}

NOVEMBER_UPDATES = {
 'zones-bosses': ('Scholomance and the displayed encounter clock',
  '<p>Checked 11 November 2026 against original v0.143.2. Scholomance, subtitled The Great Ossuary, is now present in the original client, with Darkmaster Gandling named in its zone description. The twelve-zone table below preserves the 30 October route. Inspect the current picker for Scholomance access before planning a run.</p><p>Read the selected mode before using an older boss timer. The current client includes Hyper Mode and a Heroic V unlock prompt. Use the requirement shown in your Difficulty panel, then check its encounter clock. The Elwynn times below belong to the earlier standard-mode capture.</p>'),
 'armory': ('Tier 0.5 collection checks before another run',
  '<p>Checked 11 November 2026 against original v0.143.2. The current Armory describes zone drops for your selected class, one piece possible from each boss, and priority for missing pieces until both are collected. It separately says Darkmaster Gandling’s weapons drop together. Check the class and the named encounter in Drop Tables before farming a missing slot.</p><ol><li>Inspect the class-specific Tier 0.5 collection and identify the missing armour slot or fixed Gandling weapon reward.</li><li>Use its current zone and boss entry to choose the run. The collection achievement requires all eight Scholomance armour pieces and the full fixed weapon reward for each of nine classes.</li><li>After the run, recheck the missing-piece list. A possible drop and missing-piece priority do not establish a guaranteed reward on the next kill.</li></ol>'),
 'achievements-rewards': ('Scholomance completion and The Insane',
  '<p>Checked 11 November 2026 against original v0.143.2. Decide whether you are pursuing collection, class clears or a group survival achievement before spending time on a run.</p><ul><li>The Scholomance collection requirement names eight Tier 0.5 armour pieces plus the full fixed Gandling weapon reward for each of nine classes.</li><li>Yes, I am prepared! requires solo Scholomance Heroic V completion with all nine classes, using each class’s Tier 0.5 set bonuses and matching specialization talents. Collecting the equipment alone does not satisfy the clear requirement.</li><li>The Insane requirement names at least 40 minutes in Naxxramas Heroic V with at least two other players and no deaths. Plan a party of at least three and survival for the full stated duration. A revive does not remove a death from this requirement. The Unholy weapon glow is tied to this achievement.</li></ul><p>Track the class clear or collection counter after each attempt. These are current displayed requirements. Completion and reward delivery have not been tested here.</p>'),
 'co-op': ('When a hero misses the run or a card is selected automatically',
  '<p>Checked 11 November 2026 against original v0.143.2. A new message says a hero that took too long to enter sits out this run and is in for the next one. If you see it, coordinate the next start with the host and check that your selected hero is ready before they enter.</p><p>The client also distinguishes a hero already in the party, a rejected host request with a stated reason, and a card taken for a hero that was too slow to choose. Read the actual party-chat message before retrying a join or interpreting a changed card as lost progress. Save the exact host-error reason when asking for help.</p><p>These prompts support the next checks above. They do not establish a universal reconnect timeout or recovery guarantee.</p>'),
 'patch-notes': ('Returning-player checks for v0.143.2',
  '<p>Original v0.143.2 was re-read on 11 November 2026. Start with the task that changed your next run.</p><ul><li><a href="/azeroth-survivors/zones-bosses/#november-review">Zone and mode checks</a> cover Scholomance and the clock boundary for older standard-mode timers.</li><li><a href="/azeroth-survivors/armory/#november-review">Tier 0.5 targeting</a> separates missing armour pieces from Gandling’s fixed weapon reward.</li><li><a href="/azeroth-survivors/achievements-rewards/#november-review">Achievement planning</a> separates collection, nine solo class clears and The Insane’s group/no-death condition.</li><li><a href="/azeroth-survivors/co-op/#november-review">Party-message checks</a> explain sitting out a run and an automatically selected card.</li></ul><p>These checks use current original-client text. Earlier class allocations and rank-dependent effects keep their recorded versions.</p>'),
}

def editorial(path,text):
 records=json.loads((ROOT/'data/azeroth-editorial.json').read_text(encoding='utf8'))
 key=path.lstrip('/')+'index.html'
 if key not in records:return text
 slug=path.removeprefix('/azeroth-survivors/').strip('/')
 record=records[key]
 section=re.search(r'<section[^>]*id="sources"[^>]*>.*?</section>',text,re.S)
 assert section,path
 entries={x['id']:x for x in record['sources']}
 links={};items=[]
 for n,body in re.findall(r'<li[^>]*id="source-(\d+)"[^>]*>(.*?)</li>',section[0],re.S):
  link=re.search(r'<a\b.*?</a>',body,re.S)[0];url=re.search(r'href="([^"]+)"',link)[1]
  e=entries[n];assert e['url']==url,(path,n,url)
  links[n]=link
  if slug!='' or int(n)<4:
   items.append(f'<li id="source-{n}">{link} · {escape(e["summary"])}</li>')
 heading={'ru/play':'Источники','ru/builds':'Источники','de/play':'Quellen','zh-hant/play':'檢查依據'}.get(slug,'Sources &amp; checks')
 tag='ul' if slug in NATURAL else 'ol'
 # Keep the existing copyright attribution, without the repeated acquisition log.
 credit='<p class="icon-credit">Warcraft artwork © Blizzard Entertainment.</p>' if 'class="icon-credit"'in section[0] else ''
 source=f'<section class="sources" id="sources"><h2>{heading}</h2>{credit}<{tag}>'+''.join(items)+f'</{tag}></section>'
 text=text[:section.start()]+source+text[section.end():]
 if slug in NATURAL:
  # Home entity comparisons need their specific source; basic entry facts already
  # have an explicit original-host action link. Keep distinct evidence adjacent.
  linked=set()
  def natural(m):
   n=m[1]
   if slug=='' and int(n)>=4:
    anchor='' if n in linked else f' id="source-{n}"'
    linked.add(n)
    return f' <span class="source-link"{anchor}>('+links[n]+')</span>'
   return ''
  text=REF.sub(natural,text)
 else:
  def paragraph(m):
   seen=set()
   def once(ref):
    if ref[1]in seen:return ''
    seen.add(ref[1]);return ref[0]
   return REF.sub(once,m[0])
  text=re.sub(r'<p\b[^>]*>.*?</p>',paragraph,text,flags=re.S)
 text=text.replace('These links open the original host; the top Play entry uses the separately labelled third-party provider.', 'These links and the top Play guide lead to Aethus’s original game. Keep a backup before changing hosts.')
 text=text.replace('The screenshot below records an earlier original-client menu, with its version and capture date.', 'The screenshot shows the original v0.130.0 menu captured on 30 October 2026.')
 if slug in NOVEMBER_UPDATES:
  title,body=NOVEMBER_UPDATES[slug]
  source='<p>Source for this section · <a href="https://wow.aethus.pl/" target="_blank" rel="noopener noreferrer">Aethus’s original client ↗<span class="sr-only"> (opens in a new tab)</span></a>. Displayed text checked in v0.143.2 on 11 November 2026.</p>'
  addition=f'<section id="november-review"><h2>{title}</h2>{body}{source}</section>'
  text=text.replace('<strong>On this page</strong>','<strong>On this page</strong><a href="#november-review">'+title+'</a>',1)
  text=re.sub(r'(<article class="prose">.*?)(<section\b)',lambda m:m[1]+addition+m[2],text,count=1,flags=re.S)
  if slug=='zones-bosses':
   text=text.replace('Original-game progression route','Earlier standard-mode progression route (30 October)')
   text=text.replace('these twelve original zones','this earlier twelve-zone capture')
 return text
