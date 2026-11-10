"""Check the reviewed page-image map and physical responsive assets (no network)."""
from pathlib import Path
from html.parser import HTMLParser
import json
ROOT=Path(__file__).resolve().parents[1]
class Images(HTMLParser):
 def __init__(self):super().__init__();self.active=False;self.pictures=[]
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t=='figure' and 'data-game-image' in a:self.active=True
  if t=='img' and self.active:self.pictures.append(a)
 def handle_endtag(self,t):
  if t=='figure':self.active=False
def check():
 data=json.loads((ROOT/'data/guide-images.json').read_text(encoding='utf8'));errors=[]
 for route,p in data['pages'].items():
  f=ROOT/route.lstrip('/')/'index.html';text=f.read_text(encoding='utf8')
  doc=Images();doc.feed(text)
  if len(doc.pictures)!=1:errors.append(route+': expected exactly one reviewed game figure');continue
  a=doc.pictures[0];m=data['media'][p['image']]
  if not a.get('alt') or not a.get('width','').isdigit() or not a.get('height','').isdigit():errors.append(route+': missing alt/dimensions')
  if p['alt']!=a.get('alt'):errors.append(route+': wrong page-specific image description')
  if p.get('citation_mode')=='none' and 'caption_text' in p:
   import re
   from html import unescape
   figures=re.findall(r'<figure\b[^>]*data-game-image[^>]*>.*?</figure>',text,re.S)
   for figure in figures:
    caption=re.search(r'<figcaption>(.*?)</figcaption>',figure,re.S)
    expected=p.get('caption_text','')
    if (unescape(caption[1]) if caption else '')!=expected:errors.append(route+': visible caption differs from reviewed short caption')
    if caption and re.search(r'<a\b',caption[1]):errors.append(route+': unexpected caption link')
    if 'image-zoom' in figure:errors.append(route+': redundant image zoom text')
    if re.search(r'href="https?://',figure):errors.append(route+': game image leaves site')
  if a.get('loading')!=p.get('loading','lazy'):errors.append(route+': image loading priority differs from reviewed viewport plan')
  for w in m['sizes']:
   path=m['stem']+'-'+str(w)+'.webp';asset=ROOT/path.lstrip('/')
   if not asset.exists() or asset.read_bytes()[:4]!=b'RIFF':errors.append(route+': invalid WebP '+path)
   if path not in text:errors.append(route+': missing responsive source '+path)
  if 'og:image' not in text or m['stem']+'-'+str(max(m['sizes']))+'.webp' not in text:errors.append(route+': missing actual page image')
 # Original PNGs retain their complete source pixels and their own provenance map.
 for name,m in json.loads((ROOT/'data/pokerogue-media.json').read_text(encoding='utf8')).items():
  asset=ROOT/'assets/pokerogue'/name
  if not asset.exists() or asset.read_bytes()[:8]!=b'\x89PNG\r\n\x1a\n':errors.append(name+': missing original PNG');continue
  import struct
  if list(struct.unpack('>II',asset.read_bytes()[16:24]))!=m['dimensions']:errors.append(name+': unexpected original dimensions')
  for route in [m['page']]+m.get('also_used_on',[]):
   page=(ROOT/route).read_text(encoding='utf8')
   if '/assets/pokerogue/'+name not in page or not m.get('source'):errors.append(name+': missing page/provenance association '+route)
 for e in errors:print('FAIL',e)
 print(('PASS' if not errors else 'FAIL')+f': {len(data["pages"])} content pages / {len(data["media"])} reviewed game images; all responsive assets, descriptions and generated figures checked. Relevance and visual readability require browser review.')
 return int(bool(errors))
if __name__=='__main__':raise SystemExit(check())
