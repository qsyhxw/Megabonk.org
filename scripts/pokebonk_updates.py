"""Reviewed October 25 source-based revisions; preserve existing page metadata."""
import json
import re
from pathlib import Path

VERSION = '0.8.48'
CLIENT = 'https://pokebonk.com/assets/main-Db7PlFmR-mvnw9v2s.js'
NEWS = 'https://pokebonk.com/assets/news-C0a_sdDN-mvnw9v2s.js'
CHECKED = 'October 25, 2026'


def apply_updates(ctx):
    P, pages = ctx['P'], ctx['PAGES']
    article, ref, table, ext = (ctx[n] for n in ['article', 'ref', 'table', 'ext'])
    old_date, old_version = ctx['DATE'], ctx['VERSION']
    ctx['DATE'], ctx['VERSION'] = CHECKED, 'v' + VERSION
    source_client = (CLIENT, 'Original public game client', 'Beta v0.8.48 / build mvnw9v2s, inspected October 25. SINGLE_SOURCE; client inspection is not a completed gameplay or multiplayer test.')
    source_news = (NEWS, 'Original project release notes', 'Dated v0.8.42–v0.8.48 entries, October 24–25. Source descriptions, not measured compatibility or win rates.')

    def update(slug, answer, parts, sources, links):
        before = pages[P + slug + '/']
        h1 = re.search(r'<h1>(.*?)</h1>', before['html']).group(1)
        article(slug, before['title'], h1, before['desc'], answer,
                parts, sources, links, lang='zh-Hans' if slug.startswith('zh/') else 'en')

    update('multiplayer',
        f'PokeBonk now documents a Co-op Beta for 2–4 trainers, with room creation, invites and code-based joining. Access can be restricted or paused by the server. Use the current Co-op screen to check availability; we inspected the client and notes, not a completed shared run.{ref(1)}{ref(2)}', [
        ('confirmed', 'What co-op includes now',
         f'<p>The v0.8.48 client has a dedicated Co-op flow and a 2–4 trainer label. It offers <strong>Create a room</strong> and <strong>Join with a code</strong>. Its availability states distinguish closed Beta, maintenance and a temporary pause. Friends, clans and leaderboards remain separate social systems.{ref(1)}</p>' +
         table(['Your goal', 'Use this feature', 'Important boundary'], [
             ('Enter the same run', 'Co-op room, invite or room code', 'Both access eligibility and working player connections are required.'),
             ('Find someone to invite', 'Friends', 'Adding a friend is not the same as joining their run.'),
             ('Participate in clan activity', 'Clans', 'Clan membership alone does not create a shared arena.'),
             ('Compare a team result', 'Co-op leaderboard', 'The result is a record, not evidence that a new room is currently available.')]) +
         '<p class="note">Checked October 25, v0.8.48. This page establishes documented features and entry steps. We did not join a real multiplayer session, verify every account’s Beta eligibility or test cross-device play.</p>'),
        ('friends', 'Create or join a room in order',
         f'<ol><li><strong>Open the original project.</strong> Use {ext("https://pokebonk.com/?lang=en", "pokebonk.com — original game")} and keep the account/session with your existing progress.</li>'
         '<li><strong>Check Co-op availability.</strong> If the screen says closed Beta, maintenance or paused, follow that message. A working solo menu is not proof that new co-op rooms can be created.</li>'
         '<li><strong>Choose who creates the room.</strong> The creator selects the available destination and difficulty, then invites friends or shares the room code/link.</li>'
         '<li><strong>Join the same room.</strong> Other trainers use the invitation or Join with a code. Inspect the room’s player cards; change your own partner through your card and the League selection.</li>'
         '<li><strong>Resolve version or connection warnings before Start.</strong> The client checks player-to-player readiness. When a version mismatch appears, everyone should reload the original page and check the version again.</li></ol>'
         f'<p>The current client explicitly describes direct browser-to-browser connections. We have not tested router, VPN or corporate-network fixes; do not install an unofficial client or disable device protections on the strength of a generic connection tip.{ref(1)}</p>'),
        ('release', 'Pause, menus, reviving and current team rules',
         f'<p><strong>Pause does not stop a shared run.</strong> The client warns that you remain exposed with pause open. Upgrade/menu choices use a distinct protective bubble; the v0.8.46 notes say you do not deal damage while choosing, and the guardian can move to teammates. Do not rely on opening pause as a safe break.{ref(1)}{ref(2)}</p>'
         '<p>For a downed teammate, the release notes describe going beside them and holding <kbd>E</kbd> on desktop to revive. The v0.8.45 notes give a one-minute revival window. Later fixes address full revival bars and reviving when a team crosses a portal. These are documented rules, not a latency guarantee.</p>'
         '<p><strong>Do not follow the superseded v0.8.45 team-puzzle instructions.</strong> Version 0.8.46 removed the boss seals, changing team weakness, Wrath and linked-elite mechanics introduced in that update. Gengar, cursed and Rhydon altars returned to individual use. Version 0.8.47 adds shared discoveries on the map and a way to visit the Lab from the room and return to it.</p>'),
        ('connection', 'When joining or starting fails',
         table(['What the screen says', 'Next action', 'What not to infer'], [
             ('Different version', 'Reload the original page on each participant and compare the displayed version.', 'A matching website address does not guarantee matching cached builds.'),
             ('Closed Beta / no access', 'Use the account’s actual eligibility message and the project’s announcements.', 'No player limit workaround or invite-code purchase is verified here.'),
             ('Maintenance / paused', 'Wait for the project’s stated reopening; solo and running rooms may behave differently.', 'This is not proof that the whole game or your save is broken.'),
             ('Players not connected', 'Read the room’s network warning and record which participants fail to connect.', 'We have no universal tested router or browser fix.')]) +
         f'<p>For repeated failures, give {ext("https://discord.gg/X7KusQqx8X", "PokeBonk support")} the game version, browser, room warning and time. Do not share passwords or session credentials.</p>'),
        ('megabonk', 'Is this the Megabonk multiplayer mod?',
         '<p>No. This guide covers the separate PokeBonk browser project. Megabonk mod-manager instructions apply to the Steam game. They do not create a PokeBonk room or change your Beta eligibility.</p>')],
        [source_client, source_news], [('beginners-guide/', 'First-run setup'), ('mobile/', 'Phone controls and browser checks'), ('builds/', 'Plan moves before a run')])

    # Existing mobile structure stays intact; replace only the outdated recovery
    # rows and add version-specific decisions, retaining the no-device-test limit.
    mobile = pages[P + 'mobile/']['html']
    mobile = mobile.replace('October 23, 2026', CHECKED).replace('v0.8.25', 'v' + VERSION).replace(ctx['CLIENT'], CLIENT)
    mobile = mobile.replace('<h2>Choose the next step by the symptom</h2>',
        '<h2>Choose the next step by the symptom</h2>'
        '<p>The October 25 notes describe a fallback that tries another graphics adapter if 3D initialization fails and shows a more specific explanation. Follow that displayed advice before erasing browser data. This is a documented recovery behavior, not a tested fix for every phone.</p>'
        '<p>Recent mobile changes also keep the “Not now” action visible at Bill’s Machine and allow cancellation when banishing. If you leave fullscreen, later runs should no longer re-enter it automatically. Check your current build before treating an older control screenshot as the present layout.</p>')
    mobile = mobile.replace('<p>If the problem persists,',
        '<p>Settings → Graphics now includes an FPS cap (unlimited, 30, 60, 90, 120 or 144). A lower cap is an option to compare for consistency or device workload; it does not increase the device’s maximum rendering ability. We have not measured power use or frame rates on a phone.</p>'
        '<p>If the problem persists,')
    mobile = mobile.replace('Touch, graphics options and recovery-related UI;', 'Touch, graphics options, v0.8.31 FPS settings and current recovery-related UI;')
    # The current client provides all newly described controls; cite it via the
    # existing source-2 note, and add the dated notes as source 4.
    mobile = mobile.replace('This is a documented recovery behavior, not a tested fix for every phone.</p>',
        f'This is a documented recovery behavior, not a tested fix for every phone.{ref(4)}</p>')
    mobile = mobile.replace('</ol><a class="back"',
        '<li id="source-4">' + ext(NEWS, 'Original release notes') + ' — v0.8.31 FPS cap; v0.8.45 fullscreen; v0.8.46 graphics startup; v0.8.47 mobile actions. Checked October 25; not a phone test.</li></ol><a class="back"', 1)
    pages[P + 'mobile/']['html'] = mobile

    chinese = pages[P + 'zh/beginners-guide/']['html']
    chinese = chinese.replace('October 23, 2026', CHECKED).replace('v0.8.25', 'v' + VERSION).replace(ctx['CLIENT'], CLIENT).replace(ctx['NEWS'], NEWS)
    chinese = chinese.replace('好友、社团和排行榜属于已能从当前资料确认的在线功能；它们不能自动证明可以进入同一张地图实时合作。本次没有验证共享合作局，不承诺上线时间或人数。',
        f'当前客户端已提供2–4人的合作 Beta：在 Co-op／合作入口查看开放状态，由一人创建房间，其他人使用邀请或房间代码加入。关闭测试、维护与临时暂停是不同状态，以你账号实际看到的提示为准。本次核查了公开客户端及更新记录，没有完成真实多人局或跨设备测试。{ref(2)}{ref(3)}</p>'
        '<p>共享局打开暂停菜单不会让世界停止。升级选择菜单的保护泡泡是另一个机制，不能把两者混为一谈。遇到版本不一致提示时，队员先刷新原站并核对版本，再开始。10月25日的更新还加入共享地图发现，以及从房间进入实验室后返回房间的入口。</p>'
        '<p>不要继续使用 v0.8.45 的团队封印／连接精英攻略：v0.8.46 已撤回这些机制。完整创建、加入和故障提示说明见 <a href="/pokebonk/multiplayer/">合作模式攻略（英文）</a>。')
    chinese = chinese.replace('完整技能组、被动数值与按目标筛选工具放在英文伙伴对比页；',
        '进化要看本游戏的局内阈值，而不是正作等级；当前伊布还会弹出分支选择。详见 <a href="/pokebonk/evolution/">进化规则与等级对照（英文）</a>。完整技能组、被动数值与按目标筛选工具放在英文伙伴对比页；')
    pages[P + 'zh/beginners-guide/']['html'] = chinese

    # Recheck the unchanged basic inputs and starter passives, and connect the
    # two new task pages without adding top-level navigation items.
    for slug in ['beginners-guide/', 'starters/']:
        page = pages[P + slug]
        html = page['html'].replace('v0.8.25', 'v' + VERSION).replace('October 23, 2026', CHECKED).replace(ctx['CLIENT'], CLIENT).replace(ctx['NEWS'], NEWS)
        html = html.replace('entry screen, captured October 25, 2026', 'entry screen, captured October 23, 2026')
        html = html.replace('<section class="related"><h2>Continue exploring</h2>',
            '<section class="related"><h2>Continue exploring</h2><a href="/pokebonk/evolution/">Run evolution levels and choices →</a><a href="/pokebonk/builds/">Plan your moves and items →</a>')
        if slug == 'starters/':
            html = html.replace('The species dataset contains evolution fields, but a general species table alone is not enough to promise the exact runtime evolution conditions for every partner.',
                'The client transforms species data into run thresholds and applies League-specific overrides. Bulbasaur evolves at run levels 24 and 41; Charmander and Squirtle at 24 and 44. Eevee uses a branch-selection menu. The separate evolution guide shows the checked method and exceptions.')
        page['html'] = html

    data = json.loads((ctx['ROOT'] / 'data/pokebonk-evolution.json').read_text(encoding='utf-8'))
    rows = [(r['starter'], r['route'], r['reason']) for r in data['examples']]
    article('evolution', 'PokeBonk Evolution: Run Levels, Eevee & Exceptions', 'PokeBonk evolution, explained',
        'Check PokeBonk run evolution levels, starter thresholds, Eevee choices and League overrides before relying on a main-series evolution chart.',
        f'Evolution follows your level inside the run, using thresholds calculated by the game and any League-specific overrides. Bulbasaur’s checked route is level 24 then 41; Charmander and Squirtle use 24 then 44. Eevee opens a choice at level 36 in this build.{ref(1)}{ref(2)}', [
        ('levels', 'The checked run-level examples',
         '<p>These examples are calculated from the current species data and the client’s run-evolution method, with League overrides applied. They are source-based thresholds, not screenshots of completed evolution tests.</p>' + table(['Starting partner', 'Route inside the run', 'Why it differs'], rows) +
         '<p class="note">Beta v0.8.48, checked October 25. The raw species table contains main-series-style level and trigger fields. Those fields are inputs, not the final run requirements. Do not read a “trade” or stone trigger there as proof that you must trade or buy a stone in this game.</p>'),
        ('check', 'Read your next evolution before spending upgrades',
         f'<ol><li>Inspect your selected partner’s League profile, rather than a profile for a different starting form.</li><li>During a run, inspect the next-evolution indicator and its displayed level. A question mark can indicate a branch choice rather than missing data.</li><li>Reach the threshold through run experience. The client checks evolution readiness before offering the next level-up choice.</li><li>If you have already evolved later than expected, read the next indicator again: the planner enforces a minimum gap of three levels after the current evolution.</li></ol><p>Animation timing, pending choices and whether the form’s sprite is available are separate from the numerical threshold. This guide does not promise that every animation begins at the exact instant the XP bar changes.{ref(1)}</p>'),
        ('eevee', 'Eevee is a choice, not a random-roll instruction',
         f'<p>The current League entry defines Vaporeon, Jolteon and Flareon as Eevee’s branches and sets level 36. The run planner flags that branch and calls a selection menu when evolution is ready. Choose the displayed form there; do not follow an older guide that tells you to reset for a random branch.{ref(1)}{ref(2)}</p><p>This is a client-verified interaction, not a completed Eevee run by this website. If the live menu changes, follow its actual options and check the version before assuming the old interaction still applies.</p>'),
        ('method', 'How the thresholds are derived',
         '<p>For a normal first stage that still has another evolution ahead, the client takes the next species’ raw level, adds 8, then clamps the result between 16 and 30. For a final evolution, it rounds 22 + 0.6 × the raw level, clamped between 36 and 50. A missing raw level uses a stage-dependent fallback.</p>'
         '<p>League overrides take priority. Caterpie and Weedle use 8/36; Magikarp uses 40; Eevee has its own branch rule at 36. After an evolution, the next planned level is at least the current level plus 3. This is why merely reformatting the Pokédex’s raw evolution fields can give the wrong answer.</p>'
         '<p>Our downloadable numeric reference contains these examples and their inputs. It is a small derived snapshot, not a copy of the game client: <a href="/data/pokebonk-evolution.json">view the checked example data</a>.</p>'),
        ('progress', 'Evolution and a permanent League unlock are different',
         '<p>A run begins from the partner selected for it and evolves as that run progresses. Adding a partner to your League uses its own challenge and capture rules. Evolving the Pokémon you already control is not the same action as unlocking another starter or permanently starting every later run in the evolved form.</p>'
         '<h3>Why did my Pokémon not evolve at the main-series level?</h3><p>Use this game’s transformed run threshold and League override. The raw Pokédex field alone is insufficient.</p>'
         '<h3>Do I need an evolution stone or a trade?</h3><p>Do not infer that requirement from the raw species trigger. The checked run planner uses the level route and its overrides.</p>'
         '<h3>Does a delayed first evolution shift the next one?</h3><p>It can: the next plan cannot be earlier than three levels after the current evolution.</p>')],
        [source_client, (NEWS, 'Current League definitions', 'Caterpie/Weedle 8/36, Magikarp 40 and Eevee 36 with selectable branches. SINGLE_SOURCE.'),
         ('https://pokebonk.com/data/pokemon.json', 'Original species data', 'Inputs to the runtime calculation, fetched October 25; not used as an unmodified run-level table.')],
        [('starters/', 'Compare your first partner'), ('builds/', 'Plan moves and upgrades'), ('beginners-guide/', 'First-run controls and progress')])
    # Every source listed is used by the article's actual conclusions.
    pages[P + 'evolution/']['html'] = pages[P + 'evolution/']['html'].replace('with League overrides applied.', f'with League overrides applied.{ref(3)}', 1)

    article('builds', 'PokeBonk Build Planning: Moves, Vitamins & Items', 'Plan a PokeBonk build you can follow',
        'Use PokeBonk’s current Build plan to connect moves, vitamins, items and fusions, check availability and keep a clear priority during a run.',
        f'Use the selected partner’s Build plan to mark the moves, vitamins, fusions and items you want. The game highlights planned choices during play. This is a planning aid, not a guaranteed drop sequence or an independently tested strongest build.{ref(1)}{ref(2)}', [
        ('plan', 'Set the plan for the partner you will actually play',
         f'<ol><li><strong>Select a League partner.</strong> Open the Build plan action associated with that Pokémon. The client labels the dialog with the partner’s name.</li><li><strong>Read the slots summary.</strong> Review Attacks, Vitamins and Fusions; inspect the item options as well. The plan warns about locked and archived choices.</li><li><strong>Choose a direction.</strong> Connect your passive, intended attacks and the stat bonuses that actually affect them. Do not fill a slot merely because the item name sounds strong.</li><li><strong>Mark your choices and finish.</strong> Planned options receive an “In your plan” marker in supported run choices, Poké Balls or Meowth’s shop.</li><li><strong>Keep an alternative.</strong> A marker identifies your preference; it does not force the game to offer that choice.</li></ol><p>The v0.8.44 notes introduced a six-item planning limit, but v0.8.45 removed that item limit. Do not treat a screenshot of the older editor as today’s cap.{ref(1)}{ref(2)}</p>'),
        ('starter', 'Turn a starter passive into a decision rule',
         table(['Partner / goal', 'Plan around', 'Check before selecting'], [
             ('Bulbasaur / recovery', 'Grass hits and healing-aware choices', 'The healing effect has a hit-rate limit. A Physical-only or Special-only bonus will not automatically improve every listed move.'),
             ('Squirtle / defensive start', 'Armor and shield plus a coherent Water/mixed kit', 'The separate low-HP damage bonus is conditional. It is not a reason to deliberately lose most of your HP.'),
             ('Charmander / Fire offense', 'Its Fire-focused listed kit and applicable damage bonuses', 'A Fire bonus and a general damage-class bonus describe different scopes. Read the selected move’s actual description.')]) +
         f'<p>These are editorial planning directions based on current passive and kit descriptions, not clear-time, DPS or win-rate rankings. The starter comparison preserves the numerical passive details.{ref(1)}</p>'),
        ('choices', 'Read an upgrade against your current problem',
         '<p><strong>Not surviving contact?</strong> Inspect what the defensive or recovery offer changes, and whether it works with your current passive. Extra damage is not the same effect as recovery.</p>'
         '<p><strong>Struggling to clear?</strong> Inspect the move’s damage class, type and shape. A displayed stat is useful only if it affects the part of the attack you rely on.</p>'
         '<p><strong>Planning a fusion?</strong> Keep the ingredients in the plan, but read the current fusion card before spending offers on Area, Duration or Projectiles. The October 25 notes add explanations of which part of the fusion each stat affects. The full fusion damage is not necessarily one projectile.</p>'),
        ('fusion', 'Use fusion descriptions, not a universal recipe claim',
         f'<p>The current client describes combining two moves at maximum level 8 at Bill’s Machine. The eligible pair determines the result, with signature, reaction, same-type and fallback cases. This paragraph explains the planning constraint; it is not a complete recipe database.{ref(1)}</p>'
         '<p>Use the game’s own Fusions tab to inspect the result of the actual available pair. If one ingredient is locked or archived, a saved wish list does not make it obtainable. On mobile, the latest notes keep “Not now” visible at the machine, so a premature visit need not force a decision.</p>'),
        ('limits', 'What a plan changes, and what it does not',
         f'<p>The current menu’s <strong>Favorites</strong> are just favorite Pokémon; the v0.8.47 notes explicitly say they do not change a run. The <strong>Build plan</strong> is the separate preference/highlight tool. Neither label proves a performance boost.{ref(2)}</p>'
         '<h3>Does marking an item unlock it?</h3><p>No unlock is established by a plan marker. Inspect the locked/archived warning and the actual item requirement.</p>'
         '<h3>Is there one best four-move build here?</h3><p>No. We have not collected controlled, same-version runs to establish that ranking. This page helps you make and follow a coherent plan.</p>'
         '<h3>Should I keep an old plan after a patch?</h3><p>Recheck the affected move, item or fusion description. Keep preferences that still solve the run’s problem, and revise choices whose effects changed.</p>')],
        [source_client, source_news], [('starters/', 'Compare starter passives'), ('evolution/', 'Check run evolution thresholds'), ('multiplayer/', 'Understand co-op conditions')])

    home = pages[P]['html']
    home = home.replace('October 23, 2026', CHECKED).replace('v0.8.25', 'v' + VERSION).replace(ctx['CLIENT'], CLIENT)
    home = home.replace('Online does not always mean co-op.', 'Co-op Beta has its own rooms.')
    home = home.replace('The current sources document friends, clans and rankings. A shared co-op run was not verified in this review. Check the actual feature before planning a session.',
        'The current client documents 2–4 trainer co-op rooms, invites and code-based joining. Check your account’s access and the current server message before starting. This guide has not completed a multiplayer test.')
    home = home.replace('Clans, friends and co-op verification', 'Room creation, joining, menus and connection checks')
    home = home.replace('<div class="guide-index">', '<div class="guide-index"><a href="/pokebonk/evolution/">Run evolution levels<span>Starter thresholds, Eevee choices and League overrides</span></a><a href="/pokebonk/builds/">Build planning<span>Use moves, vitamins, items and the current plan editor</span></a>', 1)
    pages[P]['html'] = home
    ctx['DATE'], ctx['VERSION'] = old_date, old_version
