"""Page-scoped editorial presentation; retain raw evidence in source modules."""
from pathlib import Path
from html import escape
import json,re
ROOT=Path(__file__).resolve().parents[1]
REF=re.compile(r'<sup class="ref"><a href="#source-(\d+)"[^>]*>.*?</a></sup>')
NATURAL={'','beginners-guide','play','ru/play','de/play','zh-hant/play'}

def editorial(path,text):
 records=json.loads((ROOT/'data/azeroth-editorial.json').read_text(encoding='utf8'))
 key=path.lstrip('/')+'index.html'
 if key not in records:return text
 slug=path.removeprefix('/azeroth-survivors/').strip('/')
 record=records[key]
 section=re.search(r'<section[^>]*id="sources"[^>]*>.*?</section>',text,re.S)
 assert section,path
 entries={x['id']:x for x in record['sources']}
 links={};items=[]
 for n,body in re.findall(r'<li[^>]*id="source-(\d+)"[^>]*>(.*?)</li>',section[0],re.S):
  link=re.search(r'<a\b.*?</a>',body,re.S)[0];url=re.search(r'href="([^"]+)"',link)[1]
  e=entries[n];assert e['url']==url,(path,n,url)
  links[n]=link
  if slug!='' or int(n)<4:
   items.append(f'<li id="source-{n}">{link} · {escape(e["summary"])}</li>')
 heading={'ru/play':'Источники','ru/builds':'Источники','de/play':'Quellen','zh-hant/play':'檢查依據'}.get(slug,'Sources &amp; checks')
 tag='ul' if slug in NATURAL else 'ol'
 # Keep the existing copyright attribution, without the repeated acquisition log.
 credit='<p class="icon-credit">Warcraft artwork © Blizzard Entertainment.</p>' if 'class="icon-credit"'in section[0] else ''
 source=f'<section class="sources" id="sources"><h2>{heading}</h2>{credit}<{tag}>'+''.join(items)+f'</{tag}></section>'
 text=text[:section.start()]+source+text[section.end():]
 if slug in NATURAL:
  # Home entity comparisons need their specific source; basic entry facts already
  # have an explicit original-host action link. Keep distinct evidence adjacent.
  linked=set()
  def natural(m):
   n=m[1]
   if slug=='' and int(n)>=4:
    anchor='' if n in linked else f' id="source-{n}"'
    linked.add(n)
    return f' <span class="source-link"{anchor}>('+links[n]+')</span>'
   return ''
  text=REF.sub(natural,text)
 else:
  def paragraph(m):
   seen=set()
   def once(ref):
    if ref[1]in seen:return ''
    seen.add(ref[1]);return ref[0]
   return REF.sub(once,m[0])
  text=re.sub(r'<p\b[^>]*>.*?</p>',paragraph,text,flags=re.S)
 text=text.replace('These links open the original host; the top Play entry uses the separately labelled third-party provider.', 'These links and the top Play guide lead to Aethus’s original game. Keep a backup before changing hosts.')
 text=text.replace('The screenshot below records an earlier original-client menu, with its version and capture date.', 'The screenshot shows the original v0.130.0 menu captured on 30 October 2026.')
 return text
