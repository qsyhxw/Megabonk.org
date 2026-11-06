"""Entity-scoped navigation and one-card-per-game root discovery.

Called by write_html so legacy per-game root patches cannot repopulate the
Megabonk guide grid. Edit data/game-sections.json for game discovery entries.
"""
from pathlib import Path
from html import escape
import json,re
ROOT=Path(__file__).resolve().parents[1]

def games():return json.loads((ROOT/'data/game-sections.json').read_text(encoding='utf8'))

def navigation(route):
 if route.startswith('/risk-of-rain-2/'):
  pairs=[('Overview','/risk-of-rain-2/'),('Crossplay','/risk-of-rain-2/crossplay/'),('Gold Portal','/risk-of-rain-2/gold-portal/'),('Испытание (RU)','/risk-of-rain-2/ru/bulwarks-ambry/')]
 elif route.startswith('/pokedive/'):
  pairs=[('Start here','/pokedive/'),('Mobile','/pokedive/mobile/'),('Shinies','/pokedive/shinies/')]
 else:pairs=[('Browser demo','/vampire-survivors/'),('Co-op','/vampire-survivors/co-op/')]
 pairs.append(('More games','/#more-games'))
 return ''.join(f'<a href="{u}"'+(' aria-current="page"' if u==route else '')+f'>{escape(t)}</a>' for t,u in pairs)

def catalog():
 cards=[]
 for g in games():
  variants=g['sizes'];stem=g['image'];w=max(variants)
  srcset=', '.join(f'{stem}-{v}.webp {v}w' for v in variants)
  extra=''.join(f'<a href="{u}">{escape(t)}</a>' for t,u in g.get('tasks',[]))
  credit=f'<p class="game-card-credit" data-required-credit>{escape(g["required_credit"])}</p>' if g.get('required_credit') else ''
  cards.append(f'<article class="game-card" data-game="{g["id"]}" id="game-{g["id"]}"><a class="game-card-main" href="{g["url"]}"><img src="{stem}-{min(variants)}.webp" srcset="{srcset}" sizes="(max-width:600px) calc(100vw - 40px), (max-width:1000px) 45vw, 280px" width="{g["width"]}" height="{g["height"]}" loading="lazy" alt="{escape(g["alt"],quote=True)}"><div><h3>{escape(g["name"])}</h3><p>{escape(g["summary"])}</p><span>{escape(g.get("action","Game & guides"))} →</span></div></a>{"<div class=game-card-tasks>"+extra+"</div>" if extra else ""}{credit}</article>')
 return '<section id="more-games" class="section section-alt game-discovery" aria-labelledby="game-discovery-title"><div class="container"><span id="pokebonk-guide"></span><div class="section-heading"><h2 id="game-discovery-title">More games</h2><p>Discover related games, their starting guides and edition details.</p></div><div class="game-discovery-grid">'+''.join(cards)+'</div></div></section>'

def div_end(text,start):
 depth=0
 for m in re.finditer(r'</?div\b[^>]*>',text[start:],re.I):
  depth+=-1 if m[0].startswith('</') else 1
  if depth==0:return start+m.end()
 raise ValueError('Unclosed root guide grid')

def root_discovery(text):
 # Keep only Megabonk's own guide cards in its guide grid.
 start=text.index('<div class="route-grid">');end=div_end(text,start)
 chunk=text[start:end]
 # Preserve actual card markup, not a new replacement homepage/template.
 matches=list(re.finditer(r'<(?P<tag>a|div)\b[^>]*class="route-card"[^>]*>.*?</(?P=tag)>',chunk,re.S))
 # Classify destinations rather than freezing the current number of main-game cards.
 foreign=tuple('/'+g['id']+'/' for g in games())+('/games-like-vampire-survivors/','/guides/pokemon-games-like-megabonk/')
 kept=[m[0] for m in matches if not any(u.startswith(foreign) for u in re.findall(r'href="([^"]+)"',m[0]))]
 assert kept,'Main-game guide grid must retain its existing tasks'
 text=text[:start]+'<div class="route-grid">'+''.join(kept)+'</div>'+text[end:]
 # Replace the former one-game promo in its original bottom-of-page position.
 old=re.search(r'<section\b[^>]*(?:id="(?:more-games|pokebonk-guide)")[^>]*>.*?</section>',text,re.S)
 assert old,'Root discovery placement missing'
 text=text[:old.start()]+catalog()+text[old.end():]
 css='<link rel="stylesheet" href="/assets/game-discovery.css">'
 if css not in text:text=text.replace('</head>',css+'\n</head>',1)
 return text

def normalize(path,text):
 rel=Path(path).resolve().relative_to(ROOT).as_posix()
 if rel=='index.html':return root_discovery(text)
 roots={g['id'] for g in games()}
 if rel.split('/')[0] in roots or rel.startswith('games-like-vampire-survivors/'):
  # A site-wide discovery link must not land in the Megabonk-only guide grid.
  text=text.replace('href="/#wiki-start"','href="/#more-games"')
 return text
