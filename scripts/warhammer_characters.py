"""Warhammer Survivors: all champions and how to unlock them (v3.23 fill, 2026-11-13).

Data: release-version unlock list, consistent across Destructoid, games.gg, intoindiegames and
howtovideogame (checked 2026-11-13); rescue directions from games.gg; Catachan route and stats
from our own frames (legend-of-catachan page). Evidence stays in ROADMAP WHS-CHAR.
Builds from the existing tips page as a template, so header, theme, analytics and ads match.
"""
from html import escape
from pathlib import Path
import re

from site_analytics import write_html

ROOT = Path(__file__).resolve().parents[1]
ROUTE = '/warhammer-survivors/characters/'
A = '/assets/warhammer-survivors/'

# (name, how, type, page) — type: start | coins | rescue | objective | paint | secret
K40 = [
    ('Malum Caedo', 'Available from the start', 'start', ''),
    ('Brother Luca Amasius', 'Buy for 200 coins', 'coins', ''),
    ('Sister Superior Amalia Novena', 'Buy for 400 coins', 'coins', 'followers'),
    ('Trooper Bartosz Kozlowski', 'Rescue on Imperial Bastion (south-east of spawn)', 'rescue', 'followers'),
    ('The Legend of Catachan', 'Rescue on Imperial Bastion (north-east corner; needs the Signum Array), then buy for 1,020 coins', 'rescue', 'legend-of-catachan'),
    ('K9 Mastiff', 'Rescue on Gallowdark (east of spawn)', 'rescue', ''),
    ('Commissar Sebastian Yarrick', 'Rescue on Ork Stronghold (north-west corner)', 'rescue', ''),
    ('Chapter Master Marneus Calgar', 'Rescue on Death World Invasion (west of spawn)', 'rescue', ''),
    ('Saint Celestine', 'Rescue on Imperial Shipyard (take the teleporter in the north-east quadrant)', 'rescue', ''),
    ('Canoness Aurora Veritas', 'Apply Burning to 100 Death Guard enemies', 'objective', ''),
    ('Max Mahon', 'Defeat 1,000 Nurglings in a single run', 'objective', ''),
    ('Captain Tor Garadon', 'Defeat 10,000 enemies in total (across runs)', 'objective', ''),
    ('Sergeant Furan', 'Get Gauntlet and Lightning Bolt to level 5 on Ork Stronghold', 'objective', ''),
    ('Knight-Commander Pask', 'Defeat 100 Ork vehicles', 'objective', ''),
    ('Celestian Sacresant Aveline Aboyé', 'Collect 10 relics', 'objective', 'secrets'),
    ("Chaplain Fo'Baran", "Recover 1,000 Wounds in 'Eavy Metal mode", 'objective', ''),
    ('Black Templars Castellan', 'Paint pot: Abaddon Black', 'paint', ''),
    ('Chief Librarian Mephiston', 'Paint pots: Abaddon Black, Leadbelcher, Mephiston Red, Rakarth Flesh', 'paint', ''),
    ('Lieutenant Titus', 'Paint pots: Abaddon Black, Agrax Earthshade, Celestra Grey, Reikland Fleshshade, Retributor Armour, Macragge Blue', 'paint', ''),
    ('Technoarcheologist Daedalosus', 'Activate the Astropathic Relay on every 40K stage', 'secret', ''),
    ('High Abbess Morvenn Vahl', 'Unlock every standard 40K champion', 'secret', ''),
]
AOS = [
    ('Neave Blacktalon', 'Available from the start', 'start', ''),
    ('Lorai, Child of the Abyss', 'Buy at character select', 'coins', ''),
    ('Juntar Bernskyn', 'Buy at character select', 'coins', ''),
    ('Armand Callis', 'Rescue on The Great Parch (south-west of spawn)', 'rescue', ''),
    ('Hanniver Toll', 'Rescue on The Great Parch (north-east corner)', 'rescue', ''),
    ('Gotrek Gurnisson', 'Rescue on Skrappa Spill (east of spawn)', 'rescue', ''),
    ('Rostus Oxenhammer', 'Rescue on Bloodwind Spoil (north of spawn)', 'rescue', ''),
    ('Ulgromthier', 'Rescue on Under-Empire (south of spawn)', 'rescue', ''),
    ('Mistress Verentia', 'Rescue on The Twin-Tailed City (north-west, toward the Chaos Sigil)', 'rescue', ''),
    ('Shakana Goldenblade', 'Apply Slowed to 100 enemies', 'objective', ''),
    ('Sharynn Azurwrath', 'Defeat 10 Troggoths', 'objective', ''),
    ('Hendrick, the Silver Wolf', 'Defeat 10,000 Gloomspite Gitz in one run as Neave Blacktalon', 'objective', ''),
    ('Maleneth Witchblade', 'Paint pot: Leadbelcher', 'paint', ''),
    ('Lyssa Revenya', 'Paint pots: Abaddon Black, Leadbelcher, Agrax Earthshade, Mechanicus Standard Grey', 'paint', ''),
    ('Valius, the Keeper Aqshian', 'Paint pots: Leadbelcher, Celestra Grey, Reikland Fleshshade, Retributor Armour, Drakenhof Nightshade, Runelord Brass', 'paint', ''),
    ('Major Docheval', 'Morph Juntar Bernskyn after collecting Amberbone', 'secret', 'evolutions'),
    ('Lord-Commander Bastian Carthalos', 'Evolve the Stormcharged Warhammer', 'secret', 'evolutions'),
    ('Celestant-Prime, Hammer of Sigmar', 'Evolve Uskavar the Sunderer', 'secret', 'evolutions'),
    ('Yndrasta, the Celestial Spear', 'Defeat a Mangler Squig on Gnarlwood', 'secret', ''),
]
PAINT = [
    ('Abaddon Black', 'Pick up on Imperial Bastion (north-west)'),
    ('Leadbelcher', 'Pick up on The Great Parch (north-east, near the Bandolier)'),
    ('Agrax Earthshade', 'Defeat 10,000 enemies with Nuln Oil'),
    ('Celestra Grey', 'Defeat 10,000 enemies on Ork Stronghold'),
    ('Reikland Fleshshade', 'Defeat 10,000 enemies with D6 Dice'),
    ('Rakarth Flesh', 'Defeat 10,000 enemies on Gnarlwood'),
    ('Mephiston Red', 'Use the Onslaught pickup (syringe, 40K) 10 times'),
    ('Drakenhof Nightshade', 'Use the Suffocating Gravetide pickup (green skull, AoS) 10 times'),
    ('Macragge Blue', 'Defeat 10,000 Tyranids as an Ultramarines champion (e.g. Malum Caedo)'),
    ('Retributor Armour', 'Defeat 10,000 Skaven as a Stormcast champion (e.g. Neave Blacktalon)'),
    ('Mechanicus Standard Grey', 'Defeat a Carnifex as Technoarcheologist Daedalosus'),
    ('Runelord Brass', 'Defeat a Plague Furnace as Gotrek Gurnisson'),
]
LABEL = {'start': 'Start', 'coins': 'Coins', 'rescue': 'Rescue', 'objective': 'Objective', 'paint': 'Paint pots', 'secret': 'Secret'}


