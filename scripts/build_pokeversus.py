"""PokéVersus playable landing: original-host click-load window, startup and identity."""
from pathlib import Path

from guide_images import decorate
from play_recommendations import recommendations, stylesheet
from site_analytics import write_html
from pokeversus_hub import hero, cards, cheat, updates, faq, manifest, build_trust

ROOT = Path(__file__).resolve().parents[1]
ROUTE = '/pokeversus/'
GAME = 'https://pokeversus.com/'
NEWS = GAME + 'js/news.js'
AD = '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8830315294299920" crossorigin="anonymous"></script>'


def ext(url, label):
    return f'<a href="{url}" target="_blank" rel="noopener noreferrer">{label} ↗<span class="sr-only"> (external website, opens in a new tab)</span></a>'


def ref(i):
    return f'<sup class="ref"><a href="#source-{i}" aria-label="Source {i}">[{i}]</a></sup>'


def sources(items):
    lis = ''.join(f'<li id="source-{i}">{ext(u, l)} — {d}</li>' for i, (u, l, d) in enumerate(items, 1))
    return f'<section class="sources" id="sources"><h2>Sources &amp; verification</h2><p>By Megabonk.org · checked 5 November 2026. Independent, source-based startup guide with an original-host inspection. PokéVersus is an unofficial fan game by Fl3xix; Pokémon names and artwork belong to Nintendo, Creatures Inc., GAME FREAK and The Pokémon Company. This guide is unaffiliated with any of them.</p><ol>{lis}</ol><a class="back" href="#guide">Back to page ↑</a></section>'


A = '/assets/pokeversus/'


def shell(route, title, desc, body, error=False, trust=False):
    """全专区外壳：theme.css 全部页面，hub.css 与 play.css/play.js 仅首页；导航与页脚由 register_page.py 按页面清单覆盖。"""
    home = route == ROUTE
    css = f'<link rel="preload" href="/assets/fonts/jersey10-400-latin.woff2" as="font" type="font/woff2" crossorigin><link rel="stylesheet" href="/assets/guide-article-layout.css"><link rel="stylesheet" href="{A}theme.css">' + (f'<link rel="stylesheet" href="{A}hub.css"><link rel="stylesheet" href="{A}play.css">' if home else '')
    og = '' if (error or trust) else f'<meta property="og:type" content="website"><meta property="og:title" content="{title}"><meta property="og:description" content="{desc}"><meta property="og:url" content="https://megabonk.org{route}"><meta property="og:image" content="https://megabonk.org/assets/pokeversus/starters-1280.webp">'
    cls = 'guide-layout pv-theme ' + ('pv-hub' if home else 'pv-guide') + (' pv-trust' if trust else '')
    extra = '<meta name="robots" content="noindex,follow">' if error else '' if trust else AD
    play = f'<script defer src="{A}play.js"></script>' if home else ''
    page = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title>'
            f'<meta name="description" content="{desc}"><link rel="canonical" href="https://megabonk.org{route}">{og}{css}{extra}{play}</head>'
            f'<body class="{cls}"><a class="skip" href="#main">Skip to content</a><header class="top"><div class="wrap"><a class="brand" href="{ROUTE}" aria-label="PokéVersus guide home"><span>PokéVersus<small>Play &amp; guide</small></span></a>'
            '<nav class="desktop-nav" aria-label="Main navigation"></nav><details class="mobile-nav"><summary>Menu</summary><nav class="mobile-links" aria-label="Mobile navigation"></nav></details></div></header>'
            '<main class="wrap" id="main">' + body + '</main><footer class="footer"></footer></body></html>')
    return stylesheet(page) if home else page


