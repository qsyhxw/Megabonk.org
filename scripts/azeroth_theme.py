"""Azeroth Survivors game theme, manifest-driven hub and section trust pages
(SOP v3.22 02 §2.1, v3.24 02 §2.6, v3.25 02 §5.1-5.2, 08 F9).

Called last in build_azeroth_survivors.build() on each page's final HTML (after present()):
- every page loads /assets/azeroth-survivors/theme.css instead of the borrowed /assets/pokebonk/site.css
  and the old light /assets/azeroth-survivors/site.css; body gets az-theme + az-hub / az-guide;
- the hub <main> is rebuilt from data/azeroth-survivors-pages.json: status line, 8 task cards, the class
  tier preview (azeroth_answers.hub_block, data/azeroth-consensus-tier.json), latest updates, grouped
  guide index with the existing local search, short game intro and FAQ (visible answers feed FAQPage
  through data/game-seo.json);
- name-disambiguation, creator-credit and AI questions move from the hub to /azeroth-survivors/about/;
- inner pages drop their hand-written breadcrumbs and "Choose your next step" lists; nav, breadcrumbs,
  related guides and the section footer are then applied by scripts/register_page.py.
Title, meta description and canonical stay as published (00 §5A). The hub H1 becomes
"Azeroth Survivors Guide & Wiki" per 08 F9 (ROADMAP AZ-THEME).
"""
from html import escape
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
P = '/azeroth-survivors/'
A = '/assets/azeroth-survivors/'
THEME = A + 'theme.css'
HUB_CSS = A + 'hub.css'
OLD_CSS = ('/assets/pokebonk/site.css', A + 'site.css')
FONT = '<link rel="preload" href="/assets/fonts/cinzel-latin.woff2" as="font" type="font/woff2" crossorigin>'
EMAIL = 'contact@megabonk.org'
MOVED = ('which-game', 'made-with-ai', 'creator-credit')
_moved = {}


def manifest():
    return json.loads((ROOT / 'data/azeroth-survivors-pages.json').read_text(encoding='utf8'))


def _url(slug):
    return P + (slug + '/' if slug else '')


def _date(iso):
    y, m, d = iso.split('-')
    return ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][int(m) - 1] + ' ' + str(int(d))


def _observed():
    return json.loads((ROOT / 'data/azeroth-sync.json').read_text(encoding='utf8'))['observed']


def _icon(thumb, size, lazy=True):
    return (f'<img src="{A}icons/{thumb}" width="{size}" height="{size}" alt=""'
            + (' loading="lazy"' if lazy else '') + ' decoding="async">')


def theme(path, html):
    """One stylesheet set for hub, guides, trust pages and the section 404."""
    for old in OLD_CSS:
        html = re.sub(r'<link rel="stylesheet" href="' + re.escape(old) + r'(?:\?[^"]*)?">', '', html)
    if not re.search(r'href="' + re.escape(THEME) + r'(?:\?[^"]*)?"', html):
        html = re.sub(r'(<link rel="stylesheet" href="/assets/guide-article-layout\.css[^"]*">)',
                      lambda m: m[1] + f'<link rel="stylesheet" href="{THEME}">', html, count=1)
    assert THEME in html, path
    if FONT not in html:
        html = html.replace('</head>', FONT + '</head>', 1)
    cls = 'az-hub' if path == P else 'az-guide'
    def body(m):
        names = [c for c in m[2].split() if c not in ('az-theme', 'az-hub', 'az-guide')] + ['az-theme', cls]
        return f'<body{m[1]} class="{" ".join(names)}"'
    html = re.sub(r'<body([^>]*) class="([^"]*az[^"]*)"', body, html, count=1)
    assert 'az-theme' in html.split('<body', 1)[1].split('>', 1)[0], path
    # the brand subtitle describes this section only (02 §2.6); main-site ownership lives in the footer
    html = html.replace('<small>Megabonk.org · Independent guide</small>', '<small>Builds, talents &amp; wiki</small>')
    return html


def _section(html, sid):
    m = re.search(r'<section class="section" id="' + sid + r'"[^>]*>.*?</section>', html, re.S)
    out = m[0] if m else ''
    if sid == 'creator-credit':
        # the WoW Forever name note sits just before this section on the old hub
        note = re.search(r'<p id="forever-name-reservation">.*?</p>', html, re.S)
        out = (note[0] if note else '') + out
    return out


