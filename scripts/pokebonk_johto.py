"""Johto partners overview (v0.10.11). Reads only data/pokebonk-johto.json.

These 59 partners have no full guide yet, so this page lists facts only:
type, Season 3 rating, official evolution links and unverified PokeBonk level
candidates. It does not add them to the 79-partner league data.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def apply_johto(ctx):
    article, ref, table, P, pages = (ctx[x] for x in ['article', 'ref', 'table', 'P', 'PAGES'])
    data = json.loads((ROOT / 'data/pokebonk-johto.json').read_text(encoding='utf8'))
    rows = data['rows']

    def evo_text(r):
        prev = f"from {r['official_prev']}" if r['official_prev'] else 'base form'
        nxt = ', '.join(f"{n['name']}{(' Lv' + str(n['level'])) if n['level'] else ''}" for n in r['official_next']) or 'none'
        return f"{prev}; next: {nxt}"

    def level_text(r):
        return ' / '.join(str(x) for x in r['pokebonk_levels']) if r['pokebonk_levels'] else 'not in public client'

    table_rows = [(r['name'], ' / '.join(r['types']), r['role'] or '—', r['tier'], evo_text(r), level_text(r))
                  for r in rows]
    counts = {t: sum(1 for r in rows if r['tier'] == t) for t in 'SABC'}

    sources = [
        ('https://pokebonk.com/data/pokemon.json', 'pokebonk.com — public species data',
         'Types and official evolution relations, checked November 20, 2026. These are official game values, not PokeBonk levels.'),
        ('https://pokebonk.com/assets/main-49bNhL5s-mwo5whhx.js', 'pokebonk.com — public game client',
         'Candidate v0.10.11 roles, challenges and evolution levels, read November 20, 2026. SINGLE_SOURCE; not checked in play.'),
        ('https://pokebonk.lorepond.com/tier-list', 'Lorepond Season 3 tier list',
         'Rating basis. The page states game v0.9.8 and was updated November 5, 2026; it does not cover v0.10.11.'),
    ]

    parts = [
        ('scope', 'What this page covers',
         '<p>PokeBonk lists 59 Johto League partners that do not have a full guide yet. '
         'This page only states their type, Season 3 rating and evolution links. It does not give passives, kits, builds or unlock routes. '
         f'Full guides follow after the evolution and kit review.{ref(2)}</p>'),
        ('list', f'Partners ({len(rows)})',
         '<p>Ratings: S ' + str(counts['S']) + ' · A ' + str(counts['A']) + ' · B ' + str(counts['B']) + ' · C ' + str(counts['C']) + f'. Season 3 basis.{ref(3)}</p>'
         + table(['Partner', 'Type', 'Role (client)', 'Season 3 tier', 'Evolution (official)', 'PokeBonk levels (unverified)'], table_rows)),
        ('evolution', 'How to read the evolution column',
         f'<p>The evolution column uses official species data.{ref(1)} PokeBonk can use different level thresholds, so its numbers are shown separately as unverified candidates from the public client. '
         'Do not copy the official levels into PokeBonk plans. Partners marked “not in public client” have no PokeBonk level candidate yet.</p>'),
    ]

    links = [('tier-list/', 'Tier list'), ('pokemon/', 'All partners'), ('unlocks/', 'Unlock requirements')]

    article('johto-partners',
            'PokeBonk Johto Partners: 59 Unpublished League Partners',
            'Johto partners not yet in the guide',
            'Types, Season 3 ratings and evolution links for the 59 Johto League partners in PokeBonk that have no full guide yet.',
            'PokeBonk lists 59 Johto League partners without full guides. This page gives their type, Season 3 rating and evolution links only; passives, kits and builds are not covered yet.',
            parts, sources, links)
    return pages
