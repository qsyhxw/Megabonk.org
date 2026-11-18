"""PokéSurvivor guide pages rewritten to the v3.20 page formats (SOP 08, /xiufu 改写, 2026-11-16).

Facts follow the live game and the creator's own guides at pokesurvivor.com (read 16 Nov 2026:
/en/guide/, /en/upgrades/, /en/moves/, /en/bosses/, /en/legendaries/, /en/items/, /en/events/,
/en/news/ up to the 13-15 Nov updates) and screenshots captured from pokesurvivor.com the same day
(assets/poke-survivor/game/). Evidence and capture notes stay in FACT_CHECK.md / _private; pages show
answers only. apply(pages) replaces answer, parts and format of the matching rows built by
poke_survivor_content.make_pages(); URL, title and canonical stay (00 §5A), descriptions that promised
removed content are corrected and logged in ROADMAP PS-REWRITE.
"""
from html import escape
from poke_survivor_rules import load as load_rules, fill, long_date, clock

P = '/poke-survivor/'
G = '/assets/poke-survivor/game/'
SITE = 'https://pokesurvivor.com/en/'
RULES = load_rules()
UPDATED = long_date(max('2026-11-16', RULES['changed']))  # pages follow the last rule change
ORDINAL = ['First', 'Second', 'Third', 'Fourth', 'Fifth', 'Sixth', 'Seventh', 'Eighth', 'Ninth', 'Tenth']


def rift_table():
    r = RULES
    events = [(m, 'Calendar boss') for m in r['calendar_boss_minutes']] + [(r['eternatus_minute'], 'Eternatus'), (r['arceus_minute'], 'Judgment of Arceus')]
    rows, rifts = [], r['rift_minutes']
    for i, m in enumerate(rifts):
        last = i == len(rifts) - 1
        what = 'Catch-up rift: a bond only if you missed one' if last else ORDINAL[i] + ' legendary' + ('; afterwards some forms can be chosen (Deoxys, Rotom, Oricorio…)' if i == 2 else '')
        nxt = [f'{n} at {clock(t)}' for t, n in events if t > m][:2 if last or i == len(rifts) - 2 else 1]
        rows.append([clock(m), what, ', '.join(nxt)])
    return tbl(['Run time', 'Rift', 'Next on the clock'], rows)

IMG = {  # name: (width, height, alt)
    'gacha-notes': (592, 336, 'Gacha notes in PokéSurvivor: the ×10 pull guarantees at least one Epic, 70 pulls without a Legendary make the next one Legendary, and bosses and rift legendaries give ×10 tickets'),
    'run-end': (782, 400, 'End-of-run screen after 1:20 at level 8: 43 PokéCoins and 2 gacha tickets earned, Embers dealing all 2,812 damage while Double Team and Harden dealt none'),
    'menu': (1280, 800, 'PokéSurvivor main menu with Play, Gacha, Friends, Upgrades and the partner card for Scorbunny marked “Guest mode: not saved”'),
    'gacha': (976, 656, 'PokéSurvivor Kanto gacha with the four pull buttons (×10 for 10 tickets or one ×10 ticket, ×100 for 100 tickets or ten ×10 tickets) and the odds panel'),
    'upgrades': (976, 710, 'PokéSurvivor Upgrades screen for Scorbunny listing Vitality, Strength, Stride, Reflexes, Armor, Synthesis, Magnet, Wisdom, Fortune, Repertoire and their coin prices'),
    'levelup-physical': (616, 518, 'Level 3 card choice: Embers upgrade, Body Slam and Flame Charge marked Physical, and Heat Wave marked Special with the note that Scorbunny hits harder with physical moves'),
    'levelup-buffs': (616, 518, 'Level 4 card choice: Harden and Agility marked “deals no damage”, the Move Deleter card and a Sitrus Berry that restores 45% HP'),
    'levelup-weather': (616, 518, 'Level 2 card choice: Embers +1 projectile, Explosion, Sunny Day (Fire ×1.5, Water ×0.5) and Quick Attack'),
    'run-hud': (1280, 800, 'A PokéSurvivor run at 0:52 in Shady Forest: Scorbunny at level 5 firing Embers, the HP bar top left and the two move slots at the bottom'),
    'controls': (636, 600, 'Settings → Controls on PC: two key boxes per action for Up, Down, Left, Right, Previous move (Q), Next move (E or Tab) and Move 1–4'),
    'friends-account': (926, 584, 'PokéSurvivor menu with the Friends tile and the message “Create an account to play with friends and appear on the leaderboard”'),
    'graphics': (636, 490, 'Settings → Graphics: Quality set to Auto with High, Medium and Low, Pokémon effects and Ground trails each set to All, Only my partner or None'),
    'graphics-language': (636, 490, 'Settings → Graphics with the Language row offering 简体中文 and 繁體中文, and the Quality options below'),
    'phone-rotate': (642, 374, 'PokéSurvivor on a phone held upright: the “Rotate your phone — PokéSurvivor is played in landscape” message'),
    'phone-landscape': (1100, 508, 'PokéSurvivor main menu on a phone in landscape, with Play, Gacha, Friends and the partner card'),
    'account': (636, 296, 'Settings → Account for a guest: “You’re playing as guest: your progress isn’t saved when you leave” with a Sign up or log in button'),
}


def fig(name, caption=''):
    w, h, alt = IMG[name]
    src = 'graphics' if name == 'graphics-language' else name
    cap = f'<figcaption>{caption}</figcaption>' if caption else ''
    return f'<figure class="game-shot"><img src="{G}{src}.webp" width="{w}" height="{h}" loading="lazy" decoding="async" alt="{escape(alt, quote=True)}">{cap}</figure>'


def tbl(head, rows):
    h = ''.join(f'<th scope="col">{x}</th>' for x in head)
    b = ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows)
    return f'<div class="table-wrap"><table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'


def a(slug, text):
    return f'<a href="{P}{slug}">{text}</a>'


