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
  for w in m['sizes']:
   path=m['stem']+'-'+str(w)+'.webp';asset=ROOT/path.lstrip('/')
   if not asset.exists() or asset.read_bytes()[:4]!=b'RIFF':errors.append(route+': invalid WebP '+path)
   if path not in text:errors.append(route+': missing responsive source '+path)
  if 'og:image' not in text or m['stem']+'-'+str(max(m['sizes']))+'.webp' not in text:errors.append(route+': missing actual page image')
 for e in errors:print('FAIL',e)
 print(('PASS' if not errors else 'FAIL')+f': {len(data["pages"])} content pages / {len(data["media"])} reviewed game images; all responsive assets, descriptions and generated figures checked. Relevance and visual readability require browser review.')
 return int(bool(errors))
if __name__=='__main__':raise SystemExit(check())
