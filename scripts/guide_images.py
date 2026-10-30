"""Insert reviewed, page-specific game figures without changing title/H1/canonical."""
from pathlib import Path
from html import escape,unescape
from urllib.parse import urlsplit,parse_qsl
import json,re
ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'data/guide-images.json').read_text(encoding='utf8'))
def key(url):
 u=urlsplit(unescape(url));return u.netloc,u.path,tuple(sorted(parse_qsl(u.query)))
def decorate(path,html):
 page=DATA['pages'].get(path)
 if not page:return html
 assert 'class="game-image' not in html,path+' double image insertion'
 m=DATA['media'][page['image']]
 section=re.search(r'<section\b[^>]*id="sources"[^>]*>.*?</section>',html,re.S)
 assert section,path+' missing source section'
 ident=None;number=None
 for item in re.finditer(r'<li\b[^>]*id="(source-(\d+))"[^>]*>(.*?)</li>',section[0],re.S):
  if any(key(url)==key(m['source']) for url in re.findall(r'href="([^"]+)"',item[3])):
   ident=item[1];number=item[2];break
 if not ident:
  number=str(max([int(n) for n in re.findall(r'id="source-(\d+)"',section[0])]+[0])+1)
  ident='source-'+number
  item=f'<li id="{ident}"><a href="{escape(m["source"],quote=True)}" target="_blank" rel="noopener noreferrer">{escape(m["label"])} ↗</a> — {escape(m["detail"])}</li>'
  new=section[0].replace('</ol>',item+'</ol>',1)
  html=html[:section.start()]+new+html[section.end():]
 lang=page.get('lang','en')
 zoom={'en':'Open full image','ja':'画像を拡大','zh-Hant':'開啟大圖','ru':'Открыть изображение'}[lang]
 variants=m['sizes'];w=max(variants);h=round(m['height']*w/m['width'])
 source=m['stem']+'-'+str(min(variants))+'.webp'
 srcset=', '.join(m['stem']+'-'+str(v)+'.webp '+str(v)+'w' for v in variants)
 detail=m['detail']
 # Keep limits in the page language; owner credit and exact version remain unambiguous.
 if lang=='zh-Hant':detail='官方素材核對：2026-10-30；版本未註明，非本站遊玩實測。'
 if lang=='ja':detail='公式素材の確認日：2026-10-30。版は未記載、当サイトのプレイ記録ではありません。'
 if lang=='ru':detail='Снимок меню оригинала 30.10.2026 · v0.130.0 (e7d9dd47), не тест игрового прохождения.'
 portrait=' portrait' if m['height']>m['width'] else ''
 figure=f'''<figure class="game-image{portrait}" data-game-image="{escape(page["image"])}"><a href="{m["stem"]}-{w}.webp" target="_blank" rel="noopener" aria-label="{zoom}"><img src="{source}" srcset="{srcset}" sizes="(max-width: 800px) calc(100vw - 36px), {'420px' if portrait else '1000px'}" width="{w}" height="{h}" loading="lazy" alt="{escape(page["alt"],quote=True)}"></a><figcaption>{escape(m["credit"])}. {escape(detail)} {escape(page["purpose"])} <a class="ref" href="#{ident}" aria-label="Image source {number}">[{number}]</a> <a class="image-zoom" href="{m["stem"]}-{w}.webp" target="_blank" rel="noopener">{zoom} ↗</a></figcaption></figure>'''
 anchor=page['anchor']
 target=re.search(r'<section\b[^>]*id="'+re.escape(anchor)+r'"[^>]*>\s*(?:<div[^>]*>)?(?:<h[23][^>]*>.*?</h[23]>)?',html,re.S) if anchor else None
 if not target:
  prose=re.search(r'<article\b[^>]*class="prose"[^>]*>',html)
  start=prose.end() if prose else html.index('<main')
  target=re.search(r'<section\b[^>]*>\s*<h2[^>]*>.*?</h2>',html[start:],re.S)
  assert target,path+' no insertion section'
  pos=start+target.start()
 else:pos=target.start()
 html=html[:pos]+figure.replace('loading="lazy"',f'loading="{page.get("loading","lazy")}"')+html[pos:]
 og=f'<meta property="og:image" content="https://megabonk.org{m["stem"]}-{w}.webp">'
 if re.search(r'<meta\b[^>]*property="og:image"[^>]*>',html):html=re.sub(r'<meta\b[^>]*property="og:image"[^>]*>',og,html,count=1)
 else:html=html.replace('</head>',og+'</head>',1)
 return html
