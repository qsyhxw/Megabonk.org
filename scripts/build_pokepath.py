"""Build the source-reviewed PokéPath game section (SOP v3.26：主题 pp-theme、首页按 F9、清单驱动导航/页脚）。

正文仍来自 pokepath_pages.py（内容不变）；外壳只输出空的 nav/footer 占位，
由最后一步 register_page.py 按 data/pokepath-pages.json 填充（02 §2.6、§5.2）。
"""
import json
import subprocess
import sys
from html import escape
from pathlib import Path

from pokepath_pages import PAGES
from site_analytics import write_html

ROOT = Path(__file__).resolve().parents[1]
BASE = '/pokepath/'
A = '/assets/pokepath/'
MEDIA = {
    'start': ('/assets/pokepath/start-800.webp', 1280, 720,
              'PokéPath TD profile creation with Charmander selected over Route 1-1',
              'Original 1.7.2 client, captured 9 November 2026 at profile creation.'),
    'route-1-3': ('/assets/pokepath/route-1-3-480.webp', 480, 416,
                    'PokéPath TD Route 1-3 graveyard path with water along the bottom',
                    'Original Route 1-3 terrain from the project wiki, checked 9 November 2026. Unit placements are not shown.'),
    'pumpkaboo': ('/assets/pokepath/pumpkaboo-original.png', 128, 128,
                 'Pumpkaboo artwork from the original PokéPath TD unlock guide',
                 'Pumpkaboo reward artwork from the original unlock guide, labelled 1.7.0. Checked 9 November 2026.'),
    'excadrill': ('/assets/pokepath/excadrill-original.png', 475, 475,
                 'Excadrill, the armor-focused pick in the PokéPath TD role shortlist',
                 'Excadrill artwork from the original PokéPath Pokédex, checked 9 November 2026.'),
}
HOME_PAGE = PAGES[0]


def manifest():
    m = json.loads((ROOT / 'data/pokepath-pages.json').read_text(encoding='utf8'))
    m['by'] = {p['slug']: p for p in m['pages']}
    return m


def figure(name):
    source, width, height, alt, caption = MEDIA[name]
    variants = ''
    if name == 'start':
        variants = ' srcset="/assets/pokepath/start-480.webp 480w, /assets/pokepath/start-800.webp 800w, /assets/pokepath/start-1280.webp 1280w" sizes="(max-width:800px) calc(100vw - 40px),800px"'
    return (f'<figure class="task-image {name}"><a href="{source}"><img src="{source}"{variants} width="{width}" height="{height}" '
            f'alt="{alt}" loading="lazy"></a><figcaption>{caption}</figcaption></figure>')


def section_html(page):
    return {key: (title, body) for key, title, body in page['sections']}


def homepage():
    from hub_components import Hub
    m = manifest()
    h = Hub(m, BASE, 'pp', '/assets/pokepath', thumb_dir='')
    sec = section_html(HOME_PAGE)
    pv = m['preview']
    bg = ''
    hero = h.hero(
        kicker='Independent player guides · Route tower defense', title='PokéPath TD ', sub='game &amp; player guides',
        deck='Choose a starter, place your Pokémon along a route and fix the wave that keeps beating you: team roles, save transfer, Route 1-3 and reward codes.',
        status=['Browser · Free', 'Play page 1.7.2', 'Checked 9 Nov 2026', 'Unofficial fan guide'],
        actions=[('Pick a guide ↓', '#guides', False), ('Open the game', '#play', True)], bg_attr=bg)
    cards = h.cards(heading='Pick the job you have right now', bg_attr=bg)
    cheat = h.cheat(pv['title'], pv['intro'], pv['rows'], bg_attr=bg)
    play_title, play_body = sec['play']
    start_title, start_body = sec['start']
    version_title, version_body = sec['version']
    play = (f'<section class="pp-band pp-start" id="play"><div class="pp-start-grid"><div><h2>{play_title}</h2>{play_body}</div>'
            f'<div>{figure(HOME_PAGE["image"])}</div></div></section>')
    start = f'<section class="pp-band" id="start"><h2>{start_title}</h2>{start_body}</section>'
    version = f'<section class="pp-band" id="version"><h2>{version_title}</h2>{version_body}</section>'
    body = hero + cards + cheat + play + start + h.updates(bg_attr=bg) + h.groups(bg_attr=bg) + version + h.faq(bg_attr=bg)
    return f'<main class="wrap" id="main">{body}</main>', h.faq_questions()


def shell(route, page, body_cls, extra_css, main, og_type='article'):
    title = escape(page['title'], quote=True)
    description = escape(page['description'], quote=True)
    source = MEDIA[page.get('image', 'start')][0]
    return f'''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><meta name="description" content="{description}">
<link rel="canonical" href="https://megabonk.org{route}">
<meta property="og:type" content="{og_type}"><meta property="og:title" content="{title}">
<meta property="og:description" content="{description}"><meta property="og:url" content="https://megabonk.org{route}">
<meta property="og:image" content="https://megabonk.org{source}">
<link rel="icon" href="/favicon.ico">
<link rel="preload" href="/assets/fonts/pixelify-sans-700.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/guide-article-layout.css">
<link rel="stylesheet" href="{A}theme.css">{extra_css}
</head><body class="guide-layout pp-theme {body_cls}">
<a class="skip" href="#main">Skip to content</a>
<header class="top"><div class="wrap"><a class="brand" href="{BASE}" aria-label="PokéPath TD guide home"><span>Poké<b>Path</b> TD<small>Guides &amp; route help</small></span></a>
<nav class="desktop-nav" aria-label="PokéPath navigation"></nav>
<details class="mobile-nav"><summary>Menu</summary><nav class="mobile-links" aria-label="PokéPath mobile navigation"></nav></details></div></header>
{main}
<footer class="footer"></footer>
</body></html>'''


