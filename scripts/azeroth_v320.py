"""v3.20 presentation pass for the Azeroth Survivors section (applied last in build).

Evidence (source URLs, dated scopes, "not tested" limits) stays in
scripts/azeroth_survivors_content.py SOURCES and data/azeroth-*.json. Public pages
drop the Sources section, [n] markers, repeated status boilerplate and
"opens in a new tab" screen-reader sentences; action links stay in their steps.
The #source-sync element keeps its id and data-* attributes for the sync checks,
with one visible line.
"""
import re

REF = re.compile(r'<sup class="ref">.*?</sup>', re.S)
SOURCES = re.compile(r'<section class="sources"[^>]*>.*?</section>', re.S)
TOC_SOURCE = re.compile(r'<a href="#sources">[^<]*</a>')
SR_NEWTAB = re.compile(r'<span class="sr-only">\s*\((?:external website, )?opens in a new tab\)</span>')
SYNC = re.compile(r'<aside class="source-status[^"]*" id="source-sync"([^>]*)>.*?</aside>', re.S)
BYLINE = re.compile(r'<p class="(?:meta|byline)">(.*?)</p>', re.S)
# Evidence-only targets: keep the words, drop the outbound link (00 §4).
EVIDENCE = re.compile(r'<a [^>]*href="https?://(?:wow\.aethus\.pl/(?:assets|js|data|api)/[^"]*|github\.com/qsyhxw/[^"]*)"[^>]*>(.*?)</a>', re.S)

# Hub: identification/credit links are evidence for a name, not reader actions.
# Keep the project names as text; same-site entries cover the related games.
HUB_TEXT_ONLY = re.compile(r'<a [^>]*href="https?://(?:thewowdb\.com|arenaofchampions\.live|github\.com|www\.pawsmonaut\.games|www\.curseforge\.com|worldofwarcraft\.blizzard\.com|news\.blizzard\.com|d2survivors\.lol|azerothsurvivors\.org|www\.reddit\.com|docs\.virustotal\.com)[^"]*"[^>]*>(.*?)</a>', re.S)
# Repeated play links on the hub: keep the first hero button and the Discord entry.
HUB_DUP_PLAY = re.compile(r'<a [^>]*href="https://wow\.aethus\.pl/"[^>]*>(Aethus · (?:original game|wow\.aethus\.pl|original browser game|original host)) ↗</a>')

HEDGE = [
    'This is an editorial choice order, not a guaranteed card sequence.',
    'This is an editorial route decision from the preserved snapshot, not a complete legal point allocation or measured best build.',
    'It is a practical core to examine, not a measured best build or proof that your character has earned the points.',
    'In-game installation not tested.',
    'Completion and reward delivery have not been tested here.',
    'This is an editorial task order, not a mandatory purchase build.',
    'These are editorial kit-based picks, not measured win-rate tiers.',
    'Not measured here; no numeric or S–D ceiling ordering is justified.',
    'This gives an editorial starting suggestion, not a measured strongest class.',
    'We have not measured clear rates or run a controlled damage test, so there is no universal S-to-D performance table.',
    'Source changes detected: this editorial route needs review against the latest client.',
    'We have not tested message delivery, shared loot/XP rules or a full revive cycle; those remain outside this workflow.',
    'Three spec slots appear on the current menu; we have not tested switching saved allocations across all versions.',
]
REWRITE = [
    ('We have not tested every cross-version import, so a rejected file is a reason to keep the original and compare versions, not to alter its contents.',
     'If the game rejects a file, keep the original and compare versions instead of editing its contents.'),
    ('We have not verified original-to-third-party import compatibility; preserve both sides before any replacement.',
     'Original-to-third-party import is not confirmed, so keep both saves before replacing either.'),
]
BYLINE_PARTS = re.compile(r'\s*·\s*(?:No new full-run test|No matched-run benchmark|Rat Den Gaming ranking dated [^·]*|Original v[0-9.]+ mechanic notes|Source-based, not a playtest|Source-based guide|'
                          r'Earlier [^·]*retained[^·]*|New advice scoped to[^·]*|earlier sections retain their dates)', re.I)

