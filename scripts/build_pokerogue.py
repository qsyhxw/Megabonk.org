"""PokeRogue original-host play hub and researched decision guides. 专区主题/页面清单/页脚见 SOP v3.26（sheji，2026-11-22）。"""
from pathlib import Path
from html import escape
import json
import subprocess,sys
from site_analytics import write_html
ROOT=Path(__file__).resolve().parents[1]
BASE='/pokerogue/'
SOURCE='https://github.com/pagefaultgames/pokerogue/blob/v1.12.2.4/src/data/mystery-encounters/encounters/'
def link(url,label):return f'<a href="{url}" target="_blank" rel="noopener noreferrer">{label} ↗<span class="sr-only"> (opens in a new tab)</span></a>'
def section(id,title,body):return f'<section id="{id}"><h2>{title}</h2>{body}</section>'
def table(head,rows):return '<div class="table-wrap" tabindex="0" role="region" aria-label="Decision comparison"><table><thead><tr>'+''.join('<th>'+x+'</th>' for x in head)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+x+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table></div>'
HEAD_CSS = '<link rel="icon" href="/assets/pokerogue/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/assets/guide-article-layout.css"><link rel="stylesheet" href="/assets/pokerogue/theme.css?v=20261122b">'
AD = '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8830315294299920" crossorigin="anonymous"></script>'
SHELL_TOP = '<a class="skip" href="#main">Skip to content</a><header class="top"><div class="wrap"><a class="brand" href="/pokerogue/"><img src="/assets/pokerogue/logo.svg" width="36" height="36" alt="">PokeRogue</a><nav class="desktop-nav" aria-label="PokeRogue tasks"></nav><details class="mobile-nav"><summary>Menu</summary><nav class="mobile-links" aria-label="PokeRogue tasks"></nav></details></div></header>'


def shell(route, page, body_cls, extra_css, main, og_type='article'):
    """分页/首页/信任页共用外壳；导航与页脚由 register_page.py 最后填充。"""
    t = escape(page['title']); d = escape(page['description'], quote=True)
    img = page.get('image', 'original-menu.png')
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{t}</title>'
            f'<meta name="description" content="{d}"><link rel="canonical" href="https://megabonk.org{route}"><meta property="og:title" content="{t}">'
            f'<meta property="og:description" content="{d}"><meta property="og:type" content="{og_type}"><meta property="og:url" content="https://megabonk.org{route}">'
            f'<meta property="og:image" content="https://megabonk.org/assets/pokerogue/{img}">{HEAD_CSS}{extra_css}</head>'
            f'<body class="guide-layout pr-theme {body_cls}">{SHELL_TOP}{main}<footer class="footer"></footer></body></html>')


def render(slug, title, desc, h1, lead, parts, img, alt, caption, *, size=None, checked="6 November 2026"):
    toc = ''.join(f'<a href="#{i}">{t}</a>' for i, t, b in parts)
    body = ''.join(section(*p) for p in parts)
    w, h = (1280, 720) if slug == 'mobile' else (419, 261) if slug == 'trash-to-treasure' else (44, 74)
    w, h = size or (w, h)
    credit = f'<figcaption>{caption}</figcaption>' if caption else ''
    fig = f'<figure class="game-image"><img src="/assets/pokerogue/{img}" alt="{alt}" width="{w}" height="{h}" loading="eager">{credit}</figure>'
    main = (f'<main class="wrap" id="main"><header class="article-head" id="guide"><p class="eyebrow">PokéRogue · Independent guide</p><h1>{h1}</h1>'
            f'<p class="answer">{lead}</p><p class="byline">Megabonk.org editors · Checked {checked} · Source-based guidance, no full run tested</p></header>'
            f'<div class="article-layout"><nav class="toc" aria-label="On this page">{toc}</nav><article class="prose">{fig}{body}<p><a href="#guide">Back to top</a></p></article></div></main>')
    return shell(BASE + slug + '/', {'title': title, 'description': desc, 'image': img}, 'pr-guide', '', main)

RELEASE = 'https://github.com/pagefaultgames/pokerogue/blob/v1.12.2.8/src/'

