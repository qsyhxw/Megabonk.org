"""Rebuild the independent Ball x Pit hub. No expectation configuration is generated."""
from site_analytics import write_html
from pathlib import Path
from html import escape as e
import json,re
from ball_x_pit_data import SOURCES,BALLS,ITEMS,CHARACTERS
from ball_x_pit_content import pages,table,paras,items
from guide_images import decorate
ROOT=Path(__file__).resolve().parents[1]
P='/ball-x-pit/'
BASE='https://megabonk.org'
DATE='2026-10-30'
ADS='<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8830315294299920" crossorigin="anonymous"></script>'
NAV=[('Start here','beginners-guide/'),('Evolutions','evolutions/'),('Builds','builds/'),('Progress','trophy-guide/')]
def slug(s):return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')
def ext(url,label):return f'<a href="{e(url,quote=True)}" target="_blank" rel="noopener noreferrer">{e(label)} ↗</a>'
def shell(path,title,desc,body,ordinary=False,tool=False,error=False,image=False):
 """全站外壳：theme.css 全部页面，hub.css 仅首页；导航/页脚由 register_page.py 按页面清单覆盖。"""
 nav=''.join(f'<a href="{P+u}"'+(' aria-current="page"' if path==P+u else '')+'>'+l+'</a>' for l,u in NAV)+'<a href="/#more-games">More games</a>'
 hub=path==P
 FORMATS={'':'hub'}|{k+'/':'other' for k in ['beginners-guide','builds','character-tier-list','characters','evolutions','new-evolutions','passive-evolutions','ghostly-shield','trophy-guide']}
 key=path[len(P):] if path.startswith(P) else ''
 fmt=f' data-format="{FORMATS[key]}"' if (ordinary and key in FORMATS) else ''
 return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc,quote=True)}"><link rel="canonical" href="{BASE+path}">
{ADS if ordinary else ''}{'<meta name="robots" content="noindex,follow">' if error else ''}
<link rel="icon" href="/favicon.ico"><link rel="stylesheet" href="/assets/guide-article-layout.css"><link rel="stylesheet" href="/assets/ball-x-pit/theme.css">{'<link rel="stylesheet" href="/assets/ball-x-pit/hub.css">' if hub else ''}
<meta property="og:type" content="{'website' if path==P else 'article'}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc,quote=True)}"><meta property="og:url" content="{BASE+path}">
{f'<meta property="og:image" content="{BASE}/assets/ball-x-pit/images/ball-2-1280.webp">' if image else ''}
{'<script defer src="/assets/ball-x-pit/tool.js"></script>' if tool else ''}</head><body class="bxp-theme guide-layout {'bxp-hub' if hub else 'bxp-guide'}"{fmt}><a class="skip" href="#main">Skip to content</a>
<header class="top"><div class="wrap"><a class="brand" href="{P}"><img src="/assets/ball-x-pit/logo.svg" width="44" height="44" alt=""><span>BALL x PIT<small>Recipes · Builds · Unlocks</small></span></a><nav class="desktop-nav" aria-label="Main navigation">{nav}</nav><details class="mobile-nav"><summary>Menu ☰</summary><nav class="mobile-links" aria-label="Mobile navigation">{nav}</nav></details></div></header>
<main class="wrap" id="main">{body}</main><footer class="site-footer"></footer></body></html>'''
BUMP={'builds','characters','evolutions','new-evolutions'}  # 2026-11-21 Risen Ballbylon 上线，仅这些页的相关表述已复核
def citations(body,when='30 October 2026'):
 used=[]
 def sub(m):
  key=m[1]
  if key not in used:used.append(key)
  n=used.index(key)+1
  return f'<sup class="ref"><a href="#source-{n}" aria-label="Source {n}">[{n}]</a></sup>'
 body=re.sub(r'\[source:([a-z]+)\]',sub,body)
 refs=f'<section class="sources" id="sources"><h2>Sources & evidence limits</h2><ol>'+''.join(f'<li id="source-{i}">{ext(SOURCES[k][0],SOURCES[k][1])} — {e(SOURCES[k][2])}.</li>' for i,k in enumerate(used,1))+f'</ol><p>Checked {when}. Community reports can change with patches. We have not played these routes or benchmarked builds.</p><a href="#guide">Back to the answer ↑</a></section>'
 return body+refs
def recipe_table(data):
 return table(['Evolution','Ingredients','Set / source'],[[f'<strong>{e(r["name"])}</strong>',e(' + '.join(r['inputs']))+(' <small>Also: '+e(' or '.join(' + '.join(a) for a in r['alternatives']))+'</small>' if r['alternatives'] else ''),e(r['version'])+' [source:'+r['source']+']'] for r in data])
def planner(data,kind,added=False):
 names=sorted({x for r in data for x in [r['name']]+r['inputs']},key=str.casefold)
 opts='<option value="">Nothing selected</option>'+''.join(f'<option>{e(x)}</option>' for x in names)
 targets='<option value="">Choose an evolution</option>'+''.join(f'<option>{e(r["name"])}</option>' for r in sorted(data,key=lambda x:x['name']) if not added or r['version']!='Base')
 return f'''<div class="tool" data-planner><p class="eyebrow">{kind} recipe workbench</p><div class="tool-fields"><label>Target evolution<select id="target">{targets}</select></label><label>Update set<select id="version"><option>All</option><option>Base</option><option>Regal</option><option>Shadow</option><option>Naturalist</option></select></label></div>
