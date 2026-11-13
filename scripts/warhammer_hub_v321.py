"""Warhammer Survivors hub redesign (v3.21, 2026-11-13; 08 F9).

Replaces the generic light hub body with a grimdark layout: game-art hero with status bar,
icon task tiles, a live evolution preview with the trigger rule, the two universes,
video guides, storefront entries and the existing launch-help details.
Called from warhammer_v321.hub(); the help <details> blocks are carried over unchanged.
"""
import re

B = '/warhammer-survivors/'
A = '/assets/warhammer-survivors/'
STORES = [
    ('https://store.steampowered.com/app/3669620/Warhammer_Survivors/', 'Steam', 'Windows PC · Steam Deck'),
    ('https://apps.apple.com/us/app/warhammer-survivors/id6752607219', 'App Store', 'iPhone · iPad'),
    ('https://play.google.com/store/apps/details?id=com.AurochDigital.WarhammerSurvivors', 'Google Play', 'Android'),
    ('https://aurochdigital.com/warhammer-survivors', 'Consoles & GOG', 'PS5 · Xbox · Switch 1/2 · GOG'),
]
PREVIEW = [  # weapon, companion, evolution, universe
    ('Lasgun', 'Gauntlet', 'Meltagun', '40k'),
    ('Boltgun', 'Dice Cube', 'Heavy Bolter', '40k'),
    ('Chainsword', 'Tape Measure', 'Eviscerator Chainsword', '40k'),
    ('Tempest Axes', 'Sabaton', 'Whirlwind Axes', 'aos'),
    ('Boltstorm Pistol', 'Dice Cube', 'Typhoon Crossbow', 'aos'),
    ('D6 Dice', 'Scatter Dice', 'Sustained Fire Dice', 'both'),
]


def tile(slug, title, blurb, img, alt, tag='', main=False, contain=False):
    cls = 'tile main' if main else 'tile'
    return (f'<a class="{cls}" href="{B}{slug}/">' + (f'<span class="tag">{tag}</span>' if tag else '')
            + f'<img src="{A}{img}" alt="{alt}" width="400" height="190" loading="lazy" decoding="async"'
            + (' class="contain"' if contain else '') + f'><div><h3>{title}</h3><p>{blurb}</p></div></a>')


def universe(u):
    return {'40k': '<span class="u u40k">40K</span>', 'aos': '<span class="u uaos">AoS</span>',
            'both': '<span class="u u40k">40K</span><span class="u uaos">AoS</span>'}[u]


