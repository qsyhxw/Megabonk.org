"""Answer-first modules for the PokeBonk section (v3.20, SOP 08 F2/F3/F9).

Rendered from data/pokebonk-consensus-tier.json and data/pokebonk-loadouts.json and
inserted directly under the article header, so the page answers the query in the
first screen. Existing detailed sections stay below as the explanation.
"""
from pathlib import Path
from html import escape
import json
import re

ROOT = Path(__file__).resolve().parents[1]
PORTRAIT = '/assets/pokebonk/portraits/{:03d}.png'
TYPE_COLOR = {
    'normal': '#9a9a7a', 'fire': '#e8733a', 'water': '#4a8fe0', 'grass': '#5aa84a', 'electric': '#e6b927',
    'ice': '#6cc3d0', 'fighting': '#b3413b', 'poison': '#9a4fa0', 'ground': '#c8a25a', 'flying': '#8a9be8',
    'psychic': '#e8578a', 'bug': '#94a52a', 'rock': '#ad9a4a', 'ghost': '#6a5a9a', 'dragon': '#6a4fe0',
    'dark': '#6a5848', 'steel': '#9aa2b0', 'fairy': '#e08ac8', 'status': '#8a8a8a',
}
TIER_LABEL = {'S': 'Best picks', 'A': 'Strong', 'B': 'Solid', 'C': 'Situational'}


def _load(name):
    return json.loads((ROOT / 'data' / name).read_text(encoding='utf8'))


def _slug(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower().replace('♀', 'f').replace('♂', 'm')).strip('-')


def _img(pid, name, size):
    return (f'<img src="{PORTRAIT.format(pid)}" width="{size}" height="{size}" alt="{escape(name)}" '
            f'loading="lazy" decoding="async">')


def _type_chip(t):
    return f'<span class="type-chip" style="--tc:{TYPE_COLOR.get(t, "#888")}">{escape(t.title())}</span>'


def tier_grid():
    data = _load('pokebonk-consensus-tier.json')
    rows = data['rows']
    built = {x['name'] for x in _load('pokebonk-loadouts.json')['loadouts']}
    groups = []
    for tier in ('S', 'A', 'B', 'C'):
        members = [r for r in rows if r.get('tier') == tier]
        cells = ''.join(
            f'<a class="tier-cell" href="{("/pokebonk/builds/#build-" + _slug(r["name"])) if r["name"] in built else "/pokebonk/pokemon/"}" title="{escape(r["name"])}">'
            f'{_img(r["id"], r["name"], 56)}<span>{escape(r["name"])}</span></a>' for r in members)
        groups.append(f'<div class="tier-row tier-{tier}"><div class="tier-label"><strong>{tier}</strong>'
                      f'<small>{TIER_LABEL[tier]}</small></div><div class="tier-cells">{cells}</div></div>')
    return ('<section class="tier-grid" id="tier-grid" aria-label="PokeBonk tier list">'
            f'<p class="tier-note">All 79 League partners · ranked by combining three public tier lists '
            f'(Season 2 data). Tap an S or A partner for its build.</p>' + ''.join(groups) + '</section>')


def loadout_card(x, compact=False):
    moves = ''.join(
        f'<li class="{"fuse" if m["fusion"] else ""}">{_type_chip(m["type"])}<span>{escape(m["name"])}</span>'
        f'{"<em>fusion</em>" if m["fusion"] else ""}</li>' for m in x['moves'])
    items = ''.join(f'<li title="{escape(i["desc"])}"><strong>{escape(i["name"])}</strong>'
                    f'<span>{escape(i["desc"])}</span></li>' for i in x['items'])
    fusion = (f'<p class="fusion-line">Signature fusion: <strong>{escape(x["fusion"]["name"])}</strong> = '
              f'{escape(x["fusion"]["moves"][0])} + {escape(x["fusion"]["moves"][1])}</p>') if x['fusion'] else ''
    evo = ' → '.join(f'{escape(e["name"])} (Lv {e["level"]})' for e in x['evolution'])
    head = (f'<div class="loadout-head">{_img(x["id"], x["name"], 72)}<div><h3 id="build-{_slug(x["name"])}">'
            f'{escape(x["name"])} build</h3><p>{"".join(_type_chip(t) for t in x["types"])}'
            f'<span class="tier-badge tier-{x["tier"]}">{x["tier"]} tier</span>'
            f'<span class="cls">{x["class"].title()} {escape(x["main_type"].title())}</span></p></div></div>')
    if compact:
        return (f'<article class="loadout loadout-compact">{head}<ol class="loadout-moves">{moves}</ol>{fusion}'
                f'<p class="loadout-items-line">Items: {", ".join(escape(i["name"]) for i in x["items"])} · '
                f'Vitamins: {", ".join(escape(v) for v in x["vitamins"])}</p></article>')
    return (f'<article class="loadout">{head}'
            f'<div class="loadout-body"><div><h4>Moves (unlock order)</h4><ol class="loadout-moves">{moves}</ol>{fusion}</div>'
            f'<div><h4>Items</h4><ul class="loadout-items">{items}</ul>'
            f'<h4>Vitamins</h4><p>{", ".join(escape(v) for v in x["vitamins"])}</p>'
            f'<h4>Passive · {escape(x["passive"]["name"])}</h4><p>{escape(x["passive"]["desc"])}</p>'
            + (f'<h4>Evolution</h4><p>{evo}</p>' if evo else '') + '</div></div></article>')


