"""Warhammer Survivors fill pages (v3.23, 2026-11-13): bosses, maps/stages, best builds.

Facts cross-checked (ROADMAP WHS-FILL2):
- Bosses: Extremis boss list, stages and counter evolutions agree across Destructoid, games.gg and the
  Steam community Extremis guide; spawn 25:00 and health formulas from games.gg + gamewith stage data;
  our own frames of the Norn Emissary fight (25:30 with boss bar).
- Stages: unlock chain, rescues, relics and Extremis per stage from gamewith stage table, matching
  games.gg rescues and our Catachan frames (Gallowdark level 40 -> Ork Stronghold).
- Builds: recipes from our 38-row table (evolutions page); in-run examples from RunItBack videos
  (Amalia + Chainsword/Tape Measure/Shield of Faith; Brother Luca + Boltgun/Dice Cube), our frames.
Pages are built from the tips page as template, like warhammer_characters.py.
"""
from html import escape
from pathlib import Path
import re

from site_analytics import write_html
from warhammer_v321 import video

ROOT = Path(__file__).resolve().parents[1]
A = '/assets/warhammer-survivors/'

BOSSES = [  # name, setting, stages, counter, recipe, health, notes
    ('Norn Emissary', '40K', 'Imperial Bastion, Death World Invasion, Desert Wasteland', 'Gauntlets of Ultramar',
     'Power Fist + Codex Astartes', 'level × 500 (min 10,000)',
     'Immune to stun, Vulnerable and Instant Kill. Fast and hits hard up close: kite in wide circles, away from walls. Codex Astartes is a hidden passive on Death World Invasion; bring the Auspex relic to reveal it.'),
    ('Great Unclean One', '40K', 'Gallowdark, Imperial Shipyard', 'Weapon of the Matriarch',
     'Ardent Blade + Tactical Rock (max level)', 'level × 700 (min 10,000)',
     'Highest health of the six. Max Tactical Rock before the 25-minute mark.'),
    ('Ghazghkull Thraka', '40K', 'Ork Stronghold', 'Bale Eye',
     'Power Klaw + Da Lucky Stikk (max level)', 'level × 500 (min 10,000)',
     'Power Klaw belongs to Commissar Yarrick (rescued on Ork Stronghold).'),
    ('Vizzik Skour, Prophet of the Horned Rat', 'AoS', 'The Great Parch, Under-Empire, The Twin-Tailed City', 'Anti-Wizard Flintlock',
     'Flintlock Pistols + Ardcoat', 'level × 650 (min 10,000)',
     'Immune to stun and Instant Kill. Flintlock Pistols belong to Hanniver Toll (rescued on The Great Parch).'),
    ('Skarbrand', 'AoS', 'Bloodwind Spoil, The Twin-Tailed City', 'Uskavar the Sunderer',
     'Stormcharged Warhammer + Tactical Rock (max level)', 'level × 300 (min 10,000)',
     'Immune to burning, poison and stun; weak to Frost, Null and Holy damage. Stormcharged Warhammer belongs to Rostus Oxenhammer.'),
    ('Trugg the Troggoth King', 'AoS', 'Skrappa Spill, Gnarlwood', 'Zangrom-Thaz',
     "Fyrestorm Greataxe + Kragg Blackhammer's Master Rune", 'level × 230 (min 10,000)',
     'Lowest health. His club slam covers a large telegraphed area and knocks you back: step out of the warning zone. Fyrestorm Greataxe belongs to Gotrek Gurnisson.'),
]