def _card(p):
    tag = f'<span class="az-card-tag">{escape(p["tag"])}</span>' if p.get('tag') else ''
    return (f'<a class="az-card" href="{_url(p["slug"])}"><span class="az-slot">{_icon(p["thumb"], 48, False)}</span>'
            f'<span class="az-card-text"><strong>{escape(p["title"])}</strong><small>{escape(p["blurb"])}</small></span>{tag}</a>')


def _faq_answer(a):
    from azeroth_answers import _tiers, _classes
    tiers = _tiers()
    if a == '{best_class}':
        s = [k.title() for k, r in tiers.items() if r['tier'] == 'S']
        x = [k.title() for k, r in tiers.items() if r['tier'] == 'A']
        return (f'{" and ".join(s)} are S tier in the current class rankings, followed by {", ".join(x)} in A tier. '
                'For a first clear, Paladin and Warrior are the most forgiving picks.')
    if a == '{warrior}':
        d = _classes()['warrior']
        r = d['routes'][0]
        return (f'Take the {r[0]} route: {r[1].replace(" → ", ", then ")}. Start with {d["start"]} and add the '
                f'{d["routes"][1][0]} branch ({d["routes"][1][1].replace(" → ", ", ")}) once it is unlocked.')
    return a


def hub_main(html, m):
    from azeroth_answers import hub_block
    pages = m['pages']
    by = {p['slug']: p for p in pages}
    o = _observed()
    search = re.search(r'<form id="guide-search".*?</form>(?:<noscript>.*?</noscript>)?', html, re.S)
    sync = re.search(r'<aside class="source-status[^"]*" id="source-sync".*?</aside>', html, re.S)
    figure = re.search(r'<figure class="game-image"[^>]*data-game-image="az-warrior".*?</figure>', html, re.S)
    cards = ''.join(_card(p) for p in sorted((p for p in pages if p.get('card')), key=lambda p: p['card']))
    updates = ''.join(f'<li><time datetime="{u["date"]}">{_date(u["date"])}</time><a href="{_url(u["slug"])}">{escape(u["text"])}</a></li>'
                      for u in m['updates'])
    groups = []
    for g in m['hub_groups']:
        rows = [p for p in pages if p.get('section') in g['sections'] and p['slug']]
        links = ''.join(f'<a href="{_url(p["slug"])}">{_icon(p["thumb"], 32) if p.get("thumb") else ""}'
                        f'<span><strong>{escape(p["title"])}</strong><small>{escape(p.get("blurb", ""))}</small></span></a>' for p in rows)
        groups.append(f'<section class="az-group"><h3>{escape(g["title"])}</h3><p>{escape(g["note"])}</p><div class="az-links">{links}</div></section>')
    langs = ' · '.join(f'<a href="{_url(p["slug"])}" lang="{p["lang"]}">{escape(p["title"])}</a>' for p in pages if p.get('lang'))
    faq = ''.join(f'<details class="az-faq"><summary>{escape(f["q"])}</summary><p>{escape(_faq_answer(f["a"]))}</p>'
                  f'<a class="az-more" href="{_url(f["link"])}">{escape(by[f["link"]]["title"])} →</a></details>' for f in m['faq'])
    return f'''<main id="main">
<section class="az-hero" id="guide"><img class="az-hero-bg" src="{A}images/azs-130-home-en-1280.webp" width="1280" height="889" alt="" aria-hidden="true" decoding="async" fetchpriority="high">
<div class="wrap az-hero-in">
<p class="az-status"><span class="az-badge">Unofficial</span><span>Free · browser &amp; Windows</span><span>Original v{escape(o["version"])}</span><span>Updated {_date(by[""]["updated"])}</span></p>
<h1>Azeroth Survivors Guide &amp; Wiki</h1>
<p class="az-lead">Class builds, the tier list, a talent planner and save help for <strong>Azeroth Survivors</strong>, Aethus’s free Warcraft-inspired horde survival game.</p>
<div class="az-actions"><a class="az-btn az-btn-play" href="{P}play/"><span aria-hidden="true">▶</span> Play &amp; start help</a><a class="az-btn" href="{P}builds/">Best builds</a></div>
</div></section>
<div class="wrap">
<nav class="az-cards" aria-label="Popular Azeroth Survivors guides">{cards}</nav>
{sync[0] if sync else ''}
<section class="az-band" id="classes">{hub_block()}</section>
<section class="az-band" id="latest"><div class="az-head"><h2>Latest updates</h2><p>Original client v{escape(o["version"])} detected {_date(o["date"])} · <a href="{P}patch-notes/">version status</a></p></div><ul class="az-updates">{updates}</ul></section>
<section class="az-band" id="guides"><div class="az-head"><h2>All Azeroth Survivors guides</h2><p>Every guide in this section, grouped by what you want to do next.</p></div>
{search[0] if search else ''}
<div class="az-groups">{''.join(groups)}</div></section>
<section class="az-band az-about" id="about-game"><div class="az-head"><h2>About the game</h2></div><p>Azeroth Survivors is a free horde-survival game by Aethus, set in a Warcraft-inspired world and played at wow.aethus.pl in a WebGPU browser or from a Windows download. You pick one of nine classes and a race, move through the crowd while your spells fire automatically, choose upgrade cards during the run and spend talent points and gear between runs. It is a separate fan project, not Blizzard’s World of Warcraft or Megabonk: <a href="{P}about/#which-game">games with similar names</a>.</p>{figure[0] if figure else ''}<p class="az-langs">Other languages: {langs}</p></section>
<section class="az-band" id="faq"><div class="az-head"><h2>Azeroth Survivors FAQ</h2><p>Short answers; each links to the full guide.</p></div>{faq}</section>
<p class="icon-credit" id="icon-credits">Class, spell and item icons come from the original game’s data and are shown to identify each entry.</p>
</div></main>'''