def ol(items):
    return '<ol class="steps">' + ''.join(f'<li>{x}</li>' for x in items) + '</ol>'


def ul(items):
    return '<ul>' + ''.join(f'<li>{x}</li>' for x in items) + '</ul>'


GAME = f'<a href="{SITE}" rel="noopener">pokesurvivor.com</a>'

RUN_TABLE = tbl(['Run time', 'What happens', 'What to do'], [
    ['[[cal_clock]]', 'A calendar boss appears, tougher each time; enraged at half HP', 'Beat it: it always drops a held item and gives a ×10 ticket 1 time in 3'],
    ['[[rift_main_clock]]', 'A rift opens to a legendary’s arena', 'Go in: a win gives a ×10 ticket and a bond'],
    ['[[et]]:00', 'Eternamax Eternatus at the Top of the Tower', 'Pick up loot first; a win gives a power, a ×10 ticket and [[coins]] PokéCoins'],
    ['[[rift_last]]:00', 'Last rift', 'Gives a bond only if you missed an earlier one'],
    ['[[ar]]:00', 'Judgment of Arceus in the Hall of Origin', 'Survive and deal damage as long as you can'],
])

PAGES = {}

# ---------------------------------------------------------------- beginner guide (08 F8)
PAGES['beginners-guide/'] = dict(
    format='beginner', h1='PokéSurvivor beginner guide: your first run',
    answer=('Open pokesurvivor.com, pick a partner and keep moving: your active move fires on its own while you dodge. '
            'Take one card per level, decide on evolution at levels [[evo]], and spend PokéCoins on your main partner’s upgrades between runs. '
            'Sign up first if you want to keep your progress.'),
    lead=ol([
        f'Open {GAME} in a browser (turn a phone to landscape). Sign up or log in: guest progress is not saved when you leave.',
        'Answer the partner questions, then keep the suggested partner or press <strong>Change</strong>.',
        'Press <strong>Play</strong> on Normal. Move with WASD or the arrow keys; only the active move attacks.',
        'At every level, pick one of four cards: a new move, an upgrade for a move you have, or a boost.',
        'At levels [[evo]], choose to evolve your partner or keep its look; its stats rise either way.',
        'Beat the bosses at [[cal]] minutes and enter the rifts at [[rift_main]] minutes.',
        'After the run, buy Magnet, Vitality and Strength levels for the partner you will keep using.',
    ]),
    parts=[
        ('controls', 'Controls on PC, phone and controller',
         tbl(['Action', 'Keyboard', 'Phone (landscape)', 'Controller'], [
             ['Move', 'WASD or arrow keys', 'Drag anywhere; the joystick appears where you touch', 'Left stick or D-pad'],
             ['Choose the active move', '1–4, or Q / E (Tab) to cycle', 'Tap the move', 'LB / RB'],
             ['Use a Mystery Dungeon orb', '5–8', 'Tap the orb', 'X'],
             ['Power (after beating Eternatus)', 'F', 'Its own button', 'B'],
             ['Pause', 'Esc', 'Top-right button', 'Start'],
         ]) + '<p>Every key can be changed in <strong>Settings → Controls</strong>, with two keys per action; if another action already uses a key, they swap.</p>'
         + fig('controls')),
        ('cards', 'Which level-up card to take',
         '<p>Each card shows whether a move is <strong>Physical</strong> or <strong>Special</strong> and how well it fits your partner, for example “With Scorbunny it deals 84%: it hits harder with physical moves”. Take moves on your partner’s strong side.</p>'
         + fig('levelup-physical')
         + ul(['<strong>Levels 2–6:</strong> get a second damaging move on your strong side, then upgrade your main move.',
               '<strong>Max a move to level 5</strong> and take the upgrade card it asks for (Power, Vigor, Reflexes, Sprint…): a golden evolution card appears, such as Ember into Fire Blast or Bubble into Surf.',
               '<strong>Buffs deal no damage</strong> (Harden, Agility, Swords Dance, Nasty Plot): they work while they are the active move, so take them after your attacks are in place.',
               '<strong>Sitrus Berry</strong> restores 45% of your HP at once; <strong>Move Deleter</strong> swaps out a move you regret; <strong>Reroll</strong> (R) redraws the four cards.'])
         + '<p>The full move-by-move advice is in ' + a('builds/', 'the PokéSurvivor builds guide') + '.</p>'),
        ('run', 'What happens during a run',
         fig('run-hud') + RUN_TABLE
         + '<p>Before you travel to Eternatus or Arceus, collect the experience, coins and heals on the ground: they disappear when the boss arena loads. See '
         + a('rifts/', 'rifts and bonds') + ' and ' + a('arceus-judgment/', 'the Judgment of Arceus') + '.</p>'),
        ('upgrades', 'Your first permanent upgrades',
         '<p>Upgrades are bought with PokéCoins in the menu and belong to one Pokémon only, so put your coins into the partner you play most. Each level costs more than the last.</p>'
         + fig('upgrades')
         + tbl(['Buy', 'First level', 'Why'], [
             ['Magnet', '[[up:Magnet]]', '[[eff:Magnet]] range: more experience and coins every run'],
             ['Vitality', '[[up:Vitality]]', '[[eff:Vitality]] per level for early mistakes'],
             ['Stride', '[[up:Stride]]', '[[eff:Stride]] to outrun the horde'],
             ['Strength', '[[up:Strength]]', '[[eff:Strength]] on every move'],
             ['Repertoire', '[[up:Repertoire]]', 'Start every run with 2 moves'],
             ['Starting move', '[[up:Starting move]]', 'Choose which move you start with'],
         ])
         + '<p>The creator’s own tip: Repertoire and the move ban (Veto) change runs the most. Maxing every upgrade costs [[uptotal]] PokéCoins per Pokémon and makes it hit and endure about 1.3 times more, so good movement still matters most.</p>'),
        ('save', 'Keep your progress',
         '<p>The partner card in the menu says <strong>Guest mode: not saved</strong> until you sign in. With an account your game is saved online and you can continue on another computer or phone; coins and tickets from a run arrive when the run ends. '
         + a('save-and-sync/', 'Save and sync checks') + ' covers moving between devices.</p>' + fig('menu')),
    ])