STAGES = [  # universe, stage, unlock, extremis, rescues, relics
    ('40K', 'Imperial Bastion', 'Start', 'Norn Emissary', 'Trooper Bartosz Kozlowski, The Legend of Catachan', 'Astropathic Relay'),
    ('40K', 'Gallowdark', 'Level 20 on Imperial Bastion', 'Great Unclean One', 'K9 Mastiff', 'Munitorum Dataslate, Tome of Ectoclades, Astropathic Relay'),
    ('40K', 'Ork Stronghold', 'Level 40 on Gallowdark', 'Ghazghkull Thraka', 'Commissar Sebastian Yarrick', 'Signum Array, Astropathic Relay'),
    ('40K', 'Imperial Shipyard', 'Level 50 on Ork Stronghold', 'Great Unclean One', 'Saint Celestine', "The Emperor's Tarot, Maelstrom Key, Astropathic Relay"),
    ('40K', 'Death World Invasion', 'Level 60 on Imperial Shipyard', 'Norn Emissary', 'Chapter Master Marneus Calgar', 'The Book of Tzeentch, Gyrotemporal Vault, Astropathic Relay'),
    ('40K', 'Desert Wasteland', "Unlock 'Eavy Metal mode on any stage", 'Norn Emissary', '—', 'Auspex'),
    ('40K', 'Hobby Table', 'Encounter all 3 40K Extremis bosses', '—', '—', 'Astropathic Relay'),
    ('40K', 'Perils of the Warp', 'Defeat all 3 40K Extremis bosses', 'Mortarion (30-minute stage)', '—', 'Book of Woe'),
    ('AoS', 'The Great Parch', 'Start', 'Vizzik Skour', 'Armand Callis, Hanniver Toll', '—'),
    ('AoS', 'Skrappa Spill', 'Level 20 on The Great Parch', 'Trugg the Troggoth King', 'Gotrek Gurnisson', 'Warscroll, Creatura Mythologica'),
    ('AoS', 'Bloodwind Spoil', 'Level 40 on Skrappa Spill', 'Skarbrand', 'Rostus Oxenhammer', 'Atmospheric Anatomiser, Carto-Arcanabulum'),
    ('AoS', 'Under-Empire', 'Level 50 on Bloodwind Spoil', 'Vizzik Skour', 'Ulgromthier', 'Celestial Orrery'),
    ('AoS', 'The Twin-Tailed City', 'Level 60 on Under-Empire', 'Vizzik Skour / Skarbrand', 'Mistress Verentia', 'Quicksilver Draught'),
    ('AoS', 'Gnarlwood', "Unlock 'Eavy Metal mode on any stage", 'Trugg the Troggoth King', '—', 'Arcanoscope, Eye of Tzeentch, Amberbone, Glimmering'),
    ('AoS', 'Hobby Table', 'Encounter all 3 AoS Extremis bosses', '—', '—', '—'),
    ('AoS', 'Necropolis', 'Defeat all 3 AoS Extremis bosses', 'Nagash', '—', 'Warpstone Talisman'),
]

ICON = {  # icons cropped from in-game level-up and chest panels (our frames)
    'chainsword': 'eviscerator-chainsword', 'boltgun': 'heavy-bolter', 'tempest-axes': 'whirlwind-axes', 'd6-dice': 'sustained-fire-dice',
}
PART_ICON = {'Dice Cube': None, 'D6 Dice': 'd6-dice', 'Bandolier': 'bandolier', 'Hourglass': 'hourglass', 'Liquid Green Stuff': 'liquid-green-stuff'}

BUILDS = [  # title, champion (unlock), core, support, why, anchor
    ('Eviscerator Chainsword (easiest strong start)', 'Sister Superior Amalia Novena (400 coins)',
     ['Chainsword → max', 'Tape Measure (any level, max later)', 'Shield of Faith'],
     'Nuln Oil, Magnet', 'Amalia gains +10% range every 10 levels and Shield of Faith blocks lanes, so the evolved chainsword sweeps whole screens. Tape Measure unlocks after surviving 1 minute.', 'chainsword'),
    ('Heavy Bolter (best ranged 40K)', 'Brother Luca Amasius (200 coins)',
     ['Boltgun → max', 'Dice Cube', 'Shield of Faith'],
     'Tape Measure, D6 Dice', 'Slow until the Boltgun has a few upgrades, then a constant barrage that pushes bosses back. Dice Cube unlocks by getting D6 Dice to level 6 in 40K.', 'boltgun'),
    ('Meltagun (boss killer)', 'Trooper Bartosz Kozlowski (rescue, Imperial Bastion)',
     ['Lasgun → max', 'Gauntlet'],
     'Shield of Faith (second follower)', 'Short-range beam with bonus damage to bosses and close enemies; Lasgun also counts toward the follower objectives.', 'lasgun'),
    ('Whirlwind Axes (Age of Sigmar start)', 'Neave Blacktalon (start)',
     ['Tempest Axes → max', 'Sabaton'],
     'Bandolier, Hourglass', 'Available from the first AoS run; Sabaton is a movement passive, so the build also kites well.', 'tempest-axes'),
    ('Sustained Fire Dice (both universes)', 'Any champion',
     ['D6 Dice → max', 'Scatter Dice'],
     'Dice Cube', 'Works in either universe; the initial roll splits into extra exploding dice.', 'd6-dice'),
]

