"""Reviewed Revenant Survivors task pages, checked 12 November 2026; updates 0.6.3 and 0.6.4 applied 17 November 2026.

专区主题（theme.css/hub.css）、首页组件、清单驱动的导航与页脚见 SOP v3.26（sheji，2026-11-22）。"""
import json
import subprocess
import sys
from pathlib import Path
from html import escape
from site_analytics import write_html

ROOT = Path(__file__).resolve().parents[1]
BASE = '/revenant-survivors/'
STORE = 'https://store.steampowered.com/app/4617500/Revenant_Survivors/?l=english'
HUB = 'https://steamcommunity.com/app/4617500'


def link(url, label):
    return f'<a href="{url}" target="_blank" rel="noopener noreferrer">{label} ↗<span class="sr-only"> (opens in a new tab)</span></a>'


def thread(number, label):
    return link('https://steamcommunity.com/app/4617500/discussions/4/' + number + '/', label)


def image(name, alt, caption):
    stem = '/assets/revenant-survivors/' + name
    return f'<figure class="game-image"><a href="{stem}-1920.webp"><img src="{stem}-960.webp" srcset="{stem}-480.webp 480w, {stem}-960.webp 960w, {stem}-1920.webp 1920w" sizes="(max-width:760px) calc(100vw - 48px), 720px" width="1920" height="1080" loading="lazy" alt="{alt}"></a><figcaption>{caption} Mongma Studio Steam promotional screenshot, capture build unspecified.</figcaption></figure>'