def eternatus():
    parts = [
        ('waves', 'Plan the last twenty waves',
         '<p>The Elite Four fight on 182, 184, 186 and 188. Their Champion follows on 190. Once you identify the first member, use that region to narrow down the remaining opponents. Heal before the next trainer if a key teammate is down.</p>'
         '<p>Save a healthy answer for the rival’s Rayquaza on 195. It belongs to a trainer, so reserve your balls for wild encounters. At 200 the opponent changes to Eternatus.</p>'),
        ('catch', 'Check whether a ball can work', table(['What you see', 'What to do'], [
            ('Other starters still locked', 'Play to defeat Eternatus. Even a Master Ball cannot bypass the starter requirement. Check your starter selection for missing species, including egg exclusives.'),
            ('Every other starter unlocked, ordinary Classic', 'A Master Ball can skip the shield check. For other balls, reach the final HP segment of the second form first. Leave it alive for the throw.'),
            ('An active challenge', 'A Master Ball does not skip the final boss shield check. Full Fresh Start blocks this capture entirely.'),
            ('Paradox Pokémon in the End before wave 200', 'In ordinary Classic you must already have that species registered as caught or hatched. Hatch the missing species first. If two opponents are on the field, reduce the battle to one target.'),
            ('Endless Eternatus or a trainer’s Pokémon', 'Keep your ball. These encounters block capture regardless of its strength.')])),
        ('fight', 'Prepare for the change to Eternamax',
         '<p>When the first form reaches its final shield it transforms and refills its health. Bring a second battle-ready Pokémon for the double battle. Save your status move for after the transformation or plan to reapply it. Earlier stat changes carry over, but effects such as Leech Seed are cleared.</p>'
         '<p>A Steel-type can cover poison attacks but still needs an answer to Flamethrower. A Fairy-type covers dragon attacks but risks Cross Poison. Keep a switch available instead of spending every healing item on a single immunity.</p>'),
        ('rules', 'Battle rules', '<p>'+link(RELEASE+'phases/command-phase.ts','Game release v1.12.2.8: ball eligibility')+' covers mode, starter and shield checks. The '+link('https://wiki.pokerogue.net/gameplay:modes:classic','Classic battle schedule')+' describes the phases and moves.</p>')]
    return render('eternatus', 'PokeRogue Eternatus: Wave 200 Fight and Catch Requirements', 'Prepare for the Elite Four, rival Rayquaza and Eternatus. Check your mode, starters and boss shields before using a ball.', 'How to fight and catch Eternatus in PokeRogue', '<strong>At wave 200 of ordinary Classic, fight for the clear unless every other starter is unlocked.</strong> Your starter collection determines whether a capture is possible.', parts, '890.png', 'Eternatus in its first form', '', size=(97,66), checked='25 November 2026')

def gimmighoul():
    parts = [
        ('count', 'Count the rewards you picked', table(['Reward', 'Evolution points'], [
            ('Nugget', '1'), ('Big Nugget', '2'), ('Relic Gold', '3'), ('Golden Punch on Gimmighoul', '1'), ('Amulet Coin', '1'), ('Golden Poké Ball', '1')]) +
         '<p>Two Relic Gold rewards and two Big Nuggets give 3 + 3 + 2 + 2 = 10. One of each gives five points. Cash earned from winning a battle does not turn into points just because your wallet grows.</p>'),
        ('check', 'If it still has not evolved', '<ol><li>Check when Gimmighoul joined. Nuggets collected before it entered your party did not add to its tracker.</li><li>Check the holder of Golden Punch. A teammate earning money with it does not give Gimmighoul that held-item point.</li><li>Read the number on the evolution tracker when available. It combines treasure reward progress and eligible persistent items. Let Gimmighoul gain a level after reaching ten.</li></ol>'),
        ('sources', 'Evolution rules', '<p>The '+link('https://wiki.pokerogue.net/pokedex:1000','Gholdengo evolution entry')+' lists values for both Chest and Roaming forms. The '+link(RELEASE+'modifier/modifier.ts','game’s treasure tracker')+' updates the Pokémon present when a money reward is collected.</p>')]
    return render('gimmighoul', 'PokeRogue Gimmighoul Evolution: Count 10 Treasure Points', 'Calculate which rewards count toward Gholdengo, check the tracker and level up Gimmighoul after reaching ten points.', 'How to evolve Gimmighoul into Gholdengo', '<strong>Keep Gimmighoul in your party while collecting treasure, reach ten points, then level it up.</strong> Track the reward items themselves. You can spend your shop money normally.', parts, '999.png', 'Chest Form Gimmighoul', '', size=(39,53), checked='25 November 2026')

