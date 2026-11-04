"""Apply reviewed name/icon pairs to structured labels without changing prose or metadata."""
from pathlib import Path
from html import escape,unescape
from html.parser import HTMLParser
from functools import lru_cache
import json,re
ROOT=Path(__file__).resolve().parents[1]
VOID={'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}

@lru_cache(maxsize=1)
def inventory():
 data=json.loads((ROOT/'data/azeroth-inline-icons.json').read_text(encoding='utf8'))
 extra=json.loads((ROOT/'data/azeroth-asbuilder-icons.json').read_text(encoding='utf8'))
 data['entities'] += [dict(name=e['name'],kind=e['kind'],**{'class':e['class_id']},asset=e['asset']) for e in extra['entities']]
 return data

def pattern(name):
 pieces=[]
 for char in name:
  pieces.append(r"(?:'|’|&#x27;|&#39;|&apos;|&#8217;)" if char in "'’" else r'(?:&amp;|&)' if char=='&' else r'\s+' if char==' ' else re.escape(char))
 return ''.join(pieces)

@lru_cache(maxsize=32)
def names_for(path):
 match=re.search(r'/builds/(warrior|paladin|hunter|rogue|priest|shaman|mage|warlock|druid)/$',path)
 cls=match[1] if match else ''
 groups={}
 for e in inventory()['entities']:
  if e['kind'] in {'spell','talent'} and cls and e['class']!=cls:continue
  if e['kind']=='race' and '-female.png' in e['asset']:continue
  groups.setdefault(e['name'].replace('’',"'"),[]).append(e)
  if '/ru/' in path:
   for alias in e.get('aliases',{}).get('ru',[]):groups.setdefault(alias,[]).append({**e,'name':alias})
 result={}
 for name,entries in groups.items():
  if path== '/azeroth-survivors/abilities/' and any(e['kind']=='spell' for e in entries):
   entries=[e for e in entries if e['kind']=='spell']
  if len({e['asset'] for e in entries})!=1:continue
  # A localized spell row must receive a spell image, not a same-named talent inference.
  result[name]=next((e for e in entries if e['kind']=='spell'),entries[0])
 order=sorted(result,key=lambda x:(-len(x),x))
 regex=re.compile(r'(?<![\w])(?:'+'|'.join('(?P<n'+str(i)+'>'+pattern(n)+')' for i,n in enumerate(order))+r')(?![\w])')
 return regex,{f'n{i}':result[n] for i,n in enumerate(order)}

class Labels(HTMLParser):
 def __init__(self,path,html):
  super().__init__(convert_charrefs=False)
  self.path=path;self.html=html;self.stack=[];self.edits=[];self.used=set();self.lines=[0];self.text_end=0
  self.lines.extend(m.end() for m in re.finditer('\n',html))
  self.regex,self.names=names_for(path);self.feed(html)
 def handle_starttag(self,t,attrs):
  if t not in VOID:self.stack.append((t,dict(attrs)))
 def handle_endtag(self,t):
  for i in range(len(self.stack)-1,-1,-1):
   if self.stack[i][0]==t:del self.stack[i:];break
 def handle_data(self,text):
  line,col=self.getpos();pos=self.lines[line-1]+col
  if pos<self.text_end:return
  # HTMLParser splits a label at character references. Match the original full
  # text segment so Hunter&#x27;s Mark and other escaped names remain one label.
  end=self.html.find('<',pos)
  self.text_end=end if end>=0 else len(self.html)
  text=self.html[pos:self.text_end]
  tags=[t for t,_ in self.stack]
  if 'main' not in tags or not any(t in tags for t in ('td','li','strong','h2','h3','a')):return
  if any(t in tags for t in ('h1','nav','aside','script','style','figcaption','dialog')):return
  if any(a.get('id')=='sources' or any(c in a.get('class','').split() for c in ('sources','article-head','az-entity','meta','icon-credit')) for _,a in self.stack):return
  row=next((a for t,a in reversed(self.stack) if t=='tr'),{})
  translated=any('data-client-name' in a for _,a in self.stack)
  anchor=next((a for t,a in reversed(self.stack) if t=='a'),{})
  count=0;seen=set()
  for m in self.regex.finditer(text):
   e=self.names[m.lastgroup]
   if e['name']=='Blizzard' and not (self.path.endswith('/builds/mage/') or row.get('data-spell-class')=='mage'):continue
   if e['asset'] in seen:continue
   if 'data-spell-class' in row:
    if translated:continue
    if e['kind']!='class' and (e['kind']!='spell' or e['class']!=row['data-spell-class']):continue
   if e['kind']=='class' and m.start()>len(text)-len(text.lstrip()) and '/builds/'+e['class']+'/' not in anchor.get('href',''):continue
   start=m.start()
   if e['kind']=='class' and anchor and start>0 and not seen:start=0
   shown=text[start:m.end()];markup='<span class="az-entity" data-icon-name="'+escape(e['name'],quote=True)+'"><img class="az-entity-icon" src="'+e['asset']+'" width="28" height="28" loading="lazy" decoding="async" alt="" aria-hidden="true"><span>'+shown+'</span></span>'
   self.edits.append((pos+start,pos+m.end(),markup));self.used.add(e['asset']);seen.add(e['asset']);count+=1
   if count==4:break

def decorate_icons(path,html):
 if path.endswith('404.html') or path.endswith('/play/'):return html
 parser=Labels(path,html)
 for start,end,markup in reversed(parser.edits):html=html[:start]+markup+html[end:]
 def link_class(m):
  tag=m[1]
  if 'class="' in tag:tag=tag.replace('class="','class="az-entity-link ',1)
  else:tag+=' class="az-entity-link"'
  return tag+'>'
 html=re.sub(r'(<a\b[^>]*?)>(?=<span class="az-entity")',link_class,html)
 if parser.used:
  credit='<p class="icon-credit">Warcraft artwork © Blizzard Entertainment. Reference icons from <a href="https://azerothsurvivor.com/sources/" target="_blank" rel="noopener noreferrer">AzerothSurvivor.com ↗</a>, retrieved 2 November 2026; original asset versions not independently verified.</p>'
  if '/ru/' in path:credit=credit.replace('Warcraft artwork','Изображения Warcraft').replace('Reference icons from','Источник значков:').replace(', retrieved 2 November 2026; original asset versions not independently verified.',', получены 2 ноября 2026 года; исходные версии изображений независимо не подтверждены.')
  html=re.sub(r'(<section[^>]*id="sources"[^>]*>\s*<h2>.*?</h2>)',lambda m:m[1]+credit,html,count=1,flags=re.S)
  if any('/icons/asbuilder/' in asset for asset in parser.used):
   credit='<p class="icon-credit">Additional name-matched reference icons from <a href="https://asbuilds.app/" target="_blank" rel="noopener noreferrer">ASBuilds.app ↗</a>, retrieved 4 November 2026. ASBuilder credits this artwork to Blizzard Entertainment. Source atlas v=0134; individual asset/game versions and open reuse licences are unverified.</p>'
   html=re.sub(r'(<section[^>]*id="sources"[^>]*>\s*<h2>.*?</h2>)',lambda m:m[1]+credit,html,count=1,flags=re.S)
 return html
