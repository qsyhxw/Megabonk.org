"""Reviewed Revenant Survivors task pages, checked 12 November 2026."""
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
        'slug': 'hard-mode', 'label': 'Hard Mode', 'title': 'Revenant Survivors Hard Mode rewards and World 5 unlock',
        'description': 'What Hard Mode rewards, when it gates World 5, and how to choose between progression and item farming after the November balance updates.',
        'answer': 'Hard Mode increases item drop rates, and clearing it is required to unlock World 5 and later worlds. The developer confirmed both points in the Steam discussion. Choose it for that progression gate or additional item drops once your build can finish the run.',
        'image': 'boss',
        'sections': [
            ('rewards', 'What Hard Mode rewards', '<p>The developer answered the player asking whether Hard Mode was only a challenge by confirming increased item drop rates and the World 5 progression requirement. The reply provides no percentage and leaves the separate question of increased Gold gain unresolved. Plan around the confirmed item benefit when comparing modes. '+thread('565924824838556705', 'Developer reply on Hard Mode rewards and unlocks')+'</p>'),
            ('choose', 'Choose a mode for your next run', '<ol><li><strong>You are trying to reach World 5 or beyond.</strong> Check your stage-selection unlock condition and work toward its Hard Mode clear. Repeating a lower-tier clear alone does not satisfy the stated Hard Mode requirement.</li><li><strong>You want equipment.</strong> Consider Hard Mode if you can complete it consistently. Higher drop rates alone do not establish the best items per minute, since failed or longer runs change that comparison.</li><li><strong>Your immediate bottleneck is Gold.</strong> Use your own completed-run rewards and time to compare. A Gold multiplier was not specified in the developer reply.</li><li><strong>You are struggling with a boss.</strong> Review your retained equipment and upgrades, then retry after confirming your installed build. The balance changed again on November 11.</li></ol>'),
            ('balance', 'Match difficulty advice to the current patch', '<p>Update 0.6.2 reduced the World 1 boss jumping-slam area and adjusted World 6 patterns. The November 11 hotfix 0.6.2.1 changed final-boss health and attack power in Tiers 2–4, reduced regular-enemy health in Tier 4, and changed the Hard Mode final-boss health multiplier. These announcements provide no numerical multiplier. '+link(HUB, 'Mongma Studio patch announcements')+'</p><p>For an unlock problem, record the world, tier, mode and result shown after the run. The developer’s short reply establishes the progression gate, while the stage-selection screen supplies the specific condition for your selected world. We have not independently played through that chain.</p>'),
        ],
        'alt': 'Angel of Obsession boss fight with radial red attack warnings',
        'caption': 'Boss arenas and their attack warnings matter when deciding whether your build can finish a harder run.',
    },
    {
        'slug': 'permanent-progression', 'label': 'Equipment & progression', 'title': 'Revenant Survivors permanent loot, upgrades and cosmetics',
        'description': 'Separate retained equipment, Forge and skill progression from appearance changes, and check how the launch Supporter Pack changes older cosmetic answers.',
        'answer': 'Equipment carries between runs and can be upgraded. Skill Trees, Soul Engraving and Forge upgrades also provide permanent progression. Equipped gear does not change character appearance according to the developer’s October reply. The November launch added a separate cosmetic Supporter Pack.',
        'image': 'forge',
        'sections': [
            ('keep', 'What carries between runs', '<p>A player asked whether loot was permanent and whether it changed appearance. Mongma Studio confirmed retained equipment and the permanent upgrade systems in its October 26 reply. The launch announcement also describes equipment and persistent progression. '+thread('588438959484653157', 'Developer explanation of retained loot')+' · '+link(HUB, 'November 9 launch announcement')+'</p><p>After a run, inspect the equipment you kept and the upgrade panels in town before judging your next attempt by its starting attacks alone. Equipment, character growth and the choices made during combat each affect a different part of preparation.</p>'),
            ('prepare', 'Turn a completed run into your next attempt', '<ol><li>Open your Bag and review retained equipment. Compare the stats relevant to the attacks you actually use.</li><li>Inspect the Forge upgrade preview and its displayed cost before spending materials.</li><li>Review the Skill Trees and Soul Engraving panels for available permanent upgrades. Follow the requirements displayed by your installed version.</li><li>Return to stage selection and choose whether your next goal is a clear, equipment drops or a Hard Mode unlock.</li></ol><p>This sequence combines the confirmed persistence rules with the visible town interfaces. It is an editorial preparation checklist. We have not measured an optimal upgrade order or resource-farming rate.</p>'),
            ('appearance', 'Gear appearance and the Supporter Pack', '<p>The October developer reply says equipment leaves character appearance unchanged and, at that time, there was no cosmetic customization system. The November 9 launch announcement subsequently introduced the Supporter Pack with two skins for each of three characters. It describes those skins as cosmetic with no effect on stats or gameplay progression. '+link(HUB, 'Launch announcement and Supporter Pack explanation')+'</p><p>If you want stronger equipment, spend your attention on gear and the upgrade panels. If you want a different character look, inspect the current skin offering separately. The launch skins do not establish that equipped armor now changes the character model.</p>'),
        ],
        'alt': 'Revenant Survivors Forge showing a weapon enhancement preview beside the Bag',
        'caption': 'The Forge preview and retained equipment inventory help you plan the next run.',
    },
    {
        'slug': 'demo-save-transfer', 'label': 'Demo save transfer', 'title': 'Revenant Survivors demo save transfer to Early Access',
        'description': 'Move demo progress into Revenant Survivors Early Access, check the first launch on the original PC, then sync the full-game save to another PC.',
        'answer': 'Demo progress can carry into the full game. For the first full-game launch, use the PC that still holds your demo save. Confirm the imported progress, close the game and let Steam Cloud finish syncing before moving to another PC on the same Steam account.',
        'image': 'tree',
        'sections': [
            ('first-launch', 'First launch on the PC with your demo save', '<p>A Steam player asked whether Demo progress would transfer to Early Access. The developer confirmed it on October 26 and supplied the first-launch and Cloud sequence in the November 9 release announcement. '+thread('563671642446948252', 'Developer confirmation of Demo transfer')+' · '+link(HUB, 'Launch instructions for save transfer')+'</p><ol><li>Use the PC where you played the Demo and still have its local save data.</li><li>Launch the full game there for the first time.</li><li>Inspect recognizable progress, such as your unlocked content and permanent-upgrade panels, before continuing.</li><li>Once the transfer looks correct, close the full game normally.</li><li>Wait for Steam Cloud to finish syncing the full-game save.</li></ol>'),
            ('second-pc', 'Continue on another PC', '<p>After the first successful transfer, sign into the same Steam account on the other PC. Enable Steam Cloud on each PC and wait for syncing to finish before starting the full game. This is the sequence specified in the release announcement.</p><p>The first local import and subsequent full-game Cloud synchronization are two consecutive steps. If you already opened the full game elsewhere and the expected progress is missing, return to checking which PC holds the Demo data before attempting further transfers.</p>'),
            ('missing', 'If expected progress is missing', '<ol><li>Record which PC contains the Demo save and where the full game was first launched.</li><li>Check the Steam account and Cloud status on both PCs.</li><li>Capture the full-game progress screen showing the discrepancy and record the installed version.</li><li>Send those details through '+link('https://steamcommunity.com/app/4617500/discussions/', 'the game’s Steam Discussions')+'. The developer requests reports when transfer fails.</li></ol><p>The reviewed instructions do not specify a manual file-copy path, recovery command or cross-store transfer procedure. A failed import therefore needs a report with the launch sequence and account details relevant to the issue. Keep passwords out of public reports. This guide follows the developer’s procedure and has no independent save-transfer test.</p>'),
        ],
        'alt': 'Revenant Survivors character skill tree with unlocked nodes and character statistics',
        'caption': 'Use recognizable permanent progression, such as your skill tree, to check the imported save.',
    },
    {
        'slug': 'controller-auto-attack', 'label': 'Controller help', 'title': 'Revenant Survivors controller and auto-attack checks',
        'description': 'Check Basic Attack and Strike automation, distinguish old playtest controller reports from the current release, and report unresolved input symptoms.',
        'answer': 'Check the auto-attack mode first. The developer describes separate options for automating Basic Attack plus Strike, or Basic Attack alone with manual Strike. Steam currently lists full controller support. Older playtest reports describe incomplete menus and interactions, so match each report to its version.',
        'image': 'controls',
        'sections': [
            ('mode', 'Check what the selected attack mode automates', '<p>In the difficulty discussion, the developer explains the two auto-attack settings. If Basic Attack happens automatically while Strike still needs input, inspect whether the Basic-only option is selected. '+thread('580554442217253070', 'Developer explanation of auto-attack modes')+'</p><ol><li>Open Settings and inspect the current auto-attack choice.</li><li>Choose whether Strike should also be automated, then follow the current UI’s confirmation prompt.</li><li>Return to combat and observe Basic Attack and Strike separately.</li><li>If neither activates as expected, record the controller model, mode and exact behavior for a report.</li></ol>'),
            ('versions', 'Separate historical problems from the release listing', '<p>The August controller thread contains reports of movement working while menus, skill choices and interactions were incomplete. The developer acknowledged those limitations on August 18. Later playtest updates addressed controller support and portal input, while the September 4 discussion identified another Demo input issue after Steam Input was introduced. '+thread('591811524772889552', 'Historical controller discussion')+' · '+thread('580554442217253070', 'Demo input follow-up')+'</p><p>The current '+link(STORE, 'Steam store listing')+' advertises Full Controller Support. That listing and the older reports have different dates and scopes. Use the installed release’s behavior to decide what still needs reporting.</p>'),
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


HOME = {
    'slug': '', 'label': 'Overview',
    'title': 'Revenant Survivors guide — start, progression and help',
    'description': 'Choose where to start in Revenant Survivors, move a Demo save into Early Access, plan retained upgrades and find version-specific help.',
    'answer': 'Start with the free Steam Demo if you want to try the game. If you already played it, transfer your Demo save on the original PC before switching computers. For continuing runs, review retained equipment and upgrades, then use Hard Mode when you need its item rewards or World 5 progression gate.',
    'image': 'boss', 'alt': 'Revenant Survivors Angel of Obsession boss arena with red ground attack warnings',
    'caption': 'Revenant Survivors combines horde combat with boss encounters and persistent character growth.',
    'sections': [
        ('start', 'Choose your starting point', '<p>Revenant Survivors is Mongma Studio’s single-player dark-fantasy horde-survival roguelite. It entered Steam Early Access on November 9, 2026. The full game and free Demo have separate Steam listings. Use the listing for your intended edition.</p><p>'+link(STORE, 'Revenant Survivors full game on Steam')+' · '+link('https://store.steampowered.com/app/4693240/', 'Free Revenant Survivors Demo on Steam')+'</p><ul><li><strong>Trying the game.</strong> Start with the Demo listing and check its current requirements before installing.</li><li><strong>Returning from the Demo.</strong> Open the full game first on the PC with your Demo save, inspect the imported progress, close the game and finish Steam Cloud syncing. Follow the <a href="/revenant-survivors/demo-save-transfer/">save-transfer steps</a> before continuing on another PC.</li><li><strong>Preparing another run.</strong> Review the equipment you kept, Forge options and permanent upgrades. The <a href="/revenant-survivors/permanent-progression/">progression guide</a> explains how equipment, upgrades and appearance relate.</li></ul>'),
        ('progression', 'Decide what your next run should achieve', '<p>Boss powers and evolving attacks shape combat, while retained equipment, Skill Trees and Soul Engraving support growth between attempts. Choose a concrete goal before selecting the next stage.</p><ul><li><strong>Advance to later worlds.</strong> Hard Mode clears are required for World 5 and beyond. Check the selected world’s displayed unlock condition, then use the <a href="/revenant-survivors/hard-mode/">Hard Mode rewards and unlock guide</a>.</li><li><strong>Improve equipment.</strong> Hard Mode has increased item drop rates. Whether it produces more useful gear for your time depends on your ability to finish the run. Review the <a href="/revenant-survivors/permanent-progression/">equipment preparation checklist</a> first.</li><li><strong>Change character appearance.</strong> The launch Supporter Pack contains cosmetic skins. Review the <a href="/revenant-survivors/permanent-progression/#appearance">gear and skin distinction</a> before choosing an upgrade or purchase.</li></ul><p>These choices combine the developer’s progression replies with the launch information. '+link(HUB, 'Mongma Studio launch and update announcements')+'</p>'),
        ('help', 'Find help for the symptom you see', '<ul><li><strong>Basic Attack or Strike behaves unexpectedly.</strong> Check which attack the automation setting controls in the <a href="/revenant-survivors/controller-auto-attack/">controller and auto-attack guide</a>. It also separates historical playtest input reports from the current Steam support listing.</li><li><strong>The screen stops after a run.</strong> Match the transition and game edition to the <a href="/revenant-survivors/stuck-after-run/">reported loading and crash fixes</a>.</li><li><strong>The full game opens without expected Demo progress.</strong> Check the original PC, first-launch sequence and Cloud status using the <a href="/revenant-survivors/demo-save-transfer/#missing">missing-progress checks</a>.</li></ul>'),
        ('versions', 'Use advice for your installed edition', '<p>The latest official update checked on November 12 is full-game hotfix 0.6.2.1, which adjusts boss and enemy balance. Demo and playtest reports use their own version numbers. Match the edition and symptom before applying an older workaround. '+link(HUB, 'Official Steam announcements')+'</p><p>These independent guides review developer announcements and public player discussions. The linked articles identify the evidence and version limits for their specific answers. The gameplay images are developer promotional screenshots with unspecified capture builds.</p>'),
    ],
}


def homepage():
    cards = [
        ('demo-save-transfer', 'tree', 'Continue your Demo save', 'Move your progress to Early Access, then sync it to another PC.'),
        ('permanent-progression', 'forge', 'Equipment & permanent upgrades', 'See what you keep and prepare your character for the next run.'),
        ('hard-mode', 'boss', 'Hard Mode & world unlocks', 'Check item rewards and the progression gate for World 5 and beyond.'),
        ('controller-auto-attack', 'controls', 'Controller & auto attack', 'Check attack modes and identify the input that needs attention.'),
        ('stuck-after-run', 'battle', 'Stuck after a run', 'Match loading and results-screen problems to reported fixes.'),
    ]
    def card(entry):
        slug, media, title, text = entry
        return f'<a class="hub-card" href="{BASE}{slug}/"><img src="/assets/revenant-survivors/{media}-480.webp" width="1920" height="1080" loading="lazy" alt=""><div><h3>{title}</h3><p>{text}</p><span>Read guide <span aria-hidden="true">↗</span></span></div></a>'
    hero = image(HOME['image'], HOME['alt'], HOME['caption']).replace('loading="lazy"', 'fetchpriority="high"')
    return f'''<main id="main" class="hub-main">
<section class="hub-hero"><div class="wrap hub-hero-grid"><div class="hub-intro"><p class="eyebrow">Independent player guides</p><h1>{HOME['title']}</h1><p class="hub-lead">Claim a boss’s power. Prepare your next run.</p><p>Find your way into Mongma Studio’s dark-fantasy survivorslike, then plan your upgrades and work through the next obstacle.</p><div class="hub-actions"><a class="hub-button" href="#guides">Explore the guides <span aria-hidden="true">↓</span></a><a class="hub-secondary" href="#start">Get the game</a></div></div>{hero}</div></section>
<div class="hub-status"><div class="wrap"><span>Steam · Single-player</span><span>Early Access</span><span>Source review · 12 November 2026</span></div></div>
<section class="wrap hub-section" id="guides"><div class="hub-heading"><div><p class="eyebrow">Your next step</p><h2>Pick up where you left off</h2></div><p>Choose the guide for your current goal.</p></div><div class="hub-feature-grid">{''.join(card(c) for c in cards[:3])}</div></section>
<section class="hub-start-band" id="start"><div class="wrap hub-start"><div><p class="eyebrow">New to Revenant Survivors</p><h2>Start with the Demo.<br>Bring your progress with you.</h2><p>Try the free Steam Demo or enter the full game’s Early Access release. Boss powers and evolving attacks shape combat, while equipment and permanent upgrades carry your preparation forward.</p><div class="hub-store-links">{link('https://store.steampowered.com/app/4693240/', 'Free Demo on Steam')}{link(STORE, 'Full game on Steam')}</div></div><div class="hub-start-note"><h3>Returning from the Demo</h3><p>Launch the full game first on the PC with your Demo save. Check your imported progress, close the game and finish Steam Cloud syncing before changing computers.</p><a href="{BASE}demo-save-transfer/">Follow the transfer steps →</a></div></div></section>
<section class="wrap hub-section" id="help"><div class="hub-heading"><div><p class="eyebrow">Get back into the game</p><h2>Help with controls and loading</h2></div></div><div class="hub-help-grid">{''.join(card(c) for c in cards[3:])}</div></section>
<section class="wrap hub-update" id="versions"><div><h2>Check your edition before applying a fix</h2><p>Full-game hotfix <strong>0.6.2.1</strong> was the latest official update checked on 12 November. Demo and playtest reports use separate version numbers.</p></div><div>{link(HUB, 'Developer announcements')}<p>Guides draw on developer statements and public player reports. Each article gives the source and version scope for its answers.</p></div></section>
</main>'''


def build():
    for page in [HOME] + PAGES:
        route = BASE + (page['slug'] + '/' if page['slug'] else '')
        nav = ''.join(f'<a href="{BASE}{p["slug"] + "/" if p["slug"] else ""}">{p["label"]}</a>' for p in (HOME, PAGES[0], PAGES[2]))
        toc = ''.join(f'<a href="#{key}">{title}</a>' for key, title, _ in page['sections'])
        body = image(page['image'], page['alt'], page['caption'])
        body += ''.join(f'<section id="{key}"><h2>{title}</h2>{text}</section>' for key, title, text in page['sections'])
        related = ''.join(f'<li><a href="{BASE}{p["slug"] + "/" if p["slug"] else ""}">{p["title"]}</a></li>' for p in PAGES if p != page)
        body += f'<section id="related"><h2>More Revenant Survivors guides</h2><ul>{related}</ul></section>'
        html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(page['title'])}</title><meta name="description" content="{escape(page['description'], quote=True)}"><link rel="canonical" href="https://megabonk.org{route}"><meta property="og:title" content="{escape(page['title'])}"><meta property="og:description" content="{escape(page['description'], quote=True)}"><meta property="og:type" content="article"><meta property="og:url" content="https://megabonk.org{route}"><meta property="og:image" content="https://megabonk.org/assets/revenant-survivors/{page['image']}-1920.webp"><link rel="icon" href="/assets/revenant-survivors/favicon.ico"><link rel="icon" type="image/svg+xml" href="/assets/revenant-survivors/favicon.svg"><link rel="apple-touch-icon" href="/assets/revenant-survivors/icon-180.png"><link rel="stylesheet" href="/assets/guide-article-layout.css"><link rel="stylesheet" href="/assets/revenant-survivors/site.css"><script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8830315294299920" crossorigin="anonymous"></script></head><body class="guide-layout revenant-guide"><a class="skip" href="#main">Skip to content</a><header class="top"><div class="wrap"><a class="brand" href="/revenant-survivors/"><img src="/assets/revenant-survivors/logo.svg" width="36" height="36" alt="">Revenant Survivors</a><nav class="desktop-nav" aria-label="Revenant Survivors tasks">{nav}</nav><details class="mobile-nav"><summary>Menu</summary><nav class="mobile-links" aria-label="Revenant Survivors tasks">{nav}</nav></details></div></header><main class="wrap" id="main"><header class="article-head"><p class="eyebrow">Revenant Survivors · Independent guides</p><h1>{escape(page['title'])}</h1><p class="answer">{page['answer']}</p><p class="meta">Megabonk.org editors · Checked 12 November 2026 · Early Access</p></header><div class="article-layout"><nav class="toc" aria-label="On this page">{toc}</nav><article class="prose">{body}</article></div></main><footer class="footer wrap"><p>Published by Megabonk.org. Independent of Mongma Studio. Source-based reporting.</p><p><a href="/#more-games">More games</a> · <a href="/about/">About</a> · <a href="/contact/">Contact</a> · <a href="/privacy-policy">Privacy</a></p></footer></body></html>'''
        if page is HOME:
            start = html.index('<main ')
            end = html.index('</main>', start) + len('</main>')
            html = html[:start] + homepage() + html[end:]
            html = html.replace('class="guide-layout revenant-guide"', 'class="guide-layout revenant-guide revenant-home"')
            html = html.replace('<link rel="stylesheet" href="/assets/revenant-survivors/site.css">', '<link rel="stylesheet" href="/assets/revenant-survivors/site.css"><link rel="stylesheet" href="/assets/revenant-survivors/home.css">')
            html = html.replace('property="og:type" content="article"', 'property="og:type" content="website"')
        target = ROOT / route.strip('/') / 'index.html'
        target.parent.mkdir(parents=True, exist_ok=True)
        write_html(target, html, encoding='utf8')
    print('Built Revenant Survivors overview and 5 reviewed task pages')


if __name__ == '__main__':
    build()