def dark():
 parts=[('choose','Choose by what this run can afford to lose',table(['Your situation','Recommendation','Reason'],[
 ('You depend on one carry or a hard-to-replace support','Refuse if losing that member would end your plan.','You do not choose the donor. Keeping a weak bench member does not guarantee that it will be selected.'),
 ('Your goal is collecting starters and the remaining team can handle a boss','Consider accepting.','You gain a catch opportunity, but must handle the encounter with one fewer original team member.'),
 ('You mainly want five Rogue Balls','Do not treat this as a free ball pickup.','The team change happens before the fight. The balls are payment for a real risk.'),
 ('You have fainted party members','Do not assume they are protected or guaranteed donors.','The release code permits fainted members in the random selection, while protecting the last battle-able member.')])+'<p>Each Rogue Ball has a 3× catch multiplier against an eligible target, compared with 2× for an Ultra Ball. See the <a href="/pokerogue/eternatus/#catch">boss capture checklist</a>.</p><p>These recommendations are a way to weigh the documented costs, not a claim that one choice wins more runs. Before accepting, identify the jobs your team needs for the next boss: damage, survival, status control or catching. If losing any one of those jobs breaks the plan, refusing preserves the team you already built.</p>'),
 ('sequence','What accepting actually does','<ol><li>A random party member is removed. This is not a screen where you nominate a sacrifice.</li><li>You receive five Rogue Balls and a new boss encounter is generated.</li><li>The removed member’s non-form-changing held items are carried into the opponent configuration. A well-equipped donor can therefore leave you facing an equipped opponent.</li><li>Fight and attempt to catch the new Pokémon if that is your goal. A catchable encounter is not a guaranteed catch or a free replacement already added to your party.</li></ol><p>Do not plan on getting the original member back by refusing the battle afterward. Refusing the initial offer is the choice that leaves your team intact, with no reward or encounter EXP.</p>'),
 ('pool','Read the odds as cost bands, not catch chances','<p>The checked release rolls <strong>35% for cost 6, 50% for cost 7, 10% for cost 8 and 5% for cost 9–10</strong>. Those are selection bands in the source, not the probability of catching the result or a guarantee of a particular species.</p><p>The selection tries to match the removed member’s typing. A Mono-Type Challenge supplies its required type instead. If the requested combination has no eligible result, the selection helper can fall back; do not promise yourself one legendary from a type alone. The exclusion list includes Mythicals, Ultra Beasts, Paradox Pokémon, Eternatus and certain special forms.</p><p>Older articles list different percentages, and the Wiki summarizes the highest band as 9. This guide uses the explicit 9–10 band in release v1.12.2.4. Offline copies on older game files may differ.</p>'),
 ('availability','When the encounter is eligible','<p>Dark Deal starts at wave 30 within the Mystery Encounter window ending at 180, requires at least two party members, and is disabled for Hardcore and Mono-Generation Challenges in the checked release. Eligibility does not mean it must appear. Mystery Encounters belong to Classic and Challenge runs, not Daily or Endless.</p>'),
 ('sources','Sources and version','<p>Rules checked against '+link(SOURCE+'dark-deal-encounter.ts','Pagefault Games · release v1.12.2.4 encounter code')+' and the '+link('https://wiki.pokerogue.net/gameplay:mysteryencounters#dark_deal','PokéRogue Wiki · Dark Deal')+'. Code inspection supports the sequence and restrictions; we did not reproduce this encounter in a live run. Recheck after an encounter or balance update.</p>')]
 return render('dark-deal','PokeRogue Dark Deal: Accept or Refuse?','Decide whether to accept PokeRogue’s Dark Deal: random party loss, held items, boss capture and current cost bands explained before you commit.','PokeRogue Dark Deal: accept or refuse?','<strong>Refuse if your run cannot survive losing an essential team member.</strong> Accepting removes a randomly selected Pokémon and opens a catchable boss fight. You get five Rogue Balls, not a guaranteed safe upgrade.',parts,'dark_deal_scientist.png','The scientist sprite used by PokeRogue’s Dark Deal encounter','Original encounter sprite from the assets revision linked to v1.12.2.4; identification art, not a playthrough screenshot.')