FORMATS = {
    '': 'hub', 'play': 'play', 'beginners-guide': 'beginner', 'builds': 'build', 'best-class': 'tier',
    'tier-list': 'tier', 'best-race': 'database', 'abilities': 'database', 'armory': 'database',
    'talents': 'database', 'download-platforms': 'platform', 'co-op': 'platform', 'mobile': 'platform',
    'troubleshooting': 'fix', 'save-backup': 'fix', 'addons': 'fix', 'zones-bosses': 'location',
}


CLASSES = ('warrior', 'mage', 'warlock', 'paladin', 'hunter', 'rogue', 'priest', 'druid', 'shaman')
TASKS = (('beginners-guide/', 'Beginner guide'), ('builds/', 'All builds'), ('tier-list/', 'Tier list'),
         ('best-class/', 'Best class'), ('talents/', 'Talents'), ('save-backup/', 'Save backup'))


def hub_entries():
    icons = ''.join(f'<a class="class-entry" href="/azeroth-survivors/builds/{c}/">'
                    f'<img src="/assets/azeroth-survivors/icons/{c}.png" width="40" height="40" alt="">'
                    f'<span>{c.title()}</span></a>' for c in CLASSES)
    tasks = ''.join(f'<a href="/azeroth-survivors/{u}">{l}</a>' for u, l in TASKS)
    return (f'<nav class="hub-entries" aria-label="Azeroth Survivors builds and guides">'
            f'<p class="hub-entries-label">Class builds</p><div class="class-row">{icons}</div>'
            f'<div class="task-row">{tasks}</div></nav>')


def _sync(match):
    attrs = match[1]
    return (f'<aside class="source-status sync-line" id="source-sync"{attrs}><p>Game data checked against the latest original client · '
            '<a href="/azeroth-survivors/patch-notes/#source-monitor">What changed</a></p></aside>')


def present(path, html):
    """Apply to one generated page; trust/404/localized play pages keep their own copy."""
    if path.endswith('404.html'):
        return html
    slug = path.removeprefix('/azeroth-survivors/').strip('/')
    if slug.split('/')[0] in ('ru', 'de', 'zh-hant'):
        fmt = 'build' if slug.endswith('builds') else 'other'
    else:
        fmt = 'build' if slug.startswith('builds/') else FORMATS.get(slug, 'other')
    # Registered figcaptions are normalised later by remaining_editorial; leave them intact.
    caps = []
    s = re.sub(r'<figcaption.*?</figcaption>', lambda m: caps.append(m[0]) or f'@@CAP{len(caps)-1}@@', html, flags=re.S)
    s = SOURCES.sub('', s)
    s = REF.sub('', s)
    s = TOC_SOURCE.sub('', s)
    s = SR_NEWTAB.sub('', s)
    s = EVIDENCE.sub(lambda m: m[1].replace(' ↗', ''), s)
    for sentence in HEDGE:
        s = s.replace(' ' + sentence, '').replace(sentence, '')
    for old, new in REWRITE:
        s = s.replace(old, new)
    if slug == '' or slug == 'download-platforms':
        s = HUB_TEXT_ONLY.sub(lambda m: m[1].replace(' ↗', ''), s)
    if slug == '':
        s = HUB_DUP_PLAY.sub(lambda m: m[1], s)
        s = re.sub(r'(</section>\s*)(<div class="statusbar">)', lambda m: m[1] + hub_entries() + m[2], s, count=1)
    s = re.sub(r'@@CAP(\d+)@@', lambda m: caps[int(m[1])], s)
    s = BYLINE.sub(lambda m: m[0].replace(m[1], BYLINE_PARTS.sub('', m[1])), s, count=1)
    s = SYNC.sub(_sync, s, count=1)
    s = re.sub(r'<p>\s*</p>', '', s)
    from azeroth_answers import present_answers, hub_block
    s = present_answers(path, s)
    if slug == '':
        # Class cards replace the icon-only class row; keep the task links row.
        s = re.sub(r'<p class="hub-entries-label">Class builds</p><div class="class-row">.*?</div>', '', s, count=1, flags=re.S)
        s = s.replace('<nav class="hub-entries"', hub_block() + '<nav class="hub-entries"', 1)
    if 'data-format=' not in s[:4000]:
        s = s.replace('<body class="', f'<body data-format="{fmt}" class="', 1)
    return s