def page():
    m = manifest()
    body = f'''{hero(ref(1))}{cards(m)}
<section class="game-panel" id="game-panel" aria-label="PokéVersus game window" data-mode="normal"><div class="game-screen" id="play"><div class="game-cover" id="game-cover"><img src="/assets/pokeversus/hub-1280.webp" srcset="/assets/pokeversus/hub-800.webp 800w, /assets/pokeversus/hub-1280.webp 1280w" sizes="(max-width:900px) calc(100vw - 36px), 620px" width="1280" height="800" alt="" loading="lazy"><div class="cover-content"><h2>PokéVersus</h2><p>3v3 brawls, weekend raids and the 10-player Toxic Fog — in your browser.</p><button class="play-button" id="game-launch" type="button">Play PokéVersus →</button><p class="cover-note">Click to load the original at pokeversus.com.<br>Guest play needs no account; progress stays in this browser unless you sign in.</p></div></div><iframe id="game-frame" title="PokéVersus original game hosted by pokeversus.com" data-src="{GAME}" allow="autoplay; fullscreen; gamepad" allowfullscreen referrerpolicy="strict-origin-when-cross-origin" hidden></iframe></div><div class="game-meta"><div class="game-tools"><button id="game-expand" type="button" aria-pressed="false" disabled>Expand game</button><button id="game-minimize" type="button" aria-expanded="true" aria-controls="play" disabled>Hide game</button>{ext(GAME, 'pokeversus.com · open original')}</div><p id="game-status" role="status" aria-live="polite">Click Play to connect. Hiding keeps the session connected; it does not pause the game.</p><p>Keep this host and browser profile for your progress. A frame and a separate tab may receive different storage treatment. <a href="/privacy-policy#pokeversus">Game-window privacy</a>.</p><noscript><p>{ext(GAME, 'pokeversus.com · play the original in its own tab')}</p></noscript></div></section>
<div class="game-dock" id="game-dock" hidden><span>PokéVersus hidden</span><button id="game-restore" type="button">Return to game ↑</button></div>
{cheat(ref(2))}{updates(m)}
<article class="play-notes" data-play-background>
<section id="start"><h2>From the login window to your first match</h2><p>These steps follow the original v2.37 client inspected on 5 November 2026, entered as a guest. This is a startup and menu check — no full or ranked match is claimed. {ref(1)}</p><ol><li>Click <strong>Play</strong> above and wait for the login window: <strong>Sign in with Google</strong>, <strong>Sign in with email</strong>, or <strong>Play as guest</strong>. The window states that an account keeps progress in the cloud and works on any device, while a guest saves only in this browser. {ref(1)}</li><li>Choose a trainer name — the game says it must be unique.</li><li>Pick your <strong>3 starter Pokémon, one of each type</strong>: Grass, Fire and Water offer nine starters each (27 total, from Bulbasaur, Charmander and Squirtle to Sprigatito, Fuecoco and Quaxly). All three evolve during matches. {ref(1)}</li><li>You land in the hub: your lead Pokémon stands between two <strong>Invite</strong> slots, and the side menu lists Pokémon, Missions, Club (clan wars), Gachas, Achievements, Friends, Ranking and Chat. A season Pass sat above the mode selector at the time of checking (Season 2 on 5 November). {ref(1)}</li><li>The mode panel shows what is live right now — it defaulted to <strong>Random</strong>, which pools everyone into one mode every 5 minutes and excludes Toxic Fog and the duel sizes. Tap it for the full list below.</li></ol><h3 id="modes">The mode list</h3><div class="table-wrap" tabindex="0" role="region" aria-label="PokéVersus mode list as of 5 November 2026"><table class="pv-identity"><thead><tr><th>Mode</th><th>What the client says it is</th></tr></thead><tbody>
<tr><td>Online / Vs bots</td><td>Live matches, or a bot practice lobby.</td></tr>
<tr><td>Random</td><td>Every 5 minutes all queued players go to the same mode so lobbies fill; Toxic Fog and 2v2/1v1 duels are excluded.</td></tr>
<tr><td>Catch the Balls</td><td>3v3: take 10 Poké Balls from the central machine and hold them for 15 seconds.</td></tr>
<tr><td>Toxic Fog</td><td>Free-for-all for 10 players (Solo or Duo): break crates for Rare Candies while the toxic fog closes in; last one standing wins.</td></tr>
<tr><td>Wake Up Snorlax</td><td>3v3: each team protects its sleeping Snorlax; first team to knock out the enemy Snorlax wins.</td></tr>
<tr><td>Voltorb Ball</td><td>3v3: carry the Voltorb into the enemy goal, first to 2 scores wins — it explodes if you hold it more than 10 seconds.</td></tr>
<tr><td>Territory</td><td>3v3: stay in the central zone with no enemies inside; first team to 100% wins.</td></tr>
<tr><td>Team Duel</td><td>3v3 (the panel also lists 2v2 and 1v1): most knockouts in 2.5 minutes, or first to 15.</td></tr>
<tr><td>Knockout</td><td>3v3 with no respawns; knock out all three rivals to take the round, best of 3.</td></tr>
<tr><td>Gigantamax Raid</td><td>Weekends only — the panel said “Come back on Saturday!” on a Wednesday check.</td></tr>
</tbody></table></div><p>Controls are advertised as WASD + mouse on desktop, touch controls with a landscape prompt on phones, and gamepad mapping in settings. We inspected menus at desktop and phone widths; this is not a physical-phone or controller benchmark. {ref(1)}{ref(3)}</p></section>
<section id="account"><h2>What is saved where</h2><p>The login window is explicit: <strong>guest progress is saved only in this browser</strong>, so keep the same host and browser profile and do not clear site data mid-run. With an account (Google or email), progress is stored in the cloud and the game advertises playing on any device. {ref(1)}</p><p>Friends, Club (clans), Rankings and the season Pass are account features advertised in the hub; the header also links the project's Discord server. Account creation, clan wars, matchmaking and cross-device saves are not verified on this page. If the framed window stalls, {ext(GAME, 'open the original in its own tab')} before troubleshooting anything else — an outage on the original site cannot be fixed from this page. {ref(1)}</p></section>
<section id="which-game"><h2>Check the name before following a guide</h2><div class="table-wrap" tabindex="0" role="region" aria-label="Identify similarly named games"><table class="pv-identity"><thead><tr><th>Name you saw</th><th>What it actually is</th><th>Route</th></tr></thead><tbody>
<tr><td>PokéVersus / Poke Versus</td><td>This game: a free 3v3 Pokémon browser brawler by Fl3xix at pokeversus.com, with a 10-player Toxic Fog and weekend Gigantamax raids (client v2.37).</td><td><a href="#play">Window above</a></td></tr>
<tr><td>PokéVersus arena / Poke versus arena</td><td>This page's game: the 3v3 brawler with the original client at pokeversus.com. “Arena” is not part of its title; Poke Arena 2D is a different game on this site with its own host and controls.</td><td><a href="#play">Window above</a> · <a href="/pokearena-2d/">Poke Arena 2D</a></td></tr>
<tr><td>Pokeverse / Pokémon Pokeverse</td><td>A different project: pokeverse.quest advertises a Pokémon MMORPG with its own downloadable clients.</td><td>{ext('https://pokeverse.quest/', 'pokeverse.quest')}</td></tr>
<tr><td>“PokeVersus!” on PokéCommunity</td><td>An unrelated forum voting game (pick which Pokémon would win) running since January 2024.</td><td>{ext('https://www.pokecommunity.com/threads/pokeversus.525785/', 'PokéCommunity thread')}</td></tr>
<tr><td>“Pokémon Brawl Stars”</td><td>A discovery phrase, not one game: players hunting a Pokémon version of Brawl Stars will find PokéVersus is the closest playable browser brawler. An unfinished Unity fan project of that name exists on a Spanish forum; it is not this browser game. {ref(6)}</td><td><a href="#play">Window above</a></td></tr>
<tr><td>Poké Arena 2D · PokéIsaac · PokeBonk · PokéSurvivor</td><td>Other free Pokémon browser games on this site, each with its own host, controls and progress.</td><td><a href="/pokearena-2d/">Poké Arena 2D</a> · <a href="/poke-isaac/">PokéIsaac</a> · <a href="/pokebonk/play/">PokeBonk window</a> · <a href="/poke-survivor/play/">PokéSurvivor window</a></td></tr>
</tbody></table></div><p>Shared names do not mean shared accounts, saves or rosters — progress does not move between any of these games. {ref(4)}{ref(5)}</p></section>
{faq(m)}
{sources([
    (GAME, 'PokéVersus · original game', 'Original client v2.37 (footer version): login window, trainer-name step, starter selection (9 Grass, 9 Fire, 9 Water), hub layout and the full mode list inspected 5 November 2026 in desktop Chrome, entered as a guest; no full or ranked match played. SINGLE_SOURCE for in-client flows.'),
    (NEWS, 'PokéVersus · patch feed (news.js)', 'Version constant 2.37 with entries dated to 4 November 2026, read 5 November 2026. High-change file — re-check before relying on version specifics.'),
    ('https://pokeversus.net/', 'PokéVersus.net · independent guide', 'Third-party site that states it is not affiliated with the developer; used to cross-check that our mode-list reading is not unique to one session. Read 5 November 2026.'),
    ('https://pokeverse.quest/', 'Pokeverse · separate MMORPG project', 'Checked 5 November 2026 for the name-disambiguation row. A different game with its own clients.'),
    ('https://www.pokecommunity.com/threads/pokeversus.525785/', 'PokéCommunity · “PokeVersus!” thread', 'Forum voting game started January 2024; unrelated to this browser game. Checked 5 November 2026 via a search snapshot of the thread index.'),
    ('https://whackahack.com/foro/threads/unity-pokemon-brawl-stars.66439', 'Whack a Hack · “Pokémon Brawl Stars” project', 'Spanish fan-project thread for an unfinished Unity game of that name; not playable in a browser. Checked 5 November 2026 via a search snapshot.'),
])}</article>
{recommendations('pokeversus')}'''
    return shell(ROUTE, 'PokéVersus: Play Online &amp; First-Match Guide | Megabonk',
                 'Play PokéVersus in an original-host window, pick one starter of each type, check guest and account saves, and tell apart similarly named Pokémon games.',
                 body)


