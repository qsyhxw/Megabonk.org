"""Brotato 专区首页块（SOP v3.26，08 F9）。

任务卡、数据预览、最新更新、分组入口、FAQ 全部来自 data/brotato-pages.json（02 §2.6）；导航、面包屑与页脚由
register_page.py 最后填充。H1、Title、description 与原首页的安装/排错/购买正文保持不变（00 §5A），
只在其前后补齐 F9 要求的首屏状态、任务卡、预览、更新、分组与 FAQ。"""
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = '/brotato/'
ASSET = '/assets/brotato/images/'


def manifest():
    m = json.loads((ROOT / 'data/brotato-pages.json').read_text(encoding='utf8'))
    m['by'] = {p['slug']: p for p in m['pages']}
    return m


def href(slug):
    return slug if slug.startswith('#') else P + (slug + '/' if slug else '')


def hero(figure_html):
    status = ['Arena shooter roguelite by Blobfish', 'PC · Primal Dread DLC out', 'Checked 18 Nov 2026', 'Unofficial fan guide']
    sts = ''.join(f'<li>{escape(s)}</li>' for s in status)
    return (f'<header class="hub-hero" id="guide"><div class="hero-copy"><p class="eyebrow">INDEPENDENT GUIDES / PRIMAL DREAD FIELD NOTES</p>'
            '<p class="hub-name">Brotato<span>Guide &amp; Wiki</span></p><h1>Make the next shop count.</h1>'
            f'<ul class="bh-status" aria-label="Game status">{sts}</ul>'
            '<p class="hero-intro">Choose an Evolution path, plan a character and get your co-op session ready.</p>'
            '<div class="hero-actions"><a class="button" href="#setup">Check your DLC setup <span aria-hidden="true">→</span></a>'
            f'<a class="text-link" href="{P}evolution/">Mecha or Mutation? <span aria-hidden="true">→</span></a></div>'
            '<p class="hero-note">Primal Dread is available on PC. Console and mobile versions are announced for early 2027, '
            'with no exact day confirmed in the checked publisher briefing.</p></div>'
            f'<div class="hero-scene">{figure_html}</div></header>')


def blocks(m):
    """返回 (任务卡+预览, 更新+分组, FAQ) 三段 HTML。"""
    cards = ''
    for i, c in enumerate(m['hub_cards']):
        cards += (f'<li><a class="bh-card" href="{escape(href(c["href"]), quote=True)}"><img src="{ASSET}{c["thumb"]}-480.webp" '
                  f'width="480" height="270" alt="" loading="{"eager" if i < 4 else "lazy"}"><span class="bh-card-body">'
                  f'<strong>{escape(c["title"])}</strong><span class="bh-card-text">{escape(c["blurb"])}</span></span></a></li>')
    pv = m['preview']
    head = ''.join(f'<th scope="col">{escape(h)}</th>' for h in pv['head'])
    rows = ''.join('<tr>' + ''.join(f'<td>{escape(x)}</td>' for x in r) + '</tr>' for r in pv['rows'])
    preview = (f'<section class="bh-block bh-preview" id="preview"><h2>{escape(pv["title"])}</h2>'
               '<div class="table-wrap" role="region" aria-label="Evolution choice table; scroll horizontally on small screens" tabindex="0"><table>'
               f'<thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div><p class="bh-cap">{escape(pv["caption"])} '
               f'<a href="{href(pv["link"])}">Full Evolution guide →</a></p></section>')
    tasks = ('<section class="bh-block" id="guides" aria-labelledby="tasks-title"><h2 id="tasks-title">Pick the task in front of you</h2>'
             '<p class="bh-lede">Every card opens a checked guide for the current game, or the setup check on this page.</p>'
             f'<ul class="bh-cards">{cards}</ul></section>') + preview

    updates = ''.join(
        f'<li><time datetime="{u["date"]}">{u["date"]}</time><a href="{href(u["slug"])}">{escape(m["by"][u["slug"]]["title"].split(" — ")[0])}</a><span>{escape(u["text"])}</span></li>'
        for u in m['recent'])
    upd = f'<section class="bh-win" id="updates"><h2>Latest updates</h2><ul class="bh-updates">{updates}</ul></section>'
    groups = ''
    for g in m['groups']:
        links = ''.join(f'<li><a href="{href(s)}">{escape(m["by"][s]["title"])}</a></li>' for s in g['slugs'])
        groups += f'<div class="bh-group"><h3>{escape(g["label"])}</h3><p>{escape(g["text"])}</p><ul>{links}</ul></div>'
    grouped = f'<section class="bh-win" id="all-guides"><h2>All guides by task</h2><div class="bh-groups">{groups}</div></section>'

    faq_items = ''.join(
        f'<details><summary>{escape(f["q"])}</summary><p>{escape(f["a"])}</p>'
        f'<a class="more" href="{escape(href(f["link"]), quote=True)}">{"Jump to the answer" if f["link"].startswith("#") else "Full guide"} →</a></details>'
        for f in m['faq'])
    faq = f'<section class="bh-win" id="faq"><h2>Quick answers</h2><div class="bh-faq">{faq_items}</div></section>'
    return tasks, upd + grouped, faq
