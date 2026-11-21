"""Spires of Azeroth 专区首页组件与信任页（SOP v3.25，02 §4 / §5.1 / 08 F9）。

任务卡、最新更新、分组入口、FAQ 都读 data/spires-of-azeroth-pages.json；导航、面包屑、页脚与登记由 register_page.py 在
build_spires_of_azeroth.py 最后一步生成。信任页只写本游戏的真实内容，不放广告。"""
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = '/spires-of-azeroth/'
GAME = 'https://thewowdb.com/spiresofazeroth/'
REPO = 'https://github.com/Chrisl252/spiresofazeroth'
BUILD = '20261103e'
CHECKED = '4 November 2026'
REVIEWED = '21 November 2026'


def manifest():
    return json.loads((ROOT / 'data/spires-of-azeroth-pages.json').read_text(encoding='utf8'))


def href(h):
    """清单里的相对写法：'#x' 与 'sub/#y' 归到专区路径，绝对路径原样。"""
    return h if h.startswith('/') else P + h


def _hub(m=None):
    from hub_components import Hub
    return Hub(m or manifest(), P, 'saz', '/assets/spires-of-azeroth/')


def hero(figure_ref=''):
    status = ['Browser · Windows · Mac · Linux · Android', f'Browser build {BUILD}', f'Checked {CHECKED}', 'Unofficial fan guide']
    return _hub({}).hero(
        kicker='A Classic WoW roguelike deckbuilder', title='Spires of Azeroth', sub='Guide &amp; Wiki',
        deck='Draft familiar spells, read the enemy’s next move and climb a spire one turn at a time. '
             f'Play the original in a window below.{figure_ref}',
        status=status, actions=[('Play now ↓', '#play', False), ('Download & platforms →', f'{P}download-platforms/', True)])


def cards(m):
    return _hub(m).cards()


def cheat():
    k = lambda s: f'<kbd>{s}</kbd>'
    rows = [
        ('Play a card', f'Drag it onto an enemy, or click the card and then the target. Keys {k("1")}–{k("9")} pick a card.'),
        ('Energy', 'The red orb refills every turn, so spend it all.'),
        ('Potions', f'Press a potion in the belt and drag the arrow onto an enemy. {k("Esc")} cancels.'),
        ('Intents', 'The icon above an enemy is its next move; a sword and a number is an attack for that much.'),
        ('End turn', f'The button, or {k("Space")} / {k("E")}. {k("Esc")} opens the menu, {k("F")} is fullscreen.'),
        ('Scope', 'The author lists nine Classic classes and 40 zones. We have not cleared them all.'),
    ]
    return _hub({}).cheat('Combat cheat sheet', f'Read from the original’s “How to fight” tutorial, browser build {BUILD}, checked {CHECKED}.', rows)


def updates(m):
    return _hub(m).updates()


def groups(m):
    return _hub(m).groups()


def faq(m):
    return _hub(m).faq()


def faq_questions(m):
    return _hub(m).faq_questions()


# ---------- 信任页（02 §5.1）----------
def email():
    return json.loads((ROOT / 'config/site-contact.json').read_text(encoding='utf8'))['email']


def ext(url, label):
    return f'<a href="{escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">{label} ↗</a>'