def about_body(o):
    return f'''<header class="article-head" id="guide"><p class="eyebrow">Azeroth Survivors · About</p><h1>About the Azeroth Survivors guides</h1>
<p class="meta">Megabonk.org editors · Reviewed 16 November 2026 · Original v{escape(o["version"])}</p></header>
<div class="article-layout"><article class="prose">
<section id="who"><h2>Who writes these guides</h2><p>This is an unofficial fan guide written by the editors of Megabonk.org, an independent site for survivors-style games. We are not Aethus, the creator of Azeroth Survivors, and we are not Blizzard Entertainment. Nothing here is an official announcement or game support. Class, spell and item names and icons belong to their owners and are shown to identify what each guide talks about.</p></section>
<section id="covers"><h2>What the section covers</h2><p>The guides answer the questions players hit between runs: which <a href="{P}builds/">talent route to build for each class</a>, where each class sits on the <a href="{P}tier-list/">tier list</a>, how <a href="{P}talents/">talent points and gates</a> work, how to plan points in the <a href="{P}build-planner/">build planner</a>, which <a href="{P}zones-bosses/">zone and boss</a> opens the next area, how <a href="{P}co-op/">co-op</a> rooms work, and how to <a href="{P}save-backup/">back up a save</a> or <a href="{P}troubleshooting/">fix a game that will not load</a>.</p></section>
<section id="sources"><h2>Where the answers come from</h2><ul>
<li><strong>The original game:</strong> class, talent, race and zone text is read from the original client at wow.aethus.pl as data, without running modified files. Talent menus, the Armory and the character screen are captured from the game itself; screenshots on each page say which version they show.</li>
<li><strong>Community rankings:</strong> the tier list averages three public class rankings and shows each source’s vote, so you can see where they disagree.</li>
<li><strong>The creator’s channels:</strong> download links and the community invite are the ones linked from the original launcher.</li>
</ul><p>When sources disagree, the page gives the answer the current client text supports and says which version it applies to.</p></section>
<section id="updates"><h2>How pages stay current</h2><p>A monitor reads the original client every six hours. The latest detected version is v{escape(o["version"])} ({escape(o["date"])}). When names, races or links change, the affected reference tables update automatically; when talents or mechanics change, the guides that depend on them show a status line until an editor rechecks them. See the <a href="{P}patch-notes/">version status page</a> for what changed.</p></section>
<div id="az-moved-slot"></div>
<section id="corrections"><h2>Found something wrong?</h2><p>Send the page address, your class and the game version shown in the bottom-right corner of the menu through the <a href="{P}contact/">contact page</a>. Corrections backed by a screenshot are usually applied in the next update.</p></section>
</article></div>'''


