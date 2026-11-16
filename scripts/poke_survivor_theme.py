"""PokéSurvivor game theme, manifest-driven hub and section trust pages
(SOP v3.22 02 §2.1, v3.24 02 §2.6, v3.25 02 §5.1-5.2, 08 F9).

Used by build_poke_survivor.py:
- shell() loads /assets/poke-survivor/theme.css (no borrowed /assets/pokebonk/site.css any more) and
  gives <body> ps-theme + ps-hub / ps-guide;
- hub_main() renders the hub <main> from data/poke-survivor-pages.json: game-panel hero with the
  status line, 8 task cards with the original game's menu icons, a run-clock data preview, latest
  updates, grouped guide index, short game intro and FAQ (visible answers feed FAQPage through
  data/game-seo.json);
- the old hub's game-identity section now lives on /poke-survivor/about/#which-game;
- nav, breadcrumbs, related guides and the section footer are applied afterwards by
  scripts/register_page.py (footer_404() does the same for the section 404, which is not a manifest row).
Title, meta description and canonical of the hub stay as published (00 §5A); the hub H1 becomes
"PokéSurvivor Guide & Wiki" per 08 F9 (ROADMAP PS-THEME).
"""
from html import escape
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
P = '/poke-survivor/'
A = '/assets/poke-survivor/'
THEME = A + 'theme.css'
HUB_CSS = A + 'hub.css'
FONT = '<link rel="preload" href="/assets/fonts/pixelify-sans-700.woff2" as="font" type="font/woff2" crossorigin>'
MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


def manifest():
    return json.loads((ROOT / 'data/poke-survivor-pages.json').read_text(encoding='utf8'))


def _url(slug):
    path, _, frag = slug.partition('#')
    return P + (path + '/' if path else '') + ('#' + frag if frag else '')


def _date(iso):
    y, m, d = iso.split('-')
    return MONTHS[int(m) - 1] + ' ' + str(int(d))


def _icon(thumb, size, lazy=True):
    return (f'<img src="{A}{thumb}" width="{size}" height="{size}" alt=""'
            + (' loading="lazy"' if lazy else '') + ' decoding="async">')


def head_links(home=False):
    """Stylesheets and font preload for every section page (02 §2.1); hub.css only on the hub."""
    return (f'<link rel="stylesheet" href="/assets/guide-article-layout.css"><link rel="stylesheet" href="{THEME}">'
            + (f'<link rel="stylesheet" href="{HUB_CSS}">' if home else '') + FONT)


def body_class(path, extra=''):
    return ' '.join(x for x in ['guide-layout', extra, 'ps-theme', 'ps-hub' if path == P else 'ps-guide'] if x)


def _card(p):
    return (f'<a class="ps-card" href="{_url(p["slug"])}"><span class="ps-slot">{_icon(p["thumb"], 36, False)}</span>'
            f'<span class="ps-card-text"><strong>{escape(p["title"])}</strong><small>{escape(p["blurb"])}</small></span></a>')


def run_clock():
    """Real data preview (08 F9): the timeline of one run, from the creator's guide and the dated source snapshot."""
    stops = [
        ('2:00', 'First calendar boss', 'Again at 6, 10, 14 and 18 minutes; each one drops a held item.'),
        ('4:00', 'First rift', 'Also at 8, 12 and 16: beat the legendary for a ×10 ticket and a bond.'),
        ('20:00', 'Eternamax Eternatus', 'Win for a power, a ×10 ticket and 600 PokéCoins.'),
        ('25:00', 'Last rift', 'Gives a bond only if you missed an earlier one.'),
        ('30:00', 'Judgment of Arceus', 'Unbeatable: survive and deal damage; it breaks an item at +2, +4 and +6 minutes.'),
    ]
    items = ''.join(f'<li><time>{t}</time><strong>{escape(a)}</strong><span>{escape(b)}</span></li>' for t, a, b in stops)
    return f'''<section class="ps-band ps-panel ps-clock" id="run-clock"><h2>A PokéSurvivor run on the clock</h2>
<p>The run schedule since the 13 November 2026 update, from the game’s own guides.</p>
<ol class="ps-timeline">{items}</ol>
<div class="ps-facts"><p><b>Level 20 &amp; 40</b>Choose to evolve your partner or keep its look.</p><p><b>Ten-pull</b>10 ordinary tickets or one ×10 ticket.</p><p><b>Co-op</b>Up to 4 players from the Friends menu.</p></div>
<a class="ps-more" href="{P}arceus-judgment/">Plan the Judgment of Arceus →</a></section>'''