PAGES = [
    {
        'slug': 'hard-mode', 'checked': '17 November 2026', 'label': 'Hard Mode', 'title': 'Revenant Survivors Hard Mode: unlocks, Hard 0–10 and rewards',
        'description': 'How Hard Mode unlocks after World 7 since update 0.6.4, how Hard 0–10 progress across worlds, what each level drops and which world to farm for Mythic gear.',
        'answer': 'Since update 0.6.4 (16 November 2026) there are no Tiers: clear Worlds 1–7 in order, and clearing World 7 unlocks Hard 0 in every world. Clearing a Hard level in any world unlocks the next one in all worlds, up to Hard 10. Higher Hard levels drop more rewards and more Mythic gear; at the same level every world has the same difficulty and rewards but drops different gear.',
        'image': 'boss',
        'sections': [
            ('unlock', 'How worlds and Hard levels unlock', '<div class="table-wrap" tabindex="0" role="region" aria-label="World and Hard level unlocks"><table><thead><tr><th scope="col">You clear</th><th scope="col">You unlock</th></tr></thead><tbody><tr><td>World 1–6</td><td>The next world (a random map each time you enter)</td></tr><tr><td>World 7</td><td>Hard 0 in every world</td></tr><tr><td>Hard N in any world</td><td>Hard N+1 in all worlds, up to Hard 10</td></tr></tbody></table></div><p>A notification appears in town when a new Hard level unlocks. Progress from before 0.6.4 was converted automatically: worlds and Hard levels you had already unlocked stay available, and achievements that asked for Tiers now use world progression. '+link(HUB, 'Update 0.6.4 announcement')+'</p>'),
            ('rewards', 'What Hard Mode drops', '<ul><li><strong>Mythic gear</strong>, the rarity above Legendary: final bosses have a higher chance at it, and at high Hard levels a Mythic drop is guaranteed. Magic Find raises the Mythic chance too.</li><li><strong>Mythic Essence</strong> from every Hard Mode enemy, more from final bosses. It is the currency for the Forge’s Mythic options.</li><li><strong>Better rarity odds</strong> at each higher level, and a guaranteed gear drop from every mid-boss.</li><li><strong>More rewards per level</strong>: Hard 10 pays more than Hard 0 at the cost of harder enemies, 8 extra Hard-only curses (such as Elite Discipline and Mini-Boss Raid) and healing orbs that restore less.</li></ul><p>Hard Mode final bosses have less health than before 0.6.4. '+link(HUB, 'Update 0.6.4 announcement')+' · '+link(HUB, 'Major Update 0.6.3 announcement')+'</p>'),
            ('choose', 'Which world to farm', '<ol><li><strong>Still clearing Worlds 1–7?</strong> Push the next world first: World 7 is the only route to Hard Mode, and later worlds already drop better gear.</li><li><strong>Hunting a Mythic set?</strong> Each of Worlds 1–6 drops its own Mythic set with 3-, 6- and 9-piece bonuses; World 7 drops Mythic gear outside the sets. Check the gear-drop preview on stage selection, then farm that world at the highest Hard level you can clear.</li><li><strong>Want the most rewards?</strong> Difficulty and rewards are identical across worlds at the same Hard level, so pick the world whose boss you clear fastest.</li></ol>'),
            ('history', 'Older Hard Mode advice', '<p>Guides written before 16 November describe Tiers and a Hard Mode clear as the gate to World 5. Update 0.6.3 (13 November) expanded Hard Mode to 11 levels, Hard 0 to Hard 10; update 0.6.4 removed Tiers and moved the gate to World 7. Earlier notes about Tier 2–4 boss health from hotfix 0.6.2.1 no longer apply.</p>'),
        ],
        'alt': 'Angel of Obsession boss fight with radial red attack warnings',
        'caption': 'Boss arenas and their attack warnings matter when deciding whether your build can finish a harder run.',
    },
    {
        'slug': 'permanent-progression', 'checked': '17 November 2026', 'label': 'Equipment & progression', 'title': 'Revenant Survivors permanent loot, upgrades and cosmetics',
        'description': 'Separate retained equipment, Forge and skill progression from appearance changes, and check how the launch Supporter Pack changes older cosmetic answers.',
        'answer': 'Equipment carries between runs and can be upgraded, rerolled or dismantled in the Forge. Skill Trees, Soul Engraving and the Armory also provide permanent progression, and since update 0.6.4 Dominions are unlocked through level-up cards during a run. Equipped gear does not change character appearance according to the developer’s October reply. The November launch added a separate cosmetic Supporter Pack.',
        'image': 'forge',
        'sections': [
            ('keep', 'What carries between runs', '<p>A player asked whether loot was permanent and whether it changed appearance. Mongma Studio confirmed retained equipment and the permanent upgrade systems in its October 26 reply. The launch announcement also describes equipment and persistent progression. '+thread('588438959484653157', 'Developer explanation of retained loot')+' · '+link(HUB, 'November 9 launch announcement')+'</p><p>After a run, inspect the equipment you kept and the upgrade panels in town before judging your next attempt by its starting attacks alone. Equipment, character growth and the choices made during combat each affect a different part of preparation.</p>'),
            ('prepare', 'Turn a completed run into your next attempt', '<ol><li>Open your Bag and review retained equipment. Compare the stats relevant to the attacks you actually use.</li><li>Inspect the Forge upgrade preview and its displayed cost before spending materials; dismantle gear you will not use for Souls and Mythic Essence.</li><li>Review the Skill Trees and Soul Engraving panels for available permanent upgrades. Follow the requirements displayed by your installed version.</li><li>Return to stage selection and choose whether your next goal is a clear, equipment drops or a Hard Mode unlock.</li></ol><p>This sequence combines the confirmed persistence rules with the visible town interfaces. It is an editorial preparation checklist. We have not measured an optimal upgrade order or resource-farming rate.</p>'),
            ('mythic', 'Mythic gear, sets and the Forge', '<ul><li><strong>Mythic</strong> is the rarity above Legendary (update 0.6.3): 86 Mythic items bring the total to 196, with 74 Mythic-only options.</li><li><strong>6 Mythic sets</strong> with 3-, 6- and 9-piece bonuses: Wrath of the Forgotten Faith, Ruin of Ashes, Obsession of the Fortress, Frenzy of the Maze, Erosion of the Mire and Malice of the Prison. Each world drops its own set; World 7 drops Mythic gear outside the sets.</li><li><strong>Forge</strong>: Reroll (lock the options you like and reroll the rest), Dismantle (returns Souls, Mythic Essence and every material spent on enhancement) and Move Option. Lock gear to protect it from Dismantle All and Sell All.</li><li><strong>Dominions</strong> now come from unlock cards in Journey of Evolution during a run and are equipped at once (update 0.6.4); Dominator’s Souls spent in the Armory were refunded.</li><li><strong>Armory</strong>: selecting a Specialization equips both its Basic Attack and Strike.</li><li><strong>Past level 10</strong>: attacks, Dominions and passives keep receiving smaller upgrades up to level 30 (see the Overview panel).</li></ul><p>'+link(HUB, 'Major Update 0.6.3 and Update 0.6.4 announcements')+' · Where to farm each set: <a href="/revenant-survivors/hard-mode/#choose">Hard Mode guide</a>.</p>'),
            ('appearance', 'Gear appearance and the Supporter Pack', '<p>The October developer reply says equipment leaves character appearance unchanged and, at that time, there was no cosmetic customization system. The November 9 launch announcement subsequently introduced the Supporter Pack with two skins for each of three characters. It describes those skins as cosmetic with no effect on stats or gameplay progression. '+link(HUB, 'Launch announcement and Supporter Pack explanation')+'</p><p>If you want stronger equipment, spend your attention on gear and the upgrade panels. If you want a different character look, inspect the current skin offering separately. The launch skins do not establish that equipped armor now changes the character model.</p>'),
        ],
        'alt': 'Revenant Survivors Forge showing a weapon enhancement preview beside the Bag',
        'caption': 'The Forge preview and retained equipment inventory help you plan the next run.',
    },
    {
        'slug': 'demo-save-transfer', 'checked': '17 November 2026', 'label': 'Demo save transfer', 'title': 'Revenant Survivors demo save transfer to Early Access',
        'description': 'Move demo progress into Revenant Survivors Early Access, check the first launch on the original PC, then sync the full-game save to another PC.',
        'answer': 'Demo progress can carry into the full game. For the first full-game launch, use the PC that still holds your demo save. Confirm the imported progress, close the game and let Steam Cloud finish syncing before moving to another PC on the same Steam account.',
        'image': 'tree',
        'sections': [
            ('first-launch', 'First launch on the PC with your demo save', '<p>A Steam player asked whether Demo progress would transfer to Early Access. The developer confirmed it on October 26 and supplied the first-launch and Cloud sequence in the November 9 release announcement. '+thread('563671642446948252', 'Developer confirmation of Demo transfer')+' · '+link(HUB, 'Launch instructions for save transfer')+'</p><ol><li>Use the PC where you played the Demo and still have its local save data.</li><li>Launch the full game there for the first time.</li><li>Inspect recognizable progress, such as your unlocked content and permanent-upgrade panels, before continuing.</li><li>Once the transfer looks correct, close the full game normally.</li><li>Wait for Steam Cloud to finish syncing the full-game save.</li></ol>'),
            ('second-pc', 'Continue on another PC', '<p>After the first successful transfer, sign into the same Steam account on the other PC. Enable Steam Cloud on each PC and wait for syncing to finish before starting the full game. This is the sequence specified in the release announcement.</p><p>The first local import and subsequent full-game Cloud synchronization are two consecutive steps. If you already opened the full game elsewhere and the expected progress is missing, return to checking which PC holds the Demo data before attempting further transfers.</p>'),
            ('missing', 'If expected progress is missing', '<ol><li>Check the profile: since update 0.6.3 you can keep up to 3 profiles, each with its own saved progress, so open the one that holds your run history first.</li><li>Record which PC contains the Demo save and where the full game was first launched.</li><li>Check the Steam account and Cloud status on both PCs.</li><li>Capture the full-game progress screen showing the discrepancy and record the installed version.</li><li>Send those details through '+link('https://steamcommunity.com/app/4617500/discussions/', 'the game’s Steam Discussions')+'. The developer requests reports when transfer fails.</li></ol><p>The reviewed instructions do not specify a manual file-copy path, recovery command or cross-store transfer procedure. A failed import therefore needs a report with the launch sequence and account details relevant to the issue. Keep passwords out of public reports. This guide follows the developer’s procedure and has no independent save-transfer test.</p>'),
        ],
        'alt': 'Revenant Survivors character skill tree with unlocked nodes and character statistics',
        'caption': 'Use recognizable permanent progression, such as your skill tree, to check the imported save.',
    },
    {
        'slug': 'controller-auto-attack', 'checked': '17 November 2026', 'label': 'Controller help', 'title': 'Revenant Survivors controller and auto-attack checks',
        'description': 'Check Basic Attack and Strike automation, distinguish old playtest controller reports from the current release, and report unresolved input symptoms.',
        'answer': 'Check the auto-attack mode first. The developer describes separate options for automating Basic Attack plus Strike, or Basic Attack alone with manual Strike. Steam currently lists full controller support. Older playtest reports describe incomplete menus and interactions, so match each report to its version.',
        'image': 'controls',
        'sections': [
            ('mode', 'Check what the selected attack mode automates', '<p>In the difficulty discussion, the developer explains the two auto-attack settings. If Basic Attack happens automatically while Strike still needs input, inspect whether the Basic-only option is selected. '+thread('580554442217253070', 'Developer explanation of auto-attack modes')+'</p><ol><li>Open Settings and inspect the current auto-attack choice.</li><li>Choose whether Strike should also be automated, then follow the current UI’s confirmation prompt.</li><li>Return to combat and observe Basic Attack and Strike separately.</li><li>If neither activates as expected, record the controller model, mode and exact behavior for a report.</li></ol>'),
            ('versions', 'Separate historical problems from the release listing', '<p>The August controller thread contains reports of movement working while menus, skill choices and interactions were incomplete. The developer acknowledged those limitations on August 18. Later playtest updates addressed controller support and portal input, while the September 4 discussion identified another Demo input issue after Steam Input was introduced. '+thread('591811524772889552', 'Historical controller discussion')+' · '+thread('580554442217253070', 'Demo input follow-up')+'</p><p>The current '+link(STORE, 'Steam store listing')+' advertises Full Controller Support. That listing and the older reports have different dates and scopes. Use the installed release’s behavior to decide what still needs reporting.</p>'),
            ('update-063', 'Controller changes in update 0.6.3', '<ul><li>Better controller navigation in gear menus and the Forge.</li><li>R3 sorts storage; B now closes only the Bag item menu.</li><li>Interaction choices map to number keys 1–4 on keyboard, with matching number icons.</li></ul><p>If a menu still cannot be reached with your controller after 0.6.3, report it with the steps below. '+link(HUB, 'Major Update 0.6.3 announcement')+'</p>'),
            ('report', 'Describe the input that fails', '<p>A useful report distinguishes movement, aiming, Basic Attack, Strike, menu navigation, level-up selection and portal interaction. Include the game edition, version, controller model, connection type and Steam Input state. These details let the developer reproduce a narrower failure than “controller broken.”</p><p>One playtest participant reported enabling auto attack through the mouse’s middle button before returning to the controller. That is an old player-reported workaround with no current-release verification here. Treat it only as historical context. This guide has no device-specific controller test or Steam Deck performance measurement.</p>'),
        ],
        'alt': 'Revenant Survivors level-up choice screen with three cards and an Auto-Attack On indicator',
        'caption': 'Combat automation and selecting a level-up card are separate inputs to check when reporting controller behavior.',
    },
    {
        'slug': 'stuck-after-run', 'label': 'Stuck after a run', 'title': 'Revenant Survivors stuck after a run — reported fixes',
        'description': 'Match results-screen freezes and return-to-town crashes to the launch skin-DLC fix, the 0.6.2 hotfix recap and the older Bloodstained Fang Demo crash.',
        'answer': 'Update the affected game edition, then check where the transition stops. The developer reported a launch skin-DLC scene-loading fix and later listed a fix for loading stuck while returning to the village. A separate Demo crash tied to Bloodstained Fang was fixed in Demo 0.3.1.',
        'image': 'battle',
        'sections': [
            ('match', 'Match the symptom to a reported fix', '<div class="table-wrap" tabindex="0" role="region" aria-label="Reported transition fixes"><table><thead><tr><th>Symptom and scope</th><th>Source finding</th><th>Next check</th></tr></thead><tbody><tr><td>Launch version freezes during scene changes</td><td>The developer linked a November 9 report to skin-DLC loading and said a patch shipped about one hour after launch.</td><td>Update the full game and retry the transition.</td></tr><tr><td>Loading stuck when returning to the village</td><td>The November 10 update 0.6.2 recap lists this as fixed in an earlier post-launch hotfix.</td><td>Confirm the installed full-game build, then identify whether the same step still fails.</td></tr><tr><td>Older Demo crashes around results/camp transitions</td><td>The developer identified Bloodstained Fang and reported a fix in Demo 0.3.1. The reporting player later described four runs without the issue.</td><td>Check the Demo version and Relic, and include them in any recurring-crash report.</td></tr></tbody></table></div><p>'+thread('565924824838457776', 'Launch freeze report and developer reply in Chinese')+' · '+link(HUB, '0.6.2 post-launch fix recap')+' · '+thread('565923773630716133', 'Bloodstained Fang Demo investigation')+'</p>'),
            ('retry', 'Check the affected transition again', '<ol><li>Identify whether you launched the Demo or full game and note its version.</li><li>Let Steam finish updating that edition.</li><li>When you next reach the affected transition, note whether the stop happens before results, between results and camp, or while loading the village.</li><li>Record whether the behavior is a frozen screen, continued loading or an application crash. Capture any error text.</li></ol><p>The reports above concern distinct loading and crash issues. They support these version checks, while their fixes cannot guarantee that every transition problem shares the same cause.</p>'),
            ('persist', 'If the updated build still fails', '<p>Reply in the relevant '+link('https://steamcommunity.com/app/4617500/discussions/', 'Steam discussion')+' with the version, transition, character, equipped Relics, skin/DLC state and repeatability. Include the exact error or a screenshot when available. The Demo investigation became actionable when the developer identified a specific Relic.</p><p>We have not reproduced these crashes. The reviewed sources provide the reported fixes and one player’s follow-up after the Demo fix. They provide no universal save-recovery procedure for a current crash. For missing progress after switching from Demo to the full game, follow the separate save-transfer sequence.</p>'),
        ],
        'alt': 'Revenant Survivors boss arena showing the Mother of Curse Margana fight',
        'caption': 'Record whether the failure happens after boss combat, on the results screen or while returning to town.',
    },
]


