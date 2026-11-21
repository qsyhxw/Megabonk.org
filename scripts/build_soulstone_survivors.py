"""Rebuild the source-based Soulstone Survivors section without editing old metadata."""
from site_analytics import write_html
from pathlib import Path
from html import escape
import json,re
from soulstone_survivors_content import P,PAGES,S,para,table
from soulstone_pages_data import CARD_NAMES,HOME_DATE,CHECKED,UPDATES,GROUPS,FAQ,FAQ_QUESTIONS
ROOT=Path(__file__).resolve().parents[1];BASE='https://megabonk.org';A='/assets/soulstone-survivors/'
AD='<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8830315294299920" crossorigin="anonymous"></script>'
NAV=[('Start here',P+'beginners-guide/'),('Builds',P+'builds/'),('Co-op & mods',P+'co-op/'),('Winter sigils',P+'bumble-crystal-order/'),('More games','/#more-games')]  # 占位，register_page.py 按清单覆盖
FORMATS={k:'other' for k in ['builds/','builds/barbarian/','beginners-guide/','co-op/','mods/','bumble-crystal-order/','ru/builds/']}
def ext(u,label):return f'<a href="{escape(u,quote=True)}" target="_blank" rel="noopener noreferrer">{escape(label)} ↗<span class="sr-only"> (opens in a new tab)</span></a>'
MEDIA=json.loads((ROOT/'data/soulstone-media.json').read_text(encoding='utf8'))
def figure(key,ref=1,ru=False):
 m=MEDIA[key];stem=m['stem'];sizes=m['sizes'];w=max(sizes);h=round(m['height']*w/m['width']);caption=m['caption'];alt=m['alt']
 if ru:caption='Официальный скриншот © Game Smithing Limited. Выбор навыков; интерфейс на английском. Версия снимка не указана, проверено 2 ноября 2026. Это не тест билда.'
 return f'<figure class="game-image" data-game-image="ss-{key}"><a href="{stem}-{w}.webp" target="_blank" rel="noopener" aria-label="Open full image"><img src="{stem}-{min(sizes)}.webp" srcset="'+', '.join(f'{stem}-{n}.webp {n}w'for n in sizes)+f'" sizes="(max-width:800px) calc(100vw - 40px), 900px" width="{w}" height="{h}" alt="{escape(alt,quote=True)}" loading="eager"></a><figcaption>{caption} <a href="#source-{ref}" aria-label="Image source">[{ref}]</a> <a class="image-zoom" href="{stem}-{w}.webp" target="_blank" rel="noopener">'+('Открыть изображение ↗'if ru else'Open full image ↗')+'</a></figcaption></figure>'
