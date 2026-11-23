"""Risk of Rain 2 Bulwark's Ambry (English): entrance, Artifact Keys and reward.

Facts come from the sources listed in SOURCES and are kept to what they state. No in-game testing.
The Russian guide at /risk-of-rain-2/ru/bulwarks-ambry/ covers the same task in Russian.
"""
from html import escape

ROUTE = '/risk-of-rain-2/bulwarks-ambry/'
TITLE = "Risk of Rain 2 Bulwark's Ambry: Entry, Keys and Reward"
DESC = ("How to enter Bulwark's Ambry in Risk of Rain 2: the Compound Generator on stage 5, the 3x3 code, "
        "the four Artifact Keys and what you get when the Reliquary breaks.")

SABO = 'https://sabo.gg/en/guides/ror2/routes/bulwarks-ambry/'
SABO_ART = 'https://sabo.gg/en/guides/ror2/artifacts/'
FANDOM = "https://riskofrain2.fandom.com/wiki/Bulwark's_Ambry"

SOURCES = [
    (SABO, "sabo.gg Bulwark's Ambry route", 'entrances, code rules, four keys, reward and exit; read 23 Nov 2026; no patch number stated'),
    (FANDOM, "Risk of Rain 2 Wiki (Fandom): Bulwark's Ambry", "entrances and key sequence match the search-result summary; the page itself returned an error when opened, so it was not read in full"),
]

ENTRANCES = [
    ('Sky Meadow (stage 5)', 'Drop through a hole in the floor into a room under the map with the Compound Generator and a laptop.'),
    ('Helminth Hatchery (stage 5, Seekers of the Storm)', 'The Compound Generator is at the very top of the map.'),
    ('Any other stage', 'No entrance. A normal Teleporter does not lead to the Ambry.'),
]

STUCK = [
    ('No portal after using the laptop', 'Recheck all nine cells. Each press cycles square, circle, triangle, diamond, and the code is read top to bottom, row by row.'),
    ('Enemies appear but the Reliquary takes no damage', 'Normal attacks do nothing to it. Pick up the Artifact Key that dropped and interact with the Reliquary while holding it.'),
    ('A teammate lost their key', 'Using any key removes every key from all players and the ground, by design. Use the current key first, then wait for the next drop.'),
    ('The artifact is not in your list next run', 'Pick it up from the destroyed Reliquary first, then enable it in the artifact menu before starting the run.'),
]


def _rows(pairs, head):
    body = ''.join(f'<tr><th scope="row">{escape(a)}</th><td>{escape(b)}</td></tr>' for a, b in pairs)
    return (f'<div class="table-wrap" role="region" aria-label="{escape(head[2])}" tabindex="0"><table><thead><tr>'
            f'<th scope="col">{escape(head[0])}</th><th scope="col">{escape(head[1])}</th></tr></thead><tbody>{body}</tbody></table></div>')


def _sources():
    return ''.join(f'<li><a href="{u}" target="_blank" rel="noopener noreferrer">{escape(l)} ↗</a> — {escape(d)}</li>'
                   for u, l, d in SOURCES)


def main_html():
    return f"""<main class="wrap" id="main">
<header class="article-head" id="guide"><p class="eyebrow">INDEPENDENT PLAYER GUIDE · RISK OF RAIN 2</p><h1>Risk of Rain 2 Bulwark's Ambry: entry, keys and reward</h1>
<p class="answer"><strong>Short answer:</strong> On stage 5 (Sky Meadow or Helminth Hatchery) find the Compound Generator, enter the artifact's nine-cell code and use the laptop to open the portal. Inside, use the four Artifact Keys on the Artifact Reliquary one after another, then pick up the artifact it leaves.</p>
<p class="byline">Compiled from published guides, not our own playthrough. Updated 24 November 2026. <a href="/risk-of-rain-2/ru/bulwarks-ambry/" lang="ru">Читать на русском</a></p></header>
<section id="entrance"><h2>Where the entrance is</h2>
<p>Bulwark's Ambry is a hidden realm opened from the Compound Generator, and the generator exists only on two fifth-stage maps.</p>
{_rows(ENTRANCES, ('Where you are', 'What to do', 'Entrance locations'))}
</section>
<section id="code"><h2>Entering the code</h2>
<p>You need the code of the artifact you want to unlock; the codes are listed in <a href="{SABO_ART}" target="_blank" rel="noopener noreferrer">sabo.gg's artifact guide ↗</a>. The code is a 3×3 grid of cells. Each press cycles a cell through square, circle, triangle, then diamond, and the code is read top to bottom, row by row. When the grid matches, use the laptop. A correct code opens a purple portal; enter it.</p>
<p>Rebirth is the exception: it has no code. According to sabo.gg you get it by offering an item to the Shrine of Rebirth at the end of Prime Meridian, a Seekers of the Storm map.</p>
</section>
<section id="trial"><h2>The trial: four Artifact Keys</h2>
<ol>
<li>Pick up the first <strong>Artifact Key</strong> in front of the Artifact Reliquary.</li>
<li>Interact with the Reliquary while holding the key. Enemies start to spawn.</li>
<li>Kill enemies until one drops the next key, pick it up right away and return to the Reliquary.</li>
<li>Repeat until the fourth key is used. Each key removes a quarter of the Reliquary's health.</li>
</ol>
<p>Only keys damage the Reliquary, so regular attacks are wasted. Using a key also removes every other key held by all players or lying on the ground, so do not stockpile them.</p>
<p>The artifact you are unlocking is already active during the trial. sabo.gg notes that this is easy with Command and harder with Frailty or Death.</p>
</section>
<section id="stuck"><h2>If the trial stalls</h2>
{_rows(STUCK, ('What you see', 'What to check', 'Troubleshooting checks'))}
</section>
<section id="reward"><h2>Reward and exit</h2>
<p>Pick up the artifact from the destroyed Reliquary before leaving. You keep it permanently and can enable it in the menu before any run; in co-op the group can enable any artifact that any player owns, per sabo.gg. The portal after the Reliquary leads to a stage 1 map, and leaving the Ambry this way counts as a loop. Your run continues with everything you carry.</p>
</section>
<section id="method"><h2>How this was checked</h2>
<p>Both sources agree on the Sky Meadow and Helminth Hatchery entrances and on four keys. Neither states a game patch number, so check the current patch notes if a step behaves differently. We did not test this in game.</p>
</section>
<section id="sources"><h2>Sources and dates</h2><ul>{_sources()}</ul></section>
</main>"""


def page(frame, decorate):
    return decorate(ROUTE, frame(ROUTE, TITLE, DESC, main_html(), og='article'))