def trash():
 parts=[('choice','Compare the two costs',table(['Choice','Immediate result','Cost to your run'],[
 ('Dig for Valuables','One Leftovers and one Shell Bell, subject to item application limits.','Black Sludge raises shop item and reroll costs to 2.5 times their normal price for the rest of the run.'),
 ('Investigate Further','A boss battle against Gigantamax Garbodor.','The fight starts with Toxic and Stockpile effects, and the boss has an extra health segment. You must survive before choosing a reward.')])+'<p><strong>Favor investigating when your team can handle the battle and still needs its money for later healing or rerolls.</strong> Favor digging only when avoiding that immediate fight is worth the permanent price penalty and the healing items materially help your plan. A damaged team can make the battle dangerous; a cash-poor team can make the penalty dangerous. Neither option is universally free value.</p>'),
 ('budget','Estimate the price penalty before digging','<p>Use the prices currently shown in your run as a baseline. A future purchase that would cost 1,000 would cost about 2,500 under a 2.5× multiplier: 1,500 extra. For a planned set of purchases with normal total cost B, the extra burden is about 1.5 × B, before other price modifiers or rounding.</p><p>This is an arithmetic example, not a measured shop price. Apply it to your likely remaining healing and rerolls, rather than assuming that an Amulet Coin or Golden Punch automatically cancels the penalty. Those items do not make every possible future purchase affordable.</p><p>The penalty lasts for the remaining run. Do not take the healing items expecting a biome change to reset shop prices. Leftovers stacks up to four on one holder. Each copy restores about one sixteenth of its maximum HP at turn end while injured. If your intended holder already has four, another copy brings it no additional healing. Also check who can receive the items: the release code checks held-item limits, so a full stack should not be treated as another guaranteed useful copy.</p>'),
 ('battle','Prepare for Garbodor’s opening','<p>Investigating reveals Gigantamax Garbodor. In the checked release it opens with <strong>Toxic against your side and Stockpile on itself</strong> before normal move choices. Its move set is Gunk Shot, Stomping Tantrum, Hammer Arm and Payback; it has one additional boss health segment.</p><p>Before choosing, consider whether your available team can take that opening and finish a shielded fight. Do not judge the route only by Poison typing: its listed attacks also cover Ground, Fighting and Dark. This is a readiness check, not a guaranteed counter build or an assertion that every opening move always lands.</p><p>After victory, the reward selection includes Leftovers plus Rogue-, Ultra- and Great-tier options. <strong>These are choices on a reward screen, not four items automatically awarded together.</strong> The fight route therefore does not promise the same immediate Shell Bell as digging.</p>'),
 ('recognize','Recognize this encounter and its limits','<p>Trash to Treasure is eligible from wave 100 within the Mystery Encounter window ending at 180, needs at least three party members and appears at most once per run. The checked code exposes investigation and digging; it does not offer a standard free “leave” option. Do not confuse Black Sludge’s encounter penalty with an ordinary held-item recommendation from another Pokémon game.</p><p>The picture above is the original Garbodor animation sheet used by the game. It identifies the encounter’s Pokémon; it is not evidence of a current battle result or a screenshot of the reward choices.</p>'),
 ('sources','Sources and version','<p>Checked against '+link(SOURCE+'trash-to-treasure-encounter.ts','Pagefault Games · v1.12.2.4 encounter code')+' and '+link('https://wiki.pokerogue.net/gameplay:mysteryencounters#trash_to_treasure','PokéRogue Wiki · Trash to Treasure')+'. The budget comparison is our arithmetic applied to the documented multiplier; neither battle success nor a full run was tested here. Older reward descriptions can differ, so compare your offline version before relying on them.</p>')]
 return render('trash-to-treasure','PokeRogue Trash to Treasure: Dig or Investigate?','Compare PokeRogue Trash to Treasure choices: healing items with a lasting shop penalty, or a Garbodor fight with reward options. Plan the trade-off.','Trash to Treasure: dig or investigate?','<strong>Digging avoids the fight but makes shop items and rerolls cost 2.5× for the rest of the run.</strong> Investigating risks a Garbodor boss battle and lets you choose a reward afterward. Decide which cost your current team can afford.',parts,'569-gigantamax.png','Original PokeRogue Gigantamax Garbodor animation sheet, showing the encounter Pokémon','Original game animation sheet, linked assets revision for v1.12.2.4. Game artwork remains with its respective owners.')