# ---------------------------------------------------------------- builds (mechanics + concrete setups)
PAGES['builds/'] = dict(
    format='other', h1='PokéSurvivor builds: physical, special and bonds',
    desc='Build PokéSurvivor moves around your partner’s Attack or Special Attack, pick the matching buff, link moves with rift bonds and choose the upgrades and items that fit.',
    answer=('Build around your partner’s stronger attack stat. A physical attacker wants physical moves plus Swords Dance or Dragon Dance; '
            'a special attacker wants special moves plus Nasty Plot. The level-up card tells you which side fits: “With Scorbunny it deals 84%: it hits harder with physical moves.”'),
    parts=[
        ('stat', 'Physical or special: the one rule that decides a build',
         '<p>Physical moves hit with your Pokémon’s Attack and special moves with its Special Attack. Moves on the strong side hit at 100%; moves on the other side hit in proportion, so a Pokémon with 120 Attack and 60 Special Attack deals half damage with special moves. A move’s type (Fire, Psychic…) is separate from its physical or special category. Partners that start already evolved (Gallade, Lucario, Volcarona) fight with their first stage’s stats until level 40.</p>'
         + fig('levelup-physical')
         + tbl(['Your partner', 'Damaging moves', 'Buff to take', 'Skip'], [
             ['Physical (Attack higher)', 'Physical moves: Quick Attack, Body Slam, Flame Charge, Dragon Claw…', 'Swords Dance; Dragon Dance builds Attack faster', 'Nasty Plot and special moves'],
             ['Special (Special Attack higher)', 'Special moves: Confusion, Psybeam, Hyper Voice, Heat Wave, Dragon Breath…', 'Nasty Plot', 'Swords Dance, Dragon Dance and physical moves'],
             ['Either', '—', 'Agility (speed) or Harden (defence) when you need to survive', 'More than one buff before your attacks are set'],
         ]) + fig('run-end', 'The end-of-run table shows damage per move: two buffs picked too early dealt nothing.')),
        ('partners', 'Builds for popular partners',
         tbl(['Partner', 'Strong side', 'Build'], [
             ['Mewtwo', 'Special', 'Confusion and Psybeam, then Nasty Plot; ban physical moves'],
             ['Eternatus', 'Special', 'Special Dragon and Poison moves with Nasty Plot'],
             ['Keldeo', 'Special', 'Special Water moves first, Nasty Plot as the only buff'],
             ['Kartana', 'Physical', 'Physical Grass and Steel moves with Swords Dance'],
             ['Slaking', 'Physical', 'Body Slam and other physical melee moves with Swords Dance'],
             ['Scorbunny (starter)', 'Physical', 'Embers early, then Flame Charge and Quick Attack; the game marks Heat Wave at 84%'],
         ])
         + '<p>Older videos that pair Swords Dance with Mewtwo’s Psychic or Confusion come from before the physical/special split (18 October 2026); in the current game only Nasty Plot raises those moves.</p>'),
        ('bonds', 'Bonds: two moves from one slot',
         '<p>Every legendary you beat in a rift gives a bond: link two moves so they fire together from a single slot, up to four bonds. Rifts open at [[rift_main]] minutes; the minute-[[rift_last]] rift gives a bond only if you missed one, so the plan is to reach Eternatus with all [[rift_main_n]].</p>'
         + ul(['Bond your two strongest damaging moves of the same category first.',
               'Use the freed slots for a third and fourth attack before adding a buff.',
               'Win the rifts: losing sends you back to the map with no bond and no ticket. ' + a('rifts/', 'Rift arenas and rewards') + '.']))
        ,
        ('evolve', 'Evolve your main move',
         '<p>123 of the 176 moves can evolve. Raise the move to level 5, then take the upgrade card it asks for and a golden evolution card appears.</p>'
         + tbl(['Move', 'Needs', 'Evolved effect'], [
             ['Tackle (physical)', 'Vigor', '×1.9 damage, more range, hits in 360°'],
             ['Quick Attack (physical)', 'Sprint', '×1.9 damage, longer dash, shorter cooldown'],
             ['Body Slam (physical)', 'Power', '×1.9 damage, more range, hits in 360°'],
             ['Hyper Voice (special)', 'Reflexes', '+6 projectiles, ×1.6 damage, +1 pierce'],
             ['Confusion (special)', 'Reflexes', '×1.8 damage, +2 projectiles, +2 pierce'],
             ['Substitute (physical)', 'Armor', '×1.8 damage, one more decoy, fires faster'],
         ]) + fig('levelup-weather', 'Weather cards such as Sunny Day change type damage for every move you use.')),
        ('upgrades', 'Upgrades and items that shape a build',
         ul(['<strong>Repertoire</strong> ([[up:Repertoire]] PokéCoins): start with 2 moves; then <strong>Starting move</strong> and <strong>Second starting move</strong> ([[up:Starting move]] each) pick them.',
             '<strong>Ban / Veto</strong> (from [[up:Ban]]): block up to five moves you never want, such as every off-side move.',
             '<strong>Card reroll</strong> (from [[up:Card reroll]]): one more reroll per run, per level bought.',
             '<strong>Held items:</strong> Choice Band gives +40% damage but locks your move; Quick Claw cuts cooldowns by 20%; Leftovers heals 1.5% HP per second. Second item ([[up:Second item]]) and Third item ([[up:Third item]]) let you hold more at once.',
             '<strong>Taught the wrong TM?</strong> A Blank TM from the Kecleon Shop erases it.'])
         + fig('levelup-buffs', 'Buff cards say “deals no damage”; Move Deleter swaps a move out mid-run.')),
    ])

