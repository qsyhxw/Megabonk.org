"""Reviewed November 8 CSV tasks, using the existing Warhammer shell."""
from html import escape
from pathlib import Path
import re
from site_analytics import write_html

ROOT = Path(__file__).resolve().parents[1]
BASE = '/warhammer-survivors/'
RECIPES_SOURCE = 'https://steamcommunity.com/app/3669620/discussions/0/582810370003993958/'
REPORTS_SOURCE = 'https://steamcommunity.com/app/3669620/discussions/0/573792283565024740/'
GAMEPASS = 'https://news.xbox.com/en-us/2026/11/03/xbox-game-pass-november-2026-wave-1/amp/'
FAQ = 'https://aurochdigital.com/warhammer-survivors-faq'
STORE = 'https://store.steampowered.com/app/3669620/Warhammer_Survivors/'
DEMO = 'https://www.warhammer-community.com/en-gb/articles/m5cfelii/try-the-new-demo-for-warhammer-survivors-now/'

# One row for the recipe reported in both universes.
RECIPES = [
    ('Tempest Axes', 'Sabaton', 'Whirlwind Axes', 'Age of Sigmar'),
    ('Nebulous Sea Fog', "Bugman's Tankard", 'Aquatic Illusions', 'Age of Sigmar'),
    ('Boltstorm Pistol', 'Dice Cube', 'Typhoon Crossbow', 'Age of Sigmar'),
    ('Brazier Staff', 'Liquid Green Stuff', 'Master of Runes', 'Age of Sigmar'),
    ('Rope & Grapnel', 'White Dwarf', 'Ghost of Rhea', 'Age of Sigmar'),
    ('Nuln Oil', 'Hourglass', 'Mordant Earth', 'Both'),
    ('Chainsword', 'Tape Measure', 'Eviscerator Chainsword', 'Warhammer 40,000'),
    ('Lasgun', 'Gauntlet', 'Meltagun', 'Warhammer 40,000'),
    ('Boltgun', 'Dice Cube', 'Heavy Bolter', 'Warhammer 40,000'),
    ('Whirlwind Battery', 'Liquid Green Stuff', 'Orbital Bombardment', 'Warhammer 40,000'),
    ('Frag Grenade', 'Bandolier', 'Ripper Pistol', 'Warhammer 40,000'),
]

def external(url, label):
    return f'<a href="{url}" target="_blank" rel="noopener noreferrer">{label} ↗<span class="sr-only"> (opens in a new tab)</span></a>'

def image(stem, alt, caption):
    return f'<figure><a href="/assets/warhammer-survivors/{stem}-1280.webp"><img src="/assets/warhammer-survivors/{stem}-800.webp" width="1920" height="1080" alt="{escape(alt, quote=True)}" loading="lazy"></a><figcaption>{caption}</figcaption></figure>'

def navigation(text):
    links = [('Overview', BASE), ('Evolutions', BASE+'evolutions/'), ('Co-op', BASE+'co-op/'), ('More games', '/#more-games')]
    markup = ''.join(f'<a href="{url}">{label}</a>' for label, url in links)
    stylesheet = '<link rel="stylesheet" href="/assets/warhammer-survivors/site.css">'
    if 'href="/assets/warhammer-survivors/site.css' not in text:
        text = text.replace('</head>', stylesheet+'</head>')
    return re.sub(r'(<nav class="(?:desktop-nav|mobile-links)"[^>]*>).*?(</nav>)', lambda match: match[1]+markup+match[2], text, flags=re.S)

def render(template, route, title, description, heading, answer, sections, stem, tool=False):
    head = template.split('<main id="main"', 1)[0]
    head = re.sub(r'<title>.*?</title>', f'<title>{title}</title>', head)
    head = re.sub(r'(<meta name="description" content=")[^"]*', lambda match: match[1]+description, head)
    for prop, value in [('title', title), ('description', description), ('url', 'https://megabonk.org'+route), ('image', f'https://megabonk.org/assets/warhammer-survivors/{stem}-1280.webp')]:
        head = re.sub(r'(<meta property="og:'+prop+r'" content=")[^"]*', lambda match: match[1]+value, head)
    head = re.sub(r'(<link rel="canonical" href=")[^"]*', lambda match: match[1]+'https://megabonk.org'+route, head)
    if tool:
        head = head.replace('</head>', '<script defer src="/assets/warhammer-survivors/recipes.js"></script></head>')
    toc = ''.join(f'<a href="#{key}">{label}</a>' for key, label, _ in sections)
    body = ''.join(f'<section id="{key}"><h2>{label}</h2>{content}</section>' for key, label, content in sections)
    footer = '<footer'+template.split('<footer', 1)[1]
    content = f'''<main id="main" class="wrap"><header class="article-head" id="guide"><p>WARHAMMER SURVIVORS · OCTOBER DEMO / PRE-RELEASE</p><h1>{heading}</h1><div class="answer">{answer}</div><p class="byline">Megabonk.org editors · Checked 8 November 2026 · Full game planned for 10 November</p></header><nav class="toc" aria-label="On this page">{toc}</nav><div class="article-layout"><article class="prose">{body}<p><a href="#guide">Back to top ↑</a></p></article></div></main>'''
    return navigation(head+content+footer)

