"""Read public original-client strings as data. Never load or execute game code."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,re,time,urllib.request,urllib.error
ROOT=Path(__file__).resolve().parents[1]
ORIGIN='https://wow.aethus.pl'
LANGS=['en','pl','cs','de','pt','es','fr','ro','tr','ru','uk','zh','ja','ko']

def digest(value):
 return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()

class Redirects(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,url):
  if not url.startswith(ORIGIN+'/'):raise ValueError('Official source redirected outside the allowed origin')
  return super().redirect_request(req,fp,code,msg,headers,url)

def fetch(url,limit,etag=None):
 if not url.startswith(ORIGIN+'/'):raise ValueError('Untrusted source URL')
 headers={'User-Agent':'Mozilla/5.0 (compatible; Megabonk.org original-guide source check)','Accept-Encoding':'identity'}
 if etag:headers['If-None-Match']=etag
 for attempt in range(3):
  try:
   with urllib.request.build_opener(Redirects()).open(urllib.request.Request(url,headers=headers),timeout=60) as r:
    chunks=[];size=0
    while True:
     chunk=r.read(1024*1024)
     if not chunk:break
     size+=len(chunk)
     if size>limit:raise ValueError('Official response exceeds the source size limit')
     chunks.append(chunk)
    return b''.join(chunks),r.headers.get('ETag','')
  except urllib.error.HTTPError as e:
   if e.code==304 and etag:return None,etag
   if e.code not in [429,500,502,503,504] or attempt==2:raise
  except (urllib.error.URLError,TimeoutError):
   if attempt==2:raise
  time.sleep(2**attempt)

def launcher(raw):
 from html.parser import HTMLParser
 class Reader(HTMLParser):
  def __init__(self):super().__init__();self.scripts=[];self.links=[]
  def handle_starttag(self,t,attrs):
   a=dict(attrs)
   if t=='script':self.scripts.append(a.get('src',''))
   if t=='a':self.links.append(a.get('href',''))
 text=raw.decode('utf8');r=Reader();r.feed(text)
 if '<title>Azeroth Survivors</title>' not in text:raise ValueError('Unexpected original launcher identity')
 stamps=[m[1] for s in r.scripts if (m:=re.fullmatch(r'(?:\./|/)?rogue\.js\?v=([a-f0-9]{8,64})',s))]
 downloads=set(ORIGIN+s if s.startswith('/') else s for s in r.links if re.fullmatch(r'(?:https://wow\.aethus\.pl)?/download/[A-Za-z0-9_.-]+\.(?:rar|zip)',s))
 discord=set(s for s in r.links if re.fullmatch(r'https://discord\.gg/[A-Za-z0-9-]+',s))
 if len(stamps)!=1 or len(downloads)!=1 or len(discord)!=1:raise ValueError('Launcher download/support contract changed')
 return {'stamp':stamps[0],'windows':downloads.pop(),'discord':discord.pop()}

def json_object(data,start):
 depth=0;quoted=False;escaped=False
 for i in range(start,min(len(data),start+2000000)):
  char=data[i]
  if quoted:
   if escaped:escaped=False
   elif char==92:escaped=True
   elif char==34:quoted=False
  elif char==34:quoted=True
  elif char==123:depth+=1
  elif char==125:
   depth-=1
   if depth==0:return data[start:i+1].decode('utf8')
 raise ValueError('Truncated or oversized localized JSON object')

def unique_pairs(pairs):
 d={}
 for k,v in pairs:
  if k in d:raise ValueError('Duplicate localized key')
  d[k]=v
 return d

def extract(data,config):
 if data[:8]!=b'\x00asm\x01\x00\x00\x00':raise ValueError('Source is not the expected WebAssembly format')
 versions=set((m[1].decode(),m[2].decode()) for m in re.finditer(rb'([a-f0-9]{9})(0\.\d{1,4}\.\d{1,4})(?!\d)',data))
 if len(versions)!=1:raise ValueError('Ambiguous or missing original-client build/version marker')
 build,version=versions.pop();tables={};identity_keys=config['identity_keys']
 signatures={tuple(v):k for k,v in config['language_identities'].items()}
 for m in re.finditer(rb'\{\s*"game\.title"\s*:',data):
  d=json.loads(json_object(data,m.start()),object_pairs_hook=unique_pairs)
  if not isinstance(d,dict) or not 2500<=len(d)<=12000 or any(not isinstance(v,str) or len(v)>16000 for v in d.values()):raise ValueError('Unexpected localized table schema')
  lang=signatures.get(tuple(d.get(k) for k in identity_keys))
  if not lang or lang in tables:raise ValueError('Locale identity changed; do not swap translation columns')
  tables[lang]=d
 if set(tables)!=set(LANGS):raise ValueError('Expected fourteen independently identified language tables')
 en=tables['en']
 for cls in config['classes']:
  if en.get('class.'+cls+'.name')!=cls.title():raise ValueError('Class identity changed')
 return version,build,tables

def read_names(tables,config):
 result=[]
 for key,cls in config['spell_classes'].items():
  names={lang:tables[lang][key] for lang in LANGS}
  if any(not 1<=len(v)<=100 or any(c in v for c in '<>{}\r\n') for v in names.values()):raise ValueError('Invalid spell label')
  result.append({'key':key,'class':cls,'names':names})
 extras=[{lang:tables[lang][key] for lang in LANGS} for key in config['extra_spell_keys']]
 if any(not 1<=len(v)<=100 or any(c in v for c in '<>{}\r\n') for x in extras for v in x.values()):raise ValueError('Invalid talent-learned spell label')
 return {'spells':result,'talent_spell_names':extras}

def read_races(en,config):
 result={}
 for key,rule in config['racial_rules'].items():
  m=re.fullmatch(rule['pattern'],en.get(key,''))
  if not m:raise ValueError('Racial wording changed beyond the numeric adapter: '+key)
  values=[float(v) for v in m.groups()]
  if any(not 0<float(v)<=1000 for v in values):raise ValueError('Racial numeric value outside reviewed bounds')
  result[key]=[int(v) if v.is_integer() else v for v in values]
 return result

def candidate(raw,info,etag,config,previous,date):
 version,build,tables=extract(raw,config);en=tables['en'];fingerprints={digest(k):digest(v) for k,v in en.items()}
 if previous and len(fingerprints)<len(previous['fingerprints'])*.9:raise ValueError('Large source inventory loss; preserve last good snapshot')
 hints={digest(k):k for k in en if re.fullmatch(r'(?:ability|race|class|opt)\.[A-Za-z0-9_.]+',k) or (len(k)<70 and re.fullmatch(r"[A-Za-z][A-Za-z '’:-]+",k))}
 domains={};errors={}
 for name,fn in [('names',lambda:read_names(tables,config)),('races',lambda:read_races(en,config))]:
  try:domains[name]=fn()
  except (KeyError,ValueError) as e:errors[name]=str(e)
 before=previous.get('fingerprints',{}) if previous else {};changed={k for k,v in fingerprints.items() if before.get(k)!=v}
 review_keys={key for item in (previous or {}).get('pending',{}).values() for key in item.get('key_ids',[])}
 examples=[{'key':k,'value':v[:800]} for k,v in en.items() if digest(k) in changed|review_keys][:200]
 return {'schema':1,'unchanged':False,'observed':{'version':version,'build':build,'stamp':info['stamp'],'client_sha256':hashlib.sha256(raw).hexdigest(),'etag':etag,'date':date,'launcher':info},'fingerprints':fingerprints,'hints':hints,'domains':domains,'domain_errors':errors,'examples':examples,'examples_truncated':len(changed|review_keys)>200}

def main():
 a=argparse.ArgumentParser();a.add_argument('output',type=Path);a.add_argument('--force',action='store_true');args=a.parse_args()
 config=json.loads((ROOT/'config/azeroth-sync.json').read_text(encoding='utf8'));previous=json.loads((ROOT/'data/azeroth-sync.json').read_text(encoding='utf8'))
 raw,_=fetch(ORIGIN+'/',1000000);info=launcher(raw);old=previous['observed']
 etag=old.get('etag') if info==old.get('launcher') and not args.force else None
 client=ORIGIN+'/wenilla_bg.wasm?v='+info['stamp'];raw,tag=fetch(client,160000000,etag)
 if raw is None:result={'schema':1,'unchanged':True,'observed':old}
 else:
  result=candidate(raw,info,tag,config,previous,datetime.now(timezone.utc).date().isoformat())
  check,_=fetch(ORIGIN+'/',1000000)
  if launcher(check)!=info:raise ValueError('Original launcher changed during capture; retry on the next run')
 args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print('Original source unchanged (HTTP validator)' if result['unchanged'] else 'Collected original '+result['observed']['version']+'; no game code executed')
if __name__=='__main__':main()
