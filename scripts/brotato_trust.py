"""Brotato 专区 About / Contact（SOP v3.25，02 §5.1）。

在 build_brotato.py 中先于 register_page.py 运行，导航与页脚由后者填充。信任页不放广告。
事实全部来自本专区已有页面引用的官方与社区来源，不新增游戏信息。Privacy 保持站级页（#brotato-guides）。"""
import json
from html import escape
from pathlib import Path

from site_analytics import write_html

ROOT = Path(__file__).resolve().parents[1]
P = '/brotato/'
CHECKED = '18 November 2026'
STEAM = 'https://store.steampowered.com/app/1942280/Brotato/'
DLC = 'https://store.steampowered.com/app/4498220/Brotato_Primal_Dread/'
NEWS = 'https://steamcommunity.com/app/1942280/announcements/?l=english'
PRESS = 'https://app.pressengine.net/newsdesk/futurefriendsgames'
WIKI = 'https://brotato.wiki.spellsandguns.com/Brotato_Wiki'
BUGS = 'https://steamcommunity.com/app/1942280/discussions/1/'


def email():
    return json.loads((ROOT / 'config/site-contact.json').read_text(encoding='utf8'))['email']


def ext(url, label):
    return f'<a href="{escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">{label} ↗<span class="sr-only"> external link, new tab</span></a>'


def about():
    return f'''<article class="legal"><header class="article-head" id="guide"><p class="eyebrow">Brotato · About</p><h1>About the Brotato guides</h1>
<p class="byline">Megabonk.org editors · Facts reviewed {CHECKED}</p></header>
<section id="who"><h2>Who runs this section</h2><p>This is an unofficial fan guide published by the editors of Megabonk.org, an independent site for survivors-style games. We are not Blobfish, who makes Brotato, or Evil Empire, who publishes it, and the guides are not endorsed by either company or by any platform that sells the game.</p></section>
<section id="covers"><h2>What it covers</h2><p>The <a href="{P}#setup">Primal Dread setup check</a>, <a href="{P}evolution/">Evolution choices</a>, the <a href="{P}caveman/">Caveman</a> and <a href="{P}veteran/">Veteran</a> character routes, <a href="{P}co-op/">co-op setup</a>, <a href="{P}mods/">mod compatibility</a>, the <a href="{P}updates/">update and branch guide</a> and a <a href="{P}vs-vampire-survivors/">comparison with Vampire Survivors</a>. Each page answers one job a player has before or during a run.</p></section>
<section id="sources"><h2>Where the answers come from</h2><ul>
<li><strong>The developer and publisher:</strong> the {ext(NEWS, 'Steam announcements')} supply patch notes, beta instructions and the Evolution demonstration; the {ext(PRESS, 'publisher press briefing')} gives the console and mobile window.</li>
<li><strong>Steam store pages:</strong> the {ext(STEAM, 'base game listing')} and the Primal Dread listing supply platforms, co-op modes and the base-game requirement.</li>
<li><strong>Player reports:</strong> the Caveman and Veteran routes rest on named launch-week community posts, and each page says so beside the claim.</li>
<li><strong>Screenshots:</strong> images are official Steam screenshots or frames from the developer's announcements, labelled where they appear. They illustrate a task and do not come from our own runs.</li></ul></section>
<section id="updates"><h2>How pages stay current</h2><p>Every guide shows the date it was checked; the section as a whole was last reviewed on {CHECKED}. When Blobfish posts a balance patch, hotfix or beta, the pages that depend on its numbers are rechecked first, and beta-only values are kept apart from the default branch.</p></section>
<section id="corrections"><h2>Send a correction</h2><p>Send the page URL, your platform, the game version and branch, and what you saw through the <a href="{P}contact/">contact page</a>. A screenshot of the tooltip or patch note helps us confirm the fix.</p></section></article>'''


def contact():
    mail = email()
    return f'''<article class="legal"><header class="article-head" id="guide"><p class="eyebrow">Brotato · Contact</p><h1>Contact the Brotato guide editors</h1>
<p class="byline">Reviewed {CHECKED}</p></header>
<section id="write"><h2>Email</h2><p>Write to <a href="mailto:{mail}?subject=%5BBrotato%5D%20Guide%20feedback">{mail}</a>. Useful reports for this section:</p><ul>
<li>A balance number, character change or Evolution rule that differs from a newer patch note;</li>
<li>A Primal Dread platform, price or release window that no longer matches the store;</li>
<li>A co-op or Remote Play step that works differently on your setup;</li>
<li>A wrong screenshot, link or character name on a Brotato page.</li></ul>
<p>Include the page URL, your platform, the game version and branch, and what happened.</p></section>
<section id="cannot"><h2>What we cannot help with</h2><p>We are not the developer or the game's support team, so we cannot restore a save, fix a store purchase or change how the game works. Use the {ext(BUGS, 'developer-linked bug forum')} for reproducible game bugs, or your platform's support for account and purchase problems.</p></section></article>'''


def page(title, desc, route, body):
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)}</title><meta name="description" content="{escape(desc, quote=True)}"><link rel="canonical" href="https://megabonk.org{route}"><link rel="icon" href="/assets/brotato/favicon.ico"><link rel="apple-touch-icon" href="/assets/brotato/icon-180.png"><link rel="stylesheet" href="/assets/guide-article-layout.css"><link rel="stylesheet" href="/assets/brotato/theme.css"></head><body class="guide-layout bt-theme bt-guide"><a class="skip" href="#main">Skip to content</a><header class="top"><div class="wrap"><a class="brand" href="{P}"><img src="/assets/brotato/logo.svg" width="44" height="44" alt=""><span>Brotato<small>Independent player guides</small></span></a><nav class="desktop-nav" aria-label="Brotato navigation"></nav><details class="mobile-nav"><summary>Menu</summary><nav class="mobile-links" aria-label="Brotato mobile navigation"></nav></details></div></header><main class="wrap" id="main">{body}</main><footer class="footer"></footer></body></html>'''


def build():
    pages = {
        'about': ('About the Brotato Guides | Megabonk.org',
                  'Who writes the unofficial Brotato guides on Megabonk.org, where patch, Evolution and co-op answers come from and how pages are rechecked after updates.', about()),
        'contact': ('Contact the Brotato Guide Editors | Megabonk.org',
                    'Report an outdated Brotato patch number, Evolution rule, Primal Dread listing or co-op step, with what to include and what we cannot help with.', contact()),
    }
    for slug, (title, desc, body) in pages.items():
        p = ROOT / 'brotato' / slug / 'index.html'
        p.parent.mkdir(parents=True, exist_ok=True)
        write_html(p, page(title, desc, f'{P}{slug}/', body), encoding='utf-8')
