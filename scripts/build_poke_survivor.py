"""Build the JPTER78 guide section from versioned editorial content.

The shared structural helpers and base CSS also serve PokeBonk. This generator
does not download, copy, host or execute any game code, and never rewrites the
integration expectations. Run the independent integration guard after building.
"""
from site_analytics import write_html
from pathlib import Path
from html import escape
import json
from build_pokebonk import ext, ref, table, section, source_list
from poke_survivor_content import make_pages, SOURCES
from poke_survivor_play import make_play_page
from poke_survivor_v320 import apply as apply_v320
from poke_survivor_theme import head_links, body_class, hub_main, manifest, footer_404, privacy as theme_privacy

ROOT=Path(__file__).resolve().parents[1]
BASE='https://megabonk.org'
P='/poke-survivor/'
A='/assets/poke-survivor/'
NAV=[('▶ Play',P+'play/'),('Start here',P+'beginners-guide/'),('Build checks',P+'builds/'),('Guides',P+'#guides'),('Mobile',P+'mobile/')]
ADS='<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8830315294299920" crossorigin="anonymous"></script>'

def navlinks(path):
    return ''.join(f'<a href="{url}"'+(' class="nav-play"' if url==P+'play/' else '')+(' aria-current="page"' if path==url else '')+f'>{label}</a>' for label,url in NAV)

def shell(path,title,desc,body,lang='en',kind='content',image='original-title-1280.webp'):
    alternate=''
    pairs=[('beginners-guide/','zh/beginners-guide/','zh-Hans'),('mobile/','es/mobile/','es')]
    for en,local,language in pairs:
        if path in [P+en,P+local]:
            alternate=''.join(f'<link rel="alternate" hreflang="{l}" href="{BASE+P+s}">' for l,s in [('en',en),(language,local),('x-default',en)])
    return f'''<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
{ADS if kind=='content' else ''}<title>{escape(title)}</title><meta name="description" content="{escape(desc,quote=True)}"><link rel="canonical" href="{BASE+path}">{alternate}
{('<meta name="robots" content="noindex,follow">' if kind=='error' else '')}
<meta property="og:type" content="website"><meta property="og:title" content="{escape(title,quote=True)}"><meta property="og:description" content="{escape(desc,quote=True)}"><meta property="og:url" content="{BASE+path}"><meta property="og:image" content="{BASE+A+image}"><meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{A}favicon.ico" sizes="any"><link rel="icon" href="{A}favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="{A}apple-touch-icon.png">{head_links(path==P)}</head><body{' data-format="hub"' if path==P else ''} class="{body_class(path)}">
<a class="skip" href="#main">Skip to content</a><header class="top"><div class="wrap"><a class="brand" href="{P}"><img src="{A}logo.svg" width="44" height="44" alt=""><span>PokéSurvivor<small>Guides &amp; wiki</small></span></a><nav class="desktop-nav" aria-label="Main navigation">{navlinks(path)}</nav><details class="mobile-nav"><summary>Menu <span aria-hidden="true">☰</span></summary><nav class="mobile-links" aria-label="Mobile navigation">{navlinks(path)}</nav></details></div></header>
{body if body.startswith('<main') else '<main class="wrap" id="main">'+body+'</main>'}<footer class="footer"><div class="wrap footer-grid"><div><strong>PokéSurvivor field guide</strong><p>Independent guides to JPTER78’s browser game. Not operated by the game creator or affiliated with Nintendo, Creatures, GAME FREAK or The Pokémon Company. Game images and names belong to their respective owners.</p><a href="/">Megabonk Wiki →</a> · <a href="/pokebonk/">PokeBonk guides →</a></div><nav aria-label="Site information"><a href="{P}about/">About</a><a href="{P}contact/">Contact</a><a href="{P}privacy/">Privacy</a></nav></div></footer></body></html>'''

