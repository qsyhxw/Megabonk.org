"""D2 Survivors section About / Contact (SOP v3.25, 02 §5.1).

Runs in build_d2_survivors.py before register_page.py, which fills nav and the footer. Trust pages carry no
ads; Umami is site-wide (write_html adds it). Facts come from the section's own pages and the original
project's pages already cited there; nothing here is new game information. Privacy stays on the site-level
page (section #d2-survivors, already published)."""
import json
from html import escape
from pathlib import Path

from site_analytics import write_html

ROOT = Path(__file__).resolve().parents[1]
P = '/d2-survivors/'
CHECKED = '3 November 2026'
BUILD = '20261102.2'


def email():
    return json.loads((ROOT / 'config/site-contact.json').read_text(encoding='utf8'))['email']


def ext(url, label):
    return f'<a href="{escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">{label} ↗</a>'


def about():
    return f'''<article class="legal" id="guide"><header class="article-head"><span class="tag">D2 Survivors · About</span><h1>About the D2 Survivors guide</h1>
<p class="byline">Megabonk.org editors · Facts reviewed {CHECKED} · Checked against original build {BUILD}</p></header>
<section id="who"><h2>Who runs this section</h2><p>This is an unofficial fan guide published by the editors of Megabonk.org, an independent site for survivors-style games. We are not framara, who makes D2 Survivors, and we are not Blizzard Entertainment; nothing here is an official announcement. Diablo II names and artwork belong to their owners.</p><p>The game is a fan project inspired by Diablo II. It is not a patch or remake of Diablo II or Diablo II: Resurrected, and the original’s own menu says it is unaffiliated with Blizzard.</p></section>
<section id="covers"><h2>What it covers</h2><p>The section answers the questions players hit before and during a first run: which edition they are looking at (<a href="{P}#versions">edition check</a>), how to <a href="{P}play/">play in a game window</a>, how to <a href="{P}setup/">prepare the original’s files</a>, how to <a href="{P}saves/">find and back up a saved run</a>, and two skill questions: <a href="{P}druid-skills/">resting or re-drafting a Druid skill</a> and <a href="{P}attack-speed/">attack speed against Faster Cast Rate</a>. Traditional Chinese and Korean entry points are on <a href="{P}zh/localization/" lang="zh-Hant">the Chinese localization page</a> and <a href="{P}ko/" lang="ko">the Korean start guide</a>.</p><p>It does not rank classes or publish a best-build list.</p></section>
<section id="sources"><h2>Where the answers come from</h2><ul>
<li><strong>The original game and its documentation:</strong> menus, the class selector, the SAVES dialog, the skill tree and the character panel are captured from the original’s browser game; platform, file and save rules are read from its {ext('https://d2survivors.lol/faq/', 'FAQ')} and {ext('https://d2survivors.lol/wiki/', 'wiki')}.</li>
<li><strong>The third-party Play window:</strong> the edition on our Play page comes from a different host, whose displayed build labels are older than the original’s. We checked that it starts and accepts movement, nothing more.</li>
<li><strong>Community tools:</strong> the Traditional Chinese tool is maintained by another player. We link to its author and have not installed or run it.</li></ul>
<p>Where the original’s current documentation and an older playable build disagree, the page says which one a step describes. We have not completed a full run, moved a save between hosts or tested on a physical phone, and the pages do not claim to.</p></section>
<section id="updates"><h2>How pages stay current</h2><p>Each guide shows the date it was checked. When the original publishes a new build, the pages that depend on its menus and save rules are rechecked first; the current baseline is build {BUILD}, read on {CHECKED}. A new build does not automatically validate every older answer.</p></section>
<section id="corrections"><h2>Found something wrong?</h2><p>Send the page URL, the host you used (original, our Play window or another site), the build shown on the menu and what you saw through the <a href="{P}contact/">contact page</a>. Corrections backed by a screenshot or a public reference are usually applied in the next update.</p></section></article>'''


def contact():
    mail = email()
    return f'''<article class="legal" id="guide"><header class="article-head"><span class="tag">D2 Survivors · Contact</span><h1>Contact the D2 Survivors guide editors</h1>
<p class="byline">Reviewed {CHECKED}</p></header>
<section id="write"><h2>Email</h2><p>Write to <a href="mailto:{mail}?subject=%5BD2%20Survivors%5D%20Guide%20feedback">{mail}</a>. Useful reports for this section:</p><ul>
<li>A setup, save or menu step that no longer matches the original’s current build;</li>
<li>A host or build label on our Play page that has changed;</li>
<li>A wrong skill, stat or Druid rule, with the screen where you saw it;</li>
<li>A broken link, image or translation on a D2 Survivors page.</li></ul>
<p>Include the page URL, the host (original, our Play window or another site), the build shown on the menu and your browser or operating system. A screenshot helps us confirm the fix quickly.</p></section>
<section id="cannot"><h2>What we cannot help with</h2><p>We are not framara or game support, so we cannot recover a lost save, read the storage of another website, install tools for you or change how the game works. For those, use the project’s own {ext('https://d2survivors.lol/faq/', 'FAQ')} and keep the backups described in the <a href="{P}saves/">saves guide</a>.</p></section></article>'''


def build(shell):
    pages = {
        'about': ('About the D2 Survivors Guide | Megabonk.org',
                  'Who writes the unofficial D2 Survivors guides on Megabonk.org, where the answers come from and how pages are rechecked after new builds.', about()),
        'contact': ('Contact the D2 Survivors Guide Editors | Megabonk.org',
                    'Report an outdated D2 Survivors setup, save, skill or Play-window answer, with what to include and what we cannot help with.', contact()),
    }
    for slug, (title, desc, body) in pages.items():
        p = ROOT / 'd2-survivors' / slug / 'index.html'
        p.parent.mkdir(parents=True, exist_ok=True)
        write_html(p, shell(f'{P}{slug}/', title, desc, body, trust=True), encoding='utf8')
