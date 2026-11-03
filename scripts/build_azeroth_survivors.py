"""Build the original-game guide section from versioned editorial sources."""
from site_analytics import write_html
from pathlib import Path
from html import escape
import re,json
from guide_images import decorate
from azeroth_survivors_iteration import apply
from azeroth_survivors_expansion import update, new_pages
from azeroth_survivors_play import play_page
from azeroth_survivors_build_refinement import refine
from azeroth_survivors_tools import apply_tools,tool_assets,home_search
from azeroth_survivors_current import refresh
from azeroth_survivors_icons import decorate_icons
from azeroth_sync_pages import apply_sync,decorate_sync
from azeroth_survivors_keywords import apply_keywords
from azeroth_survivors_discovery import improve_pages, improve_home
from azeroth_survivors_planner import apply_planner, home_entry, planner_assets
from azeroth_planner_reference import write_reference
from azeroth_survivors_content import P,SOURCES,CLASSES,ref,a,ext,para,steps,table,articles,russian
ROOT=Path(__file__).resolve().parents[1]
BASE='https://megabonk.org'
ADS='<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8830315294299920" crossorigin="anonymous"></script>'
ASSET='/assets/azeroth-survivors/'
NAV=[('▶ Play',P+'play/'),('Start here',P+'beginners-guide/'),('Builds',P+'builds/'),('Guides',P+'#guides'),('Help',P+'#help')]
def sources(body,ru=False):
 keys=list(dict.fromkeys(re.findall(r'\{\{s:(\w+)\}\}',body)))
 details={k:SOURCES[k][2] for k in keys}
 # One source entry per destination; preserve both dated scopes when referenced.
 unique=[]
 for k in keys:
  old=next((x for x in unique if SOURCES[x][0]==SOURCES[k][0]),None)
  if old:
   body=body.replace(ref(k),ref(old));details[old]+=' '+SOURCES[k][2]
  else:unique.append(k)
 keys=unique
 for i,k in enumerate(keys,1):body=body.replace(ref(k),f'<sup class="ref"><a href="#source-{i}" aria-label="Source {i}">[{i}]</a></sup>')
 source='<section class="sources" id="sources"><h2>'+('Источники и ограничения' if ru else 'Sources & verification')+'</h2><ol>'
 source+=''.join(f'<li id="source-{i}">{ext(SOURCES[k][0],SOURCES[k][1])} — {details[k]}</li>' for i,k in enumerate(keys,1))
 source+='</ol><a class="back" href="#guide">'+('Вернуться к тексту ↑' if ru else 'Back to guide ↑')+'</a></section>'
 return body,source