def ads(html):
    """普通内容页保留站点既有 AdSense 加载器；信任页不放。"""
    tag = '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8830315294299920" crossorigin="anonymous"></script>'
    return html.replace('</head>', tag + '</head>', 1)


def task_main(page):
    sections = []
    for position, (identifier, heading, body) in enumerate(page['sections']):
        media = figure(page['image']) if position == 0 else ''
        sections.append(f'<section id="{identifier}"><h2>{heading}</h2>{body}{media}</section>')
    toc = ''.join(f'<a href="#{identifier}">{heading}</a>' for identifier, heading, _ in page['sections'])
    return (f'<main class="wrap" id="main"><header class="article-head" id="guide"><p class="eyebrow">PokéPath TD · Route tower defense</p>'
            f'<h1>{page["heading"]}</h1><div class="answer"><p>{page["answer"]}</p></div>'
            f'<p class="byline">Megabonk.org editors · Checked 9 November 2026 · Current play page 1.7.2</p></header>'
            f'<div class="article-layout"><nav class="toc" aria-label="On this page">{toc}</nav><article class="prose">{"".join(sections)}'
            f'<p><a href="#guide">Back to top ↑</a></p></article></div></main>')


def build():
    questions = []
    for page in PAGES:
        route = BASE + (page['slug'] + '/' if page['slug'] else '')
        if page['slug'] == '':
            main, questions = homepage()
            html = shell(route, page, 'pp-hub', f'<link rel="stylesheet" href="{A}hub.css">', main, 'website')
        else:
            html = shell(route, page, 'pp-guide', '', task_main(page))
        html = ads(html)
        target = ROOT / route.strip('/') / 'index.html'
        target.parent.mkdir(parents=True, exist_ok=True)
        write_html(target, html, encoding='utf8')
    from pokepath_trust import build as build_trust
    build_trust(shell)
    privacy()
    subprocess.run([sys.executable, str(Path(__file__).resolve().parent / 'register_page.py'), str(ROOT), 'pokepath'], check=True, stdout=subprocess.DEVNULL)
    register_seo(questions)
    from game_seo import edit as seo_edit  # register_page 追加头部标记后，保持 SEO 编辑器幂等
    for fp in (ROOT / 'pokepath').rglob('index.html'):
        t0 = fp.read_text(encoding='utf8')
        n0 = seo_edit(fp, t0)
        if n0 != t0:
            fp.write_text(n0, encoding='utf8')
    print('Built PokéPath home, 4 task pages and About/Contact')


def register_seo(questions):
    """首页 FAQ 登记到 data/game-seo.json（可见问答与 FAQPage 同源），信任页补进 pages_list.txt（只追加）。"""
    f = ROOT / 'data/game-seo.json'
    d = json.loads(f.read_text(encoding='utf8'))
    d['pages']['pokepath/index.html'] = {
        'questions': list(questions),
        'faq_review': 'Hub FAQ from data/pokepath-pages.json (v3.26 F9); visible answers and FAQPage share one source (2026-11-22).',
        'language_review': 'English task; no equivalent language task established.',
        'reviewed_candidates': list(questions),
    }
    new = json.dumps(d, ensure_ascii=False, indent=2) + '\n'
    if f.read_text(encoding='utf8') != new:
        f.write_text(new, encoding='utf8')
    pl = ROOT / 'pages_list.txt'
    text = open(pl, encoding='utf8', newline='').read()
    add = ''.join(f'https://megabonk.org{BASE}{s}/\r\n' for s in ('about', 'contact') if f'{BASE}{s}/' not in text)
    if add:
        with open(pl, 'a', encoding='utf8', newline='') as out:
            out.write(add)


def privacy():
    """站级隐私页为本专区保留一节（02 §5.1），已有则不重复。"""
    f = ROOT / 'privacy-policy.html'
    s = open(f, encoding='utf8', newline='').read()
    if 'id="pokepath"' in s:
        return
    section = ('<h2 id="pokepath">PokéPath TD guides</h2><p>Reviewed 22 November 2026. These pages host no game client, account or save and embed no third-party game window. '
               'Links to pokepath.gg, its wiki and community threads open the destination site in a new tab only when you click them, and that site then applies its own privacy practices. '
               'Ordinary guide pages inherit this site’s existing AdSense loader and site-wide Umami analytics described here; About and Contact carry no advertising. '
               'Cloudflare hosting and possible performance measurement are described above.</p>')
    marker = '<h2 id="revenant-survivors">'
    if marker not in s:
        raise SystemExit('privacy-policy.html: marker section not found')
    with open(f, 'w', encoding='utf8', newline='') as out:  # 保持原 CRLF，不经 write_html 重排
        out.write(s.replace(marker, section + marker, 1))


if __name__ == '__main__':
    build()
