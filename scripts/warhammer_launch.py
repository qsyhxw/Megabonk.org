"""Launch-day corrections and reviewed task additions, checked November 11."""
from html import escape
import re

FAQ = 'https://aurochdigital.com/warhammer-survivors-faq'
APPLE = 'https://apps.apple.com/us/app/warhammer-survivors/id6752607219'
EVOLUTIONS = 'https://www.destructoid.com/all-weapon-evolutions-in-warhammer-survivors/'
CHARACTERS = 'https://www.destructoid.com/all-characters-in-warhammer-survivors-and-how-to-unlock-them/'

# Additional launch-report entries. The October rows remain sourced separately.
ADDITIONS = [
    ('Shield of Faith', "Bugman's Tankard", "Emperor's Wrath", 'Warhammer 40,000'),
    ('Flamer', 'Glue', 'Heavy Flamer', 'Warhammer 40,000'),
    ('Combat Shotgun', 'Magnet', 'Executioner Shotgun', 'Warhammer 40,000'),
    ('Mechanical Bite', 'Sabaton', 'Remote Detonation', 'Warhammer 40,000'),
    ('Power Klaw', 'Da Lucky Stikk', 'Bale Eye', 'Warhammer 40,000'),
    ('Ardent Blade', 'Tactical Rock', 'Weapon of the Matriarch', 'Warhammer 40,000'),
    ('Power Fist', 'Codex Astartes', 'Gauntlets of Ultramar', 'Warhammer 40,000'),
    ('Storm Bolter', 'Lightning Bolt', 'Assault Cannon', 'Warhammer 40,000'),
    ('Battle Cannon', 'Figure Case', 'Side Sponsors', 'Warhammer 40,000'),
    ('Spear of the Faithful', 'Chaos Sigil', 'Thorn of the White Rose', 'Warhammer 40,000'),
    ('Crozius Arcanum', 'Lightning Bolt', 'Benediction of Fury', 'Warhammer 40,000'),
    ('Smite', 'Ardcoat', 'Fury of the Ancients', 'Warhammer 40,000'),
    ('Fidelis', 'Golden Demon', 'Purgator Mirabilis', 'Warhammer 40,000'),
    ('Storm Eagle Rocket', 'White Dwarf', 'Deathstrike Missile', 'Warhammer 40,000'),
    ('D6 Dice', 'Scatter Dice', 'Sustained Fire Dice', 'Both'),
    ('Brace of Pistols', 'Bandolier', 'Duelling Pistols', 'Age of Sigmar'),
    ('Grandblade', 'Tape Measure', 'Celestial Greatsword', 'Age of Sigmar'),
    ('Cyclone Sword', 'Magnet', 'Voice of God-King', 'Age of Sigmar'),
    ('Flintlock Pistols', 'Ardcoat', 'Anto-Wizard Flintlock', 'Age of Sigmar'),
    ('Fyrestorm Greataxe', "Kragg Blackhammer's Master Rune", 'Zangrom-Thaz', 'Age of Sigmar'),
    ('Stormcharged Warhammer', 'Tactical Rock', 'Uskavar the Sunderer', 'Age of Sigmar'),
    ('Twin-Tailed Cat', 'Golden Demon', 'Enchanted Glove', 'Age of Sigmar'),
    ('Blade of the High Heavens', 'Figure Case', 'Thengavar', 'Age of Sigmar'),
    ('Poisoned Throwing Knives', 'Gauntlet', 'Bladed Vortex', 'Age of Sigmar'),
    ('Mystical Ward', 'Glue', 'Warding Lantern', 'Age of Sigmar'),
]

def link(url, label):
    return f'<a href="{url}" target="_blank" rel="noopener noreferrer">{label} ↗<span class="sr-only"> (opens in a new tab)</span></a>'