# ---------------------------------------------------------------- gacha
PAGES['gacha/'] = dict(
    format='other', h1='PokéSurvivor gacha: tickets, pull costs and pity',
    desc='How to get PokéSurvivor gacha tickets, what each pull button costs, the drop odds, the ×10 Epic guarantee and the 70-pull legendary pity per region.',
    answer=('A ten-pull costs 10 tickets or one ×10 ticket; a hundred-pull costs 100 tickets or ten ×10 tickets. Every ×10 pull guarantees at least one Epic, and after 70 pulls without a Legendary on a region’s banner the next one is Legendary. '
            'You earn tickets by playing: defeated Pokémon drop them now and then, and bosses, rift legendaries and the weekly challenge give ×10 tickets.'),
    parts=[
        ('costs', 'Pull buttons and costs',
         tbl(['Button', 'Pays with', 'Results'], [
             ['Pull ×10 · 10', '10 tickets', '10 Pokémon'],
             ['Pull ×10 · 1', '1 ×10 ticket', '10 Pokémon'],
             ['Pull ×100 · 100', '100 tickets', '100 Pokémon'],
             ['Pull ×100 · 10', '10 ×10 tickets', '100 Pokémon'],
         ]) + '<p>Tickets and ×10 tickets are two separate balances shown at the top of the screen: 9 tickets plus one ×10 ticket does not pay for the first button.</p>'
         + fig('gacha')),
        ('earn', 'How to get tickets',
         tbl(['Source', 'Reward'], [
             ['Defeated wild Pokémon', 'A ticket now and then'],
             ['Calendar bosses ([[cal_list]] min)', 'A ×10 ticket 1 time in 3, plus a held item'],
             ['Rift legendary win ([[rift_main_list]] min)', 'A ×10 ticket and a bond'],
             ['Eternamax Eternatus win ([[et]] min)', 'A ×10 ticket and [[coins]] PokéCoins'],
             ['Weekly challenge', 'A ×10 ticket if you last 3 minutes (one attempt a week)'],
             ['Coin thief event', 'A Gholdengo carries a ×10 ticket 1 time in 4'],
             ['Lost Pokémon event', 'One ticket'],
             ['Hard / Nightmare difficulty', '×1.5 / ×2 coins and tickets'],
         ]) + fig('run-end', 'Even a short run pays out: this 1:20 run earned 2 tickets.') + '<p>Tickets cannot be bought with real money. Tickets you pick up in a run are saved when the run ends; if the game closes halfway, you get them when you come back.</p>'),
        ('odds', 'Odds and guarantees',
         tbl(['Rarity', 'Chance (Kanto)'], [['Legendary', '1.5%'], ['Epic', '6.5%'], ['Rare', '17%'], ['Uncommon', '30%'], ['Common', '45%'], ['Shiny', '1%']])
         + ul(['Each ×10 pull guarantees at least one Epic.',
               'The legendary counter is per region: “Pulls without a legendary in Kanto: 0 / 70”. Switching regions does not carry it over.',
               'Duplicates turn into PokéCoins; shinies never repeat.',
               'Every 10 ×10 pulls on a region give an egg that hatches in the Bag.'])),
        ('plan', 'How to spend tickets',
         ul(['Choose the region whose legendary or Pokémon you want and stay on it until its 70-pull counter pays out.',
             'Save ×10 tickets and use the ×10 button so every ten results include the Epic guarantee.',
             'With an account, the gacha needs a connection; the 15 November update fixed balances that showed tickets you did not have.',
             'Spend duplicate PokéCoins on ' + a('beginners-guide/#upgrades', 'upgrades for your main partner') + '.'])),
    ])

# ---------------------------------------------------------------- rifts
PAGES['rifts/'] = dict(
    format='other', h1='PokéSurvivor rifts: times, arenas and bonds',
    desc='When PokéSurvivor rifts open ([[rift_all]] minutes), the 18 legendary arenas, and what a win gives: a ×10 ticket, a bond and a held item.',
    answer=('Rifts open at [[rift_all]] minutes of a run. Step in to fight a legendary in an arena of its type: a win gives a ×10 ticket, a bond that links two moves into one slot, and a held item; '
            'a loss sends you back to the map with nothing. The minute-[[rift_last]] rift only gives a bond if you missed an earlier one.'),
    parts=[
        ('times', 'When rifts open',
         rift_table() + '<p>In co-op everyone enters together. Legendaries you are missing in your collection show up more often.</p>'),
        ('arenas', 'The 18 arenas',
         tbl(['Type', 'Arena', 'Type', 'Arena'], [
             ['Normal', 'Eternal Meadow', 'Flying', 'Sky Peak'], ['Fire', 'Igneous Volcano', 'Psychic', 'Mind Temple'],
             ['Water', 'Sea Grotto', 'Bug', 'Hive Forest'], ['Grass', 'Emerald Jungle', 'Rock', 'Ancient Quarry'],
             ['Electric', 'Volt Plant', 'Ghost', 'Gloomy Graveyard'], ['Ice', 'Eternal Glacier', 'Dragon', 'Dragon Sanctuary'],
             ['Fighting', 'Ancient Dojo', 'Dark', 'Dark Alley'], ['Poison', 'Toxic Swamp', 'Steel', 'Steel Fortress'],
             ['Ground', 'Red Desert', 'Fairy', 'Enchanted Forest'],
         ]) + '<p>Dual-type legendaries pick one of their types for the arena. Terrain matters: lava burns, ice is slippery and water slows you. Legendaries fight in three phases with five moving attacks per type and an ultimate; since 15 November their whirlwinds (Gust, Whirlpool, Fire Spin) pull you in less.</p>'),
        ('win', 'How to win a rift',
         ul(['Bring a move that is super effective against the arena’s type; the weather in the arena also changes type damage.',
             'Keep moving in wide circles and step out of ground markers before they fill.',
             'Enter with full HP: take a Sitrus Berry card or heal before the 4- and 8-minute rifts if you can.',
             'Beat each legendary to collect all [[rift_main_n]] bonds before Eternatus; ' + a('builds/#bonds', 'which moves to bond') + '.'])),
        ('rewards', 'Rewards',
         tbl(['Result', 'You get'], [
             ['Win', 'A ×10 ticket, a bond, a held item; with an account, an egg that arrives when the run ends'],
             ['Lose', 'Back to the map with no reward; the run continues'],
         ]) + fig('gacha-notes') + '<p>Spend the ×10 tickets in ' + a('gacha/', 'the gacha') + '.</p>'),
    ])

