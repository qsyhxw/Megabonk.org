"""Attributed class tiers with dated mechanics and progression-aware advice."""
from azeroth_survivors_content import SOURCES, a, para, ref, steps, table

# The source author's written description supplies all nine placements. Advice is ours.
CLASSES = [
    ('S', 'Warrior', 'warrior', 'Fury spins',
     'The recurring Whirlwind route gives a concrete reason to consider Warrior for close-range wave fighting. The inspected Bladestorm capstone supplies the Whirlwind opener and recurring casts.',
     'The capstone is an unlock, so a fresh Warrior still needs to work with Cleave and the offers available. Keep a path out of the pack. A kill-triggered extra spin needs a kill.'),
    ('S', 'Warlock', 'warlock', 'Summons or DoT spread',
     'Warlock offers distinct summon and damage-over-time routes. An unlocked Imp supplies another attacker while you move. Affliction instead asks you to maintain effects and create the kills that spread them.',
     'Pick one engine before drafting for a distant capstone. Summon names and interactions changed after earlier snapshots, so inspect the dated Warlock guide and current tooltips before importing an old plan.'),
    ('S', 'Mage', 'mage', 'Developed Fire',
     'The source author specifically credits a geared Fire Mage Heroic V Naxxramas example for Mage’s move into S. Original Fire text links critical hits to free Pyroblasts and the capstone to Fire-kill explosions.',
     'The cited example is a developed character. A fresh Mage has neither its equipment nor its completed talent engine. Against a lone boss, evaluate the sustained attacks separately from explosions that require a kill.'),
    ('A', 'Hunter', 'hunter', 'Range and pets',
     'Hunter is worth comparing when you want ranged attacks with companion support. The inspected Tame Beast milestone adds a wolf, while Bestial Wrath adds a raptor later.',
     'A new Hunter does not begin with the complete pet pair. A Marksmanship plan prioritizing Aimed Shot and a pet plan are different routes, even though both share this class tier.'),
    ('A', 'Paladin', 'paladin', 'Holy or defensive routes',
     'Paladin’s recovery and defensive choices make it a useful alternative when mistakes end attempts. The Holy route has a milestone that changes the opening spell to Holy Shock and adds chained hits.',
     'Read the actual talent allocation before expecting that opener. Protection and Holy solve different problems. Choose the route that addresses your missing recovery or damage, rather than copying another character’s endgame equipment.'),
    ('A', 'Druid', 'druid', 'Ranged spells or one form',
     'Druid can answer very different playstyle goals. The inspected Balance text includes recurring Starfire, while Dire Bear adds a distinct close-range survival package with Swipe-based recovery.',
     'Cat and Dire Bear are mutually exclusive choices in the inspected text. An A-tier class label does not combine both forms with the full ranged tree. Open the route you actually intend to build.'),
    ('B', 'Rogue', 'rogue', 'Close-range bursts',
     'Rogue remains an option for players who want close-range finishers. The inspected Backstab capstone changes the starter and gives Backstab and Eviscerate splash around their target.',
     'That splash belongs to the unlocked route. Before it is available, judge the starter and actual card offers. Keep direct-hit damage and poison-death propagation separate when comparing a boss attempt with a dense wave.'),
    ('B', 'Shaman', 'shaman', 'Lightning coverage',
     'The inspected Elemental route has concrete repeat-cast and chain-coverage tools. Its capstone changes the opener to Chain Lightning and supplies a recurring second cast.',
     'A chain needs additional targets to realize its coverage. A totem setup and an Elemental lightning setup require different checks. Later Shaman changes also make the historical B placement a candidate for fresh testing.'),
    ('C', 'Priest', 'priest', 'Shields or spreading Shadow',
     'Priest offers shield-oriented choices and a Shadow route built around ongoing damage. The inspected Shadowform capstone spreads Shadow Word: Pain after an afflicted enemy dies.',
     'That death trigger contributes less when a single durable boss remains. C is this creator’s lower general recommendation, not a failed-clear verdict. If you prefer Priest, inspect the shield or Shadow route before abandoning existing progress.'),
]


