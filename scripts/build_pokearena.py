"""Original-host launch guide. The game publisher prohibits remote framing."""
import json
from html import escape
from pathlib import Path

from guide_images import decorate
from play_recommendations import recommendations, stylesheet
from site_analytics import write_html

ROOT = Path(__file__).resolve().parents[1]
ROUTE = '/pokearena-2d/'
GAME = 'https://www.pokearena2d.com/'


def build():
    manifest = json.loads((ROOT / 'data/pokearena-2d-pages.json').read_text(encoding='utf-8'))
    nav = ''.join(f'<a href="{escape(item["href"])}">{escape(item["label"])}</a>' for item in manifest['nav_extra'])
    html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Poké Arena 2D: Original Game &amp; First Match Guide</title><meta name="description" content="Open Poké Arena 2D on its original site, follow the Training setup, check controls and save limits, and find more browser games on Megabonk.org.">
<link rel="canonical" href="https://megabonk.org{ROUTE}"><meta property="og:type" content="website"><meta property="og:title" content="Poké Arena 2D: Original Game &amp; First Match Guide"><meta property="og:description" content="Find the original browser game and follow its Training setup."><meta property="og:url" content="https://megabonk.org{ROUTE}"><meta property="og:image" content="https://megabonk.org/assets/pokearena-2d/menu-1280.webp">
<link rel="stylesheet" href="/assets/guide-article-layout.css"><link rel="stylesheet" href="/assets/pokearena-2d/theme.css"><link rel="stylesheet" href="/assets/pokearena-2d/hub.css">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8830315294299920" crossorigin="anonymous"></script></head>
<body data-format="play" class="guide-layout pa-guide"><a class="skip" href="#main">Skip to content</a><header class="top"><div class="wrap"><a class="brand" href="/"><span>Megabonk.org<small>Game guides</small></span></a><nav class="desktop-nav" aria-label="Main navigation">{nav}</nav><details class="mobile-nav"><summary>Menu</summary><nav class="mobile-links" aria-label="Mobile navigation">{nav}</nav></details></div></header>
<main id="main"><header class="pa-hero" id="guide"><div class="wrap pa-hero-in"><div class="pa-copy"><p class="eyebrow">First match guide</p><h1>Poké Arena 2D</h1><p class="lead">Pick a Pokémon, choose a training dummy and learn your moves before your first duel.</p><ul class="pa-tags" aria-label="Game type"><li>Real-time duels</li><li>Browser</li><li>Training mode</li></ul><div id="play"><a class="pa-launch" href="{GAME}" target="_blank" rel="noopener noreferrer">Play on pokearena2d.com ↗</a><a class="pa-secondary" href="#start">Training setup ↓</a></div><p class="pa-caption">The original game opens in a new tab.</p></div><figure class="menu-shot"><img src="/assets/pokearena-2d/menu-1280.webp" srcset="/assets/pokearena-2d/menu-800.webp 800w, /assets/pokearena-2d/menu-1280.webp 1280w" sizes="(max-width:900px) calc(100vw - 36px), 650px" width="1440" height="900" alt="Original Poké Arena 2D Alpha 0.64.0 menu with Play, Online, Customize, Pokédex, Tutorial and Settings"><figcaption>Title menu <span>Alpha 0.64.0 · 4 Nov 2026</span></figcaption></figure></div></header>
<div class="wrap"><article class="pa-notes">
<section id="start"><h2>Set up a training match</h2><p>From the title menu, select <strong>Play → Training</strong>. Online matches have their own entry on the title screen.</p><ol class="steps"><li><strong>Choose your fighter.</strong> Pick an unlocked Pokémon from the top roster for Player 1.</li><li><strong>Set the dummy and arena.</strong> Fill the dummy slot, then choose an arena along the bottom of the screen.</li><li><strong>Read your kit and select Fight!</strong> Try moving and aiming before working through the attacks shown on your fighter’s panel.</li></ol></section>
<section id="controls"><h2>Battle controls</h2><p>In the Alpha 0.64.0 Training selector, Bulbasaur’s kit uses the following inputs. Check your own fighter’s panel for its moves.</p><dl class="keymap"><div><dt>Move and aim</dt><dd><kbd>WASD</kbd> + mouse</dd></div><div><dt>Attacks</dt><dd><kbd>LMB</kbd> <kbd>RMB</kbd> <kbd>Space</kbd> <kbd>Q</kbd> <kbd>E</kbd></dd></div><div><dt>Evolve</dt><dd><kbd>F</kbd></dd></div><div><dt>Pause</dt><dd><kbd>P</kbd></dd></div></dl><p>On a phone, rotate to landscape. For gamepad options or a refresher on inputs, open <strong>Settings</strong> or <strong>Tutorial</strong> on the title menu.</p></section>
<section id="save"><h2>Keep your League progress</h2><p>The game stores League progress and settings in your browser. Return to the same site with the same browser profile. Clearing site data removes the local save. The project lists accounts for online modes. <a href="{GAME}privacy" target="_blank" rel="noopener noreferrer">Game privacy notice ↗</a></p></section>
<section id="which-game"><h2>Which arena game?</h2><dl class="domains"><div><dt>pokearena2d.com</dt><dd>The real-time fighter pictured here. Use <a href="#play">the game entry above</a> for its Training mode.</dd></div><div><dt>pokemonarena2d.com</dt><dd>Big Kid Nation’s separate Pokémon Arena 2D project. <a href="https://www.pokemonarena2d.com/" target="_blank" rel="noopener noreferrer">Project website ↗</a></dd></div></dl></section><section class="sources" id="sources"><h2>Sources &amp; verification</h2><p>By Megabonk.org · checked 4 November 2026. Independent, source-based instructions with an original-host startup inspection. Pokémon names and game artwork belong to their respective owners. This fan game and this guide are unaffiliated with Nintendo, GAME FREAK and The Pokémon Company.</p><ol><li id="source-1"><a href="{GAME}" target="_blank" rel="noopener noreferrer">Poké Arena 2D · original game ↗</a> — Alpha 0.64.0 title, Play and Training menus inspected in desktop Chrome. The original response prohibits remote framing. SINGLE_SOURCE for this project's menus. No full clear, ranked-match or physical-device benchmark.</li><li id="source-2"><a href="{GAME}privacy" target="_blank" rel="noopener noreferrer">Poké Arena 2D · project privacy notice ↗</a> — local progress, accounts and WebRTC statements, read 4 November. Policy statements, not save-recovery tests.</li><li id="source-3"><a href="https://www.pokemonarena2d.com/" target="_blank" rel="noopener noreferrer">Big Kid Nation · separate Pokémon Arena 2D project ↗</a> — December 2026 beta plan checked 4 November. A different game.</li></ol><a class="back" href="#guide">Back to page ↑</a></section></article>
{recommendations('pokearena-2d')}
</div></main><footer class="footer"><div class="wrap footer-grid"><div><strong>Megabonk.org</strong><p>Independent editorial by Megabonk.org. The original project operates the game and its services.</p><a href="/#more-games">More games &amp; guides →</a></div><nav aria-label="Site information"><a href="/about/">About</a><a href="/contact/">Contact</a><a href="/privacy-policy#pokearena-2d">Privacy</a></nav></div></footer></body></html>'''
    target = ROOT / 'pokearena-2d/index.html'
    target.parent.mkdir(exist_ok=True)
    write_html(target, decorate(ROUTE, stylesheet(html)), encoding='utf-8')
    target = ROOT / 'privacy-policy.html'
    html = target.read_text(encoding='utf-8')
    if 'id="pokearena-2d"' not in html:
        html = html.replace('</body>', '<h2 id="pokearena-2d">Poké Arena 2D external game links</h2><p>Updated 4 November 2026. The guide links to pokearena2d.com in a new tab. Its publisher prohibits remote embedding, so this page does not load its game client or provide an account or save service. Opening an external link connects you to that destination and its own services and storage. Our screenshots are local files. The guide inherits this site\'s existing AdSense and site-wide Umami integrations described above.</p></body>', 1)
        write_html(target, html, encoding='utf-8')
    print('Built Poké Arena original-host launch guide.')


if __name__ == '__main__':
    build()