# ---------------------------------------------------------------- Arceus
PAGES['arceus-judgment/'] = dict(
    format='other', h1='PokéSurvivor Judgment of Arceus: how to last longer',
    desc='How the PokéSurvivor Judgment of Arceus works at minute [[ar]]: its attacks by time, the items it breaks, how fast it chases you and how to score more time and damage.',
    answer=('At minute [[ar]] Arceus takes you to the Hall of Origin. It cannot be beaten: your score is how long you last and how much damage you deal. '
            'It breaks one held item at [[brk]] minutes, ignores Protect, Sturdy and Focus Sash, and is faster than you after 3 minutes; lasting 10 minutes (about [[ar10]]:00 of run time) is a top result.'),
    parts=[
        ('before', 'Before minute [[ar]]',
         ul(['Beat Eternamax Eternatus at [[et]]:00 for a power (Mega Evolution, Dynamax, Z-Ring or Terastal).',
             'Collect every bit of experience, coins and heals on the ground before [[ar]]:00: it disappears when you travel.',
             'Amulet Coin, Exp. Charm and Luck Incense still pay out at the end even if Arceus breaks them.',
             'On Normal the Judgment is unchanged; only the earlier part of the run is easier.'])),
        ('attacks', 'Arceus’s attacks by time',
         tbl(['From', 'Attack', 'What to do'], [
             ['0:00', 'Judgment: pillars of light on everyone', 'Step out of the circles'],
             ['0:00', 'Holy Cross: cross-shaped beams to the edge (8 from 0:30)', 'Stand between the arms'],
             ['0:00', 'Divine Wave around Arceus', 'Do not stay next to it'],
             ['0:30', 'Extreme Speed across a marked lane', 'Leave the lane when it is marked'],
             ['1:00', 'Future Sight explodes where you just were', 'Do not retrace your steps'],
             ['1:30', 'Gravity: 4 s at 60% speed, no dash; Arceus stays still while it lasts', 'Move away from it while it cannot chase you'],
             ['2:00', 'Hyper Beam: 16 beams sweep a quarter of the arena', 'Move to the open quarter'],
             ['2:30', 'Plate Judgment: bullets of every type', 'Weave through the gaps'],
             ['5:00 / 7:00', 'Golden Wheels race around a lane near the edge, then a second lane further in', 'Cross through the gaps; a hit takes 35% HP'],
         ])),
        ('rules', 'Rules that end most Judgments',
         tbl(['Rule', 'Detail'], [
             ['Speed', 'Matches your speed after 1 minute, faster than you at 3, 140% of your speed at 10'],
             ['Touch', 'Takes [[touch]]% of your HP; from 10 minutes it knocks you out'],
             ['Items', 'Breaks one held item at [[brk]] minutes (and at 8 if you hold a fourth)'],
             ['Damage', 'Ignores types; damage reduction from Armor, items and upgrades cuts its attacks by at most 30% (only with the 80% maximum); Protect, Sturdy and Focus Sash do not work'],
             ['Floor', 'Every 4 s a chunk cracks and falls, up to 30% of the floor; standing on it hurts'],
             ['Chasing', 'Run far and it appears in front of you; three jumps in 45 s break the move you flee with'],
             ['Co-op', 'The first fall can be revived; a second fall means you are judged and out'],
         ])),
        ('score', 'Score more time or more damage',
         tbl(['Goal', 'Bring', 'Why'], [
             ['Last longer', 'Stride, Vitality and Armor upgrades, Agility, healing such as Leftovers', 'Arceus outruns you after 3 minutes and its touch takes [[touch]]%'],
             ['Deal more damage', 'Your strongest evolved moves on your strong side, Critical Hit and Power Crits', 'Damage to Arceus counts in full on the ranking; level-up cards such as Power and Brutal Blow have no limit, but hitting Arceus does not heal you'],
         ]) + '<p>Arceus holds a random Plate that sets its type for the Judgment, announced when you enter. The ranking counts both time survived and damage dealt. At Halloween the witch Gengar takes Arceus’s place. Builds for each side: ' + a('builds/', 'physical and special builds') + '.</p>'),
    ])

