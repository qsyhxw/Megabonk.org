"""Soulstone Survivors 首页数据：任务卡文案、FAQ、更新、分组（页面清单见 data/soulstone-survivors-pages.json）。"""
P = '/soulstone-survivors/'
CARD_NAMES = {'builds': 'Builds', 'ru/builds': 'Билды на русском', 'beginners-guide': 'Beginner guide',
              'builds/barbarian': 'Barbarian build', 'bumble-crystal-order': 'Bumble crystal order',
              'co-op': 'Co-op', 'mods': 'Mods'}
HOME_DATE = '21 November 2026'
CHECKED = '2 November 2026'
UPDATES = [
    ('2 Nov 2026', 'Barbarian page compares two reported routes: a Bloodgod’s Legacy bleed template and a July 2025 community loadout.', 'builds/barbarian/', 'Barbarian routes'),
    ('2 Nov 2026', 'Co-op guide checked against the online mod README (game 1.5.3.2) and the local mod README 1.3.0.', 'co-op/', 'Co-op choices'),
    ('2 Nov 2026', 'Bumble guide: winter circles in red → blue → yellow → green → purple order, with the Christmas Portal check.', 'bumble-crystal-order/', 'Crystal order'),
    ('17 Jun 2025', 'Version 1.0: Steam lists the game as out of Early Access (Early Access began 7 Nov 2022).', 'beginners-guide/', 'Start here'),
]
GROUPS = [
    ('Start with the next decision', 'Permanent progress before a perfect run.',
     [('beginners-guide', 'Beginner guide', 'Spend, return or continue')]),
    ('Choose a damage plan', 'Skill types, chains and a named character.',
     [('builds', 'Builds', 'Trigger and payoff checklist'), ('builds/barbarian', 'Barbarian build', 'Two reported routes'),
      ('ru/builds', 'Билды на русском', 'Типы навыков и цепочки')]),
    ('Play with friends', 'Online and same-PC fan mods are separate projects.',
     [('co-op', 'Co-op', 'Online or local route'), ('mods', 'Mods', 'Loaders and versions')]),
    ('Finish the winter event', 'A hidden five-colour task, separate from normal progress.',
     [('bumble-crystal-order', 'Bumble crystal order', 'Circles and Christmas Portal')]),
]
FAQ = [
    ('Is Soulstone Survivors single-player?', 'Steam lists the base game as single-player. On Windows, fan mods add separate online and same-PC co-op routes; they are not official multiplayer support.', 'co-op/', 'Co-op choices'),
    ('Do the co-op mods work with the current game?', 'Each author documents one game version: the online README targets 1.5.3.2 and the local README was tested on 1.5d2. Match the version and loader before installing, and keep a backup.', 'mods/', 'Mod compatibility'),
    ('What is the Bumble crystal order?', 'Activate the five winter circles in red, blue, yellow, green, purple order. Kill a boss that drops the matching colour of major Soulstone inside its circle; standing in the circle is not enough.', 'bumble-crystal-order/', 'Crystal order'),
    ('Is there a Soulstone Survivors tier list?', 'Not here. The sources we checked do not establish a tested ranking for every character and mode, so we publish a build checklist and a Barbarian comparison instead.', 'builds/', 'Build checklist'),
    ('What should I do first as a new player?', 'Use early runs for permanent upgrades and one damage plan you can describe. After a clear, decide whether you need a safe return to spend resources or a harder continuation.', 'beginners-guide/', 'Beginner guide'),
    ('Is Soulstone Survivors on console or Switch?', 'Steam lists Windows, macOS and Linux. The official site links PS5 and Xbox Series versions; the links we checked do not list Nintendo Switch, which is not a promise that a port will never happen.', 'beginners-guide/', 'Start here'),
    ('Is there a Russian build guide?', 'Yes. The Russian page explains skill types, chains and replacements for builds; English skill names are kept so you can compare the source text.', 'ru/builds/', 'Билды на русском'),
]
FAQ_QUESTIONS = [q for q, _, _, _ in FAQ]