def button(url, label, secondary):
    cls = 'button secondary' if secondary else 'button'
    return f'<a class="{cls}" href="{url}" target="_blank" rel="noopener noreferrer">{label} ↗<span class="sr-only"> (opens in a new tab)</span></a>'


HOME = {
    'slug': '', 'label': 'Overview',
    'title': 'Revenant Survivors guide — start, progression and help',
    'description': 'Choose where to start in Revenant Survivors, move a Demo save into Early Access, plan retained upgrades and find version-specific help.',
    'image': 'boss', 'alt': 'Revenant Survivors Angel of Obsession boss arena with red ground attack warnings',
    'caption': 'Revenant Survivors combines horde combat with boss encounters and persistent character growth.',
}

START = (
    '<p>Revenant Survivors is Mongma Studio’s single-player dark-fantasy horde-survival roguelite. It entered Steam Early Access on November 9, 2026. '
    'The full game and free Demo have separate Steam listings. Use the listing for your intended edition.</p>'
    '<ul><li><strong>Trying the game.</strong> Start with the Demo listing and check its current requirements before installing.</li>'
    '<li><strong>Returning from the Demo.</strong> Open the full game first on the PC with your Demo save, inspect the imported progress, close the game and finish Steam Cloud syncing. '
    'Follow the <a href="/revenant-survivors/demo-save-transfer/">save-transfer steps</a> before continuing on another PC.</li>'
    '<li><strong>Preparing another run.</strong> Review the equipment you kept, Forge options and permanent upgrades. '
    'The <a href="/revenant-survivors/permanent-progression/">progression guide</a> explains how equipment, upgrades and appearance relate.</li></ul>'
    '<p class="rv-start-links">' + button('https://store.steampowered.com/app/4693240/', 'Free Demo on Steam', False) + button(STORE, 'Full game on Steam', True) + '</p>'
)

