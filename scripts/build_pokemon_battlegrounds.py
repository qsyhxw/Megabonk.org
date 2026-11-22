"""PB Ranked original-host entry. Never embed the publisher's DENY-protected client.

专区主题（theme.css/hub.css）、首页组件、清单驱动的导航与页脚见 SOP v3.26（sheji，2026-11-22）。
首页任务卡/更新/分组/FAQ 读 data/pokemon-battlegrounds-pages.json；导航与页脚由 register_page.py 最后一步生成。"""
from pathlib import Path
import json
import re
import subprocess
import sys
from html import escape, unescape
from guide_images import decorate
from play_recommendations import recommendations, stylesheet
from site_analytics import write_html

ROOT = Path(__file__).resolve().parents[1]
ROUTE = '/pokemon-battlegrounds/'
GAME = 'https://pbranked.com/'
OLD_HOST = 'ranked.pokemonbattlegrounds.com'
CHANNEL = 'https://pokemonbattlegrounds.com/'
CHECKED = '5 November 2026'
ADDRESS_CHECKED = '22 November 2026'
ADS = '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8830315294299920" crossorigin="anonymous"></script>'


def manifest():
    return json.loads((ROOT / 'data/pokemon-battlegrounds-pages.json').read_text(encoding='utf-8'))


def hub(m):
    from hub_components import Hub
    return Hub(m, ROUTE, 'pbg', '/assets/pokemon-battlegrounds/')


def shell(route, page, body_cls, extra_css, main, og_type='article'):
    """首页与信任页共用外壳：只加载本专区 theme.css（首页另加 hub.css），导航/页脚留空由 register_page.py 填充。"""
    t, d = escape(page['title']), escape(page['description'], quote=True)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{t}</title><meta name="description" content="{d}">
<link rel="canonical" href="https://megabonk.org{route}"><meta property="og:type" content="{og_type}"><meta property="og:title" content="{t}"><meta property="og:description" content="{d}"><meta property="og:url" content="https://megabonk.org{route}"><meta property="og:image" content="https://megabonk.org/assets/pokemon-battlegrounds/login-panel-640.webp">
<link rel="stylesheet" href="/assets/guide-article-layout.css"><link rel="stylesheet" href="/assets/pokemon-battlegrounds/theme.css">{extra_css}</head>
<body class="guide-layout pbg-theme {body_cls}"><a class="skip" href="#main">Skip to content</a><header class="top"><div class="wrap"><a class="brand" href="{ROUTE}"><span>Pokémon Battlegrounds<small>Unofficial PB Ranked guide</small></span></a><nav class="desktop-nav" aria-label="Pokémon Battlegrounds tasks"></nav><details class="mobile-nav"><summary>Menu</summary><nav class="mobile-links" aria-label="Pokémon Battlegrounds tasks"></nav></details></div></header>
{main}<footer class="footer"></footer></body></html>'''


def table(label, head, rows):
    th = ''.join(f'<th scope="col">{h}</th>' for h in head)
    tr = ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows)
    return f'<div class="table-wrap" tabindex="0" role="region" aria-label="{label}"><table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'


def ext(url, label):
    return f'<a href="{url}" target="_blank" rel="noopener noreferrer">{label} ↗</a>'


def hero():
    status = ['Browser · free · real-time', 'Sign-in: Discord or Google', f'Updated {ADDRESS_CHECKED}', 'Unofficial fan guide']
    sts = ''.join(f'<li>{s}</li>' for s in status)
    return f'''<header class="pbg-hero" id="guide" data-play-background><div><p class="pbg-kicker eyebrow">PB Ranked · Independent start guide</p>
<h1>Pokémon Battlegrounds<span class="pbg-h1-sub">Guide &amp; Wiki</span></h1>
<p class="pbg-deck">The playable game from the Pokémon Battlegrounds animation channel is <strong>PB Ranked</strong>: real-time battles in your browser. It now lives at <strong>pbranked.com</strong> and asks you to <strong>sign in with Discord or Google</strong> before your first match.</p>
<ul class="pbg-status" aria-label="Game status">{sts}</ul>
<div id="play"><div class="hero-actions"><a class="button" href="{GAME}" target="_blank" rel="noopener noreferrer">Open PB Ranked ↗<span class="sr-only"> (opens in a new tab)</span></a><a class="button secondary" href="#start">First battle →</a></div>
<p class="pbg-dest">Destination: pbranked.com. The publisher blocks embedding, so the game opens in its own tab. By Megabonk.org · Unofficial guide.</p></div></div><!--PB_ENTRY_FIGURE--></header>'''


def cheat():
    k = lambda s: f'<kbd>{s}</kbd>'
    rows = [('Move', f'{k("W")} {k("A")} {k("S")} {k("D")} in Manual.'),
            ('Call a move', f'{k("1")}–{k("4")}, in Auto or Manual.'),
            ('Dodge', f'{k("Space")} in Manual; Auto dodges for you.'),
            ('Bench · Mega', f'{k("Z")} {k("X")} {k("C")} switch; {k("M")} Mega Evolves.')]
    dl = ''.join(f'<div><dt>{a}</dt><dd>{b}</dd></div>' for a, b in rows)
    return (f'<section class="pbg-cheat" id="cheat" data-play-background><h2>Default keys</h2><p>From the client’s in-game help ({CHECKED}). Open the controller icon in the game to see your current bindings.</p><dl>{dl}</dl></section>')


def sections():
    sec = lambda sid, body: f'<section class="pbg-sec" id="{sid}" data-play-background>{body}</section>'
    out = []
    out.append(sec('address', f'''<h2>Use the new address: pbranked.com</h2>