def apply_tier_list(pages):
    SOURCES['tier_creator'] = (
        'https://www.youtube.com/watch?v=vsv5uk7I5Xo', 'YouTube · Rat Den Gaming ranking',
        'Published 28 October 2026; original author description read directly 5 November 2026. '
        'The description explicitly assigns all nine classes to S/A/B/C and attributes Mage’s rise to Zergs. '
        'Creator opinion and historical placements. No matched-condition test or original client build number supplied in that description. Video playback was not used as our own playtest.')
    SOURCES['tier_mage'] = (
        'https://www.youtube.com/watch?v=2kdXVbcuAhU', 'YouTube · Zergs Fire Mage example',
        'Author title and description read directly 5 November 2026. Describes Heroic 1–5 Naxxramas with a fully geared Fire Mage, cooldown/critical rings and Pyroblast, Fireball and Ice Barrier. '
        'Author-described example, not a controlled comparison with eight other classes or a run reproduced by this site.')
    SOURCES['tier_mechanics'] = (
        'https://wow.aethus.pl/', 'Aethus · original menu and talent text',
        'Original English v0.130.0 / e7d9dd47 snapshot, captured 30 October 2026, re-read for this guide on 5 November. '
        'Checks cover named talent conditions for all nine classes. Values left as runtime placeholders are omitted. '
        'Historical mechanic explanations do not revalidate the creator’s tiers on the latest original build. No community reconstruction combat values used.')
    for page in pages:
        if page['slug'] in ['best-class/', 'builds/']:
            page['parts'].insert(0, ('tier-list', 'Looking for a class tier list?', para(a('tier-list/', 'See all nine classes in the sourced tier list')+' for the dated S/A/B/C placements, progression limits and class-by-class trade-offs. '+('Use the finder below to choose for your own playstyle and unlocks.' if page['slug']=='best-class/' else 'Use this directory for the route inside the class you select.'))))
    board = table(['Tier', 'Classes', 'How to read the tier'], [
        ['S', a('tier-list/#warrior', 'Warrior')+' · '+a('tier-list/#warlock', 'Warlock')+' · '+a('tier-list/#mage', 'Mage'), 'The creator’s leading general recommendations. Mage’s cited evidence is a geared Fire example.'],
        ['A', a('tier-list/#hunter', 'Hunter')+' · '+a('tier-list/#paladin', 'Paladin')+' · '+a('tier-list/#druid', 'Druid'), 'Strong alternatives whose playstyle or defensive tools may fit your next attempt better.'],
        ['B', a('tier-list/#rogue', 'Rogue')+' · '+a('tier-list/#shaman', 'Shaman'), 'Lower general priority in this historical ranking; compare their unlocked engine and the encounter.'],
        ['C', a('tier-list/#priest', 'Priest'), 'The lowest placement in this source, with viable route choices still explained below.'],
    ])
    profiles = ''
    for tier, name, slug, route, why, limitation in CLASSES:
        profiles += '<section id="'+slug+'"><h3>'+tier+' · '+name+' — '+route+'</h3>'+para(why+' '+ref('tier_mechanics'))+para(limitation)+para(a('builds/'+slug+'/', name+' build routes'))+'</section>'
    pages.append(dict(
        id='TL01', slug='tier-list/', title='Azeroth Survivors Tier List: All 9 Classes & Builds',
        h1='Azeroth Survivors tier list: all nine classes',
        desc='See a sourced Azeroth Survivors class tier list, with all nine placements, beginner choices, build links and the limits of its dated community ranking.',
        review_note='Reviewed 5 November 2026 · Rat Den Gaming ranking dated 28 October · Original v0.130.0 mechanic notes · No matched-run benchmark',
        answer='Warrior, Warlock and Mage are S tier in Rat Den Gaming’s 28 October ranking. Hunter, Paladin and Druid are A; Rogue and Shaman are B; Priest is C. The board below preserves that creator’s dated opinion. Use the unlock and encounter checks before applying it to your character. '+ref('tier_creator'),
        parts=[
            ('rankings', 'Class tier list at a glance', board+para('Placements come directly from the source author’s written description, checked 5 November. Classes inside a tier have no strict order here. The source does not state an exact original-client build. These tiers have not been retested against the latest detected release. '+ref('tier_creator'))),
            ('beginners', 'Which class should a beginner choose?', para('Start by comparing Warrior for close-range play, Paladin for defensive choices and Hunter for range. These are our kit-based starting suggestions. Their unlocks and movement requirements matter more to a first character than a finished build’s letter. '+a('best-class/', 'Use the class finder')+ref('tier_mechanics'))+para('For example, Bladestorm’s recurring Whirlwind and Hunter’s second pet are talent outcomes. If you have not reached those talents, compare the attack and recovery you can use now. Spend an affordable point budget before copying a completed route. '+a('beginners-guide/', 'Follow the first-run steps'))),
            ('classes', 'Why consider each class?', para('The letters below repeat the creator’s ordering. The route explanations are our editorial reading of dated original-client text. They explain how to use a class choice, rather than claiming the text alone proves the ranking. '+ref('tier_creator')+ref('tier_mechanics'))+profiles),
            ('mage-example', 'Why does this source put Mage in S tier?', para('Rat Den Gaming’s description explicitly points to Zergs’s Fire Mage example for Mage’s promotion. Zergs labels that character fully geared and describes Heroic 1–5 Naxxramas, with a cooldown ring, a critical-chance ring and a Fire-focused spell setup. Those conditions are part of the example. '+ref('tier_creator')+ref('tier_mage'))+para('Treat it as a developed Fire route to investigate. It does not rank a fresh Frost Mage, establish a nine-class win rate or reproduce the same result with different equipment. '+a('builds/mage/', 'Compare Fire, Frost and Arcane'))),
            ('compare', 'Check these conditions before changing class', steps([
                'Match the game host, original-client version, zone and difficulty. Keep community rebuilds in a separate comparison.',
                'Record talent points and the actual opening spell. A capstone starter can change the first minutes of an attempt.',
                'Record gear, set bonuses and spell-specific jewelry. Keep a backup before moving progress to another client.',
                'Separate wave coverage from damage against one surviving boss. Kill effects and extra jumps need their stated conditions.',
                'Compare survival, clear time and repeated attempts at the same setup. One impressive damage window cannot supply a general class order.'
            ])+para('A new release number updates the game reference, but it does not automatically update these historical letters. A change to a defining talent or a new comparable run is a reason to review an affected placement. '+a('patch-notes/', 'Check source-change notes')+' · '+a('damage-meter/', 'Compare the right damage window'))),
            ('faq', 'Tier list questions', '<h3>Is tierlist different from tier list?</h3>'+para('Both spellings refer to the same class-ranking task on this page.')+'<h3>Is this an official Azeroth Survivors ranking?</h3>'+para('The placements are attributed to Rat Den Gaming’s dated community ranking. This site has not run a controlled nine-class benchmark. '+ref('tier_creator'))+'<h3>Should I reroll a B- or C-tier character?</h3>'+para('Check its missing talent engine, survival problem and current gear first. Retaining a developed character may suit your next attempt better than starting an S-tier character with fewer unlocks. Open the class route above to compare the choices.')+'<h3>Does this page rank items or every build?</h3>'+para('This board ranks classes in one source. '+a('builds/', 'Use the build directory')+' for talent routes and '+a('items/', 'compare jewelry by function')+' for run-item choices.'))
        ], related=[('best-class/', 'Choose a class for your progress'), ('builds/', 'Find the route inside your class'), ('heroic-difficulty/', 'Check the difficulty conditions')]))
    return pages


def home_tier_list(html):
    marker = '<section class="section" id="guides">'
    return html.replace(marker, marker+para(a('tier-list/', 'Class tier list: all nine placements and their source')), 1)
