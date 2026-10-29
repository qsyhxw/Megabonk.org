"""Pre-publication snapshot, metadata protection and scoped content dates."""
from pathlib import Path
import argparse,json,re,subprocess,xml.etree.ElementTree as ET
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
PATTERNS=[r'<title>(.*?)</title>',r'<meta[^>]*name=["\']description["\'][^>]*>',r'<h1\b[^>]*>(.*?)</h1>',r'<link[^>]*rel=["\']canonical["\'][^>]*>']
def metadata(s):return[re.findall(p,s,re.I|re.S)for p in PATTERNS]
def files():return[p for p in subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')if p.endswith(('.html','.htm'))]
def main():
 a=argparse.ArgumentParser();a.add_argument('mode',choices=['before','after']);a.add_argument('snapshot',type=Path);args=a.parse_args()
 if args.mode=='before':
  data={'metadata':{},'html':{},'xml':(ROOT/'sitemap.xml').read_text(encoding='utf8')}
  for p in files():
   s=(ROOT/p).read_text(encoding='utf-8-sig');data['metadata'][p]=metadata(s)
   if p.startswith('pokebonk/'):data['html'][p]=s
  args.snapshot.write_text(json.dumps(data),encoding='utf8');print('Snapshot',len(data['metadata']),'HTML');return
 data=json.loads(args.snapshot.read_text(encoding='utf8'));changed=[]
 if set(files())!=set(data['metadata']):raise ValueError('Published HTML inventory changed')
 for p,meta in data['metadata'].items():
  s=(ROOT/p).read_text(encoding='utf-8-sig')
  if metadata(s)!=meta:raise ValueError('Protected metadata changed: '+p)
  if p in data['html']and s!=data['html'][p]:changed.append(p)
 oldxml=ET.fromstring(data['xml']);xmlpath=ROOT/'sitemap.xml';xml=xmlpath.read_text(encoding='utf8');tree=ET.fromstring(xml)
 if [x.findtext('{*}loc')for x in tree]!=[x.findtext('{*}loc')for x in oldxml]:raise ValueError('Sitemap URL inventory changed')
 datespath=ROOT/'data/content-dates.json';dates=json.loads(datespath.read_text(encoding='utf8'));today=datetime.now(timezone.utc).date().isoformat();dated=[]
 # Source-observation badges alone do not refresh an article's content date.
 normalize=lambda s:re.sub(r'<aside id="source-sync".*?</aside>','',s,flags=re.S)
 for p in changed:
  if normalize(data['html'][p])==normalize((ROOT/p).read_text(encoding='utf8')):continue
  if not p.endswith('index.html'):continue
  u='https://megabonk.org/'+p[:-10];dates[u]=today;dated.append(u);xml=re.sub(r'(<loc>'+re.escape(u)+r'</loc>\s*<lastmod>)[^<]*(</lastmod>)',lambda m:m[1]+today+m[2],xml)
 if dated:datespath.write_text(json.dumps(dates,ensure_ascii=False,indent=2)+'\n',encoding='utf8');xmlpath.write_text(xml,encoding='utf8')
 allowed={'data/pokebonk-sync.json','data/content-dates.json','sitemap.xml'}|set(data['html'])
 edited=set(subprocess.check_output(['git','diff','--name-only'],cwd=ROOT).decode().splitlines())
 if not edited<=allowed:raise ValueError('Updater changed files outside its scope: '+str(edited-allowed))
 print('PASS',len(data['metadata']),'protected metadata;',len(changed),'changed pages;',len(tree),'unchanged XML URLs;',len(dated),'content dates')
if __name__=='__main__':main()
