"""Rebuild the independent Ball x Pit hub. No expectation configuration is generated."""
from pathlib import Path
from html import escape as e
import json,re
from ball_x_pit_data import SOURCES,BALLS,ITEMS,CHARACTERS
from ball_x_pit_content import pages,table,paras,items
ROOT=Path(__file__).resolve().parents[1]
P='/ball-x-pit/'
BASE='https://megabonk.org'
DATE='2026-10-30'
ADS='<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8830315294299920" crossorigin="anonymous"></script>'
NAV=[('Start here','beginners-guide/'),('Evolutions','evolutions/'),('Build choices','builds/'),('Guides','#guides')]
def slug(s):return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')
def ext(url,label):return f'<a href="{e(url,quote=True)}" target="_blank" rel="noopener noreferrer">{e(label)} ↗</a>'
def shell(path,title,desc,body,ordinary=False,tool=False,error=False,image=False):
 nav=''.join(f'<a href="{P+u}"'+(' aria-current="page"' if path==P+u else '')+'>'+l+'</a>' for l,u in NAV)
 return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc,quote=True)}"><link rel="canonical" href="{BASE+path}">
{ADS if ordinary else ''}{'<meta name="robots" content="noindex,follow">' if error else ''}
<link rel="icon" href="/favicon.ico"><link rel="stylesheet" href="/assets/pokebonk/site.css"><link rel="stylesheet" href="/assets/ball-x-pit/site.css"><link rel="stylesheet" href="/assets/guide-article-layout.css">
<meta property="og:type" content="{'website' if path==P else 'article'}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc,quote=True)}"><meta property="og:url" content="{BASE+path}">
{f'<meta property="og:image" content="{BASE}/assets/ball-x-pit/recipe-map.svg">' if image else ''}
{'<script defer src="/assets/ball-x-pit/tool.js"></script>' if tool else ''}</head><body class="bxp guide-layout"><a class="skip" href="#main">Skip to content</a>
<header class="top"><div class="wrap"><a class="brand" href="{P}"><img src="/assets/ball-x-pit/logo.svg" width="44" height="44" alt=""><span>BALL x PIT<small>Megabonk.org · Independent guides</small></span></a><nav class="desktop-nav" aria-label="Main navigation">{nav}</nav><details class="mobile-nav"><summary>Menu ☰</summary><nav class="mobile-links" aria-label="Mobile navigation">{nav}</nav></details></div></header>
<main class="wrap" id="main">{body}</main><footer class="footer"><div class="wrap footer-grid"><div><strong>Ball x Pit · Independent guide notebook</strong><p>Published by Megabonk.org editors. Not affiliated with Kenny Sun and Friends or Devolver Digital. Source-based guides; no claimed gameplay tests.</p><a href="/#wiki-start">More survival-game guides →</a></div><nav aria-label="Site information"><a href="{P}about/">About</a><a href="{P}contact/">Contact</a><a href="/privacy-policy#ball-x-pit-guides">Privacy</a></nav></div></footer></body></html>'''
def citations(body):
 used=[]
 def sub(m):
  key=m[1]
  if key not in used:used.append(key)
  n=used.index(key)+1
  return f'<sup class="ref"><a href="#source-{n}" aria-label="Source {n}">[{n}]</a></sup>'
 body=re.sub(r'\[source:([a-z]+)\]',sub,body)
 refs='<section class="sources" id="sources"><h2>Sources & evidence limits</h2><ol>'+''.join(f'<li id="source-{i}">{ext(SOURCES[k][0],SOURCES[k][1])} — {e(SOURCES[k][2])}.</li>' for i,k in enumerate(used,1))+'</ol><p>Checked 30 October 2026. Community reports can change with patches. We have not played these routes or benchmarked builds.</p><a href="#guide">Back to the answer ↑</a></section>'
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
 body=f'<nav class="crumbs" aria-label="Breadcrumb"><a href="{P}">Ball x Pit guides</a> / {e(x["h1"])}</nav><header class="article-head" id="guide"><span class="tag">Ball x Pit · Source-based guide</span><h1>{e(x["h1"])}</h1><p class="answer">{x["answer"]}</p><p class="meta">Megabonk.org editors · Checked {DATE} · Base game + free updates · No claimed gameplay test</p></header><div class="article-layout">{toc}<article class="prose">'
 body=citations(body+''.join(blocks))
 related='<section class="related"><h2>Next useful checks</h2>'+''.join(f'<a href="{P+s}/">{e(s.replace("-"," ").title())} →</a>' for s in x['related'])+'</section>'
 return shell(P+x['slug']+'/',x['title'],x['desc'],body+related+'</article></div>',True,tool)
def home():
 specs=pages()
 groups=[('start','Start with a workable run',['beginners-guide']),('recipes','Find the missing ingredient',['evolutions','passive-evolutions']),('choose','Choose a build and character',['builds','character-tier-list']),('progression','Turn discoveries into progress',['characters','ghostly-shield','trophy-guide']),('updates','Return for the new recipes',['new-evolutions'])]
 lookup={x['slug']:x for x in specs}
 hero=f'''<header class="hero" id="guide"><div><span class="eyebrow">Independent guide notebook / 01</span><h1>One more run.<br><em>A better plan.</em></h1><p class="lead">Ball x Pit is out now: a brick-breaking survival roguelite with ball evolutions and a town to rebuild. Find your recipe, choose for your roster, then head back into the pit.</p><div class="actions"><a class="button" href="{P}evolutions/">Find an evolution →</a><a class="button secondary" href="{P}beginners-guide/">Start your first run</a></div><p class="meta">Megabonk.org editors · Checked 30 October 2026<br>Unofficial · Base game + free updates</p></div><figure class="hero-art"><img src="/assets/ball-x-pit/recipe-map.svg" width="1000" height="760" alt="Original diagram: Burn and Iron evolve into Bomb, then Poison leads to Nuclear Bomb"><figcaption>Original recipe diagram, not a game screenshot. Documented ingredient route. [source:base]</figcaption></figure></header>'''
 hero+='<div class="statusbar"><div><small>Base game</small><strong>Released</strong></div><div><small>Latest free set</small><strong>Naturalist</strong></div><div><small>Tools</small><strong>Ingredient routes</strong></div><div><small>Next expansion</small><strong>12 Nov · planned</strong></div></div>'
 body=hero+'<section id="guides" class="section"><div class="section-head"><h2>Bring the right plan.</h2><p>Pick the task you are trying to finish. Every link below leads to a complete guide.</p></div>'
 for ident,title,slugs in groups:
  body+=f'<section id="{ident}" class="hub-group"><h3>{title}</h3><div class="hub-grid">'
  for s in slugs:
   x=lookup[s]
   summaries={'evolutions':'Choose a target and reveal its missing ingredient branches.','passive-evolutions':'Check item ingredients, capacity and the Evolution action.','builds':'Choose reported combos that fit your unlocked roster.','character-tier-list':'Compare picks by task, partner and control style.','beginners-guide':'Go from a short recipe to completed town construction.','ghostly-shield':'Meet the stone-ally requirement before hunting the offer.','new-evolutions':'Filter Regal, Shadow and Naturalist recipes.','characters':'Check the blueprint, materials and completed house.','trophy-guide':'Track original-roster stage clears and avoid repeat pairs.'}
   body+=f'<article class="card"><span class="number">{list(lookup).index(s)+1:02}</span><h4><a href="{P+s}/">{e(x["h1"])}</a></h4><p>{summaries[s]}</p><a href="{P+s}/">Open guide →</a></article>'
  body+='</div>'
  if ident=='updates':body+='<p>Regal, Shadow and Naturalist are available free updates. Risen Ballbylon is a separate paid expansion planned for 12 November 2026; its unreleased recipes are not included here. [source:news]</p>'
  body+='</section>'
 body+='</section>'
 body+='<section class="section overview" id="platforms"><h2>Same game. Check the platform.</h2>'+paras('The released game is developed by Kenny Sun and Friends and published by Devolver Digital. Steam lists Windows and macOS; the game is also on consoles and mobile. These guides cover Ball x Pit, not an online ball-pit toy or a Megabonk game mode. [source:official]',
 'Switch 2 Edition advertises improved resolution and frame rates; this is an official qualitative description, not our benchmark. Mobile is free to try with a purchase to unlock the full game. We do not promise cross-platform save transfer or identical performance. [source:switch][source:ios]')+f'<p>{ext(SOURCES["official"][0],"Steam · PC / Mac")} · {ext(SOURCES["ios"][0],"App Store · iOS")} · {ext(SOURCES["switch"][0],"Nintendo · Switch / Switch 2")} · {ext("https://www.playstation.com/en-us/games/ball-x-pit/","PlayStation · PS5")}</p></section>'
 body+='<section class="section overview" id="buy"><h2>Looking for a key or the controls?</h2>'+paras('For a purchase key, use the platform’s official listing above and check your region and edition before buying. If you meant keyboard or controller inputs, follow your version’s on-screen prompts and the '+f'<a href="{P}beginners-guide/#controls">beginner controls notes</a>. This site does not sell keys or host a playable browser copy.')+'</section>'
 body+='<section class="section overview" id="release-notes"><h2>Free updates and the forthcoming expansion</h2>'+paras('Regal, Shadow and Naturalist are released free updates. Risen Ballbylon is a paid expansion announced for 12 November 2026; the developer says its content is accessed after completing the base game. The ingredient tools here exclude its unreleased recipes. Check the official listing for your region’s date. [source:news]')+'</section>'
 body+='<section class="section overview" id="playtime"><h2>How long is a run through the game?</h2>'+paras('Separate a first clear from full trophy completion and continued Endless play. Dayngls estimates 25–30 hours for its base-game trophy route; that is a route estimate, not a guaranteed first-clear time. See the '+f'<a href="{P}trophy-guide/">trophy checklist</a> for the workload behind completion. [source:trophy]')+'</section>'
 body+='<section class="section overview" id="languages"><h2>Which game name am I looking for?</h2>'+paras('球比伦战记 is the Simplified Chinese game name used on Steam. ボールピット commonly appears in Japanese queries. These English guides use Burn, Freeze, Dark and Egg Sac consistently; community synonyms are explained beside the recipe tools. Language-specific guide pages are not currently offered here.')+'</section>'
 body+='<section class="section overview" id="community"><h2>Community reports, with their limits</h2>'+paras('Player questions and recipe reports help explain missing discoveries and build choices. They are attributed to their authors; exact post dates can be obscured by cached relative timestamps. No tier here claims a controlled performance test. '+ext('https://www.reddit.com/r/BALLxPIT/','Reddit · r/BALLxPIT')+' is a community forum, not our support desk.')+'</section>'
 # Citation source section remains inside the hub, with only one back link.
 body=citations(body)
 return shell(P,'Ball x Pit Guides: Evolutions, Builds & Unlocks','Plan Ball x Pit evolutions, choose builds for your roster and check character unlocks. Independent guides, recipe tools and a base-game trophy checklist.',body,True,image=True)
def build():
 result=[(P,home())]+[(P+x['slug']+'/',article(x)) for x in pages()]
 for s,title,body in [
 ('about/','About the Ball x Pit guides',paras('Megabonk.org editors publish this independent guide section for players of Ball x Pit. We are not Kenny Sun and Friends, Devolver Digital or game support. We use official descriptions and attributed community reports; we do not claim to have played or benchmarked the routes.',
 'Recipe tools follow documented ingredient graphs, keeping alternative recipes visible and distinguishing conflicts from verified instructions. Build choices are editorial advice based on published mechanics and player preferences, not a combined performance score.',
 'Each guide records its checked date, source authors and relevant limitations. To suggest a correction, send the URL and an accessible source via our Contact page. Game names belong to their owners.')),
 ('contact/','Contact the guide editors',paras('For a correction to a Ball x Pit guide, email <a href="mailto:qsyhxw@gmail.com?subject=%5BMegabonk.org%5D%20Website%20feedback">qsyhxw@gmail.com</a>. Include the page URL, your platform, game version and a public source or a description of the issue. Do not send passwords, purchase keys or game credentials.',
 'We cannot restore saves, issue refunds or credit in-game items. For purchase/account problems, use the support link provided by the store you purchased from. There is no promised reply time. '+ext(SOURCES['official'][0],'Steam · Ball x Pit store and support links')))]:
  result.append((P+s,shell(P+s,title+' | Ball x Pit','Publisher, source-review method and contact information for the independent Ball x Pit guides on Megabonk.org.',f'<article class="legal" id="guide"><p class="crumbs"><a href="{P}">Ball x Pit guides</a></p><h1>{title}</h1><p class="meta">Reviewed {DATE}</p>{body}<p><a href="{P}about/">About</a> · <a href="{P}contact/">Contact</a></p></article>')))
 result.append((P+'404.html',shell(P+'404','Page not found | Ball x Pit Guides','This Ball x Pit guide page could not be found. Return to the guide index to find current recipe, build and unlock help.',f'<article class="legal"><h1>That route ends here.</h1><p>This guide page was not found.</p><a class="button" href="{P}">Back to Ball x Pit guides</a></article>',error=True)))
 for route,html in result:
  f=ROOT/route.lstrip('/') if route.endswith('.html') else ROOT/route.lstrip('/')/'index.html'
  f.parent.mkdir(parents=True,exist_ok=True);f.write_text(html,encoding='utf-8')
 print(f'Built {len(result)} Ball x Pit pages: 10 ordinary, 2 trust, 1 error; {len(BALLS)} ball outputs and {len(ITEMS)} passive outputs.')
if __name__=='__main__':build()
