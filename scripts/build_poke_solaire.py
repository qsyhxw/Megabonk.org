"""PokéSolaire playable landing: original-host click-load window, startup and identity."""
import json
from html import escape
from pathlib import Path

from guide_images import decorate
from play_recommendations import recommendations, stylesheet
from site_analytics import write_html

ROOT = Path(__file__).resolve().parents[1]
ROUTE = '/poke-solaire/'
MANIFEST = json.loads((ROOT / 'data/poke-solaire-pages.json').read_text(encoding='utf-8'))
CHECKED_HOST = '22 November 2026'
GAME = 'https://pokesolaire.com/'
REDDIT = 'https://www.reddit.com/r/playmygame/comments/1xlk2ga/pok%C3%A9solaire_i_built_a_browserbased_pok%C3%A9mon/'
AD = '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8830315294299920" crossorigin="anonymous"></script>'

TITLE = 'PokéSolaire: Play the Original & Start Guide | Megabonk'
DESC = 'Play PokéSolaire in an original-host window, switch the client to English from Settings, keep guest saves safe, and tell it apart from same-name games.'


def ext(url, label):
    return f'<a href="{url}" target="_blank" rel="noopener noreferrer">{label} ↗<span class="sr-only"> (external website, opens in a new tab)</span></a>'


def ref(i):
    return f'<sup class="ref"><a href="#source-{i}" aria-label="Source {i}">[{i}]</a></sup>'


def sources(items):
    lis = ''.join(f'<li id="source-{i}">{ext(u, l)} — {d}</li>' for i, (u, l, d) in enumerate(items, 1))
    return f'<section class="sources" id="sources"><h2>Sources &amp; verification</h2><p>By Megabonk.org · checked 5 November 2026. Independent, source-based startup guide with an original-host inspection. PokéSolaire is an unofficial fan game by Alonso y Roa; Pokémon names and artwork belong to Nintendo, Creatures Inc., GAME FREAK and The Pokémon Company. This guide is unaffiliated with any of them.</p><ol>{lis}</ol><a class="back" href="#guide">Back to page ↑</a></section>'


NAV = ''.join(f'<a href="{x["href"]}">{escape(x["label"])}</a>' for x in MANIFEST['nav_extra'])


