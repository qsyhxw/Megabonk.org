"""通用专区首页组件（SOP v3.26，02 §4 / 08 F9）。

把 F9 首页的固定骨架渲染成 HTML 片段：英雄区 → 任务卡 → 速查 → 最新更新 → 分组入口 → FAQ。
内容全部来自页面清单 data/{game}-pages.json（字段见 模板/pages.small-hub.example.json），
本模块不含任何游戏文案；游戏相关的文案（H1、状态行、速查条目、信任页正文）由调用方传入。

用法（生成脚本里）：
    from hub_components import Hub
    h = Hub(manifest, base='/spires-of-azeroth/', prefix='saz', asset_dir='/assets/spires-of-azeroth/')
    body = h.hero(kicker=..., title=..., sub='Guide & Wiki', deck=..., status=[...], actions=[...])
    body += h.cards() + 游戏窗口等自定义块 + h.cheat(...) + h.updates() + h.groups() + h.faq()
    faq 问题列表：h.faq_questions()（登记到 data/game-seo.json 的 questions / reviewed_candidates）

样式：`python hub_components.py --css PREFIX` 输出带前缀的布局 CSS（颜色全部走 --hub-* 变量，
在游戏 theme.css 里把 --hub-* 映射到本游戏配色）。<body> 需带 `{prefix}-theme {prefix}-hub` 类。
导航、面包屑、页脚仍由 register_page.py 生成，本模块不碰。

清单字段：cards[{label,href,thumb,blurb}]、updates[{date,text,label,href}]、
groups[{label,text,items:[[href,title,desc]]}]、faq[{q,a,href}]；href 以 "/" 开头为站内绝对路径，
否则按专区 base 相对（"#x"、"sub/#y"）。缩略图 {asset_dir}{thumb_dir}/{thumb}-480.webp（16:9 真实游戏截图裁切）。
"""
import sys
from html import escape
from pathlib import Path


class Hub:
    def __init__(self, manifest, base, prefix, asset_dir, thumb_dir='images', thumb_suffix='-480.webp', eager_cards=4):
        self.m, self.base, self.p = manifest, base, prefix
        self.asset_dir, self.thumb_dir, self.thumb_suffix, self.eager = asset_dir, thumb_dir, thumb_suffix, eager_cards

    def href(self, h):
        return h if h.startswith('/') else self.base + h

    def _a(self, h):
        return escape(self.href(h), quote=True)

    def hero(self, kicker, title, sub, deck, status, actions, bg_attr='data-play-background'):
        """H1 含游戏名 + Guide/Wiki（08 F9）：title 放游戏名，sub 放 Guide & Wiki。actions=[(label,href,secondary?)]。"""
        p = self.p
        btns = ''.join(f'<a class="button{" secondary" if sec else ""}" href="{escape(h, quote=True)}">{escape(l)}</a>' for l, h, sec in actions)
        sts = ''.join(f'<li>{escape(s)}</li>' for s in status)
        return (f'<header class="{p}-hero" id="guide" {bg_attr}><p class="{p}-kicker">{escape(kicker)}</p>'
                f'<h1>{escape(title)}<span class="{p}-h1-sub">{sub}</span></h1><p class="{p}-deck">{deck}</p>'
                f'<ul class="{p}-status" aria-label="Game status">{sts}</ul><div class="hero-actions">{btns}</div></header>')

    def cards(self, heading='Pick your task', bg_attr='data-play-background'):
        p = self.p
        items = ''.join(
            f'<li><a class="{p}-card" href="{self._a(c["href"])}"><img src="{self.asset_dir}{self.thumb_dir}/{c["thumb"]}{self.thumb_suffix}" '
            f'width="480" height="270" alt="" loading="{"eager" if i < self.eager else "lazy"}"><span class="{p}-card-body"><strong>{escape(c["label"])}</strong>'
            f'<span class="{p}-card-text">{escape(c["blurb"])}</span></span></a></li>' for i, c in enumerate(self.m['cards']))
        return f'<section class="{p}-tasks" id="guides" {bg_attr}><h2>{escape(heading)}</h2><ul class="{p}-cards">{items}</ul></section>'

    def cheat(self, title, intro, rows, bg_attr='data-play-background'):
        """数据预览块（08 F9 首屏“真实数据预览”）：rows=[(名称, 已转义的 HTML 说明)]。"""
        p = self.p
        dl = ''.join(f'<div><dt>{a}</dt><dd>{b}</dd></div>' for a, b in rows)
        return f'<section class="{p}-cheat" id="cheat-sheet" {bg_attr}><h2>{escape(title)}</h2><p>{intro}</p><dl>{dl}</dl></section>'

    def updates(self, heading='Latest updates', bg_attr='data-play-background'):
        p = self.p
        rows = sorted(self.m['updates'], key=lambda u: u['date'], reverse=True)
        li = ''.join(f'<li><time datetime="{u["date"]}">{u["date"]}</time><span>{escape(u["text"])} '
                     f'<a href="{self._a(u["href"])}">{escape(u["label"])} →</a></span></li>' for u in rows)
        return f'<section class="{p}-band" id="updates" {bg_attr}><h2>{escape(heading)}</h2><ul class="{p}-updates">{li}</ul></section>'

    def groups(self, heading='All guides by task', bg_attr='data-play-background'):
        p = self.p
        out = ''
        for g in self.m['groups']:
            links = ''.join(f'<li><a href="{self._a(h)}">{escape(t)} <span>{escape(d)}</span></a></li>' for h, t, d in g['items'])
            out += f'<div class="{p}-group"><h3>{escape(g["label"])}</h3><p>{escape(g["text"])}</p><ul>{links}</ul></div>'
        return f'<section class="{p}-band" id="all-guides" {bg_attr}><h2>{escape(heading)}</h2><div class="{p}-groups">{out}</div></section>'

    def faq(self, heading='Common questions', more='Full answer →', bg_attr='data-play-background'):
        p = self.p
        items = ''.join(f'<details><summary>{escape(f["q"])}</summary><p>{escape(f["a"])}</p>'
                        f'<a class="{p}-faq-more" href="{self._a(f["href"])}">{escape(more)}</a></details>' for f in self.m['faq'])
        return f'<section class="{p}-band" id="faq" {bg_attr}><h2>{escape(heading)}</h2><div class="{p}-faq">{items}</div></section>'

    def faq_questions(self):
        return [f['q'] for f in self.m['faq']]


CSS_FILE = Path(__file__).with_name('hub-components.css')


def css(prefix):
    return CSS_FILE.read_text(encoding='utf8').replace('__P__', prefix)


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--css':
        sys.stdout.write(css(sys.argv[2]))
    else:
        print(__doc__)
