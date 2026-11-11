"""Build the Warhammer hub independently of the guide article body."""
import re

BASE = '/warhammer-survivors/'


def redesign(document):
    sections = dict(re.findall(r'<section id="([^"]+)">(.*?)</section>', document, re.S))
    head = document.split('<main id="main"', 1)[0]
    for theme in ('pokebonk', 'vampire-survivors'):
        head = head.replace(f'<link rel="stylesheet" href="/assets/{theme}/site.css">', '')
    head = head.replace('</head>', '<link rel="stylesheet" href="/assets/warhammer-survivors/home.css"></head>')
    head = head.replace('class="guide-layout vs-guide"', 'class="guide-layout wh-home"')
    footer = '<footer' + document.split('<footer', 1)[1]

    def detail(key, label):
        body = re.sub(r'^<h2>.*?</h2>', '', sections[key], count=1)
        return f'<details id="{key}" class="help-item"><summary>{label}</summary><div class="help-body">{body}</div></details>'

    help_items = ''.join(detail(key, label) for key, label in [
        ('demo', 'Try the PC demo & understand save transfers'),
        ('ios', 'iPhone & iPad availability'),
        ('tor-garadon', 'Tor Garadon & launch content'),
        ('launch-help', 'Launch issues & support'),
        ('identity', 'The game, its developers & the two universes'),
    ])
    release = sections['release']
    main = f'''<main id="main">
<section class="hero" id="guide"><div class="wrap hero-grid">
<div class="hero-copy"><p class="eyebrow">Independent player guides</p>
<h1>Warhammer Survivors</h1>
<p class="hero-description">A survivors-style action game spanning Warhammer 40,000 and Age of Sigmar. Find weapon evolutions, check co-op, and plan your next unlock.</p>
<p class="release-line">Out now · Released 10 November 2026</p>
<div class="hero-actions"><a class="button primary" href="{BASE}evolutions/">Find an evolution <span aria-hidden="true">→</span></a><a class="button secondary" href="{BASE}co-op/">Co-op & multiplayer <span aria-hidden="true">→</span></a></div>
<a class="platform-link" href="#release">PC, console & mobile access <span aria-hidden="true">↓</span></a></div>
<figure class="hero-image"><img src="/assets/warhammer-survivors/squad-1280.webp" srcset="/assets/warhammer-survivors/squad-800.webp 800w, /assets/warhammer-survivors/squad-1280.webp 1280w" sizes="(max-width: 900px) 100vw, 58vw" width="1920" height="1080" alt="Warhammer Survivors soldiers and allies facing Tyranids beside a tank" fetchpriority="high"><figcaption>© Games Workshop Limited.</figcaption></figure>
</div></section>
<div class="wrap hub-content">
<section id="choose" class="featured-section"><div class="section-heading"><h2>Plan your next run</h2><p>Weapons, companions and who can join you.</p></div>
<div class="featured-grid"><a class="feature-card evolution-card" href="{BASE}evolutions/"><div><p class="card-kicker">Weapons & companions</p><h3>Weapon evolutions</h3><p>Search the recipe table by weapon, passive or evolved form. Filter by universe and check a pair that will not evolve.</p><span class="card-action">Open the evolution finder <span aria-hidden="true">→</span></span></div><img src="/assets/warhammer-survivors/combat-800.webp" width="1920" height="1080" alt="A gold-armoured champion fighting in a stone courtyard" loading="lazy"></a>
<a class="feature-card coop-card" href="{BASE}co-op/"><p class="card-kicker">Playing with friends</p><h3>Co-op & multiplayer</h3><p>Check the current player-count answer, multiplayer plans and the difference between squad allies and human players.</p><span class="card-action">Check before your group buys <span aria-hidden="true">→</span></span></a></div></section>
<section id="guides" class="progression-section"><div class="section-heading" id="progression-guides"><h2>Saves & unlocks</h2><p>Get past a specific progression roadblock.</p></div><div class="task-grid">
<a class="task-card" href="{BASE}cross-save/"><h3>Cross-save & cross-progression</h3><p>Check what carries between devices, storefronts and the demo.</p><span class="card-action">Check your save route <span aria-hidden="true">→</span></span></a>
<a class="task-card" href="{BASE}followers/"><h3>Two followers at once</h3><p>Understand the objective and check the Tankard unlock.</p><span class="card-action">Work through the objective <span aria-hidden="true">→</span></span></a>
<a class="task-card" href="{BASE}dice-cube/"><h3>Dice Cube</h3><p>Find the relevant unlock and weapon pair for your universe.</p><span class="card-action">Find the Dice Cube steps <span aria-hidden="true">→</span></span></a>
</div></section>
<section id="release" class="access-section"><div class="section-heading"><h2>Get into the game</h2><p>Full release, Game Pass and platform choices.</p></div><div class="access-copy">{re.sub(r'^<h2>.*?</h2>', '', release, count=1)}<p><a href="https://store.steampowered.com/app/3669620/Warhammer_Survivors/" target="_blank" rel="noopener noreferrer">View Warhammer Survivors on Steam ↗<span class="sr-only"> (opens in a new tab)</span></a></p></div></section>
<section class="help-section"><div class="section-heading"><h2>Before you start</h2><p>Demo progress, platforms and launch-day questions.</p></div>{help_items}</section>
<div class="editorial-note"><p>Independent guides by Megabonk.org. Facts checked 11 November 2026. Recipe and unlock pages identify their supporting sources and build-specific limits.</p><a href="#guide">Back to top ↑</a></div>
</div></main>'''
    return head + main + footer
