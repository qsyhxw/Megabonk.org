"""Risk of Rain 2 专区首页（08 F9）：由 hub_components.Hub 读取 data/risk-of-rain-2-pages.json 渲染。

首页文案（H1、状态行、起步分流）写在这里，任务卡/更新/分组/FAQ 来自页面清单。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = '/risk-of-rain-2/'
TITLE = 'Risk of Rain 2 Guides: Crossplay, Gold Portal & Artifacts'
DESC = ('Choose a Risk of Rain 2 guide for crossplay, the Gold Portal and False Son route, or Bulwark’s Ambry. '
        'Find the right starting point for your run.')

START = (
    '<ul><li><strong>Joining a friend?</strong> Start with <a href="/risk-of-rain-2/crossplay/#check">both copies and their settings</a>. '
    'The guide separates store compatibility, console generations and invitations.</li>'
    '<li><strong>Already carrying Halcyon Seed?</strong> Use the <a href="/risk-of-rain-2/gold-portal/#start">starting-point table</a> to pick up the route where you are. '
    'Check the DLC and exit conditions before continuing toward False Son.</li>'
    '<li><strong>Looking for the artifact chamber?</strong> The <a href="/risk-of-rain-2/ru/bulwarks-ambry/" hreflang="ru" lang="ru">Russian trial guide</a> covers entry and keys. '
    'Its language is marked so you can choose the appropriate guide.</li></ul>')

NOTES = ('<p>Megabonk.org is an independent guide site. Each linked guide keeps the sources and version conditions relevant to its task. '
         'The header image is from the official 1.0 launch footage and shows the game’s co-op setting. Guide facts were last checked on 5 November 2026.</p>')


def manifest():
    m = json.loads((ROOT / 'data/risk-of-rain-2-pages.json').read_text(encoding='utf8'))
    m['by'] = {p['slug']: p for p in m['pages']}
    return m


def render(frame):
    """返回 (完整页面 HTML, 首页 FAQ 问题列表)。"""
    from hub_components import Hub
    m = manifest()
    h = Hub(m, BASE, 'ror', '/assets/risk-of-rain-2', thumb_dir='')
    bg = ''
    pv = m['preview']
    hero = h.hero(
        kicker='Independent player guides · Hopoo Games’ co-op roguelike',
        title='Risk of Rain 2 ', sub='guides — crossplay, Gold Portal and artifacts',
        deck='Get your group connected, follow the Gold Portal route, or work through an artifact trial. Choose the guide that matches what you are trying to do.',
        status=['Co-op action roguelike', 'Facts checked 5 Nov 2026', 'Unofficial fan guide'],
        actions=[('Pick a guide ↓', '#guides', False), ('Start from your problem', '#choose', True)], bg_attr=bg)
    cards = h.cards(heading='Pick the guide for your goal', bg_attr=bg)
    cheat = h.cheat(pv['title'], pv['intro'], [(a, b) for a, b in pv['rows']], bg_attr=bg)
    choose = f'<section class="ror-band ror-choose" id="choose"><h2>Choose before you commit</h2>{START}</section>'
    notes = f'<section class="ror-band" id="notes"><h2>About these guides</h2>{NOTES}</section>'
    body = hero + cards + cheat + choose + h.updates(bg_attr=bg) + h.groups(bg_attr=bg) + h.faq(bg_attr=bg) + notes
    main = f'<main class="wrap" id="main">{body}</main>'
    return frame(BASE, TITLE, DESC, main, og='website'), h.faq_questions()
