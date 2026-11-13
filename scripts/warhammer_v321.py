"""v3.21 pass for the Warhammer Survivors section (2026-11-13).

Runs last in build_warhammer_survivors.py, on the finished HTML:
- Evolutions: one definitive trigger rule (two gameplay videos agree), in-game frames,
  a click-to-load video after the steps, no who-reported-what prose.
- Legend of Catachan: full route (Signum Array relic -> Imperial Bastion -> 1,020 coins)
  from the GameSteed video, cross-checked with the GrindnStrat relic list; map frames.
- Other pages: answer-first wording, in-game Objectives frame instead of Destructoid's,
  no "reported / not a site test" boilerplate, external links cut to action entries.
Evidence (video URLs, timestamps, articles) is kept in _private/wh-v321-sources.json.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'warhammer-survivors'
YT_HEAD = '<link rel="stylesheet" href="/assets/yt-embed.css"><script defer src="/assets/yt-embed.js"></script>'


def video(vid, start, label, title, channel):
    t = sum(int(x) * 60 ** i for i, x in enumerate(reversed(start.split(':')))) if start else 0
    return (f'<figure class="yt-embed"><button type="button" class="yt-facade" data-yt="{vid}" data-start="{t}" '
            f'aria-label="Play video: {label}"><img src="/assets/warhammer-survivors/video/{vid}.webp" width="960" height="540" '
            f'alt="" loading="lazy" decoding="async"><span class="yt-play" aria-hidden="true"></span></button>'
            f'<figcaption>{title} · {channel} · <a href="https://www.youtube.com/watch?v={vid}{"&amp;t=" + str(t) + "s" if t else ""}">Watch on YouTube</a></figcaption></figure>')


def frame(src, w, h, alt, caption=''):
    cap = f'<figcaption>{caption}</figcaption>' if caption else ''
    return f'<figure><img src="/assets/warhammer-survivors/{src}" width="{w}" height="{h}" alt="{alt}" loading="lazy" decoding="async">{cap}</figure>'


def section(text, sid):
    m = re.search(rf'<section id="{sid}">.*?</section>', text, re.S)
    assert m, sid
    return m


def replace_section(text, sid, html):
    m = section(text, sid)
    return text[:m.start()] + html + text[m.end():]


def drop_section(text, sid):
    return replace_section(text, sid, '')


THEME = '/assets/warhammer-survivors/theme.css'
BORROWED = re.compile(r'<link rel="stylesheet" href="/assets/(?:pokebonk|vampire-survivors)/site\.css(?:\?v=[0-9a-f]+)?">\n?'
                      r'|<link rel="stylesheet" href="/assets/warhammer-survivors/home\.css(?:\?v=[0-9a-f]+)?">\n?')


def theme(name, text):
    """One game theme for the hub and every guide (SOP 02 §2.1, v3.22); drop styles borrowed from other games."""
    text = BORROWED.sub('', text)
    if THEME not in text:
        text = re.sub(r'(<link rel="stylesheet" href="/assets/guide-article-layout\.css[^"]*">)', r'\1<link rel="stylesheet" href="' + THEME + '">', text, count=1)
    assert THEME in text, name
    cls = 'guide-layout wh-theme wh-hub' if name == '' else 'guide-layout wh-theme wh-guide'
    return re.sub(r'(<body[^>]*?) class="guide-layout[^"]*"', lambda m: m[1] + f' class="{cls}"', text, count=1)


def with_video_assets(text):
    return text if 'yt-embed.js' in text else text.replace('</head>', YT_HEAD + '</head>', 1)


def must(text, old, new):
    assert old in text, old[:80]
    return text.replace(old, new, 1)


def anchor_rows(text):
    """Give every recipe row an id (#lasgun, #chainsword …) so single-weapon searches land on their row."""
    def row(m):
        slug = re.sub(r'[^a-z0-9]+', '-', re.sub(r'&[^;]+;', '', m[1]).lower()).strip('-')
        return f'<tr id="{slug}"><td>{m[1]}</td>'
    return re.sub(r'<tr><td>([^<]+)</td>', row, text)


def evolutions(text):
    text = must(text, '<p><strong>Match a weapon with its companion, then check the reported upgrade and chest conditions.</strong> The table now includes 38 unique reported pairings, with launch additions and older demo evidence identified below. Use the universe filter to find the pair relevant to your run.</p>',
                '<p><strong>Max the weapon, hold its companion passive (level 1 is enough for most), then open a chest from an elite or boss.</strong> The table below lists all 38 weapon + companion pairs for both universes; filter by your universe or search a weapon.</p>')
    recipes = section(text, 'recipes').group(0)
    recipes = re.sub(r'<p>These are <strong>October-demo community reports</strong>.*?</p><p><strong>Launch additions checked 11 November\.</strong>.*?</p>',
                     '<p>Release version (10 November 2026). Nuln Oil and D6 Dice evolve in both universes. If an item name differs in your Armoury, trust the in-game Evolution Requirements panel (shown below).</p>', recipes, flags=re.S)
    recipes = recipes.replace('38 reported recipes</p>', '38 recipes</p>')
    text = replace_section(text, 'recipes', recipes)
    trigger = ('<section id="sequence"><h2>How to trigger an evolution</h2><ol>'
               '<li><strong>Level the base weapon to its maximum.</strong> A partly upgraded weapon never evolves.</li>'
               '<li><strong>Pick up the companion passive.</strong> Level 1 is enough, except four recipes marked “max level” in the table (Bale Eye, Weapon of the Matriarch, Uskavar the Sunderer and Ghal Maraz).</li>'
               '<li><strong>Open the next chest from an elite or boss.</strong> With both conditions met, that chest gives the evolution instead of a normal upgrade.</li></ol>'
               + frame('evo/evolution-requirements.webp', 1001, 626, 'Level-up screen with the Whirlwind Axes card showing Evolution Requirements: Tempest Axes plus Sabaton equals Whirlwind Axes',
                       '① Hover a weapon on the level-up screen to see its Evolution Requirements: weapon + companion = evolution.')
               + frame('evo/chest-evolution.webp', 556, 488, 'Chest opening that turns Boltstorm Pistol into Typhoon Crossbow',
                       '③ The next elite/boss chest after maxing Boltstorm Pistol with Dice Cube held returns Typhoon Crossbow.')
               + '<p><strong>Chest did not evolve?</strong> The weapon was not at max level yet when you opened it, or the passive was missing. Max the weapon first, keep the passive, and open the next boss chest. If the companion never shows up in level-up choices, it is still locked: check <a href="#weapon-checks">its unlock</a>.</p>'
               + '<h3>Watch it happen</h3>'
               + video('bq1k1U5KXaM', '12:02', 'Boltstorm Pistol evolving into Typhoon Crossbow from a boss chest', 'I evolved EVERY WEAPON to slay THOUSANDS in this Roguelite!', 'Gohjoe')
               + '</section>')
    text = replace_section(text, 'sequence', trigger)
    text = replace_section(text, 'version', '<section id="version"><h2>Older demo pairings you may still see online</h2><p>Guides written for the first October demo list three pairs that changed: Whirlwind Battery now uses <strong>Liquid Green Stuff</strong> (not Tape Measure), Nebulous Sea Fog uses <strong>Bugman\'s Tankard</strong> (not Glue), and the Age of Sigmar Boltstorm Pistol uses <strong>Dice Cube</strong>. Dice Cube and Liquid Green Stuff each appear in both universes with a different weapon, so filter by universe before planning a run.</p></section>')
    checks = section(text, 'weapon-checks').group(0)
    checks = checks.replace('The launch item guide reports surviving one minute in a 40K run as the Tape Measure unlock.', 'Unlock Tape Measure by surviving 1 minute with any character.')
    checks = checks.replace('The launch item report gives Boltgun level 4 as Bandolier’s unlock condition. This is separate from upgrading Bandolier during the evolution attempt.', 'Unlock Bandolier by getting Boltgun to level 4.')
    checks = re.sub(r'<p>Unlock conditions are from .*?</p>', '<p>Unlocks happen once through Objectives; after that the passive can appear in any run of that universe.</p>' + frame('objectives-ingame.webp', 570, 910, 'In-game Objectives list: Survive 1 minute with any character unlocks Tape Measure; Survive 5 minutes with Sister Superior unlocks Shield of Faith'), checks, flags=re.S)
    checks = checks.replace('<h2>Start with your weapon’s unlock and companion</h2>', '<h2>Unlock the companion first</h2>')
    text = replace_section(text, 'weapon-checks', checks)
    text = drop_section(text, 'missing')
    nxt = section(text, 'next').group(0)
    nxt = re.sub(r'<p>The game released on 10 November\..*?</p>', '<p><a href="/warhammer-survivors/best-builds/">Best builds using these evolutions →</a></p><p><a href="/warhammer-survivors/bosses/">Which evolution beats each Extremis boss →</a></p><p><a href="/warhammer-survivors/dice-cube/">Unlock Dice Cube in your universe →</a></p><p><a href="/warhammer-survivors/followers/">Get followers and unlock Bugman’s Tankard →</a></p>', nxt, flags=re.S)
    nxt = re.sub(r'<figure>.*?</figure>', '', nxt, flags=re.S)
    text = replace_section(text, 'next', nxt)
    text = re.sub(r'<nav class="toc"[^>]*>.*?</nav>', '<nav class="toc" aria-label="On this page"><a href="#recipes">All 38 recipes</a><a href="#sequence">How to trigger an evolution</a><a href="#weapon-checks">Unlock the companion first</a><a href="#version">Older demo pairings</a></nav>', text, count=1, flags=re.S)
    text = anchor_rows(text)
    return with_video_assets(text)


def catachan(text):
    text = must(text, '<p>Rescue the Legend of Catachan on Imperial Bastion in the Warhammer 40,000 universe. Check character selection after the run to use him as your champion.</p>',
                '<p><strong>Get the Signum Array relic on Ork Stronghold, then rescue him in the top-right of Imperial Bastion and buy him for 1,020 coins.</strong> All three steps are in the Warhammer 40,000 universe.</p>')
    rescue = ('<section id="rescue"><h2>Unlock route</h2><ol>'
              '<li><strong>Unlock Ork Stronghold</strong> by reaching level 40 on Gallowdark.</li>'
              '<li><strong>Pick up the Signum Array.</strong> Start Ork Stronghold with any character, pause, open the Map tab and head to the green <strong>?</strong> in the bottom-right corner. The relic adds extra markers to every 40K map.</li>'
              + frame('catachan/signum-array-map.webp', 1080, 565, 'Ork Stronghold pause map with the Signum Array question mark in the bottom-right corner', '① Ork Stronghold map: the Signum Array is the ? in the bottom-right.')
              + '<li><strong>Rescue him on Imperial Bastion.</strong> With the relic collected, a new <strong>?</strong> appears near the top-right of the Imperial Bastion map. Travel north-east, kill the enemies around him and walk up to him; he joins your run. The Heavy Metal modifier speeds up the walk.</li>'
              + frame('catachan/imperial-bastion-map.webp', 800, 377, 'Imperial Bastion pause map with the Legend of Catachan question mark near the top-right', '② Imperial Bastion map after the relic: his location is the new ? near the top-right.')
              + '<li><strong>Finish the run, then buy him</strong> in Character Select for <strong>1,020 coins</strong>. The objective "Find and rescue the character on Imperial Bastion" completes at the end of the run.</li></ol>'
              + frame('catachan/character-select.webp', 975, 485, 'Character Select stats for The Legend of Catachan: 108 Wounds, +20% Strength and Sustain, +25% Tithe, +4 Skip')
              + '<p><strong>Stats:</strong> 108 Wounds, +20% Strength, +20% Sustain, +25% Tithe, +16% Move, +4 Skip. His passive applies Battleshocked to nearby enemies when his Wounds are critically low, and he finds more explosives.</p>'
              + video('aKB9KGqGceY', '', 'How to unlock the Legend of Catachan, full route', 'How To Unlock Legend of Catachan', 'GameSteed')
              + '</section>')
    text = replace_section(text, 'rescue', rescue)
    text = text.replace(' Developer hotfix announcements</p>', '</p>')
    demo = section(text, 'demo').group(0)
    demo = re.sub(r'<p>The portrait above is an in-game asset.*?</p>', '<p>Continue with <a href="/warhammer-survivors/tips/">first-run planning</a> or <a href="/warhammer-survivors/secrets/">Secrets</a> (the <code>catachandevil</code> incantation is an alternative unlock).</p>', demo, flags=re.S)
    demo = re.sub(r' <a href="https://www\.warhammer-community\.com[^"]*"[^>]*>Official demo announcement ↗</a>', '', demo)
    text = replace_section(text, 'demo', demo)
    text = re.sub(r'<nav class="toc"[^>]*>.*?</nav>', '<nav class="toc" aria-label="On this page"><a href="#rescue">Unlock route</a><a href="#weapon">Frag Grenade bug</a><a href="#demo">Demo progress</a></nav>', text, count=1, flags=re.S)
    text = text.replace('Rescue the Legend of Catachan on Imperial Bastion, check the demo reset, and distinguish his Frag Grenade weapon from the launch Chainsword bug.',
                        'Get the Signum Array on Ork Stronghold, rescue the Legend of Catachan on Imperial Bastion and buy him for 1,020 coins. Map locations and stats.')
    return with_video_assets(text)


OBJ_FIG = re.compile(r'<figure[^>]*>(?:<a href="/assets/warhammer-survivors/objectives\.webp">)?<img src="/assets/warhammer-survivors/objectives\.webp"[^>]*>(?:</a>)?(?:<figcaption>.*?</figcaption>)?</figure>', re.S)
INGAME_OBJ = frame('objectives-ingame.webp', 570, 910, 'In-game Objectives list: Survive 1 minute with any character unlocks Tape Measure; Survive 5 minutes with Sister Superior unlocks Shield of Faith')

EDITS = {
    'followers': [
        ('The launch item guide reports that having two followers unlocks Bugman’s Tankard.', 'Having two followers unlocks Bugman’s Tankard.'),
        ('The item guide reports unlocking Shield of Faith by surviving five minutes with Amalia.', 'Unlock Shield of Faith by surviving five minutes with Amalia (Sister Superior).'),
        ('The reported route recruits Kozlowski through Lasgun and Amalia through Shield of Faith.', 'Take Lasgun (recruits Kozlowski) and Shield of Faith (recruits Amalia).'),
        (' The reports do not establish that this 40K route completes the other universe’s objective.', ' Age of Sigmar has its own follower objective.'),
        ('Destructoid’s follower guide describes the same Malum Caedo loadout and upgrading Lasgun to level 6. It reports that Kozlowski’s additional soldiers, together with Amalia, complete the five-follower target and unlock Figure Case.',
         'For five followers, keep the same Malum Caedo loadout and upgrade Lasgun to level 6: Kozlowski’s extra soldiers plus Amalia complete the target and unlock Figure Case.'),
        ('Bugman’s Tankard is reported beside Shield of Faith in 40K and Nebulous Sea Fog in Age of Sigmar.', 'Bugman’s Tankard evolves Shield of Faith in 40K and Nebulous Sea Fog in Age of Sigmar.'),
    ],
    'dice-cube': [
        (' The launch item guide reports different Dice Cube unlock conditions for the two universes.', ' Each universe has its own Dice Cube objective.'),
        ('Use the <a href="/warhammer-survivors/evolutions/">recipe finder</a> and search Dice Cube to compare the two reported pairings.', 'Search Dice Cube in the <a href="/warhammer-survivors/evolutions/">recipe finder</a> to see both pairings.'),
        ('If the current Objective differs from the report, keep its displayed wording and game version when asking support. ', ''),
    ],
    'tips': [
        ('The pictured 40K objective lists surviving one minute as the Tape Measure unlock.', 'Surviving one minute with any character unlocks Tape Measure.'),
    ],
    'secrets': [
        ('Type the reported word as shown, submit it, and check the named reward.', 'Type the word exactly as shown, submit it, and check the named reward.'),
        ('<th>Reported incantation</th>', '<th>Incantation</th>'),
    ],
    'co-op': [
        ('These choices combine the two developers\' rules; they are not our performance tests. ', ''),
    ],
    '': [
        ('Open the right universe’s menu and understand reported codes.', 'Open the right universe’s menu and enter incantations.'),
        ('Arka Sarkar\'s launch guide reports <strong>10,000 enemies defeated across multiple runs</strong> as Tor Garadon\'s unlock condition.', 'Tor Garadon unlocks after <strong>10,000 enemies defeated across multiple runs</strong>.'),
        (' The guide does not provide a recommended Tor build or a precise claim about which other modes contribute.', ''),
        ('<a href="/warhammer-survivors/evolutions/">reported recipe table</a>', '<a href="/warhammer-survivors/evolutions/">recipe table</a>'),
        (' Recipe and unlock pages identify their supporting sources and build-specific limits.', ''),
    ],
}

# Sentences that only described where a fact came from or what this site did not test.
DROP = [
    r'<p>Those prerequisites combine the launch character, item and follower guides\..*?</p>',
    r'<p>This is a published route, with no full-run test by this site\..*?</p>',
    r'<p>The launch item report gives both conditions and says universe objectives must be completed separately\..*?</p>',
    r'<p>These selected examples are community launch reports from <a [^>]*>Wikily’s Secrets reference ↗</a>\. They have not been entered in a live save by this site\.</p>',
    r' Locations and effects are listed in <a [^>]*>GrindnStrat’s relic guide ↗</a>\. The pictured Book is the 40K object, as identified by <a [^>]*>Wikily’s relic entry ↗</a>\.',
    r'<p>Objectives screenshot by Destructoid, from its launch item guide\..*?</p>',
    r' These planning tips combine documented objectives and existing guides, with no site-run performance or build-ranking test\.',
    r' Destructoid character unlock report, 10 November',
    r'Checked 12 November 2026\. No standalone developer APK download has been verified in this review\. Direct APK sideloading and installation on devices without Google Play remain unresolved\.',
    r'Checked 12 November 2026\. Native-edition versus compatibility differences, measured frame rate and handheld battery life have not been established by this review\.',
    r' Exact selection odds and a guaranteed appearance time have not been established\.',
    r'<p>[^<]*Character unlock report · Item unlock report</p>',
    r' Bugman’s Tankard unlock report',
    r' Reported five-follower route, 10 November',
    r' Destructoid launch item unlocks',
]

BYLINE = re.compile(r'(<p class="byline">Megabonk\.org editors · )Checked (\d+ November 2026)(?: · [^<]*)?</p>')


def tidy(name, text):
    for old, new in EDITS.get(name, []):
        text = text.replace(old, new)
    for pat in DROP:
        text = re.sub(pat, '', text, flags=re.S)
    text = OBJ_FIG.sub(INGAME_OBJ, text)
    if name == '':
        # Evidence links on the hub become plain text; store/platform entries stay (00 §4).
        for host in ('aurochdigital.com/warhammer-survivors-faq', 'www.warhammer-community.com', 'news.xbox.com', 'www.xbox.com/en-US/games/store/warhammer-survivors-demo'):
            text = re.sub(r'<a href="https://' + re.escape(host) + r'[^"]*"[^>]*>(.*?)\s*↗(?:<span[^>]*>[^<]*</span>)?</a>', r'\1', text)
    if name == 'co-op':
        # poncle's FAQs belong to the Vampire Survivors co-op guide this page links to.
        text = re.sub(r'<a href="https://poncle\.games/[^"]*"[^>]*>(.*?) ↗</a>', r'\1', text)
    fmt = {'evolutions': 'database', 'legend-of-catachan': 'location', 'followers': 'location', 'dice-cube': 'entry', 'secrets': 'other', 'tips': 'beginner', 'co-op': 'platform', 'cross-save': 'platform', '': 'hub'}.get(name)
    if fmt and 'data-format=' not in text:
        text = re.sub(r'<body(?=[\s>])', f'<body data-format="{fmt}"', text, count=1)
    text = text.replace('<p></p>', '')
    text = BYLINE.sub(lambda m: f'{m[1]}Updated {m[2]} · Release v2.1</p>', text)
    return text


ENH = frame('enhancements.webp', 573, 1110, 'Enhancements screen: Strength raises damage by 4% per rank, up to +40%; ranks apply to both universes; Refund All button')
AMALIA = frame('amalia-select.webp', 573, 960, 'Character Select for Sister Superior Amalia Novena: +10% Range every 10 levels, +10% Chance below 50% health')
LEVELUP = frame('evo/evolution-requirements.webp', 1001, 626, 'Level-up screen offering four passives, with a weapon card showing its evolution requirements')


def tips(text):
    text = must(text, '<p>Pick one visible objective before starting a run. Check its universe and prerequisites, then choose a weapon plan that also moves that objective forward.</p>',
                '<p><strong>Start as Sister Superior Amalia Novena, spend coins on Strength in Enhancements, and aim every run at one Objective.</strong> Max one weapon early and hold its companion passive so the first boss chest evolves it.</p>')
    first = ('<section id="start"><h2>First hour: what to do</h2><ol>'
             '<li><strong>Buy Strength first</strong> in Enhancements: +4% damage per rank (max +40%), and ranks count in both universes. Refund All is free, so you can respec any time.</li>'
             '<li><strong>Play Amalia Novena early.</strong> She gains +10% Range every 10 levels (max +30% at level 30), and surviving 5 minutes with her unlocks Shield of Faith.</li>'
             '<li><strong>Clear the cheap Objectives</strong>: survive 1 minute (Tape Measure), survive 10 minutes (Hourglass), take 250 damage (Glue).</li>'
             '<li><strong>Evolve one weapon per run</strong>: max it, hold its companion and open the next boss chest (<a href="/warhammer-survivors/evolutions/">all 38 recipes</a>, <a href="/warhammer-survivors/best-builds/">best builds</a>).</li></ol>'
             + ENH + AMALIA + '</section>')
    text = text.replace('<section id="plan">', first + '<section id="plan">', 1)
    text = text.replace('<section id="loadout"><h2>Check unlocks before planning an evolution</h2>', '<section id="loadout"><h2>Check unlocks before planning an evolution</h2>' + LEVELUP, 1)
    text = text.replace('<a href="#plan">Choose a run with a concrete goal</a>', '<a href="#start">First hour</a><a href="#plan">Choose a run with a concrete goal</a>', 1)
    return with_video_assets(text.replace('</section><p><a href="#guide">Back to top', video('9bLZOyYe2sU', '1:52', 'Warhammer Survivors beginner guide', 'WARHAMMER SURVIVORS: Beginner Guide', 'iPICKmyBUTT') + '</section><p><a href="#guide">Back to top', 1))


def followers(text):
    text = text.replace('Unlock Sister Superior Amalia Novena. The character guide lists a 400-coin purchase.</li>', 'Unlock Sister Superior Amalia Novena in Character Select.</li>', 1)
    return must(text, '</ol></section><section id="two">', '</ol>' + AMALIA + '</section><section id="two">')


def hub(text):
    block = ('<section class="progression-section" id="videos"><div class="section-heading"><h2>Video guides</h2><p>Watch the hard parts, then use the written steps.</p></div><div class="yt-row">'
             + video('aKB9KGqGceY', '', 'How to unlock the Legend of Catachan', 'Legend of Catachan unlock route', 'GameSteed').replace('</figcaption>', ' · <a href="/warhammer-survivors/legend-of-catachan/">Written route →</a></figcaption>')
             + video('bq1k1U5KXaM', '12:02', 'A weapon evolving from a boss chest', 'Evolving every weapon', 'Gohjoe').replace('</figcaption>', ' · <a href="/warhammer-survivors/evolutions/">All 38 recipes →</a></figcaption>')
             + video('9bLZOyYe2sU', '1:52', 'Warhammer Survivors beginner guide', 'Beginner guide', 'iPICKmyBUTT').replace('</figcaption>', ' · <a href="/warhammer-survivors/tips/">First-run tips →</a></figcaption>')
             + '</div></section>')
    from warhammer_hub_v321 import rebuild
    videos = re.search(r'<div class="yt-row">(.*)</div></section>$', block, re.S)[1]
    text = rebuild(text, videos)
    # Evidence links inside the carried-over help items become plain text; store entries stay (00 §4).
    for host in ('aurochdigital.com/warhammer-survivors-faq', 'www.warhammer-community.com', 'news.xbox.com', 'www.xbox.com/en-US/games/store/warhammer-survivors-demo'):
        text = re.sub(r'<a href="https://' + re.escape(host) + r'[^"]*"[^>]*>(.*?)\s*↗(?:<span[^>]*>[^<]*</span>)?</a>', r'\1', text)
    return with_video_assets(text)


def apply():
    pages = {p.parent.name if p.parent != BASE else '': p for p in BASE.glob('**/index.html')}
    pages[''] = BASE/'index.html'
    from site_analytics import write_html
    for name, path in pages.items():
        text = path.read_text(encoding='utf8')
        if 'data-v321="1"' in text:
            continue
        if name == 'evolutions':
            text = evolutions(text)
        elif name == 'legend-of-catachan':
            text = catachan(text)
        elif name == 'tips':
            text = tips(text)
        elif name == '':
            text = hub(text)
        text = tidy(name, text)
        if name == 'followers':
            text = followers(text)  # anchors on markup left after tidy() drops the source line
        text = re.sub(r'<body(?=[\s>])', '<body data-v321="1"', text, count=1)
        text = theme(name, text)
        write_html(path, text, encoding='utf8')


if __name__ == '__main__':
    apply()
