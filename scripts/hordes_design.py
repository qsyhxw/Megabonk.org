"""Hordes of Azeroth hub home (SOP v3.25, 08 F9): hero with status chips, client-check strip, task cards, updates, grouped entries, FAQ.

Cards, groups, updates and FAQ come from data/hordes-of-azeroth-pages.json (02 §2.6); nav, breadcrumbs and the
footer are filled afterwards by register_page.py. H1, title and description of the existing home are kept
(00 §5A: the page has stable clicks). The reviewed article sections are reused unchanged as reading panels."""
import json
from html import escape
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
P = '/hordes-of-azeroth/'
RELEASE = 'https://github.com/jonhaldors/hordes-of-azeroth/releases'

ICONS = {
    'files': '<path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4M9 13h6M9 17h6"/>',
    'download': '<path d="M12 4v10m0 0-4-4m4 4 4-4M5 19h14"/>',
    'laptop': '<rect x="5" y="5" width="14" height="10" rx="1.5"/><path d="M3 19h18"/>',
    'users': '<circle cx="9" cy="9" r="3"/><path d="M3.5 19c.5-3 2.8-5 5.5-5s5 2 5.5 5"/><circle cx="17" cy="10" r="2.3"/><path d="M16 14.2c2.6.2 4.2 1.9 4.6 4.3"/>',
    'scales': '<path d="M12 4v16M7 20h10M5 8h14"/><path d="m5 8-3 6a3.5 3.5 0 0 0 6 0zM19 8l-3 6a3.5 3.5 0 0 0 6 0z"/>',
    'wrench': '<path d="M14.5 6.5a4 4 0 0 0-5 5L4 17l3 3 5.5-5.5a4 4 0 0 0 5-5l-2.5 2.5-2.5-.5-.5-2.5z"/>',
    'book': '<path d="M5 4h10a3 3 0 0 1 3 3v13H8a3 3 0 0 1-3-3z"/><path d="M5 17a3 3 0 0 1 3-3h10"/>',
}

# 客户端速查条：均为页面已有的作者 README 事实（2026-11-05 核对，v0.6.4）
GLANCE = [
    ('Client', 'WoW 1.12.1 · build 5875 · enUS'),
    ('Disk', 'About 3 GB free next to the game'),
    ('Platforms', 'Windows 10/11 · Linux beta · Mac unsupported'),
    ('Party', 'Solo or up to 4 players'),
]


def manifest():
    m = json.loads((ROOT / 'data/hordes-of-azeroth-pages.json').read_text(encoding='utf8'))
    m['by'] = {p['slug']: p for p in m['pages']}
    return m


def href(slug):
    return P + (slug + '/' if slug else '')


