"""Homepage presentation over the preserved, reviewed demo guide."""
import re


def redesign(html):
    html = html.replace('<link rel="stylesheet" href="/assets/pokebonk/site.css">', '')
    html = html.replace('<link rel="stylesheet" href="/assets/vampire-survivors/site.css">',
                        '<link rel="stylesheet" href="/assets/vampire-survivors/home.css">')
    html = html.replace('class="guide-layout vs-guide"', 'class="guide-layout vs-home"')
    tasks = '''<section class="hub-tasks" id="guides" aria-labelledby="progression-title">
<div class="section-label"><span>01 / PLAN YOUR NEXT RUN</span><span>FULL-GAME GUIDES</span></div>
<h2 id="progression-title">Make the next run count.</h2>
<div class="task-grid">
<a class="task task-primary" href="/vampire-survivors/evolutions/"><span class="task-number">01</span><span class="task-tag">WEAPON + PASSIVE + CHEST</span><h3>Find your evolution.</h3><p>Match a starting weapon to its passive, plan your slots, and check a chest that will not evolve.</p><span class="task-detail">Common starting recipes · level and chest checks</span><span class="task-link">Open the evolution guide <span aria-hidden="true">→</span></span></a>
<a class="task" id="unlocks" href="/vampire-survivors/infinite-corridor/"><span class="task-number">02</span><span class="task-tag">UNLOCK ROUTE</span><h3>Reach Infinite Corridor.</h3><p>Follow the Yellow Sign and ring prerequisites, then find the next step for your current progress.</p><span class="task-link">Follow the unlock route <span aria-hidden="true">→</span></span></a>
<a class="task" href="/vampire-survivors/collection-1-0/"><span class="task-number">03</span><span class="task-tag">COLLECTION CHECKLIST</span><h3>Find the missing entry.</h3><p>Check Collection 1.0 gaps, Gemini counterparts and the Queen Sigma exceptions.</p><span class="task-link">Check your collection <span aria-hidden="true">→</span></span></a>
</div><div class="coop-strip"><div><span class="task-tag">PLAYING TOGETHER?</span><h3>Check both copies first.</h3><p>Choose both players’ devices and stores to check the documented co-op route.</p></div><a class="button secondary" href="/vampire-survivors/co-op/">Check co-op compatibility <span aria-hidden="true">→</span></a></div>
<p class="scope-note">These guides cover the tasks listed above. The evolution guide covers common starting recipes. All-DLC coverage remains incomplete.</p>
<div class="batch-guides"><h3>Choose your next objective</h3><ul><li><a href="/vampire-survivors/unlocks/">Base-game unlock roadmap</a></li><li><a href="/vampire-survivors/how-to-beat-death/">Beat the 30-minute Red Death</a></li><li><a href="/vampire-survivors/secret-characters/">Selected secret-character gameplay routes</a></li><li><a href="/vampire-survivors/dlc/">Compare DLC packs</a></li><li><a href="/vampire-survivors/ode-to-castlevania/">Castlevania gate checkpoints</a></li><li><a href="/vampire-survivors/sonic-whip/">Sonic Whip unlock and evolution</a></li></ul></div></section>'''
    html = re.sub(r'<section id="guides">.*?</section>', '', html, count=1, flags=re.S)
    start = html.index('<header class="article-head"')
    end = html.index('</header>', start) + len('</header>')
    original = html[start:end]
    h1 = re.search(r'<h1>.*?</h1>', original, re.S)[0]
    hero = f'''<header class="hub-hero" id="guide"><div class="hero-copy"><p class="eyebrow">INDEPENDENT GUIDES / PONCLE’S SURVIVAL ROGUELITE</p><p class="hub-name">Vampire<br><span>Survivors</span></p>{h1}<p class="hero-intro">Try the original browser demo, find a weapon recipe, or plan the next unlock in your full-game save.</p><div class="hero-actions"><a class="button" href="/vampire-survivors/evolutions/">Find an evolution <span aria-hidden="true">→</span></a><a class="text-link" href="#demo">Open the browser demo <span aria-hidden="true">↓</span></a></div><p class="hero-note">The web demo is the old v0.2.4 edition. Full-game progression and co-op have separate guides below.</p></div><figure class="hero-scene"><img src="/assets/vampire-survivors/demo-combat-800.webp" srcset="/assets/vampire-survivors/demo-combat-800.webp 800w, /assets/vampire-survivors/demo-combat-958.webp 958w" sizes="(max-width:900px) calc(100vw - 40px), 52vw" width="958" height="640" fetchpriority="high" alt="Antonio automatically whipping a bat in the original Vampire Survivors v0.2.4 browser demo"><figcaption><span>THE ORIGINAL BROWSER DEMO</span><span>v0.2.4 · opening captured 5 Nov 2026</span></figcaption></figure></header>'''
    html = html[:start] + hero + tasks + html[end:]
    # Preserve the original demo answer and its citations beside the real entry.
    answer = re.search(r'<div class="answer">(.*?)</div>', original, re.S)[1]
    html = html.replace('<section id="demo"><h2>Open the original demo</h2>',
                        '<section id="demo"><p class="eyebrow">02 / TRY THE ORIGINAL</p><h2>Open the original demo</h2>' + answer, 1)
    html = html.replace('<strong>On this page</strong>', '<strong>Browser demo &amp; edition guide</strong>', 1)
    html = html.replace('<a href="#guides">Full-game progression guides</a>', '', 1)
    return html
