"""Game-level task selection for the existing Risk of Rain 2 guides."""
import re


def render(shell):
    page = shell(
        '/risk-of-rain-2/',
        'Risk of Rain 2 Guides: Crossplay, Gold Portal & Artifacts',
        'Choose a Risk of Rain 2 guide for crossplay, the Gold Portal and False Son route, or Bulwark’s Ambry. Find the right starting point for your run.',
        'Risk of Rain 2 guides', '', [], [],
    )
    main = '''<main class="wrap ror-hub" id="main">
<section class="hub-hero" aria-labelledby="hub-title">
<div><p class="eyebrow">RISK OF RAIN 2 · PLAYER GUIDES</p>
<h1 id="hub-title">Risk of Rain 2 guides</h1>
<p class="hub-intro">Get your group connected, follow the Gold Portal route, or work through an artifact trial. Choose the guide that matches what you are trying to do.</p>
<a class="hub-button" href="#guides">Choose a guide <span aria-hidden="true">↓</span></a></div>
<img src="/assets/risk-of-rain-2/coop-survivors-800.webp" srcset="/assets/risk-of-rain-2/coop-survivors-800.webp 800w, /assets/risk-of-rain-2/coop-survivors-1280.webp 1280w" sizes="(max-width:900px) calc(100vw - 40px), 52vw" width="1280" height="720" alt="Survivors fighting together in Risk of Rain 2's official launch footage" fetchpriority="high">
</section>
<section class="hub-section" id="guides" aria-labelledby="guides-title"><p class="eyebrow">PICK YOUR GOAL</p><h2 id="guides-title">Where do you want to go?</h2>
<div class="hub-grid">
<a class="hub-task" href="/risk-of-rain-2/crossplay/"><span class="hub-number">01 · PLAY TOGETHER</span><h3>Can your copies connect?</h3><p>Compare both players’ stores, Steam crossplay settings and console editions. Use the two-copy check before planning a session.</p><span class="hub-action">Check crossplay →</span></a>
<a class="hub-task" href="/risk-of-rain-2/gold-portal/"><span class="hub-number">02 · PLAN AN UNLOCK</span><h3>Gold Portal to False Son</h3><p>Find your place on the route from Gilded Coast and seven beacons to Halcyon Seed and the Seekers of the Storm unlock.</p><span class="hub-action">Follow the route →</span></a>
<a class="hub-task" href="/risk-of-rain-2/ru/bulwarks-ambry/" hreflang="ru"><span class="hub-number">03 · ARTIFACT TRIAL · РУССКИЙ</span><h3>Bulwark’s Ambry</h3><p>Russian-language help with the fifth-stage entrance, Artifact Keys, the trial and its reward.</p><span class="hub-action" lang="ru">Открыть руководство →</span></a>
</div></section>
<section class="hub-section hub-choose" id="choose" aria-labelledby="choose-title"><div><p class="eyebrow">START FROM YOUR CURRENT PROBLEM</p><h2 id="choose-title">Choose before you commit.</h2></div>
<div><h3>Joining a friend?</h3><p>Start with <a href="/risk-of-rain-2/crossplay/">both copies and their settings</a>. The guide separates store compatibility, console generations and invitations.</p>
<h3>Already carrying Halcyon Seed?</h3><p>Use the <a href="/risk-of-rain-2/gold-portal/#start">starting-point table</a> to pick up the route where you are. Check the DLC and exit conditions before continuing toward False Son.</p>
<h3>Looking for the artifact chamber?</h3><p>The <a href="/risk-of-rain-2/ru/bulwarks-ambry/">Russian trial guide</a> covers entry and keys. Its language is marked so you can choose the appropriate guide.</p></div></section>
<section class="hub-notes"><h2>About these guides</h2><p>Megabonk.org is an independent guide site. Each linked guide keeps the sources and version conditions relevant to its task. The header image is from the official 1.0 launch footage and shows the game’s co-op setting. Guide facts were last checked on 5 November 2026.</p></section>
</main>'''
    page = re.sub(r'<main\b.*?</main>', lambda _: main, page, count=1, flags=re.S)
    page = page.replace('class="guide-layout ror-guide"', 'class="guide-layout ror-guide ror-hub-page"')
    page = page.replace('property="og:type" content="article"', 'property="og:type" content="website"')
    return page.replace('</head>', '<link rel="stylesheet" href="/assets/risk-of-rain-2/hub.css"></head>', 1)