def body(help_items, videos):
    rows = ''.join(f'<tr><td>{w}</td><td>{c}</td><td>{e}{universe(u)}</td></tr>' for w, c, e, u in PREVIEW)
    stores = ''.join(f'<a href="{h}" target="_blank" rel="noopener noreferrer">{n} ↗<span>{d}</span></a>' for h, n, d in STORES)
    tiles = ''.join([
        tile('evolutions', 'Weapon evolutions', 'All 38 weapon + companion recipes for both universes, with a search and universe filter.', 'evo/chest-evolution.webp', 'A boss chest turning Boltstorm Pistol into Typhoon Crossbow', 'Most used'),
        tile('legend-of-catachan', 'Legend of Catachan', 'Signum Array → Imperial Bastion rescue → 1,020 coins.', 'catachan/imperial-bastion-map.webp', 'Imperial Bastion map marking the Legend of Catachan'),
        tile('tips', 'First-hour tips', 'What to buy in Enhancements and which Objectives to clear first.', 'enhancements.webp', 'Enhancements screen with Strength selected'),
        tile('followers', 'Two & five followers', 'Malum Caedo + Lasgun + Shield of Faith unlocks Bugman’s Tankard.', 'amalia-select.webp', 'Sister Superior Amalia Novena in Character Select'),
        tile('dice-cube', 'Dice Cube', '40K: D6 Dice to level 6. AoS: hold four weapons at once.', 'evo/sustained-fire-dice.webp', 'D6 Dice evolving into Sustained Fire Dice'),
        tile('secrets', 'Secrets & incantations', 'Which relic opens the menu in each universe, and the codes.', 'book-tzeentch.webp', 'The Book of Tzeentch relic', contain=True),
        tile('co-op', 'Co-op & multiplayer', 'Single-player only at launch; squad followers are not a second player.', 'squad-480.webp', 'Champion and squad allies beside a tank'),
        tile('cross-save', 'Cross-save', 'What carries between Xbox, PC, Steam and mobile copies.', 'objectives-ingame.webp', 'Objectives menu'),
    ])
    return f'''<main id="main">
<section class="hub-hero" id="guide"><div class="wrap">
<p class="kicker">Warhammer 40,000 · Age of Sigmar</p>
<h1>Warhammer Survivors <span>Guide &amp; Wiki</span></h1>
<p class="hub-lead">Every weapon evolution, champion unlock and relic route for both universes, written from release-version gameplay. Pick a task and get the answer on the first screen.</p>
<div class="hub-actions"><a class="btn btn-gold" href="{B}evolutions/">Evolution recipes <span aria-hidden="true">→</span></a><a class="btn btn-ghost" href="{B}legend-of-catachan/">Unlock Catachan <span aria-hidden="true">→</span></a></div>
<div class="status"><div><small>Released</small><strong>10 Nov 2026</strong></div><div><small>Version</small><strong>v2.1.6 (Steam)</strong></div><div><small>Price</small><strong>$7.99 / £6.39</strong></div><div><small>Players</small><strong>Single-player</strong></div></div>
</div></section>
<div class="hazard" aria-hidden="true"></div>
<div class="wrap">
<section class="band" id="choose"><div class="band-head"><h2>Choose your task</h2><p>Answer-first guides with in-game screenshots.</p></div><div class="tiles">{tiles}</div></section>
<section class="band" id="evolve"><div class="band-head"><h2>Evolution quick reference</h2><p>Six common recipes; the full table has all 38.</p></div>
<div class="preview"><div><table class="evo-table"><thead><tr><th>Weapon</th><th>Companion</th><th>Evolves into</th></tr></thead><tbody>{rows}</tbody></table><a class="more" href="{B}evolutions/">See all 38 recipes →</a></div>
<div class="rule"><h3>How every evolution triggers</h3><ol><li><strong>Max the weapon.</strong> A partly upgraded weapon never evolves.</li><li><strong>Hold its companion passive</strong> — level 1 is enough (four recipes need it maxed).</li><li><strong>Open the next elite or boss chest.</strong></li></ol><img src="{A}evo/evolution-requirements.webp" alt="Level-up screen showing a weapon's Evolution Requirements" width="1001" height="626" loading="lazy" decoding="async"></div></div></section>
<section class="band" id="universes"><div class="band-head"><h2>Two universes, separate unlocks</h2><p>Objectives, relics and some recipes differ per universe.</p></div>
<div class="realms"><div class="realm k40"><h3>Warhammer 40,000</h3><p>Imperial Bastion, Gallowdark (level 40 opens Ork Stronghold) and more. Champions include Malum Caedo, Sister Superior Amalia Novena and the Legend of Catachan.</p><p>The Book of Tzeentch (Death World Invasion) opens Secrets. <a href="{B}legend-of-catachan/">Catachan route →</a></p></div>
<div class="realm aos"><h3>Age of Sigmar</h3><p>Its own stages and weapons, such as Tempest Axes and Boltstorm Pistol, with separate Objectives from 40K.</p><p>The Eye of Tzeentch opens its Secrets menu; Dice Cube unlocks by holding four weapons. <a href="{B}dice-cube/">Dice Cube →</a></p></div></div></section>
<section class="band" id="videos"><div class="band-head"><h2>Video guides</h2><p>Watch the hard parts, then use the written steps.</p></div><div class="yt-row">{videos}</div></section>
<section class="band" id="release"><div class="band-head"><h2>Where to buy &amp; play</h2><p>Out now on PC, console and mobile.</p></div>
<div class="access"><div><p>Launch price is $7.99 / £6.39 / €7.49 before regional discounts. <strong>Game Pass Ultimate and PC Game Pass</strong> include it from 10 November on Xbox Series X|S, PC, handheld and cloud, so check your membership before buying.</p><p>Demo progress does not carry into the full game. Only Xbox Play Anywhere (Xbox ↔ Microsoft PC) shares saves across devices; see <a href="{B}cross-save/">cross-save</a>.</p></div><div class="stores">{stores}</div></div></section>
<section class="band help-section" id="faq"><div class="band-head"><h2>Before you start</h2><p>Demo, platforms and launch-day problems.</p></div>{help_items}</section>
<div class="editorial-note"><p>Independent fan guide by Megabonk.org · Updated 13 November 2026 · Release v2.1</p><a href="#guide">Back to top ↑</a></div>
</div></main>'''


def rebuild(text, videos):
    help_items = ''.join(re.findall(r'<details class="help-item".*?</details>|<details id="[^"]+" class="help-item">.*?</details>', text, re.S))
    assert 'id="ios"' in help_items and 'id="switch-2"' in help_items, 'help anchors used by other pages'
    head, rest = text.split('<main id="main"', 1)
    footer = '<footer' + rest.split('<footer', 1)[1]
    head = re.sub(r'<body([^>]*) class="guide-layout wh-home"', r'<body\1 class="guide-layout wh-home wh-hub"', head, count=1)
    if 'hub.css' not in head:
        head = head.replace('</head>', '<link rel="stylesheet" href="/assets/warhammer-survivors/hub.css"></head>', 1)
    return head + body(help_items, videos) + footer
