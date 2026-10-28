"""Build the JPTER78 guide section from versioned editorial content.

The shared structural helpers and base CSS also serve PokeBonk. This generator
does not download, copy, host or execute any game code, and never rewrites the
integration expectations. Run the independent integration guard after building.
"""
from pathlib import Path
from html import escape
import json
from build_pokebonk import ext, ref, table, section, source_list
from poke_survivor_content import make_pages, SOURCES
from poke_survivor_play import make_play_page

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
<link rel="icon" href="{A}favicon.ico" sizes="any"><link rel="icon" href="{A}favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="{A}apple-touch-icon.png"><link rel="stylesheet" href="{A}site.css"><link rel="preload" href="/assets/pokebonk/pixelify-700.ttf" as="font" type="font/ttf" crossorigin><link rel="stylesheet" href="/assets/guide-article-layout.css"></head><body class="guide-layout">
<a class="skip" href="#main">Skip to content</a><header class="top"><div class="wrap"><a class="brand" href="{P}"><img src="{A}logo.svg" width="44" height="44" alt=""><span>PokéSurvivor<small>Independent guides · Megabonk.org</small></span></a><nav class="desktop-nav" aria-label="Main navigation">{navlinks(path)}</nav><details class="mobile-nav"><summary>Menu <span aria-hidden="true">☰</span></summary><nav class="mobile-links" aria-label="Mobile navigation">{navlinks(path)}</nav></details></div></header>
<main class="wrap" id="main">{body}</main><footer class="footer"><div class="wrap footer-grid"><div><strong>PokéSurvivor field guide</strong><p>Independent guides to JPTER78’s browser game. Not operated by the game creator or affiliated with Nintendo, Creatures, GAME FREAK or The Pokémon Company. Game images and names belong to their respective owners.</p><a href="/">Megabonk Wiki →</a> · <a href="/pokebonk/">PokeBonk guides →</a></div><nav aria-label="Site information"><a href="{P}about/">About</a><a href="{P}contact/">Contact</a><a href="{P}privacy/">Privacy</a></nav></div></footer></body></html>'''

def render(page):
    path=P+page['slug']; kind=page.get('kind','content')
    sources=source_list([SOURCES[key] for key in page['sources']]) if page['sources'] else ''
    links='<section class="related"><h2>Next useful guides</h2>'+''.join(f'<a href="{P+slug}">{label} →</a>' for slug,label in page.get('related',[]))+'</section>'
    if page.get('home'):
        body=page['body']+sources
    elif kind in ['trust','error']:
        body=f'<nav class="crumbs" aria-label="Breadcrumb"><a href="{P}">PokéSurvivor</a> / {page["h1"]}</nav><article class="legal" id="guide"><p class="eyebrow">Independent player guide</p><h1>{page["h1"]}</h1><p class="meta">Updated October 26, 2026</p>{page["body"]}{sources}</article>'
    else:
        toc='<aside class="toc" aria-label="On this page"><strong>On this page</strong>'+''.join(f'<a href="#{id}">{title}</a>' for id,title,_ in page['parts'])+'<a href="#sources">Sources</a></aside>'
        diagram=f'<figure class="diagram"><img src="{A+page["diagram"]}.svg" width="1100" height="300" alt="{escape(page["diagram_alt"],quote=True)}"><figcaption>{page["diagram_caption"]}</figcaption></figure>'
        body=f'<nav class="crumbs" aria-label="Breadcrumb"><a href="{P}">PokéSurvivor</a> / {page["h1"]}</nav><header class="article-head" id="guide"><span class="tag">JPTER78 browser game · Independent guide</span><h1>{page["h1"]}</h1><p class="answer">{page["answer"]}</p><p class="meta">By Megabonk.org editors · Checked October 26, 2026 · Source-based; no comparative gameplay test</p>{page.get("language","")}</header><div class="article-layout"><article class="prose">{diagram}'+''.join(section(*part) for part in page['parts'])+sources+links+'</article>'+toc+'</div>'
    return path,shell(path,page['title'],page['desc'],body,page.get('lang','en'),kind,page.get('diagram','original-title-1280.webp')+'.png' if page.get('diagram') else 'original-title-1280.webp')

def build():
    pages=make_pages()
    for page in pages:
        path,html=render(page)
        file=ROOT/(path.lstrip('/')+'index.html') if page.get('kind')!='error' else ROOT/'poke-survivor/404.html'
        file.parent.mkdir(parents=True,exist_ok=True);file.write_text(html,encoding='utf-8')
    play=ROOT/'poke-survivor/play/index.html'
    play.parent.mkdir(parents=True,exist_ok=True)
    play.write_text(make_play_page(shell),encoding='utf-8')
    print(json.dumps([dict(slug=p['slug'],title_length=len(p['title']),description_length=len(p['desc']),kind=p.get('kind','content')) for p in pages],ensure_ascii=False,indent=2))

if __name__=='__main__':build()