def mobile():
 parts=[('version','Choose the version before installing anything',table(['Route','Use it for','Keep in mind'],[
 ('pokerogue.net in your browser','Starting with the original online game.','The inspected client opens a login/account screen; this site does not provide an account or host your run.'),
 ('Home-screen web app or shortcut','Opening that same site with less browser chrome.','Adding a shortcut does not create an offline copy of the game or remove its account requirements.'),
 ('Admiral Billy’s community app','A separate wrapper with an offline mode option.','It is a community project. Desktop and Android packages differ; follow its own release instructions rather than a random download mirror.')])+'<p>Start with the browser route unless you specifically need the community wrapper’s features. This keeps the choice clear: changing how a site opens is different from changing which game files and save system you use.</p>'),
 ('open','Open the original game','<p>'+link('https://pokerogue.net/','Open PokéRogue on pokerogue.net')+'</p><ol><li>Check the address is <strong>pokerogue.net</strong>. A matching name alone is not enough: one .app search result inspected in this research offers a collection of different mini-games.</li><li>Let the initial game files load, then read the login or account choices. Returning players should use their existing game account rather than treating another fan game’s account as interchangeable.</li><li>If you only want a home-screen entry, use your browser’s installation or add-to-home-screen feature. The exact label depends on the browser and OS.</li></ol><p>The captured screen above is from the original client, with its language set to Chinese. It identifies the account step; we did not sign in, create an account or test a complete run.</p>'),
 ('shortcut','Add a home-screen entry','<p>The community’s mobile guide documents these routes:</p><ul><li><strong>Android / Chrome:</strong> open the original site, then look in the browser’s three-dot menu for <strong>Install app</strong> or <strong>Add to Home screen</strong>.</li><li><strong>iPhone / Safari:</strong> open the site, use the browser’s share controls and choose <strong>Add to Home Screen</strong>.</li></ul><p>If the wording or option is missing, continue in the browser while checking that browser’s current help. An absent installation prompt is not a reason to download an unrelated APK. A home-screen launch also does not establish that offline play or crash-free performance is supported.</p><p>In-game navigation uses directional controls and a confirm/cancel action rather than assuming every element works like a normal webpage. Consult the '+link('https://wiki.pokerogue.net/gameplay:controls','PokéRogue Wiki controls')+' for the current mappings. Physical-phone controls and installation were not tested in this check.</p>'),
 ('offline','Keep offline progress separate','<p>The community wrapper’s author documents downloading game files and switching to offline mode. Its desktop README links a separate Android project. Those instructions are not evidence of an official iOS app, and the desktop menu sequence should not be presented as an Android walkthrough.</p><p>The Wiki’s community-tools page says data can transfer <strong>from online to offline, but not back from offline to online</strong>. Treat an offline run as a separate commitment. Before changing versions, read the wrapper’s current instructions and keep a backup through the supported export process; do not erase browser data as a general repair step.</p><p>If something fails, first record whether you are using the original browser site, a home-screen shortcut or the community app, along with the device and failure stage. A login problem, a failed offline-file download and a crash after battles are different issues. This page does not claim one universal fix.</p>'),
 ('sources','Sources and checks','<p>Checked 6 November 2026: original client reached its account screen in desktop Chrome. Sources: '+link('https://www.reddit.com/r/pokerogue/comments/1c7sqaf/guide_to_the_best_mobile_experience_for_pok%C3%A9rogue/','community mobile guide')+' for home-screen steps; '+link('https://wiki.pokerogue.net/community:tools','Wiki community tools')+' for wrapper identity and transfer direction; '+link('https://github.com/Admiral-Billy/Pokerogue-App','wrapper author’s desktop README')+' and '+link('https://github.com/Admiral-Billy/PokeRogue-App-Android','Android repository')+' for project boundaries. No app package was installed and no physical phone or account synchronization was tested.</p>')]
 return render('mobile','PokeRogue Mobile: Browser, Home Screen or App?','Choose the original PokeRogue mobile browser game, a home-screen shortcut or a community app. Check account and offline-save boundaries before switching.','PokeRogue on mobile: choose the right version','<strong>Start at pokerogue.net in your browser.</strong> A home-screen shortcut opens the web game; Admiral Billy’s offline-capable app is a separate community wrapper. Choose the route before following installation or save-transfer advice.',parts,'original-menu.png','PokeRogue original client account screen in Chinese, with username, password and external sign-in choices','Original-site account screen captured 6 November 2026; interface inspection only, not a mobile gameplay test.')