def build():
    f = ROOT / 'pokeversus/index.html'
    f.parent.mkdir(exist_ok=True)
    write_html(f, decorate(ROUTE, page()), encoding='utf-8')
    build_trust(shell, write_html)
    import re, subprocess, sys
    subprocess.run([sys.executable, str(Path(__file__).resolve().parent / 'register_page.py'), str(ROOT), 'pokeversus'], check=True, stdout=subprocess.DEVNULL)
    from game_seo import edit as seo_edit
    for fp in (ROOT / 'pokeversus').rglob('index.html'):
        t0 = fp.read_text(encoding='utf-8'); n0 = seo_edit(fp, t0)
        if n0 != t0:
            fp.write_text(n0, encoding='utf-8')
    f = ROOT / 'index.html'
    text = f.read_text(encoding='utf-8')
    if 'id="pokeversus-game-entry"' not in text:
        text = text.replace('<div class="route-grid">', '<div class="route-grid"><a class="route-card" id="pokeversus-game-entry" href="/pokeversus/"><h3>PokéVersus</h3><p>Free 3v3 Pokémon browser brawler: play the original in a click-loaded window, pick one starter of each type and check same-name games.</p><span class="route-link">Play &amp; start guide →</span></a>', 1)
        write_html(f, text, encoding='utf-8')
    f = ROOT / 'privacy-policy.html'
    text = f.read_text(encoding='utf-8')
    if 'id="pokeversus"' not in text:
        text = text.replace('</body>', '<h2 id="pokeversus">PokéVersus game window</h2><p>Updated 5 November 2026. Clicking Play loads the original game from pokeversus.com, including its resources and services. Login, guest play and any account choices happen inside that window and belong to the original project; hiding the window keeps the same frame connected and does not pause the game — close or leave the page to end the session. Framed and separate-tab storage can differ; we cannot read or recover game saves, and guest progress is saved only in the player\'s own browser by the game itself. Ordinary page integrations inherit this site\'s existing AdSense and site-wide Umami services described above.</p></body>', 1)
        write_html(f, text, encoding='utf-8')
    print('Built PokéVersus playable landing; patched root entry/privacy.')


if __name__ == '__main__':
    build()