def hub_main(m):
    pages = m['pages']
    by = {p['slug']: p for p in pages}
    cards = ''.join(_card(p) for p in sorted((p for p in pages if p.get('card')), key=lambda p: p['card']))
    updates = ''.join(f'<li><time datetime="{u["date"]}">{_date(u["date"])}</time><a href="{_url(u["slug"])}">{escape(u["text"])}</a></li>'
                      for u in m['updates'])
    groups = []
    for g in m['hub_groups']:
        rows = [p for p in pages if p.get('section') in g['sections'] and p['slug']]
        links = ''.join(f'<a href="{_url(p["slug"])}">{_icon(p["thumb"], 28)}'
                        f'<span><strong>{escape(p["title"])}</strong><small>{escape(p.get("blurb", ""))}</small></span></a>' for p in rows)
        groups.append(f'<section class="ps-group"><h3>{escape(g["title"])}</h3><p>{escape(g["note"])}</p><div class="ps-links">{links}</div></section>')
    langs = ' · '.join(f'<a href="{_url(p["slug"])}" lang="{p["lang"]}">{escape(p["title"])}</a>' for p in pages if p.get('lang'))
    faq = ''.join(f'<details class="ps-faq"><summary>{escape(f["q"])}</summary><p>{escape(f["a"])}</p>'
                  f'<a class="ps-more" href="{_url(f["link"])}">{escape(by[f["link"].split("#")[0]]["title"])} →</a></details>' for f in m['faq'])
    return f'''<main id="main">
<section class="ps-hero" id="guide"><img class="ps-hero-bg" src="{A}images/title-field-1440.webp" srcset="{A}images/title-field-800.webp 800w, {A}images/title-field-1440.webp 1440w" sizes="100vw" width="1440" height="900" alt="" aria-hidden="true" decoding="async" fetchpriority="high">
<div class="wrap"><div class="ps-panel ps-hero-panel">
<p class="ps-status"><span class="ps-badge">Unofficial</span><span>Free</span><span>Browser, PC &amp; mobile</span><span>Updated {_date(by[""]["updated"])}, 2026</span></p>
<h1>PokéSurvivor Guide &amp; Wiki<small>Mystery Dungeon · by JPTER78</small></h1>
<p class="ps-lead">Controls, move builds, tickets, rifts, phone play and save help for <strong>PokéSurvivor</strong>, the free browser game where your Pokémon partner survives the hordes.</p>
<div class="actions"><a class="ps-btn ps-btn-play" href="{P}play/"><span aria-hidden="true">▶</span> Play online</a><a class="ps-btn" href="{P}beginners-guide/">First-run guide</a></div>
</div></div></section>
<div class="wrap">
<nav class="ps-cards" aria-label="Popular PokéSurvivor guides">{cards}</nav>
{run_clock()}
<section class="ps-band" id="latest"><div class="ps-head"><h2>Latest updates</h2><p>What changed in the game and in these guides</p></div><ul class="ps-updates">{updates}</ul></section>
<section class="ps-band" id="guides"><div class="ps-head"><h2>All PokéSurvivor guides</h2><p>Every guide in this section, grouped by what you want to do next.</p></div>
<div class="ps-groups">{''.join(groups)}</div></section>
<section class="ps-band ps-about" id="about-game"><h2>About the game</h2><div><p>PokéSurvivor is a free survival game by JPTER78 that you play in a browser on PC or phone at pokesurvivor.com. You pick a Pokémon partner, roam a top-down field while your active move fires on its own, and choose a card each level: a new move, an upgrade or a boost. Between runs you spend tickets in the gacha, collect partners and team up with up to three friends. It is a fan project, separate from PokeBonk and from the Megabonk Steam game; see <a href="{P}about/#which-game">games with similar names</a>.</p><p class="ps-langs">Other languages: {langs}</p></div>
<figure><img src="{A}images/login-panel-440.webp" width="440" height="460" loading="lazy" decoding="async" alt="PokéSurvivor login panel titled Mystery Dungeon, naming pokesurvivor.com as the official website, with Log in and Sign up tabs"></figure></section>
<section class="ps-band" id="faq"><div class="ps-head"><h2>PokéSurvivor FAQ</h2><p>Short answers; each links to the full guide.</p></div>{faq}</section>
<p class="icon-credit" id="icon-credits">Task icons are the original game’s own menu icons and the hero background is its title screen, shown to identify each section.</p>
</div></main>'''


def footer_404(html):
    """The section 404 is not a manifest row: give it the manifest nav and section footer."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from register_page import footer_html, load, nav_html
    m = load(ROOT, 'poke-survivor')
    nav = nav_html(m, '404')
    html = re.sub(r'(<nav class="(?:desktop-nav|mobile-links)"[^>]*>).*?(</nav>)', lambda x: x[1] + nav + x[2], html, flags=re.S)
    ends = list(re.finditer(r'<footer\b[^>]*>.*?</footer>', html, flags=re.S))
    return html[:ends[-1].start()] + footer_html(m) + html[ends[-1].end():]


PRIVACY_ANCHOR = '<section id="poke-survivor">'
PRIVACY_SECTION = ('<section id="poke-survivor"><h2>PokéSurvivor guides (/poke-survivor/)</h2>'
                   '<p>The PokéSurvivor hub and ordinary guides load this website’s Google AdSense code; the section About, Contact, Privacy notice and error pages do not. '
                   'Fonts, icons and screenshots are hosted on megabonk.org. The <a href="/poke-survivor/play/">Play page</a> loads a third-party edition from pokesurvivor.pro only after you press Play; '
                   'from then on that provider and the services it calls apply their own practices, and its sign-in and guest features are not run by Megabonk.org. '
                   'The full section notice, including the services the embedded game requests, is on the <a href="/poke-survivor/privacy/">PokéSurvivor privacy notice</a>.</p></section>')


def privacy():
    """Site-level Privacy keeps one section per game hub (02 §5.1); the section footer links to its anchor."""
    f = ROOT / 'privacy-policy.html'
    if not f.exists():
        return None
    s = f.read_text(encoding='utf-8')
    if PRIVACY_ANCHOR in s:
        return None
    anchor = '<section id="warhammer-survivors">'
    assert anchor in s
    return f, s.replace(anchor, PRIVACY_SECTION + anchor, 1)
