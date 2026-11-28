"""生成 /games/ 索引页：按 data/games-index-groups.json 分组，卡片由 game_sections.card_html 渲染（与首页同源）。

用法：python scripts/build_games_index.py
- 页面为 noindex,follow 的导航页（无搜索需求，且分组增量有限，见 ROADMAP SHEJI-B7），因此不会进入 sitemap。
- 分组数据必须与 data/game-sections.json 一一对应，不一致时直接报错，防止首页与索引页漂移。
"""
import json
import sys
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from game_sections import card_html, games  # noqa: E402
from site_analytics import write_html  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://megabonk.org'
PATH = '/games/'
TITLE = 'All Games Covered on Megabonk.org'
DESC = 'Browse every related game that has a start page on Megabonk.org, grouped by theme, with a short note on what each guide covers.'

NAV = ('<a href="/guides/">Guides</a><a href="/guides/builds/">Builds</a>'
       '<a href="/database/">Database</a><a href="/mods/">Mods</a>')
FOOTER = (
    '<footer class="footer"><div class="footer-in"><div><p class="footer-brand">Megabonk<span>.org</span></p>'
    '<p>Independent player resource, not the developer or publisher of the games or mods covered.</p></div>'
    '<div><h3>Guides</h3><ul><li><a href="/guides/">All Guides</a></li><li><a href="/guides/builds/">Builds</a></li>'
    '<li><a href="/guides/characters/">Characters</a></li><li><a href="/guides/unlocks/">Unlocks</a></li></ul></div>'
    '<div><h3>Database</h3><ul><li><a href="/database/weapons/">Weapons</a></li><li><a href="/database/tomes/">Tomes</a></li>'
    '<li><a href="/database/items/">Items</a></li><li><a href="/mods/">Mods</a></li></ul></div>'
    '<div><h3>Site</h3><ul><li><a href="/about/">About</a></li><li><a href="/contact/">Contact</a></li>'
    '<li><a href="/privacy-policy">Privacy</a></li></ul></div></div></footer>'
)


def load_groups(all_games):
    data = json.loads((ROOT / 'data/games-index-groups.json').read_text(encoding='utf-8'))
    registered = [g['id'] for g in all_games]
    listed = [i for grp in data['groups'] for i in grp['ids']]
    missing = sorted(set(registered) - set(listed))
    extra = sorted(set(listed) - set(registered))
    dupes = sorted({i for i in listed if listed.count(i) > 1})
    if missing or extra or dupes:
        raise SystemExit(f'games-index-groups.json 与 game-sections.json 不一致：缺少 {missing}，多余 {extra}，重复 {dupes}')
    return data['groups']


def render():
    all_games = games()
    by_id = {g['id']: g for g in all_games}
    groups = load_groups(all_games)
    sections = []
    for grp in groups:
        cards = ''.join(card_html(by_id[i]) for i in grp['ids'])
        sections.append(
            f'<section id="{escape(grp["id"])}"><h2>{escape(grp["title"])}</h2><p class="group-intro">{escape(grp["intro"])}</p>'
            f'<div class="games-grid">{cards}</div></section>'
        )
    jump = ''.join(f'<a href="#{escape(g["id"])}">{escape(g["title"])}</a>' for g in groups)
    lead = (f'Megabonk.org is an independent guide site. Besides Megabonk itself, it has start pages for {len(all_games)} related games. '
            'Each card opens that game\'s own start page on this site.')
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(TITLE)}</title><meta name="description" content="{escape(DESC, quote=True)}"><meta name="robots" content="noindex,follow"><link rel="canonical" href="{BASE+PATH}"><link rel="icon" href="/favicon.ico"><link rel="stylesheet" href="/assets/site.css"><link rel="stylesheet" href="/assets/games-index.css"></head><body class="games-index"><a class="skip" href="#main">Skip to content</a><header class="header"><div class="nav"><a class="logo" href="/">Megabonk<span>.org</span></a><nav class="main-desktop" aria-label="Main navigation" style="display:flex;gap:1.2rem">{NAV}</nav><details class="main-mobile"><summary>Menu</summary><nav aria-label="Mobile navigation">{NAV}</nav></details></div></header><main id="main"><nav class="crumb" aria-label="Breadcrumb"><a href="/">Home</a> / Games</nav><header><p class="eyebrow">Independent player guides</p><h1>Games covered on Megabonk.org</h1><p class="lead">{escape(lead)}</p></header><nav class="jump" aria-label="On this page">{jump}</nav>{"".join(sections)}</main>{FOOTER}</body></html>'''


def main():
    out = ROOT / 'games' / 'index.html'
    out.parent.mkdir(parents=True, exist_ok=True)
    write_html(out, render(), encoding='utf-8')
    print(f'Built {out.relative_to(ROOT)} with {len(games())} game cards in {len(load_groups(games()))} groups (noindex,follow).')


if __name__ == '__main__':
    main()
