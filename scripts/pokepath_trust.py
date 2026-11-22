"""PokéPath TD 专区 About / Contact（SOP v3.26，02 §5.1）。

由 build_pokepath.py 调用，导航与页脚由随后运行的 register_page.py 填充。信任页不放广告。
事实全部来自本专区已有页面及其引用的原作站资料，不新增游戏信息。Privacy 使用站级页的 #pokepath 一节。"""
import json
from html import escape
from pathlib import Path

from site_analytics import write_html

ROOT = Path(__file__).resolve().parents[1]
P = '/pokepath/'
REVIEWED = '22 November 2026'
CHECKED = '9 November 2026'
HOME = 'https://pokepath.gg/'
LEGAL = HOME + 'legal'
FAQ = HOME + 'wiki/faq/'
PATCH = HOME + 'devlog/patch-notes-1-7-2/'


def email():
    return json.loads((ROOT / 'config/site-contact.json').read_text(encoding='utf8'))['email']


def ext(url, label):
    return f'<a href="{escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">{label} ↗</a>'


def about():
    return f'''<main class="wrap" id="main"><article class="legal"><header class="article-head" id="guide"><p class="eyebrow">PokéPath TD · About</p><h1>About the PokéPath TD guide</h1>
<p class="byline">Megabonk.org editors · Facts reviewed {REVIEWED} · Play page checked: 1.7.2 ({CHECKED})</p></header>
<section id="who"><h2>Who runs this section</h2><p>This is an unofficial fan guide published by the editors of Megabonk.org, an independent site for survivors-style and Pokémon-themed games. The original game and its website come from other people: the {ext(LEGAL, 'original legal page')} names Khydra as the game developer and Nox as the site maintainer. We work with neither, and nothing here is endorsed by them or by the owners of the Pokémon names and artwork the game uses.</p></section>
<section id="covers"><h2>What it covers</h2><p>The <a href="{P}">guide home</a> sends you to the page for your next job: <a href="{P}best-pokemon/">team roles and upgrade choices</a>, <a href="{P}mobile/">phone limits and save transfer</a>, <a href="{P}route-1-3/">Route 1-3 and Lunala</a> and <a href="{P}codes/">reward codes and redemption fields</a>.</p></section>
<section id="sources"><h2>Where the answers come from</h2><ul>
<li><strong>The original site’s own pages:</strong> the {ext(HOME + 'pokedex/', 'Pokédex')}, bestiary, map pages, the {ext(FAQ, 'device FAQ')}, the non-shop unlock guide and the {ext(PATCH, '1.7.2 patch notes')} supply unit abilities, enemy rules, save steps and listed codes.</li>
<li><strong>The browser client:</strong> the profile-creation screen and the Route 1-1 tutorial were opened on {CHECKED}. A full route clear, a save transfer and a code redemption were not completed, and the pages say so where it matters.</li>
<li><strong>Public player threads:</strong> Reddit discussions are used as symptom reports and labelled with the build they describe; they are not treated as proof of a working setup.</li>
<li><strong>Images:</strong> the profile screenshot is our capture of the original client; the route terrain and Pokémon artwork come from the original project’s own pages, checked {CHECKED}.</li></ul></section>
<section id="updates"><h2>How pages stay current</h2><p>Each guide shows the date it was checked and the play-page version it was checked against. The section as a whole was last reviewed on {REVIEWED}; the content was last checked against play page 1.7.2. The game changes abilities, items and attackers between patches, so the pages that depend on those numbers are rechecked after a new patch, and a page’s date changes only when its answer was confirmed again.</p></section>
<section id="identity"><h2>Which game this guide is about</h2><p>These pages cover PokéPath TD, the route tower defense game at pokepath.gg. PokeBonk, PokéSurvivor, PokéRogue and PokéClicker are separate projects with their own progression, and other sites and hosts may add their own features to a copy of the same game, so guidance here follows the original site.</p></section>
<section id="corrections"><h2>Send a correction</h2><p>Send the page URL, the game version shown on your play page and what you saw through the <a href="{P}contact/">contact page</a>. Corrections backed by a screenshot or the original site’s own statement are reviewed first.</p></section>
</article></main>'''


def contact():
    mail = email()
    return f'''<main class="wrap" id="main"><article class="legal"><header class="article-head" id="guide"><p class="eyebrow">PokéPath TD · Contact</p><h1>Contact the PokéPath TD guide editors</h1>
<p class="byline">Reviewed {REVIEWED}</p></header>
<section id="write"><h2>Email</h2><p>Write to <a href="mailto:{mail}?subject=%5BPok%C3%A9Path%20TD%5D%20Guide%20feedback">{mail}</a>. Useful reports for this section:</p><ul>
<li>A unit ability, enemy rule or item that changed in a newer patch;</li>
<li>A save export or import step that works differently on your device or browser;</li>
<li>A reward code or redemption field that behaves differently from the code guide;</li>
<li>A wrong screenshot, link or Pokémon name on a PokéPath TD page.</li></ul>
<p>Include the page URL, your device and browser, the version shown on your play page and what happened. A screenshot helps us confirm the fix quickly.</p></section>
<section id="cannot"><h2>What we cannot help with</h2><p>We are not the developer or the game’s support team, so we cannot restore a save, grant a reward or change how the game works. Use the {ext(HOME, 'original PokéPath site')} to reach the project.</p></section>
</article></main>'''


def build(shell):
    pages = {
        'about': ({'title': 'About the PokéPath TD Guide | Megabonk.org',
                   'description': 'Who writes the unofficial PokéPath TD guides on Megabonk.org, where unit, route and save answers come from and how pages are rechecked after patches.',
                   'image': 'start'}, about()),
        'contact': ({'title': 'Contact the PokéPath TD Guide Editors | Megabonk.org',
                     'description': 'Report an outdated PokéPath TD team, route, save or code answer, with what to include and what we cannot help with.',
                     'image': 'start'}, contact()),
    }
    for slug, (page, main) in pages.items():
        route = f'{P}{slug}/'
        html = shell(route, page, 'pp-guide', '', main)
        p = ROOT / 'pokepath' / slug / 'index.html'
        p.parent.mkdir(parents=True, exist_ok=True)
        write_html(p, html, encoding='utf-8')