def about():
    return f'''<article class="legal" id="guide"><header class="article-head"><span class="tag">Spires of Azeroth · About</span><h1>About the Spires of Azeroth guide</h1>
<p class="byline">Megabonk.org editors · Facts reviewed {REVIEWED} · Checked against browser build {BUILD}</p></header>
<section id="who"><h2>Who runs this section</h2><p>This is an unofficial fan guide published by the editors of Megabonk.org. We are not Chrisl252, who makes Spires of Azeroth, we do not run TheWoWDB where the game is hosted, and we are not Blizzard Entertainment. Warcraft names and artwork belong to their owners.</p><p>The game is a fan project inspired by Classic World of Warcraft. It is a turn-based card roguelike, not Blizzard’s MMO and not the survival game Azeroth Survivors.</p></section>
<section id="covers"><h2>What it covers</h2><p>The <a href="{P}">guide home</a> loads the original game in a window on click and explains the <a href="{P}#how-to-play">first run</a>, the <a href="{P}#controls">card controls</a> and <a href="{P}#classes">how the nine classes differ</a>. The <a href="{P}download-platforms/">download page</a> separates the browser, the author’s desktop and Android packages and the iPhone / iPad Safari route, and explains why saves do not move between them.</p><p>It does not rank classes or publish a best-deck list.</p></section>
<section id="sources"><h2>Where the answers come from</h2><ul>
<li><strong>The original game:</strong> menus, the “How to fight” tutorial, the Download panel and the title screen are captured from the browser game at {ext(GAME, 'thewowdb.com')}.</li>
<li><strong>The author’s repository:</strong> platform packages, first-launch behaviour and version numbers come from {ext(REPO, 'Chrisl252/spiresofazeroth')} and its latest release.</li>
<li><strong>Our own checks:</strong> a short run to the second turn in a browser window, desktop and mobile viewport sizes. We have not cleared a full run, installed a package, moved a save between hosts, tried the Co-op mode or used a physical phone, and the pages do not claim to.</li></ul></section>
<section id="updates"><h2>How pages stay current</h2><p>Each page shows the date it was checked. The version line on the download page follows the author’s browser build and latest GitHub package automatically; the walkthrough steps are rechecked when a new build changes the menus. The current baseline is browser build {BUILD}, inspected {CHECKED}.</p></section>
<section id="corrections"><h2>Found something wrong?</h2><p>Send the page URL, the host you used (the original site, our game window or an app package), the build or version shown and what you saw through the <a href="{P}contact/">contact page</a>. Corrections with a screenshot or a public reference are usually applied in the next update.</p></section></article>'''


def contact():
    mail = email()
    return f'''<article class="legal" id="guide"><header class="article-head"><span class="tag">Spires of Azeroth · Contact</span><h1>Contact the Spires of Azeroth guide editors</h1>
<p class="byline">Reviewed {REVIEWED}</p></header>
<section id="write"><h2>Email</h2><p>Write to <a href="mailto:{mail}?subject=%5BSpires%20of%20Azeroth%5D%20Guide%20feedback">{mail}</a>. Useful reports for this section:</p><ul>
<li>A first-run step, control or menu that no longer matches the original’s current build;</li>
<li>A download route, package name or version line that has changed;</li>
<li>A wrong class, card or save statement, with the screen where you saw it;</li>
<li>A broken link, image or layout on a Spires of Azeroth page.</li></ul>
<p>Include the page URL, the host (original, our game window or an app package), the build or version shown and your browser or operating system. A screenshot helps us confirm the fix quickly.</p></section>
<section id="cannot"><h2>What we cannot help with</h2><p>We are not the game’s author or support, so we cannot recover a lost save, read the storage of another website, install a package for you or change how the game works. For those, use the project’s own {ext(REPO, 'GitHub repository')} and keep the backups described on the <a href="{P}download-platforms/#saves">saves &amp; versions section</a>.</p></section></article>'''


def build_trust(shell, write_html):
    pages = {
        'about': ('About the Spires of Azeroth Guide | Megabonk.org',
                  'Who writes the unofficial Spires of Azeroth guide on Megabonk.org, where the answers come from, what was and was not tested, and how pages are rechecked.', about()),
        'contact': ('Contact the Spires of Azeroth Guide Editors | Megabonk.org',
                    'Report an outdated first-run step, download route or save statement in the Spires of Azeroth guide, with what to include and what we cannot help with.', contact()),
    }
    for slug, (title, desc, body) in pages.items():
        p = ROOT / 'spires-of-azeroth' / slug / 'index.html'
        p.parent.mkdir(parents=True, exist_ok=True)
        write_html(p, shell(f'{P}{slug}/', title, desc, body, trust=True), encoding='utf8')
