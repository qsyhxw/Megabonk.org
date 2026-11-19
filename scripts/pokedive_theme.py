"""PokeDive 游戏主题层与专区首页（SOP v3.22 02 §2.1、v3.24 02 §2.6、08 F9；LIGHT_CONTENT 先例同 pokearena-2d）。

对 /pokedive/、/pokedive/mobile/、/pokedive/shinies/ 现有 HTML 做幂等改写（不重建正文，避免 build_pokedive.py
与已发布页之间的引用漂移）：
- 三页都加载 /assets/pokedive/theme.css，移除借用的 /assets/pokebonk/site.css 与旧 /assets/pokedive/site.css；
  body 加 pd-theme，首页另加 pd-hub 与 hub.css；
- 左上主标识指向专区首页（02 §2.6）；分页手写的 “Related PokeDive tasks” 删除，由 register_page.py 生成；
- 首页：首屏（红面板 + 原作菜单图）→ 状态条 → 6 张任务卡 → 数据预览 → 最新更新 → 原有全文 → FAQ → More games；
  FAQ 的可见问答经 data/game-seo.json 生成 FAQPage。
title / description / H1 / canonical 保持已发布内容（00 §5A）。
页脚、About、Contact 沿用站级（02 §5.1 LIGHT_CONTENT）。
用法：python scripts/pokedive_theme.py，然后 python ../prompts/v3/模板/register_page.py . pokedive
"""
from html import escape
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
A = '/assets/pokedive/'
PAGES = {'/pokedive/': 'hub', '/pokedive/mobile/': 'platform', '/pokedive/shinies/': 'other'}

ICON = {
    'play': '<path d="M8 5v14l11-7z"/>',
    'key': '<circle cx="8" cy="15" r="4"/><path d="M11 12l9-9M16 7l3 3"/>',
    'phone': '<rect x="7" y="2" width="10" height="20" rx="2"/><path d="M11 18h2"/>',
    'spark': '<path d="M12 3l2.2 5.8L20 11l-5.8 2.2L12 19l-2.2-5.8L4 11l5.8-2.2z"/>',
    'ask': '<circle cx="12" cy="12" r="9"/><path d="M9.5 9.5a2.5 2.5 0 115 0c0 1.8-2.5 2-2.5 4M12 17h.01"/>',
    'save': '<path d="M5 3h11l3 3v15H5z"/><path d="M8 3v6h7V3M8 21v-7h8v7"/>',
}
TASKS = [
    ('play', 'Open the original game', 'Guest entry, partner choice and the first rescue.', '#start', 'Start'),
    ('key', 'Do you need a code?', 'The old REDDIT code was a Beta access code.', '#codes', ''),
    ('phone', 'Phone, PWA & offline', 'Landscape play, home-screen install, offline limits.', '/pokedive/mobile/', 'Guide'),
    ('spark', 'Shiny odds', 'Reported 2.5% and 5%, and how to tell a shiny.', '/pokedive/shinies/', 'Guide'),
    ('ask', 'Which game is this?', 'Tell PokéDive apart from PokeBonk and PokéSurvivor.', '#which-game', ''),
    ('save', 'Saves & accounts', 'What to keep before changing browsers.', '#save', ''),
]
UPDATES = [
    ('2026-11-05', '5 Nov 2026', 'Opening check in v0.7.4', 'User-assisted sign-in reached Mossy Woods Floor 1/25. Not a full run.', '#start'),
    ('2026-10-29', '29 Oct 2026', 'Night of Ghosts update announced', 'Advertised for 30 Oct–9 Nov 2026; those dates have passed.', '#current-event'),
    ('2026-10-28', '28 Oct 2026', 'Public access announced', 'The developer says guests no longer need the old Beta code.', '#codes'),
]
FAQ = [
    ('Is a PokeDive code needed to play?',
     'Not for entry. The old REDDIT code was a Beta access code, and the 28 October announcement says guests no longer need it. We have not verified a reward-code system.',
     '#codes', 'Code details'),
    ('Can I play PokeDive on a phone?',
     'The developer describes phone play in landscape and a PWA install option. A PWA is a website on your home screen, not a native APK or IPA.',
     '/pokedive/mobile/', 'Mobile guide'),
    ('Does PokeDive work offline?',
     'No offline route is verified here. A later developer reply said server processes prevent fully offline play, so keep a connection.',
     '/pokedive/mobile/#offline', 'Offline limits'),
    ('What are the PokeDive shiny odds?',
     'The developer reported 2.5% (1 in 40) in the Beta discussion, and 5% for eggs with a shiny parent. These are not odds measured by this site.',
     '/pokedive/shinies/', 'Shiny guide'),
    ('Will my guest save move to another browser?',
     'Not tested. An earlier developer reply said no Beta wipe was planned then, which is not a promise of cross-device recovery. Keep the same browser profile.',
     '#save', 'Save checks'),
    ('Is PokeDive the same game as PokeBonk?',
     'No. PokéDive is a separate fan project with its own accounts and progress. PokeBonk is a 3D survivor project, and PokéSurvivor is a 2D one.',
     '#which-game', 'Compare the names'),
]


