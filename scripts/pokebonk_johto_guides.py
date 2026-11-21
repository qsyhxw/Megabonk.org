"""Five first-batch Johto partner guides (client v0.10.18). Reads data/pokebonk-johto-guides.json only.

Scope: facts that the public client states (passive, kit, evolution levels, challenge) plus the
Season 3 rating basis. No in-game playtest, so no stage-by-stage strategy is written.
Type markers are original text badges, not game icons (no licensed icon source exists).
"""
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Original palette for type badges: colour plus the type name in text, never colour alone.
TYPE_COLOR = {
    'normal': '#7d7d6b', 'fire': '#b5472d', 'water': '#2e6fb0', 'grass': '#3c7d3a',
    'electric': '#b58b00', 'ice': '#3a8ea3', 'fighting': '#8c3b2a', 'poison': '#6c3a7f',
    'ground': '#8a6a3a', 'flying': '#5a6fa8', 'psychic': '#b13f7a', 'bug': '#6f7d1f',
    'rock': '#7a6a4f', 'ghost': '#4f3f7a', 'dragon': '#4d3ea0', 'dark': '#3b3a40',
    'steel': '#5f7080', 'fairy': '#b06a8f',
}


def badge(t):
    key = t.lower()
    color = TYPE_COLOR.get(key, '#555')
    return f'<span class="type-badge" style="background:{color};color:#fff;border-radius:4px;padding:1px 7px;font-size:.9em">{escape(t.title())}</span>'


def apply_johto_guides(ctx):
    article, ref, table, P, pages = (ctx[x] for x in ['article', 'ref', 'table', 'P', 'PAGES'])
    data = json.loads((ROOT / 'data/pokebonk-johto-guides.json').read_text(encoding='utf8'))
    for p in data['partners']:
        build_one(p, data, article, ref, table, P)
    return pages


def build_one(p, data, article, ref, table, P):
    name = p['name']
    types = ' '.join(badge(t) for t in p['types'])
    lv = p['evo']['levels']
    nxt = p['evo']['official_next']
    if lv and nxt:
        evo_text = f'<p>PokeBonk client evolution levels: the first evolution happens at Lv {lv[0]}'
        if len(lv) > 1:
            evo_text += f' and the second at Lv {lv[1]}'
        evo_text += '. These are the client values; the official games use different levels.' + ref(1) + ref(2) + '</p>'
    else:
        evo_text = f'<p>{escape(name)} has no level-based evolution in the public client.{ref(1)}</p>'

    kit_rows = [(k['name'], badge(k['type']), k['cls'].title(), f"{k['cd']} s", k['status'], k['desc'])
                for k in p['kit']]
    chal = ''.join(f'<li>{escape(c)}</li>' for c in p['challenge'])
    tier = p['tier']

    parts = [
        ('types', 'Type and role',
         f'<p>{escape(name)} is a {escape(p["role"] or "League")} partner. Type: {types}.{ref(1)}</p>'
         f'<p><img src="/assets/pokebonk/portraits/{p["id"]:03d}.png" width="64" height="64" alt="{escape(name)}" loading="lazy"> Portrait from the existing PokeBonk sprite set.</p>'),
        ('passive', f'Passive: {escape(p["passive"]["name"])}',
         f'<p>{escape(p["passive"]["desc"])}{ref(2)}</p>'),
        ('kit', 'Kit: the four listed moves',
         '<p>Base values from the public client. Upgrades, vitamins and fusions change them in play.</p>'
         + table(['Move', 'Type', 'Class', 'Cooldown', 'Status', 'Client description'], kit_rows) + f'{ref(2)}'),
        ('evolution', 'Evolution', evo_text),
        ('challenge', 'Unlock requirement',
         f'<ul>{chal}</ul><p>Challenge text from the public client.{ref(2)}</p>'),
        ('rating', 'Season 3 rating',
         f'<p>Rated <strong>{tier}</strong> in the Season 3 list. This rating is not re-checked for v{data["version"]}.{ref(3)}</p>'),
        ('limits', 'What this page does not cover',
         '<p>Based on the client text only. No in-game run was completed, so no damage, win-rate or clear-time claim is made.</p>''<p>No in-game screenshot is included yet. The only images are the sprite portrait and the original text type badges; screenshots will be added when they are available.</p>'),
    ]
    sources = [
        ('https://pokebonk.com/data/pokemon.json', 'pokebonk.com — public species data',
         'Types and official evolution relations, checked November 21, 2026.'),
        ('https://pokebonk.com/assets/main-Cl2MuFvV-mwpbcjrx.js', 'pokebonk.com — public game client',
         f'Passive, kit, evolution levels and challenge text. Client v{data["version"]} checked November 21, 2026. SINGLE_SOURCE.'),
        ('https://pokebonk.lorepond.com/tier-list', 'Lorepond Season 3 tier list',
         'Rating basis. Page states game v0.9.8, updated November 5, 2026.'),
    ]
    siblings = [(f"{o['slug']}/", f"{o['name']} guide") for o in data['partners'] if o['slug'] != p['slug']]
    links = [('johto-partners/', 'All Johto partners'), ('tier-list/', 'Tier list'), ('unlocks/', 'Unlock requirements')] + siblings
    article(p['slug'],
            f'PokeBonk {name}: Passive, Kit & Evolution',
            f'{name}: passive, kit and evolution',
            f'{name} in PokeBonk v{data["version"]}: passive, four listed moves, client evolution levels and unlock requirement.',
            f'{name} is a Johto League partner in PokeBonk v{data["version"]}. Its passive is {escape(p["passive"]["name"])}; its evolution levels come from the public client and differ from the official games.',
            parts, sources, links)