CSS = '<style>.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px;margin:18px 0}.card{background:var(--plate);border:1px solid var(--edge);padding:16px 18px}.card h3{margin:0 0 6px;font-size:1.1rem}.card .who{color:var(--parch-dim);font-size:13px;margin:0 0 10px}.card ul{margin:0 0 10px;padding-left:18px}.card p{font-size:14px;margin:0}.card .icons{display:flex;gap:8px;margin-bottom:10px}.card .ico{width:48px;height:48px;image-rendering:pixelated;border:1px solid var(--edge);background:#0b0c0d}.uni{display:inline-block;font-size:10px;letter-spacing:.1em;padding:2px 6px;border:1px solid;margin-left:6px}.u40k{color:#e07a6a;border-color:#7b2b22}.uaos{color:#8ec5e0;border-color:#2c5a70}</style>'


def uni(u):
    return '<span class="uni u40k">40K</span>' if u == '40K' else '<span class="uni uaos">AoS</span>'


def bosses_body():
    rows = ''.join(f'<tr id="{re.sub(r"[^a-z0-9]+", "-", n.split(",")[0].lower()).strip("-")}"><td><strong>{escape(n)}</strong>{uni(u)}</td><td>{escape(s)}</td><td><strong>{escape(c)}</strong><br><small>{escape(r)}</small></td><td>{escape(h)}</td></tr>'
                   for n, u, s, c, r, h, _ in BOSSES)
    notes = ''.join(f'<li><strong>{escape(n.split(",")[0])}</strong>: {escape(x)}</li>' for n, *_ , x in BOSSES)
    return f'''<header class="article-head" id="guide"><p>WARHAMMER SURVIVORS · BOSSES</p><h1>Warhammer Survivors bosses: all 6 Extremis bosses and how to beat them</h1><div class="answer"><p><strong>Each Extremis boss arrives at 25:00 and can only be beaten with one specific evolved weapon.</strong> Without that evolution its health bar does not go down. Bring the counter below, then survive to the 25-minute mark.</p></div><p class="byline">Megabonk.org editors · Updated 13 November 2026 · Release v2.1</p></header>
<nav class="toc" aria-label="On this page"><a href="#list">All 6 bosses</a><a href="#how">How the fight works</a><a href="#tips">Boss tips</a><a href="#special">Mortarion and Nagash</a></nav>
<div class="article-layout"><article class="prose">
<section id="list"><h2>All Extremis bosses and their counters</h2><div class="table-wrap" tabindex="0" role="region" aria-label="Extremis bosses, scroll horizontally"><table><thead><tr><th>Boss</th><th>Stages</th><th>Counter evolution</th><th>Health</th></tr></thead><tbody>{rows}</tbody></table></div><p>Recipes and max-level passives: <a href="/warhammer-survivors/evolutions/">all 38 evolutions</a>. The counter weapons belong to specific champions: <a href="/warhammer-survivors/characters/">how to unlock them</a>.</p></section>
<section id="how"><h2>How an Extremis fight works</h2><ol><li><strong>Pick the champion who carries the counter's base weapon</strong> (for example Hanniver Toll for Flintlock Pistols).</li><li><strong>Evolve it before 25:00</strong>: max the weapon, hold the companion passive, open an elite/boss chest.</li><li><strong>Survive to 25:00.</strong> The boss spawns with its own health bar at the bottom of the screen.</li><li><strong>Win for 500 coins.</strong> Beating all three bosses of a universe opens its special stage.</li></ol><figure><img src="{A}bosses/norn-emissary-fight.webp" width="1001" height="626" alt="Norn Emissary fight at 25:30 with its health bar at the bottom of the screen" loading="lazy" decoding="async"><figcaption>Norn Emissary at 25:30: the boss bar appears along the bottom edge.</figcaption></figure>
<p><strong>Mode traps:</strong> Endless War removes the final boss, and Fast Attack doubles the mission clock. Turn both off while learning a boss.</p></section>
<section id="tips"><h2>Boss-by-boss tips</h2><ul>{notes}</ul><h3>Watch it</h3>{video('tILdBRKXQHg', '', 'Norn Emissary boss fight', 'How To Win Norn Emissary Boss Fight', 'Video Game News')}</section>
<section id="special"><h2>Mortarion and Nagash</h2><p>Defeating all three 40K Extremis bosses opens <strong>Perils of the Warp</strong> (Mortarion, 30-minute stage). Defeating all three Age of Sigmar Extremis bosses opens <strong>Necropolis</strong> (Nagash). Both are immune to stun and Instant Kill. Stage unlock order: <a href="/warhammer-survivors/maps/">all maps</a>.</p></section>
<p><a href="#guide">Back to top ↑</a></p></article></div>'''