def manifest():
    m = json.loads((ROOT / 'data/pokerogue-pages.json').read_text(encoding='utf8'))
    m['by'] = {p['slug']: p for p in m['pages']}
    return m


HOME = {
    'title': 'PokeRogue: Play Online & Encounter Guides',
    'description': 'Load the original PokeRogue browser game, sign in to start a run, and find guides for mobile versions, Dark Deal and Trash to Treasure encounter choices.',
    'image': 'original-menu.png',
}
CHEAT = [
    ('Dark Deal appears', 'From wave 30 in the Mystery Encounter window, with at least two party members. <a href="/pokerogue/dark-deal/#availability">Eligibility details →</a>'),
    ('Dark Deal costs', 'A random party member is removed. You get five Rogue Balls and a catchable boss. <a href="/pokerogue/dark-deal/#choose">Accept or refuse →</a>'),
    ('Trash to Treasure appears', 'From wave 100 with at least three party members, at most once per run. <a href="/pokerogue/trash-to-treasure/#recognize">Limits →</a>'),
    ('Dig for Valuables', 'Leftovers and Shell Bell, but shop items and rerolls cost 2.5× for the rest of the run. <a href="/pokerogue/trash-to-treasure/#budget">Price penalty →</a>'),
    ('Investigate Further', 'A Garbodor boss fight that opens with Toxic and Stockpile, then a reward choice. <a href="/pokerogue/trash-to-treasure/#battle">Prepare →</a>'),
]