# ---------------------------------------------------------------- mobile (08 F7)
PAGES['mobile/'] = dict(
    format='platform', h1='PokéSurvivor on mobile: Android, iPhone and app',
    desc='Play PokéSurvivor on Android or iPhone in the browser, held in landscape, with no APK: add it to your home screen, keep saves with an account and fix touch and battery settings.',
    answer=('Play in your phone’s browser at pokesurvivor.com, held in landscape; you do not need an APK. For an app icon use “Add to Home Screen”. '
            'Sign up to keep your progress: guest progress is not saved when you leave.'),
    lead=tbl(['Way to play', 'Where', 'Saves', 'Co-op and rankings'], [
        ['Phone browser (recommended)', GAME, 'Online with an account', 'Yes'],
        ['Home-screen app', 'Browser menu → Add to Home Screen', 'Same account as the browser', 'Yes'],
        ['Offline download', '<a href="https://jpter78.itch.io/pokesurvivor" rel="noopener">itch.io</a>: unzip and open index.html', 'Only in that browser', 'No, solo only'],
        ['Native ports (e.g. Poke Survivors by JayElDragon)', 'Third-party builds', 'Separate from pokesurvivor.com', 'Separate'],
    ]),
    parts=[
        ('landscape', 'Hold the phone sideways',
         '<p>On an upright phone the game only shows a “Rotate your phone” message; turn it to landscape and the menu appears.</p>'
         + fig('phone-rotate') + fig('phone-landscape')),
        ('touch', 'Touch controls',
         ul(['Put a finger anywhere and drag to move; the joystick appears where you touch.',
             'Tap a move icon to make it the active move, or an orb to use it.',
             'Pause with the top-right button; after beating Eternatus your power has its own button.',
             'Settings → Controls also lists controller buttons if you connect one.'])
         + '<p>Android and iPhone use the same browser game and the same account.</p>'),
        ('performance', 'Smoother play and less battery',
         fig('graphics')
         + ul(['Settings → Graphics → <strong>Quality: Low</strong> (or Auto, which lowers it when the game stutters).',
               '<strong>Pokémon effects</strong> and <strong>Ground trails</strong>: “Only my partner” or “None” in big fights.',
               '<strong>FPS limit</strong> 60 or 30: the game runs just as fast and the phone stays cooler.',
               'Close other tabs; if moves stop responding, see ' + a('troubleshooting/', 'freezes and lag') + '.'])),
        ('safe', 'Downloads to avoid',
         '<p>PokéSurvivor is free, with no ads or purchases, and the only official website is pokesurvivor.com; the game itself says that anyone asking you to pay is not the creator. An APK from another site is not the creator’s app, and its saves and rules can differ. Moving progress between devices: ' + a('save-and-sync/', 'save and sync checks') + '.</p>'),
    ])

# ---------------------------------------------------------------- save and sync (08 F6)
PAGES['save-and-sync/'] = dict(
    format='fix', h1='PokéSurvivor save and sync: keep your progress',
    desc='Fix missing PokéSurvivor progress: why guest progress is lost, how account saves and runs sync between devices, and what to do when coins, tickets or eggs seem missing.',
    answer='Progress is only kept with an account. If the menu says “Guest mode: not saved”, sign up before you close the game; then log in with the same account on any other device.',
    lead=ol([
        'Look at the partner card in the menu: “Guest mode: not saved” means nothing is kept when you leave. Press <strong>Sign up or log in</strong> now.',
        'Finish the current run normally: coins and tickets from a run arrive when it ends.',
        'On the second device, open pokesurvivor.com and log in with the same name or Google account.',
        'Compare the Pokémon count (for example 1 / 1082) and coins before buying anything.',
        'Stay online while you buy upgrades, pull the gacha or hatch eggs: with an account these need a connection.',
    ]),
    parts=[
        ('symptoms', 'Missing progress: cause and fix',
         tbl(['What you see', 'Likely cause', 'Fix'], [
             ['Everything gone after closing the tab', 'You played as guest', 'Guest progress cannot be recovered; sign up before your next run'],
             ['Old collection on another device', 'Different account, not logged in, or the run was not finished', 'Log in with the same account and finish runs before switching'],
             ['Tickets from a run missing', 'The game closed mid-run', 'They arrive when you come back (since 14 November)'],
             ['Coins came back after buying', 'A purchase was still saving (fixed 15 November)', 'Reload once; purchases now stick'],
             ['Egg from a rift not in the Bag', 'Rift eggs arrive when the run ends', 'Finish the run, then open the Bag'],
             ['Offline download progress not online', 'The itch.io copy saves only in that browser', 'Play online at pokesurvivor.com to use an account'],
             ['Play-page progress not on pokesurvivor.com', 'Our ' + a('play/', 'Play page') + ' loads a third-party edition (pokesurvivor.pro)', 'Use one site for your main progress'],
         ]) + fig('account')),
        ('account', 'Protect your account',
         ul(['Link a Gmail account when the game asks “Afraid of losing your account?”, so you can log in with Google if you forget your password.',
             'The login panel has a “Forgot your password?” link.',
             'Do not play the same account in two tabs while buying; the 14 November update fixed items lost that way.',
             'Never share your password; the creator will not ask you to pay.'])
         + fig('menu')),
    ])

# ---------------------------------------------------------------- multiplayer (08 F7)
PAGES['multiplayer/'] = dict(
    format='platform', h1='PokéSurvivor multiplayer: co-op with friends',
    desc='Play PokéSurvivor co-op with up to [[coop]] friends: account requirement, adding friends and rooms, co-op rules for rifts, bosses and Arceus, and fixing lag with the ping display.',
    answer=('Yes: PokéSurvivor has online co-op for up to [[coop]] players. Everyone needs an account on pokesurvivor.com; add friends in the Friends menu, '
            'invite them to a room and the host starts the run. A downed teammate can be revived.'),
    lead=tbl(['Mode', 'Players', 'Account', 'Notes'], [
        ['Co-op room', 'Up to 4', 'Required for everyone', 'Shared run; revive fallen teammates'],
        ['Solo run', '1', 'Optional (guest not saved)', 'Team Rocket casino appears only solo'],
        ['Weekly challenge', '1', '—', 'Same map and Pokémon for everyone, one attempt a week'],
        ['Offline download', '1', '—', 'No co-op'],
    ]),
    parts=[
        ('join', 'Start a co-op run',
         ol(['Each player signs up on pokesurvivor.com (guests see “Create an account to play with friends”).',
             'Open <strong>Friends</strong> and add each other.',
             'The host creates a room and invites; wait until everyone is in the room.',
             'The host starts the run. If you go down, you can watch a standing teammate (Q / E) while you wait to be revived; after the run, “Play again” keeps the room together.'])
         + fig('friends-account')),
        ('rules', 'How co-op changes a run',
         tbl(['Moment', 'In co-op'], [
             ['Rifts', 'Everyone enters together'],
             ['Eternatus (20:00)', 'You can revive each other; solo, a fall ends the run'],
             ['Judgment of Arceus', 'The first fall can be revived; a second fall means you are judged and out'],
             ['Munchlax event', 'Its gift appears at each player’s feet, one each'],
             ['Upgrades', 'Everyone brings their own Pokémon’s upgrades'],
         ])),
        ('lag', 'Fix lag and stuck rooms',
         fig('graphics')
         + ul(['Turn on <strong>Settings → Graphics → Show ping</strong>: green below 100 ms, yellow up to 200 ms, red above. The player with the best connection should host.',
               'Lower Quality and set Pokémon effects to “Only my partner” if everyone stutters in big fights.',
               'If the host switches tabs or stops responding, the others wait 30 seconds; after that the host passes to another player and the run goes on. Keep the game tab in front. If you yourself are away longer than the group waits (about one minute), your run ends with what you had; rewards earned while the game is hidden, locked or offline go to the group, not to you.',
               'A host leaving after everyone picked a card no longer freezes the run, and “X is choosing…” stuck screens were fixed on 14 November: reload once if you still see one. Since 18 November, co-op no longer shows “reconnecting…” forever after a host change.',
               'More fixes: ' + a('troubleshooting/', 'loading, freezes and lag') + '.'])),
    ])