def maps_body():
    def rows(u):
        return ''.join(f'<tr><td><strong>{escape(s)}</strong></td><td>{escape(x)}</td><td>{escape(b)}</td><td>{escape(r)}</td><td>{escape(rel)}</td></tr>'
                       for uu, s, x, b, r, rel in STAGES if uu == u)
    head = '<thead><tr><th>Stage</th><th>How to unlock</th><th>Extremis boss</th><th>Rescue</th><th>Relics</th></tr></thead>'
    return f'''<header class="article-head" id="guide"><p>WARHAMMER SURVIVORS · MAPS</p><h1>Warhammer Survivors maps: every stage and how to unlock it</h1><div class="answer"><p><strong>Stages unlock in a chain by reaching a character level on the previous map: 20, then 40, 50 and 60.</strong> Each universe has five main stages, a bonus stage from 'Eavy Metal mode, a Hobby Table and a final special stage.</p></div><p class="byline">Megabonk.org editors · Updated 13 November 2026 · Release v2.1</p></header>
<nav class="toc" aria-label="On this page"><a href="#k40">40K stages</a><a href="#aos">Age of Sigmar stages</a><a href="#tips">Unlock tips</a></nav>
<div class="article-layout"><article class="prose">
<section id="k40"><h2>Warhammer 40,000 stages</h2><div class="table-wrap" tabindex="0" role="region" aria-label="40K stages, scroll horizontally"><table>{head}<tbody>{rows("40K")}</tbody></table></div></section>
<section id="aos"><h2>Age of Sigmar stages</h2><div class="table-wrap" tabindex="0" role="region" aria-label="Age of Sigmar stages, scroll horizontally"><table>{head}<tbody>{rows("AoS")}</tbody></table></div></section>
<section id="tips"><h2>Unlock tips</h2><ol><li><strong>Level, not survival time, opens the next map.</strong> A run that reaches level 40 on Gallowdark unlocks Ork Stronghold even if you die afterwards.</li><li><strong>Pick up the map relics</strong>: the Signum Array (Ork Stronghold) reveals rescue targets on every 40K map; the Auspex (Desert Wasteland) and Arcanoscope (Gnarlwood) reveal hidden passives.</li><li><strong>Turn on 'Eavy Metal once</strong> on any stage to open Desert Wasteland (40K) and Gnarlwood (AoS).</li><li>Rescues on each map are listed with directions on the <a href="/warhammer-survivors/characters/">characters page</a>; Extremis bosses on the <a href="/warhammer-survivors/bosses/">bosses page</a>.</li></ol><figure><img src="{A}catachan/signum-array-map.webp" width="1080" height="565" alt="Ork Stronghold pause map with the Signum Array relic marked" loading="lazy" decoding="async"><figcaption>Map relics show as a green ? on the pause map.</figcaption></figure></section>
<p><a href="#guide">Back to top ↑</a></p></article></div>'''