VERSIONS = (
    '<p>The latest official update checked on 17 November is full-game update <strong>0.6.4</strong> (16 November 2026), which removed Tiers and made World 7 the gate to Hard Mode. '
    'Demo and playtest reports use their own version numbers. Match the edition and symptom before applying an older workaround. '
    + link(HUB, 'Official Steam announcements') + '</p>'
    '<p>These independent guides review developer announcements and public player discussions. The linked articles identify the evidence and version limits for their specific answers. '
    'The gameplay images are developer promotional screenshots with unspecified capture builds.</p>'
)


def manifest():
    m = json.loads((ROOT / 'data/revenant-survivors-pages.json').read_text(encoding='utf8'))
    m['by'] = {p['slug']: p for p in m['pages']}
    return m


def hub(m):
    from hub_components import Hub
    # 缩略图直接放在 /assets/revenant-survivors/{名}-480.webp，thumb_dir 为空
    return Hub(m, BASE, 'rv', '/assets/revenant-survivors', thumb_dir='')


def homepage():
    m = manifest()
    h = hub(m)
    bg = ''
    pv = m['preview']
    rows = [(a, b) for a, b in pv['rows']]
    figure = image(HOME['image'], HOME['alt'], HOME['caption'])
    hero = h.hero(
        kicker='Independent player guides · Mongma Studio’s survivorslike', title='Revenant Survivors ', sub='guide — start, progression and help',
        deck='Claim a boss’s power, then prepare the next run: move a Demo save into Early Access, plan the gear you keep and check what Hard Mode drops.',
        status=['Steam · Single-player', 'Early Access', 'Update 0.6.4 · 17 Nov 2026', 'Unofficial fan guide'],
        actions=[('Pick a guide ↓', '#guides', False), ('Get the game', '#start', True)], bg_attr=bg)
    cards = h.cards(heading='Pick the job you have right now', bg_attr=bg)
    cheat = h.cheat(pv['title'], pv['intro'], rows, bg_attr=bg)
    start = (f'<section class="rv-band rv-start" id="start"><div class="rv-start-grid"><div><h2>Choose your starting point</h2>{START}</div>'
             f'<div>{figure}<div class="rv-start-note"><h3>Returning from the Demo</h3><p>Launch the full game first on the PC with your Demo save. '
             f'Check your imported progress, close the game and finish Steam Cloud syncing before changing computers.</p>'
             f'<a href="{BASE}demo-save-transfer/">Follow the transfer steps →</a></div></div></div></section>')
    versions = f'<section class="rv-band" id="versions"><h2>Check your edition before applying a fix</h2>{VERSIONS}</section>'
    body = hero + cards + cheat + start + h.updates(bg_attr=bg) + h.groups(bg_attr=bg) + versions + h.faq(bg_attr=bg)
    return f'<main class="wrap" id="main">{body}</main>', h.faq_questions()


