"""v3.20 presentation pass for the PokeBonk section (runs last in build_pokebonk).

Readers get answers, not the evidence trail: source URLs, check dates and
SINGLE_SOURCE limits stay in the generators, data/*.json and FACT_CHECK. This
pass removes the public Sources section, [n] markers, repeated "checked /
source-based / not tested" boilerplate and screen-reader "opens in a new tab"
sentences, keeps action links (play / download / redeem) in their steps, and
rewrites the hub hero so the H1 names the game.

Contract checked by scripts/check_pokebonk_v320.py and content_gate.py.
"""
import re

REF = re.compile(r'<sup class="ref">.*?</sup>', re.S)
SOURCES = re.compile(r'<section class="sources"[^>]*>.*?</section>', re.S)
TOC_SOURCE = re.compile(r'<a href="#sources">[^<]*</a>')
SR_NEWTAB = re.compile(r'<span class="sr-only">\s*\(external website, opens in a new tab\)</span>')
META = re.compile(r'<p class="meta">(.*?)</p>', re.S)
SYNC = re.compile(r'<aside id="source-sync"([^>]*)>.*?</aside>', re.S)
PORTRAIT_CREDIT = re.compile(r'<section class="portrait-credit" id="portrait-credits"><h2>Pokémon image credits</h2>.*?</section>', re.S)
CREDIT_NOTE = ('<p class="credit-note" id="portrait-credits">Pokémon images and names belong to Nintendo, Creatures Inc. and GAME FREAK Inc.; '
               'shown for identification. <a href="/pokebonk/contact/">Rights contact</a>.</p>')

# Evidence-only targets: keep the visible words, drop the outbound link (00 §4).
EVIDENCE = re.compile(r'<a [^>]*href="https?://(?:pokebonk\.com/(?:assets/[^"]*|version\.json|legal)|api\.pokebonk\.com/[^"]*|github\.com/qsyhxw/[^"]*)"[^>]*>(.*?)</a>', re.S)

# Whole sentences that only state our evidence status (no player action).
HEDGE_SENTENCES = [
    'Source-described passive, including its stated conditions; not a measured strength ranking.',
    'Source-based instructions.',
    'Extraction, recovery, installation and competitive results were not playtested.',
    'New task-specific additions reviewed October 28 against the original v0.8.62 client; recommendations remain source-based.',
    'Recommendations here are source-based decisions; no original-game full clear, catch, reward claim or co-op completion was tested.',
    'Calculated baselines exclude passives, Lab, items and vitamins; runtime move templates are not measured DPS.',
    'This guide contains no claimed personal clear.',
    'Use it as an optional introduction alongside the checked written reference, not as our gameplay test.',
    'A client definition is not a measured win rate or a phone compatibility test.',
    'We do not label those as tested.',
    'These are editorial planning directions based on current passive and kit descriptions, not clear-time, DPS or win-rate rankings.',
    'These are editorial routes from current kits and fusion definitions, not a guaranteed offer sequence or measured strongest build.',
    'These are source-based practice drafts, not measured best builds.',
    'These are editorial practice drafts from checked kit and effect definitions, not proven best builds or measured clear times.',
    'This guide has not claimed a prize or reproduced the reset boundary.',
    'The variant decisions are editorial interpretations of checked rules, not benchmarked builds.',
    'No use was tested here.',
    'This is editorial learning advice, not a measured easiest or fastest clear.',
    'These are spending decisions derived from the mechanics, not a measured optimal purchase order.',
    'We have not completed this climb or measured a safe build.',
]

