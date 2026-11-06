"""Guard reviewed source presentation and provenance after regeneration."""
from pathlib import Path
import json,re
from remaining_editorial import edit
ROOT=Path(__file__).resolve().parents[1]
records=json.loads((ROOT/'data/remaining-editorial.json').read_text(encoding='utf8'))
for name,rule in records.items():
 text=(ROOT/name).read_text(encoding='utf8')
 assert 'data-editorial="20261106"' in text,name
 assert edit(ROOT/name,text)==text,('not idempotent',name)
 ids=re.findall(r'\bid="([^"]+)"',text)
 assert len(ids)==len(set(ids)),('duplicate IDs',name)
 assert all(x in ids for x in re.findall(r'href="#([^"]+)"',text)),('broken anchor',name)
 if rule['mode']=='natural':assert '<sup class="ref">' not in text,name
 section=re.search(r'<section[^>]*id="sources"[^>]*>.*?</section>',text,re.S)[0]
 assert not any(x in section for x in ['SINGLE_SOURCE','NOT_VERIFIED','HTTP403','SHA-256']),name
 for n,url in re.findall(r'<li[^>]*id="source-(\d+)"[^>]*>\s*<a[^>]*href="([^"]+)"',section):
  assert url==rule['sources'][n]['url'],('source changed',name,n)
 for caption in re.findall(r'<figcaption[^>]*>(.*?)</figcaption>',text,re.S):
  assert caption not in rule.get('captions',{}) or rule['captions'][caption]==caption,('old caption',name)
print(f'PASS: {len(records)} reviewed pages; source identity, natural citations, captions, anchors and idempotency')