<fieldset><legend>Already carrying (optional; one entry per actual item)</legend><div class="owned-fields">{''.join(f'<label>Carried {i}<select class="owned">{opts}</select></label>' for i in range(1,6))}</div></fieldset>
<div class="tool-actions"><span id="route-selection">Choose a target</span><button type="button" class="button" id="view-route" disabled>View ingredient route</button><button type="button" id="clear-route">Clear selections</button></div><p id="route-status" role="status" aria-live="polite">Choose a target to plan a route.</p><p class="meta">Uses the first listed recipe, keeps duplicate ingredients and stops at carried items. This is not a save reader, drop simulator, capacity check or shortest-route optimizer.</p>
<dialog id="route-dialog" aria-labelledby="route-title"><button type="button" id="route-close" autofocus>Close route</button><h2 id="route-title">Ingredient route</h2><div id="route-output"></div></dialog><script type="application/json" id="recipe-data">{json.dumps(data,ensure_ascii=False).replace('<','\\u003c')}</script><noscript>JavaScript is optional: all recipes are listed in the table below.</noscript></div>'''
def matrix():
 stages=['BONExYARD','SNOWYxSHORES','LIMINALxDESERT','GORYxGRASSLANDS','FUNGALxFOREST','SMOLDERINGxDEPTHS','HEAVENLYxGATES','VASTxVOID']
 return '<div class="tool" data-checklist><p id="clear-progress" role="status" aria-live="polite">Manual clear record: loading saved ticks…</p><button type="button" id="reset-clears">Reset checklist</button><p class="meta">Saved on this device only. No game-save access. Reset clears only these ticks.</p>'+table(['Original roster']+stages,[[e(n)]+[f'<label class="tick"><input type="checkbox" data-clear="{i}-{j}" aria-label="{e(n)} — {s}"><span class="sr-only">{e(n)} — {s}</span></label>' for j,s in enumerate(stages)] for i,(n,_,_) in enumerate(CHARACTERS[:16])])+'</div>'
def article(x):
 tool=x['slug'] in ['evolutions','passive-evolutions','new-evolutions','trophy-guide']
 blocks=[]
 for ident,title,body in x['parts']:
  replacements={'@ball-tool':lambda:planner(BALLS,'Ball'),'@passive-tool':lambda:planner(ITEMS,'Passive'),'@new-tool':lambda:planner(BALLS,'Added ball',True),
   '@ball-table':lambda:recipe_table(BALLS),'@passive-table':lambda:recipe_table(ITEMS),'@new-ball-table':lambda:recipe_table([r for r in BALLS if r['version']!='Base']),
   '@new-passive-table':lambda:recipe_table([r for r in ITEMS if r['version']!='Base']),
   '@character-table':lambda:table(['Character','House / blueprint','Set'],[[e(n),e(h),v] for n,h,v in CHARACTERS])+'<p>House associations: [source:characters]. No fixed drop location is guaranteed by this table.</p>',
   '@trophy-tool':matrix}
  if body in replacements:body=replacements[body]()
  blocks.append(f'<section id="{ident}"><h2>{title}</h2>{body}</section>')
 toc='<aside class="toc" aria-label="On this page"><strong>On this page</strong>'+''.join(f'<a href="#{i}">{t}</a>' for i,t,_ in x['parts'])+'<a href="#sources">Sources</a></aside>'
 body=f'<header class="article-head" id="guide"><span class="tag">Ball x Pit · Source-based guide</span><h1>{e(x["h1"])}</h1><p class="answer">{x["answer"]}</p><p class="meta">Megabonk.org editors · Checked {'2026-11-21' if x['slug'] in BUMP else DATE} · Base game + free updates · No claimed gameplay test</p></header><div class="article-layout">{toc}<article class="prose">'
 slug_=x['slug'];body=citations(body+''.join(blocks),'21 November 2026' if slug_ in BUMP else '30 October 2026')
 return shell(P+x['slug']+'/',x['title'],x['desc'],body+'</article></div>',True,tool)
HOME_DATE='21 November 2026'
def home():
 """F9 专区首页：状态行 → 8 张任务卡 → 数据预览 + 最新更新 → 分组入口 → 简介 → FAQ。任务卡读 data/ball-x-pit-pages.json 的 card 排序。"""
 manifest=json.loads((ROOT/'data/ball-x-pit-pages.json').read_text(encoding='utf-8'))
 cards=sorted((x for x in manifest['pages'] if x.get('card')),key=lambda x:x['card'])
 names={'trophy-guide':'Trophy guide','builds':'Builds','new-evolutions':'New evolutions','evolutions':'Evolutions','ghostly-shield':'Ghostly Shield','passive-evolutions':'Passive evolutions','beginners-guide':"Beginner's guide",'character-tier-list':'Character tier list','characters':'Characters'}
 task_cards=''.join(f'<li class="task-card"><img src="/assets/ball-x-pit/images/{x["thumb"]}-480.webp" width="480" height="270" alt="" loading="lazy"><div class="body"><h3><a href="{P}{x["slug"]}/">{e(names[x["slug"]])}</a></h3><p>{e(x["blurb"])}</p></div></li>' for x in cards)
 balls={r['name']:r for r in BALLS}
 def recipe_row(name):
  r=balls[name];ing='<span class="plus">+</span>'.join(e(i) for i in r['inputs'])
  return f'<tr><th scope="row">{e(name)}</th><td>{ing}</td></tr>'
 recipes=''.join(recipe_row(n) for n in ['Bomb','Magma','Maggot','Nuclear Bomb'])
 hero=f'''<header class="hero" id="top"><div><span class="eyebrow">Unofficial guide notebook</span><h1>Ball x Pit Guide</h1><p class="subtitle">Evolutions, builds and unlocks</p><p class="lead">Find the missing ingredient for an evolution, pick a build that fits your roster, then drop back into the pit.</p><div class="actions"><a class="button" href="{P}evolutions/">Find an evolution →</a><a class="button secondary" href="{P}beginners-guide/">Start your first run</a></div><nav class="quick" aria-label="Most opened guides"><span>Most opened</span><a href="{P}trophy-guide/">Trophy guide</a><a href="{P}builds/">Builds</a><a href="{P}new-evolutions/">New evolutions</a><a href="{P}ghostly-shield/">Ghostly Shield</a></nav><ul class="status" aria-label="Game status"><li>Platforms<b>PC · Console · Mobile</b></li><li>Price<b>$14.99 on Steam</b></li><li>Latest free update<b>Naturalist</b></li><li>Expansion<b>Risen Ballbylon · $6.99</b></li><li>Checked<b>{HOME_DATE}</b></li><li class="unofficial">Status<b>Unofficial fan guide</b></li></ul></div><figure class="hero-art"><img src="/assets/ball-x-pit/images/ball-2-1280.webp" srcset="/assets/ball-x-pit/images/ball-2-800.webp 800w, /assets/ball-x-pit/images/ball-2-1280.webp 1280w" sizes="(max-width: 900px) calc(100vw - 32px), 560px" width="1280" height="720" alt="Ball x Pit combat: several balls in flight and the carried loadout at the left edge" fetchpriority="high"></figure></header>'''
 tasks=f'<section class="section" id="guides"><div class="section-head"><h2>Pick your task</h2><p>Every card opens a complete guide, ordered by what readers open most.</p></div><ul class="task-grid">{task_cards}</ul></section>'
 updates=[('21 Nov 2026','Risen Ballbylon expansion is on sale ($6.99 on Steam). The recipe tools here still cover the base game and free updates.',f'{P}new-evolutions/','See what the tools cover'),
  ('6 Aug 2026','Naturalist update: 11 new balls, 5 passives and two characters.',f'{P}new-evolutions/','Naturalist recipes'),
  ('27 Apr 2026','Shadow update: Tunneller, Tiptoer and the Guildhall.',f'{P}characters/','Character unlocks'),
  ('26 Jan 2026','Regal update: Endless Mode, Falconer and Carouser.',f'{P}character-tier-list/','Pick a character')]
 upd=''.join(f'<li><time>{d}</time><span>{e(t)} <a href="{u}">{e(l)} →</a></span></li>' for d,t,u,l in updates)
 duo=f'<section class="section" id="updates"><div class="duo"><div class="panel"><h2>Recipe check</h2><p>Four short routes from the evolution chart. The finder shows the rest.</p><table class="recipes"><tbody>{recipes}</tbody></table><a class="more" href="{P}evolutions/">Open the recipe finder →</a></div><div class="panel"><h2>What changed</h2><ul class="updates">{upd}</ul></div></div></section>'
 groups=[('Start with a workable run','Your first clear and first buildings.',[('beginners-guide',"Beginner's guide",'Short first recipe, town loop')]),
  ('Find the missing ingredient','Ball and passive recipes, free-update additions.',[('evolutions','Evolutions','Ball recipes and route finder'),('passive-evolutions','Passive evolutions','Item recipes and slot checks'),('new-evolutions','New evolutions','Regal, Shadow and Naturalist')]),
  ('Choose a build and character','Picks that fit what you have unlocked.',[('builds','Builds','Combos by progression'),('character-tier-list','Character tier list','Picks with conditions'),('characters','Characters','Houses, blueprints and materials')]),
  ('Turn discoveries into progress','Unlocks and the trophy route.',[('ghostly-shield','Ghostly Shield','Stone-ally requirement'),('trophy-guide','Trophy guide','Stage clears checklist')])]
 grp=''.join(f'<div class="hub-group"><h3>{t}</h3><p>{d}</p>'+''.join(f'<a class="row" href="{P}{s}/">{e(n)} <span>{e(w)}</span></a>' for s,n,w in rows)+'</div>' for t,d,rows in groups)
 allguides=f'<section class="section" id="all-guides"><div class="section-head"><h2>All guides by task</h2></div><div class="groups">{grp}</div></section>'
 about=f'<section class="section" id="platforms"><div class="about-game"><div><h2>About the game</h2><p>Ball x Pit mixes brick-breaking with a survival roguelite and a town you rebuild between runs. It is made by Kenny Sun and Friends and published by Devolver Digital. Steam lists Windows and macOS; the official site also lists Switch, Switch 2, Xbox, PlayStation, App Store and Google Play.</p><p>These guides cover the game itself, not an online ball-pit toy or a Megabonk mode. Prices and platform lists change, so check the store page for your region: {ext(SOURCES["official"][0],"Steam")} · {ext("https://ballxpit.com/","Official site")}.</p></div><div><h2>How we check</h2><p>Recipes come from attributed community charts and the official update notes, checked against each other. We have not benchmarked builds or played every route. Each guide shows its checked date.</p></div></div></section>'
 faq=[('Is Ball x Pit still getting free updates?','Steam lists the Naturalist update (6 Aug 2026) as the latest free update, after Regal and Shadow. Risen Ballbylon is a separate paid expansion. Our recipe tools cover the base game and the free updates, not the expansion yet.',f'{P}new-evolutions/','New evolutions'),
  ('How do I make an evolution?','Carry the listed ingredients, upgrade them fully, then choose Evolution at a fusion core. A fused ball with a generic name is not the named evolution.',f'{P}evolutions/','Evolution finder'),
  ('Which character should I start with?','The Warrior is the starting character, and a good one for learning pickups and the town loop. Later picks depend on what you have unlocked and who you pair them with.',f'{P}character-tier-list/','Character picks'),
  ('Is Ball x Pit on mobile and consoles?','Yes. Steam lists Windows and macOS, and the official site lists Switch, Switch 2, Xbox, PlayStation, App Store and Google Play. Save transfer between platforms is not promised here.',f'{P}beginners-guide/','Beginner\'s guide'),
  ('Looking for a key or the controls?','For a purchase key use the official store listing for your platform and check region and edition. For controls, follow your version\'s on-screen prompts and the beginner notes. This site does not sell keys or host a playable copy.',f'{P}beginners-guide/#controls','Controls notes'),
  ('How long is a run through the game?','Separate a first clear from full trophy completion and Endless play. Dayngls estimates 25–30 hours for the base-game trophy route; that is a route estimate, not a first-clear time.',f'{P}trophy-guide/','Trophy checklist'),
  ('Which game name am I looking for?','球比伦战记 is the Simplified Chinese name on Steam, and ボールピット appears in Japanese searches. The guides here are in English and use Burn, Freeze, Dark and Egg Sac consistently.',f'{P}evolutions/','Recipe names')]
 faq_html='<section class="section" id="faq"><div class="section-head"><h2>Common questions</h2></div><div class="faq">'+''.join(f'<details><summary>{e(q)}</summary><p>{e(a)} <a href="{u}">{e(l)} →</a></p></details>' for q,a,u,l in faq)+'</div></section>'
 body=hero+tasks+duo+allguides+about+faq_html
 return shell(P,'Ball x Pit Guides: Evolutions, Builds & Unlocks','Plan Ball x Pit evolutions, choose builds for your roster and check character unlocks. Independent guides, recipe tools and a base-game trophy checklist.',body,True,image=True)
FAQ_QUESTIONS=['Is Ball x Pit still getting free updates?','How do I make an evolution?','Which character should I start with?','Is Ball x Pit on mobile and consoles?','Looking for a key or the controls?','How long is a run through the game?','Which game name am I looking for?']
def build():
 result=[(P,home())]+[(P+x['slug']+'/',article(x)) for x in pages()]
 for s,title,body in [
 ('about/','About the Ball x Pit guides',paras('This is an unofficial guide section for players of Ball x Pit, written by the Megabonk.org editors. It is not made by Kenny Sun and Friends or Devolver Digital, and it is not game support.',
 'Sources: the Steam store page and update notes, the official site, and attributed community recipe charts and reports. Each guide lists the sources it relies on and the date we checked them. We have not benchmarked builds or played every route, and we say so where it matters.',
 'Checked against the Naturalist update (6 Aug 2026) and the Risen Ballbylon store listing on 21 Nov 2026. The recipe tools cover the base game and the free updates; Risen Ballbylon recipes are not included yet.',
 'Covered here: evolutions and passive evolutions, new recipes from the free updates, builds, the character tier list and unlocks, Ghostly Shield, the trophy checklist and a beginner guide. To suggest a correction, send the page URL and a public source through the <a href="/ball-x-pit/contact/">contact page</a>. Game names belong to their owners.')),
 ('contact/','Contact the Ball x Pit guide editors',paras('Found a wrong recipe, an outdated update note or a broken tool? Email <a href="mailto:contact@megabonk.org?subject=%5BMegabonk.org%5D%20Website%20feedback">contact@megabonk.org</a> with the page URL, your platform and game version, and a public source or a short description of what you saw.',
 'Useful reports: a recipe that does not match your game, a character unlock that is described incorrectly, a price or platform change on the store page. Please do not send passwords, purchase keys or game credentials.',
 'We cannot restore saves, issue refunds or give in-game items. For purchase or account problems, use the support link on the store where you bought the game. There is no promised reply time. '+ext(SOURCES['official'][0],'Steam · Ball x Pit store and support links')))]:
  result.append((P+s,shell(P+s,title+' | Ball x Pit','Who writes the unofficial Ball x Pit guides, which sources they use and how to report a correction.' if s=='about/' else 'How to report a wrong recipe, outdated note or broken tool in the Ball x Pit guides.',f'<article class="legal" id="guide"><p class="crumbs"><a href="{P}">Ball x Pit guide</a></p><h1>{title}</h1><p class="meta">Reviewed {HOME_DATE}</p>{body}<p><a href="{P}">Back to the Ball x Pit guide →</a></p></article>')))
 result.append((P+'404.html',shell(P+'404','Page not found | Ball x Pit Guides','This Ball x Pit guide page could not be found. Return to the guide index to find current recipe, build and unlock help.',f'<article class="legal"><h1>That route ends here.</h1><p>This guide page was not found.</p><a class="button" href="{P}">Back to the Ball x Pit guide</a></article>',error=True)))
 for route,html in result:
  f=ROOT/route.lstrip('/') if route.endswith('.html') else ROOT/route.lstrip('/')/'index.html'
  f.parent.mkdir(parents=True,exist_ok=True);write_html(f, decorate(route,html),encoding='utf-8')
 import subprocess,sys
 subprocess.run([sys.executable,str(Path(__file__).resolve().parent/'register_page.py'),str(ROOT),'ball-x-pit'],check=True)
 # register_page 追加面包屑后，让 SEO 编辑器再跑一遍，使 FAQ/面包屑顺序稳定（pre-push 的 render drift 检查）
 from game_seo import edit as edit_seo
 for route,_ in result:
  f=ROOT/route.lstrip('/') if route.endswith('.html') else ROOT/route.lstrip('/')/'index.html'
  t0=f.read_text(encoding='utf-8');t1=edit_seo(f,t0)
  if t1!=t0:f.write_text(t1,encoding='utf-8')
 # 404 不在页面清单里：同一套导航与页脚由清单直接生成
 sys.path.insert(0,str(Path(__file__).resolve().parent))
 import register_page as rp
 m=rp.load(ROOT,'ball-x-pit');f404=ROOT/'ball-x-pit/404.html';t=f404.read_text(encoding='utf-8')
 nav=rp.nav_html(m,'__404__')
 t=re.sub(r'(<nav class="(?:desktop-nav|mobile-links)"[^>]*>).*?(</nav>)',lambda x:x[1]+nav+x[2],t,flags=re.S)
 t=re.sub(r'<footer class="site-footer"[^>]*>.*?</footer>',lambda x:rp.footer_html(m),t,count=1,flags=re.S)
 write_html(f404,t,encoding='utf-8')
 print(f'Built {len(result)} Ball x Pit pages: 10 ordinary, 2 trust, 1 error; {len(BALLS)} ball outputs and {len(ITEMS)} passive outputs.')
if __name__=='__main__':build()