# Sentence-level boilerplate. Each pattern removes a whole sentence that only
# restates evidence status; version conditions that change a decision stay.
BOILERPLATE = [
    r'\s*This is a planning aid, not a guaranteed drop sequence or an independently tested strongest build\.',
    r'\s*This is a source-based build plan, not a measured best-DPS build\.',
    r'\s*These are passive-based suggestions, not measured win rates\.',
    r'\s*These recommendations interpret the current passives; they are not a tested PokeBonk tier list or a claim about the strongest endgame Pokémon\.',
    r'\s*The table compares kits and trade-offs; it does not invent S–D strength scores or win rates from base stats\.',
    r'\s*Pick the role you want to learn; these are not measured strength tiers\.',
    r'\s*We have not tested conversion, recovery or the inactivity deadline\.',
    r'\s*We have not tested router, VPN or corporate-network fixes;',
    r'\s*本文依据当前菜单与公开客户端整理，没有冒称通关实测。',
    r'\s*此项未实测恢复成功。',
    r'\s*Use the arena prompts to adjust your timing; this is a source-based route\.',
]


def _meta(match, lang):
    """Keep one dated line: 'Megabonk.org · Updated <date> · <version>'."""
    parts = [p.strip() for p in re.sub(r'<br\s*/?>', ' · ', match[1]).split('·')]
    date = next((re.sub(r'^(Checked|Gameplay review:|Updated)\s*', '', p) for p in parts
                 if re.match(r'(Checked|Gameplay review:|Updated)\b', p)), '')
    version = next((p for p in parts if re.search(r'\bv?\d+\.\d+', p) and not re.match(r'(Checked|Updated)', p)), '')
    version = version.replace('Beta ', '')
    bits = ['Megabonk.org'] + ([f'Updated {date}'] if date else []) + ([version] if version else [])
    if lang != 'en':
        return f'<p class="meta">{match[1]}</p>'
    return '<p class="meta">' + ' · '.join(bits) + '</p>'


def _sync(match, version):
    # Keep the element id/revision for the automated sync checks, one line of text.
    attrs = re.sub(r'\s*class="[^"]*"', '', match[1])
    return (f'<aside id="source-sync"{attrs} class="sync-line"><p>Game data: '
            f'<strong>v{version}</strong> · <a href="/pokebonk/updates/">What changed</a></p></aside>')


HUB_HERO = re.compile(r'<h1>PokeBonk\.<br><em>Big adventure\.</em></h1>')
HUB_ACTIONS = (
    ('beginners-guide/', 'Beginner guide', 'First run, controls, saves', 25),
    ('builds/', 'Builds', 'Copy a current partner build', 63),
    ('tier-list/', 'Tier list', 'All partners by role', 150),
    ('starters/', 'Starters', 'Bulbasaur, Squirtle or Charmander', 1),
    ('pokemon/', 'Pokémon database', 'Every League partner', 133),
    ('move-fusions/', 'Move fusions', 'Fusion recipes', 4),
    ('evolution/', 'Evolution', 'Levels and branches', 133),
    ('how-to-catch-pokemon/', 'How to catch', 'Unlock new partners', 143),
    ('mobile/', 'Mobile', 'Phone and APK', 7),
)
PORTRAIT = '/assets/pokebonk/portraits/{:03d}.png'


def portrait_strip(ids, label):
    imgs = ''.join(f'<img src="{PORTRAIT.format(i)}" width="64" height="64" alt="{label[i]}" loading="lazy">'
                   for i in ids if i in label)
    return f'<div class="portrait-strip">{imgs}</div>'


# Pages whose subject is a set of partners: show them before the first section.
PAGE_PORTRAITS = {
    'builds': [1, 4, 7, 63, 133, 25, 92, 147],
    'abra-build': [63],
    'how-to-win': [1, 4, 7, 150], 'luck-status-chance': [25, 133, 143],
    'how-to-catch-pokemon': [144, 145, 146, 150, 151],
    'mewtwo': [150, 144, 145, 146],
    'articuno': [144], 'zapdos': [145], 'lavender-tower': [92, 93, 94],
    'unlocks': [1, 4, 7, 25, 133],
    'beginners-guide': [1, 4, 7], 'zh/beginners-guide': [1, 4, 7], 'ko/beginners-guide': [1, 4, 7],
}