def shell(route, page, body_cls, extra_css, main, og_type='article'):
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(page['title'])}</title><meta name="description" content="{escape(page['description'], quote=True)}"><link rel="canonical" href="https://megabonk.org{route}"><meta property="og:title" content="{escape(page['title'])}"><meta property="og:description" content="{escape(page['description'], quote=True)}"><meta property="og:type" content="{og_type}"><meta property="og:url" content="https://megabonk.org{route}"><meta property="og:image" content="https://megabonk.org/assets/revenant-survivors/{page.get('image', 'boss')}-1920.webp"><link rel="icon" href="/assets/revenant-survivors/favicon.ico"><link rel="icon" type="image/svg+xml" href="/assets/revenant-survivors/favicon.svg"><link rel="apple-touch-icon" href="/assets/revenant-survivors/icon-180.png"><link rel="stylesheet" href="/assets/guide-article-layout.css"><link rel="stylesheet" href="/assets/revenant-survivors/theme.css">{extra_css}</head><body class="guide-layout rv-theme {body_cls}"><a class="skip" href="#main">Skip to content</a><header class="top"><div class="wrap"><a class="brand" href="{BASE}"><img src="/assets/revenant-survivors/logo.svg" width="36" height="36" alt="">Revenant Survivors</a><nav class="desktop-nav" aria-label="Revenant Survivors tasks"></nav><details class="mobile-nav"><summary>Menu</summary><nav class="mobile-links" aria-label="Revenant Survivors tasks"></nav></details></div></header>{main}<footer class="footer"></footer></body></html>'''


def ads(html):
    """普通内容页保留站点既有 AdSense 加载器；信任页不放。"""
    tag = '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8830315294299920" crossorigin="anonymous"></script>'
    return html.replace('</head>', tag + '</head>', 1)


def build():
    questions = {}
    for page in [HOME] + PAGES:
        route = BASE + (page['slug'] + '/' if page['slug'] else '')
        if page is HOME:
            main, questions = homepage()
            html = shell(route, page, 'rv-hub', '<link rel="stylesheet" href="/assets/revenant-survivors/hub.css">', main, 'website')
        else:
            toc = ''.join(f'<a href="#{key}">{title}</a>' for key, title, _ in page['sections'])
            body = image(page['image'], page['alt'], page['caption'])
            body += ''.join(f'<section id="{key}"><h2>{title}</h2>{text}</section>' for key, title, text in page['sections'])
            main = (f'<main class="wrap" id="main"><header class="article-head" id="guide"><p class="eyebrow">Revenant Survivors · Independent guides</p><h1>{escape(page["title"])}</h1>'
                    f'<p class="answer">{page["answer"]}</p><p class="byline">Megabonk.org editors · Checked {page.get("checked", "12 November 2026")} · Early Access</p></header>'
                    f'<div class="article-layout"><nav class="toc" aria-label="On this page">{toc}</nav><article class="prose">{body}'
                    f'<p><a href="#guide">Back to top</a></p></article></div></main>')
            html = shell(route, page, 'rv-guide', '', main)
        html = ads(html)
        target = ROOT / route.strip('/') / 'index.html'
        target.parent.mkdir(parents=True, exist_ok=True)
        write_html(target, html, encoding='utf8')
    from revenant_trust import build as build_trust
    build_trust(shell)
    privacy()
    # 导航、面包屑、相关任务、页脚与登记来自 data/revenant-survivors-pages.json（02 §2.6、§5.2）
    subprocess.run([sys.executable, str(Path(__file__).resolve().parent / 'register_page.py'), str(ROOT), 'revenant-survivors'], check=True, stdout=subprocess.DEVNULL)
    register_seo(questions)
    from game_seo import edit as seo_edit  # register_page 追加头部标记后，保持 SEO 编辑器幂等
    for fp in (ROOT / 'revenant-survivors').rglob('index.html'):
        t0 = fp.read_text(encoding='utf8')
        n0 = seo_edit(fp, t0)
        if n0 != t0:
            fp.write_text(n0, encoding='utf8')
    print('Built Revenant Survivors home, 5 task pages and About/Contact')


def register_seo(questions):
    """首页 FAQ 登记到 data/game-seo.json（可见问答与 FAQPage 同源），信任页补进 pages_list.txt（只追加）。"""
    f = ROOT / 'data/game-seo.json'
    d = json.loads(f.read_text(encoding='utf8'))
    d['pages']['revenant-survivors/index.html'] = {
        'questions': list(questions),
        'faq_review': 'Hub FAQ from data/revenant-survivors-pages.json (v3.26 F9); visible answers and FAQPage share one source (2026-11-22).',
        'language_review': 'No equivalent language page identified; do not map unrelated topics.',
        'reviewed_candidates': list(questions),
    }
    new = json.dumps(d, ensure_ascii=False, indent=2) + '\n'
    if f.read_text(encoding='utf8') != new:
        f.write_text(new, encoding='utf8')
    pl = ROOT / 'pages_list.txt'
    text = open(pl, encoding='utf8', newline='').read()
    add = ''.join(f'https://megabonk.org{BASE}{s}/\r\n' for s in ('about', 'contact') if f'{BASE}{s}/' not in text)
    if add:
        with open(pl, 'a', encoding='utf8', newline='') as out:
            out.write(add)


def privacy():
    """站级隐私页为本专区保留一节（02 §5.1），已有则不重复。"""
    f = ROOT / 'privacy-policy.html'
    s = open(f, encoding='utf8', newline='').read()
    if 'id="revenant-survivors"' in s:
        return
    section = ('<h2 id="revenant-survivors">Revenant Survivors guides</h2><p>Reviewed 22 November 2026. These pages host no game client, account or save and embed no third-party game window. '
               'Steam, Steam Community and developer links open the destination site in a new tab only when you click them, and that site then applies its own privacy practices. '
               'Ordinary guide pages inherit this site’s existing AdSense loader and site-wide Umami analytics described here; About and Contact carry no advertising. '
               'Cloudflare hosting and possible performance measurement are described above.</p>')
    marker = '<h2 id="midgard-survivors">'
    if marker not in s:
        raise SystemExit('privacy-policy.html: marker section not found')
    with open(f, 'w', encoding='utf8', newline='') as out:  # 保持原 CRLF，不经 write_html 重排
        out.write(s.replace(marker, section + marker, 1))


if __name__ == '__main__':
    build()