def apply(route, text):
    # The evolution title's obsolete demo scope has a recorded launch exception.
    if route.endswith('/evolutions/'):
        text = text.replace('Warhammer Survivors Evolutions: October Demo Recipes', 'Warhammer Survivors Evolutions: Launch Recipe List')
        text = text.replace('Find 11 reported Warhammer Survivors weapon evolution recipes, match a companion to your universe, and check upgrade, chest and old-demo differences.', 'Find 36 reported Warhammer Survivors weapon evolution recipes, filter by universe or companion, and check launch additions against older demo reports.')
    text = text.replace('WARHAMMER SURVIVORS · OCTOBER DEMO / PRE-RELEASE', 'WARHAMMER SURVIVORS · RELEASED 10 NOVEMBER 2026')
    text = text.replace('WARHAMMER SURVIVORS · PRE-RELEASE GUIDE', 'WARHAMMER SURVIVORS · LAUNCH GUIDE')
    text = text.replace('Checked 8 November 2026', 'Checked 11 November 2026').replace('Checked 7 November 2026', 'Checked 11 November 2026')
    text = text.replace('Full game planned for 10 November', 'Full game released 10 November 2026').replace('Full release planned for 10 November', 'Released 10 November 2026')
    text = text.replace('href="/" class="brand"', 'href="/warhammer-survivors/" class="brand"')
    text = text.replace('class="brand" href="/"', 'class="brand" href="/warhammer-survivors/"')
    text = text.replace('<span>Megabonk.org<small>Independent games &amp; guides</small></span>', '<span>Warhammer Survivors<small>Guides &amp; weapon evolutions</small></span>')
    if route == '/warhammer-survivors/':
        text = text.replace('The full game is planned for 10 November 2026.', 'Warhammer Survivors released on 10 November 2026.')
        text = text.replace('Try the current PC demo, check your Game Pass access, or use the October-demo evolution guide to plan your next run.', 'Choose your storefront, check existing Game Pass access, or find a weapon and its companion in the updated evolution guide.')
        text = text.replace('Try it before launch', 'Choose demo or full game').replace('If you want permanent launch progress, wait for the full release because demo unlocks do not transfer.', 'Start in the full game for permanent progress. Demo unlocks do not transfer.')
        text = text.replace('The developer gives <strong>10 November 2026</strong> as the full launch date. As of this check on 8 November, the demo is the playable pre-release reference.', 'The developer confirms the full game launched on <strong>10 November 2026</strong>.')
        text = text.replace('Other announced storefronts and platforms include', 'The released platform list includes')
        text = text.replace('Solo combat.','Solo combat.')
        extra = f'''<section id="ios"><h2>iPhone and iPad purchase checks</h2><p>The developer-linked App Store listing is by <strong>Auroch Digital Ltd</strong>. The US listing showed <strong>$7.19</strong> on 11 November, alongside the developer's $7.99 base price and platform-dependent launch discount. Check your local storefront price before purchase. {link(APPLE, 'Apple App Store listing')}</p><ol><li>Open the listing on the device you plan to use.</li><li>Expand Compatibility and compare its iOS or iPadOS requirement with Settings → General → About. The current listing requires version 15.0 or later.</li><li>Confirm that your device and store region offer the purchase, then check available storage and the current download size.</li></ol><p>Apple lists iPhone and iPad support. Cross-store save transfer and device-specific performance have not been verified here. If continuing a PC save is essential, confirm that support before buying a second copy.</p></section><section id="tor-garadon"><h2>Tor Garadon unlock check</h2><p>Arka Sarkar's launch guide reports <strong>10,000 enemies defeated across multiple runs</strong> as Tor Garadon's unlock condition. Check the 40K Objectives entry and cumulative progress between runs. A single-run kill target would lead you to spend effort on a different task. The guide does not provide a recommended Tor build or a precise claim about which other modes contribute. {link(CHARACTERS, 'Destructoid character unlock report, 10 November')}</p></section><section id="launch-help"><h2>Launch issues with confirmed next steps</h2><p>After seeing the first chest of each rarity, the developer says you can skip that rarity's animation using right-click, Esc or gamepad B. On Switch 2 with a Switch Pro Controller, use the joystick if menu d-pad input fails. These checks address the two symptoms documented in the 10 November FAQ. For the separate Failed to load il2cpp error, consult the developer's current instructions and report form before changing Windows security settings. {link(FAQ, 'Official known issues and reporting form')}</p></section>'''
        text = text.replace('<p><a href="#guide">Back to top', extra+'<p><a href="#guide">Back to top')
        text = text.replace('before launch.', 'in the demo.')
    elif route.endswith('/co-op/'):
        text = text.replace('As checked on 7 November 2026, the full game is still scheduled for 10 November; the available demo is not proof of a later multiplayer mode.', 'As checked on 11 November 2026, the game has launched and the official FAQ continues to describe a single-player experience.')
    elif route.endswith('/evolutions/'):
        rows = ''.join('<tr>'+''.join('<td>'+escape(cell)+'</td>' for cell in row)+'</tr>' for row in ADDITIONS)
        text = text.replace('</tbody>', rows+'</tbody>', 1)
        text = text.replace('The October demo has 11 unique community-reported pairings below.', 'The table now includes 36 unique reported pairings, with launch additions and older demo evidence identified below.')
        text = text.replace('11 reported recipes</p>', '36 reported recipes</p>')
        text = text.replace('in your current run to the October table', 'in your current run to the relevant row')
        text = text.replace('Names and availability may change at full release.', 'The full game is now available. These older rows remain identified by their original evidence date.')
        text = text.replace('<form id="recipe-filter"', f'<p><strong>Launch additions checked 11 November.</strong> The additional 25 rows come from {link(EVOLUTIONS, "Arka Sarkar’s 10 November launch recipe report")}. These are reported recipes, rather than our playtest. The source reverses the Age of Sigmar column labels. We normalize those rows to weapon → companion → result and retain the earlier Tempest Axes pairing. Nuln Oil and D6 Dice are listed once each as Both. Confirm the entry against your current Armoury when a name differs.</p><form id="recipe-filter"')
        text = text.replace('The full game is planned for 10 November. Recheck demo recipes against its actual Armoury before using them as launch recipes.', 'The game released on 10 November. Use the launch rows for newly available weapons and check your current Armoury when an older demo instruction differs.')
    return text
