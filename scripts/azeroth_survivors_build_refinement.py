"""Actionable build comparisons, edited 1 November; mechanics scoped to original 0.130.

Do not infer runtime rank values or turn these editorial priorities into DPS rankings.
"""
from azeroth_survivors_content import CLASSES, SOURCES, a, para, steps, table, ref


def p(text):
    return para(text + ref('build130'))


def link(slug, anchor, label):
    return a('builds/' + slug + '/#' + anchor, label)


def refine(pages):
    SOURCES['build130'] = (
        'https://wow.aethus.pl/', 'Aethus · original v0.130.0',
        'Original English client snapshot v0.130.0 / e7d9dd47, captured 30 October 2026 '
        '(resource stamp 98f593b6313e). Build, talent and jewelry descriptions re-read '
        'for this editorial revision on 1 November. Single primary source; not a new '
        'live-version check or completed-run test. Runtime rank placeholders remain omitted; '
        'spell priorities and pairings are editorial recommendations, not measured best-in-slot results.')
    for d in pages:
        slug = d['slug']
        if slug not in ['builds/', 'builds/mage/', 'builds/warlock/', 'talents/', 'items/']:
            continue
        d['review_note'] = ('Edited 1 November 2026 · New advice uses the original v0.130.0 snapshot '
                            'captured 30 October; earlier v0.127.0 sections remain scoped · Source-based, not a playtest')
        if slug == 'builds/':
            rows = []
            goals = {'warrior': 'Repeated melee hits or health/shield scaling',
                     'paladin': 'Shield retaliation or critical-triggered bursts',
                     'hunter': 'Aimed Shot or developed pets', 'rogue': 'Nearby hits, poison deaths or Backstab',
                     'priest': 'Shield recovery or spreading Shadow damage',
                     'druid': 'Repeated ranged spells or one melee form',
                     'mage': 'Fire kills, Frost control or Arcane repeat strikes',
                     'warlock': 'DoT spread, demons or direct spell interactions'}
            for k in ['warrior', 'paladin', 'hunter', 'rogue', 'priest', 'druid', 'mage', 'warlock']:
                c = CLASSES[k]
                routes = ' / '.join(r[0] for r in c['routes'])
                if k == 'warlock':
                    routes = 'Affliction / Demonology / Destruction'
                anchor = 'build-options' if k in ['mage', 'warlock'] else 'choose'
                rows.append([link(k, anchor, c['name']), c['start'], routes, goals[k]])
            rows.insert(5, [link('shaman', 'choose', 'Shaman'), 'Lightning Bolt',
                            'Elemental / Restoration', 'Repeated lightning or a developed totem route'])
            body = table(['Class', 'Default starter', 'Routes to compare', 'Choose by this engine'], rows)
            body += p('All nine classes are listed here. Mage includes Arcane; Warlock includes Destruction. '
                      'The table is a route index, not a performance ranking. Earlier eight-class guides retain '
                      'their v0.127.0 details; new Mage/Warlock advice and Shaman use the dated v0.130.0 evidence.')
            d['parts'] = [(i, 'All nine classes: choose a build route' if i == 'routes' else t,
                           body if i == 'routes' else b) for i, t, b in d['parts']]
            d['parts'].insert(1, ('quick-pick', 'Choose by progress and the run you want', table(
                ['Your situation', 'Start here', 'Next decision'], [
                    ['Fresh Mage, learning space control', link('mage', 'frost-plan', 'Frost preparation'),
                     'Use Fireball until a talent actually changes the starter; a planned elemental is not yet a summon.'],
                    ['Mage with a Fire engine already allocated', link('mage', 'fire-plan', 'Fire priorities'),
                     'Support Fire damage and critical triggers; judge isolated bosses separately from death explosions.'],
                    ['Warlock seeking spreading damage', link('warlock', 'affliction-plan', 'Affliction priorities'),
                     'Establish DoTs first, then check whether Contagion and Siphon Life are active.'],
                    ['Warlock building around direct spells', link('warlock', 'destruction-plan', 'Destruction priorities'),
                     'Read the Immolate-start milestone before drafting Shadow Bolt and Searing Pain support.'],
                    ['A developed summon character', link('warlock', 'demonology-plan', 'Demonology choices'),
                     'Choose the actual demon branch; mutually exclusive pets do not form one loadout.']]) +
                p('These are editorial starting decisions. For another class, use the nine-class table above. '
                  'A route name is not a point-by-point allocation. ' + a('talents/#budgets', 'Check what your point budget can reach'))))
        elif slug == 'builds/mage/':
            mage(d)
        elif slug == 'builds/warlock/':
            warlock(d)
        elif slug == 'talents/':
            d['parts'].insert(1, ('budgets', '10, 20, 30 and 51 points: a gate is not a purchase',
                table(['Total budget available', 'What that permits', 'What still needs checking'], [
                    ['10 points', 'Ten points spent in one tree can meet its first major-node gate.',
                     'The node itself needs another point. A 10-point total budget cannot buy an additional gated node.'],
                    ['20 points', 'Twenty spent in that tree can meet its next major gate.',
                     'Points spent in another tree do not meet this threshold; prerequisites may add restrictions.'],
                    ['30 points', 'Thirty spent in the tree can meet the capstone gate.',
                     'With no spare point, the capstone is still unallocated.'],
                    ['31–51 points', 'A 31-point total may reach a capstone if its path is legal.',
                     '51 is the total cap, not 51 per tree. Check rank limits, earlier nodes and exclusive choices.']]) +
                p('For example, 30 points in a tree plus its one-point capstone uses 31 of the 51-point maximum '
                  'and leaves up to 20 points for other choices. This arithmetic does not verify a particular allocation. '
                  'Use the actual game tree to confirm every spend; these guides do not supply a complete legal 51-point recipe.')))
            d['parts'].append(('route-checks', 'Apply the gate checks to a build', steps([
                'Choose the spell interaction you want, then inspect its named milestone in the game.',
                'Record your earned budget, points already in that tree, node rank and any predecessor.',
                'Check whether allocating it changes the starter. Read the picker again before entering.',
                'For Warlock summons, inspect exclusive pet choices before counting their benefits together.',
                'Use the remaining choices to fix the failure you actually see, rather than adding every school.']) +
                para(link('mage', 'build-options', 'Mage route plans') + ' · ' +
                     link('warlock', 'build-options', 'Warlock route plans'))))
        elif slug == 'items/':
            d['parts'].insert(1, ('build-pairings', 'Named jewelry to compare for your build',
                p('Use these names to inspect an actual offer. Effects below are paraphrased from the v0.130.0 '
                  'English snapshot; its rank-dependent percentages are placeholders, so read the displayed offer '
                  'for the value. The pairings are editorial suggestions, not drop guarantees or best-in-slot rankings.') +
                table(['Item', 'Described benefit', 'When to compare it'], [
                    ['Seal of the Damned', 'Faster damage-over-time ticks', 'An Affliction route already applying DoTs.'],
                    ['Quick Strike Ring', 'Shorter cooldowns', 'Repeated spells; check whether the talent already defines a separate fixed/free cast.'],
                    ["Master Dragonslayer's Ring", 'More critical strike chance', 'Fire or another route needing critical triggers.'],
                    ["Blackhand's Breadth", 'More critical strike damage', 'A route already generating critical hits; it does not supply critical chance.'],
                    ['Ring of Spell Power', 'More area of effect', 'Crowds and coverage; this is not proof of better single-target damage.'],
                    ["Blooddrinker's Band", 'Healing from damage dealt', 'Recovery when you can keep dealing damage; no damage means no healing from this effect.'],
                    ['Heavy Dark Iron Ring', 'More maximum health', 'A larger health buffer when damage alone is not the problem.']]) +
                p('Missing your preferred item? Keep the working build and compare the next offer by function: '
                  'repeat casts, coverage, critical triggers or survival. Do not take an unrelated legendary amulet '
                  'only for its rarity. ' + link('mage', 'gear-picks', 'Mage pairings') + ' · ' +
                  link('warlock', 'gear-picks', 'Warlock pairings'))))
    return pages