def builds_block():
    data = _load('pokebonk-loadouts.json')
    s = [x for x in data['loadouts'] if x['tier'] == 'S']
    a = [x for x in data['loadouts'] if x['tier'] == 'A']
    nav = ''.join(f'<a href="#build-{_slug(x["name"])}">{_img(x["id"], x["name"], 36)}{escape(x["name"])}</a>' for x in s + a)
    return ('<section class="loadouts" id="best-builds" aria-label="Best PokeBonk builds">'
            '<p class="tier-note">One copyable starting build for each S and A tier partner: take the moves in order, '
            'level the two marked moves together for the signature fusion, and pick these items when offered.</p>'
            f'<nav class="loadout-nav" aria-label="Jump to a partner">{nav}</nav>'
            '<h2 class="loadout-h2">S tier builds</h2>' + ''.join(loadout_card(x) for x in s) +
            '<h2 class="loadout-h2">A tier builds</h2>' + ''.join(loadout_card(x, compact=True) for x in a) +
            '</section>')


def hub_preview():
    data = _load('pokebonk-loadouts.json')
    top = [x for x in data['loadouts'] if x['tier'] == 'S'][:3]
    cards = ''.join(
        f'<a class="preview-card" href="/pokebonk/builds/#build-{_slug(x["name"])}">{_img(x["id"], x["name"], 64)}'
        f'<span><strong>{escape(x["name"])}</strong><small>{escape(x["fusion"]["name"] if x["fusion"] else x["moves"][0]["name"])}'
        f' · {escape(x["items"][0]["name"])}</small></span></a>' for x in top)
    return ('<section class="hub-preview" aria-label="Top PokeBonk builds right now">'
            '<h2>Top builds right now</h2>'
            f'<div class="preview-row">{cards}</div>'
            '<p><a href="/pokebonk/builds/">All S and A tier builds →</a> · <a href="/pokebonk/tier-list/">Full tier list →</a></p></section>')


def insert_after_header(html, block):
    return re.sub(r'(<header class="article-head"[^>]*>.*?</header>)', lambda m: m[1] + block, html, count=1, flags=re.S)


LEDE = re.compile(r'(<header class="article-head"[^>]*>.*?<h1>.*?</h1>)\s*<p class="answer">.*?</p>', re.S)


def _lede(html, text):
    return LEDE.sub(lambda m: m[1] + '<p class="answer">' + text + '</p>', html, count=1)


def apply_answers(pages):
    loads = _load('pokebonk-loadouts.json')['loadouts']
    s = [x['name'] for x in loads if x['tier'] == 'S']
    tl = pages.get('/pokebonk/tier-list/')
    if tl:
        tl['html'] = _lede(tl['html'], f'Best PokeBonk partners right now: <strong>{", ".join(s[:-1])} and {s[-1]}</strong> (S tier). '
                           'Bulbasaur and Charmander are the strongest starters. The full S–C board for all 79 League partners is below.')
        tl['html'] = insert_after_header(tl['html'], tier_grid())
    bd = pages.get('/pokebonk/builds/')
    if bd:
        top = loads[0]
        bd['html'] = _lede(bd['html'], f'The best build to start with is <strong>{escape(top["name"])}</strong>: '
                           f'{", ".join(escape(m["name"]) for m in top["moves"])}, fused into '
                           f'<strong>{escape(top["fusion"]["name"])}</strong>, with {", ".join(escape(i["name"]) for i in top["items"])}. '
                           'Every S and A tier partner has a copyable build below.')
        bd['html'] = insert_after_header(bd['html'], builds_block())