def shell(path,title,desc,body,lang='en',ads=True,error=False,image=''):
 nav=''.join(f'<a href="{u}"'+(' class="nav-play"' if u==P+'play/' else '')+(' aria-current="page"' if path==u else '')+f'>{l}</a>' for l,u in NAV)
 return f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)}</title><meta name="description" content="{escape(desc,quote=True)}"><link rel="canonical" href="{BASE+path}">
{'<meta name="robots" content="noindex,follow">' if error else ''}{ADS if ads else ''}<link rel="icon" href="{ASSET}favicon.ico" sizes="any"><link rel="icon" type="image/svg+xml" href="{ASSET}logo.svg"><link rel="apple-touch-icon" href="{ASSET}apple-touch-icon.png">
<link rel="stylesheet" href="/assets/pokebonk/site.css"><link rel="stylesheet" href="/assets/guide-article-layout.css"><link rel="stylesheet" href="{ASSET}site.css">
<meta property="og:type" content="{'website' if path==P else 'article'}"><meta property="og:title" content="{escape(title,quote=True)}"><meta property="og:description" content="{escape(desc,quote=True)}"><meta property="og:url" content="{BASE+path}">{f'<meta property="og:image" content="{BASE+image}">' if image else ''}</head>
<body class="az guide-layout"><a class="skip" href="#main">Skip to content</a><header class="top"><div class="wrap"><a class="brand" href="{P}"><img src="{ASSET}logo.svg" width="42" height="42" alt=""><span>Azeroth Survivors<small>Megabonk.org · Independent guide</small></span></a><nav class="desktop-nav" aria-label="Main navigation">{nav}</nav><details class="mobile-nav"><summary>Menu</summary><nav class="mobile-links" aria-label="Mobile navigation">{nav}</nav></details></div></header>
<main class="wrap" id="main">{body}</main><footer class="footer"><div class="wrap footer-grid"><div><strong>A guide for your next run.</strong><p>Independent editorial by Megabonk.org. Azeroth Survivors is by Aethus. Not affiliated with Aethus or Blizzard Entertainment. Menu and source-text research is labelled; no gameplay benchmark is claimed.</p><a href="/">Megabonk Wiki →</a></div><nav aria-label="Site information"><a href="/about/">About</a><a href="/contact/">Contact</a><a href="/privacy-policy">Privacy</a></nav></div></footer></body></html>'''
def article(d):
 ru=d.get('lang')=='ru';parts=d['parts'];path=P+d['slug']
 content=para(d['answer'])+''.join(f'<section id="{id}"><h2>{title}</h2>{text}</section>' for id,title,text in parts)
 content,source=sources(content,ru)
 # Keep the short answer in the header, with citations resolved by the same source map.
 first,content=content.split('</p>',1)
 toc='<aside class="toc" aria-label="On this page"><strong>'+('На этой странице' if ru else 'On this page')+'</strong>'+''.join(f'<a href="#{i}">{t}</a>' for i,t,_ in parts)+'<a href="#sources">'+('Источники' if ru else 'Sources')+'</a></aside>'
 body=f'<nav class="crumbs" aria-label="Breadcrumb"><a href="{P}">Azeroth Survivors</a> / {d["h1"]}</nav><header class="article-head" id="guide"><span class="tag">Original game · Independent guide</span><h1>{d["h1"]}</h1><div class="answer">{first}</p></div><p class="meta">Megabonk.org editors · {d.get("review_note", "Reviewed 29 October 2026 · Original v0.127.0 · Source-based, not a playtest")}</p></header><div class="article-layout">{toc}<article class="prose">{content}{source}<section class="related"><h2>'+('Дальше' if ru else 'Choose your next step')+'</h2>'+''.join(a(s,l) for s,l in d['related'])+'</section></article></div>'
 return path,shell(path,d['title'],d['desc'],body,d.get('lang','en'))
def home():
 title='Azeroth Survivors Guide: Play, Builds & Save Help'
 desc='Find Aethus’s original Azeroth Survivors, choose a class build and protect your save. Independent guides to browser play, addons, DPS and mobile checks.'
 body=f'''<section class="atlas-hero" id="guide"><div><p class="eyebrow">The next run starts here</p><h1>Azeroth<br><em>Survivors.</em></h1><p class="lead">Choose your route.<br>Keep your progress.</p><p>Aethus’s free Warcraft-inspired horde-survival game: move through the crowd, let spells attack, and build around the upgrades you receive. This is an independent guide to the original game.{ref('game')}</p><div class="actions">{ext('https://wow.aethus.pl/','Play the original game')}<a class="button secondary" href="{P}beginners-guide/">Plan your first run →</a></div><p class="meta">Opens wow.aethus.pl in a new tab. The original blocks embedded play; your game and save stay on its host.{ref('launcher')}</p></div><figure class="atlas-art"><img src="{ASSET}route-atlas.svg" width="640" height="610" alt="Guide route diagram: pick a hero, draft a build and keep a save"><figcaption>Original guide illustration · not game footage</figcaption></figure></section>