def mage(d):
    plans = [
        ('fire-plan', 'Fire: critical hits into kill explosions',
         'Choose this when Fire damage and critical-hit interactions are already available. Ignite and Hot Streak '
         'support the route; Pyroclasm changes the starter to Pyroblast. A new Fireball Mage does not yet have that endpoint.',
         ['Start with the Fire spell actually on the bar. With Pyroclasm allocated, support the Pyroblast opening.',
          'Prioritise Fire damage and critical-hit support that feeds the allocated talents. Do not add Frost solely to fill a slot.',
          'Use another Fire spell offered by the client when it supports the same plan. A specific card is not guaranteed.',
          'If crowds clear but a boss stalls, compare repeatable boss hits; explosions requiring kills need nearby victims.']),
        ('frost-plan', 'Frost: control first, elemental when unlocked',
         'Our editorial starting direction for a player wanting more space to move. Summon Water Elemental changes '
         'Fireball to Frostbolt and grants an elemental plus a periodic free Frost Nova. Until it is allocated, those effects are unavailable.',
         ['Before the capstone, keep the Fireball opening functional and take usable Frost control when offered.',
          'With the elemental allocated, support Frostbolt and the available Frost interactions. Read Frostbite and Splitting Ice in the tree.',
          'Compare health or coverage when contact is the failure. Control buys room; it is not a guarantee of safety.',
          'If the elemental is missing, inspect the allocation and starter before treating it as a broken summon.']),
        ('arcane-plan', 'Arcane: repeated spell strikes',
         'Choose Arcane when you want to develop Arcane Missiles and repeat-strike interactions. Arcane Power '
         'changes the starter to Arcane Missiles; Presence of Mind changes its missiles, while Arcane Concentration '
         'adds a free Arcane Explosion interaction.',
         ['Before Arcane Power, use the actual Fireball starter; take Arcane Missiles when offered if committing to this route.',
          'Support Missiles and the milestones already allocated. More missile effects and a chance to strike again are different benefits.',
          'After Arcane Power changes the opener, draft for the Arcane engine rather than waiting for a Fire starter.',
          'If the planned card never appears, strengthen an attack you have or take needed survival; a distant milestone cannot deal present damage.'])]
    d['parts'].insert(0, ('build-options', 'Mage builds at a glance',
        table(['Route', 'Choose it for', 'Starter check'], [
            ['<a href="#fire-plan">Fire</a>', 'Critical interactions and Fire-kill explosions', 'Pyroblast only after Pyroclasm.'],
            ['<a href="#frost-plan">Frost</a>', 'Space control and a developed elemental route', 'Frostbolt only after the starter-changing capstone.'],
            ['<a href="#arcane-plan">Arcane</a>', 'Missiles and repeat-strike interactions', 'Arcane Missiles after Arcane Power.']]) +
        p('For a fresh Mage, plan around Fireball. Choose Frost as a control-oriented direction if learning movement; '
          'choose Fire or Arcane for their respective triggers once available. These are conditional recommendations, not measured win-rate tiers.')))
    for offset, (i, title, intro, order) in enumerate(plans, 1):
        d['parts'].insert(offset, (i, title, p(intro) + steps(order) + para(ref('build130'))))
    d['parts'].insert(4, ('gear-picks', 'Race, jewelry and missing-item alternatives',
        p('Compare Gnome when shorter cooldowns and luck support your plan; its racial roots can also create space. '
          'Race availability depends on your unlocks. ' + a('best-race/', 'Check race access and alternatives')) +
        table(['Route or failure', 'Jewelry to inspect', 'If it is unavailable'], [
            ['Fire critical triggers', "Master Dragonslayer's Ring; Blackhand's Breadth", 'Compare chance and critical damage separately; keep survival if you cannot stay alive to cast.'],
            ['Repeated casts / Arcane', 'Quick Strike Ring', 'Keep an existing useful modifier; do not assume cooldown recovery speeds every separately timed talent proc.'],
            ['Frost coverage', 'Ring of Spell Power', 'Compare health if contact, rather than coverage, ends the run.'],
            ['Too little health buffer', 'Heavy Dark Iron Ring', 'Use another relevant defence or recovery offer instead of waiting for one named ring.']]) +
        p('Read the actual rank value. These items are optional pairings, not requirements for the route. '
          'Permanent equipment is a separate choice: inspect its bonuses and set threshold in the ' + a('armory/', 'Armory') +
          '. ' + a('items/#build-pairings', 'Compare item effects'))))
    d['parts'].append(('build-faq', 'Mage build questions',
        '<h3>Which Mage build is best for a beginner?</h3>' + para('Frost is our control-oriented starting direction. '
        'A new Mage still starts with Fireball; build toward Frost without assuming an unallocated elemental already exists.') +
        '<h3>Should I take every spell school?</h3>' + para('Choose offers that support the active route or fix a survival problem. '
        'An unrelated spell can consume a choice without strengthening the intended interaction.') +
        '<h3>Where should the remaining talent points go?</h3>' + para('Check earned points and legal prerequisites in the game, '
        'then address the observed failure. These route plans do not claim a verified optimal 51-point allocation. ' +
        a('talents/#budgets', 'Read the point-budget checks'))))


