"""Guard editorial output after full generation, including automated data sync."""
from pathlib import Path
from html.parser import HTMLParser
import json
import re
from pokebonk_editorial import NATURAL

ROOT = Path(__file__).resolve().parents[1]
records = json.loads((ROOT / 'data/pokebonk-editorial.json').read_text(encoding='utf8'))

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.fragments = set(), []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            assert a['id'] not in self.ids, ('duplicate ID', a['id'])
            self.ids.add(a['id'])
        if tag == 'a' and a.get('href', '').startswith('#'):
            self.fragments.append(a['href'][1:])

for slug, record in records.items():
    text = (ROOT / 'pokebonk' / slug / 'index.html').read_text(encoding='utf8')
    parser = Links()
    parser.feed(text)
    assert all(not x or x in parser.ids for x in parser.fragments), slug
    assert not any(x in text for x in ['SINGLE_SOURCE', 'Missing mechanic base', "added: ['affinity']"]), slug
    if slug in NATURAL:
        assert '<sup class="ref">' not in text, slug
    assert '<section class="sources" id="sources">' in text, slug
    active = {str(n) for g in record.get('source_groups', []) for n, _ in g['links']}
    for n, entry in record['sources'].items():
        if not active or n in active:
            assert f'href="{entry["url"]}"' in text, (slug, n)
    assert 'figcaption>Original game entry screen, captured' not in text, slug

privacy = (ROOT / 'pokebonk/privacy/index.html').read_text(encoding='utf8')
assert 'This section adds no analytics tags.' not in privacy
assert privacy.count('id="umami-analytics"') == 1
assert privacy.index('id="umami-analytics"') < privacy.index('</article>')
print(f'PASS: {len(records)} editorial pages, source identities, fragment links, natural citations and privacy disclosure')
