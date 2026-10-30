"""Guard shared game-section layout wiring after rebuilding all generators."""
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class Page(HTMLParser):
 def __init__(self):super().__init__();self.classes=set();self.css=[];self.ids=set()
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='body':self.classes.update(a.get('class','').split())
  if tag=='link'and a.get('rel')=='stylesheet':self.css.append(a.get('href'))
  if a.get('id'):self.ids.add(a['id'])
def check():
 errors=[];count=0
 # Discover additional sections using the shared base/layout, as well as the three existing ones.
 sections={'pokebonk','poke-survivor','survivor-ace','azeroth-survivors','ball-x-pit'}
 for folder in ROOT.iterdir():
  if not folder.is_dir() or folder.name.startswith(('.', '_')) or folder.name in ['node_modules','assets','scripts','PAGE_REPORTS']:continue
  for file in folder.rglob('*.html'):
   text=file.read_text(encoding='utf-8-sig')
   if 'guide-layout' in text or '/assets/pokebonk/site.css' in text or '/assets/guide-article-layout.css' in text:
    sections.add(folder.name);break
 for section in sorted(sections):
  for file in sorted((ROOT/section).rglob('*.html')):
   p=Page();p.feed(file.read_text(encoding='utf-8-sig'));count+=1
   if 'guide-layout'not in p.classes:errors.append(str(file.relative_to(ROOT))+': missing shared layout body class')
   if '/assets/guide-article-layout.css'not in p.css:errors.append(str(file.relative_to(ROOT))+': missing shared article stylesheet')
   if 'comparison-output'in p.ids:
    for ident in ['compare-tray','compare-open','compare-dialog','compare-modal-output','compare-close','compare-status']:
     if ident not in p.ids:errors.append('Partner comparison missing visible result control '+ident)
 if count<3:errors.append('No complete game sections found')
 for x in errors:print('FAIL',x)
 print(('PASS'if not errors else'FAILED')+f': {count} game-section HTML files use the shared layout; comparison result controls present')
 return int(bool(errors))
if __name__=='__main__':raise SystemExit(check())
