"""D2 Survivors hub home (SOP v3.25, 08 F9): status line, task cards, edition check, updates, grouped entries, FAQ.

Cards, groups, updates and FAQ come from data/d2-survivors-pages.json (02 §2.6); the nav, breadcrumbs,
footer and registries are filled afterwards by register_page.py. The H1 text, title and description of the
original home are kept (00 §5A: the page has stable clicks)."""
import json
import re
from html import escape
from pathlib import Path

P = '/d2-survivors/'
ROOT = Path(__file__).resolve().parents[1]


def manifest():
    m = json.loads((ROOT / 'data/d2-survivors-pages.json').read_text(encoding='utf8'))
    m['by'] = {p['slug']: p for p in m['pages']}
    return m


def href(slug):
    return P + (slug + '/' if slug else '')


def home(shell, ext, figure):
    m = manifest()
    cards = sorted((p for p in m['pages'] if p.get('card')), key=lambda p: p['card'])
    lang = lambda p: f' lang="{p["lang"]}"' if p.get('lang') else ''
    card_html = ''.join(
        f'<a class="d2-card" href="{href(p["slug"])}"{lang(p)}>'
        f'<img src="/assets/d2-survivors/{p["thumb"]}" width="320" height="200" alt="" loading="eager">'
        f'<span class="d2-card-body"><span class="d2-number">{p["card"]:02d}</span><strong>{escape(p["title"])}</strong>'
        f'<span class="d2-card-text">{escape(p["blurb"])}</span></span></a>' for p in cards)
    status = ['Browser + desktop', 'Original build 20261102.2', 'Checked 3 Nov 2026', 'Unofficial fan guide']
    hero = (
        '<header class="d2-hero" id="guide"><p class="d2-kicker">Guide &amp; wiki · Framara’s Diablo II-inspired survivors game</p>'
        '<h1>D2 Survivors</h1>'
        '<p class="d2-deck">Pick the right edition, get it running and keep your saved run safe.</p>'
        '<ul class="d2-status" aria-label="Game status">' + ''.join(f'<li>{s}</li>' for s in status) + '</ul>'
        f'<div class="hero-actions"><a class="button" href="{P}play/">Play in a game window →</a>'
        f'<a class="button secondary" href="{P}beginners-guide/">Start here →</a></div>'
        f'<p class="d2-source">Want the current original? {ext("https://d2survivors.lol/", "D2 Survivors · original project")} [1]</p></header>'
        '<div class="d2-hero-media">'
        + figure('druid-select', 'Druid selected among the original D2 Survivors heroes',
                 'Original hero-selector interface, captured 3 November 2026. Game art © Blizzard Entertainment / respective owners. Interface inspection, not a build ranking.', 2)
        + '</div>')
    tasks = ('<section class="d2-tasks" id="guides"><h2>What are you trying to do?</h2>'
             f'<div class="d2-cards">{card_html}</div></section>')
    versions = '''<section class="d2-band" id="versions"><p class="d2-eyebrow">Edition check</p><h2>One name does not mean one version</h2><div class="table-wrap" tabindex="0" role="region" aria-label="D2 Survivors editions"><table><thead><tr><th>What you found</th><th>What this guide means</th><th>Where to go</th></tr></thead><tbody><tr><td>Framara’s original</td><td>The fan project at d2survivors.lol, with its own browser and desktop routes. Its current FAQ asks for your own Diablo II or D2R installation.</td><td><a href="/d2-survivors/setup/">Prepare the original →</a></td></tr><tr><td>Our Play window</td><td>A third-party edition from play.d2survivors.org. Its menu and run display older, differing build labels. It is not presented as the current original.</td><td><a href="/d2-survivors/play/">Read the host notice and play →</a></td></tr><tr><td>zombodotcom’s Windows project</td><td>Another publisher’s D2 Survivors project, with its own launcher and mode descriptions. Do not assume our original-game instructions or saves apply.</td><td>Follow that project’s own page [3]</td></tr></tbody></table></div><p>Bring a backup, not an assumption of compatibility. A name match, familiar Diablo art or an identical button does not prove that two websites share progress. [1][2][3]</p></section>'''
    recent = sorted((p for p in m['pages'] if p.get('card')), key=lambda p: (p['updated'], -p['card']), reverse=True)[:4]
    updates = ('<section class="d2-band" id="updates"><h2>Latest updates</h2><ul class="d2-updates">'
               + ''.join(f'<li><time datetime="{p["updated"]}">{p["updated"]}</time> <a href="{href(p["slug"])}"{lang(p)}>{escape(p["title"])}</a> <span>{escape(p["blurb"])}</span></li>' for p in recent)
               + '</ul><p>Read the build before following old advice: a new menu build does not automatically validate every guide, so each page keeps its own check date. [2][4]</p></section>')
    groups = ''
    for g in m['groups']:
        links = ''.join(f'<li><a href="{href(p["slug"])}"{lang(p)}>{escape(p["title"])}</a></li>' for p in m['pages'] if p.get('group') == g['id'])
        groups += f'<div class="d2-group"><h3>{escape(g["label"])}</h3><p>{escape(g["text"])}</p><ul>{links}</ul></div>'
    grouped = f'<section class="d2-band" id="all-guides"><h2>All guides by task</h2><div class="d2-groups">{groups}</div></section>'
    about = '''<section class="d2-band" id="about-game"><h2>About D2 Survivors</h2><div class="d2-two"><div id="start"><p>D2 Survivors is a fan-made survival game: pick a Diablo II hero, move through the horde and let skills attack on their own while each level-up shapes the next upgrade. The checked original menu displayed build 20261102.2 and a class selector, while current reference pages also describe a camp and waypoint; the <a href="/d2-survivors/beginners-guide/">beginner guide</a> covers both so you do not hunt an older menu for a newer control. [2][4]</p></div><div id="platforms"><p>The original offers browser and desktop routes. Its setup warns that temporary hosted files are going away, and its FAQ currently recommends a computer; older phone reports can describe a different transition state. A mobile app request, a home-screen shortcut and a verified native app are different things. <a href="/d2-survivors/setup/">Choose the supported setup path</a>. [1][4]</p></div></div></section>'''
    faq_items = ''.join(
        f'<details class="d2-faq-item"><summary>{escape(f["q"])}</summary><p>{escape(f["a"])}</p>'
        f'<a class="d2-faq-more" href="{href(f["link"])}">Full guide →</a></details>' for f in m['faq'])
    faq = f'<section class="d2-band" id="faq"><h2>FAQ</h2><p class="d2-lede">Quick answers; each links to the full guide.</p><div class="d2-faq">{faq_items}</div></section>'
    sources = [('https://d2survivors.lol/faq/', 'D2 Survivors · original FAQ', 'Identity, platforms and mode boundaries; checked 3 November 2026.'),
               ('https://d2survivors.lol/play/', 'D2 Survivors · original browser game', 'Actual interface capture and displayed menu build 20261102.2. No completed run or account migration claim.'),
               ('https://zombodotcom.github.io/d2survivors-releases/', 'GitHub Pages · zombodotcom project', 'Separate publisher and launcher; identity check, not an installation test.'),
               ('https://d2survivors.lol/wiki/getting-started/', 'D2 Survivors · original reference', 'Current camp/waypoint and file transition documentation; can differ from the observed playable build.')]
    src = ('<section class="sources" id="sources"><h2>Reference pages checked</h2><p>By Megabonk.org editors · 3 November 2026. This is an independent game guide, not a Blizzard or developer website. Reference pages from one project share one publisher. Version and test limits are stated on each task page.</p><ol>'
           + ''.join(f'<li id="source-{i}">{ext(u, l)} — {d}</li>' for i, (u, l, d) in enumerate(sources, 1))
           + '</ol><a href="#guide">Back to guide ↑</a></section>')
    body = f'<div class="d2-front">{hero}{tasks}</div>{versions}{updates}{grouped}{about}{faq}{src}'
    body = re.sub(r'(?<![>\w-])\[(\d+)\]', lambda x: f'<sup class="ref"><a href="#source-{x[1]}">[{x[1]}]</a></sup>', body)
    return shell(P, 'D2 Survivors Guides: Play, Setup, Skills & Saves',
                 'Find the right D2 Survivors edition, play in a browser window, prepare your game files and follow guides for starting, saving, Druid skills and speed stats.',
                 body, home=True).replace('original-menu-1280.webp', 'druid-select-1280.webp').replace('loading="lazy"', 'loading="eager"', 1)
