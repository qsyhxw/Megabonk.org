"""Pokémon Battlegrounds 专区 About / Contact（SOP v3.26，02 §5.1）。

由 build_pokemon_battlegrounds.py 调用，导航与页脚由随后运行的 register_page.py 填充。信任页不放广告。
事实只来自本专区首页已写明的内容与 PB Ranked 公开的隐私/条款页，不新增游戏信息。Privacy 使用站级页的 #pokemon-battlegrounds 一节。"""
import json
from html import escape
from pathlib import Path

from site_analytics import write_html

ROOT = Path(__file__).resolve().parents[1]
P = '/pokemon-battlegrounds/'
REVIEWED = '22 November 2026'
GAME = 'https://pbranked.com/'
CHANNEL = 'https://pokemonbattlegrounds.com/'


def email():
    return json.loads((ROOT / 'config/site-contact.json').read_text(encoding='utf8'))['email']


def ext(url, label):
    return f'<a href="{escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">{label} ↗</a>'


def about():
    return f'''<main class="wrap" id="main"><article class="legal"><header class="article-head" id="guide"><p class="eyebrow">Pokémon Battlegrounds · About</p><h1>About the Pokémon Battlegrounds guide</h1>
<p class="byline">Megabonk.org editors · Facts reviewed {REVIEWED} · Sign-in and practice flow checked 5 November 2026</p></header>
<section id="who"><h2>Who runs this section</h2><p>This is an unofficial fan guide published by the editors of Megabonk.org. We do not make PB Ranked, we do not run the Pokémon Battlegrounds channel, and nothing here is endorsed by either. Pokémon names and artwork belong to their owners.</p><p>PB Ranked is a free fan game; its own privacy page names its maker. The guide points you to the game and explains what you meet before your first match. It does not host the game, your sign-in or any progress.</p></section>
<section id="covers"><h2>What it covers</h2><p>The <a href="{P}">guide home</a> gives the game’s <a href="{P}#address">current address</a>, then the <a href="{P}#start">first-battle path</a> from sign-in to an Easy practice match, the <a href="{P}#controls">Auto, called-move and Manual choices</a>, what the game <a href="{P}#account">keeps for your account</a> and a table for <a href="{P}#which-game">telling PB Ranked apart</a> from the channel website and from separate fan games.</p><p>It does not rank trainers or Pokémon, and it publishes no team lists.</p></section>
<section id="sources"><h2>Where the answers come from</h2><ul>
<li><strong>The original client:</strong> sign-in, the in-game help, the team screen and an Easy practice battle through its result screen, opened on 5 November 2026. The address change was read from the old address’s own notice on {REVIEWED}.</li>
<li><strong>The game’s published pages:</strong> {ext(GAME + 'privacy', 'privacy')} and {ext(GAME + 'terms', 'terms')}, both updated 1 November 2026, supply what the game stores and how seasons work.</li>
<li><strong>The creator’s announcement:</strong> the {ext('https://www.youtube.com/watch?v=23gz_hdNsrc', 'channel video')} of 30 October 2026 identifies the ranked game.</li>
<li><strong>Images:</strong> the sign-in screenshot and the task-card crops are captures of the game’s own screens, and the “which game” crop is the channel website’s home page. Competitive play and account transfer were not tried.</li></ul></section>
<section id="updates"><h2>How the page stays current</h2><p>The home page shows the dates it was checked. When the game changes its address, sign-in options or help text, the affected section is checked again and its date changes only after the answer was confirmed.</p></section>
<section id="identity"><h2>Which game this guide is about</h2><p>It covers PB Ranked at {ext(GAME, 'pbranked.com')}, the real-time browser game from the Pokémon Battlegrounds animation channel. The channel website, Pokémon Apex Arena and Poké Arena 2D are different projects and are marked as such on the home page.</p></section>
<section id="corrections"><h2>Send a correction</h2><p>Send the page URL and what you saw through the <a href="{P}contact/">contact page</a>. A screenshot of the game screen helps us confirm the fix quickly.</p></section>
</article></main>'''


def contact():
    mail = email()
    return f'''<main class="wrap" id="main"><article class="legal"><header class="article-head" id="guide"><p class="eyebrow">Pokémon Battlegrounds · Contact</p><h1>Contact the Pokémon Battlegrounds guide editors</h1>
<p class="byline">Reviewed {REVIEWED}</p></header>
<section id="write"><h2>Email</h2><p>Write to <a href="mailto:{mail}?subject=%5BPokemon%20Battlegrounds%5D%20Guide%20feedback">{mail}</a>. Useful reports for this section:</p><ul>
<li>A game address, sign-in option or practice mode that no longer matches the home page;</li>
<li>A control key or in-game help line that reads differently in the current client;</li>
<li>A wrong link, screenshot or project name in the “which game” table.</li></ul>
<p>Include the page URL, the device and browser you used and what the game showed. Do not send passwords or sign-in codes.</p></section>
<section id="cannot"><h2>What we cannot help with</h2><p>We do not run PB Ranked, so we cannot recover an account, restore a team or change a rating. Use <strong>Report a problem</strong> inside the original client, or the developer contact on its {ext(GAME + 'privacy', 'privacy page')}.</p></section>
</article></main>'''


def build(shell):
    pages = {
        'about': ({'title': 'About the Pokémon Battlegrounds Guide | Megabonk.org',
                   'description': 'Who writes the unofficial Pokémon Battlegrounds guide on Megabonk.org, where the PB Ranked address, sign-in and controls answers come from, and how they are rechecked.'}, about()),
        'contact': ({'title': 'Contact the Pokémon Battlegrounds Guide Editors | Megabonk.org',
                     'description': 'Report an outdated PB Ranked address, sign-in step or control key, with what to include and what we cannot help with.'}, contact()),
    }
    for slug, (page, main) in pages.items():
        route = f'{P}{slug}/'
        html = shell(route, page, 'pbg-guide', '', main, 'article')
        p = ROOT / 'pokemon-battlegrounds' / slug / 'index.html'
        p.parent.mkdir(parents=True, exist_ok=True)
        write_html(p, html, encoding='utf-8')
