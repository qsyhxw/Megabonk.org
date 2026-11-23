"""Risk of Rain 2 item tier page: consensus of three published 2026 rankings (B02a).

Only items with a wiki icon and a stated tier in at least one source are listed.
Rankings are third-party aggregates or opinion pieces, not our own playtests.
"""
from html import escape
from urllib.parse import quote

ROUTE = '/risk-of-rain-2/item-tier-list/'
TITLE = 'Risk of Rain 2 Item Tier List: Where 2026 Rankings Agree'
DESC = ('Risk of Rain 2 item tier list built from three 2026 rankings. See which items most sources rank S or A, '
        'and where the rankings disagree.')

TIERSPIRE = 'https://tierspire.com/risk-of-rain-2/item-tier-list/'
PIXELNITRO = 'https://pixelnitro.com/risk-of-rain-2-item-tier-list-2026-best-items-and-meta-breakdown/'
GAMEBRIEF = 'https://www.gamebrief.net/blog/risk-of-rain-2-item-tier-list-2026'

SOURCES = [
    (TIERSPIRE, 'Tierspire item tier list', 'aggregates six published lists; page dated 28 Oct 2026, rebuilt 23 Nov 2026; no game patch number stated'),
    (PIXELNITRO, 'PixelNitro item tier list', 'author judgement; dated 11 Oct 2026; no game patch number stated'),
    (GAMEBRIEF, 'GameBrief item tier list', 'first-pick priority for a solo run on Rainstorm or Monsoon; published 8 Oct 2026, updated 18 Nov 2026; cites patch 1.4.1 and the 14 Oct hotfix'),
]

# slug, name, rarity, tier per source (None = not placed by that source), short consensus note
ITEMS = [
    ('tougher-times', 'Tougher Times', 'White', 'S', 'S', 'S',
     'Top tier in all three sources.'),
    ('atg-missile', 'AtG Missile Mk. 1', 'Green', 'S', 'S', 'S',
     'Top tier in all three sources.'),
    ('leaf-clover', '57 Leaf Clover', 'Red', 'S', 'S', None,
     'Top tier in two sources; GameBrief does not place it.'),
    ('goat-hoof', "Paul's Goat Hoof", 'White', 'S', 'S', None,
     'Top tier in two sources; GameBrief does not place it.'),
    ('will-o-wisp', "Will-o'-the-wisp", 'Green', 'S', 'S', None,
     'Top tier in two sources; GameBrief does not place it.'),
    ('ukulele', 'Ukulele', 'Green', 'A', 'A', 'A',
     'A tier in all three sources.'),
    ('soldiers-syringe', "Soldier's Syringe", 'White', 'S', 'A', None,
     'Sources split: S in Tierspire, A in PixelNitro.'),
    ('gasoline', 'Gasoline', 'White', 'A', 'S', None,
     'Sources split: A in Tierspire, S in PixelNitro.'),
    ('mocha', 'Mocha', 'White', 'A', 'S', None,
     'Sources split: A in Tierspire, S in PixelNitro.'),
    ('safer-spaces', 'Safer Spaces', 'Void', 'A', 'S', 'S',
     'Sources split: A in Tierspire; S in PixelNitro and GameBrief. Both list it under Void items.'),
]


def _icon_file(name):
    return f'https://riskofrain2.wiki.gg/wiki/File:{quote(name.replace(" ", " "))}.png'


def _tier(v):
    return v if v else '<span class="muted">Not placed</span>'


def _rows():
    out = []
    for slug, name, rarity, t1, t2, t3, note in ITEMS:
        icon = f'/assets/risk-of-rain-2/items/{slug}.webp'
        out.append(
            '<tr>'
            f'<td><img src="{icon}" width="48" height="48" alt="{escape(name)} icon" loading="lazy"></td>'
            f'<th scope="row">{escape(name)}<br><small>{rarity}</small></th>'
            f'<td>{_tier(t1)}</td><td>{_tier(t2)}</td><td>{_tier(t3)}</td>'
            f'<td>{escape(note)}</td>'
            '</tr>')
    return ''.join(out)


def _sources():
    return ''.join(f'<li><a href="{u}" target="_blank" rel="noopener noreferrer">{escape(l)} ↗</a> — {escape(d)}</li>'
                   for u, l, d in SOURCES)


def _credit():
    seen = []
    for slug, name, *_ in ITEMS:
        seen.append(f'<li>{escape(name)}: <a href="{_icon_file(name)}" target="_blank" rel="noopener noreferrer">Risk of Rain 2 Wiki file page ↗</a></li>')
    return ''.join(seen)


def main_html():
    return f'''<main class="wrap" id="main">
<header class="article-head" id="guide"><p class="eyebrow">INDEPENDENT PLAYER GUIDE · RISK OF RAIN 2</p><h1>Risk of Rain 2 item tier list: where the 2026 rankings agree</h1>
<p class="answer"><strong>Short answer:</strong> Tougher Times and AtG Missile Mk. 1 are top tier in all three sources, and 57 Leaf Clover is top tier in two. Ukulele is A tier everywhere. Gasoline, Mocha, Soldier's Syringe and Safer Spaces are contested. This is a summary of published rankings, not our own playtesting.</p>
</header>
<section id="table"><h2>Consensus by source</h2>
<p>Each row shows the tier that three 2026 rankings give an item. "Not placed" means that source does not rank the item; it does not mean the item is weak.</p>
<div class="table-wrap" role="region" aria-label="Item tier comparison" tabindex="0"><table><thead><tr><th scope="col">Icon</th><th scope="col">Item</th><th scope="col">Tierspire</th><th scope="col">PixelNitro</th><th scope="col">GameBrief</th><th scope="col">Note</th></tr></thead><tbody>{_rows()}</tbody></table></div>
</section>
<section id="method"><h2>How these rankings were chosen</h2>
<p>Only three sources were compared. Tierspire combines six published lists, with letter grades averaged. PixelNitro is one author's judgement. GameBrief ranks items for first-pick value in a solo run on Rainstorm or Monsoon. The three use different criteria, so a tier in one does not directly equal a tier in another.</p>
<p>None of these sources is a patch-by-patch test, so check the current patch notes before relying on a specific item.</p>
</section>
<section id="sources"><h2>Sources and dates</h2><ul>{_sources()}</ul></section>
<section id="icons"><h2>Icon credits</h2><p>Icons come from the Risk of Rain 2 Wiki. Each item links to its wiki file page. The wiki's content licence (CC BY-SA 4.0) does not clearly cover game artwork, which belongs to its rights holders. Tell us if you are the rights holder and want an icon removed.</p><ul>{_credit()}</ul></section>
</main>'''


def page(frame, decorate):
    desc = DESC
    return decorate(ROUTE, frame(ROUTE, TITLE, desc, main_html(), og='article'))