# ---------------------------------------------------------------- troubleshooting (08 F6)
PAGES['troubleshooting/'] = dict(
    format='fix', h1='PokéSurvivor not working: freezes, lag and loading',
    desc='Fix PokéSurvivor not loading, freezing or lagging: graphics settings that cut stutter, phone orientation, co-op ping, and what to try when a run or room gets stuck.',
    answer='Most stutter and freezes go away with lower graphics settings. Reload pokesurvivor.com in its own tab, then set Quality to Low and Pokémon effects to “Only my partner”.',
    lead=ol([
        'Open pokesurvivor.com in its own browser tab and wait for the title screen.',
        'Settings → Graphics: set <strong>Quality</strong> to Low (or Auto), <strong>Pokémon effects</strong> and <strong>Ground trails</strong> to “Only my partner”.',
        'Turn on <strong>Show FPS</strong>; in co-op also <strong>Show ping</strong> to see whether it is your device or the connection.',
        'On a phone, hold it in landscape, close other tabs and set an FPS limit of 60 or 30.',
        'If a run is stuck on a choice screen, reload: progress from finished runs is saved with an account.',
    ]),
    parts=[
        ('symptoms', 'Symptom, cause and fix',
         tbl(['Symptom', 'Likely cause', 'Fix'], [
             ['Black or blank screen', 'Page still loading or blocked', 'Reload in its own tab; disable extensions that block scripts'],
             ['Only “Rotate your phone” shows', 'Phone held upright', 'Turn the phone to landscape'],
             ['Menu works but you cannot move', 'Changed key bindings or touch outside the game', 'Settings → Controls; drag inside the game area'],
             ['Stutter in big fights, bosses or Arceus', 'Too many effects and particles', 'Quality Low, effects “Only my partner”, trails “None”'],
             ['Phone gets hot, battery drains', 'Uncapped frame rate', 'FPS limit 60 or 30'],
             ['Only co-op is slow', 'Host connection', 'Show ping; let the player with green ping host'],
             ['Co-op paused for everyone', 'The host switched tabs or lost connection', 'Keep the game tab in front; after 30 seconds the host passes to another player'],
             ['Enemies freeze at the screen edge', 'Very unusual window shape', 'Return the window to a normal size'],
         ]) + fig('graphics')),
        ('stuck', 'Stuck runs and rooms',
         ul(['“X is choosing…” forever in co-op: fixed 14 November; reload if it still happens.',
             'The host left mid-run: the run now continues for the others.',
             'Tickets from a run that closed halfway arrive when you come back.',
             'Saves and missing progress: ' + a('save-and-sync/', 'save and sync checks') + '; co-op setup: ' + a('multiplayer/', 'friends and co-op') + '.'])
         + fig('run-hud')),
        ('report', 'Report a bug to the creator',
         '<p>Use the Support and Discord links inside the game menu at ' + GAME + '. Give your browser and device, the run time on the screen and what you pressed just before the problem.</p>'),
    ])

# ---------------------------------------------------------------- Spanish mobile
PAGES['es/mobile/'] = dict(
    format='platform', h1='PokéSurvivor en móvil: jugar y descargar',
    answer=('Juega en el navegador del móvil en pokesurvivor.com, en horizontal; no necesitas APK. Para tener un icono usa «Añadir a pantalla de inicio». '
            'Crea una cuenta para guardar: el progreso de invitado no se guarda al salir.'),
    lead=tbl(['Forma de jugar', 'Dónde', 'Guardado', 'Cooperativo'], [
        ['Navegador del móvil (recomendado)', GAME, 'En línea con cuenta', 'Sí'],
        ['App en pantalla de inicio', 'Menú del navegador → Añadir a pantalla de inicio', 'La misma cuenta', 'Sí'],
        ['Descarga sin conexión', '<a href="https://jpter78.itch.io/pokesurvivor" rel="noopener">itch.io</a>: descomprime y abre index.html', 'Solo en ese navegador', 'No'],
        ['Ports nativos (p. ej. Poke Survivors de JayElDragon)', 'Versiones de terceros', 'Aparte de pokesurvivor.com', 'Aparte'],
    ]),
    parts=[
        ('horizontal', 'Gira el móvil',
         '<p>Con el móvil en vertical solo aparece «Rotate your phone»; gíralo a horizontal y verás el menú.</p>' + fig('phone-rotate') + fig('phone-landscape')),
        ('controles', 'Controles táctiles',
         ul(['Pon el dedo en cualquier sitio y arrastra para moverte; el joystick aparece donde tocas.',
             'Toca un movimiento para activarlo o un orbe para usarlo.',
             'Pausa con el botón de arriba a la derecha.',
             'El juego también admite mando: revisa Ajustes → Controles.'])),
        ('rendimiento', 'Más fluido y menos batería',
         ul(['Ajustes → Gráficos → <strong>Calidad: Baja</strong> (o Auto).',
             '<strong>Efectos</strong> y <strong>rastros</strong>: «Solo mi compañero» o «Ninguno».',
             '<strong>Límite de FPS</strong> 60 o 30: el juego va igual de rápido y el móvil se calienta menos.'])
         + fig('graphics')),
        ('seguro', 'Descargas que evitar',
         '<p>PokéSurvivor es gratis, sin anuncios ni compras, y la única web oficial es pokesurvivor.com: si alguien te pide pagar, no es el creador. Un APK de otra web no es la app del creador y puede tener otro guardado y otras reglas. Guía en inglés: ' + a('mobile/', 'PokéSurvivor on mobile') + '.</p>'),
    ])

