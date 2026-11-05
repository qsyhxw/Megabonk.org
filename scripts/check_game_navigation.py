"""Prevent cross-game guide menus and per-article root discovery cards."""
from pathlib import Path
from html.parser import HTMLParser
import json,subprocess
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

class RecommendationCards(HTMLParser):
 def __init__(self):super().__init__();self.articles=[];self.links=[];self.count=0
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t=='article':
   active=bool(set(a.get('class','').split())&{'game-card','play-rec-card'})
   self.articles.append(active)
   self.count+=int(active)
  if t=='a' and any(self.articles):self.links.append(a)
 def handle_endtag(self,t):
  if t=='article' and self.articles:self.articles.pop()

def check():
 errors=[];count=0
 public=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard'],cwd=ROOT).decode('utf8').splitlines()
 card_pages=card_count=0
 for name in public:
  if Path(name).suffix.lower() not in {'.html','.htm'}:continue
  p=RecommendationCards();p.feed((ROOT/name).read_text(encoding='utf8'))
  if p.count:card_pages+=1;card_count+=p.count
  for a in p.links:
   href=a.get('href','')
   if not href.startswith('/') or href.startswith('//') or a.get('target') or any(k.startswith('on') for k in a):
    errors.append(name+': recommendation card must link internally in the same tab: '+href)
    continue
   dest=ROOT/href.split('#')[0].split('?')[0].lstrip('/')
   if not dest.is_file() and not (dest/'index.html').is_file() and not Path(str(dest)+'.html').is_file():
    errors.append(name+': recommendation card has missing internal destination: '+href)
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
 print(f'Checked {card_count} recommendation cards across {card_pages} pages: internal destinations only, including image credits.')
 print(('PASS' if not errors else 'FAILED')+f': {count} game-section pages checked for entity-scoped menus; {len(GAMES)} unique game cards; main-game guide grid separated.')
 return int(bool(errors))
if __name__=='__main__':raise SystemExit(check())