def warlock(d):
    d['parts'].insert(0, ('build-options', 'Warlock builds at a glance',
        table(['Route', 'Choose it for', 'Check before entering'], [
            ['<a href="#affliction-plan">Affliction</a>', 'DoT spread and conditional healing', 'Contagion / Siphon Life allocated; Corruption starter after Seed.'],
            ['<a href="#demonology-plan">Demonology</a>', 'A specific summon branch', 'Which demons are allocated and which exclude each other.'],
            ['<a href="#destruction-plan">Destruction</a>', 'Shadow Bolt / Immolate / Searing Pain interactions', 'Conflagrate changes the opening to Immolate.']]) +
        p('Start from Shadow Bolt on a fresh Warlock. Choose Affliction for spreading DoTs, Demonology for summons, '
          'or Destruction for linked direct spells. The strongest choice for every progression state has not been measured.')))
    plans = [
        ('affliction-plan', 'Affliction: establish DoTs before counting spread',
         ['With the default Shadow Bolt start, take usable Corruption or Curse of Agony when offered to establish the DoT engine.',
          'Aim toward Nightfall, Contagion, Siphon Life and Seed of Corruption, checking the actual gate and prerequisite before each purchase.',
          'Once Contagion is active, keep DoTs applied so deaths can pass them on. Do not expect spreading from an isolated target with no deaths.',
          'With Siphon Life active, DoT damage supplies healing. If it is not allocated, use available survival rather than assuming the route already heals.',
          'After Seed changes the starter to Corruption, draft around that opening. Against a lone boss, compare sustained damage rather than a chain-clear peak.']),
        ('demonology-plan', 'Demonology: choose the demon you can support',
         ['Inspect the summons actually allocated. Demonic Familiar, Soul Devourer and Soul Link describe different pet interactions.',
          'Choose between Soul Devourer and Soul Link; do not count the Felhunter and Voidwalker benefits together.',
          'For the developed Dread Lord branch, Searing Pain has an explicit link to Felseeker. Support that spell if this is the selected engine.',
          'If Butcher is selected instead, inspect the Felguard description. Do not assume the Dread Lord spell-scaling rule applies to it.',
          'If summon damage is working but you still die, take relevant recovery or defence before adding another disconnected attack.']),
        ('destruction-plan', 'Destruction: connect Immolate to direct hits',
         ['Before the starter-changing milestone, maintain the default Shadow Bolt attack. Shadow Cleave adds a fork interaction when allocated.',
          'Read Conflagrate before drafting: it starts the run with Immolate and makes Shadow Bolt or Searing Pain hits explode on Immolated targets.',
          'Support Immolate plus the direct spell that triggers the interaction. An unburning target does not satisfy the Immolated-target condition.',
          'Rain of Chaos supplies a second automatic Rain of Fire and slowing ground. This is a later talent benefit, not a free effect on a new Warlock.',
          'When a desired card is missing, strengthen the linked spell you have or take survival. Do not treat an unallocated Siphon Life as healing for this branch.'])]
    for offset, (i, title, order) in enumerate(plans, 1):
        d['parts'].insert(offset, (i, title, steps(order) + p('This is a priority framework for the dated original snapshot, '
            'not a guaranteed offer sequence or complete point allocation. ' + a('talents/#budgets', 'Check talent budgets and gates'))))
    d['parts'].insert(4, ('gear-picks', 'Race, jewelry and workable substitutes',
        p('Compare Gnome for shorter cooldowns and luck when repeated spells or the selected summon timer can benefit. '
          'Compare an available defensive race when survival is the constraint; changing race is not required to start a route. ' +
          a('best-race/', 'Read race benefits and unlocks')) +
        table(['Your engine or problem', 'Jewelry to inspect', 'Alternative decision'], [
            ['Affliction DoT output', 'Seal of the Damned', 'Keep another useful damage or repeat-cast offer if the faster-tick item never appears.'],
            ['Repeated casts or Dread Lord timing', 'Quick Strike Ring', 'Read the summon interval floor; shorter cooldowns do not imply unlimited summons.'],
            ['Damage works, recovery does not', "Blooddrinker's Band", 'Compare a health buffer if you cannot keep dealing damage safely.'],
            ['Too little health buffer', 'Heavy Dark Iron Ring', 'Take relevant defence rather than waiting for a particular damage item.']]) +
        p('Use each actual offer’s value rather than fixed percentages from an older guide. Permanent class gear is '
          'separate from in-run jewelry. ' + a('items/#build-pairings', 'Named jewelry effects') + ' · ' + a('armory/', 'Equipment and set thresholds'))))
    d['parts'].append(('build-faq', 'Warlock build questions',
        '<h3>Is Affliction always the best Warlock build?</h3>' + para('It is a clear direction for DoT spread, but '
        'its healing and propagation need the named talents. The same chain does not establish isolated-boss performance.') +
        '<h3>Can I combine the Dread Lord and Felguard endpoints?</h3>' + p('Pact of the Nathrezim and Butcher '
        'are exclusive in the inspected original snapshot. Plan around the branch actually selected.') +
        '<h3>Should I restart when the recommended item does not appear?</h3>' + para('No named jewelry item is a '
        'requirement in these plans. Keep a working engine and compare the offer that solves the current damage or survival problem.')))