def contact_body():
    return f'''<header class="article-head" id="guide"><p class="eyebrow">Azeroth Survivors · Contact</p><h1>Contact the Azeroth Survivors guide editors</h1>
<p class="meta">Megabonk.org editors · Reviewed 16 November 2026</p></header>
<div class="article-layout"><article class="prose">
<section id="write"><h2>Email</h2><p>Write to <a href="mailto:{EMAIL}?subject=%5BAzeroth%20Survivors%5D%20Guide%20feedback">{EMAIL}</a>. Useful reports for this section:</p><ul>
<li>A class build or talent route that no longer works after an update;</li>
<li>A tier placement, zone unlock or boss that differs in your game;</li>
<li>A broken link, image or tool on an Azeroth Survivors page, including the build planner.</li></ul>
<p>Include the page address, your class and the version shown in the bottom-right corner of the game menu. A screenshot of the talent tree or tooltip helps us confirm the fix quickly.</p></section>
<section id="cannot"><h2>What we cannot help with</h2><p>We are not Aethus or game support, so we cannot restore saves, recover progress from another host or fix server problems. For those, use the community channel linked from the original launcher at <a href="https://wow.aethus.pl/" rel="noopener">wow.aethus.pl</a>; our <a href="{P}save-backup/">save backup guide</a> explains how to keep an export before you change browser or device. Do not send passwords or save files you need to keep private. There is no promised reply time.</p></section>
</article></div>'''


PRIVACY_NOTE = ('<p id="azeroth-survivors-trust">Updated 16 November 2026: the section now has its own About and Contact pages at '
                '/azeroth-survivors/about/ and /azeroth-survivors/contact/. Like the section error page, they load no advertising.</p>')


def privacy():
    f = ROOT / 'privacy-policy.html'
    if not f.exists():  # isolated test copies of the generator carry no site-level pages
        return None
    s = f.read_text(encoding='utf-8')
    if 'id="azeroth-survivors-trust"' in s:
        return None
    anchor = '<h3 id="azeroth-build-planner">'
    assert anchor in s
    return f, s.replace(anchor, PRIVACY_NOTE + anchor, 1)


def footer_404(html):
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from register_page import footer_html, load, nav_html
    m = load(ROOT, 'azeroth-survivors')
    nav = nav_html(m, '404')
    html = re.sub(r'(<nav class="(?:desktop-nav|mobile-links)"[^>]*>).*?(</nav>)', lambda x: x[1] + nav + x[2], html, flags=re.S)
    ends = list(re.finditer(r'<footer\b[^>]*>.*?</footer>', html, flags=re.S))
    return html[:ends[-1].start()] + footer_html(m) + html[ends[-1].end():]


def apply(path, html, shell=None):
    """Final pass for one page; returns the themed HTML."""
    m = manifest()
    slug = path.removeprefix(P).strip('/')
    if path == P:
        for sid in MOVED:
            _moved[sid] = _section(html, sid)
        head, rest = html.split('<main', 1)
        footer = '<footer' + rest.split('<footer', 1)[1]
        if HUB_CSS not in head:
            head = head.replace('</head>', f'<link rel="stylesheet" href="{HUB_CSS}"></head>', 1)
        html = head + hub_main(html, m) + footer
    elif path in (P + 'about/', P + 'contact/'):
        html = html.replace('<body data-format="other" ', '<body ', 1)  # trust pages carry no content format (08)
        if path == P + 'about/':
            assert _moved, 'hub must be processed before the About page'
            moved = ''.join(_moved[s] for s in MOVED).replace('class="section"', 'class="az-moved"')
            moved = moved.replace('The original character-menu screenshot shown on this page', f'The original character-menu screenshot on the <a href="{P}#about-game">guide home page</a>')
            html = html.replace('<div id="az-moved-slot"></div>', moved, 1)
    elif path.endswith('404.html'):
        html = footer_404(html)
    else:
        row = next((p for p in m['pages'] if p['slug'] == slug), None)
        if row and not row.get('plain') and '<header class="article-head"' in html:
            html = re.sub(r'<nav class="crumbs" aria-label="Breadcrumb">.*?</nav>', '', html, count=1, flags=re.S)
            html = re.sub(r'<section class="related"><h2>Choose your next step</h2>.*?</section>', '', html, flags=re.S)
    return theme(path, html)


def trust_pages(shell):
    """Section About / Contact (02 §5.1): no ads, same shell; built after the hub so moved sections exist."""
    o = _observed()
    return [
        (P + 'about/', shell(P + 'about/', 'About the Azeroth Survivors Guides | Megabonk.org',
                             'Who writes the unofficial Azeroth Survivors guides, where class, talent and zone answers come from and how pages are rechecked after updates.',
                             about_body(o), ads=False)),
        (P + 'contact/', shell(P + 'contact/', 'Contact the Azeroth Survivors Guide Editors | Megabonk.org',
                               'Report an outdated Azeroth Survivors build, talent route, tier placement or broken guide page, with what to include and what we cannot help with.',
                               contact_body(), ads=False)),
    ]
