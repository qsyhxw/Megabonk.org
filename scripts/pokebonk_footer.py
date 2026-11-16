"""PokeBonk section footer and trust links (SOP v3.25, 02 §5.1-5.2).

- The footer itself comes from data/pokebonk-pages.json ("footer" block) via scripts/register_page.py.
- footer_404(): the section 404 page is not a manifest row, so it gets the same nav and footer here.
- privacy_section(): the site-level /privacy-policy gets a #pokebonk section, the footer's Privacy anchor.
  The section notice is still assembled by the build modules but is published only as that section;
  /pokebonk/privacy/ itself redirects there (functions/pokebonk/[[path]].js, _redirects).
- about_body() / contact_body(): section About and Contact text with the current game version.
Run from build_pokebonk.py after register_page.py.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = '/pokebonk/'
REVIEWED = 'November 16, 2026'


def observed():
    d = json.loads((ROOT / 'data/pokebonk-sync.json').read_text(encoding='utf8'))
    when = d.get('changed_at', '')[:10]
    if when:
        y, mo, da = when.split('-')
        months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        when = f'{months[int(mo) - 1]} {int(da)}, {y}'
    return d['observed']['version'], when


def about_body(ext):
    version, when = observed()
    return (
        '<p>This PokeBonk section is an unofficial player guide published by the editors of Megabonk.org, an independent site for survivors-style games. '
        'It is not run by the game’s developer and is not game support.</p>'
        '<h2 id="who">Who owns the game?</h2><p>PokeBonk is a free fan game led by Charcher and played at pokebonk.com. This guide is not affiliated with Charcher, Nintendo, The Pokémon Company, Creatures or GAME FREAK. '
        'Pokémon names and game images belong to their respective rights holders. Our seed-compass mark identifies this guide, not the game.</p>'
        '<h2 id="covers">What this section covers</h2><p>'
        f'<a href="{P}builds/">Copyable builds</a>, the <a href="{P}build-planner/">build planner</a> and <a href="{P}move-fusions/">move fusions</a>; '
        f'the <a href="{P}tier-list/">tier list</a> and <a href="{P}starters/">starter choice</a>; reference data in the <a href="{P}pokemon/">Pokédex</a>, '
        f'<a href="{P}evolution/">evolution levels</a>, <a href="{P}type-chart/">type chart</a> and <a href="{P}lab/">Lab costs</a>; '
        f'run help such as the <a href="{P}beginners-guide/">beginner guide</a>, <a href="{P}how-to-catch-pokemon/">catching partners</a> and <a href="{P}mewtwo/">Mewtwo</a>; '
        f'and platform questions on <a href="{P}mobile/">mobile</a>, <a href="{P}multiplayer/">co-op</a> and <a href="{P}troubleshooting/">loading problems</a>.</p>'
        '<h2 id="sources">Where the answers come from</h2><ul>'
        '<li><strong>The public game client:</strong> partner kits, moves, items, Lab costs and type multipliers are read from the game data that pokebonk.com loads in the browser, without running a modified game.</li>'
        '<li><strong>The game’s own update notes and menus:</strong> version changes, events and modes are checked against the in-game update notes and menu screens.</li>'
        f'<li><strong>The original project’s public pages:</strong> {ext("https://pokebonk.com/legal", "the legal and credits notice")} and its linked community channels for ownership, accounts and support.</li>'
        '</ul><p>A value in the game data is not a measured win rate or a device test. Pages keep dates and versions next to the answers, and we do not label something as tested when it was not.</p>'
        f'<h2 id="current">How pages stay current</h2><p>A monitor reads the public game client every six hours. The latest version it detected is <strong>v{version}</strong>'
        + (f' ({when})' if when else '') +
        f'. Reference tables update once new data passes validation; changes that cannot be validated automatically keep the last reviewed data until an editor checks them. See <a href="{P}updates/">patch changes</a> for what the current version changes.</p>'
        f'<h2 id="corrections">Corrections and image requests</h2><p>Send the page URL, the detail that is wrong, the game version you see and a screenshot or public source through the <a href="{P}contact/">contact page</a>. Rights holders can use the same address for image or content requests.</p>'
        f'<p><a href="{P}#guides">Browse all guides →</a></p>')


def contact_body(ext, mail):
    return (
        f'<p>For this guide’s corrections, broken links, source updates or image requests, email <a href="{mail}">contact@megabonk.org</a>.</p>'
        '<h2 id="report">What you can report</h2><ul>'
        '<li>A build, starter pick or tier placement that no longer works after a game update;</li>'
        '<li>A wrong number for a move, evolution level, type multiplier, item or Lab cost;</li>'
        '<li>Event, mode or capture requirements that changed in game;</li>'
        '<li>A broken link, image, guide search result or the Play window failing to load.</li></ul>'
        '<h2 id="details">Help us check the right detail</h2><ul><li>The guide URL and the sentence or image concerned.</li><li>The game version and date if a mechanic changed.</li><li>A public project announcement, screenshot or other source that supports the correction.</li></ul>'
        '<p>There is no on-site submission form. Your email provider opens when you select the address. We do not promise a response time.</p>'
        f'<h2 id="support">Game accounts and support</h2><p>We cannot reset passwords, restore Guests, resolve suspensions or inspect the game’s database. For game support use {ext("https://discord.gg/X7KusQqx8X", "the original project’s Discord")}, linked from the original website. Never send us game passwords or authentication data.</p>'
        f'<h2 id="personal">Personal information</h2><p>Only include details needed to explain the issue. See the <a href="{PRIVACY_ANCHOR}">privacy notice</a> for how contact email and this website are handled.</p>')


PRIVACY_ANCHOR = '/privacy-policy#pokebonk'
# headings of the section notice that are PokeBonk-specific; delivery, ads choices, contact email and
# Umami are already covered by the site-level policy above this section
KEEP = ('Scripts and browser storage', 'Third-party game window', 'External websites', 'Optional local build drafts',
        'Additional local planning tools', 'Unified declared drafts', 'Upgrade logs, Lab targets and private attempt notes')


def privacy_html(notice):
    """Turn the generated section notice (PAGES['/pokebonk/privacy/'] html) into the #pokebonk section."""
    art = re.search(r'<article\b.*?</article>', notice, flags=re.S).group(0)
    parts = re.split(r'(?=<h2\b)', art)
    body = []
    for part in parts[1:]:
        m = re.match(r'<h2\b([^>]*)>(.*?)</h2>', part, flags=re.S)
        title = re.sub(r'<[^>]+>', '', m.group(2)).strip()
        if title not in KEEP:
            continue
        rest = part[m.end():].replace('</article>', '')
        # the site-level policy is the "separate notice" this paragraph pointed to
        rest = re.sub(r'<p>Other Megabonk\.org pages use .*?</p>', '', rest, flags=re.S)
        hid = ' id="pokebonk-game-window"' if 'id="game-window"' in m.group(1) else ''
        body.append(f'<h3{hid}>{title}</h3>{rest}')
    intro = ('<p>Reviewed ' + REVIEWED + '. This part covers the PokeBonk guide section at megabonk.org/pokebonk/. It is separate from the privacy policy of the original game at pokebonk.com. '
             'The home page and ordinary guide pages load this domain’s existing Google AdSense code; the section’s About and Contact pages and its error page load no advertising. '
             'The site-wide Umami analytics, Cloudflare hosting, advertising choices and contact email terms described above apply.</p>')
    return '<section id="pokebonk"><h2>PokeBonk guides</h2>' + intro + ''.join(body) + '</section>'


def privacy_section(notice):
    """Return (path, new_text) when the #pokebonk section of /privacy-policy differs from the notice, else None."""
    f = ROOT / 'privacy-policy.html'
    if not f.exists():
        return None
    s = f.read_text(encoding='utf-8')
    sec = privacy_html(notice)
    if '<section id="pokebonk">' in s:
        n = re.sub(r'<section id="pokebonk">.*?</section>', lambda _: sec, s, count=1, flags=re.S)
    else:
        assert '</body>' in s
        n = s.replace('</body>', sec + '</body>', 1)
    return None if n == s else (f, n)


def footer_404(html):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from register_page import footer_html, load, nav_html
    m = load(ROOT, 'pokebonk')
    nav = nav_html(m, '404')
    html = re.sub(r'(<nav class="(?:desktop-nav|mobile-links)"[^>]*>).*?(</nav>)', lambda x: x[1] + nav + x[2], html, flags=re.S)
    ends = list(re.finditer(r'<footer\b[^>]*>.*?</footer>', html, flags=re.S))
    return html[:ends[-1].start()] + footer_html(m) + html[ends[-1].end():]