def overview():
    return [
        ('choose', 'Choose what you need today', '''<div class="choice"><h3>Try it before launch</h3><p>Use the PC demo links below. If you want permanent launch progress, wait for the full release because demo unlocks do not transfer.</p></div><div class="choice"><h3>Already playing the demo</h3><p>Open the <a href="/warhammer-survivors/evolutions/">weapon evolution list</a> to match your weapon and passive, then check the reported trigger sequence.</p></div><div class="choice"><h3>Buying for a group</h3><p>Check the <a href="/warhammer-survivors/co-op/">co-op and friends guide</a> before buying extra copies. The announced launch experience is single-player.</p></div>'''),
        ('release', 'Release date and access choices', f'''<p>The developer gives <strong>10 November 2026</strong> as the full launch date. As of this check on 8 November, the demo is the playable pre-release reference. The announced base price is $7.99 / £6.39 / €7.49, with platform and region differences possible. {external(FAQ, 'Auroch Digital FAQ')}</p><p>If you have <strong>Game Pass Ultimate or PC Game Pass</strong>, check your existing access before buying a second copy. Xbox Wire lists Warhammer Survivors for 10 November across cloud, Xbox Series X|S, handheld and PC under those plans. The named device list and membership determine the route available to you. {external(GAMEPASS, 'Xbox Wire November lineup')}</p><p>Other announced storefronts and platforms include Steam, GOG, PS5, Switch 1 and 2, Google Play and iOS. Choose your actual storefront and region to confirm availability and checkout price. {external(FAQ, 'Developer platform list')}</p>'''),
        ('demo', 'Get the current demo and understand its save boundary', f'''<ol><li>On Windows PC, open the {external(STORE, 'official Steam page')} and look for <strong>Download Warhammer Survivors Demo</strong>. The full game and the demo are separate choices.</li><li>For Xbox PC, use the {external('https://www.xbox.com/en-US/games/store/warhammer-survivors-demo/9nnc01xm23nc', 'Xbox demo listing')}. Check the device compatibility on that listing.</li><li>Start the current October demo if you want to judge the controls and solo combat. Keep any recipe notes tied to that build.</li></ol><p>Warhammer Community names Steam and Xbox PC as demo routes. Its console launch list does not establish that every console has a demo. {external(DEMO, 'Warhammer Community demo announcement')}</p><p>The earlier demo's progress does not carry into the updated demo, and this demo's progress does not carry into the full game. For permanent progression, begin again in the released game. {external('https://steamcommunity.com/app/3669620/announcements/', 'Auroch October 6 release announcement')}</p>'''),
        ('identity', 'Warhammer, Vampire Survivors and the two settings', f'''<p>Auroch Digital develops Warhammer Survivors in partnership with Warhammer and poncle. It is a standalone purchase. Existing Vampire Survivors ownership does not supply this game's license. The developer describes a game built on the Vampire Survivors foundation, with its own champions, weapons, stages and secrets. {external(FAQ, 'Developer game FAQ')}</p><p>Warhammer 40,000 and Age of Sigmar are represented here. Select the universe that matches your run when using the <a href="/warhammer-survivors/evolutions/">reported recipe table</a>. Several similar-looking weapon names lead to different recipes.</p>'''),
        ('guides', 'Guides for your next decision', '<p><a href="/warhammer-survivors/evolutions/">Weapon evolutions, companion lookup and failed-pair checks →</a></p><p><a href="/warhammer-survivors/co-op/">Single-player status and ways to play a survivors game with friends →</a></p>'+image('squad', 'Warhammer Survivors champion and allies beside a tank facing Tyranids', 'Official Steam gameplay image, © Games Workshop Limited. Capture build unspecified.')),
    ]