def builds_body():
    cards = ''
    for title, who, core, sup, why, anc in BUILDS:
        items = ''.join(f'<li>{escape(c)}</li>' for c in core)
        icons = ''
        if anc in ICON:
            icons += f'<img class="ico" src="{A}icons/{ICON[anc]}.webp" width="64" height="64" alt="{escape(title.split(" (")[0])} icon" loading="lazy">'
        for part, ic in PART_ICON.items():
            if ic and any(part in c for c in core + [sup]):
                icons += f'<img class="ico" src="{A}icons/{ic}.webp" width="64" height="64" alt="{part} icon" loading="lazy">'
        cards += (f'<div class="card loadout"><div class="icons">{icons}</div><h3>{escape(title)}</h3><p class="who">{escape(who)}</p><ul>{items}</ul>'
                  f'<p><strong>Add:</strong> {escape(sup)}</p><p>{escape(why)} <a href="/warhammer-survivors/evolutions/#{anc}">Recipe →</a></p></div>')
    return f'''<header class="article-head" id="guide"><p>WARHAMMER SURVIVORS · BEST BUILDS</p><h1>Best builds in Warhammer Survivors</h1><div class="answer"><p><strong>Start with Amalia Novena and the Eviscerator Chainsword, or Brother Luca and the Heavy Bolter.</strong> Both are cheap champions (400 and 200 coins), evolve with passives you unlock in the first runs, and carry you into the 25-minute bosses.</p></div><p class="byline">Megabonk.org editors · Updated 13 November 2026 · Release v2.1</p></header>
<nav class="toc" aria-label="On this page"><a href="#builds">5 builds</a><a href="#order">Upgrade order</a><a href="#boss">Builds for bosses</a></nav>
<div class="article-layout"><article class="prose">
<section id="builds"><h2>Five builds that work now</h2><div class="cards loadout">{cards}</div>
<figure><img src="{A}builds/eviscerator-chest.webp" width="650" height="731" alt="Chest evolving Chainsword into Eviscerator Chainsword" loading="lazy" decoding="async"><figcaption>Eviscerator Chainsword from the first boss chest after maxing Chainsword with Tape Measure.</figcaption></figure>
<figure><img src="{A}builds/heavy-bolter-chest.webp" width="489" height="564" alt="Chest evolving Boltgun into Heavy Bolter" loading="lazy" decoding="async"><figcaption>Heavy Bolter: Boltgun maxed with Dice Cube held.</figcaption></figure>
<figure><img src="{A}evo/chest-evolution.webp" width="556" height="488" alt="Chest evolving Boltstorm Pistol into Typhoon Crossbow" loading="lazy" decoding="async"><figcaption>Age of Sigmar: Boltstorm Pistol + Dice Cube evolves into Typhoon Crossbow.</figcaption></figure></section>
<section id="order"><h2>Upgrade order inside a run</h2><ol><li><strong>Level the main weapon first</strong> until it is maxed; take its companion passive the first time it is offered (level 1 is enough for most recipes).</li><li><strong>Take Shield of Faith early</strong> if offered: it blocks enemy lanes and is the strongest early defensive pick.</li><li><strong>Grab a Magnet before big XP piles</strong>: one Magnet can give several levels at once.</li><li><strong>Open the next elite/boss chest</strong> once the weapon is maxed to evolve it, then start the second evolution.</li></ol><h3>Watch the chainsword build</h3>{video('mQsdlToCnEo', '15:00', 'Eviscerator Chainsword build gameplay', 'This S+ TIER Evolved Chainsword Build Is BROKEN!', 'RunItBack')}</section>
<section id="boss"><h2>Builds for the Extremis bosses</h2><p>The six 25-minute bosses each need a specific evolution (Gauntlets of Ultramar, Weapon of the Matriarch, Bale Eye, Anti-Wizard Flintlock, Uskavar the Sunderer, Zangrom-Thaz). Plan that weapon as your main build for a boss run: <a href="/warhammer-survivors/bosses/">boss counters</a>.</p></section>
<p><a href="#guide">Back to top ↑</a></p></article></div>'''


PAGES = [
    ('bosses', 'Warhammer Survivors Bosses: All 6 Extremis Bosses & Counters', 'Every Warhammer Survivors Extremis boss, its stages, health and the one evolution that beats it, plus Mortarion and Nagash unlocks.', 'database', bosses_body, True),
    ('maps', 'Warhammer Survivors Maps: Every Stage & How to Unlock It', 'All Warhammer Survivors stages in 40K and Age of Sigmar: unlock level, Extremis boss, rescues and relics on each map.', 'database', maps_body, False),
    ('best-builds', 'Warhammer Survivors Best Builds: 5 Strong Weapon Builds', 'The best Warhammer Survivors builds right now: Eviscerator Chainsword, Heavy Bolter, Meltagun, Whirlwind Axes and Sustained Fire Dice, with upgrade order.', 'build', builds_body, True),
]


def build():
    template = (ROOT / 'warhammer-survivors/tips/index.html').read_text(encoding='utf8')
    head0, rest = template.split('<main id="main"', 1)
    footer = '<footer' + rest.split('<footer', 1)[1]
    for slug, title, desc, fmt, body, has_video in PAGES:
        route = f'/warhammer-survivors/{slug}/'
        head = re.sub(r'<title>.*?</title>', f'<title>{title}</title>', head0)
        head = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m[1] + desc, head)
        for prop, val in (('title', title), ('description', desc), ('url', 'https://megabonk.org' + route)):
            head = re.sub(r'(<meta property="og:' + prop + r'" content=")[^"]*', lambda m: m[1] + val, head)
        head = re.sub(r'(<link rel="canonical" href=")[^"]*', lambda m: m[1] + 'https://megabonk.org' + route, head)
        head = re.sub(r'<script type="application/ld\+json"[^>]*>.*?</script>', '', head, flags=re.S)
        if not has_video:
            head = re.sub(r'<script defer src="/assets/yt-embed\.js"></script>|<link rel="stylesheet" href="/assets/yt-embed\.css[^"]*">\n?', '', head)
        head = head.replace('</head>', CSS + '</head>', 1)
        head = re.sub(r'<body[^>]*>', f'<body data-v321="1" data-format="{fmt}" class="guide-layout wh-theme wh-guide">', head, count=1)
        path = ROOT / 'warhammer-survivors' / slug / 'index.html'
        path.parent.mkdir(parents=True, exist_ok=True)
        write_html(path, head + '<main id="main" class="wrap">' + body() + '</main>' + footer, encoding='utf8')


if __name__ == '__main__':
    build()