def shell(title, desc, body):
    return stylesheet(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><meta name="description" content="{desc}"><link rel="canonical" href="https://megabonk.org{ROUTE}"><meta property="og:type" content="website"><meta property="og:title" content="{title}"><meta property="og:description" content="{desc}"><meta property="og:url" content="https://megabonk.org{ROUTE}"><meta property="og:image" content="https://megabonk.org/assets/poke-solaire/hub-1280.webp"><link rel="preload" href="/assets/fonts/pixelify-sans-700.woff2" as="font" type="font/woff2" crossorigin><link rel="stylesheet" href="/assets/guide-article-layout.css"><link rel="stylesheet" href="/assets/poke-solaire/theme.css"><link rel="stylesheet" href="/assets/poke-solaire/hub.css"><link rel="stylesheet" href="/assets/poke-solaire/play.css">{AD}<script defer src="/assets/poke-solaire/play.js"></script></head><body class="guide-layout psol-theme psol-hub psol-guide"><a class="skip" href="#main">Skip to content</a><header class="top"><div class="wrap"><a class="brand" href="/poke-solaire/" aria-label="PokéSolaire guide home"><span>Poké<b>Solaire</b><small>Unofficial guide</small></span></a><nav class="desktop-nav" aria-label="Main navigation">{NAV}</nav><details class="mobile-nav"><summary>Menu</summary><nav class="mobile-links" aria-label="Mobile navigation">{NAV}</nav></details></div></header><main id="main">{body}</main><footer class="footer"><div class="wrap footer-grid"><div><strong>Find your next game.</strong><p>Independent editorial by Megabonk.org. The original project operates the game and its services.</p><a href="/#wiki-start">More games &amp; guides →</a></div><nav aria-label="Site information"><a href="/about/">About</a><a href="/contact/">Contact</a><a href="/privacy-policy#poke-solaire">Privacy</a></nav></div></footer></body></html>''')

ICON = {
    'play': '<path d="M8 5v14l11-7z"/>',
    'steps': '<path d="M4 18h5v-5h5V8h6"/><path d="M4 18v2h16"/>',
    'lang': '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18"/>',
    'pad': '<rect x="3" y="8" width="18" height="10" rx="3"/><path d="M8 11v4M6 13h4M16 12h.01M18 14h.01"/>',
    'save': '<path d="M5 3h11l3 3v15H5z"/><path d="M8 3v6h7V3M8 21v-7h8v7"/>',
    'ask': '<circle cx="12" cy="12" r="9"/><path d="M9.5 9.5a2.5 2.5 0 115 0c0 1.8-2.5 2-2.5 4M12 17h.01"/>',
}


def mhref(h):
    return h if h.startswith('/') else ROUTE + h


def cards_html():
    items = ''.join(
        f'<li><a class="psol-task" href="{escape(mhref(c["href"]), quote=True)}"><span class="ico"><svg viewBox="0 0 24 24" aria-hidden="true">{ICON[c["icon"]]}</svg></span>'
        f'<strong>{escape(c["label"])}</strong><span class="d">{escape(c["blurb"])}</span></a></li>' for c in MANIFEST['cards'])
    return (f'<section class="psol-section" id="tasks" data-play-background><div class="wrap"><h2>Pick a task</h2>'
            f'<p class="psol-lede">Six answers from the original v1.8 client check.</p><ul class="psol-tasks">{items}</ul></div></section>')


def preview_html():
    keys = [('Roll', 'A / ✕'), ('Sprint', 'B / ○'), ('Block / parry', 'RB / R1'), ('Light attack', 'X / □'),
            ('Heavy attack', 'Y / △'), ('Special / interact', 'LB / L1'), ('Switch type', 'View / Share · Tab on keyboard'), ('Lock on', 'R3')]
    dl = ''.join(f'<div><dt>{a}</dt><dd>{b}</dd></div>' for a, b in keys)
    return ('<section class="psol-section" id="facts" data-play-background><div class="wrap"><h2>Quick facts</h2><div class="psol-preview">'
            f'<div class="psol-card"><h3>Gamepad mapping in Settings</h3><dl class="psol-keys">{dl}</dl>'
            f'<p>English UI read 5 November 2026; the Tab key switch comes from the developer&rsquo;s post. <a href="#controls">Controls in context →</a>{ref(1)}{ref(4)}</p></div>'
            '<div class="psol-card"><h3>Latest client note</h3><b class="psol-ver">v1.8</b>'
            '<p>&ldquo;El juego en inglés, portugués y francés&rdquo;, dated 1 November 2026 in the in-game update notes.'
            f' <a href="#language">Switch the language →</a>{ref(2)}</p></div></div></div></section>')


def updates_html():
    rows = sorted(MANIFEST['updates'], key=lambda u: u['date'], reverse=True)
    li = ''.join(f'<li><time datetime="{u["date"]}">{u["date"]}</time><span>{escape(u["text"])} <a href="{escape(mhref(u["href"]), quote=True)}">{escape(u["label"])} →</a></span></li>' for u in rows)
    return f'<section class="psol-section" id="updates" data-play-background><div class="wrap"><h2>Latest updates</h2><ul class="psol-updates">{li}</ul></div></section>'


def faq_html():
    items = ''.join(f'<details><summary>{escape(f["q"])}</summary><p>{escape(f["a"])}</p><a class="more" href="{escape(mhref(f["href"]), quote=True)}">Full answer →</a></details>' for f in MANIFEST['faq'])
    return f'<section class="psol-faq" id="faq" data-play-background><h2>Quick answers</h2>{items}</section>'


def page():
    body = f'''<section class="psol-hero" id="guide" data-play-background><div class="wrap psol-hero-in"><div><p class="eyebrow">Pokémon browser roguelike · soulslike · unofficial guide</p><h1>PokéSolaire</h1><p class="psol-sub">Play &amp; start guide</p>
<ul class="psol-chips"><li>Free in your browser</li><li>2.5D soulslike</li><li>Guest play</li></ul>
<p class="psol-deck">A free fan-made 2.5D action roguelike by Alonso y Roa: dodge, parry and survive a labyrinth of rooms that keeps getting harder, with evolutions mid-run. Play the original below or open it in its own tab; guest play needs no account. {ref(1)}</p>
<div class="psol-cta"><a class="psol-btn" href="#play">Play the original ↓</a><a class="psol-btn ghost" href="#start">First session</a></div>
<p class="byline">Original client v1.8 · landing page, click-to-continue screen, first-run notice, language settings and the first labyrinth room checked 5 November 2026 (open beta, in active development). The landing page and first screens are Spanish; Settings → Language switches the client to English, Português or Français. {ref(2)}</p></div>
<figure><img src="/assets/poke-solaire/hub-1280.webp" srcset="/assets/poke-solaire/hub-800.webp 800w, /assets/poke-solaire/hub-1280.webp 1280w" sizes="(max-width:900px) calc(100vw - 28px), 480px" width="1440" height="900" alt="Original PokéSolaire menu: pixel Pikachu at a campfire inside a cave, the play entry list Novedades, Sugerencias, Jugar, Huevos, Diaria, Juramentos, Ranking and Códice, and an online-players badge" fetchpriority="high"><figcaption>Original menu, 5 November 2026. Game art © Alonso y Roa / respective owners; not a promotional banner.</figcaption></figure></div></section>
<div class="psol-status" data-play-background><div class="wrap"><span><b>Browser</b> · free</span><span><b>Client</b> v1.8 checked 5 Nov</span><span class="warn"><b>Original host</b> error on 22 Nov</span><span><b>Fan guide</b> · unofficial</span></div></div>
{cards_html()}
<div class="wrap psol-play" id="play-area">
<section class="game-panel" id="game-panel" aria-label="PokéSolaire game window" data-mode="normal"><div class="game-screen" id="play"><div class="game-cover" id="game-cover"><img src="/assets/poke-solaire/hub-1280.webp" srcset="/assets/poke-solaire/hub-800.webp 800w, /assets/poke-solaire/hub-1280.webp 1280w" sizes="(max-width:900px) calc(100vw - 36px), 620px" width="1280" height="800" alt="" loading="lazy"><div class="cover-content"><h2>PokéSolaire</h2><p>Dodge, parry and climb a soulslike Pokémon labyrinth — in your browser.</p><button class="play-button" id="game-launch" type="button">Play PokéSolaire →</button><p class="cover-warn">Checked {CHECKED_HOST}: pokesolaire.com returned a deployment-disabled error, so the window may not load.</p><p class="cover-note">Click to load the original at pokesolaire.com.<br>Guest play needs no account; progress stays in this browser unless you sign in inside the game.</p></div></div><iframe id="game-frame" title="PokéSolaire original game hosted by pokesolaire.com" data-src="{GAME}" allow="autoplay; fullscreen; gamepad" allowfullscreen referrerpolicy="strict-origin-when-cross-origin" hidden></iframe></div><div class="game-meta"><div class="game-tools"><button id="game-expand" type="button" aria-pressed="false" disabled>Expand game</button><button id="game-minimize" type="button" aria-expanded="true" aria-controls="play" disabled>Hide game</button>{ext(GAME, 'pokesolaire.com · open original')}</div><p id="game-status" role="status" aria-live="polite">Click Play to connect. Hiding keeps the session connected; it does not pause the game.</p><p>Keep this host and browser profile for your progress. A frame and a separate tab may receive different storage treatment. <a href="/privacy-policy#poke-solaire">Game-window privacy</a>.</p><noscript><p>{ext(GAME, 'pokesolaire.com · play the original in its own tab')}</p></noscript></div></section>
<div class="game-dock" id="game-dock" hidden><span>PokéSolaire hidden</span><button id="game-restore" type="button">Return to game ↑</button></div>
</div>
{preview_html()}
{updates_html()}
<div class="wrap"><h2 class="psol-guide-title" id="full-guide" data-play-background>The full starting checks</h2></div>
<article class="play-notes" data-play-background><nav class="play-jump" aria-label="On this page"><a href="#start">First session</a><a href="#saves">Saves &amp; language</a><a href="#which-game">Which game?</a><a href="#sources">Sources</a></nav>
<section id="start"><h2>From the click gate to your first room</h2><p>These steps follow the original v1.8 client inspected on 5 November 2026, entered as a guest. This is a startup and menu check — no full run is claimed. {ref(1)}</p><ol><li>Click <strong>Play</strong> above and wait for the original to load. The first screen says <strong>CLIC PARA CONTINUAR</strong> — click the screen once to pass its audio gate.</li><li>A first-run notice (<strong>Aviso antes de jugar</strong>) explains that PokéSolaire is in development and runs on free services; your progress (Pokémon, eggs, mastery, missions) saves <strong>only on this device</strong>, while an in-game account also keeps it in the cloud. The Continue button unlocks after a short countdown. {ref(1)}</li><li id="language">Switch the language if you want English: <strong>Ajustes → Idioma → English</strong> (Português and Français sit next to it). As of v1.8 the settings page notes that encounter dialogues remain in Spanish. {ref(1)}{ref(2)}</li><li>Choose <strong>JUGAR</strong>: your starter <strong>Pikachu</strong> waits at the bonfire — tap it or press <strong>CAMBIAR</strong> to pick another companion — then press <strong>EMPEZAR</strong>. The first-run notice says you unlock the full first generation by finding eggs and evolving mid-run. {ref(1)}</li><li>You start in <strong>El Laberinto, Sala 1</strong>. The original ships its own interactive guides («Cómo pelear» and the movement panel); replay them any time via Settings → <strong>Ver las guías otra vez</strong>. {ref(2)}</li></ol><p id="controls">For controls, Ajustes has TECLADO (keyboard) and MANDO (gamepad) tabs. The gamepad tab lists Roll on A/✕, Sprint on B/○, Block/parry on RB/R1, Light attack on X/□, Heavy attack on Y/△, Special/interact on LB/L1, Switch type on View/Share, Lock on R3 and Pause on Start/Options (English UI read 5 November 2026). The developer's Reddit post adds that the Tab key switches your active elemental type mid-run. {ref(1)}{ref(4)} We checked menus and the first room as guests; this is not a full-run, ranked or controller benchmark.</p></section>
<section id="saves"><h2>What is saved where</h2><p>The first-run notice is explicit: guest progress is saved only on this device, so keep the same host and browser profile and do not clear site data mid-run. With an in-game account, progress is stored in the cloud and the notice says you can recover it on another device. We have not tested account creation or cross-device saves ourselves. {ref(1)}</p><p>The game menu links the project's Discord server. If the framed window stalls, {ext(GAME, 'open the original in its own tab')} before troubleshooting anything else — an outage on the original site cannot be fixed from this page. {ref(5)}</p></section>
<section id="which-game"><h2>Check the name before following a guide</h2><div class="table-wrap" tabindex="0" role="region" aria-label="Identify similarly named games"><table class="psol-identity"><thead><tr><th>Name you saw</th><th>What it actually is</th><th>Route</th></tr></thead><tbody>
<tr><td>PokéSolaire / Pokésolaire</td><td>This game: a free 2.5D soulslike Pokémon browser roguelike by Alonso y Roa at pokesolaire.com, in open beta (client v1.8).</td><td><a href="#play">Window above</a></td></tr>
<tr><td>“Pokesolaire” (French creator)</td><td>A French Pokémon TCG content creator using a similar name — a person, not this browser game.</td><td>Check the address bar: only pokesolaire.com is this game.</td></tr>
<tr><td>PokéSouls: Episode Charmander</td><td>A different souls-like Pokémon fan game on itch.io. Confusingly, this dev team also brands itself “PokeSouls” on TikTok and lists a pokesouls2.5d@gmail.com contact — same words, different games.</td><td>{ext('https://jab-lao.itch.io/pokesouls-episode-chamander', 'itch.io page')}</td></tr>
<tr><td>PokéRogue / PokéSurvivor / PokéBonk</td><td>Other Pokémon roguelike browser games: similar genre, unrelated projects, hosts and accounts.</td><td>Check the host domain before trusting a guide.</td></tr>
<tr><td>PokéIsaac · Poké Arena 2D · PokéVersus</td><td>Other free Pokémon browser games on this site, each with its own host, controls and progress.</td><td><a href="/poke-isaac/">PokéIsaac</a> · <a href="/pokearena-2d/">Poké Arena 2D</a> · <a href="/pokeversus/">PokéVersus</a></td></tr>
</tbody></table></div><p>Shared names do not mean shared accounts, saves or rosters — progress does not move between any of these games. {ref(1)}{ref(3)}</p></section>
{sources([
    (GAME, 'PokéSolaire · original game', 'Landing page, click-to-continue screen, first-run notice (development status, device-only saves, starter Pikachu), hub menu, Settings → Language (English/Português/Français), gamepad mapping and the first labyrinth room inspected 5 November 2026 in desktop Chrome, entered as a guest; menus and the first room only, no full run played. SINGLE_SOURCE for in-client flows.'),
    (GAME, 'PokéSolaire · in-game update notes (NOVEDADES)', 'v1.8 “El juego en inglés, portugués y francés” dated 1 November 2026 (Chile time); v1.6 and v1.7.1 dated 31 October 2026; the notes also document combo attacks, weapon switching, controller support and the in-game «Cómo pelear» guides. Read 5 November 2026 — high-change, recheck before relying on version specifics.'),
    (GAME, 'PokéSolaire · in-game Legal panel', 'States the project is a non-profit fan game unaffiliated with Nintendo, Game Freak, Creatures Inc. and The Pokémon Company; Dark Souls references belong to FromSoftware and Bandai Namco; free with no ads or purchases; Ko-fi donations are voluntary; page updated 27 October 2026. Read 5 November 2026.'),
    (REDDIT, 'r/playmygame · developer post (u/Far_List_3384)', 'Developer-described features: real-time combat, the Tab key switching the active elemental type, mid-battle evolutions, Darkrai and Rayquaza bosses, global daily runs and leaderboards; the post calls the game open source (we found no official repository — treat as unverified). Posted about 2 November 2026, read 5 November 2026.'),
    ('https://discord.gg/y94yMHbsyA', 'PokéSolaire · official Discord invite', 'Linked from the original game menu. The invite existed on 5 November 2026; server contents were not read (login-gated for our tools).'),
])}</article>
{faq_html()}
{recommendations('poke-solaire')}'''
    return shell(TITLE, DESC, body)


def build():
    f = ROOT / 'poke-solaire/index.html'
    f.parent.mkdir(exist_ok=True)
    write_html(f, decorate(ROUTE, page()), encoding='utf-8')
    f = ROOT / 'index.html'
    text = f.read_text(encoding='utf-8')
    if 'id="poke-solaire-game-entry"' not in text:
        text = text.replace('<div class="route-grid">', '<div class="route-grid"><a class="route-card" id="poke-solaire-game-entry" href="/poke-solaire/"><h3>PokéSolaire</h3><p>Free Pokémon soulslike browser roguelike: play the original in a click-loaded window, switch the client to English and check same-name games.</p><span class="route-link">Play &amp; start guide →</span></a>', 1)
        write_html(f, text, encoding='utf-8')
    f = ROOT / 'privacy-policy.html'
    text = f.read_text(encoding='utf-8')
    if 'id="poke-solaire"' not in text:
        text = text.replace('</body>', '<h2 id="poke-solaire">PokéSolaire game window</h2><p>Updated 5 November 2026. Clicking Play loads the original game from pokesolaire.com, including its resources and services. The original shows its own click-to-continue screen, first-run notice and any account choices inside that window, and they belong to the original project; hiding the window keeps the same frame connected and does not pause the game — close or leave the page to end the session. Framed and separate-tab storage can differ; we cannot read or recover game saves, and guest progress is saved only in the player\'s own browser by the game itself. Ordinary page integrations inherit this site\'s existing AdSense and site-wide Umami services described above.</p></body>', 1)
        write_html(f, text, encoding='utf-8')
    print(f'Built PokéSolaire playable landing; title={len(TITLE)} chars, description={len(DESC)} chars; patched root entry/privacy.')


if __name__ == '__main__':
    build()
