"""Scoped presentation pass after dated fact/data modules; never refresh review dates.

Source URLs and historical snapshots stay in their original generators. Public
support summaries are authored per page in pokebonk-editorial.json. Unknown or
changed source identities fail rather than silently attaching the wrong summary.
"""
from pathlib import Path
from html import escape
import json
import re

ROOT = Path(__file__).resolve().parents[1]
REF = re.compile(r'<sup class="ref"><a href="#source-(\d+)"[^>]*>.*?</a></sup>')
NATURAL = {'', 'beginners-guide', 'mobile', 'play', 'zh/beginners-guide',
           'ko/beginners-guide', 'es/mobile'}


def apply_editorial(ctx):
    records = json.loads((ROOT / 'data/pokebonk-editorial.json').read_text(encoding='utf8'))
    for path, page in ctx['PAGES'].items():
        slug = path.removeprefix('/pokebonk/').strip('/')
        s = page['html']
        if slug == 'privacy':
            s = s.replace('This section adds no analytics tags.',
                          'This section also loads the site-wide Umami analytics service described below.')
            from site_analytics import NOTICE
            # Keep the actual disclosure within the article, not after the footer.
            notice = NOTICE.replace('This site-wide service also applies to sections described below as adding no separate analytics tag.', 'This service also applies to this guide section.')
            s = s.replace('</article>', notice + '</article>', 1)
        if slug not in records:
            page['html'] = s
            continue
        record = records[slug]
        source = re.search(r'<section class="sources"[^>]*>.*?</section>', s, re.S)
        if not source:
            raise ValueError('Missing sources: ' + path)
        links = {}
        items = []
        for n, body in re.findall(r'<li id="source-(\d+)">(.*?)</li>', source[0], re.S):
            anchor = re.search(r'<a\b.*?</a>', body, re.S)[0]
            url = re.search(r'href="([^"]+)"', anchor)[1]
            if 'automatically observed public configuration' in anchor:
                state = json.loads((ROOT / 'data/pokebonk-sync.json').read_text(encoding='utf8'))
                label = 'PokeBonk source version'
                desc = f"Version {state['observed']['version']} observed {state['changed_at'][:10]}; accepted data dates above."
            else:
                entry = record['sources'][n]
                if entry['url'] != url:
                    raise ValueError(f'Source changed: {path} #{n}')
                label, desc = entry['label'], entry['summary']
            links[n] = ctx['ext'](url, label)
            items.append(f'<li id="source-{n}">{links[n]} · {escape(desc)}</li>')
        if 'source_groups' in record:
            items = []
            for group in record['source_groups']:
                anchors = []
                for n, label in group['links']:
                    n = str(n)
                    a = re.sub(r'>[^<]+', '>' + escape(label) + ' ↗', links[n], count=1)
                    a = a.replace('<a ', f'<a id="source-{n}" ', 1)
                    anchors.append(a)
                items.append('<li>' + ' / '.join(anchors) + ' · ' + escape(group['summary']) + '</li>')
        heading = {'zh/beginners-guide': '检查依据', 'ko/beginners-guide': '출처 및 확인 범위',
                   'es/mobile': 'Fuentes y comprobaciones'}.get(slug, 'Sources &amp; checks')
        tag = 'ul' if slug in NATURAL else 'ol'
        scope = record.get('scope', '')
        scope = f'<p class="check-scope">{escape(scope)}</p>' if scope else ''
        replacement = f'<section class="sources" id="sources"><h2>{heading}</h2>{scope}<{tag}>'+''.join(items)+f'</{tag}><a class="back" href="#guide">Back to guide ↑</a></section>'
        s = s[:source.start()] + replacement + s[source.end():]
        # Self-evident entry screenshot: no routine provenance caption. Retain the
        # distinction for art/diagrams, which must not masquerade as screenshots.
        s = re.sub(r'<figcaption>Original game entry screen, captured.*?</figcaption>', '', s)
        s = s.replace('Official promotional artwork © Charcher / respective rights holders. Not a gameplay screenshot.', 'Promotional artwork.')
        s = re.sub(r'<figcaption>Editorial (?:workflow|decision diagram|planning diagram|reference diagram).*?</figcaption>', '<figcaption>Guide diagram.</figcaption>', s)
        for old, new in record.get('replacements', []):
            if old not in s:
                raise ValueError(f'Editorial replacement drift: {path}: {old[:60]}')
            s = s.replace(old, new)
        # This repeated boilerplate carries no extra evidence beyond the source
        # scope. Edition differences immediately before it are intentionally kept.
        s = s.replace(' Mechanics are SINGLE_SOURCE; no full-run, reward-claim or multiplayer completion test is claimed.', '')
        s = s.replace('They are SINGLE_SOURCE, not our completed boss run, measured success rate or a frame-perfect route.', 'Use the arena prompts to adjust your timing; this is a source-based route.')
        if slug in NATURAL:
            # Keep the consequential source in its sentence as a named link.
            for old, number, label in record.get('inline_links', []):
                if old not in s:
                    raise ValueError(f'Missing inline attribution: {path}: {old}')
                entry = record['sources'][str(number)]
                s = s.replace(old, ctx['ext'](entry['url'], label), 1)
            s = REF.sub('', s)
        else:
            # Drop only repetitions inside a single paragraph, never relocate a
            # table's citation or erase a different source in the same block.
            def dedupe(m):
                seen = set()
                def keep(ref):
                    n = ref[1]
                    if n in seen:
                        return ''
                    seen.add(n)
                    return ref[0]
                return REF.sub(keep, m[0])
            s = re.sub(r'<p\b[^>]*>.*?</p>', dedupe, s, flags=re.S)
        s = s.replace('SINGLE_SOURCE', 'the original project’s own data')
        page['html'] = s