def evolutions():
    rows = ''.join('<tr>'+''.join(f'<td>{escape(cell)}</td>' for cell in row)+'</tr>' for row in RECIPES)
    return [
        ('recipes', 'Find the weapon and companion', f'''<p>These are <strong>October-demo community reports</strong> from Unknown Traveller's 7 October Steam table. Names and availability may change at full release. Nuln Oil appears in both universe lists, producing 12 entries but 11 unique recipes. {external(RECIPES_SOURCE, 'Original October recipe table')}</p><form id="recipe-filter" class="tool"><label for="recipe-query">Weapon, passive or evolved form</label><input id="recipe-query" type="search" placeholder="Try Lasgun or Dice Cube"><label for="recipe-universe">Your universe</label><select id="recipe-universe"><option value="All">All</option><option>Age of Sigmar</option><option>Warhammer 40,000</option></select><button type="reset">Clear filters</button><p id="recipe-count" role="status">11 reported recipes</p></form><div class="table-wrap" tabindex="0" role="region" aria-label="Evolution recipes, scroll horizontally"><table id="recipe-table"><thead><tr><th>Weapon</th><th>Companion</th><th>Evolution</th><th>Universe</th></tr></thead><tbody>{rows}</tbody></table></div><noscript><p>The full recipe table above works without JavaScript.</p></noscript>'''),
        ('sequence', 'From holding the pair to trying the evolution', f'''<ol><li>Match the <strong>weapon and companion</strong> in your current run to the October table.</li><li>Check the weapon's upgrade state. In the October discussion, Bastion reports that the weapon must be at its maximum.</li><li>Then open a Boss chest, following that player's reported sequence.</li><li>For <strong>Frag Grenade</strong>, check Bandolier specifically. bdhaskell separately reports a maxed Bandolier for that pairing.</li></ol><p>These trigger conditions are player reports. Their replies do not give universal numeric levels or chest timing, and the Bandolier observation does not establish a maximum-passive requirement for every recipe. Keep the displayed weapon and passive states in a screenshot if your attempt fails. {external(REPORTS_SOURCE, 'Bastion and bdhaskell evolution reports')}</p>'''),
        ('version', 'Three older pairings to recheck', f'''<p>The early replies in the same discussion contain older combinations. October replies change Whirlwind Battery to <strong>Liquid Green Stuff</strong>, Sea Fog to <strong>Bugman's Tankard</strong>, and the Age of Sigmar pistol pairing to <strong>Dice Cube</strong>. A guide that gives Tape Measure for Whirlwind Battery or Glue for Sea Fog may describe the older demo. Compare the post date and the item you actually see. {external(REPORTS_SOURCE, 'Older list and October corrections')}</p><p>Dice Cube appears next to Boltstorm Pistol in Age of Sigmar and Boltgun in 40K. Liquid Green Stuff appears next to Brazier Staff and Whirlwind Battery respectively. Use the universe filter before treating those as choices available together in one run.</p>'''),
        ('missing', 'A missing passive is a different next step', f'''<p>If the companion never appears in your choices, first inspect the game's Objectives and Armoury for your selected universe. One player in the recipe thread reported repeatedly surviving while Bandolier stayed locked. The reply proposing a Boltgun level requirement explicitly could not name the level, so it does not supply an exact unlock instruction. {external(RECIPES_SOURCE, 'Bandolier availability discussion')}</p><p>If both items are present, use the reported upgrade and chest checks above. If one is unavailable, record the locked objective and its wording. This separates an unlock question from an evolution trigger question.</p>'''),
        ('next', 'Choose your next task', '<p>The full game is planned for 10 November. Recheck demo recipes against its actual Armoury before using them as launch recipes. <a href="/warhammer-survivors/">Get the demo and check the release/access choices →</a></p><p>For player count and squad allies, use the <a href="/warhammer-survivors/co-op/">co-op guide →</a>.</p>'+image('combat', 'A gold-armoured Warhammer Survivors champion attacking approaching enemies in a stone courtyard', 'Official development gameplay screenshot, © Games Workshop Limited. It illustrates weapon combat. The recipe evidence comes from the linked player reports.')),
    ]

def build():
    from warhammer_home import redesign
    from warhammer_launch import apply
    from warhammer_gsc_tasks import build as build_tasks, connect
    old = ROOT/'warhammer-survivors/co-op/index.html'
    template = old.read_text(encoding='utf8')
    write_html(old, connect(BASE+'co-op/', apply(BASE+'co-op/', navigation(template))), encoding='utf8')
    pages = [
        (BASE, 'Warhammer Survivors Guide: Demo, Release & Game Pass', 'Choose how to try Warhammer Survivors, check November 10 release and Game Pass access, then find October-demo weapon evolutions or co-op answers.', 'Warhammer Survivors', '<p><strong>The full game is planned for 10 November 2026.</strong> Try the current PC demo, check your Game Pass access, or use the October-demo evolution guide to plan your next run.</p>', overview(), 'squad', False),
        (BASE+'evolutions/', 'Warhammer Survivors Evolutions: October Demo Recipes', 'Find 11 reported Warhammer Survivors weapon evolution recipes, match a companion to your universe, and check upgrade, chest and old-demo differences.', 'Warhammer Survivors weapon evolutions', '<p><strong>Match a weapon with its companion, then check the reported upgrade and chest conditions.</strong> The October demo has 11 unique community-reported pairings below. Use the universe filter to find the pair relevant to your run.</p>', evolutions(), 'combat', True),
    ]
    for route, title, description, heading, answer, sections, stem, tool in pages:
        file = ROOT/route.strip('/')/'index.html'
        file.parent.mkdir(parents=True, exist_ok=True)
        document = connect(route, apply(route, render(template, route, title, description, heading, answer, sections, stem, tool)))
        if route == BASE:
            document = redesign(document)
            # Intermediate hub layer: warhammer_v321 rebuilds the hub (with its FAQ) and writes it through
            # write_html at the end, so skip the SEO/FAQ editor here (it needs the final visible FAQ).
            file.write_text(document, encoding='utf8')
            continue
        write_html(file, document, encoding='utf8')
    build_tasks((ROOT/'warhammer-survivors/co-op/index.html').read_text(encoding='utf8'))
    from warhammer_query_batch import build as build_query_batch
    build_query_batch((ROOT/'warhammer-survivors/co-op/index.html').read_text(encoding='utf8'))
