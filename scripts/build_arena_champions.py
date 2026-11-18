"""Build the Arena of Champions original-game entry and quickstart."""
from html import escape
from pathlib import Path

from play_recommendations import recommendations, stylesheet
from register_page import apply_page, load
from site_analytics import write_html

ROOT = Path(__file__).resolve().parents[1]
GAME_ID = 'arena-of-champions'
GAME = 'https://arenaofchampions.live/'
ASSETS = '/assets/arena-of-champions'


def build():
    manifest = load(ROOT, GAME_ID)
    url = manifest['base']
    canonical = manifest['site'] + url
    title = escape(manifest['pages'][0]['title'])
    task_cards = ''.join(
        f'<a href="#{task["id"]}"><strong>{escape(task["label"])} <span aria-hidden="true">↘</span></strong>'
        f'<span>{escape(task["summary"])}</span></a>'
        for task in manifest['tasks']
    )
    trust_links = ''.join(
        f'<a href="{link["href"]}">{escape(link["label"])}</a>'
        for link in manifest['trust_links']
    )
    body = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Play Arena of Champions Online | Megabonk.org</title>
<meta name="description" content="Open the original Arena of Champions browser game and find guest sign-in, Windows download, save progress and connection help.">
<link rel="canonical" href="{canonical}">
<link rel="icon" href="/favicon.ico">
<link rel="stylesheet" href="/assets/guide-article-layout.css">
<link rel="stylesheet" href="{ASSETS}/theme.css">
<link rel="stylesheet" href="{ASSETS}/hub.css">
<meta property="og:type" content="website">
<meta property="og:title" content="Play Arena of Champions Online">
<meta property="og:description" content="A WoW-style arena PvP game, hosted by its original project.">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{manifest['site']}{ASSETS}/town-1052.webp">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8830315294299920" crossorigin="anonymous"></script>
</head>
<body class="arena-of-champions-theme arena-of-champions-hub guide-layout" data-format="play" data-v320="1">
<a class="skip" href="#main">Skip to content</a>
<header class="top">
  <div class="wrap">
    <a class="brand" href="{url}"><span class="brand-mark" aria-hidden="true">A</span> Arena of Champions</a>
    <nav class="desktop-nav" aria-label="Main navigation"></nav>
    <details class="mobile-nav">
      <summary>Menu</summary>
      <nav class="mobile-links" aria-label="Mobile navigation"></nav>
    </details>
  </div>
</header>
<main class="wrap" id="main">
  <header class="arena-hero" id="guide">
    <div class="arena-intro" id="play">
      <p class="arena-platform">Desktop browser <span aria-hidden="true">·</span> PvP <span aria-hidden="true">·</span> Guest play</p>
      <h1>{title}</h1>
      <p class="arena-lead">Pick a hero and queue for WoW-style 1v1, 2v2 or 3v3. Start with a desktop browser and a keyboard and mouse.</p>
      <a class="primary" href="{GAME}" target="_blank" rel="noopener noreferrer">Open original game <span aria-hidden="true">↗</span></a>
      <p class="arena-destination">arenaofchampions.live opens in a new tab.</p>
    </div>
    <figure class="arena-preview">
      <img src="{ASSETS}/town-640.webp" srcset="{ASSETS}/town-640.webp 640w, {ASSETS}/town-1052.webp 1052w" sizes="(max-width: 720px) calc(100vw - 32px), (max-width: 1240px) 53vw, 640px" width="1052" height="473" fetchpriority="high" alt="Heroes gather around torchlight in the original Arena of Champions town lobby">
      <figcaption>Town lobby, captured 1 Nov 2026</figcaption>
    </figure>
  </header>

  <nav class="task-grid" aria-label="On this page">{task_cards}</nav>

  <article class="arena-notes prose" aria-label="Arena of Champions starting guide">
    <section id="start">
      <h2>From guest sign-in to the arena</h2>
      <ol class="start-steps">
        <li><strong>Enter as a guest.</strong> Wait for the sign-in screen on the original site, then choose <b>Play as Guest</b>.</li>
        <li><strong>Set up your controls.</strong> Pick a hero and review <b>Controls</b> and <b>Key Bindings</b>. Try movement, targeting and a few abilities in town.</li>
        <li><strong>Choose a bracket.</strong> Use the game’s queue interface for 1v1, 2v2 or 3v3. Match availability depends on who is queuing.</li>
      </ol>
    </section>

    <section id="desktop">
      <h2>Windows download and guest progress</h2>
      <p>Play in a desktop browser for a session without installation. For the desktop client, choose <strong>Download for Windows</strong> from the original sign-in screen.</p>
      <p>To move a guest session to the Windows app, the game instructs you to use <strong>Save Progress</strong> in town, then sign in with that account in the app. Keep your browser’s guest data until you can confirm the account opens with your progress.</p>
      <figure class="game-image" data-game-image="aoc-login">
        <a href="{ASSETS}/login-1280.webp" aria-label="Open full-size Arena of Champions sign-in screenshot">
          <img src="{ASSETS}/login-800.webp" srcset="{ASSETS}/login-800.webp 800w, {ASSETS}/login-1280.webp 1280w" sizes="(max-width:800px) calc(100vw - 56px), 700px" width="1400" height="900" loading="lazy" alt="The original Arena of Champions sign-in menu offers guest access and a Windows download">
        </a>
      </figure>
    </section>

    <section id="help">
      <h2>If the game stalls</h2>
      <p>Start at the <a href="#play">original game link</a> on a desktop browser. If the original site shows a browser verification screen, wait for it to finish before looking for the game’s sign-in menu. If it stalls, note whether the message appeared during verification, in the game download, or after choosing <strong>Play as Guest</strong>.</p>
      <p class="arena-check">On 18 November 2026 the original site showed browser verification, so guest entry could not be rechecked. The sign-in and town screenshots show the original client on 1 November 2026.</p>
    </section>

    <section id="choose">
      <h2>Arena PvP or a survival run?</h2>
      <p>Choose Arena of Champions for online PvP with manual abilities. Choose Azeroth Survivors for automatic spells and enemy waves. The two games use separate characters, builds and saves.</p>
    </section>
  </article>

  {recommendations(GAME_ID, limit=4)}
</main>
<footer class="footer">
  <div class="wrap footer-grid">
    <div><strong>Arena of Champions</strong><p>Independent game guide by Megabonk.org.</p></div>
    <nav aria-label="Site information">{trust_links}<a href="#more-games">More games</a></nav>
  </div>
</footer>
</body>
</html>
'''
    target = ROOT / GAME_ID / 'index.html'
    write_html(target, stylesheet(apply_page(body, manifest, '')), encoding='utf-8', newline='\n')


if __name__ == '__main__':
    build()
