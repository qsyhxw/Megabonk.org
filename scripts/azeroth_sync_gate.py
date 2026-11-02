"""Restrict automatic writes, protect metadata, and date only changed reference values."""
from pathlib import Path
import argparse,json,re,subprocess,xml.etree.ElementTree as ET
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
PATTERNS=[r'<title>(.*?)</title>',r'<meta[^>]*name=["\']description["\'][^>]*>',r'<h1\b[^>]*>(.*?)</h1>',r'<link[^>]*rel=["\']canonical["\'][^>]*>']
def metadata(s):return [re.findall(p,s,re.I|re.S) for p in PATTERNS]
def files():return [p for p in subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0') if p.endswith(('.html','.htm'))]
def snapshot():
 return {'metadata':{p:metadata((ROOT/p).read_text(encoding='utf-8-sig')) for p in files()},'html':{p:(ROOT/p).read_text(encoding='utf8') for p in files() if p.startswith('azeroth-survivors/')},'state':json.loads((ROOT/'data/azeroth-sync.json').read_text(encoding='utf8')),'dates':json.loads((ROOT/'data/content-dates.json').read_text(encoding='utf8')),'xml':(ROOT/'sitemap.xml').read_text(encoding='utf8')}
def check(old,*,enforce_scope=True):
 current=files()
 if set(current)!=set(old['metadata']):raise ValueError('Updater changed the published HTML inventory')
 for p in current:
  if metadata((ROOT/p).read_text(encoding='utf-8-sig'))!=old['metadata'][p]:raise ValueError('Protected metadata changed: '+p)
 xmlpath=ROOT/'sitemap.xml';xml=xmlpath.read_text(encoding='utf8');tree=ET.fromstring(xml);before=ET.fromstring(old['xml'])
 if [u.findtext('{*}loc') for u in tree]!=[u.findtext('{*}loc') for u in before]:raise ValueError('Updater changed sitemap URLs')
 state=json.loads((ROOT/'data/azeroth-sync.json').read_text(encoding='utf8'));oldstate=old['state'];dated=set()
 names=json.loads((ROOT/'data/azeroth-spell-names.json').read_text(encoding='utf8'));accepted=state['accepted']['names']
 if names['spells']!=accepted['data']['spells'] or names['version']!=accepted['version'] or names['sha256']!=accepted['sha256']:raise ValueError('Name lookup and accepted source record diverged')
 if state['accepted']['names']['data']!=oldstate['accepted']['names']['data']:dated.add('azeroth-survivors/abilities/index.html')
 if state['accepted']['races']['data']!=oldstate['accepted']['races']['data']:dated.add('azeroth-survivors/best-race/index.html')
 if state['observed']['launcher']!=oldstate['observed']['launcher']:
  # A stamp alone is observation metadata. Only actual action-link changes date articles.
  if any(state['observed']['launcher'][k]!=oldstate['observed']['launcher'][k] for k in ['windows','discord']):
   for p,s in old['html'].items():
    if any('href="'+oldstate['observed']['launcher'][k]+'"' in s for k in ['windows','discord']):dated.add(p)
 dates=old['dates'].copy();today=datetime.now(timezone.utc).date().isoformat()
 for p in sorted(dated):
  if p not in old['html'] or (ROOT/p).read_text(encoding='utf8')==old['html'][p]:continue
  url='https://megabonk.org/'+p[:-10];dates[url]=today;xml=re.sub(r'(<loc>'+re.escape(url)+r'</loc>\s*<lastmod>)[^<]*(</lastmod>)',lambda m:m[1]+today+m[2],xml)
 actual_dates=json.loads((ROOT/'data/content-dates.json').read_text(encoding='utf8'))
 if actual_dates not in (old['dates'],dates):raise ValueError('Unrelated content dates changed')
 oldmods={u.findtext('{*}loc'):u.findtext('{*}lastmod') for u in before}
 for u in ET.fromstring(xml):
  url=u.findtext('{*}loc');expected=today if 'azeroth-survivors/'+url.split('/azeroth-survivors/')[-1]+'index.html' in dated and '/azeroth-survivors/' in url else oldmods[url]
  if u.findtext('{*}lastmod')!=expected:raise ValueError('Unrelated sitemap date changed: '+url)
 if dates!=actual_dates:(ROOT/'data/content-dates.json').write_text(json.dumps(dates,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 if xml!=xmlpath.read_text(encoding='utf8'):xmlpath.write_text(xml,encoding='utf8')
 if enforce_scope:
  allowed={'data/azeroth-sync.json','data/azeroth-spell-names.json','data/content-dates.json','sitemap.xml'}|set(old['html'])
  edited=set(subprocess.check_output(['git','diff','--name-only'],cwd=ROOT).decode().splitlines())
  untracked=set(subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=ROOT).decode().splitlines())
  if not (edited|untracked)<=allowed:raise ValueError('Updater wrote outside its permitted files: '+str((edited|untracked)-allowed))
 print('PASS',len(current),'protected metadata records;',len(tree),'sitemap URLs;',len(dated),'reference-content dates; source-status-only changes do not refresh dates')
def main():
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['before','after']);p.add_argument('snapshot',type=Path);a=p.parse_args()
 if a.mode=='before':a.snapshot.write_text(json.dumps(snapshot()),encoding='utf8')
 else:check(json.loads(a.snapshot.read_text(encoding='utf8')))
if __name__=='__main__':main()
