"""Midgard Survivors hub home (SOP v3.25, 08 F9): status line, task cards, download table, updates, grouped entries, FAQ.

Cards, groups, updates and FAQ come from data/midgard-survivors-pages.json (02 §2.6); nav, breadcrumbs and
footer are filled afterwards by register_page.py. H1, title and description of the original home are kept
(00 §5A: the page has stable clicks). Existing download/start/identity sections are reused unchanged."""
import json
from html import escape
from pathlib import Path

from bs4 import BeautifulSoup

from live_versions import value

ROOT = Path(__file__).resolve().parents[1]
P = '/midgard-survivors/'

ICONS = {
    'download': '<path d="M12 4v10m0 0-4-4m4 4 4-4M5 19h14"/>',
    'play': '<path d="M8 5.5v13l11-6.5z"/>',
    'phone': '<rect x="7" y="3" width="10" height="18" rx="2"/><path d="M11 18h2"/>',
    'laptop': '<rect x="5" y="5" width="14" height="10" rx="1.5"/><path d="M3 19h18"/>',
    'shield': '<path d="M12 3 5 6v5c0 4.5 3 7.7 7 10 4-2.3 7-5.5 7-10V6z"/>',
    'users': '<circle cx="9" cy="9" r="3"/><path d="M3.5 19c.5-3 2.8-5 5.5-5s5 2 5.5 5"/><circle cx="17" cy="10" r="2.3"/><path d="M16 14.2c2.6.2 4.2 1.9 4.6 4.3"/>',
    'search': '<circle cx="11" cy="11" r="6"/><path d="m16 16 4.5 4.5"/>',
}


def manifest():
    m = json.loads((ROOT / 'data/midgard-survivors-pages.json').read_text(encoding='utf8'))
    m['by'] = {p['slug']: p for p in m['pages']}
    return m


def href(slug):
    return P + (slug + '/' if slug else '')


def compose(main):
    """Rebuild the children of <main> from the article-style home; returns nothing (mutates the soup)."""
    m = manifest()
    soup = main.find_parent('[document]') or main
    figure = main.select_one('figure').extract()
    if figure.a:
        figure.a.unwrap()
    figure.img.attrs.pop('loading', None)
    figure.img['fetchpriority'] = 'high'
    figure['class'] = ['game-image']
    secs = {k: main.select_one('#' + k).extract() for k in ('download', 'start', 'identity', 'checks') if main.select_one('#' + k)}
    answer = main.select_one('.answer p').decode_contents()
    title = main.select_one('h1').decode_contents()

    cards = ''
    for c in m['hub_cards']:
        link = c.get('href') or href(c['slug'])
        cards += (f'<a class="mg-card{" wide" if c.get("wide") else ""}" href="{link}"><span class="mg-ico" aria-hidden="true">'
                  f'<svg viewBox="0 0 24 24">{ICONS[c["icon"]]}</svg></span><strong>{escape(c["title"])}</strong>'
                  f'<span class="mg-text">{escape(c["blurb"])}</span></a>')
    status = ['Free · Windows, Android, Mac, Linux', f'Client {value("midgard-client")}', 'Checked 12 Nov 2026', 'Unofficial fan guide']
    hero = (f'<div class="mg-hero"><div class="mg-copy"><p class="mg-kicker">nearQ · Ragnarok fan game · Guide &amp; downloads</p><h1>{title}</h1>'
            f'<p class="mg-deck">{answer}</p><ul class="mg-status" aria-label="Game status">'
            + ''.join(f'<li>{s}</li>' for s in status) + '</ul>'
            '<div class="mg-actions"><a class="mg-btn primary" href="#download">Choose your download</a>'
            f'<a class="mg-btn secondary" href="#guides">Find a guide ↓</a></div>'
            '</div>'
            f'<div class="mg-media">{figure}</div></div>')
    tasks = f'<section class="mg-tasks" id="guides"><h2>What are you trying to do?</h2><div class="mg-cards">{cards}</div></section>'

    updates = ''.join(
        f'<li><time datetime="{u["date"]}">{u["date"]}</time><a href="{href(u["slug"])}">{escape(m["by"][u["slug"]]["title"])}</a><span>{escape(u["text"])}</span></li>'
        for u in m['recent'])
    upd = f'<section class="mg-win" id="updates"><h2>Latest updates</h2><ul class="mg-updates">{updates}</ul></section>'
    groups = ''
    for g in m['groups']:
        links = ''.join(f'<li><a href="{href(s)}">{escape(m["by"][s]["title"])}</a></li>' for s in g['slugs'])
        links += ''.join(f'<li><a href="{x["href"]}">{escape(x["label"])}</a></li>' for x in g.get('extra', []))
        groups += f'<div class="mg-group"><h3>{escape(g["label"])}</h3><p>{escape(g["text"])}</p><ul>{links}</ul></div>'
    grouped = f'<section class="mg-win" id="all-guides"><h2>All guides by task</h2><div class="mg-groups">{groups}</div></section>'
    faq_items = ''.join(
        f'<details><summary>{escape(f["q"])}</summary><p>{escape(f["a"])}</p>'
        f'<a class="more" href="{f["link"] if f["link"].startswith("#") else href(f["link"])}">{"Jump to the answer" if f["link"].startswith("#") else "Full guide"} →</a></details>'
        for f in m['faq'])
    faq = f'<section class="mg-win" id="faq"><h2>FAQ</h2><div class="mg-faq">{faq_items}</div></section>'
    about = ('<section class="mg-win" id="about-game"><h2>About this guide</h2><p>Midgard Survivors is nearQ’s Ragnarok Online-inspired survivors-like: pick a class, '
             'let attacks fire on their own and carry equipment between runs. These pages follow the developer’s own site and itch.io listing, plus linked player discussions. '
             f'Read <a href="{P}about/">how the guide is sourced</a> or <a href="{P}contact/">report an outdated answer</a>.</p></section>')

    main.clear()
    body = [hero, tasks]
    for node in body:
        main.append(BeautifulSoup(node, 'html.parser'))
    order = [secs.get('download'), secs.get('start'), secs.get('identity'), secs.get('checks')]
    for sec in order:
        if sec is None:
            continue
        sec['class'] = ['mg-win'] + (['source-notes'] if sec.get('id') == 'checks' else [])
        main.append(sec)
    for node in (upd, grouped, faq, about):
        main.append(BeautifulSoup(node, 'html.parser'))