def shell(route,title,desc,body,image=None,lang='en',error=False,ordinary=True):
 """全站外壳：theme.css 全部页面，hub.css 仅首页；导航/页脚由 register_page.py 按页面清单覆盖。"""
 nav=''.join(f'<a href="{u}"'+(' aria-current="page"'if u==route else'')+f'>{t}</a>'for t,u in NAV)
 hub=route==P
 alts=''
 if route in [P+'builds/',P+'ru/builds/']:alts=f'<link rel="alternate" hreflang="en" href="{BASE+P}builds/"><link rel="alternate" hreflang="ru" href="{BASE+P}ru/builds/">'
 og=f'<meta property="og:image" content="{BASE+MEDIA[image]["stem"]}-{max(MEDIA[image]["sizes"])}.webp">'if image else''
 fmt=FORMATS.get(route[len(P):]) if route.startswith(P) else None
 if hub:fmt='hub'
 fmt=f' data-format="{fmt}"' if (fmt and ordinary and not error) else ''
 return f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)}</title><meta name="description" content="{escape(desc,quote=True)}"><link rel="canonical" href="{BASE+route}">{alts}{'<meta name="robots" content="noindex,follow">'if error else (AD if ordinary else '')}<meta property="og:type" content="{'website' if hub else 'article'}"><meta property="og:title" content="{escape(title,quote=True)}"><meta property="og:description" content="{escape(desc,quote=True)}"><meta property="og:url" content="{BASE+route}">{og}<link rel="icon" href="{A}favicon.ico"><link rel="apple-touch-icon" href="{A}apple-touch-icon.png"><link rel="stylesheet" href="/assets/guide-article-layout.css"><link rel="stylesheet" href="{A}theme.css">{f'<link rel="stylesheet" href="{A}hub.css">' if hub else ''}</head><body class="ss-theme guide-layout {'ss-hub' if hub else 'ss-guide'}"{fmt}><a class="skip" href="#main">Skip to content</a><header class="top"><div class="wrap"><a class="brand" href="{P}"><img src="{A}logo.svg" alt="" width="44" height="44"><span>Soulstone Survivors<small>Builds · Co-op · Progress</small></span></a><nav class="desktop-nav" aria-label="Main navigation">{nav}</nav><details class="mobile-nav"><summary>Menu ☰</summary><nav class="mobile-links" aria-label="Mobile navigation">{nav}</nav></details></div></header><main class="wrap" id="main">{body}</main><footer class="site-footer"></footer></body></html>'''
def article(p):
 sources=list(p['sources']);image_source='online'if p['image']=='coop'else'official'
 if image_source not in sources:sources.append(image_source)
 def refs(text):
  return re.sub(r'\{\{(\w+)\}\}',lambda m:f'<sup class="ref"><a href="#source-{sources.index(m[1])+1}" aria-label="Source {sources.index(m[1])+1}">[{sources.index(m[1])+1}]</a></sup>',text)
 ru=p.get('lang')=='ru';toc='<aside class="toc" aria-label="On this page"><strong>'+('На этой странице'if ru else'On this page')+'</strong>'+''.join(f'<a href="#{s[0]}">{s[1]}</a>'for s in p['sections'])+'<a href="#sources">'+('Источники'if ru else'Sources')+'</a></aside>'
 body=f'<header class="article-head" id="guide"><span class="tag">Soulstone Survivors guide</span><h1>{p["h1"]}</h1><div class="answer"><p>{p["answer"]}</p></div><p class="meta">'+('Редакция Megabonk.org · Проверено 2 ноября 2026'if ru else'Megabonk.org editors · Checked 2 November 2026')+'</p></header><div class="article-layout">'+toc+'<article class="prose">'
 for i,s in enumerate(p['sections']):
  body+=f'<section id="{s[0]}"><h2>{s[1]}</h2>'+refs(''.join(s[2:]))+'</section>'
  if i==0:body+=figure(p['image'],sources.index(image_source)+1,ru)
 body+='<section class="sources" id="sources"><h2>'+('Источники и ограничения'if ru else'Sources & verification')+'</h2><ol>'+''.join(f'<li id="source-{i}">{ext(S[k][0],S[k][1])} — {escape(S[k][2])}</li>'for i,k in enumerate(sources,1))+'</ol><p><a href="#guide">'+('К началу ↑'if ru else'Back to guide ↑')+'</a></p></section>'
 if p['slug']=='ru/builds':body+=f'<p class="lang-switch"><a href="{P}builds/" lang="en">English build guide →</a> · <a href="{P}" lang="en">Soulstone Survivors guide home →</a></p>'
 return shell(P+p['slug']+'/',p['title'],p['desc'],body+'</section></article></div>',p['image'],p.get('lang','en'))
def home():
 """F9 专区首页：状态行 → 任务卡 → 数据预览 + 最新更新 → 分组入口 → 简介 → FAQ。任务卡读 data/soulstone-survivors-pages.json 的 card 排序。"""
 manifest=json.loads((ROOT/'data/soulstone-survivors-pages.json').read_text(encoding='utf8'))
 cards=sorted((x for x in manifest['pages'] if x.get('card')),key=lambda x:x['card'])
 task_cards=''.join(f'<li class="task-card"><img src="{A}images/{x["thumb"]}-480.webp" width="480" height="270" alt="" loading="lazy"><div class="body"><h3><a href="{P}{x["slug"]}/"'+(' lang="ru"'if x['slug'].startswith('ru/')else'')+f'>{escape(CARD_NAMES[x["slug"]])}</a></h3><p'+(' lang="ru"'if x['slug'].startswith('ru/')else'')+f'>{escape(x["blurb"])}</p></div></li>' for x in cards)
 plus='<span class="plus">+</span>'
 preview_rows=[('Bleed route',f'<a href="{P}builds/barbarian/">Bladestorm {plus} Flurry {plus} Bloody Saw {plus} Heavy Strike</a>'),('2025 weapon answer',f'<a href="{P}builds/barbarian/#weapon">Battle Shout {plus} Beacon of Light {plus} Scent of Blood</a>'),('Winter circles',f'<a href="{P}bumble-crystal-order/">Red → Blue → Yellow → Green → Purple</a>')]
 recipes=''.join(f'<tr><th scope="row">{h}</th><td>{d}</td></tr>' for h,d in preview_rows)
 hero=f'''<header class="hero" id="guide"><div><span class="eyebrow">Unofficial player guide</span><h1>Soulstone Survivors Guide</h1><p class="subtitle">Builds, co-op mods and progression</p><p class="lead">Pick a skill-chain plan, set up a fan co-op mod that matches your game version, and know what to spend before the next run.</p><div class="actions"><a class="button" href="{P}builds/">Plan a build →</a><a class="button secondary" href="{P}beginners-guide/">Start your first run</a></div><nav class="quick" aria-label="Most opened guides"><span>Most opened</span><a href="{P}builds/">Builds</a><a href="{P}beginners-guide/">Beginner guide</a><a href="{P}builds/barbarian/">Barbarian build</a><a href="{P}co-op/">Co-op</a></nav><ul class="status" aria-label="Game status"><li>Platforms<b>Windows · macOS · Linux</b></li><li>Players<b>Single-player base game</b></li><li>Release<b>1.0 · 17 Jun 2025</b></li><li>Checked<b>{CHECKED}</b></li><li class="unofficial">Status<b>Unofficial fan guide</b></li></ul></div><div class="hero-visual">'''+figure('combat',2)+'</div></header>'
 tasks=f'<section class="section" id="guides"><div class="section-head"><h2>Pick your task</h2><p>Every card opens a full guide, ordered by what readers open most.</p></div><ul class="task-grid">{task_cards}</ul></section>'
 upd=''.join(f'<li><time>{d}</time><span>{escape(x)} <a href="{P}{u}">{escape(l)} →</a></span></li>' for d,x,u,l in UPDATES)
 duo=f'<section class="section" id="updates"><div class="duo"><div class="panel"><h2>Reported routes at a glance</h2><p>Three answers from the guides. Each page shows the source, date and limits.</p><table class="recipes"><tbody>{recipes}</tbody></table><a class="more" href="{P}builds/">Open the build checklist →</a></div><div class="panel"><h2>Latest checks</h2><ul class="updates">{upd}</ul></div></div></section>'
 grp=''.join(f'<div class="hub-group"><h3>{t}</h3><p>{d}</p>'+''.join(f'<a class="row" href="{P}{s}/"'+(' lang="ru"'if s.startswith('ru/')else'')+f'>{escape(n)} <span>{escape(w)}</span></a>' for s,n,w in rows)+'</div>' for t,d,rows in GROUPS)
 allguides=f'<section class="section" id="all-guides"><div class="section-head"><h2>All guides by task</h2></div><div class="groups">{grp}</div></section>'
 about=f'<section class="section" id="platforms"><div class="about-game"><div><h2>About the game</h2><p>Soulstone Survivors is a 3D horde-survival action roguelite by Game Smithing Limited. Steam App 2066020 left Early Access on 17 June 2025 (Early Access began 7 November 2022) and lists Windows, macOS and Linux. The official site also links PS5 and Xbox Series versions; the links we checked do not list Nintendo Switch.</p><p>Mod instructions here apply to their documented Windows versions. Official pages: '+ext(S['store'][0],'Steam')+' · '+ext(S['official'][0],'Official site')+'.</p></div><div><h2>How we check</h2><p>Each guide names its sources, the date we read them and what a source does not show. Community builds are reports, not our tests, and we do not claim a tested all-character tier list.</p></div></div></section>'
 faq_html='<section class="section" id="faq"><div class="section-head"><h2>Common questions</h2></div><div class="faq">'+''.join(f'<details><summary>{escape(q)}</summary><p>{escape(a)} <a href="{P}{u}"'+(' lang="ru"'if u.startswith('ru/')else'')+f'>{escape(l)} →</a></p></details>' for q,a,u,l in FAQ)+'</div></section>'
 srcs='<section class="sources" id="sources"><h2>Sources & verification</h2><ol><li id="source-1">'+ext(S['store'][0],S['store'][1])+' — product checked 2 November 2026.</li><li id="source-2">'+ext(S['official'][0],S['official'][1])+' — official media and platform links; capture build unknown.</li></ol><p><a href="#guide">Back to top ↑</a></p></section>'
 body=hero+tasks+duo+allguides+about+faq_html+srcs
 return shell(P,'Soulstone Survivors Guides: Builds, Co-op & Progress','Choose a Soulstone Survivors guide for builds, Barbarian routes, progression, co-op mods and the Bumble crystal order. Independent, source-based help.',body,'combat')
def xl(u,label):return f'<a href="{escape(u,quote=True)}" target="_blank" rel="noopener noreferrer">{escape(label)} ↗</a>'
def trust(slug,title,desc,paras_):
 return shell(P+slug+'/',title+' | Soulstone Survivors',desc,f'<article class="legal" id="guide"><p class="crumbs"><a href="{P}">Soulstone Survivors guide</a></p><h1>{title}</h1><p class="meta">Reviewed {HOME_DATE}</p>{paras_}<p><a href="{P}">Back to the Soulstone Survivors guide →</a></p></article>',ordinary=False)
def build():
 for p in PAGES:
  f=ROOT/(P+p['slug']).lstrip('/')/'index.html';f.parent.mkdir(parents=True,exist_ok=True);write_html(f, article(p),encoding='utf8')
 write_html(ROOT/P.lstrip('/')/'index.html', home(),encoding='utf8')
 contact_mail='<a href="mailto:contact@megabonk.org?subject=%5BMegabonk.org%5D%20Website%20feedback">contact@megabonk.org</a>'
 (ROOT/P.lstrip('/')/'about').mkdir(exist_ok=True)
 write_html(ROOT/P.lstrip('/')/'about'/'index.html', trust('about','About the Soulstone Survivors guides','Who writes the unofficial Soulstone Survivors guides, which sources they use and how to report a correction.',para('This is an unofficial guide section for players of Soulstone Survivors, written by the Megabonk.org editors. It is not made by Game Smithing Limited and it is not game support.')+para('Sources: the Steam store page and the official game website for product facts and platforms; the READMEs of the online and local co-op mods for installation and version limits; and dated community reports for builds and the winter event. Each guide lists the sources it relies on, the date we read them and what they do not show. We have not installed the mods or played these builds ourselves, and we say so where it matters.')+para('Checked on 2 November 2026 against Steam App 2066020 (released from Early Access on 17 June 2025). The co-op READMEs target game 1.5.3.2 (online) and 1.5d2 (local); a newer game version may need a newer mod release.')+para('Covered here: the beginner progression loop, skill-chain builds, a Barbarian route comparison and a Russian build page, online and same-PC co-op, mod loaders and the Bumble winter crystal order. To suggest a correction, send the page URL and a public source through the <a href="/soulstone-survivors/contact/">contact page</a>. Players also discuss the game on '+xl('https://www.reddit.com/r/SoulstoneSurvivors/','Reddit · r/SoulstoneSurvivors')+' and keep reference tables on the '+xl('https://soulstone-survivors.fandom.com/wiki/Soulstone_Survivors_Wiki','Fandom wiki')+'; community data can lag behind a patch. Game names and artwork belong to their owners.')),encoding='utf8')
 (ROOT/P.lstrip('/')/'contact').mkdir(exist_ok=True)
 write_html(ROOT/P.lstrip('/')/'contact'/'index.html', trust('contact','Contact the Soulstone Survivors guide editors','How to report an outdated mod version, wrong skill name or broken link in the Soulstone Survivors guides.',para(f'Found an outdated mod version, a wrong skill or rune name, or a dead link? Email {contact_mail} with the page URL, your game version and loader, and a public source or a short description of what you saw.')+para('Useful reports: a co-op mod release that no longer matches the game version, a skill chain that behaves differently in your build, a circle or portal step in the Bumble guide that failed. Please do not send passwords, purchase keys or save files.')+para('We cannot restore saves, fix a mod install or give in-game items. For purchase or account problems use the support link on the store where you bought the game; for a mod bug, use that mod author’s issue tracker. There is no promised reply time. '+xl(S['store'][0],'Steam · Soulstone Survivors store and support links'))),encoding='utf8')
 write_html(ROOT/P.lstrip('/')/'404.html', shell(P+'404','Page not found | Soulstone Survivors Guides','Find an independent Soulstone Survivors task guide.',f'<article class="legal"><h1>That route ends here.</h1><p>This guide page was not found.</p><a class="button" href="{P}">Back to the Soulstone Survivors guide</a></article>',error=True,ordinary=False),encoding='utf8')
 # Only idempotent body additions to existing publisher/root pages.
 f=ROOT/'index.html';t=f.read_text(encoding='utf8');marker='<div class="route-grid">'
 if 'id="soulstone-guide-entry"'not in t:
  assert marker in t;t=t.replace(marker,marker+f'<a class="route-card" id="soulstone-guide-entry" href="{P}"><span class="route-icon" aria-hidden="true">◇</span><h3>Soulstone Survivors guides</h3><p>Choose a skill-chain build, compare co-op mods and follow the winter crystal order.</p><span class="route-link">Open the independent field guide →</span></a>',1);write_html(f, t,encoding='utf8')
 f=ROOT/'privacy-policy.html';t=f.read_text(encoding='utf8')
 if 'id="soulstone-survivors-guides"'not in t:
  t=t.replace('</body>','<h2 id="soulstone-survivors-guides">Soulstone Survivors guides</h2><p>Reviewed 2 November 2026. Ordinary pages in /soulstone-survivors/ use this domain’s existing Google AdSense loader. They add no analytics tag, account form, save uploader, video embed or browser storage. External mod downloads and community links open their providers’ websites; we do not host or run their plugins. Cloudflare may add performance measurement on pages and error responses as described above. Gmail handles mail sent to our contact address.</p></body>');write_html(f, t,encoding='utf8')
 import subprocess,sys
 subprocess.run([sys.executable,str(Path(__file__).resolve().parent/'register_page.py'),str(ROOT),'soulstone-survivors'],check=True)
 # register_page 追加面包屑后让 SEO 编辑器再跑一遍，使 FAQ/面包屑顺序稳定（pre-push 的 render drift 检查）
 from game_seo import edit as edit_seo
 files=[ROOT/(P+p['slug']).lstrip('/')/'index.html' for p in PAGES]+[ROOT/P.lstrip('/')/'index.html',ROOT/P.lstrip('/')/'about'/'index.html',ROOT/P.lstrip('/')/'contact'/'index.html']
 for f in files:
  t0=f.read_text(encoding='utf8');t1=edit_seo(f,t0)
  if t1!=t0:f.write_text(t1,encoding='utf8')
 # 404 不在页面清单里：同一套导航与页脚由清单直接生成
 sys.path.insert(0,str(Path(__file__).resolve().parent))
 import register_page as rp
 m=rp.load(ROOT,'soulstone-survivors');f404=ROOT/P.lstrip('/')/'404.html';t=f404.read_text(encoding='utf8')
 nav=rp.nav_html(m,'__404__')
 t=re.sub(r'(<nav class="(?:desktop-nav|mobile-links)"[^>]*>).*?(</nav>)',lambda x:x[1]+nav+x[2],t,flags=re.S)
 t=re.sub(r'<footer class="site-footer"[^>]*>.*?</footer>',lambda x:rp.footer_html(m),t,count=1,flags=re.S)
 write_html(f404,t,encoding='utf8')
 print('Built 7 ordinary pages + home, 2 trust pages and scoped 404; footer/nav from data/soulstone-survivors-pages.json.')
if __name__=='__main__':build()
