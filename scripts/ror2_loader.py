"""Risk of Rain 2 Loader build page: loadout and items from two guides, plus one tier ranking.

Only the items and skills named in the fetched pages are listed. Items named by both
guides are marked as agreed; items named by one guide are marked as single-source.
"""
from html import escape
from urllib.parse import quote

ROUTE = '/risk-of-rain-2/loader-build/'
TITLE = 'Risk of Rain 2 Loader Build: Loadout and Items from 2026 Guides'
DESC = ('Risk of Rain 2 Loader build from two guides: the skills and items both name, '
        'what only one guide recommends, and which skills depend on unlocks.')

GAMEBRIEF = 'https://www.gamebrief.net/blog/risk-of-rain-2-best-survivors-2026'
ROGUERANKER = 'https://rogueranker.com/loader-ror2/'
SABO = 'https://sabo.gg/en/guides/ror2/loader/'

SOURCES = [
    (GAMEBRIEF, 'GameBrief best survivors 2026', 'S tier for Loader on a solo Rainstorm baseline; published 10 Oct 2026, updated 20 Oct 2026; no loadout or ordered item list; no patch number'),
    (ROGUERANKER, 'Rogue Ranker Loader guide', 'loadout and item list; no publication date shown; no patch number'),
    (SABO, 'sabo.gg Loader guide', 'loadout (two versions) and ordered item list; "reviewed" date written as 05-11-2026, format not clear; no patch number'),
]

# 技能：槽位、Rogue Ranker、sabo.gg、说明
SKILLS = [
    ('Primary', 'Not in its loadout list (Knuckleboom is the default swing)', 'Knuckleboom (loadout 1)', 'Only sabo.gg names it in a loadout; Rogue Ranker only describes it as the default swing.'),
    ('Secondary', 'Spiked Fist (after unlock)', 'Grapple Fist (loadout 1)', 'Sources differ; the secondary depends on what you have unlocked.'),
    ('Utility', 'Charged Gauntlet', 'Charged Gauntlet (both loadouts)', 'Agreed.'),
    ('Special', 'Thunderslam (after unlock, replaces M551 Pylon)', 'M551 Pylon (loadout 1); Thunderslam (loadout 2)', 'Sources differ; sabo.gg offers both versions.'),
]

# slug, 名称, 稀有度, 是否两处都提到, 说明（来自所列来源）, 来源标注
ITEMS = [
    ('kjaros-band', "Kjaro's Band", 'Uncommon', True,
     'Hits over 400% damage trigger a flame tornado (Rogue Ranker). Ranked first by sabo.gg.',
     'Both guides'),
    ('runalds-band', "Runald's Band", 'Uncommon', True,
     'Hits over 400% damage trigger an ice blast (Rogue Ranker). Ranked second by sabo.gg.',
     'Both guides'),
    ('crowbar', 'Crowbar', 'Uncommon', True,
     'Adds damage against enemies above 90% HP. Named by both guides.',
     'Both guides'),
    ('focus-crystal', 'Focus Crystal', 'Uncommon', False,
     'Adds damage to enemies within 13 m, which covers Loader\'s melee range.',
     'Rogue Ranker only'),
    ('goat-hoof', "Paul's Goat Hoof", 'White', False,
     'Increases movement speed, which Rogue Ranker says boosts Charged Gauntlet damage.',
     'Rogue Ranker only'),
    ('backup-magazine', 'Backup Magazine', 'White', False,
     'Adds an extra grapple charge.',
     'Rogue Ranker only'),
    ('soldiers-syringe', "Soldier's Syringe", 'White', False,
     'Speeds up attacks, which Rogue Ranker says helps Scrap Barrier builds.',
     'Rogue Ranker only'),
    ('tougher-times', 'Tougher Times', 'White', False,
     'Listed fourth by sabo.gg, without a description on the page.',
     'sabo.gg only'),
    ('ukulele', 'Ukulele', 'Green', False,
     'Listed fifth by sabo.gg, without a description on the page.',
     'sabo.gg only'),
    ('h3ad-5t-v2', 'H3AD-5T v2', 'Legendary', False,
     'Increases jump height and causes an explosion on landing, scaling with fall distance.',
     'Rogue Ranker only'),
    ('leaf-clover', '57 Leaf Clover', 'Legendary', False,
     'Rerolls random effects, which Rogue Ranker says can improve the Kjaro\'s and Runald\'s Band procs.',
     'Rogue Ranker only'),
]


