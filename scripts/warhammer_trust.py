"""Warhammer Survivors section About / Contact and its Privacy section (SOP v3.25, 02 §5.1).

Runs in build_warhammer_survivors.py before register_page.py, which fills nav and the footer.
Trust pages carry no ads; Umami is site-wide (write_html adds it). Facts come from the
section's own pages and FACT_CHECK (WHS rows); nothing here is new game information.
"""
from pathlib import Path
from site_analytics import write_html

ROOT = Path(__file__).resolve().parents[1]
BASE = '/warhammer-survivors/'
EMAIL = 'contact@megabonk.org'
CHECKED = '13 November 2026'
VERSION = 'Steam v2.1.6'


def shell(slug, title, desc, body):
    nav = '<a href="/#more-games">More games</a>'  # replaced by register_page.py
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{title}</title><meta name="description" content="{desc}"><link rel="canonical" href="https://megabonk.org{BASE}{slug}/">'
            f'<link rel="icon" href="/favicon.ico"><link rel="stylesheet" href="/assets/guide-article-layout.css">'
            f'<link rel="stylesheet" href="/assets/warhammer-survivors/theme.css"></head>'
            f'<body class="guide-layout wh-theme wh-guide wh-trust"><a class="skip" href="#main">Skip to content</a>'
            f'<header class="top"><div class="wrap"><a class="brand" href="{BASE}"><span>Warhammer Survivors<small>Guides &amp; weapon evolutions</small></span></a>'
            f'<nav class="desktop-nav" aria-label="Warhammer Survivors navigation">{nav}</nav><details class="mobile-nav"><summary>Menu</summary>'
            f'<nav class="mobile-links" aria-label="Warhammer Survivors mobile navigation">{nav}</nav></details></div></header>'
            f'<main id="main" class="wrap"><article class="prose legal" id="guide">{body}</article></main>'
            f'<footer class="footer"></footer></body></html>')


ABOUT = f'''<header class="article-head"><p>WARHAMMER SURVIVORS · ABOUT</p><h1>About the Warhammer Survivors guides</h1>
<p class="byline">Megabonk.org editors · Reviewed {CHECKED} · Checked against {VERSION}</p></header>
<section id="who"><h2>Who runs this section</h2><p>This is an unofficial fan guide published by the editors of Megabonk.org, an independent site for survivors-style games. We are not Auroch Digital, Games Workshop or game support, and nothing here is an official announcement. Warhammer names, artwork and in-game images belong to their owners.</p></section>
<section id="covers"><h2>What it covers</h2><p>The section answers the questions players hit in their first weeks: which <a href="{BASE}evolutions/">weapon + companion pairs evolve</a>, which <a href="{BASE}best-builds/">builds</a> carry a run, how to beat each <a href="{BASE}bosses/">Extremis boss</a>, how to unlock <a href="{BASE}characters/">champions</a> and <a href="{BASE}maps/">stages</a>, and what <a href="{BASE}co-op/">co-op</a> and <a href="{BASE}cross-save/">cross-save</a> support actually exist on each platform.</p></section>
<section id="sources"><h2>Where the answers come from</h2><ul>
<li><strong>The game itself:</strong> evolution requirements, objectives and map relics are read from the in-game level-up screen, Objectives list and pause map; the screenshots on each page are frames from that UI.</li>
<li><strong>Gameplay recordings:</strong> boss timings, rescue routes and build orders are checked against full-run videos, which are credited where they appear and load only when you click play.</li>
<li><strong>Official channels:</strong> release status, platforms, patch notes and the single-player answer come from Auroch Digital's FAQ, the Steam store page and Steam announcements, and the Xbox and mobile store listings.</li>
</ul><p>Where two sources disagree, the page gives the answer the in-game UI supports. Platform-specific limits (Switch, mobile, Xbox) are stated on the page they affect.</p></section>
<section id="updates"><h2>How pages stay current</h2><p>Each guide shows the date it was last updated and the release it was checked against. When a patch changes weapons, bosses or unlocks, the affected pages are rechecked first; the current baseline is {VERSION} (11 November 2026 hotfix), whose console changes are scheduled to reach Switch a week later.</p></section>
<section id="corrections"><h2>Found something wrong?</h2><p>Send the page URL, your platform and game version, and what you saw in game through the <a href="{BASE}contact/">contact page</a>. Corrections backed by a screenshot or a public source are usually applied in the next update.</p></section>'''

CONTACT = f'''<header class="article-head"><p>WARHAMMER SURVIVORS · CONTACT</p><h1>Contact the Warhammer Survivors guide editors</h1>
<p class="byline">Reviewed {CHECKED}</p></header>
<section id="write"><h2>Email</h2><p>Write to <a href="mailto:{EMAIL}?subject=%5BWarhammer%20Survivors%5D%20Guide%20feedback">{EMAIL}</a>. Useful reports for this section:</p><ul>
<li>An evolution recipe, build or boss answer that no longer works after a patch;</li>
<li>A champion, stage or relic unlock that differs on your platform;</li>
<li>A broken link, image or video on a Warhammer Survivors page.</li></ul>
<p>Include the page URL, your platform (Steam, Xbox/PC Game Pass, Switch, iOS or Android) and the game version from the title screen. A screenshot helps us confirm the fix quickly.</p></section>
<section id="cannot"><h2>What we cannot help with</h2><p>We are not Auroch Digital or game support, so we cannot restore saves, transfer progress, refund purchases or grant in-game items. For those, use the developer's support or the store you bought from; the <a href="https://aurochdigital.com/warhammer-survivors-faq">official FAQ</a> lists the current known issues. Do not send passwords, purchase keys or account details. There is no promised reply time.</p></section>'''

PRIVACY = (f'<section id="warhammer-survivors"><h2>Warhammer Survivors guides</h2><p>Reviewed {CHECKED}. Ordinary pages under {BASE} use this domain\'s existing Google AdSense loader; the section\'s About and Contact pages and error page load no advertising. '
           'Gameplay videos on some guides are shown as a still image and connect to YouTube (youtube-nocookie.com) only after you click play; YouTube then receives technical request data under Google\'s policies. '
           'The evolution search and universe filter run in your browser and do not store or upload your choices. The section adds no account, save upload or separate analytics tag; the site-wide Umami analytics and Cloudflare hosting described above apply. '
           'External store and developer links open those providers\' websites.</p></section>')


def build():
    pages = {
        'about': ('About the Warhammer Survivors Guides | Megabonk.org',
                  'Who writes the unofficial Warhammer Survivors guides on Megabonk.org, where the answers come from and how pages are rechecked after patches.', ABOUT),
        'contact': ('Contact the Warhammer Survivors Guide Editors | Megabonk.org',
                    'Report an outdated Warhammer Survivors evolution, build, boss or unlock answer, with what to include and what we cannot help with.', CONTACT),
    }
    for slug, (title, desc, body) in pages.items():
        p = ROOT / 'warhammer-survivors' / slug / 'index.html'
        p.parent.mkdir(parents=True, exist_ok=True)
        write_html(p, shell(slug, title, desc, body), encoding='utf8')
    f = ROOT / 'privacy-policy.html'
    s = f.read_text(encoding='utf-8')
    if 'id="warhammer-survivors"' not in s:
        s = s.replace('</body>', PRIVACY + '</body>', 1)
        write_html(f, s, encoding='utf-8')


if __name__ == '__main__':
    build()