def homepage():
    from hub_components import Hub
    m = manifest()
    h = Hub(m, BASE, 'pr', '/assets/pokerogue', thumb_dir='')
    bg = ''
    hero = h.hero(
        kicker='Turn-based Pokémon roguelite · Independent guides', title='PokeRogue ', sub='play online &amp; encounter guides',
        deck='Build a team, battle through a run, and weigh the choices you cannot take back. Open the original browser game in its own tab; a game account is required.',
        status=['Browser game · Account required', 'Release v1.12.2.4 checked', 'Checked 6 Nov 2026', 'Unofficial fan guide'],
        actions=[('Play on pokerogue.net ↓', '#play', False), ('Pick a guide', '#guides', True)], bg_attr=bg)
    cards = h.cards(heading='Pick the job you have right now', bg_attr=bg)
    cheat = h.cheat(m['preview']['title'], m['preview']['intro'], CHEAT, bg_attr=bg)
    play = (f'<section class="pr-band pr-start" id="play"><div class="pr-start-grid"><div><h2>Play on pokerogue.net</h2>'
            f'<p>Open the original game in its own tab to sign in, register and continue your run.</p>'
            f'<p><a class="button" href="https://pokerogue.net/" target="_blank" rel="noopener noreferrer">Play on pokerogue.net ↗<span class="sr-only"> (opens in a new tab)</span></a></p>'
            f'<p class="pr-entry-note">Sign-in, registration and saves are managed by the original game. Keep this guide open in a separate tab.</p></div>'
            f'<figure class="game-image"><img src="/assets/pokerogue/original-menu.png" width="1280" height="720" alt="Original PokeRogue account screen" loading="lazy"></figure></div></section>')
    start = ('<section class="pr-band" id="start"><h2>Start with the original game</h2><ol><li>Choose Play on pokerogue.net above. The original game opens in a new tab.</li>'
             '<li>Use your PokeRogue account or choose the original game’s registration option. This is an account-based game, not a guest-play demo.</li>'
             '<li>Follow the original game’s menus to begin or continue your run. Keep this guide tab open to check encounter choices.</li></ol>'
             '<p>On a small screen, the original’s touch controls and a larger landscape window can help. For browser shortcuts and community offline-app differences, use the '
             '<a href="/pokerogue/mobile/">mobile guide</a>. Do not assume a community app shares the web game’s account or saves.</p></section>')
    about = ('<section class="pr-band" id="about-game"><h2>About this game entry</h2><p>PokéRogue is a fan-made, turn-based Pokémon roguelite by the Pagefault Games project. '
             'This independent page links to the original ' + link('https://pokerogue.net/', 'pokerogue.net') + ' game; Megabonk.org does not operate the game, accounts or saves. '
             'It is a different game from PokeBonk and other similarly named Pokémon projects.</p><p>Checked 6 November 2026 against the original client and the '
             + link('https://github.com/pagefaultgames/pokerogue', 'project repository') + '. The original game opens in a separate tab and may change independently of these guides. '
             'Pokémon names and artwork belong to their respective owners.</p></section>')
    first_run = ('<section class="pr-band" id="first-run"><h2>Choose your first run</h2>'
                 '<p><strong>Classic:</strong> Pick one attacker with a useful starting move, then spend the remaining points on a teammate who can switch into its weaknesses. For example, pair a Fire attacker with a Grass starter to cover Water and Ground opponents. A purple frame on starter select means Pokérus and bonus experience. When two options fill the same job, use that as a tiebreaker.</p>'
                 '<p><strong>Daily Run:</strong> Everyone starts with the same seeded team. Plan for 50 waves and five biomes. The Map lets you choose between offered routes. The seed changes at midnight UTC. A run saved before rollover can still be finished. See the '+link('https://wiki.pokerogue.net/gameplay:modes:daily','Daily Run rules')+'.</p>'
                 '<p><strong>Map in Classic:</strong> At a biome boundary the Map offers connected destinations. For example, leaving Town with the Map can offer Plains, Metropolis or Lake. An optional connection can be absent on a given roll. Check the '+link('https://wiki.pokerogue.net/biomes:biomes','biome connections')+' before choosing.</p>'
                 '<p><strong>Menu and eggs:</strong> On a default keyboard press M or Esc to open the menu, or X or Backspace to cancel a selection. Spend vouchers in Egg Gacha. A hatch unlocks a future starter. The Golden Egg held item instead gives its holder 100% extra EXP. See the '+link('https://wiki.pokerogue.net/gameplay:eggs','egg guide')+' and '+link(RELEASE+'modifier/modifier-type.ts','held-item definitions')+'.</p></section>')
    resources = ('<section class="pr-band" id="community"><h2>Updates and community help</h2><p>For game changes, check the '+link('https://github.com/pagefaultgames/pokerogue/releases','project release notes')+'. Check the '+link('https://discord.gg/pokerogue','project Discord')+' for announcements and account support. For player strategies, visit '+link('https://www.reddit.com/r/pokerogue/','r/pokerogue')+'.</p></section>')
    body = hero + cards + cheat + play + start + first_run + h.updates(bg_attr=bg) + h.groups(bg_attr=bg) + about + resources + h.faq(bg_attr=bg)
    return f'<main class="wrap" id="main">{body}</main>', h.faq_questions()