def sub1(pattern, repl, text, flags=0):
    return re.sub(pattern, repl, text, count=1, flags=flags)


def head_and_body(text, route, kind):
    text = re.sub(r'<link rel="stylesheet" href="/assets/(?:pokebonk|pokedive)/site\.css[^"]*">', '', text)
    text = re.sub(r'<link rel="stylesheet" href="/assets/pokedive/(?:theme|hub)\.css[^"]*">', '', text)
    text = re.sub(r'<link rel="preload" href="/assets/fonts/mplus-rounded[^>]*>', '', text)
    links = (f'<link rel="preload" href="/assets/fonts/mplus-rounded-800-latin.woff2" as="font" type="font/woff2" crossorigin>'
             f'<link rel="stylesheet" href="{A}theme.css">' + (f'<link rel="stylesheet" href="{A}hub.css">' if kind == 'hub' else ''))
    text = re.sub(r'(<link rel="stylesheet" href="/assets/guide-article-layout\.css[^"]*">)', lambda m: m[1] + links, text, count=1)
    classes = 'guide-layout pd-theme pd-guide' + (' pd-hub' if kind == 'hub' else '')
    def body_tag(m):
        attrs = re.sub(r' data-format="[^"]*"', '', m[1])
        return f'<body{attrs} data-format="{kind}" class="{classes}"'
    text = re.sub(r'<body([^>]*?)\s*class="[^"]*"', body_tag, text, count=1)
    text = re.sub(r'<a class="brand" href="[^"]*"[^>]*><span>.*?</span></a>',
                  '<a class="brand" href="/pokedive/" aria-label="PokeDive guide home"><span>Poké<b>Dive</b><small>Unofficial guide</small></span></a>',
                  text, count=1, flags=re.S)
    text = re.sub(r'<section id="related">.*?</section>', '', text, flags=re.S)
    return text


