"""Protect concise source presentation through normal and scheduled builds."""
from pathlib import Path
import re,json
ROOT=Path(__file__).resolve().parents[1]
records=json.loads((ROOT/'data/azeroth-editorial.json').read_text(encoding='utf8'))
for path,record in records.items():
 text=(ROOT/path).read_text(encoding='utf8')
 slug=path.removeprefix('azeroth-survivors/').removesuffix('index.html').strip('/')
 ids=re.findall(r'\bid="([^"]+)"',text)
 assert len(ids)==len(set(ids)),path
 assert all(x in ids for x in re.findall(r'href="#([^"]+)"',text)),path
 assert all('<figcaption' not in f for f in re.findall(r'<figure class="game-image[^>]*>.*?</figure>',text,re.S)),path
 # v3.20: evidence stays in data/azeroth-editorial.json; pages carry no Sources section or [n] markers.
 assert '<section class="sources"' not in text and '<sup class="ref">' not in text,path
 assert 'SHA-256' not in text and 'HTTP403' not in text,path
 assert 'top Play entry uses the separately labelled third-party provider' not in text
print(f"PASS: {len(records)} Azeroth editorial pages; no public source lists, fragment links, caption-free figures and original-host entry")