def ads(html):
    return html.replace('</head>', AD + '</head>', 1)


def build():
    main, questions = homepage()
    html = ads(shell(BASE, HOME, 'pr-hub', '<link rel="stylesheet" href="/assets/pokerogue/hub.css?v=20261122">', main, 'website'))
    write_html(ROOT / 'pokerogue/index.html', html, encoding='utf8')
    for slug, fn in [('mobile', mobile), ('dark-deal', dark), ('trash-to-treasure', trash), ('eternatus', eternatus), ('gimmighoul', gimmighoul)]:
        p = ROOT / 'pokerogue' / slug / 'index.html'
        p.parent.mkdir(parents=True, exist_ok=True)
        write_html(p, ads(fn()), encoding='utf8')
    from pokerogue_trust import build as build_trust
    build_trust(shell)
    privacy()
    # 导航、面包屑、相关任务、页脚与登记来自 data/pokerogue-pages.json（02 §2.6、§5.2）
    subprocess.run([sys.executable, str(Path(__file__).resolve().parent / 'register_page.py'), str(ROOT), 'pokerogue'], check=True, stdout=subprocess.DEVNULL)
    register_seo(questions)
    from game_seo import edit as seo_edit  # register_page 追加头部标记后，保持 SEO 编辑器幂等
    for fp in (ROOT / 'pokerogue').rglob('index.html'):
        t0 = fp.read_text(encoding='utf8')
        n0 = seo_edit(fp, t0)
        if n0 != t0:
            fp.write_text(n0, encoding='utf8')
    print('Built PokeRogue home, 5 guides and About/Contact')


def register_seo(questions):
    """首页 FAQ 登记到 data/game-seo.json（可见问答与 FAQPage 同源），信任页补进 pages_list.txt（只追加）。"""
    f = ROOT / 'data/game-seo.json'
    d = json.loads(f.read_text(encoding='utf8'))
    d['pages']['pokerogue/index.html'] = {
        'questions': list(questions),
        'faq_review': 'Hub FAQ from data/pokerogue-pages.json (v3.26 F9); visible answers and FAQPage share one source (2026-11-22).',
        'language_review': 'No equivalent language page identified; do not map unrelated topics.',
        'reviewed_candidates': list(questions),
    }
    new = json.dumps(d, ensure_ascii=False, indent=2) + '\n'
    if f.read_text(encoding='utf8') != new:
        f.write_text(new, encoding='utf8')
    pl = ROOT / 'pages_list.txt'
    text = open(pl, encoding='utf8', newline='').read()
    add = ''.join(f'https://megabonk.org{BASE}{s}/\r\n' for s in ('about', 'contact', 'eternatus', 'gimmighoul') if f'{BASE}{s}/' not in text)
    if add:
        with open(pl, 'a', encoding='utf8', newline='') as out:
            out.write(add)


def privacy():
    """站级隐私页为本专区保留一节（02 §5.1），已有则不重复。"""
    f = ROOT / 'privacy-policy.html'
    s = open(f, encoding='utf8', newline='').read()
    if 'id="pokerogue"' in s:
        return
    section_html = ('<h2 id="pokerogue">PokeRogue guides</h2><p>Reviewed 22 November 2026. These pages host no game client, account or save and embed no third-party game window. '
                    'The Play button and the source links open pokerogue.net, GitHub or the community wiki in a new tab only when you click them, and that site then applies its own privacy practices; '
                    'sign-in and saves are handled entirely by the original game. Ordinary guide pages inherit this site’s existing AdSense loader and site-wide Umami analytics described here; '
                    'About and Contact carry no advertising. Cloudflare hosting and possible performance measurement are described above.</p>')
    marker = '<h2 id="midgard-survivors">'
    if marker not in s:
        raise SystemExit('privacy-policy.html: marker section not found')
    with open(f, 'w', encoding='utf8', newline='') as out:  # 保持原换行，不经 write_html 重排
        out.write(s.replace(marker, section_html + marker, 1))


if __name__ == '__main__':
    build()
