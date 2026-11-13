"""PokeBonk game theme and manifest-driven hub (SOP v3.22 02 §2.1, v3.24 02 §2.6, 08 F9).

Runs last in build_pokebonk.build() on the in-memory PAGES:
- every page loads /assets/pokebonk/theme.css and gets body classes pb-theme + pb-hub / pb-guide;
- the hub <main> is rebuilt from data/pokebonk-pages.json: status line, task cards, top builds,
  latest updates, grouped guide index, short intro and FAQ (visible answers feed FAQPage via
  data/game-seo.json, one source);
- nav, breadcrumbs and related guides are applied afterwards by scripts/register_page.py.
Title, description and canonical stay as published (00 §5A; hub CTR experiment until 11-26). The hub H1
becomes "PokeBonk Guide & Wiki" per 08 F9 (recorded in ROADMAP).
"""
from html import escape
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
B = '/pokebonk/'
A = '/assets/pokebonk/'
THEME = '/assets/pokebonk/theme.css'
HUB_CSS = '/assets/pokebonk/hub.css'
PORTRAIT = A + 'portraits/{:03d}.png'
FONT = '<link rel="preload" href="/assets/fonts/mplus-rounded-800-latin.woff2" as="font" type="font/woff2" crossorigin>'


def manifest():
    return json.loads((ROOT / 'data/pokebonk-pages.json').read_text(encoding='utf8'))


def _url(slug):
    return B + (slug + '/' if slug else '')


def _date(iso):
    y, m, d = iso.split('-')
    return ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][int(m) - 1] + ' ' + str(int(d))


def theme(slug, html):
    """One theme for hub and every page; trust pages keep the shell but share the palette."""
    if THEME not in html:
        html = re.sub(r'(<link rel="stylesheet" href="/assets/guide-article-layout\.css[^"]*">)',
                      lambda m: m[1] + f'<link rel="stylesheet" href="{THEME}">', html, count=1)
    assert THEME in html, slug
    if FONT not in html:
        html = html.replace('</head>', FONT + '</head>', 1)
    cls = 'pb-theme pb-hub' if slug == '' else 'pb-theme pb-guide'
    return re.sub(r'<body([^>]*) class="pb-layout guide-layout([^"]*)"',
                  lambda m: f'<body{m[1]} class="pb-layout guide-layout{m[2]} {cls}"', html, count=1)


def _card(p, names):
    pid = p['portrait']
    return (f'<a class="pb-card" href="{_url(p["slug"])}"><span class="pb-card-icon"><img src="{PORTRAIT.format(pid)}" '
            f'width="56" height="56" alt="" decoding="async"></span><span class="pb-card-text"><strong>{escape(p["title"])}</strong>'
            f'<small>{escape(p["blurb"])}</small></span></a>')


def _top_builds():
    data = json.loads((ROOT / 'data/pokebonk-loadouts.json').read_text(encoding='utf8'))
    top = [x for x in data['loadouts'] if x['tier'] == 'S'][:3]
    from pokebonk_answers import _slug
    cards = ''.join(
        f'<a class="pb-build" href="{B}builds/#build-{_slug(x["name"])}"><img src="{PORTRAIT.format(x["id"])}" width="72" height="72" alt="{escape(x["name"])}" decoding="async">'
        f'<span><b class="pb-tier">S</b><strong>{escape(x["name"])}</strong>'
        f'<small>{" · ".join(escape(m["name"]) for m in x["moves"])}</small>'
        f'<small class="pb-fuse">{escape(x["fusion"]["name"]) if x["fusion"] else ""}{" · " if x["fusion"] else ""}{escape(x["items"][0]["name"])}</small></span></a>'
        for x in top)
    return data, top, cards


def best_build_answer():
    data, top, _ = _top_builds()
    x = top[0]
    return (f'Celebi is the top Season 3 pick: take {", ".join(m["name"] for m in x["moves"])}, fuse them into '
            f'{x["fusion"]["name"]} and add {", ".join(i["name"] for i in x["items"])}. '
            f'{", ".join(t["name"] for t in top[1:])} are the next S tier builds.') if x['name'] == 'Celebi' else (
            f'{x["name"]} is the top Season 3 pick: take {", ".join(m["name"] for m in x["moves"])} and add {", ".join(i["name"] for i in x["items"])}.')


