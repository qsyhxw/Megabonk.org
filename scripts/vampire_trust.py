"""Vampire Survivors 专区 About / Contact（SOP v3.25，02 §5.1）。

在 build_vampire_survivors.py 中先于 register_page.py 运行，导航与页脚由后者填充。信任页不放广告。
事实全部来自本专区已有页面及其引用的作者资料，不新增游戏信息。Privacy 保持站级页（#vampire-survivors）。"""
import json
from html import escape
from pathlib import Path

from game_sections import navigation
from site_analytics import write_html

ROOT = Path(__file__).resolve().parents[1]
P = '/vampire-survivors/'
CHECKED = '10 November 2026'
STEAM = 'https://store.steampowered.com/app/1794680/Vampire_Survivors/'
DEMO = 'https://poncle.itch.io/vampire-survivors'
FAQ = 'https://poncle.games/vs-online-faq'
WIKI = 'https://vampire.survivors.wiki/'


def email():
    return json.loads((ROOT / 'config/site-contact.json').read_text(encoding='utf8'))['email']


def ext(url, label):
    return f'<a href="{escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">{label} ↗<span class="sr-only"> (external website)</span></a>'


def about():
    return f'''<article class="legal"><header class="article-head" id="guide"><p class="eyebrow">Vampire Survivors · About</p><h1>About the Vampire Survivors guide</h1>
<p class="byline">Megabonk.org editors · Facts reviewed {CHECKED}</p></header>
<section id="who"><h2>Who runs this section</h2><p>This is an unofficial fan guide published by the editors of Megabonk.org, an independent site for survivors-style games. We are not poncle, who makes Vampire Survivors, and the guides are not endorsed by the developer or by any platform that sells the game.</p></section>
<section id="covers"><h2>What it covers</h2><p>Weapon <a href="{P}evolutions/">evolution recipes</a>, <a href="{P}unlocks/">unlock routes</a>, the <a href="{P}collection-1-0/">Collection 1.0 checklist</a>, <a href="{P}dlc/">DLC pack comparison</a>, <a href="{P}co-op/">co-op compatibility</a> and the <a href="{P}">original browser demo</a>. Each page answers one job a player has during a run or before buying, and the DLC and recipe pages say plainly where coverage stops.</p></section>
<section id="sources"><h2>Where the answers come from</h2><ul>
<li><strong>The developer's own pages:</strong> the {ext(DEMO, 'itch.io demo page')} and its FAQ describe the browser demo and its save; the {ext(FAQ, 'online co-op FAQ')} and the {ext(STEAM, 'Steam store page')} supply supported modes, editions and DLC listings.</li>
<li><strong>The community wiki:</strong> recipe levels, passive conditions and unlock requirements are checked against the {ext(WIKI, 'Vampire Survivors Wiki')}, and each guide links the entry behind its claim.</li>
<li><strong>Demo screenshots:</strong> the browser-demo images are frames from one opening run in desktop Chrome on 5 November 2026. The full-game guides rely on the sources above rather than on our own complete playthroughs.</li></ul></section>
<section id="updates"><h2>How pages stay current</h2><p>Every guide shows the date it was checked; the section as a whole was last reviewed on {CHECKED}. When poncle releases an update or a new DLC, the pages that depend on its recipes, unlock conditions or storefront rules are rechecked first.</p></section>
<section id="identity"><h2>Which game this guide is about</h2><p>Searches for the name also return similarly named browser games and clones. These pages cover poncle's Vampire Survivors and its original itch.io demo only. Browser games inspired by it are compared on a separate page, with their own saves and hosts.</p></section>
<section id="corrections"><h2>Send a correction</h2><p>Send the page URL, your platform and what you saw through the <a href="{P}contact/">contact page</a>. Corrections backed by a screenshot or the developer's own statement are reviewed first.</p></section></article>'''


def contact():
    mail = email()
    return f'''<article class="legal"><header class="article-head" id="guide"><p class="eyebrow">Vampire Survivors · Contact</p><h1>Contact the Vampire Survivors guide editors</h1>
<p class="byline">Reviewed {CHECKED}</p></header>
<section id="write"><h2>Email</h2><p>Write to <a href="mailto:{mail}?subject=%5BVampire%20Survivors%5D%20Guide%20feedback">{mail}</a>. Useful reports for this section:</p><ul>
<li>A recipe, passive level or unlock condition that changed in a newer game update;</li>
<li>A DLC pack, price or free-pack listing that no longer matches the store;</li>
<li>A co-op or storefront pairing that works differently from the co-op page;</li>
<li>A wrong screenshot, link or character name on a Vampire Survivors page.</li></ul>
<p>Include the page URL, your platform, the game version and what happened. A screenshot helps us confirm the fix quickly.</p></section>
<section id="cannot"><h2>What we cannot help with</h2><p>We are not the developer or the game's support team, so we cannot restore a save, fix a store purchase or change how the game works. Use the developer's {ext(FAQ, 'support pages')} or your platform's support for account and purchase problems.</p></section></article>'''


def page(route, title, desc, body):
    nav = navigation(route)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)}</title><meta name="description" content="{escape(desc, quote=True)}"><link rel="canonical" href="https://megabonk.org{route}"><link rel="icon" href="/favicon.ico"><link rel="stylesheet" href="/assets/guide-article-layout.css"><link rel="stylesheet" href="/assets/vampire-survivors/theme.css"></head><body class="guide-layout vs-theme vs-guide"><a class="skip" href="#main">Skip to content</a><header class="top"><div class="wrap"><a class="brand" href="{P}"><span>Vampire Survivors<small>Independent player guides</small></span></a><nav class="desktop-nav" aria-label="Main navigation">{nav}</nav><details class="mobile-nav"><summary>Menu</summary><nav class="mobile-links" aria-label="Mobile navigation">{nav}</nav></details></div></header><main class="wrap" id="main">{body}</main><footer class="footer"></footer></body></html>'''


def build():
    pages = {
        'about': ('About the Vampire Survivors Guide | Megabonk.org',
                  'Who writes the unofficial Vampire Survivors guides on Megabonk.org, where recipes and unlock answers come from and how pages are rechecked after game updates.', about()),
        'contact': ('Contact the Vampire Survivors Guide Editors | Megabonk.org',
                    'Report an outdated Vampire Survivors recipe, unlock, DLC or co-op answer, with what to include and what we cannot help with.', contact()),
    }
    for slug, (title, desc, body) in pages.items():
        p = ROOT / 'vampire-survivors' / slug / 'index.html'
        p.parent.mkdir(parents=True, exist_ok=True)
        write_html(p, page(f'{P}{slug}/', title, desc, body), encoding='utf-8')
