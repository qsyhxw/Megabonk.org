"""Risk of Rain 2 专区 About / Contact（SOP v3.26，02 §5.1）。

由 build_risk_of_rain_2.py 调用，导航与页脚由随后运行的 register_page.py 填充。信任页不放广告。
事实全部来自本专区已有页面引用的来源，不新增游戏信息。Privacy 使用站级页的 #risk-of-rain-2 一节。"""
import json
from html import escape
from pathlib import Path

from site_analytics import write_html

ROOT = Path(__file__).resolve().parents[1]
P = '/risk-of-rain-2/'
REVIEWED = '22 November 2026'
CHECKED = '5 November 2026'
STORE = 'https://store.steampowered.com/app/632360/Risk_of_Rain_2/'
CROSS = 'https://support.2k.com/hc/en-us/articles/35232640119443-Risk-of-Rain-2-Crossplay-and-You-An-Epic-Tale'
GEN = 'https://support.2k.com/hc/en-us/articles/48628339700371-Risk-of-Rain-2-The-Future-of-Risk-of-Rain-2-on-Gen-8-Consoles'
WIKI = 'https://riskofrain2.wiki.gg/'
HUB = 'https://steamcommunity.com/app/632360'


def email():
    return json.loads((ROOT / 'config/site-contact.json').read_text(encoding='utf8'))['email']


def ext(url, label):
    return f'<a href="{escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">{label} ↗</a>'


def about():
    return f'''<main class="wrap" id="main"><article class="legal"><header class="article-head" id="guide"><p class="eyebrow">Risk of Rain 2 · About</p><h1>About the Risk of Rain 2 guides</h1>
<p class="byline">Megabonk.org editors · Facts reviewed {REVIEWED} · Sources last checked {CHECKED}</p></header>
<section id="who"><h2>Who runs this section</h2><p>This is an unofficial fan guide published by the editors of Megabonk.org, an independent site for survivors-style games. We are not Hopoo Games, Gearbox or 2K, and nothing here is endorsed by them.</p></section>
<section id="covers"><h2>What it covers</h2><p>The <a href="{P}">guide home</a> sends you to the page for your next job: the <a href="{P}crossplay/">crossplay copy check</a>, the <a href="{P}gold-portal/">Gold Portal route to the False Son unlock</a> and, in Russian, the <a href="{P}ru/bulwarks-ambry/" hreflang="ru">Bulwark’s Ambry artifact trial</a>.</p></section>
<section id="sources"><h2>Where the answers come from</h2><ul>
<li><strong>Publisher support articles:</strong> 2K’s {ext(CROSS, 'crossplay instructions')} and {ext(GEN, 'console notice')} supply the Steam and Epic route, the Steam setting and the console-generation limits.</li>
<li><strong>The store listing and announcements:</strong> the {ext(STORE, 'Steam page')} and the {ext(HUB, 'Steam Community hub')} supply editions, patch notes and the artifact announcement.</li>
<li><strong>Community reference:</strong> the {ext(WIKI, 'Risk of Rain 2 Wiki')} supplies Gilded Coast and challenge details. Where a page rests on a single community source, that page says so.</li>
<li><strong>Images:</strong> gameplay images are frames from the official 1.0 launch trailer and an official patch-note comparison. The guides rely on the sources above and on no complete playthrough of our own.</li></ul></section>
<section id="updates"><h2>How pages stay current</h2><p>Each guide shows the date it was checked; the section as a whole was last reviewed on {REVIEWED}, with source facts last confirmed on {CHECKED}. When 2K or the developers change crossplay rules, consoles or the unlock route, the pages that depend on them are rechecked and each date changes only when its answer was confirmed again.</p></section>
<section id="identity"><h2>Which game this guide is about</h2><p>These pages cover Risk of Rain 2 from Hopoo Games, published by Gearbox Publishing and 2K, including its Seekers of the Storm content where a page needs it. Advice for one store or console edition is marked as such.</p></section>
<section id="corrections"><h2>Send a correction</h2><p>Send the page URL, your store or console edition and what you saw through the <a href="{P}contact/">contact page</a>. Corrections backed by a screenshot or a publisher statement are reviewed first.</p></section>
</article></main>'''


def contact():
    mail = email()
    return f'''<main class="wrap" id="main"><article class="legal"><header class="article-head" id="guide"><p class="eyebrow">Risk of Rain 2 · Contact</p><h1>Contact the Risk of Rain 2 guide editors</h1>
<p class="byline">Reviewed {REVIEWED}</p></header>
<section id="write"><h2>Email</h2><p>Write to <a href="mailto:{mail}?subject=%5BRisk%20of%20Rain%202%5D%20Guide%20feedback">{mail}</a>. Useful reports for this section:</p><ul>
<li>A crossplay pairing or console-generation rule that changed in a newer 2K notice;</li>
<li>A Gold Portal, beacon or False Son step that behaves differently in your run;</li>
<li>A Bulwark’s Ambry key or entrance detail that differs from the Russian guide;</li>
<li>A wrong screenshot, link or item name on a Risk of Rain 2 page.</li></ul>
<p>Include the page URL, your store or console edition, the game version and what happened. A screenshot helps us confirm the fix quickly.</p></section>
<section id="cannot"><h2>What we cannot help with</h2><p>We are not the developer or the game’s support team, so we cannot restore a save, fix a purchase or change how the game works. Use {ext('https://support.2k.com/hc/en-us/requests/new', '2K support')} or the {ext(HUB, 'Steam Community hub')} for that.</p></section>
</article></main>'''


def build(shell):
    pages = {
        'about': ({'title': 'About the Risk of Rain 2 Guides | Megabonk.org',
                   'description': 'Who writes the unofficial Risk of Rain 2 guides on Megabonk.org, where crossplay and unlock answers come from and how pages are rechecked.'}, about()),
        'contact': ({'title': 'Contact the Risk of Rain 2 Guide Editors | Megabonk.org',
                     'description': 'Report an outdated Risk of Rain 2 crossplay, Gold Portal or artifact answer, with what to include and what we cannot help with.'}, contact()),
    }
    for slug, (page, main) in pages.items():
        route = f'{P}{slug}/'
        html = shell(route, page['title'], page['description'], main, trust=True)
        p = ROOT / 'risk-of-rain-2' / slug / 'index.html'
        p.parent.mkdir(parents=True, exist_ok=True)
        write_html(p, html, encoding='utf-8')