def _hub(html, ctx):
    # H1 already names the game; TDK protected (00 §5A). Add a plain subtitle only.
    html = HUB_HERO.sub(lambda m: m[0] + '<p class="hero-sub">PokeBonk guide &amp; wiki: builds, partners and fixes for the Pokémon browser survivor.</p>', html, count=1)
    pages = ctx['PAGES']
    cards = ''.join(
        f'<a class="task" href="/pokebonk/{slug}"><img src="{PORTRAIT.format(pid)}" width="48" height="48" alt="">'
        f'<strong>{label}</strong><span>{note}</span></a>'
        for slug, label, note, pid in HUB_ACTIONS if '/pokebonk/' + slug in pages)
    tasks = f'<nav class="task-grid" aria-label="PokeBonk guides">{cards}</nav>'
    # Task entries directly under the hero, before the long explanatory sections.
    from pokebonk_answers import hub_preview
    html = html.replace('<div class="statusbar">', tasks + hub_preview() + '<div class="statusbar">', 1)
    return html


FORMATS = {
    '': 'hub', 'play': 'play', 'beginners-guide': 'beginner', 'zh/beginners-guide': 'beginner',
    'ko/beginners-guide': 'beginner', 'builds': 'build', 'abra-build': 'build', 'build-planner': 'other',
    'tier-list': 'tier', 'pokemon': 'database', 'moves': 'database', 'move-fusions': 'database',
    'items-vitamins': 'database', 'type-chart': 'database', 'lab': 'database', 'ultimates': 'database',
    'mobile': 'platform', 'es/mobile': 'platform', 'steam-deck': 'platform', 'multiplayer': 'platform',
    'mewtwo': 'location', 'zapdos': 'location', 'articuno': 'location', 'lavender-tower': 'location',
    'how-to-catch-pokemon': 'location', 'unlocks': 'location',
}


def apply_v320(ctx):
    from pokebonk_answers import apply_answers
    apply_answers(ctx['PAGES'])
    import json
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    version = json.loads((root / 'data/pokebonk-sync.json').read_text(encoding='utf8'))['observed']['version']
    meta = json.loads((root / 'data/pokebonk-portraits.json').read_text(encoding='utf8'))
    names = {x['id']: x['name'] for x in meta['images']
             if (root / x['local_path']).exists()}
    for path, page in ctx['PAGES'].items():
        slug = path.removeprefix('/pokebonk/').strip('/')
        if slug in ('contact', 'privacy'):
            continue
        s = page['html']
        lang = re.search(r'<html lang="([^"]+)"', s)[1]
        s = SOURCES.sub('', s)
        s = PORTRAIT_CREDIT.sub(CREDIT_NOTE, s)
        s = REF.sub('', s)
        s = TOC_SOURCE.sub('', s)
        s = SR_NEWTAB.sub('', s)
        s = EVIDENCE.sub(lambda m: m[1].replace(' ↗', ''), s)
        s = s.replace(' · Source-based guide', '').replace('Source-based guide · ', '')
        for sentence in HEDGE_SENTENCES:
            s = s.replace(' ' + sentence, '').replace(sentence + ' ', '').replace(sentence, '')
        for pat in BOILERPLATE:
            s = re.sub(pat, '', s)
        s = META.sub(lambda m: _meta(m, lang), s, count=1)
        s = SYNC.sub(lambda m: _sync(m, version), s, count=1)
        s = re.sub(r'<p>\s*</p>', '', s)
        if slug in PAGE_PORTRAITS:
            strip = portrait_strip(PAGE_PORTRAITS[slug], names)
            s = re.sub(r'(<article class="prose">)', lambda m: m[1] + strip, s, count=1)
            if 'id="portrait-credits"' not in s:
                s = s.replace('</main>', CREDIT_NOTE + '</main>', 1)
        if slug == '':
            s = _hub(s, ctx)
            if 'id="portrait-credits"' not in s:
                s = s.replace('</main>', CREDIT_NOTE + '</main>', 1)
        s = s.replace('<body class="', '<body data-format="' + FORMATS.get(slug, 'other') + '" class="', 1)
        page['html'] = s
