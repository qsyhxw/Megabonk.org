"""Answer-first modules for the Azeroth Survivors section (v3.20, SOP 08 F2/F3/F9).

Build cards come from the reviewed CLASSES routes in azeroth_survivors_content.py
(start spell, talent chain, priorities); tiers from data/azeroth-consensus-tier.json.
Icons reuse the reviewed name→asset inventory of azeroth_survivors_icons.
Inserted under the article header so the first screen answers the query.
"""
from pathlib import Path
from html import escape
import json
import re

from azeroth_survivors_content import CLASSES
from azeroth_survivors_icons import inventory

ROOT = Path(__file__).resolve().parents[1]
P = '/azeroth-survivors/'
TIER_LABEL = {'S': 'Best picks', 'A': 'Strong', 'B': 'Solid', 'C': 'Situational'}
# Shaman is documented on its own build page rather than in CLASSES.
EXTRA = {'shaman': dict(name='Shaman', start='Lightning Bolt', routes=[
    ['Elemental', 'Lightning Overload → Elemental Fury → Chain Lightning', 'Repeated Chain Lightning clears packs once Elemental talents are allocated.', ''],
    ['Enhancement', 'Windfury Weapon → Stormstrike', 'Rockbiter into Stormstrike gives a melee route.', '']],
    priority=['Build one working lightning damage source before taking totems.',
              'Add Chain Lightning as soon as it is offered for pack clear.',
              'Take totems after the damage engine works, not before.'])}


def _icon(cls, name):
    for e in inventory()['entities']:
        if e['name'].replace('’', "'") == name and e['kind'] in ('spell', 'talent') and e.get('class') == cls:
            return e['asset']
    return None


def _chip(cls, name, size=32):
    src = _icon(cls, name)
    img = f'<img src="{src}" width="{size}" height="{size}" alt="" loading="lazy" decoding="async">' if src else ''
    return f'<span class="talent-chip">{img}<span>{escape(name)}</span></span>'


def _classes():
    data = dict(CLASSES)
    data.update(EXTRA)
    return data


def _tiers():
    return {r['cls'].lower(): r for r in json.loads((ROOT / 'data/azeroth-consensus-tier.json').read_text(encoding='utf8'))['rows']}


def _class_icon(cls, size):
    return (f'<img src="/assets/azeroth-survivors/icons/{cls}.png" width="{size}" height="{size}" alt="" '
            'loading="lazy" decoding="async">')


def tier_grid():
    tiers = _tiers()
    rows = []
    for t in ('S', 'A', 'B', 'C'):
        members = [k for k, r in tiers.items() if r['tier'] == t]
        if not members:
            continue
        cells = ''.join(f'<a class="tier-cell" href="{P}builds/{k}/">{_class_icon(k, 56)}<span>{k.title()}</span></a>' for k in members)
        rows.append(f'<div class="tier-row tier-{t}"><div class="tier-label"><strong>{t}</strong><small>{TIER_LABEL[t]}</small></div>'
                    f'<div class="tier-cells">{cells}</div></div>')
    return ('<section class="tier-grid" id="tier-grid" aria-label="Azeroth Survivors class tier list">'
            '<p class="tier-note">All nine classes, ranked by combining three public class rankings. Tap a class for its build.</p>'
            + ''.join(rows) + '</section>')


def route_line(cls, route):
    steps = [s for s in re.split(r'\s*→\s*', route[1])]
    chain = ' <span class="arrow">→</span> '.join(_chip(cls, s) if _icon(cls, s) else f'<span class="talent-chip plain">{escape(s)}</span>' for s in steps)
    return f'<li><strong>{escape(route[0])}</strong><div class="talent-chain">{chain}</div><p>{escape(route[2].split(". ")[0].rstrip("."))}.</p></li>'


def build_card(cls, d, tier):
    routes = ''.join(route_line(cls, r) for r in d['routes'])
    prio = ''.join(f'<li>{escape(p.split(". ")[0].rstrip("."))}.</li>' for p in d.get('priority', [])[:3])
    return (f'<section class="loadout az-loadout" id="best-build" aria-label="{d["name"]} build">'
            f'<div class="loadout-head">{_class_icon(cls, 56)}<div><h2>Best {d["name"]} build</h2>'
            f'<p><span class="tier-badge tier-{tier}">{tier} tier</span> Starts with {_chip(cls, d["start"], 24)}</p></div></div>'
            f'<div class="loadout-body"><div><h4>Talent routes</h4><ol class="route-list">{routes}</ol></div>'
            f'<div><h4>Draft priority in a run</h4><ol class="prio-list">{prio}</ol></div></div></section>')


def builds_hub_block():
    tiers = _tiers()
    cards = []
    for cls, d in sorted(_classes().items(), key=lambda kv: (-tiers[kv[0]]['score'], kv[0])):
        main = d['routes'][0]
        cards.append(f'<a class="class-card" href="{P}builds/{cls}/">{_class_icon(cls, 48)}<span><strong>{d["name"]}</strong>'
                     f'<small><span class="tier-badge tier-{tiers[cls]["tier"]}">{tiers[cls]["tier"]}</span> {escape(main[0])}: '
                     f'{escape(main[1])}</small></span></a>')
    return ('<section class="class-cards" aria-label="Best build for every class">' + ''.join(cards) + '</section>')


LEDE = re.compile(r'(<header class="article-head"[^>]*>.*?<h1>.*?</h1>)\s*<div class="answer">.*?</div>', re.S)


def _lede(html, text):
    return LEDE.sub(lambda m: m[1] + '<div class="answer"><p>' + text + '</p></div>', html, count=1)


def insert_after_header(html, block):
    return re.sub(r'(<header class="article-head"[^>]*>.*?</header>)', lambda m: m[1] + block, html, count=1, flags=re.S)


def hub_block():
    tiers = _tiers()
    s = [k.title() for k, r in tiers.items() if r['tier'] == 'S']
    return (f'<section class="hub-preview" aria-label="Best Azeroth Survivors classes"><h2>Best classes right now</h2>'
            f'<p>{" and ".join(s)} lead the current rankings. Pick a class for its talent route:</p>'
            + builds_hub_block() + f'<p><a href="{P}tier-list/">Full class tier list →</a></p></section>')


def present_answers(path, html):
    tiers = _tiers()
    classes = _classes()
    m = re.fullmatch(P + r'builds/([a-z]+)/', path)
    if m and m[1] in classes:
        cls, d = m[1], classes[m[1]]
        r = d['routes'][0]
        html = _lede(html, f'<strong>Best {d["name"]} build:</strong> {escape(r[0])} — '
                     f'{escape(r[1])}. Start with {escape(d["start"])}; '
                     + (f'switch to {escape(d["routes"][1][0])} ({escape(d["routes"][1][1])}) when that branch is unlocked.'
                        if len(d['routes']) > 1 else ''))
        return insert_after_header(html, build_card(cls, d, tiers[cls]['tier']))
    if path == P + 'tier-list/':
        s = [k.title() for k, r in tiers.items() if r['tier'] == 'S']
        a = [k.title() for k, r in tiers.items() if r['tier'] == 'A']
        html = _lede(html, f'Best classes in Azeroth Survivors: <strong>{" and ".join(s)}</strong> (S tier), then '
                     f'{", ".join(a)} (A tier). Paladin and Warrior are the easiest first clears.')
        return insert_after_header(html, tier_grid())
    if path == P + 'builds/':
        return insert_after_header(html, builds_hub_block())
    return html