def render(page):
    path=P+page['slug']; kind=page.get('kind','content')
    sources=source_list([SOURCES[key] for key in page['sources']]) if page['sources'] else ''
    links='<section class="related"><h2>Next useful guides</h2>'+''.join(f'<a href="{P+slug}">{label} →</a>' for slug,label in page.get('related',[]))+'</section>'
    if page.get('home'):
        body=hub_main(manifest())  # 08 F9 hub; old identity section moved to /poke-survivor/about/#which-game
    elif kind in ['trust','error']:
        body=f'<nav class="crumbs" aria-label="Breadcrumb"><a href="{P}">PokéSurvivor</a> / {page["h1"]}</nav><article class="legal" id="guide"><p class="eyebrow">Independent player guide</p><h1>{page["h1"]}</h1><p class="meta">Updated {page.get("updated","October 26, 2026")}</p>{page["body"]}{sources}</article>'
    else:
        toc_links=''.join(f'<a href="#{id}">{title}</a>' for id,title,_ in page['parts'])+('<a href="#sources">Sources</a>' if sources else '')
        toc=f'<aside class="toc" aria-label="On this page"><strong>On this page</strong>{toc_links}</aside>' if len(page['parts'])>=4 else ''
        diagram=f'<figure class="diagram"><img src="{A+page["diagram"]}.svg" width="1100" height="300" alt="{escape(page["diagram_alt"],quote=True)}"><figcaption>{page["diagram_caption"]}</figcaption></figure>' if page.get('diagram') else ''
        lead=f'<div class="answer-module">{page["lead"]}</div>' if page.get('lead') else ''
        updated=page.get('updated','October 26, 2026')
        tag='PokéSurvivor guide' if page.get('format') else 'JPTER78 browser game · Independent guide'
        body=f'<header class="article-head" id="guide"><span class="tag">{tag}</span><h1>{page["h1"]}</h1><p class="answer">{page["answer"]}</p><p class="meta">PokéSurvivor guide · Updated {updated}</p>{page.get("language","")}</header>{lead}<div class="article-layout"><article class="prose">{diagram}'+''.join(section(*part) for part in page['parts'])+sources+'</article>'+toc+'</div>'
    image=page.get('image') or (page['diagram']+'.png' if page.get('diagram') else 'original-title-1280.webp')
    html=shell(path,page['title'],page['desc'],body,page.get('lang','en'),kind,image)
    if page.get('format'):  # 08 page format for the content gate
        html=html.replace('<body class="',f'<body data-format="{page["format"]}" class="',1)
    return path,html

def build():
    pages=apply_v320(make_pages())  # /xiufu 2026-11-16: v3.20 page formats (scripts/poke_survivor_v320.py)
    for page in pages:
        path,html=render(page)
        file=ROOT/(path.lstrip('/')+'index.html') if page.get('kind')!='error' else ROOT/'poke-survivor/404.html'
        file.parent.mkdir(parents=True,exist_ok=True);write_html(file, html,encoding='utf-8')
    play=ROOT/'poke-survivor/play/index.html'
    play.parent.mkdir(parents=True,exist_ok=True)
    write_html(play, make_play_page(shell),encoding='utf-8')
    # v3.25: site-level Privacy keeps a PokéSurvivor section; the section footer links to its anchor
    pv=theme_privacy()
    if pv:write_html(pv[0],pv[1],encoding='utf-8')
    # v3.24/v3.25: nav, breadcrumbs, related guides, footer and registries from data/poke-survivor-pages.json
    import subprocess,sys
    subprocess.run([sys.executable,str(Path(__file__).resolve().parent/'register_page.py'),str(ROOT),'poke-survivor'],check=True,stdout=subprocess.DEVNULL)
    err=ROOT/'poke-survivor/404.html'
    err.write_text(footer_404(err.read_text(encoding='utf-8')),encoding='utf-8')
    # register_page appends BreadcrumbList after the FAQ script; re-run the SEO editor so its output stays last (idempotent).
    from game_seo import edit as edit_seo
    for f in (ROOT/'poke-survivor').rglob('*.html'):
        t=f.read_text(encoding='utf8');n=edit_seo(f,t)
        if n!=t:f.write_text(n,encoding='utf8')
    print(json.dumps([dict(slug=p['slug'],title_length=len(p['title']),description_length=len(p['desc']),kind=p.get('kind','content')) for p in pages],ensure_ascii=False,indent=2))

if __name__=='__main__':build()