def _icon_file(name):
    return f'https://riskofrain2.wiki.gg/wiki/File:{quote(name)}.png'


def _skill_rows():
    return ''.join(
        f'<tr><th scope="row">{escape(slot)}</th><td>{escape(rr)}</td><td>{escape(so)}</td><td>{escape(note)}</td></tr>'
        for slot, rr, so, note in SKILLS)


def _item_rows():
    out = []
    for slug, name, rarity, both, note, src in ITEMS:
        out.append(
            '<tr>'
            f'<td><img src="/assets/risk-of-rain-2/items/{slug}.webp" width="48" height="48" alt="{escape(name)} icon" loading="lazy"></td>'
            f'<th scope="row">{escape(name)}<br><small>{rarity}</small></th>'
            f'<td>{escape(note)}</td>'
            f'<td>{escape(src)}</td>'
            '</tr>')
    return ''.join(out)


def _sources():
    return ''.join(f'<li><a href="{u}" target="_blank" rel="noopener noreferrer">{escape(l)} ↗</a> — {escape(d)}</li>'
                   for u, l, d in SOURCES)


def _credit():
    return ''.join(f'<li>{escape(name)}: <a href="{_icon_file(name)}" target="_blank" rel="noopener noreferrer">Risk of Rain 2 Wiki file page ↗</a></li>'
                   for slug, name, *_ in ITEMS)


def main_html():
    return f'''<main class="wrap" id="main">
<header class="article-head" id="guide"><p class="eyebrow">INDEPENDENT PLAYER GUIDE · RISK OF RAIN 2</p><h1>Risk of Rain 2 Loader build: loadout and items from 2026 guides</h1>
<p class="answer"><strong>Short answer:</strong> GameBrief rates Loader S tier for a solo Rainstorm run. Both guides name Charged Gauntlet as the utility. Knuckleboom is the default primary, named in sabo.gg's loadout and called the default swing by Rogue Ranker. Kjaro's Band, Runald's Band and Crowbar are the items both guides name. The secondary and special skills depend on what you have unlocked. This is a summary of two guides, not our own playtesting.</p>
</header>
<section id="skills"><h2>Skills: where the guides agree</h2>
<p>Each row shows what each guide recommends. Only the utility skill is named by both guides in a loadout.</p>
<div class="table-wrap" role="region" aria-label="Loader skill comparison" tabindex="0"><table><thead><tr><th scope="col">Slot</th><th scope="col">Rogue Ranker</th><th scope="col">sabo.gg</th><th scope="col">Note</th></tr></thead><tbody>{_skill_rows()}</tbody></table></div>
</section>
<section id="items"><h2>Items: agreed and single-source</h2>
<p>Items named by both guides are listed first in the table order. "Single-source" items come from one guide only; they are not a consensus.</p>
<div class="table-wrap" role="region" aria-label="Loader item list" tabindex="0"><table><thead><tr><th scope="col">Icon</th><th scope="col">Item</th><th scope="col">What the guide says</th><th scope="col">Source</th></tr></thead><tbody>{_item_rows()}</tbody></table></div>
</section>
<section id="tier"><h2>Tier and mode</h2>
<p>GameBrief places Loader in S tier and calls her the best general recommendation. Its ranking uses a solo Rainstorm baseline. It also lists Loader among solo picks and mentions her for co-op objectives and Eclipse. Rogue Ranker and sabo.gg do not give a tier.</p>
</section>
<section id="method"><h2>How these were chosen</h2>
<p>Two guides name skills and items; GameBrief gives the tier only. None of the three states a game patch number, so check the current patch notes before relying on specific skill or item behaviour. Only items named by a guide are listed; this page does not add items from our own testing.</p>
</section>
<section id="sources"><h2>Sources and dates</h2><ul>{_sources()}</ul></section>
<section id="icons"><h2>Icon credits</h2><p>Icons come from the Risk of Rain 2 Wiki. Each item links to its wiki file page. The wiki's content licence (CC BY-SA 4.0) does not clearly cover game artwork, which belongs to its rights holders. Tell us if you are the rights holder and want an icon removed.</p><ul>{_credit()}</ul></section>
</main>'''


def page(frame, decorate):
    return decorate(ROUTE, frame(ROUTE, TITLE, DESC, main_html(), og='article'))