<div class="statusbar"><div><small>Platform</small><strong>WebGPU browser</strong></div><div><small>Also available</small><strong>Windows download</strong></div><div><small>Source reviewed</small><strong>v0.127.0</strong></div><div><small>Checked</small><strong>29 Oct 2026</strong></div></div>
<section class="section" id="launch"><h2>Play at the source.</h2><p>The original opens in its own tab. Keep the guide here while you play; no embedded frame or substitute game is loaded.</p><div class="guide-index"><div><strong>Browser</strong><p>{ext('https://wow.aethus.pl/','Aethus · original game')} — requires WebGPU and a usable adapter. Allow its first game-data download to finish.</p></div><div><strong>Windows</strong><p>{ext('https://wow.aethus.pl/download/AzerothSurvivorsWindowsNew.rar','Aethus · Windows archive')} — the original page’s downloadable route. Keep your save copy before changing client.</p></div></div><p>{a('mobile/','Phone and tablet checks')} · {a('save-backup/','Export before switching')}{ref('launcher')}</p></section>
<section class="section" id="start"><div class="section-head"><div><p class="eyebrow">01 / Get your bearings</p><h2>Start with your next decision.</h2></div><p>First run, a developed character, or a move to another device: use the path that matches.</p></div><div class="grid"><article class="card"><span class="number">FIRST RUN</span><h3>Get into the original.</h3><p>Use the original host, read the movement and card controls, then separate run upgrades from permanent talents.</p>{a('beginners-guide/','Start here')}</article><article class="card"><span class="number">CHOOSE A HERO</span><h3>Pick for your progress.</h3><p>Warrior for a melee opening, Paladin for a defensive route, Hunter for range; check the talent conditions before copying an endpoint.</p>{a('best-class/','Choose a class')}</article><article class="card"><span class="number">KEEP YOUR SAVE</span><h3>Export before you move.</h3><p>Import replaces the destination’s progress. Keep both files before changing device, browser or client.</p>{a('save-backup/','Follow the backup order')}</article></div></section>
<section class="section" id="builds"><div class="section-head"><div><p class="eyebrow">02 / Choose your engine</p><h2>One class. Different routes.</h2></div><p>Start with the talent you have, then choose cards for its trigger.</p></div><p>{a('builds/','Compare all build decisions')} · <a href="{P}ru/builds/" lang="ru">Билды на русском →</a></p><div class="atlas-routes">'''
 for k,d in CLASSES.items():body+=f'<a href="{P}builds/{k}/"><strong>{d["name"]}</strong><span>{d["routes"][0][0]} / {d["routes"][1][0]}</span><span aria-hidden="true">→</span></a>'
 body+='</div></section><section class="section" id="help"><p class="eyebrow">03 / Before the next attempt</p><h2>Fix the question in front of you.</h2><div class="guide-index">'
 for slug,label,summary in [('addons/','Install addons','Browser ZIP and desktop folder paths are different.'),('damage-meter/','Read the damage meter','A recent DPS window and a run average answer different questions.'),('save-backup/','Move or recover a save','Export both sides, then check local backup options.'),('mobile/','Check phone access','Separate GPU support, input and storage from device-specific reports.')]:body+=f'<a href="{P+slug}">{label}<span>{summary}</span></a>'
 body+='</div></section><section class="section" id="guides"><h2>The guide index</h2>'+para('Start &amp; class choice: '+a('beginners-guide/','First-run guide')+' · '+a('best-class/','Best class for your goal')+'. Builds &amp; choices: '+a('builds/','Build routes')+' plus the eight named class routes above. Help: addons, meter, save and mobile guides in the section just above. All listed pages are part of this guide; community support stays on the original author’s channels.')+'</section>'
 body+='<section class="section" id="zh-start" lang="zh-Hans"><h2>艾泽拉斯幸存者：先找对原版</h2>'+para('原作者 Aethus 的入口是 wow.aethus.pl。原版禁止在其他网站内嵌；点击本站 Play original 会在新标签页打开原站。更换浏览器或设备前，先在 Options → Saves 导出存档；导入会替换目标端进度，不会合并。繁体名称「艾澤拉斯倖存者」也指向这款游戏。'+ref('launcher')+ref('saves'))+'</section>'
 body+='<section class="section" id="which-game"><h2>Which game did you mean?</h2>'+table(['Name you found','How to distinguish it'],[['Azeroth Survivors / WoW Survivors','The Aethus original at wow.aethus.pl. Use its current client text for these guides.'],['Community reconstruction','OutThisLife’s separate rebuild. Do not mix its map or ability values into original-game advice. '+ref('rebuild')],['WoW Forever','A separate Blizzard game; its name reservations do not apply here. '+ref('forever')],['Hordes of Azeroth / D2 Survivors','Separate survivors projects, not alternative names for this save or client. '+ref('hordes')+ref('d2')],['Aevoria Survivors','A different game which a third-party Azeroth-named page labels as its embedded offering. '+ref('aevoria')],['Pokémon Megabonk / PokeBonk','Charcher’s separate project. <a href="/pokebonk/#guide">Use the existing PokeBonk guide →</a>']])+'</section>'
 body+='<section class="section" id="community"><h2>The original community, when you need it</h2>'+para('Use '+ext('https://discord.gg/azerothsurvivors','Discord · linked by Aethus’s original launcher')+' for the author’s community. Recheck the original page if an invite changes. Public Reddit reports are player experiences, not official support or a compatibility guarantee. '+ref('launcher'))+'</section>'
 body+='<section class="section" id="progression"><h2>Choose your next task</h2><p>Current system checks: 30 October 2026. Earlier class-route version scopes remain explicit.</p>'
 groups=[('Play together and change device',[2,14]),('Build and character choices',[1,8,10]),('Progression and rewards',[3,4,5,6,7]),('Version checks',[9])]
 for label,ids in groups:
  body+='<h3>'+label+'</h3><div class="guide-index">'+''.join(f'<a href="{P+d["slug"]}">{d["title"].replace("Azeroth Survivors ","")}<span>{d["h1"]}</span></a>' for d in new_pages() if int(d['id'][-3:]) in ids)+'</div>'
 body+='</section>'
 body=body.replace('<div class="actions">','<div class="actions"><a class="button" href="'+P+'play/">Play in a game window →</a>',1)
 body=body.replace('The original opens in its own tab. Keep the guide here while you play; no embedded frame or substitute game is loaded.','Choose the <a href="'+P+'play/">third-party game window</a> for embedded play, or open the original in its own tab. These are separate providers; keep saves with the host that created them.')
 body=body.replace('点击本站 Play original 会在新标签页打开原站。','本页原版入口在新标签页打开原站；顶部 Play 为第三方内嵌版本，两者的版本和存档互通尚未核实。')
 body=body.replace('<tr><td>Community reconstruction</td>', '<tr><td>Arena of Champions</td><td>A separate online arena PvP game at '+'<a href="/arena-of-champions/">Arena of Champions · play &amp; entry checks →</a>'+'. Choose it for player-versus-player matches, not automatic-spell survival runs. These class builds and save files do not apply to it. '+ref('arena_champions')+'</td></tr><tr><td>Community reconstruction</td>',1)
 body=body.replace('<small>Source reviewed</small><strong>v0.127.0</strong>','<small>Latest text check</small><strong>v0.139.0</strong>').replace('<small>Checked</small><strong>29 Oct 2026</strong>','<small>Checked</small><strong>2 Nov 2026</strong>')
 body=body.replace('<section class="section" id="launch">', '<p class="meta">Selected v0.139 client strings checked 2 November; individual guides and screenshots retain their own version dates. '+a('patch-notes/#nov2','See the verified changes')+ref('nov2')+'</p><section class="section" id="launch">',1)
 body=body.replace('<section class="section" id="community"><h2>The original community, when you need it</h2>', '<section class="section" id="community"><h2>The original community, when you need it</h2>'+para(ext('https://www.reddit.com/r/WoWPrivateServers/comments/1x16xwn/azeroth_survivors_roguelike_wow_singleplayer_game/','Reddit · original-game discussion')+' — player discussion, not creator support. Check the host and build before following a download or workaround.'))
 body=body.replace('<section class="section" id="guides"><h2>The guide index</h2>', '<section class="section" id="guides"><h2>The guide index</h2>'+para(a('luck/','Luck: rarity and upgrade decisions')+' · '+a('download-platforms/#source-safety','Original website, GitHub and source checks')))
 body=body.replace('<section class="section" id="guides"><h2>The guide index</h2>', '<section class="section" id="guides"><h2>The guide index</h2>'+para(a('addons/#asbuilder','ASBuilder: plan and track a build')+' · '+a('damage-meter/#dot-crits','DoT critical hits: what the evidence establishes')))
 body=body.replace('<section class="section" id="zh-start"', '<section class="section" id="language-start"><h2>Play at the original source</h2><p lang="ru">Играть в оригинал: '+ext('https://wow.aethus.pl/','Aethus · wow.aethus.pl')+'. Нужны WebGPU и доступный графический адаптер. Перед сменой браузера экспортируйте прогресс через Options → Saves → Export Save: импорт заменяет сохранение на целевом устройстве. <a href="'+P+'ru/builds/" lang="ru">Билды на русском →</a></p><p lang="de">Im Original spielen: '+ext('https://wow.aethus.pl/','Aethus · wow.aethus.pl')+'. WebGPU und ein nutzbarer Grafikadapter sind erforderlich. Vor einem Browserwechsel unter Options → Saves → Export Save sichern: Ein Import ersetzt den Spielstand am Ziel. '+a('beginners-guide/','Steuerung und Einstieg (Englisch)')+'</p><p>These links open the original host; the top Play entry uses the separately labelled third-party provider. '+ref('launcher')+ref('saves')+'</p></section><section class="section" id="zh-start"',1)
 body=body.replace('<section class="section" id="which-game"><h2>Which game did you mean?</h2>', '<section class="section" id="which-game"><h2>Which game did you mean?</h2>'+para('Looking for the Warcraft-themed game with automatic spells? This guide covers Aethus’s Azeroth Survivors at '+ext('https://wow.aethus.pl/','Aethus · original browser game')+'. Descriptions such as “WoW roguelike”, “WoW Vampire Survivors” or “WoW Megabonk” can point to this style of game; they do not make it Blizzard’s World of Warcraft, Vampire Survivors or Megabonk itself. Choose the actual game and host before using a build or moving a save. '+ref('game')))
 body=body.replace('<tr><td>Hordes of Azeroth / D2 Survivors</td><td>Separate survivors projects, not alternative names for this save or client. '+ref('hordes')+ref('d2')+'</td></tr>', '<tr><td>Hordes of Azeroth</td><td>A separate survivors-style project. Its author describes 1.12.1 game files and a local server on your PC, rather than Aethus’s browser entry. These builds and save instructions are not a compatibility guide for it. '+ref('hordes_author')+'</td></tr><tr><td>D2 Survivors</td><td>A separate Diablo II survivors project, not an alternative name for the Aethus client. '+ref('d2')+'</td></tr>')
 body=body.replace('<tr><td>WoW Forever</td>', '<tr><td>AETHUS by Pawsmonaut Games</td><td>A separate sci-fi survival-crafting title. A search for “Aethus game” can mean this game rather than the creator of Azeroth Survivors. '+ref('aethus_other')+'</td></tr><tr><td>WanderLust: Azeroth Survival</td><td>A WoW addon with survival systems, not this browser survivors game. Check the author project before treating the shorter phrase “Azeroth Survival” as a spelling variant. '+ref('wanderlust')+'</td></tr><tr><td>WoW Forever</td>',1)
 body=body.replace('<section class="section" id="community">', '<section class="section" id="creator-credit"><h2>Who is Aethus? What does “zuzia miau miau” refer to?</h2>'+para('The original character-menu screenshot shown on this page credits “Made by Aethus (zuzia miau miau)” at the bottom left. This is the visible creator credit in the English v0.130.0 menu captured on 30 October 2026 and re-read on 2 November. It identifies the game credit; it does not establish a legal name, another account’s identity or a separate download site. '+ref('creator_capture'))+para('For the game itself, use '+ext('https://wow.aethus.pl/','Aethus · wow.aethus.pl')+'. Check the full spelling, including the <code>.pl</code> ending, when returning from a search result. The original WebGPU browser route and our separately labelled third-party Play window have different providers; keep your save with the host that created it. '+a('download-platforms/#source-safety','Check original and community sources')+ref('launcher'))+'</section><section class="section" id="community">',1)
 body=body.replace('<section class="section" id="creator-credit">', '<p id="forever-name-reservation">Looking for WoW Forever name reservation? That belongs to Blizzard’s separate game. Use '+ext('https://news.blizzard.com/en-us/article/24303866/claim-your-world-of-warcraft-forever-character-names','Blizzard · reservation instructions and eligibility')+' for the account requirements and regional schedule; the Aethus browser entry does not reserve those names. Checked 2 November 2026. '+ref('forever_names')+'</p><section class="section" id="creator-credit">',1)
 body,source=sources(body)
 return P,shell(P,title,desc,body+source,image=ASSET+'route-atlas.svg')
def trust():
 body=f'<article class="legal" id="guide"><h1>Page not found</h1><p>This guide address does not exist. Return to the <a href="{P}">Azeroth Survivors guide index</a> or <a href="{P}builds/">choose a class build</a>.</p></article>'
 return [(P+'404.html',shell(P+'404','Page not found | Azeroth Survivors Guides','Find the original-game guide index, class builds and help after a missing page.',body,ads=False,error=True))]

def build():
 write_reference()
 content=apply_planner(improve_pages(apply_sync(apply_keywords(refresh(apply_tools(refine(update(apply(articles()+[russian()])))))))))
 path,html=home()
 html=html.replace('A separate Diablo II survivors project, not an alternative name for the Aethus client.', 'A separate Diablo II survivors project, not an alternative name for the Aethus client. <a href="/d2-survivors/">D2 Survivors guides →</a> · <a href="/d2-survivors/play/">Play D2 Survivors →</a> · <a href="/d2-survivors/zh/localization/" lang="zh-Hant">繁體中文化與備份 →</a>')
 html=html.replace('<section class="section" id="start">',home_search(content)+'<section class="section" id="start">',1)
 pages=[(path,home_entry(improve_home(html)))]+[article(x) for x in content]+[play_page(shell,ext)]+trust()
 for path,text in pages:
  file=ROOT/path.lstrip('/') if path.endswith('.html') else ROOT/path.lstrip('/')/'index.html'
  file.parent.mkdir(parents=True,exist_ok=True);write_html(file, planner_assets(path,tool_assets(path,decorate_icons(path,decorate_sync(path,decorate(path,text))))),encoding='utf8')
 print(f'Built {len(pages)} Azeroth guide files; existing main-site trust pages reused, 1 noindex404. Click-loaded third-party Play; no copied client.')
if __name__=='__main__':build()
