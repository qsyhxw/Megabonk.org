"""Build the source-reviewed PokéPath game section."""
from html import escape
from pathlib import Path

from pokepath_pages import PAGES
from site_analytics import write_html

ROOT = Path(__file__).resolve().parents[1]
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
NAVIGATION = [
    ('Overview', '/pokepath/'),
    ('Teams', '/pokepath/best-pokemon/'),
    ('Mobile', '/pokepath/mobile/'),
    ('More games', '/#more-games'),
]


def build():
    for page in PAGES:
        route = '/pokepath/' + (page['slug'] + '/' if page['slug'] else '')
        navigation = ''.join(
            f'<a href="{url}"' + (' aria-current="page"' if url == route else '')
            + f'>{label}</a>' for label, url in NAVIGATION
        )
        source, width, height, alt, caption = MEDIA[page['image']]
        variants = ''
        if page['image'] == 'start':
            variants = ' srcset="/assets/pokepath/start-480.webp 480w, /assets/pokepath/start-800.webp 800w, /assets/pokepath/start-1280.webp 1280w" sizes="(max-width:800px) calc(100vw - 40px),800px"'
        image = f'<figure class="task-image {page["image"]}"><a href="{source}"><img src="{source}"{variants} width="{width}" height="{height}" alt="{alt}" loading="lazy"></a><figcaption>{caption}</figcaption></figure>'
        sections = []
        for position, (identifier, heading, body) in enumerate(page['sections']):
            media = image if position == 0 else ''
            sections.append(f'<section id="{identifier}"><h2>{heading}</h2>{body}{media}</section>')
        toc = ''.join(f'<a href="#{identifier}">{heading}</a>' for identifier, heading, _ in page['sections'])
        title = escape(page['title'], quote=True)
        description = escape(page['description'], quote=True)
        html = f'''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><meta name="description" content="{description}">
<link rel="canonical" href="https://megabonk.org{route}">
<meta property="og:type" content="article"><meta property="og:title" content="{title}">
<meta property="og:description" content="{description}"><meta property="og:url" content="https://megabonk.org{route}">
<meta property="og:image" content="https://megabonk.org{source}">
<link rel="icon" href="/favicon.ico">
<link rel="stylesheet" href="/assets/pokebonk/site.css">
<link rel="stylesheet" href="/assets/guide-article-layout.css">
<link rel="stylesheet" href="/assets/vampire-survivors/site.css">
<link rel="stylesheet" href="/assets/pokepath/site.css">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8830315294299920" crossorigin="anonymous"></script>
</head><body class="guide-layout vs-guide pokepath-guide">
<a class="skip" href="#main">Skip to content</a>
<header class="top"><div class="wrap"><a class="brand" href="/pokepath/"><span>PokéPath field guide<small>Megabonk.org · Independent player guides</small></span></a>
<nav class="desktop-nav" aria-label="PokéPath navigation">{navigation}</nav>
<details class="mobile-nav"><summary>Menu</summary><nav class="mobile-links" aria-label="PokéPath mobile navigation">{navigation}</nav></details></div></header>
<main id="main" class="wrap"><header class="article-head"><p>POKÉPATH TD · ROUTE TOWER DEFENSE</p>
<h1>{page['heading']}</h1><div class="answer"><p>{page['answer']}</p></div>
<p class="byline">Megabonk.org editors · Checked 9 November 2026 · Current play page 1.7.2</p></header>
<nav class="toc" aria-label="On this page">{toc}</nav>
<div class="article-layout"><article class="prose">{''.join(sections)}
<p><a href="/pokepath/">PokéPath guide index</a> · <a href="#main">Back to top ↑</a></p>
</article></div></main>
<footer class="footer"><div class="wrap footer-grid"><div><strong>Independent player guides</strong>
<p>PokéPath TD by Khydra. Pokémon names and artwork belong to their rights holders. This guide is independently published by Megabonk.org.</p>
<a href="/#more-games">More games →</a></div><nav aria-label="Site information"><a href="/about/">About</a><a href="/contact/">Contact</a><a href="/privacy-policy">Privacy</a></nav></div></footer>
</body></html>'''
        target = ROOT / route.lstrip('/') / 'index.html'
        target.parent.mkdir(parents=True, exist_ok=True)
        write_html(target, html, encoding='utf8')


if __name__ == '__main__':
    build()
