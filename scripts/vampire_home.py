"""Vampire Survivors 专区首页（SOP v3.25，08 F9）。

在已审核的 Demo 指南之上重排：英雄区+状态条、任务卡、数据预览、最新更新、分组入口、FAQ。
卡片、更新、分组、FAQ 与预览表全部来自 data/vampire-survivors-pages.json（02 §2.6）；导航、面包屑与页脚由
register_page.py 最后填充。H1、Title、description、canonical 与原 Demo 正文保持不变（00 §5A）。"""
import json
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = '/vampire-survivors/'

ICONS = {
    'play': '<path d="M8 5v14l11-7z"/>',
    'flame': '<path d="M12 3c1 4 5 5.5 5 10a5 5 0 0 1-10 0c0-2 1-3 2-4 .2 1.5 1 2 2 2-.5-3 0-5 1-8z"/>',
    'key': '<circle cx="8" cy="12" r="3.5"/><path d="M11.5 12H21m-3 0v3m-3-3v2"/>',
    'ring': '<circle cx="12" cy="12" r="7"/><circle cx="12" cy="12" r="3"/>',
    'grid': '<rect x="4" y="4" width="7" height="7"/><rect x="13" y="4" width="7" height="7"/><rect x="4" y="13" width="7" height="7"/><rect x="13" y="13" width="7" height="7"/>',
    'skull': '<path d="M5 11a7 7 0 0 1 14 0v3l-2 1v3H7v-3l-2-1z"/><circle cx="9.5" cy="11.5" r="1.3"/><circle cx="14.5" cy="11.5" r="1.3"/><path d="M11 18v-2m2 2v-2"/>',
    'box': '<path d="M4 8l8-4 8 4v8l-8 4-8-4z"/><path d="M4 8l8 4 8-4M12 12v8"/>',
    'mask': '<path d="M5 6c4 1.5 10 1.5 14 0v6c0 4-3 7-7 8-4-1-7-4-7-8z"/><path d="M9 11h1m4 0h1M9.5 15c1.5 1 3.5 1 5 0"/>',
    'users': '<circle cx="9" cy="9" r="3"/><path d="M3.5 19c.5-3 2.8-5 5.5-5s5 2 5.5 5"/><circle cx="17" cy="10" r="2.3"/><path d="M16 14.2c2.6.2 4.2 1.9 4.6 4.3"/>',
}


def manifest():
    m = json.loads((ROOT / 'data/vampire-survivors-pages.json').read_text(encoding='utf8'))
    m['by'] = {p['slug']: p for p in m['pages']}
    return m


def href(slug):
    return P + (slug + '/' if slug else '')


def blocks(m):
    """返回 (任务卡+预览, 更新+分组, FAQ) 三段 HTML。"""
    cards = ''
    for c in m['hub_cards']:
        anchor = ' id="unlocks"' if c['href'].endswith('/unlocks/') else ''
        cards += (f'<a class="vh-card"{anchor} href="{c["href"]}"><span class="vh-ico" aria-hidden="true">'
                  f'<svg viewBox="0 0 24 24">{ICONS[c["icon"]]}</svg></span><strong>{escape(c["title"])}</strong>'
                  f'<span class="vh-text">{escape(c["blurb"])}</span></a>')
    pv = m['preview']
    rows = ''.join('<tr>' + ''.join(f'<td>{escape(x)}</td>' for x in r) + '</tr>' for r in pv['rows'])
    preview = (f'<section class="vh-block vh-preview" id="recipes"><h2>{escape(pv["title"])}</h2>'
               '<div class="table-wrap" role="region" aria-label="Starting weapon recipes; scroll horizontally on small screens" tabindex="0"><table>'
               '<thead><tr><th scope="col">Weapon</th><th scope="col">Passive you need</th><th scope="col">Evolves into</th></tr></thead>'
               f'<tbody>{rows}</tbody></table></div><p class="vh-cap">{escape(pv["caption"])} '
               f'<a href="{href(pv["link"])}">Full recipe chart →</a></p></section>')
    tasks = ('<section class="vh-block" id="guides" aria-labelledby="progression-title"><h2 id="progression-title">Make the next run count.</h2>'
             '<p class="vh-lede">Pick the job you have right now. Every card opens a checked guide for the full game, or the original browser demo below.</p>'
             f'<div class="vh-cards">{cards}</div></section>') + preview

    updates = ''.join(
        f'<li><time datetime="{u["date"]}">{u["date"]}</time><a href="{href(u["slug"])}">{escape(m["by"][u["slug"]]["title"])}</a><span>{escape(u["text"])}</span></li>'
        for u in m['recent'])
    upd = f'<section class="vh-win" id="updates"><h2>Latest updates</h2><ul class="vh-updates">{updates}</ul></section>'
    groups = ''
    for g in m['groups']:
        links = ''.join(f'<li><a href="{href(s)}">{escape(m["by"][s]["title"])}</a></li>' for s in g['slugs'])
        groups += f'<div class="vh-group"><h3>{escape(g["label"])}</h3><p>{escape(g["text"])}</p><ul>{links}</ul></div>'
    grouped = f'<section class="vh-win" id="all-guides"><h2>All guides by task</h2><div class="vh-groups">{groups}</div></section>'

    faq_items = ''.join(
        f'<details><summary>{escape(f["q"])}</summary><p>{escape(f["a"])}</p>'
        f'<a class="more" href="{f["link"] if f["link"].startswith("#") else href(f["link"])}">'
        f'{"Jump to the answer" if f["link"].startswith("#") else "Full guide"} →</a></details>' for f in m['faq'])
    faq = f'<section id="faq"><h2>Quick answers</h2><div class="vh-faq">{faq_items}</div></section>'
    return tasks, upd + grouped, faq


