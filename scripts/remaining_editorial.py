"""Explicitly scoped editorial rules for the remaining game sections.

Evidence stays in the original generators and per-page manifest. This is a final
presentation pass so scheduled rebuilds cannot restore old footnote boilerplate.
"""
from pathlib import Path
from html import escape
from functools import lru_cache
import json,re
ROOT=Path(__file__).resolve().parents[1]
REF=re.compile(r'<sup class="ref"><a href="#source-(\d+)"[^>]*>.*?</a></sup>')

@lru_cache(maxsize=1)
def records():
 p=ROOT/'data/remaining-editorial.json'
 return json.loads(p.read_text(encoding='utf8')) if p.exists() else {}

def edit(path,text):
 try:key=Path(path).resolve().relative_to(ROOT).as_posix()
 except ValueError:return text
 if key=='poke-survivor/privacy/index.html':
  text=text.replace('This section adds no Google Analytics tag or other new analytics service.', 'This section uses the site-wide Umami analytics service described below; it adds no Google Analytics tag.')
  from site_analytics import NOTICE
  if 'id="umami-analytics"' not in text:
   notice=NOTICE.replace('This site-wide service also applies to sections described below as adding no separate analytics tag.', 'This service also applies to this guide section.')
   text=text.replace('</article>',notice+'</article>',1)
 rule=records().get(key)
 if not rule:return text
 if 'data-editorial="20261106"' in text:return text
 source=re.search(r'<section[^>]*id="sources"[^>]*>.*?</section>',text,re.S)
 if not source:raise ValueError('Missing sources: '+key)
 links={}
 def item(m):
  n=m[1];body=m[2];a=re.search(r'<a\b.*?</a>',body,re.S)
  if not a:return m[0]
  url=re.search(r'href="([^"]+)"',a[0])[1];entry=rule['sources'][n]
  if url!=entry['url']:raise ValueError(f'Source identity changed: {key} #{n}')
  links[n]=a[0]
  return f'<li id="source-{n}" value="{n}">{a[0]} · {escape(entry["summary"])}</li>'
 block=re.sub(r'<li[^>]*id="source-(\d+)"[^>]*>(.*?)</li>',item,source[0],flags=re.S)
 block=block.replace('Sources &amp; verification','Sources &amp; checks').replace('Sources & verification','Sources &amp; checks')
 if rule['mode']=='natural':block=block.replace('<ol>','<ul>').replace('</ol>','</ul>')
 block=block.replace('id="sources"','id="sources" data-editorial="20261106"',1)
 text=text[:source.start()]+block+text[source.end():]
 # Legacy figures outside the shared image decorator have explicit per-page
 # caption decisions. Preserve useful edition/illustration distinctions only.
 def figure(m):
  html=m[0]
  caption=re.search(r'<figcaption[^>]*>(.*?)</figcaption>',html,re.S)
  if not caption:return html
  decision=rule.get('captions',{}).get(caption[1])
  if decision is None:return html
  if not decision:
   # Preserve the former full-image action on the image itself.
   zoom=re.search(r'<a[^>]*href="([^"]+)"[^>]*>[^<]*(?:Open full image|Открыть изображение)',caption[1])
   image=re.search(r'<img\b[^>]*>',html)
   if zoom and image and '<a ' not in html[:image.start()]:
    html=html[:image.start()]+f'<a href="{zoom[1]}" target="_blank" rel="noopener" aria-label="Open full image">'+image[0]+'</a>'+html[image.end():]
   return re.sub(r'<figcaption[^>]*>.*?</figcaption>','',html,flags=re.S)
  return html.replace(caption[0],'<figcaption>'+escape(decision)+'</figcaption>')
 text=re.sub(r'<figure\b[^>]*>.*?</figure>',figure,text,flags=re.S)
 for old,new in rule.get('replacements',[]):
  if old not in text:raise ValueError(f'Editorial text changed: {key}: {old[:60]}')
  text=text.replace(old,new)
 if rule['mode']=='natural':
  # Existing action links already establish the basic original-game entry.
  # Different announcements/policies retain natural attribution near the claim.
  primary=set(rule.get('entry_sources',[]))
  # A prose link to the exact source already supplies attribution in that block.
  def linked_paragraph(m):
   html=m[0]
   return REF.sub(lambda ref: '' if 'href="'+rule['sources'][ref[1]]['url']+'"' in html else ref[0],html)
  text=re.sub(r'<p\b[^>]*>.*?</p>',linked_paragraph,text,flags=re.S)
  attributed=set()
  def cite(ref):
   n=ref[1]
   if n in primary or n in attributed:return ''
   attributed.add(n)
   return ' <span class="source-link">('+links[n]+')</span>'
  text=REF.sub(cite,text)
 else:
  def paragraph(m):
   seen=set()
   def once(ref):
    if ref[1]in seen:return ''
    seen.add(ref[1]);return ref[0]
   return REF.sub(once,m[0])
  text=re.sub(r'<p\b[^>]*>.*?</p>',paragraph,text,flags=re.S)
 return text
