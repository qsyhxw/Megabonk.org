"""Apply reviewed access and troubleshooting changes after historical generators."""
from pathlib import Path
from html import escape
import json
import re

ROOT = Path(__file__).resolve().parents[1]


def apply_main_first(ctx):
    data = json.loads((ROOT / 'data/pokebonk-main-first.json').read_text(encoding='utf-8'))
    for slug, record in data['pages'].items():
        page = ctx['PAGES']['/pokebonk/' + slug + '/']
        text = page['html']
        for ident, body in record.get('sections', {}).items():
            pattern = r'(<section\b[^>]*id="' + re.escape(ident) + r'"[^>]*><h2>.*?</h2>).*?</section>'
            text, count = re.subn(pattern, lambda match: match[1] + body + '</section>', text, count=1, flags=re.S)
            if count != 1:
                raise ValueError(f'Missing reviewed section {slug}#{ident}')
        for old, new in record.get('replacements', []):
            if old not in text:
                raise ValueError(f'Missing reviewed text in {slug}: {old[:80]}')
            text = text.replace(old, new)
        if record.get('addition'):
            addition = '<section id="current-check"><h2>' + record['heading'] + '</h2>' + record['addition'] + '</section>'
            text = text.replace('<section class="sources"', addition + '<section class="sources"', 1)
            text = text.replace('<strong>On this page</strong>', '<strong>On this page</strong><a href="#current-check">' + record['heading'] + '</a>', 1)
        if record.get('image'):
            media = data['media'][record['image']]
            image = f'<figure class="game-image"><a href="{media["asset"]}" target="_blank" rel="noopener" aria-label="Open full image"><img src="{media["asset"]}" width="{media["width"]}" height="{media["height"]}" alt="{escape(record["alt"], quote=True)}" loading="lazy"></a></figure>'
            text, count = re.subn(r'<figure\b[^>]*>.*?</figure>', lambda _: image, text, count=1, flags=re.S)
            if count == 0:
                text, count = re.subn(r'(<article class="prose">)', lambda m: m[1] + image, text, count=1)
                if count != 1:
                    raise ValueError('Missing article image insertion: ' + slug)
            text = re.sub(r'(<meta property="og:image" content=")[^"]+', lambda m: m[1] + 'https://megabonk.org' + media['asset'], text, count=1)
        note = '<p class="note">' + record['review'] + '</p>'
        text = re.sub(r'(<p class="meta">.*?</p>)', lambda m: m[1] + note, text, count=1, flags=re.S)
        support = '<p>' + record['support'] + ' ' + ctx['ext'](data['source'], record.get('source_label', 'Original project release notes')) + '</p>'
        text = re.sub(r'(<section class="sources"[^>]*><h2>.*?</h2>)', lambda m: m[1] + support, text, count=1, flags=re.S)
        page['html'] = text
