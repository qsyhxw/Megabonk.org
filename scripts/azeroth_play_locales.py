"""Localized original-host play journeys and reciprocal language discovery."""
from html import escape
import json
from pathlib import Path
from play_recommendations import recommendations, stylesheet
from azeroth_survivors_play import P

ROOT = Path(__file__).resolve().parents[1]
COPY = json.loads((ROOT / 'data/azeroth-play-locales.json').read_text(encoding='utf8'))


def route(lang):
    return P + ('zh-hant' if lang == 'zh-Hant' else lang) + '/play/'


def language_links():
    links = '<a href="'+P+'play/" lang="en" hreflang="en">English</a>'
    for lang, copy in COPY.items():
        links += '<a href="'+route(lang)+'" lang="'+lang+'" hreflang="'+lang+'">'+copy['name']+'</a>'
    return '<nav class="play-languages" aria-label="Language / Sprache / 語言" data-play-background>'+links+'</nav>'


def alternatives(html):
    paths = [('en', P+'play/')] + [(lang,route(lang)) for lang in COPY]
    tags = ''.join('<link rel="alternate" hreflang="'+lang+'" href="https://megabonk.org'+path+'">' for lang,path in paths)
    tags += '<link rel="alternate" hreflang="x-default" href="https://megabonk.org'+P+'play/">'
    return html.replace('</head>', tags+'</head>', 1)


def localize_shell(html, lang):
    c = COPY[lang]
    labels = ['Skip to content','Independent guide','Main navigation','Menu','Mobile navigation','A guide for your next run.',
              'Independent editorial by Megabonk.org. Azeroth Survivors is by Aethus. Not affiliated with Aethus or Blizzard Entertainment. Menu and source-text research is labelled; no gameplay benchmark is claimed.',
              'Megabonk Wiki →','About','Contact','Privacy']
    for old,new in zip(labels,c['shell']):
        html = html.replace(old,new)
    for old,new in zip(['▶ Play','Start here','Builds','Guides','Help'],c['nav']):
        html = html.replace('>'+old+'</a>','>'+new+'</a>')
    html = html.replace('href="'+P+'play/" class="nav-play"','href="'+route(lang)+'" class="nav-play" aria-current="page"')
    return html


def localized_pages(shell, ext):
    pages = []
    for lang, copy in COPY.items():
        body = language_links()
        body += '<header class="article-head" id="guide"><h1>'+copy['h1']+'</h1><div class="answer"><p>'+copy['intro']+'</p></div><p class="meta">Megabonk.org · '+copy['sources']+'</p><div class="actions">'+ext('https://wow.aethus.pl/',copy['original'])+'</div></header>'
        body += '<div class="article-layout"><aside class="toc" aria-label="'+copy['sections'][0]+'">'
        for anchor, title in zip(['start','loading','edition','sources'],copy['sections']):
            body += '<a href="#'+anchor+'">'+title+'</a>'
        body += '</aside><article class="prose">'
        for anchor, key, title in [('start','start',copy['sections'][0]),('loading','loading',copy['sections'][1]),('edition','saves',copy['sections'][2])]:
            body += '<section id="'+anchor+'"><h2>'+title+'</h2>'
            if key == 'start':
                body += '<ol>'+''.join('<li>'+text+'</li>' for text in copy[key])+'</ol>'
            else:
                body += ''.join('<p>'+text+'</p>' for text in copy[key])
            body += '<p><sup class="ref"><a href="#source-1">[1]</a></sup> <sup class="ref"><a href="#source-2">[2]</a></sup></p></section>'
        body += '<p><a href="/privacy-policy#azeroth-survivors-guides">'+copy['privacy']+'</a> · <a href="'+P+'play/" lang="en">English · 5 Nov 2026</a></p>'
        body += '<section class="sources" id="sources"><h2>'+copy['sections'][3]+'</h2><ol><li id="source-1">'+ext('https://wow.aethus.pl/rogue.js?v=f3a3d645a1ed','Aethus · rogue.js')+' — '+copy['source_host']+'</li><li id="source-2">'+ext('https://wow.aethus.pl/','Aethus · wow.aethus.pl')+' — '+copy['source_original']+'</li></ol><a href="#guide">'+copy['back']+'</a></section>'
        body += '<section class="related"><h2>'+copy['next']+'</h2>'
        for slug, label in zip(['beginners-guide/','troubleshooting/','save-backup/'],copy['related']):
            body += '<a href="'+P+slug+'" lang="en">'+label+' →</a>'
        body += '</section></article></div>'+recommendations('azeroth-survivors',lang)
        html = shell(route(lang),copy['title'],copy['description'],body,lang=lang)
        html = html.replace('class="az guide-layout"','class="az guide-layout localized-play"',1)
        html = html.replace('</head>','<link rel="stylesheet" href="/assets/azeroth-survivors/play.css"></head>',1)
        pages.append((route(lang),alternatives(stylesheet(localize_shell(html,lang)))))
    return pages


def connect_languages(path,html):
    if path==P+'play/':
        html = html.replace('<header class="article-head"',language_links()+'<header class="article-head"',1)
        return alternatives(html)
    if path==P:
        marker='<section class="section" id="language-start">'
        html = html.replace(marker,marker+'<p>Play help in your language</p>'+language_links(),1)
    return html
