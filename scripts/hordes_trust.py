"""Hordes of Azeroth 专区 About / Contact（SOP v3.25，02 §5.1）。

在 build_hordes_of_azeroth.py 中先于 register_page.py 运行，导航与页脚由后者填充。信任页不放广告。
事实全部来自本专区已有页面及其引用的作者资料，不新增游戏信息。Privacy 保持站级页（#hordes-of-azeroth）。"""
import json
from html import escape
from pathlib import Path

from site_analytics import write_html

ROOT = Path(__file__).resolve().parents[1]
P = '/hordes-of-azeroth/'
CHECKED = '5 November 2026'
REPO = 'https://github.com/jonhaldors/hordes-of-azeroth'
RELEASE = REPO + '/releases'


def email():
    return json.loads((ROOT / 'config/site-contact.json').read_text(encoding='utf8'))['email']


def ext(url, label):
    return f'<a href="{escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">{label} ↗<span class="sr-only"> (opens in a new tab)</span></a>'


def about():
    return f'''<article class="legal"><header class="article-head"><p>Hordes of Azeroth · About</p><h1>About the Hordes of Azeroth guide</h1>
<p class="byline">Megabonk.org editors · Facts reviewed {CHECKED}</p></header>
<section id="who"><h2>Who runs this section</h2><p>This is an unofficial fan guide published by the editors of Megabonk.org, an independent site for survivors-style games. We are not jonhaldors, who makes Hordes of Azeroth, and we are not Blizzard Entertainment, which owns World of Warcraft; nothing here is an official announcement.</p></section>
<section id="covers"><h2>What it covers</h2><p>The section answers the questions that come before and during a first install: which client files the <a href="{P}">install and platform page</a> expects, how to pick between this project and Aethus's browser game in <a href="{P}vs-azeroth-survivors/">the comparison</a>, how to find the failing stage in <a href="{P}install-troubleshooting/">installation troubleshooting</a>, and a Chinese start page at <a href="{P}zh/getting-started/" lang="zh-Hans">中文入门</a>.</p><p>It does not rank classes or publish builds for this game.</p></section>
<section id="sources"><h2>Where the answers come from</h2><ul>
<li><strong>The author's repository:</strong> the {ext(REPO, 'README')} supplies the client build, disk space, platforms, install steps and co-op rules; the {ext(RELEASE, 'releases page')} supplies the launcher files and version notes.</li>
<li><strong>Named public reports:</strong> GitHub issues and launch threads supply the installation symptoms and the Mac / Wine report, each limited to what its reporter described.</li>
<li><strong>Author gameplay footage:</strong> screenshots are frames from the author's own recording and a reported error screen. We have not installed the client or played a run, and the pages do not claim to.</li></ul></section>
<section id="updates"><h2>How pages stay current</h2><p>Each guide shows the date it was checked, currently {CHECKED}, against version 0.6.4. When the author publishes a new release, the pages that depend on its requirements, platform list or co-op rules are rechecked first.</p></section>
<section id="identity"><h2>Which game is this?</h2><p>Searches for the name also return similarly named websites and Azeroth Survivors. This guide follows jonhaldors's repository only; the author states that the hordes-of-azeroth.com website is not run by him.</p></section>
<section id="corrections"><h2>Found something wrong?</h2><p>Send the page URL, your operating system, the launcher version and what you saw through the <a href="{P}contact/">contact page</a>. Corrections backed by a screenshot or the author's own statement are usually applied in the next update.</p></section></article>'''


def contact():
    mail = email()
    return f'''<article class="legal"><header class="article-head"><p>Hordes of Azeroth · Contact</p><h1>Contact the Hordes of Azeroth guide editors</h1>
<p class="byline">Reviewed {CHECKED}</p></header>
<section id="write"><h2>Email</h2><p>Write to <a href="mailto:{mail}?subject=%5BHordes%20of%20Azeroth%5D%20Guide%20feedback">{mail}</a>. Useful reports for this section:</p><ul>
<li>A client requirement, platform or co-op rule that changed in a newer release;</li>
<li>An installation message or fix that does not match the stage described on the troubleshooting page;</li>
<li>A wrong project identification, link or screenshot on a Hordes of Azeroth page;</li>
<li>A Chinese start-page step that no longer matches the launcher.</li></ul>
<p>Include the page URL, your operating system, the launcher version and what happened. A screenshot helps us confirm the fix quickly.</p></section>
<section id="cannot"><h2>What we cannot help with</h2><p>We are not the author or the project's support, so we cannot repair an installation, recover a save or change how the game works. Use the launcher's Report a bug option or the author's {ext(REPO, 'GitHub repository')} for those.</p></section></article>'''


def build():
    from build_hordes_of_azeroth import shell
    pages = {
        'about': ('About the Hordes of Azeroth Guide | Megabonk.org',
                  'Who writes the unofficial Hordes of Azeroth guides on Megabonk.org, where the answers come from and how pages are rechecked after new releases.', about()),
        'contact': ('Contact the Hordes of Azeroth Guide Editors | Megabonk.org',
                    'Report an outdated Hordes of Azeroth client requirement, platform, installation or co-op answer, with what to include and what we cannot help with.', contact()),
    }
    for slug, (title, desc, body) in pages.items():
        p = ROOT / 'hordes-of-azeroth' / slug / 'index.html'
        p.parent.mkdir(parents=True, exist_ok=True)
        write_html(p, shell(f'{P}{slug}/', title, desc, body, trust=True), encoding='utf8')
