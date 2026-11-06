"""Check every registered game page, FAQ agreement and reciprocal locale sets."""
from pathlib import Path
import re,json
from game_seo import candidates,edit,settings,Document
ROOT=Path(__file__).resolve().parents[1]
def main():
 config=settings();pages=config['pages'];groups=config['groups']
 expected={p.relative_to(ROOT).as_posix() for g in json.loads((ROOT/'data/game-sections.json').read_text(encoding='utf8')) for p in (ROOT/g['id']).rglob('*.html')}
 assert expected==set(pages),'Review new/removed game pages in data/game-seo.json'
 assigned={};links={}
 for group in groups:
  actual={k:v for k,v in group['pages'].items() if k!='x-default'}
  assert len(actual)>=2
  for lang,name in actual.items():
   assert re.fullmatch(r'[a-z]{2,3}(?:-[A-Z][a-z]{3})?(?:-[A-Z]{2})?',lang),lang
   assert name not in assigned,('multiple groups',name)
   assigned[name]=group['pages'];links[name]=lang
 count=0
 for name,record in pages.items():
  text=(ROOT/name).read_text(encoding='utf8');doc=Document(text)
  nodes=list(doc.root.walk());language=next(n.attrs['lang'] for n in nodes if n.tag=='html')
  canonical=next(n.attrs['href'] for n in nodes if n.tag=='link' and n.attrs.get('rel')=='canonical')
  assert edit(ROOT/name,text)==text,('render drift',name)
  assert list(candidates(text))==record['reviewed_candidates'],('Review changed question blocks',name)
  scripts=[json.loads(''.join(n.children)) for n in nodes if n.tag=='script' and n.attrs.get('type')=='application/ld+json']
  def faqs(x):
   if isinstance(x,dict):
    if x.get('@type')=='FAQPage':yield x
    for v in x.values():yield from faqs(v)
   elif isinstance(x,list):
    for v in x:yield from faqs(v)
  faq=[f for s in scripts for f in faqs(s)]
  assert len(faq)==int(bool(record['questions'])),('FAQ count',name)
  if faq:
   count+=1;f=faq[0];assert f['url']==canonical and f['inLanguage']==language
   answers=candidates(text)
   assert [q['name'] for q in f['mainEntity']]==record['questions']
   for q in f['mainEntity']:
    assert q['@type']=='Question' and q['acceptedAnswer']['@type']=='Answer'
    assert q['acceptedAnswer']['text']==answers[q['name']],('visible answer drift',name,q['name'])
  alt=[n.attrs for n in nodes if n.tag=='link' and 'hreflang' in n.attrs]
  group=assigned.get(name,{})
  assert len(alt)==len(group),('hreflang count',name)
  assert {a['hreflang']:a['href'] for a in alt}=={l:'https://megabonk.org/'+p.removesuffix('index.html') for l,p in group.items()},('locale set',name)
  if group:
   assert language==links[name]
   assert canonical=='https://megabonk.org/'+name.removesuffix('index.html')
   assert not any(n.tag=='meta' and n.attrs.get('name')=='robots' and 'noindex' in n.attrs.get('content','') for n in nodes)
 print(f'PASS: {len(pages)} pages; {count} FAQ pages; {len(groups)} reciprocal language groups; body-derived answers and idempotency')
if __name__=='__main__':main()
