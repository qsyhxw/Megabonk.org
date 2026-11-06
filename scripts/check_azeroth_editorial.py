"""Protect concise source presentation through normal and scheduled builds."""
from pathlib import Path
import re,json
from azeroth_editorial import NATURAL
ROOT=Path(__file__).resolve().parents[1]
records=json.loads((ROOT/'data/azeroth-editorial.json').read_text(encoding='utf8'))
for path,record in records.items():
 text=(ROOT/path).read_text(encoding='utf8')
 slug=path.removeprefix('azeroth-survivors/').removesuffix('index.html').strip('/')
 ids=re.findall(r'\bid="([^"]+)"',text)
 assert len(ids)==len(set(ids)),path
 assert all(x in ids for x in re.findall(r'href="#([^"]+)"',text)),path
 if slug in NATURAL:assert '<sup class="ref">' not in text,path
 assert all('<figcaption' not in f for f in re.findall(r'<figure class="game-image[^>]*>.*?</figure>',text,re.S)),path
 section=re.search(r'<section[^>]*id="sources"[^>]*>.*?</section>',text,re.S)[0]
 assert 'SHA-256' not in section and 'HTTP403' not in section,path
 for source in record['sources']:
  # Image-only citations can disappear when the figure no longer creates one.
  if source['id'] in re.findall(r'id="source-(\d+)"',text):
   assert 'href="'+source['url']+'"' in text,(path,source['id'])
 assert 'top Play entry uses the separately labelled third-party provider' not in text
print(f'PASS: {len(records)} Azeroth editorial pages; citations, source anchors, caption-free figures and original-host entry')