# ---------------------------------------------------------------- Chinese beginner guide
PAGES['zh/beginners-guide/'] = dict(
    format='beginner', h1='PokéSurvivor 中文入门攻略',
    answer='打开 pokesurvivor.com，在设置里把语言改成简体或繁体中文，选好伙伴后只管移动躲避：当前招式会自动攻击。每次升级选一张卡，[[evo1]] 级和 [[evo2]] 级可选择是否进化；想保留进度先注册账号，访客进度离开就会丢失。',
    lead=ol([
        f'打开 {GAME}，手机请横屏。点“Sign up / Log in”注册或登录；访客（Guest）进度不保存。',
        '回答几个性格问题，接受推荐伙伴，或点 <strong>Change</strong> 换一只。',
        '设置（右上角齿轮）→ Graphics → Language 选 简体中文 或 繁體中文，游戏会重新载入。',
        '点 <strong>Play</strong>，选 Normal。WASD 或方向键移动，1–4 或 Q/E 切换当前招式，Esc 暂停。',
        '每次升级从四张卡里选一张：新招式、已有招式升级，或属性加成。',
        '[[evo1]] 级和 [[evo2]] 级会问是否进化，不进化也会涨属性。',
        '结束后用 PokéCoins 在 Upgrades 里给主力伙伴买 Magnet、Vitality、Strength。',
    ]),
    parts=[
        ('language', '把游戏切换成中文',
         '<p>游戏自带 简体中文 和 繁體中文：设置 → Graphics 最上面的 Language 一栏，选好后游戏会重新载入，不需要第三方汉化。</p>' + fig('graphics-language')),
        ('controls', '操作',
         tbl(['操作', '键盘', '手机（横屏）', '手柄'], [
             ['移动', 'WASD 或方向键', '在任意位置拖动，摇杆出现在手指处', '左摇杆或十字键'],
             ['切换当前招式', '1–4，或 Q / E（Tab）', '点招式图标', 'LB / RB'],
             ['使用宝珠', '5–8', '点宝珠', 'X'],
             ['暂停', 'Esc', '右上角按钮', 'Start'],
         ]) + '<p>所有按键都能在 设置 → Controls 里改，每个动作可设两个键。</p>'),
        ('cards', '升级卡怎么选',
         '<p>卡片会标明招式是物理（Physical）还是特殊（Special），并提示与伙伴的契合度，例如“With Scorbunny it deals 84%: it hits harder with physical moves”。优先拿伙伴强项那一边的招式。</p>'
         + fig('levelup-physical')
         + ul(['前几级先拿第二个同侧伤害招式，再升级主力招式。',
               '招式升到 5 级并拿到它要求的属性卡（Power、Vigor、Reflexes、Sprint 等）后，会出现金色进化卡，例如 Ember 进化成 Fire Blast。',
               'Harden、Agility、Swords Dance、Nasty Plot 不造成伤害，只在作为当前招式时生效，等攻击招式成型后再拿。',
               '物理伙伴配 Swords Dance，特殊伙伴（如超梦 Mewtwo）配 Nasty Plot。详细构筑见 ' + a('builds/', '英文构筑指南') + '。'])),
        ('run', '一局里会发生什么',
         tbl(['时间', '事件', '做什么'], [
             ['[[cal_zh]] 分钟', '日历 Boss', '击败必掉道具，1/3 概率给 ×10 抽卡券'],
             ['[[rift_main_zh]] 分钟', '裂隙（传说宝可梦）', '获胜得 ×10 抽卡券和一个羁绊（Bond）'],
             ['[[et]] 分钟', '无极巨化 无极汰那', '获胜选一种力量（超级进化、极巨化等）'],
             ['[[rift_last]] 分钟', '最后一个裂隙', '只有错过之前的裂隙才给羁绊'],
             ['[[ar]] 分钟', '阿尔宙斯的审判', '无法击败，按存活时间和伤害计分'],
         ]) + fig('run-hud')),
        ('save', '保存进度',
         '<p>菜单伙伴卡上写着 “Guest mode: not saved” 时，关闭页面进度就会丢失。注册账号后进度保存在云端，可在其他电脑或手机登录继续；一局获得的金币和抽卡券在这局结束时到账。换设备前请看 ' + a('save-and-sync/', '存档与同步（英文）') + '。</p>'
         + fig('upgrades', 'Upgrades 里的永久升级只对当前这只宝可梦生效。')),
    ])


def apply(pages):
    """Replace the old evidence-led bodies with the v3.20 pages above."""
    for page in pages:
        new = PAGES.get(page['slug'])
        if not new:
            continue
        page['answer'] = fill(new['answer'], RULES)
        page['lead'] = fill(new.get('lead', ''), RULES)
        page['parts'] = [(i, fill(t, RULES), fill(b, RULES)) for i, t, b in new['parts']]
        page['sources'] = []
        page['diagram'] = None
        page['format'] = new['format']
        page['h1'] = new['h1']
        page['updated'] = UPDATED
        if new.get('desc'):
            page['desc'] = fill(new['desc'], RULES)
        page['language'] = page.get('language', '')
        import re
        first = re.search(r'/assets/poke-survivor/(game/[^"]+\.webp)', new.get('lead', '') + ''.join(x[2] for x in new['parts']))
        if first:
            page['image'] = first[1]
    return pages
