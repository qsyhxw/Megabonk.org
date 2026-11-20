"""Midgard Survivors section About / Contact (SOP v3.25, 02 §5.1).

Runs in build_midgard_survivors.py before register_page.py, which fills nav and the footer. Trust pages carry no
ads; Umami is site-wide (write_html adds it). Facts come from the section's own pages and the developer sources
they already cite; nothing here is new game information. Privacy stays on the site-level page (#midgard-survivors)."""
import json
from html import escape
from pathlib import Path

from site_analytics import write_html

ROOT = Path(__file__).resolve().parents[1]
P = '/midgard-survivors/'
CHECKED = '12 November 2026'
ITCH = 'https://nearq.itch.io/midgard-survivors'
OFFICIAL = 'https://midgardsurvivors.com/'


def email():
    return json.loads((ROOT / 'config/site-contact.json').read_text(encoding='utf8'))['email']


def ext(url, label):
    return f'<a href="{escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">{label} ↗<span class="sr-only"> (opens in a new tab)</span></a>'


def about():
    return f'''<article class="legal"><header class="article-head"><p>Midgard Survivors · About</p><h1>About the Midgard Survivors guide</h1>
<p class="byline">Megabonk.org editors · Facts reviewed {CHECKED}</p></header>
<section id="who"><h2>Who runs this section</h2><p>This is an unofficial fan guide published by the editors of Megabonk.org, an independent site for survivors-style games. We are not nearQ or Pawgres Studios, who make Midgard Survivors, and we are not Gravity, which owns Ragnarok Online; nothing here is an official announcement.</p></section>
<section id="covers"><h2>What it covers</h2><p>The section answers the questions players hit around a first install: which file to take for each device on the <a href="{P}">download and start page</a>, how to fix a black screen or crash with the <a href="{P}android/">Android Vulkan and OpenGL APKs</a>, how to open the alpha on a Mac in the <a href="{P}mac/">damaged-app guide</a>, how to keep and equip gear between runs in <a href="{P}equipment/">the equipment guide</a>, and how rooms and accounts work in <a href="{P}co-op/">co-op</a>.</p><p>It does not rank classes, publish a best-build list or give a safe refining threshold; the sources checked do not support those.</p></section>
<section id="sources"><h2>Where the answers come from</h2><ul>
<li><strong>The developer’s own pages:</strong> the {ext(OFFICIAL, 'developer website')} and the {ext(ITCH, 'itch.io listing')} supply the downloads, platform notes, controls and the Mac and Android installation guidance.</li>
<li><strong>Developer replies in community threads:</strong> launch and devlog replies on the Ragnarok Online subreddit supply the damaged-app command, the equipment route and the co-op and cross-save status at launch.</li>
<li><strong>The update manifest:</strong> the client version shown on the start page is read automatically from the developer’s public update manifest on GitHub.</li></ul>
<p>Screenshots are developer-distributed gameplay images that we downloaded and looked at. We have not run the clients ourselves, tested phones, completed a full run or played co-op, and the pages do not claim to.</p></section>
<section id="updates"><h2>How pages stay current</h2><p>Each guide shows the date it was checked, currently {CHECKED}. When the developer ships a new client, the pages that depend on its menus, platform files or save rules are rechecked first. The version number on the start page updates automatically; the instructions on each page do not, until we have reread them.</p></section>
<section id="identity"><h2>Which game is this?</h2><p>Searches for the name also surface Tastygraph’s Norse-themed game and RO Classic+’s Midgard Survival. This guide covers nearQ’s game only, and does not apply those projects’ mechanics.</p></section>
<section id="corrections"><h2>Found something wrong?</h2><p>Send the page URL, your device and client version, and what you saw through the <a href="{P}contact/">contact page</a>. Corrections backed by a screenshot or the developer’s own statement are usually applied in the next update.</p></section></article>'''


def contact():
    mail = email()
    return f'''<article class="legal"><header class="article-head"><p>Midgard Survivors · Contact</p><h1>Contact the Midgard Survivors guide editors</h1>
<p class="byline">Reviewed {CHECKED}</p></header>
<section id="write"><h2>Email</h2><p>Write to <a href="mailto:{mail}?subject=%5BMidgard%20Survivors%5D%20Guide%20feedback">{mail}</a>. Useful reports for this section:</p><ul>
<li>A download, Android, Mac or co-op step that no longer matches the current client;</li>
<li>A changed platform file, renderer option or update note on the developer’s pages;</li>
<li>A gear or progression rule that differs in your build, with the screen where you saw it;</li>
<li>A broken link, image or wrong game identification on a Midgard Survivors page.</li></ul>
<p>Include the page URL, your device or operating system, the client version shown in the launcher and what happened. A screenshot helps us confirm the fix quickly.</p></section>
<section id="cannot"><h2>What we cannot help with</h2><p>We are not the developer or game support, so we cannot recover a lost save, fix an account or change how the game works. For those, use the developer’s own channels linked from the {ext(ITCH, 'itch.io listing')}.</p></section></article>'''


def build():
    from build_midgard_survivors import shell
    pages = {
        'about': ('About the Midgard Survivors Guide | Megabonk.org',
                  'Who writes the unofficial Midgard Survivors guides on Megabonk.org, where the answers come from and how pages are rechecked after new client versions.', about()),
        'contact': ('Contact the Midgard Survivors Guide Editors | Megabonk.org',
                    'Report an outdated Midgard Survivors download, Android, Mac, equipment or co-op answer, with what to include and what we cannot help with.', contact()),
    }
    for slug, (title, desc, body) in pages.items():
        p = ROOT / 'midgard-survivors' / slug / 'index.html'
        p.parent.mkdir(parents=True, exist_ok=True)
        write_html(p, shell(f'{P}{slug}/', title, desc, body, trust=True), encoding='utf8')
