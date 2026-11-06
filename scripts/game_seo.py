"""Scoped FAQ and language metadata, derived from reviewed visible content."""
from html.parser import HTMLParser
from html import escape
from pathlib import Path
import re,json
from functools import lru_cache
ROOT=Path(__file__).resolve().parents[1]
class Node:
 def __init__(self,tag='',attrs=(),parent=None):self.tag=tag;self.attrs=dict(attrs);self.parent=parent;self.children=[]
 def text(self):
  if self.tag in ('script','style','sup','nav','button') or 'sr-only' in self.attrs.get('class','').split() or 'hidden' in self.attrs:return ''
  return re.sub(r'\s+',' ',' '.join(c.text() if isinstance(c,Node) else c for c in self.children)).strip()
 def walk(self):
  yield self
  for c in self.children:
   if isinstance(c,Node):yield from c.walk()
class Document(HTMLParser):
 def __init__(self,text):
  super().__init__(convert_charrefs=True);self.root=Node();self.current=self.root;self.feed(text)
 def handle_starttag(self,tag,attrs):
  n=Node(tag,attrs,self.current);self.current.children.append(n)
  if tag not in ('area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'):self.current=n
 def handle_startendtag(self,tag,attrs):self.handle_starttag(tag,attrs);self.handle_endtag(tag)
 def handle_endtag(self,tag):
  n=self.current
  while n.parent:
   if n.tag==tag:self.current=n.parent;return
   n=n.parent
 def handle_data(self,data):self.current.children.append(data)

def candidates(text):
 result={};doc=Document(text)
 for n in doc.root.walk():
  if n.tag not in ('h2','h3','summary'):continue
  q=n.text()
  if not ('?' in q or '？' in q):continue
  parent=n.parent
  if n.tag=='summary' and parent.tag!='details':continue
  parts=[]
  for sibling in parent.children[parent.children.index(n)+1:]:
   if isinstance(sibling,Node):
    if sibling.tag in ('h1','h2','h3','h4','section','nav','footer'):break
    if sibling.tag in ('p','ul','ol','div'):parts.append(sibling.text())
  answer=' '.join(x for x in parts if x)
  if answer:result[q]=answer
 return result

@lru_cache(maxsize=1)
def settings():
 p=ROOT/'data/game-seo.json'
 return json.loads(p.read_text(encoding='utf8')) if p.exists() else {'pages':{},'groups':[]}

def edit(path,text):
 try:key=Path(path).resolve().relative_to(ROOT).as_posix()
 except ValueError:return text
 config=settings();record=config['pages'].get(key)
 if record is None:return text
 text=re.sub(r'\n?<script id="game-faq" type="application/ld\+json">.*?</script>','',text,flags=re.S)
 text=re.sub(r'\s*<link\b(?=[^>]*\bhreflang=)[^>]*>','',text)
 markup=[]
 qs=record['questions']
 if qs:
  answers=candidates(text);canonical=re.search(r'<link[^>]*rel="canonical"[^>]*href="([^"]+)"',text)[1]
  lang=re.search(r'<html[^>]*lang="([^"]+)"',text)[1]
  schema={'@context':'https://schema.org','@type':'FAQPage','@id':canonical+'#faq','url':canonical,'inLanguage':lang,'mainEntity':[]}
  for q in qs:
   if not answers.get(q):raise ValueError('Missing reviewed visible answer: '+key+' '+q)
   schema['mainEntity'].append({'@type':'Question','name':q,'acceptedAnswer':{'@type':'Answer','text':answers[q]}})
  encoded=json.dumps(schema,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
  markup.append('<script id="game-faq" type="application/ld+json">'+encoded+'</script>')
 for group in config['groups']:
  if key in group['pages'].values():
   for lang,route in group['pages'].items():markup.append('<link rel="alternate" hreflang="'+lang+'" href="https://megabonk.org/'+route.removesuffix('index.html')+'">')
 if markup:text=re.sub(r'\s*</head>',lambda m:'\n'+'\n'.join(markup)+'</head>',text,count=1)
 return text
