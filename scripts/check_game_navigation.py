"""Prevent cross-game guide menus and per-article root discovery cards."""
from pathlib import Path
from html.parser import HTMLParser
import json
ROOT=Path(__file__).resolve().parents[1]
GAMES=json.loads((ROOT/'data/game-sections.json').read_text(encoding='utf8'))
class Doc(HTMLParser):
 def __init__(self):super().__init__();self.n=False;self.a=None;self.links=[];self.cards=[]
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t=='nav':self.n=bool(set(a.get('class','').split())&{'desktop-nav','mobile-links','toc'})
  if t=='a' and self.n:self.a=[a.get('href',''),'']
  if 'data-game' in a:self.cards.append(a['data-game'])
 def handle_data(self,s):
  if self.a:self.a[1]+=s
 def handle_endtag(self,t):
  if t=='a' and self.a:self.links.append(self.a);self.a=None
  if t=='nav':self.n=False

def check():
 errors=[];count=0
 for g in GAMES:
  folder=ROOT/g['id']
  files=list(folder.rglob('*.html'))
  if g['id']=='vampire-survivors':files.append(ROOT/'games-like-vampire-survivors/index.html')
  for f in files:
   p=Doc();p.feed(f.read_text(encoding='utf8'));count+=1
   for href,label in p.links:
    if href.startswith('#') or href.startswith('/'+g['id']+'/'):continue
    if href=='/#more-games' and ('games' in label.lower() or 'игры' in label):continue
    errors.append(f'{f.relative_to(ROOT)}: misleading/cross-game menu {label!r} -> {href}')
 root=(ROOT/'index.html').read_text(encoding='utf8');d=Doc();d.feed(root)
 if sorted(d.cards)!=sorted(g['id'] for g in GAMES):errors.append('Root requires exactly one card per registered game')
 start=root.index('<section id="wiki-start"');end=root.index('</section>',start);guide=root[start:end]
 for g in GAMES:
  if '/'+g['id']+'/' in guide:errors.append('Other game in Megabonk guide grid: '+g['id'])
 for crossgame in ['/games-like-vampire-survivors/','/guides/pokemon-games-like-megabonk/']:
  if crossgame in guide:errors.append('Cross-game comparison in main-game task grid: '+crossgame)
 if 'Looking for the Pokémon-style survivor?' in root:errors.append('Old one-game bottom promo remains')
 for g in GAMES:
  f=ROOT/g['url'].split('#')[0].lstrip('/')/'index.html'
  if not f.exists():errors.append('Discovery has missing destination: '+g['url'])
  for w in g['sizes']:
   if not (ROOT/(g['image'].lstrip('/')+'-'+str(w)+'.webp')).is_file():errors.append('Missing thumbnail '+g['id'])
 for e in errors:print('FAIL',e)
 print(('PASS' if not errors else 'FAILED')+f': {count} game-section pages checked for entity-scoped menus; {len(GAMES)} unique game cards; main-game guide grid separated.')
 return int(bool(errors))
if __name__=='__main__':raise SystemExit(check())
