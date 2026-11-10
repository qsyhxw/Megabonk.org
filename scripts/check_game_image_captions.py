"""Guard reviewed captions and local image destinations across game sections."""
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import re

from remaining_editorial import caption_records, edit_captions

ROOT = Path(__file__).resolve().parents[1]
FIGURE = re.compile(r'<figure\b[^>]*>.*?</figure>', re.S)
CAPTION = re.compile(r'<figcaption[^>]*>(.*?)</figcaption>', re.S)


class ImageLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.anchors = []
        self.external = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'a':
            self.anchors.append(attrs.get('href', ''))
        if tag == 'img':
            self.external.extend(url for url in self.anchors
                                 if url.startswith(('http:', 'https:', '//')))

    def handle_endtag(self, tag):
        if tag == 'a' and self.anchors:
            self.anchors.pop()


def main():
    policies = caption_records()
    games = json.loads((ROOT/'data/game-sections.json').read_text(encoding='utf8'))
    pages = 0
    figures = 0
    for game in games:
        if game['id'] == 'vampire-survivors':
            continue  # Covered by the existing explicit guide-image policy.
        for path in sorted((ROOT/game['id']).rglob('*.html')):
            key = path.relative_to(ROOT).as_posix()
            text = path.read_text(encoding='utf8')
            if key == 'hordes-of-azeroth/index.html':
                hero_caption = re.search(r'</header><p class="meta">(.*?)</p>', text, re.S)
                assert hero_caption and hero_caption[1] == 'Early v0.1 gameplay frame.', key
            links = ImageLinks()
            links.feed(text)
            assert not links.external, ('external image destination', key, links.external)
            rules = {entry['image']: entry for entry in policies.get(key, [])}
            seen = set()
            for figure in FIGURE.findall(text):
                figures += 1
                image = re.search(r'<img\b[^>]*\bsrc="([^"]+)"', figure)
                caption = CAPTION.search(figure)
                assert not re.search(r'<a\b[^>]*href="(?:https?:)?//', figure), key
                if image and image[1] in rules:
                    seen.add(image[1])
                    expected = escape(rules[image[1]]['caption'])
                    assert (caption[1] if caption else '') == expected, ('caption', key)
                elif caption:
                    raise AssertionError(('unreviewed image caption', key))
            assert seen == set(rules), ('reviewed image missing', key)
            assert edit_captions(path, text) == text, ('not idempotent', key)
            pages += 1
    # Replay each original caption through the production path so rebuilding
    # old generators cannot restore source links or verbose inspection notes.
    for key, entries in policies.items():
        for entry in entries:
            original = ('<figure><img src="'+entry['image']+'"><figcaption>'
                        +entry['original_html']+'</figcaption></figure>')
            result = edit_captions(ROOT/key, original)
            expected = escape(entry['caption'])
            assert (CAPTION.search(result)[1] if expected else '') == expected, key
            assert bool(CAPTION.search(result)) == bool(expected), key
            changed = original.replace(entry['original_html'], 'Unexpected new credit')
            try:
                edit_captions(ROOT/key, changed)
            except ValueError:
                pass
            else:
                raise AssertionError(('changed credit was silently replaced', key))
    print(f'PASS: {pages} pages, {figures} figures, {len(policies)} caption policies; '
          'local image links, reviewed captions and regeneration')


if __name__ == '__main__':
    main()