def hub_main(m, version):
    pages = m['pages']
    by = {p['slug']: p for p in pages}
    cards = ''.join(_card(p, None) for p in sorted((p for p in pages if p.get('card')), key=lambda p: p['card']))
    data, top, builds = _top_builds()
    updates = ''.join(f'<li><time datetime="{u["date"]}">{_date(u["date"])}</time><a href="{_url(u["slug"])}">{escape(u["text"])}</a></li>'
                      for u in m['updates'])
    groups = []
    for g in m['hub_groups']:
        rows = [p for p in pages if p.get('section') in g['sections'] and p['slug']]
        links = ''.join(
            f'<a href="{_url(p["slug"])}"' + (f' lang="{p["lang"]}"' if p.get('lang') else '') + '>'
            + (f'<img src="{PORTRAIT.format(p["portrait"])}" width="32" height="32" alt="" loading="lazy" decoding="async">' if p.get('portrait') else '<span class="pb-lang" aria-hidden="true">' + p.get('lang', '').upper() + '</span>')
            + f'<span><strong>{escape(p["title"])}</strong><small>{escape(p.get("blurb", ""))}</small></span></a>' for p in rows)
        groups.append(f'<section class="pb-group"><h3>{escape(g["title"])}</h3><p>{escape(g["note"])}</p><div class="pb-links">{links}</div></section>')
    faq = ''.join(
        f'<details class="pb-faq"><summary>{escape(f["q"])}</summary><p>{escape(best_build_answer() if f["a"] == "{best_build}" else f["a"])}</p>'
        f'<a class="pb-more" href="{_url(f["link"])}">{escape(by[f["link"]]["title"])} →</a></details>' for f in m['faq'])
    return f'''<main id="main">
<section class="pb-hero" id="guide"><div class="wrap pb-hero-in">
<p class="pb-status"><span class="pb-badge">Unofficial</span><span>Free browser game</span><span>PC · Android · iPhone</span><span>Season 3 · v{escape(version)}</span><span>Updated {_date(m["pages"][0]["updated"])}</span></p>
<h1>PokeBonk Guide &amp; Wiki</h1>
<p class="pb-lead">Builds, tier list, Pokédex and fixes for <strong>PokeBonk</strong>, the free 3D Pokémon survivor you play in your browser.</p>
<div class="pb-actions"><a class="pb-btn pb-btn-red" href="{B}play/"><span aria-hidden="true">▶</span> Play here</a><a class="pb-btn pb-btn-light" href="https://pokebonk.com/?lang=en" target="_blank" rel="noopener noreferrer">pokebonk.com ↗</a></div>
</div><div class="pb-pano" aria-hidden="true"></div></section>
<div class="wrap">
<nav class="pb-cards" aria-label="Popular PokeBonk guides">{cards}</nav>
<section class="pb-band" id="top-builds"><div class="pb-head"><h2>Best builds right now</h2><p>{escape(data["tier_version"] if "tier_version" in data else "Season 3")} · four moves in order, fusion and first item</p></div>
<div class="pb-builds">{builds}</div><p class="pb-row-links"><a href="{B}builds/">All 48 S and A tier builds →</a><a href="{B}tier-list/">Full tier list →</a></p></section>
<section class="pb-band" id="latest"><div class="pb-head"><h2>Latest updates</h2><p>Game data v{escape(version)} · <a href="{B}updates/">patch changes</a></p></div><ul class="pb-updates">{updates}</ul></section>
<section class="pb-band" id="guides"><div class="pb-head"><h2>All PokeBonk guides</h2><p>Every guide on this site, grouped by what you want to do.</p></div>
<label class="guide-search">Find a guide <input id="guide-search" type="search" placeholder="Try fusion, Mewtwo, Survival or Lab"></label><p id="guide-search-status" role="status"></p><ul id="guide-results" hidden>{''.join(f'<li data-guide-search="{escape((p["title"] + " " + p.get("blurb", "") + " " + p["slug"]).lower(), quote=True)}"><a href="{_url(p["slug"])}">{escape(p["title"])}</a></li>' for p in pages if p['slug'] and p.get('section'))}</ul>
<div class="pb-groups">{''.join(groups)}</div></section>
<section class="pb-band pb-about" id="about-game"><div class="pb-head"><h2>About the game</h2></div><p>PokeBonk is a free, unofficial 3D horde-survival fan game by Charcher, played at pokebonk.com. You pick a Pokémon partner, level four moves during a run, fuse pairs into stronger moves and unlock more League partners between runs. Season 3 added Johto, bringing the League to 138 partners. It is a separate game from Megabonk: <a href="{B}megabonk-vs-pokebonk/">PokeBonk vs Megabonk</a>.</p></section>
<section class="pb-band" id="faq"><div class="pb-head"><h2>PokeBonk FAQ</h2><p>Short answers; each links to the full guide.</p></div>{faq}</section>
<p class="credit-note" id="portrait-credits">Pokémon images and names belong to Nintendo, Creatures Inc. and GAME FREAK Inc.; shown for identification. <a href="{B}contact/">Rights contact</a>.</p>
</div></main>'''


def apply_theme(ctx):
    m = manifest()
    version = json.loads((ROOT / 'data/pokebonk-sync.json').read_text(encoding='utf8'))['observed']['version']
    for path, page in ctx['PAGES'].items():
        slug = path.removeprefix(B).strip('/')
        s = page['html']
        if slug == '':
            head, rest = s.split('<main id="main"', 1)
            footer = '<footer' + rest.split('<footer', 1)[1]
            if HUB_CSS not in head:
                head = head.replace('</head>', f'<link rel="stylesheet" href="{HUB_CSS}"></head>', 1)
            head = head.replace('<link rel="stylesheet" href="/assets/pokebonk/tools.css">', '')
            s = head + hub_main(m, version) + footer
        row = next((p for p in m['pages'] if p['slug'] == slug), None)
        if slug and row and not row.get('plain') and '<header class="article-head"' in s:
            # Hand-written crumbs and "Continue exploring" lists give way to the manifest ones (register_page.py).
            s = re.sub(r'<nav class="crumbs" aria-label="Breadcrumb">.*?</nav>', '', s, count=1, flags=re.S)
            s = re.sub(r'<section class="related"><h2>Continue exploring</h2>.*?</section>', '', s, flags=re.S)
        page['html'] = theme(slug, s)