<p class="pbg-notice"><strong>PB Ranked has a new address.</strong> On {ADDRESS_CHECKED} the old {OLD_HOST} address showed a notice that your account, rank, teams and settings come with you, and that the old address forwards to the new one on its own. Use {ext(GAME, 'pbranked.com')} directly.</p>
<p>If you see a gallery of animated battles or a Masters Eight ballot, you are on the channel website, not the PB Ranked client. The channel site is a different destination; see <a href="#which-game">the table below</a>.</p>'''))
    out.append(sec('start', '''<h2>Start with the right account and mode</h2><p><strong>Start with an Easy practice battle to learn your team without risking rating.</strong> You will need to sign in before choosing your Pokémon and entering practice.</p><ol><li><strong>Open the game.</strong> Use the button at the top of this page; it opens pbranked.com in a new tab.</li><li><strong>Check whether you are returning.</strong> Existing players should sign in with the same Discord or Google account. New players are prompted to pick a trainer name of 2–16 characters and a trainer before signing in. Some trainer choices show rating or star requirements; do not assume every portrait is available immediately.</li><li><strong>Read the help before queuing.</strong> The top-bar <strong>?</strong> opens How battles work even on the sign-in screen. Use the controller icon to inspect current key bindings.</li><li><strong>After sign-in, prepare your team, then choose Practice vs bot → Easy.</strong> For the inspected 3v3 format, Your team shows three slots. Use the Pokémon list to fill your team and click a team member to inspect its moves. The practice chooser offers Easy, Casual, Normal, Hard and Hardest, with no rating on the line. Read the selected moves and try Auto before switching to Manual. Use <strong>Find battle</strong> when you intend to seek an opponent; practice is a separate button, not the Ranked/Unranked selector.</li></ol><p>If you cannot reach the team screen, use the original client’s help or choose <a href="#more-games">another browser game</a>. PB Ranked requires sign-in; a guest route has not been verified.</p>'''))
    out.append(sec('controls', '<h2>Choose Auto, called moves or full Manual control</h2><p>PB Ranked’s in-game help describes three control options. Try Auto first, then take over attacks or movement when you are ready.</p>' + table('PB Ranked control choices', ['Your choice', 'What the client says it does', 'What to do next'], [
        ['Auto', 'Your Pokémon moves, dodges and chooses attacks itself. You can still call one of its four moves.', 'Watch cooldown and range. A glowing move button means ready and in range; a called move waits for the current attack to finish.'],
        ['Auto movement, your attacks', 'Turning off <strong>Auto attacks for me</strong> keeps automatic movement and dodging, but attacks only when you call a move.', 'Look under your trainer settings after sign-in. This is a different choice from full Manual.'],
        ['Manual', 'Press Auto to switch to Manual. You steer, call attacks and trigger Dodge yourself.', 'The inspected defaults show WASD movement, 1–4 moves and Space dodge. Read Controls if you change bindings.']]) + '<p>The help shows Z/X/C for bench switches and M for Mega Evolve or Greninja’s Battle Bond, when applicable. The client lists controller support and recommends landscape orientation on phones. Neither was tested on a physical device in our check.</p><p><strong>Leaving the tab is not a pause.</strong> The help says your team keeps fighting if you leave a match, and you lose if you are absent when it ends. Do not use tab switching as a pause strategy.</p>'))
    out.append(sec('account', f'''<h2>Keep your account separate from other fan games</h2><p>The project’s privacy notice (updated 1 November 2026) says PB Ranked keeps your trainer, rating, win/loss record and matches on its server, while settings, teams and a sign-in code use your browser’s local storage. It describes Discord/Google sign-in as sharing an account ID, rather than giving the game your password.</p><p>Return using the same sign-in provider and account. Do not assume that PB Ranked, Poké Arena 2D, Apex Arena or PokeBonk share trainers, teams, saves or ratings. The project says ratings may reset at a season boundary and that the game can change or stop during development.</p><p>For account or game issues, use <strong>Report a problem</strong> in the original client, or <a href="mailto:stinsonoscar@gmail.com">PB Ranked developer email ↗</a>. Do not send passwords or sign-in codes. Megabonk.org cannot recover an original-game account.</p>'''))
    out.append(sec('which-game', '<h2>Tell PB Ranked apart from other Pokémon battle projects</h2>' + table('Identify Pokémon Battlegrounds and separate fan games', ['Project', 'Recognize the destination', 'Use this route'], [
        ['PB Ranked', 'pbranked.com; real-time browser battles from the animation channel.', '<a href="#play">Original-game launch above</a>'],
        ['Pokémon Battlegrounds channel', 'pokemonbattlegrounds.com; animated match gallery and voting, rather than the ranked client.', ext(CHANNEL, 'Pokémon Battlegrounds · channel website')],
        ['Pokémon Apex Arena', 'pokemonapexarena.com; its creator explicitly describes a separate fan project inspired by the Battlegrounds videos.', ext('https://pokemonapexarena.com/', 'Pokémon Apex Arena · separate project')],
        ['Poké Arena 2D', 'pokearena2d.com; a separate arena game with its own Training setup, controls and progress.', '<a href="/pokearena-2d/">Original game &amp; Training guide</a>'],
        ['PokeBonk / PokéSurvivor', 'Pokémon-themed survival games with hordes and run progression, rather than this ranked client.', '<a href="/pokebonk/play/">PokeBonk</a> · <a href="/poke-survivor/play/">PokéSurvivor</a>']]) + '<p>Apex Arena’s creator identifies it as a separate project inspired by the channel. Use the destination above to avoid following another game’s controls or account instructions.</p>'))
    return out


def sources():
    return f'''<section class="sources pbg-sec" id="sources" data-play-background><h2>Sources &amp; checks</h2>