def hub_main(text):
    m = re.search(r'<main class="wrap" id="main"><header class="article-head" id="guide">(.*?)</header>(<div class="article-layout">.*?</div>)(<section class="play-recommendations".*?</section>)</main>', text, re.S)
    if not m:
        if 'class="pd-hero"' in text:
            return text
        raise SystemExit('hub structure not recognised')
    head, layout, recs = m.groups()
    eyebrow = re.search(r'<p class="eyebrow">(.*?)</p>', head)[1]
    h1 = re.search(r'<h1>(.*?)</h1>', head)[1]
    answer = re.search(r'<div class="answer">(.*?)</div>', head, re.S)[1]
    byline = re.search(r'<p class="byline">(.*?)</p>', head)[1]
    fig = re.search(r'<figure class="game-image" data-game-image="pd-entry">.*?</figure>', layout, re.S)[0]
    layout = layout.replace(fig, '', 1)
    fig = fig.replace('loading="lazy"', 'loading="eager" fetchpriority="high"').replace('sizes="(max-width: 800px) calc(100vw - 36px), 1000px"', 'sizes="(max-width: 960px) calc(100vw - 28px), 560px"')
    ext = ('<a class="pd-btn" href="https://pokedive.com/en/" target="_blank" rel="noopener noreferrer">Open the original game ↗'
           '<span class="sr-only"> (pokedive.com, opens in a new tab)</span></a>')
    hero = (f'<section class="pd-hero" id="guide"><div class="wrap pd-hero-in"><div class="pd-hero-copy"><p class="eyebrow">{eyebrow}</p><h1>{h1}</h1>'
            '<ul class="pd-chips"><li>Free in your browser</li><li>Dungeons + village</li><li>Solo or up to 4</li></ul>'
            f'<div class="answer-text">{answer}</div>'
            f'<div class="pd-hero-cta">{ext}<a class="pd-btn ghost" href="/pokedive/mobile/">Phone &amp; PWA</a></div>'
            f'<p class="byline">{byline}</p></div>{fig}</div></section>')
    status = ('<div class="pd-status"><div class="wrap"><span><b>Browser</b> · free</span><span><b>Version</b> v0.7.4 checked</span>'
              '<span><b>Pages</b> 3 tasks</span><span><b>Fan project</b> · unofficial</span></div></div>')
    cards = ''.join(
        f'<li><a class="pd-task" href="{u}"><span class="ico"><svg viewBox="0 0 24 24" aria-hidden="true">{ICON[i]}</svg></span>'
        f'<strong>{escape(t)}</strong><span class="d">{escape(d)}</span>' + (f'<span class="tag">{tag}</span>' if tag else '') + '</a></li>'
        for i, t, d, u, tag in TASKS)
    tasks = (f'<section class="pd-section" id="tasks"><div class="wrap"><h2>Pick a task</h2>'
             f'<p class="pd-lede">Six answers from the checks below.</p><ul class="pd-tasks">{cards}</ul></div></section>')
    preview = ('<section class="pd-section" id="preview"><div class="wrap"><h2>Quick facts</h2><div class="pd-preview">'
               '<div class="pd-card"><h3>Shiny odds, as the developer reported them</h3><div class="pd-odds">'
               '<div><b>2.5%</b><small>1 in 40 per opportunity</small></div><div><b>5%</b><small>1 in 20 for eggs with a shiny parent</small></div></div>'
               '<div class="pd-pair"><img src="/assets/pokedive/grovyle-normal-40.webp" width="40" height="40" loading="lazy" alt="Normal Grovyle portrait, green with a red belly">'
               '<img src="/assets/pokedive/grovyle-shiny-40.webp" width="40" height="40" loading="lazy" alt="Shiny Grovyle portrait, blue variant"><span>Normal and shiny Grovyle, original 40px portraits</span></div>'
               '<p>From the Beta discussion; not measured by this site. <a href="/pokedive/shinies/#odds">See the conditions →</a></p></div>'
               '<div class="pd-card pd-event"><h3>Latest opening check</h3><b>v0.7.4</b><p>Tepig, the village, then Mossy Woods Floor 1/25 with the first ability lesson.</p>'
               '<p>An opening-state check, not a full run. <a href="#start">Follow the steps →</a></p></div></div></div></section>')
    ups = ''.join(f'<li><time datetime="{iso}">{lab}</time><div><a href="{u}">{escape(t)}</a><span>{escape(d)}</span></div></li>' for iso, lab, t, d, u in UPDATES)
    updates = f'<section class="pd-section" id="updates"><div class="wrap"><h2>Latest updates</h2><ul class="pd-updates">{ups}</ul></div></section>'
    faq = ''.join(f'<details><summary>{escape(q)}</summary><p>{escape(a)} <a href="{u}">{escape(l)} →</a></p></details>' for q, a, u, l in FAQ)
    faq = f'<section class="pd-faq" id="faq"><h2>Quick answers</h2>{faq}</section>'
    body = (f'<main id="main">{hero}{status}{tasks}{preview}{updates}<div class="wrap pd-guide-wrap">'
            f'<h2 class="pd-guide-title" id="full-guide">The full starting checks</h2>{layout}{faq}{recs}</div></main>')
    return text[:m.start()] + body + text[m.end():]


def process(route, kind):
    path = ROOT / route.strip('/') / 'index.html'
    text = path.read_text(encoding='utf-8')
    text = head_and_body(text, route, kind)
    if kind == 'hub':
        text = hub_main(text)
    from site_analytics import _version_css
    text = _version_css(text)
    from game_seo import edit as edit_seo
    text = edit_seo(path, text)
    path.write_text(text, encoding='utf-8', newline='')
    print('themed', route)


if __name__ == '__main__':
    for r, k in PAGES.items():
        process(r, k)
