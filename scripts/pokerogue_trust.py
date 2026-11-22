"""PokeRogue 专区 About / Contact（SOP v3.26，02 §5.1）。

由 build_pokerogue.py 调用，导航与页脚由随后运行的 register_page.py 填充。信任页不放广告。
事实全部来自本专区已有页面引用的来源，不新增游戏信息。Privacy 使用站级页的 #pokerogue 一节。"""
import json
from html import escape
from pathlib import Path

from site_analytics import write_html

ROOT = Path(__file__).resolve().parents[1]
P = '/pokerogue/'
REVIEWED = '22 November 2026'
CHECKED = '6 November 2026'
GAME = 'https://pokerogue.net/'
REPO = 'https://github.com/pagefaultgames/pokerogue'
WIKI = 'https://wiki.pokerogue.net/'


def email():
    return json.loads((ROOT / 'config/site-contact.json').read_text(encoding='utf8'))['email']


def ext(url, label):
    return f'<a href="{escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">{label} ↗<span class="sr-only"> (opens in a new tab)</span></a>'


def about():
    return f'''<main class="wrap" id="main"><article class="legal"><header class="article-head" id="guide"><p class="eyebrow">PokeRogue · About</p><h1>About the PokeRogue guides</h1>
<p class="byline">Megabonk.org editors · Facts reviewed {REVIEWED} · Game release checked: v1.12.2.4</p></header>
<section id="who"><h2>Who runs this section</h2><p>This is an unofficial fan guide published by the editors of Megabonk.org, an independent site for survivors-style and roguelite games. We are not the Pagefault Games project that makes PokéRogue, and nothing here is endorsed by it or by any Pokémon rights holder.</p></section>
<section id="covers"><h2>What it covers</h2><p>The <a href="{P}">guide home</a> sends you to the original game and to the page for your next decision: <a href="{P}mobile/">mobile versions and the original entry</a>, <a href="{P}dark-deal/">whether to accept Dark Deal</a> and <a href="{P}trash-to-treasure/">whether to dig or investigate in Trash to Treasure</a>. We do not host the game, accounts or saves.</p></section>
<section id="sources"><h2>Where the answers come from</h2><ul>
<li><strong>The original game:</strong> the account screen and links at {ext(GAME, 'pokerogue.net')} identify the official entry point.</li>
<li><strong>The project code:</strong> encounter rules, wave windows and cost bands are checked against release v1.12.2.4 in the {ext(REPO, 'project repository')}. Code inspection supports the rules; it is not a live run.</li>
<li><strong>The community wiki and player guides:</strong> the {ext(WIKI, 'PokéRogue Wiki')} and a named community mobile guide supply controls, home-screen steps and the online-to-offline save direction.</li>
<li><strong>Images:</strong> the account screen was captured from the original client and encounter sprites come from the project’s assets revision for v1.12.2.4. They identify the game or encounter and are not gameplay screenshots.</li></ul></section>
<section id="updates"><h2>How pages stay current</h2><p>Each guide shows the date it was checked; the section as a whole was last reviewed on {REVIEWED}, with rules last confirmed on {CHECKED}. When an encounter or balance update changes a rule, the page that depends on it is rechecked and its date changes only when the answer was confirmed again.</p></section>
<section id="identity"><h2>Which game this guide is about</h2><p>These pages cover PokéRogue, the browser roguelite at pokerogue.net. It is a different game from PokeBonk and other similarly named Pokémon projects, which have their own pages on this site.</p></section>
<section id="corrections"><h2>Send a correction</h2><p>Send the page URL, how you play (browser, shortcut or community app), the game version if you know it and what you saw through the <a href="{P}contact/">contact page</a>. Corrections backed by a screenshot or the project’s own code are reviewed first.</p></section>
</article></main>'''


def contact():
    mail = email()
    return f'''<main class="wrap" id="main"><article class="legal"><header class="article-head" id="guide"><p class="eyebrow">PokeRogue · Contact</p><h1>Contact the PokeRogue guide editors</h1>
<p class="byline">Reviewed {REVIEWED}</p></header>
<section id="write"><h2>Email</h2><p>Write to <a href="mailto:{mail}?subject=%5BPokeRogue%5D%20Guide%20feedback">{mail}</a>. Useful reports for this section:</p><ul>
<li>A Dark Deal or Trash to Treasure rule, cost band or wave window that differs in a newer release;</li>
<li>A browser, home-screen or community-app step that works differently on your device;</li>
<li>An offline-save or transfer detail that no longer matches the wiki;</li>
<li>A wrong screenshot, link or encounter name on a PokeRogue page.</li></ul>
<p>Include the page URL, your device and browser, how you play and what happened. A screenshot helps us confirm the fix quickly.</p></section>
<section id="cannot"><h2>What we cannot help with</h2><p>We do not run PokéRogue, so we cannot restore an account or save, fix a login problem or change how the game works. Use the {ext(GAME, 'original game')} for account questions or the {ext(REPO, 'project repository')} to reach the developers.</p></section>
</article></main>'''


def build(shell):
    pages = {
        'about': ({'title': 'About the PokeRogue Guides | Megabonk.org',
                   'description': 'Who writes the unofficial PokeRogue guides on Megabonk.org, where encounter and version answers come from and how pages are rechecked after game updates.'}, about()),
        'contact': ({'title': 'Contact the PokeRogue Guide Editors | Megabonk.org',
                     'description': 'Report an outdated PokeRogue encounter rule, mobile step or offline-save detail, with what to include and what we cannot help with.'}, contact()),
    }
    for slug, (page, main) in pages.items():
        route = f'{P}{slug}/'
        html = shell(route, page, 'pr-guide', '', main)
        p = ROOT / 'pokerogue' / slug / 'index.html'
        p.parent.mkdir(parents=True, exist_ok=True)
        write_html(p, html, encoding='utf-8')