<p>Checked {CHECKED}: sign-in, in-game help, team selection and an Easy practice battle through its result screen. The new address was confirmed on {ADDRESS_CHECKED}: pbranked.com loads the game, and the old address shows a forwarding notice. Gameplay instructions follow the client’s help; competitive performance and account transfer were not tested. The development build showed no version number.</p>
<ul>
<li>{ext(GAME, 'PB Ranked')} — game entry, controls and practice options.</li>
<li>{ext('https://www.youtube.com/watch?v=23gz_hdNsrc', 'Creator’s announcement')} — identifies the ranked game; 30 October 2026.</li>
<li>{ext(GAME + 'privacy', 'PB Ranked privacy')} / {ext(GAME + 'terms', 'terms')} — account storage and season resets; both updated 1 November 2026.</li>
<li>{ext('https://pokemonapexarena.com/', 'Apex Arena')} — creator’s statement that it is a separate project.</li>
</ul></section>'''


def homepage(m):
    h = hub(m)
    s = sections()
    body = hero() + h.cards() + cheat() + s[0] + s[1] + s[2] + s[3] + s[4] + h.updates() + h.groups() + h.faq() + sources() + recommendations('pokemon-battlegrounds')
    return f'<main class="wrap" id="main">{body}</main>', h.faq_questions()


def accessible_links(html):
    """外链文字补上“外部网站、新标签页打开”的无障碍说明。"""
    def fix(match):
        tag, text = match.groups()
        if 'target="_blank"' not in tag or 'aria-label=' in tag or 'sr-only' in text:
            return match[0]
        label = escape(unescape(text).strip() + ' (external website, opens in a new tab)', quote=True)
        return tag[:-1] + f' aria-label="{label}">' + text + '</a>'
    return re.sub(r'(<a\b[^>]*>)([^<]*(?:<span[^>]*>.*?</span>)?)</a>', fix, html)


def build():
    m = manifest()
    page = {'title': 'Pokémon Battlegrounds: Original Game & Start Guide', 'description': 'Find PB Ranked, the Pokémon Battlegrounds browser game, at its new address. Check its sign-in requirement, Auto and Manual controls, and the correct original-game link.'}
    main, questions = homepage(m)
    html = shell(ROUTE, page, 'pbg-hub', '<link rel="stylesheet" href="/assets/pokemon-battlegrounds/hub.css">', main, 'website')
    html = html.replace('</head>', ADS + '</head>', 1)
    html = decorate(ROUTE, stylesheet(html))
    figure = re.search(r'<figure class="game-image.*?</figure>', html, re.S)
    assert figure, 'PB Ranked requires its reviewed login figure'
    html = html[:figure.start()] + html[figure.end():]
    html = html.replace('<!--PB_ENTRY_FIGURE-->', figure[0], 1)
    html = accessible_links(html)
    target = ROOT / 'pokemon-battlegrounds/index.html'
    target.parent.mkdir(exist_ok=True)
    write_html(target, html, encoding='utf-8')
    from pbg_trust import build as build_trust
    build_trust(shell)
    for slug in ('about', 'contact'):
        fp = ROOT / 'pokemon-battlegrounds' / slug / 'index.html'
        fp.write_text(accessible_links(fp.read_text(encoding='utf-8')), encoding='utf-8')
    root_entry()
    privacy()
    # 导航、页脚与登记来自 data/pokemon-battlegrounds-pages.json（02 §2.6、§5.2）
    subprocess.run([sys.executable, str(Path(__file__).resolve().parent / 'register_page.py'), str(ROOT), 'pokemon-battlegrounds'], check=True, stdout=subprocess.DEVNULL)
    register_seo(questions)
    from game_seo import edit as seo_edit  # register_page 追加头部标记后，保持 SEO 编辑器幂等
    for fp in (ROOT / 'pokemon-battlegrounds').rglob('index.html'):
        t0 = fp.read_text(encoding='utf-8')
        n0 = seo_edit(fp, t0)
        if n0 != t0:
            fp.write_text(n0, encoding='utf-8')
    print('Built PB Ranked home and About/Contact; root and privacy links checked.')


def root_entry():
    target = ROOT / 'index.html'
    html = target.read_text(encoding='utf-8')
    if 'id="pokemon-battlegrounds-game-entry"' not in html:
        html = html.replace('<div class="route-grid">', '<div class="route-grid"><a class="route-card" id="pokemon-battlegrounds-game-entry" href="/pokemon-battlegrounds/"><h3>Pokémon Battlegrounds</h3><p>Find PB Ranked at its new address. Check the sign-in requirement, Auto/Manual choices and separate fan-game identities.</p><span class="route-link">Original game &amp; start guide →</span></a>', 1)
        write_html(target, html, encoding='utf-8')


def register_seo(questions):
    """首页 FAQ 登记到 data/game-seo.json（可见问答与 FAQPage 同源），信任页补进 pages_list.txt（只追加）。"""
    f = ROOT / 'data/game-seo.json'
    d = json.loads(f.read_text(encoding='utf-8'))
    d['pages']['pokemon-battlegrounds/index.html'] = {
        'questions': list(questions),
        'faq_review': 'Hub FAQ from data/pokemon-battlegrounds-pages.json (v3.26 F9); visible answers and FAQPage share one source (2026-11-22).',
        'language_review': 'No equivalent language page identified; do not map unrelated topics.',
        'reviewed_candidates': list(questions),
    }
    new = json.dumps(d, ensure_ascii=False, indent=2) + '\n'
    if f.read_text(encoding='utf-8') != new:
        f.write_text(new, encoding='utf-8')
    pl = ROOT / 'pages_list.txt'
    text = open(pl, encoding='utf-8', newline='').read()
    add = ''.join(f'https://megabonk.org{ROUTE}{s}/\r\n' for s in ('about', 'contact') if f'{ROUTE}{s}/' not in text)
    if add:
        with open(pl, 'a', encoding='utf-8', newline='') as out:
            out.write(add)


def privacy():
    """站级隐私页本专区一节：更新为新地址（02 §5.1）；无此节则新增。保持原行尾，不经 write_html 重排。"""
    f = ROOT / 'privacy-policy.html'
    s = open(f, encoding='utf-8', newline='').read()
    section = ('<h2 id="pokemon-battlegrounds">Pokémon Battlegrounds external game links</h2><p>Updated 22 November 2026. Our guide opens pbranked.com in a new tab. The publisher prohibits remote embedding; this guide does not load its game client, handle its sign-in, or provide an account/save service. '
               'Following the link connects you to the original project and any login provider you choose there, under their own policies. Screenshots on this guide are local files. '
               'The guide inherits the site’s existing AdSense and site-wide Umami integrations described above; its About and Contact pages carry no advertising.</p>')
    m = re.search(r'<h2 id="pokemon-battlegrounds">.*?</p>', s, re.S)
    if m:
        new = s[:m.start()] + section + s[m.end():]
    else:
        new = s.replace('</body>', section + '</body>', 1)
    if new != s:
        with open(f, 'w', encoding='utf-8', newline='') as out:
            out.write(new)


if __name__ == '__main__':
    build()