def table(rows, uni):
    body = ''
    for name, how, kind, page in rows:
        link = f' <a href="/warhammer-survivors/{page}/">guide →</a>' if page else ''
        body += (f'<tr data-kind="{kind}"><td><strong>{escape(name)}</strong></td><td><span class="kind kind-{kind}">{LABEL[kind]}</span></td>'
                 f'<td>{escape(how)}{link}</td></tr>')
    return (f'<div class="table-wrap" tabindex="0" role="region" aria-label="{uni} champions and unlock conditions, scroll horizontally">'
            f'<table class="char-table"><thead><tr><th>Champion</th><th>Type</th><th>How to unlock</th></tr></thead><tbody>{body}</tbody></table></div>')


def body():
    n40, naos = len(K40), len(AOS)
    paint = ''.join(f'<tr><td><strong>{escape(p)}</strong></td><td>{escape(h)}</td></tr>' for p, h in PAINT)
    return f'''<main id="main" class="wrap"><header class="article-head" id="guide"><p>WARHAMMER SURVIVORS · ALL CHAMPIONS</p><h1>Warhammer Survivors characters: all {n40 + naos} champions and how to unlock them</h1><div class="answer"><p><strong>{n40} champions in Warhammer 40,000 and {naos} in Age of Sigmar.</strong> Most unlock by rescuing them on a stage, finishing an Objective or collecting Paint Pots; a few are bought with coins. Each universe tracks its own unlocks.</p></div><p class="byline">Megabonk.org editors · Updated 13 November 2026 · Release v2.1</p></header>
<nav class="toc" aria-label="On this page"><a href="#k40">40K champions</a><a href="#aos">Age of Sigmar champions</a><a href="#paint">Paint pots</a><a href="#rescue">How rescues work</a></nav>
<div class="article-layout"><article class="prose">
<section id="quick"><h2>Fastest unlocks first</h2><ol><li><strong>Buy Amalia Novena (400 coins)</strong> in 40K: strong early and needed for the <a href="/warhammer-survivors/followers/">follower objectives</a>.</li><li><strong>Rescue the easy captives</strong>: Kozlowski and the Legend of Catachan on Imperial Bastion, K9 Mastiff on Gallowdark; Armand Callis and Hanniver Toll on The Great Parch.</li><li><strong>Grab Abaddon Black</strong> on Imperial Bastion and <strong>Leadbelcher</strong> on The Great Parch: two Paint Pots unlock Black Templars Castellan and Maleneth Witchblade straight away.</li><li><strong>Let totals run in the background</strong>: Tor Garadon (10,000 kills) and the 10,000-kill Paint Pots finish on their own over several runs.</li></ol></section>
<section id="k40"><h2>Warhammer 40,000 champions ({n40})</h2>{table(K40, "Warhammer 40,000")}</section>
<section id="aos"><h2>Age of Sigmar champions ({naos})</h2>{table(AOS, "Age of Sigmar")}</section>
<section id="paint"><h2>Where to get every Paint Pot</h2><p>Paint Pots are permanent unlocks shared by every champion that needs them. Two are pickups on a stage; the rest come from kill totals or bosses.</p><div class="table-wrap" tabindex="0" role="region" aria-label="Paint pot sources, scroll horizontally"><table><thead><tr><th>Paint pot</th><th>How to get it</th></tr></thead><tbody>{paint}</tbody></table></div><figure><img src="{A}objectives-ingame.webp" width="570" height="570" alt="In-game Objectives list showing unlock conditions" loading="lazy" decoding="async"><figcaption>Every unlock condition is listed in the Objectives menu of that universe.</figcaption></figure></section>
<section id="rescue"><h2>How rescues work</h2><ol><li>Start the named stage in the right universe with any champion.</li><li>Pause and open the <strong>Map</strong> tab: captives show as a green <strong>?</strong>. Some only appear after you pick up a map relic (the Legend of Catachan needs the Signum Array from Ork Stronghold).</li><li>Clear the enemies around the captive and walk up to them; they join your run.</li><li>Finish the run. Rescued champions appear in Character Select, some with a coin price.</li></ol><figure><img src="{A}catachan/imperial-bastion-map.webp" width="800" height="377" alt="Imperial Bastion pause map with a captive marked by a question mark" loading="lazy" decoding="async"><figcaption>Captives are the green ? on the pause map.</figcaption></figure></section>
<section id="next"><h2>Next steps</h2><p><a href="/warhammer-survivors/legend-of-catachan/">Full Legend of Catachan route →</a></p><p><a href="/warhammer-survivors/evolutions/">All 38 weapon evolutions →</a></p><p><a href="/warhammer-survivors/tips/">First-hour tips →</a></p></section>
<p><a href="#guide">Back to top ↑</a></p></article></div></main>'''