def adapt(html):
    """把文章式首页重排为 hub 布局；<main> 之外保持不变。"""
    start = html.index('<main ')
    end = html.index('</main>', start) + len('</main>')
    soup = BeautifulSoup(html[start:end], 'html.parser')
    main = soup.main
    m = manifest()
    img = BeautifulSoup(str(main.select_one('.hero img')), 'html.parser').img
    img.attrs.pop('loading', None)
    img['fetchpriority'] = 'high'
    keys = ('requirements', 'install', 'platforms', 'co-op', 'language', 'sources')
    secs = {k: main.select_one('#' + k).extract() for k in keys if main.select_one('#' + k)}
    # 安装截图 figure 在原文中位于 #install 之前、不在任何 section 内：随 #install 一起保留
    shot = main.select_one('figure[data-game-image]')
    if shot is not None and 'install' in secs:
        secs['install'].h2.insert_after(shot.extract())

    cards = ''
    for c in m['hub_cards']:
        link = c.get('href') or href(c['slug'])
        lang = f' lang="{c["lang"]}"' if c.get('lang') else ''
        cards += (f'<a class="hz-card{" wide" if c.get("wide") else ""}" href="{link}"{lang}><span class="hz-ico" aria-hidden="true">'
                  f'<svg viewBox="0 0 24 24">{ICONS[c["icon"]]}</svg></span><strong>{escape(c["title"])}</strong>'
                  f'<span class="hz-text">{escape(c["blurb"])}</span></a>')
    status = ['Free · fan project for WoW 1.12.1', 'v0.6.4', 'Checked 5 Nov 2026', 'Unofficial fan guide']
    hero = ('<div class="hz-hero"><div class="hz-copy"><p class="hz-kicker">Local survivors-like · Install &amp; platform guide</p><h1>Hordes of Azeroth</h1>'
            "<p class=\"hz-deck\">Survive a Warcraft-inspired horde, choose upgrades and return to the Inn. Start with <strong>jonhaldors's project on GitHub</strong> "
            'and your own compatible WoW client files. The game runs on a server on your PC.</p>'
            '<ul class="hz-status" aria-label="Game status">' + ''.join(f'<li>{s}</li>' for s in status) + '</ul>'
            '<div class="hz-actions"><a class="hz-btn primary" href="#requirements">Check your client first</a>'
            f'<a class="hz-btn secondary" href="{RELEASE}" target="_blank" rel="noopener noreferrer">Author releases ↗<span class="sr-only"> (opens in a new tab)</span></a></div></div>'
            f'<div class="hz-media"><figure class="game-image">{img}</figure></div></div>')
    glance = ('<dl class="hz-glance" aria-label="Client check at a glance">'
              + ''.join(f'<div><dt>{a}</dt><dd>{b}</dd></div>' for a, b in GLANCE) + '</dl>')
    tasks = f'<section class="hz-tasks" id="start"><h2>What are you trying to do?</h2><div class="hz-cards">{cards}</div></section>'

    updates = ''.join(
        f'<li><time datetime="{u["date"]}">{u["date"]}</time><a href="{href(u["slug"])}">{escape(m["by"][u["slug"]]["title"])}</a><span>{escape(u["text"])}</span></li>'
        for u in m['recent'])
    upd = f'<section class="hz-win" id="updates"><h2>Latest updates</h2><ul class="hz-updates">{updates}</ul></section>'
    groups = ''
    for g in m['groups']:
        links = ''.join(f'<li><a href="{href(s)}">{escape(m["by"][s]["title"])}</a></li>' for s in g['slugs'])
        links += ''.join(f'<li><a href="{x["href"]}">{escape(x["label"])}</a></li>' for x in g.get('extra', []))
        groups += f'<div class="hz-group"><h3>{escape(g["label"])}</h3><p>{escape(g["text"])}</p><ul>{links}</ul></div>'
    grouped = f'<section class="hz-win" id="all-guides"><h2>All guides by task</h2><div class="hz-groups">{groups}</div></section>'
    faq_items = ''.join(
        f'<details><summary>{escape(f["q"])}</summary><p>{escape(f["a"])}</p>'
        f'<a class="more" href="{f["link"] if f["link"].startswith("#") else href(f["link"])}">{"Jump to the answer" if f["link"].startswith("#") else "Full guide"} →</a></details>'
        for f in m['faq'])
    faq = f'<section class="hz-win" id="faq"><h2>FAQ</h2><div class="hz-faq">{faq_items}</div></section>'
    about = ("<section class=\"hz-win\" id=\"about-game\"><h2>About this guide</h2><p>Hordes of Azeroth is jonhaldors's survivors-style mode for World of Warcraft 1.12.1: "
             "spells fire on their own, every level-up offers a choice and the game runs on a small server on your PC. These pages follow the author's README and releases, plus named public reports. "
             f'Read <a href="{P}about/">how the guide is sourced</a> or <a href="{P}contact/">report an outdated answer</a>.</p></section>')

    main.clear()
    for node in (hero, glance, tasks):
        main.append(BeautifulSoup(node, 'html.parser'))
    for key in keys:
        sec = secs.get(key)
        if sec is None:
            continue
        sec['class'] = ['hz-win'] + (['source-notes'] if key == 'sources' else [])
        main.append(sec)
    for node in (upd, grouped, faq, about):
        main.append(BeautifulSoup(node, 'html.parser'))
    for table in main.select('table'):
        headings = [th.get_text(' ', strip=True) for th in table.select('thead th')]
        for row in table.select('tbody tr'):
            for cell, heading in zip(row.select('td'), headings):
                cell['data-label'] = heading
    return html[:start] + str(main) + html[end:]
