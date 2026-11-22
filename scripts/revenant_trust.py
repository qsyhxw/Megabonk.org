"""Revenant Survivors 专区 About / Contact（SOP v3.26，02 §5.1）。

由 build_revenant_survivors.py 调用，导航与页脚由随后运行的 register_page.py 填充。信任页不放广告。
事实全部来自本专区已有页面及其引用的开发者资料，不新增游戏信息。Privacy 使用站级页的 #revenant-survivors 一节。"""
import json
from html import escape
from pathlib import Path

from site_analytics import write_html

ROOT = Path(__file__).resolve().parents[1]
P = '/revenant-survivors/'
REVIEWED = '22 November 2026'
CHECKED = '17 November 2026'
STORE = 'https://store.steampowered.com/app/4617500/Revenant_Survivors/?l=english'
DEMO = 'https://store.steampowered.com/app/4693240/'
HUB = 'https://steamcommunity.com/app/4617500'


def email():
    return json.loads((ROOT / 'config/site-contact.json').read_text(encoding='utf8'))['email']


def ext(url, label):
    return f'<a href="{escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">{label} ↗</a>'


def about():
    return f'''<main class="wrap" id="main"><article class="legal"><header class="article-head" id="guide"><p class="eyebrow">Revenant Survivors · About</p><h1>About the Revenant Survivors guide</h1>
<p class="byline">Megabonk.org editors · Facts reviewed {REVIEWED} · Game version checked: update 0.6.4</p></header>
<section id="who"><h2>Who runs this section</h2><p>This is an unofficial fan guide published by the editors of Megabonk.org, an independent site for survivors-style games. We are not Mongma Studio, who makes Revenant Survivors, and nothing here is endorsed by the studio.</p></section>
<section id="covers"><h2>What it covers</h2><p>The <a href="{P}">guide home</a> sends you to the page for your next job: <a href="{P}demo-save-transfer/">moving a Demo save</a>, <a href="{P}permanent-progression/">retained equipment and the Forge</a>, <a href="{P}hard-mode/">Hard Mode unlocks and rewards</a>, <a href="{P}controller-auto-attack/">controller and auto-attack checks</a> and <a href="{P}stuck-after-run/">reported fixes for freezes after a run</a>.</p></section>
<section id="sources"><h2>Where the answers come from</h2><ul>
<li><strong>The developer’s announcements and replies:</strong> update notes, the launch announcement and the studio’s answers in public threads on the {ext(HUB, 'Steam Community hub')} supply the save-transfer sequence, progression rules and fix lists.</li>
<li><strong>The store listings:</strong> the {ext(STORE, 'full game')} and {ext(DEMO, 'free Demo')} pages supply the edition split, release stage and controller support listing.</li>
<li><strong>Public player reports:</strong> older playtest reports are kept apart from the current release and labelled with the version they describe.</li>
<li><strong>Images:</strong> the gameplay images are Mongma Studio’s Steam promotional screenshots with the capture build unspecified. The guides rely on the sources above rather than on our own complete playthroughs.</li></ul></section>
<section id="updates"><h2>How pages stay current</h2><p>Each guide shows the date it was checked; the section as a whole was last reviewed on {REVIEWED}, against update 0.6.4 of {CHECKED}. When the studio ships a new update, the pages that depend on its unlock rules, rewards or fixes are rechecked and the date on each page changes only when its answer was confirmed again.</p></section>
<section id="identity"><h2>Which game this guide is about</h2><p>These pages cover Revenant Survivors from Mongma Studio, Steam app 4617500, in both its full Early Access release and its separate free Demo. Advice written for one edition is marked as such, because the two have their own version numbers.</p></section>
<section id="corrections"><h2>Send a correction</h2><p>Send the page URL, your edition and what you saw through the <a href="{P}contact/">contact page</a>. Corrections backed by a screenshot or the developer’s own statement are reviewed first.</p></section>
</article></main>'''


def contact():
    mail = email()
    return f'''<main class="wrap" id="main"><article class="legal"><header class="article-head" id="guide"><p class="eyebrow">Revenant Survivors · Contact</p><h1>Contact the Revenant Survivors guide editors</h1>
<p class="byline">Reviewed {REVIEWED}</p></header>
<section id="write"><h2>Email</h2><p>Write to <a href="mailto:{mail}?subject=%5BRevenant%20Survivors%5D%20Guide%20feedback">{mail}</a>. Useful reports for this section:</p><ul>
<li>An unlock rule, Hard level reward or Mythic set that changed in a newer update;</li>
<li>A Demo save or Steam Cloud step that works differently from the transfer guide;</li>
<li>A controller or auto-attack behaviour that the current release handles differently;</li>
<li>A wrong screenshot, link or item name on a Revenant Survivors page.</li></ul>
<p>Include the page URL, your edition (Demo or full game), the game version and what happened. A screenshot helps us confirm the fix quickly.</p></section>
<section id="cannot"><h2>What we cannot help with</h2><p>We are not the developer or the game’s support team, so we cannot restore a save, fix a Steam purchase or change how the game works. Use the {ext(HUB, 'Steam Community hub')} to reach Mongma Studio.</p></section>
</article></main>'''


def build(shell):
    pages = {
        'about': ({'title': 'About the Revenant Survivors Guide | Megabonk.org',
                   'description': 'Who writes the unofficial Revenant Survivors guides on Megabonk.org, where unlock and save answers come from and how pages are rechecked after game updates.'}, about()),
        'contact': ({'title': 'Contact the Revenant Survivors Guide Editors | Megabonk.org',
                     'description': 'Report an outdated Revenant Survivors unlock, reward, save or controller answer, with what to include and what we cannot help with.'}, contact()),
    }
    for slug, (page, main) in pages.items():
        route = f'{P}{slug}/'
        html = shell(route, page, 'rv-guide', '', main)
        # 信任页不带社交预览图字段和广告
        p = ROOT / 'revenant-survivors' / slug / 'index.html'
        p.parent.mkdir(parents=True, exist_ok=True)
        write_html(p, html, encoding='utf-8')
