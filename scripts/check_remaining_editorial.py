"""Guard reviewed pages after regeneration (v3.20: no public source list; evidence stays in data/remaining-editorial.json)."""
from pathlib import Path
import json,re
from remaining_editorial import edit
ROOT=Path(__file__).resolve().parents[1]
records=json.loads((ROOT/'data/remaining-editorial.json').read_text(encoding='utf8'))
for name,rule in records.items():
 text=(ROOT/name).read_text(encoding='utf8')
 assert 'data-v320="1"' in text,name
 assert edit(ROOT/name,text)==text,('not idempotent',name)
 ids=re.findall(r'\bid="([^"]+)"',text)
 assert len(ids)==len(set(ids)),('duplicate IDs',name)
 assert all(x in ids for x in re.findall(r'href="#([^"]+)"',text)),('broken anchor',name)
 assert '<sup class="ref">' not in text and '<section class="sources"' not in text,name
 # Internal evidence labels must not leak; a player instruction to check a release SHA-256 is allowed.
 assert not any(x in text for x in ['SINGLE_SOURCE','NOT_VERIFIED','HTTP403']),name
 for caption in re.findall(r'<figcaption[^>]*>(.*?)</figcaption>',text,re.S):
  assert caption not in rule.get('captions',{}) or rule['captions'][caption]==caption,('old caption',name)
print(f'PASS: {len(records)} reviewed pages; no public source lists, captions, anchors and idempotency')
