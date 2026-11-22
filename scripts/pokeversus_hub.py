"""PokéVersus 专区首页组件与信任页（SOP v3.25，02 §4 / §5.1 / 08 F9）。

任务卡、最新更新、FAQ 读 data/pokeversus-pages.json；导航、页脚与登记由 register_page.py 在
build_pokeversus.py 最后一步生成。信任页只写本游戏的真实内容，不放广告。"""
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = '/pokeversus/'
GAME = 'https://pokeversus.com/'
NEWS = GAME + 'js/news.js'
VERSION = '2.37'
CHECKED = '5 November 2026'
REVIEWED = '22 November 2026'


def manifest():
    return json.loads((ROOT / 'data/pokeversus-pages.json').read_text(encoding='utf8'))


def _hub(m=None):
    from hub_components import Hub
    return Hub(m or {}, P, 'pv', '/assets/pokeversus/')


def hero(ref_html=''):
    status = ['Free in your browser', '3v3 brawler · 10-player Toxic Fog', f'Original client v{VERSION}', f'Checked {CHECKED}', 'Unofficial fan guide']
    return _hub().hero(
        kicker='Pokémon browser brawler · 3v3',
        title='PokéVersus', sub='',
        deck='A free fan-made brawler by Fl3xix: pick one starter of each type and fight short 3v3 matches, or drop into the '
             f'10-player Toxic Fog. Play the original below or open it in its own tab; guest play needs no account.{ref_html}',
        status=status, actions=[('Play now ↓', '#play', False), ('First match →', '#start', True)])


def cards(m):
    return _hub(m).cards(heading='Pick your task')


def cheat(ref_html=''):
    rows = [
        ('Catch the Balls', '3v3: take 10 Poké Balls from the central machine and hold them for 15 seconds.'),
        ('Toxic Fog', 'Free-for-all for 10 players, Solo or Duo: break crates for Rare Candies; last one standing wins.'),
        ('Wake Up Snorlax', '3v3: protect your sleeping Snorlax and knock out the enemy one first.'),
        ('Voltorb Ball', '3v3: carry the Voltorb into the enemy goal; first to 2 wins, and it explodes after 10 seconds.'),
        ('Territory', '3v3: hold the central zone with no enemies inside; first team to 100% wins.'),
        ('Team Duel', 'Most knockouts in 2.5 minutes, or first to 15. Knockout is the no-respawn version, best of 3.'),
    ]
    return _hub().cheat('Mode quick sheet',
                        f'Read from the mode list in original client v{VERSION}, checked {CHECKED}. Random pools everyone into one mode every 5 minutes.{ref_html}',
                        rows)


def updates(m):
    return _hub(m).updates()


def faq(m):
    return _hub(m).faq(heading='Quick answers')


def faq_questions(m):
    return _hub(m).faq_questions()


# ---------- 信任页（02 §5.1）----------
def email():
    return json.loads((ROOT / 'config/site-contact.json').read_text(encoding='utf8'))['email']


def ext(url, label):
    return f'<a href="{escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">{label} ↗</a>'


def about():
    return f'''<article class="legal" id="guide"><header class="article-head"><span class="tag">PokéVersus · About</span><h1>About the PokéVersus guide</h1>
<p class="byline">Megabonk.org editors · Facts reviewed {REVIEWED} · Checked against original client v{VERSION}</p></header>
<section id="who"><h2>Who runs this section</h2><p>This is an unofficial fan guide published by the editors of Megabonk.org. We are not Fl3xix (Chacoon Studio), who makes PokéVersus, and we do not run pokeversus.com. Pokémon names and artwork belong to Nintendo, Creatures Inc., GAME FREAK and The Pokémon Company, and this guide is unaffiliated with any of them.</p></section>
<section id="covers"><h2>What it covers</h2><p>The <a href="{P}">guide page</a> loads the original game in a window on click, then walks through the <a href="{P}#start">login window, trainer name and starter choice</a>, the <a href="{P}#modes">mode list</a>, <a href="{P}#account">what a guest and an account save</a>, and <a href="{P}#which-game">which similarly named games are different projects</a>.</p></section>
<section id="sources"><h2>Where the answers come from</h2><ul>
<li><strong>The original game:</strong> the login window, starter selection, hub and mode list were captured from the browser client at {ext(GAME, 'pokeversus.com')}, entered as a guest.</li>
<li><strong>The patch feed:</strong> the version number and recent changes come from the game’s own {ext(NEWS, 'news.js')} feed, read on {CHECKED}.</li>
<li><strong>Our own checks:</strong> a guest start through to the mode list at desktop and phone-width viewport sizes. No full or ranked match, account sign-up, clan war, cross-device save or physical phone was part of the check, and the frame itself accepts input only inside its own origin.</li></ul></section>
<section id="updates"><h2>How the page stays current</h2><p>The page shows the client version and the date it was checked. The game updates often, so the version line and the mode list are the first things to recheck when the feed shows a new release.</p></section>
<section id="corrections"><h2>Corrections</h2><p>Send the page URL, the host you used (the original site or our game window), the version shown at the bottom of the client and what you saw through the <a href="{P}contact/">contact page</a>. A confirmed error is corrected on the page and the check date updated.</p></section></article>'''


def contact():
    mail = email()
    return f'''<article class="legal" id="guide"><header class="article-head"><span class="tag">PokéVersus · Contact</span><h1>Contact the PokéVersus guide editors</h1>
<p class="byline">Reviewed {REVIEWED}</p></header>
<section id="write"><h2>Email</h2><p>Write to <a href="mailto:{mail}?subject=%5BPok%C3%A9Versus%5D%20Guide%20feedback">{mail}</a>. Useful reports for this section:</p><ul>
<li>A login, starter or hub step that no longer matches the current client;</li>
<li>A mode description, rule or limit that the mode list now words differently;</li>
<li>A save or account statement that your own experience contradicts, with what you did;</li>
<li>A broken link, image or layout on the PokéVersus page.</li></ul>
<p>Include the page URL, the version shown in the client, whether you played as a guest or signed in, and your browser or operating system. A screenshot helps us confirm the fix quickly.</p></section>
<section id="cannot"><h2>What we cannot help with</h2><p>We are not the game’s author or support, so we cannot recover a lost account or guest save, read the storage of another website, change matchmaking or restore a banned account. For those, use the contact routes inside the original game.</p></section></article>'''


def build_trust(shell, write_html):
    pages = {
        'about': ('About the PokéVersus Guide | Megabonk.org',
                  'Who writes the unofficial PokéVersus guide on Megabonk.org, where the answers come from, what was and was not checked, and how the page is rechecked.', about()),
        'contact': ('Contact the PokéVersus Guide Editors | Megabonk.org',
                    'Report an outdated login step, mode description or save statement in the PokéVersus guide, with what to include and what we cannot help with.', contact()),
    }
    for slug, (title, desc, body) in pages.items():
        p = ROOT / 'pokeversus' / slug / 'index.html'
        p.parent.mkdir(parents=True, exist_ok=True)
        write_html(p, shell(f'{P}{slug}/', title, desc, body, trust=True), encoding='utf8')