def redesign(html):
    m = manifest()
    html = re.sub(r'<link rel="stylesheet" href="/assets/pokebonk/site\.css(?:\?v=[0-9a-f]+)?">\n?', '', html)
    html = html.replace('<link rel="stylesheet" href="/assets/vampire-survivors/theme.css">',
                        '<link rel="stylesheet" href="/assets/vampire-survivors/theme.css"><link rel="stylesheet" href="/assets/vampire-survivors/hub.css">')
    html = html.replace('class="guide-layout vs-theme vs-guide"', 'class="guide-layout vs-theme vs-hub"')
    html = re.sub(r'<section id="guides">.*?</section>', '', html, count=1, flags=re.S)  # 原“全部攻略”段由任务卡取代
    tasks, middle, faq = blocks(m)
    start = html.index('<header class="article-head"')
    end = html.index('</header>', start) + len('</header>')
    original = html[start:end]
    h1 = re.search(r'<h1>.*?</h1>', original, re.S)[0]
    status = ['Survival roguelite by poncle', 'Browser demo v0.2.4', 'Guides checked 5-10 Nov 2026', 'Unofficial fan guide']
    hero = f'''<header class="hub-hero" id="guide"><div class="hero-copy"><p class="eyebrow">INDEPENDENT GUIDES / PONCLE'S SURVIVAL ROGUELITE</p><p class="hub-name">Vampire<br><span>Survivors</span></p>{h1}<ul class="vh-status" aria-label="Game status">{''.join(f'<li>{s}</li>' for s in status)}</ul><p class="hero-intro">Try the original browser demo, find a weapon recipe, or plan the next unlock in your full-game save.</p><div class="hero-actions"><a class="button" href="/vampire-survivors/evolutions/">Find an evolution <span aria-hidden="true">→</span></a><a class="text-link" href="#demo">Open the browser demo <span aria-hidden="true">→</span></a></div><p class="hero-note">The web demo is the old v0.2.4 edition. Full-game progression and co-op have separate guides below.</p></div><figure class="hero-scene"><img src="/assets/vampire-survivors/demo-combat-800.webp" srcset="/assets/vampire-survivors/demo-combat-800.webp 800w, /assets/vampire-survivors/demo-combat-958.webp 958w" sizes="(max-width:900px) calc(100vw - 40px), 52vw" width="958" height="640" fetchpriority="high" alt="Antonio automatically whipping a bat in the original Vampire Survivors v0.2.4 browser demo"><figcaption><span>THE ORIGINAL BROWSER DEMO</span><span>v0.2.4 · opening captured 5 Nov 2026</span></figcaption></figure></header>'''
    html = html[:start] + hero + tasks + middle + html[end:]
    # 保留原 Demo 答案与引用，放在真实入口旁。
    answer = re.search(r'<div class="answer">(.*?)</div>', original, re.S)[1]
    html = html.replace('<section id="demo"><h2>Open the original demo</h2>',
                        '<section id="demo"><p class="eyebrow">TRY THE ORIGINAL</p><h2>Open the original demo</h2>' + answer, 1)
    html = html.replace('<strong>On this page</strong>', '<strong>Browser demo &amp; edition guide</strong>', 1)
    html = html.replace('<a href="#guides">Full-game progression guides</a>', '', 1)
    # FAQ 放在 Related choices 之前（仍在正文内、More games 之上）
    marker = '<section><h2>Related choices</h2>'
    if marker in html:
        html = html.replace(marker, faq + marker, 1)
    else:
        raise SystemExit('vampire_home: Related choices marker not found')
    return html