CSS = '<style>.char-table td:first-child{white-space:nowrap}.kind{display:inline-block;font-size:11px;letter-spacing:.06em;padding:2px 7px;border:1px solid var(--edge);white-space:nowrap}.kind-rescue{color:#8ec5e0;border-color:#2c5a70}.kind-objective{color:#e8c874;border-color:#7a6430}.kind-paint{color:#e07a6a;border-color:#7b2b22}.kind-secret{color:#c9a0e8;border-color:#5a3a78}.kind-coins,.kind-start{color:#b9ae94}@media(max-width:600px){.char-table td:first-child{white-space:normal}}</style>'


def build():
    template = (ROOT / 'warhammer-survivors/tips/index.html').read_text(encoding='utf8')
    head, rest = template.split('<main id="main"', 1)
    footer = '<footer' + rest.split('<footer', 1)[1]
    title = 'Warhammer Survivors Characters: All Champions & How to Unlock'
    desc = f'All {len(K40) + len(AOS)} Warhammer Survivors champions in 40K and Age of Sigmar, with every unlock condition, rescue location and Paint Pot source.'
    head = re.sub(r'<title>.*?</title>', f'<title>{title}</title>', head)
    head = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m[1] + desc, head)
    for prop, val in (('title', title), ('description', desc), ('url', 'https://megabonk.org' + ROUTE)):
        head = re.sub(r'(<meta property="og:' + prop + r'" content=")[^"]*', lambda m: m[1] + val, head)
    head = re.sub(r'(<link rel="canonical" href=")[^"]*', lambda m: m[1] + 'https://megabonk.org' + ROUTE, head)
    head = re.sub(r'<script defer src="/assets/yt-embed\.js"></script>|<link rel="stylesheet" href="/assets/yt-embed\.css[^"]*">\n?', '', head)
    head = re.sub(r'<script type="application/ld\+json"[^>]*>.*?</script>', '', head, flags=re.S)
    head = head.replace('</head>', CSS + '</head>', 1)
    head = re.sub(r'<body[^>]*>', '<body data-v321="1" data-format="database" class="guide-layout wh-theme wh-guide">', head, count=1)
    path = ROOT / 'warhammer-survivors/characters/index.html'
    path.parent.mkdir(parents=True, exist_ok=True)
    write_html(path, head + body() + footer, encoding='utf8')


if __name__ == '__main__':
    build()
