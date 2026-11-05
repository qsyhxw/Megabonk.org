"""Negative and render fixtures for a privileged automatic publication path."""
from pathlib import Path
from copy import deepcopy
import unittest,json,re,sys,tempfile,shutil,subprocess
from unittest.mock import patch,MagicMock
import azeroth_sync_source as source
import azeroth_sync as sync
import azeroth_sync_gate as gate
ROOT=Path(__file__).resolve().parents[1]

class SyncTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.config=json.loads((ROOT/'config/azeroth-sync.json').read_text(encoding='utf8'));real=json.loads((ROOT/'data/azeroth-sync.json').read_text(encoding='utf8'));cls.info=deepcopy(real['observed']['launcher'])
  lookup=json.loads((ROOT/'data/azeroth-spell-names.json').read_text(encoding='utf8'))
  if lookup['spells']!=real['accepted']['names']['data']['spells'] or lookup['version']!=real['accepted']['names']['version'] or lookup['sha256']!=real['accepted']['names']['sha256']:raise ValueError('Committed name lookup diverges from the accepted sync record')
  cls.tables={lang:{'game.title':'Azeroth Survivors',**dict(zip(cls.config['identity_keys'],cls.config['language_identities'][lang]))} for lang in source.LANGS}
  for lang,d in cls.tables.items():
   d.update({'class.'+c+'.name':c.title() for c in cls.config['classes']})
   d.update({s['key']:s['names'][lang] for s in real['accepted']['names']['data']['spells']})
   d.update({k:real['accepted']['names']['data']['talent_spell_names'][i][lang] for i,k in enumerate(cls.config['extra_spell_keys'])})
   for k,rule in cls.config['racial_rules'].items():
    # Build a reviewed wording fixture from its regex and current numeric groups.
    pat=rule['pattern'];vals=iter(real['accepted']['races']['data'][k]);text=re.sub(r'\(\[0-9\]\+\(\?:\\\.\[0-9\]\+\)\?\)',lambda m:str(next(vals)),pat);d[k]=re.sub(r'\\(.)',r'\1',text)
   d.update({'fixture.'+str(i):'baseline '+str(i) for i in range(3400)})
  c=cls.make(cls.tables)
  cls.old={'schema':1,'observed':c['observed'],'fingerprints':c['fingerprints'],'hints':c['hints'],'accepted':{k:{'version':c['observed']['version'],'sha256':c['observed']['client_sha256'],'date':c['observed']['date'],'data':v} for k,v in c['domains'].items()},'domain_errors':{},'pending':{},'last_changes':{'added':0,'removed':0,'changed':0,'data_domains':[],'affected_pages':[]}}
  assert not c['domain_errors'],c['domain_errors']
 @classmethod
 def wasm(cls,tables,version='0.400.0',tail=b''):
  return b'\x00asm\x01\x00\x00\x00'+b'abcdef123'+version.encode()+b'\x00'+b'\x00'.join(json.dumps(d,ensure_ascii=False,indent=2).encode() for d in reversed(list(tables.values())))+tail
 @classmethod
 def make(cls,tables,version='0.400.0',tail=b''):
  return source.candidate(cls.wasm(tables,version,tail),cls.info,'"fixture"',cls.config,None,'2026-11-02')
 def test_locale_identity_not_array_order(self):
  _,_,tables=source.extract(self.wasm(self.tables),self.config)
  self.assertEqual(tables['zh']['picker.language'],self.config['language_identities']['zh'][2])
  t=deepcopy(self.tables);t['zh']['picker.language']='unknown locale'
  with self.assertRaises(ValueError):source.extract(self.wasm(t),self.config)
 def test_bad_wasm_and_ambiguous_version(self):
  for raw in [b'<html>Error</html>',self.wasm(self.tables,tail=b'123abcdef0.401.0')]:
   with self.assertRaises(ValueError):source.extract(raw,self.config)
 def test_launcher_and_redirect_allowlist(self):
  good=b'<title>Azeroth Survivors</title><script src="./rogue.js?v=abcdef123456"></script><a href="/download/game.rar">Windows</a><a href="https://discord.gg/abc">Discord</a>'
  self.assertEqual(source.launcher(good)['windows'],'https://wow.aethus.pl/download/game.rar')
  with self.assertRaises(ValueError):source.launcher(good.replace(b'/download/game.rar',b'https://evil.invalid/game.rar'))
  with self.assertRaises(ValueError):source.Redirects().redirect_request(None,None,302,'',{},'https://evil.invalid/game.wasm')
 def test_transient_fetch_retries_but_forbidden_does_not(self):
  opener=MagicMock();response=MagicMock();response.__enter__.return_value=response;response.headers={'ETag':'"test"'};response.read.side_effect=[b'data',b''];opener.open.side_effect=[source.urllib.error.HTTPError(source.ORIGIN+'/',503,'busy',{},None),response]
  with patch.object(source.urllib.request,'build_opener',return_value=opener),patch.object(source.time,'sleep'):
   self.assertEqual(source.fetch(source.ORIGIN+'/',100),(b'data',{'etag':'"test"','last_modified':''}));self.assertEqual(opener.open.call_count,2)
  opener=MagicMock();opener.open.side_effect=source.urllib.error.HTTPError(source.ORIGIN+'/',403,'forbidden',{},None)
  with patch.object(source.urllib.request,'build_opener',return_value=opener),self.assertRaises(source.urllib.error.HTTPError):source.fetch(source.ORIGIN+'/',100)
  self.assertEqual(opener.open.call_count,1)
 def test_no_change_is_byte_stable_and_review_can_clear(self):
  c={'schema':1,'unchanged':True,'observed':deepcopy(self.old['observed'])};state,report=sync.assess(c,self.old,self.config)
  self.assertEqual(state,self.old);self.assertTrue(report['unchanged'])
  old=deepcopy(self.old);route='/azeroth-survivors/builds/mage/';old['pending'][route]={'version':'0.400.0'};config=deepcopy(self.config);config['editorial_reviews'][route]={'client_sha256':old['observed']['client_sha256'],'note':'Reviewed changed source and corrected the article.'}
  state,_=sync.assess(c,old,config);self.assertNotIn(route,state['pending'])
  old=deepcopy(self.old);old['last_changes']={'added':1,'removed':0,'changed':2,'data_domains':['names'],'affected_pages':[route]}
  state,_=sync.assess(self.make(self.tables),old,self.config);self.assertEqual(state['last_changes'],old['last_changes']);self.assertEqual(state,old)
  forced=self.make(self.tables);forced['observed']['etag']='"different compression representation"';state,_=sync.assess(forced,old,self.config);self.assertEqual(state,old)
 def test_race_numbers_apply_but_semantic_change_freezes(self):
  t=deepcopy(self.tables);t['en']['race.human.line2']='The Human Spirit: +25% experience';c=self.make(t);state,report=sync.assess(c,self.old,self.config)
  self.assertEqual(state['accepted']['races']['data']['race.human.line2'],[25]);self.assertIn('races',report['domains']);self.assertIn('/azeroth-survivors/best-race/',state['pending'])
  t['en']['race.human.line2']='The Human Spirit: experience only while mounted';c=self.make(t);state,_=sync.assess(c,self.old,self.config)
  self.assertEqual(state['accepted']['races'],self.old['accepted']['races']);self.assertIn('races',state['domain_errors'])
 def test_missing_spell_keeps_old_lookup(self):
  t=deepcopy(self.tables);del t['en']['ability.fireball.name'];state,_=sync.assess(self.make(t),self.old,self.config)
  self.assertEqual(state['accepted']['names'],self.old['accepted']['names']);self.assertIn('names',state['domain_errors'])
 def test_renames_and_unsafe_labels(self):
  t=deepcopy(self.tables);t['en']['ability.fireball.name']='Fire Orb';state,r=sync.assess(self.make(t),self.old,self.config)
  self.assertIn('names',r['domains']);self.assertIn('/azeroth-survivors/builds/mage/',r['pending_pages'])
  t['en']['ability.fireball.name']='<script>bad</script>';state,_=sync.assess(self.make(t),self.old,self.config)
  self.assertEqual(state['accepted']['names'],self.old['accepted']['names'])
 def test_large_rename_is_retained_for_review(self):
  t=deepcopy(self.tables)
  for key in list(self.config['spell_classes'])[:11]:t['en'][key]+=' Updated'
  state,_=sync.assess(self.make(t),self.old,self.config)
  self.assertEqual(state['accepted']['names'],self.old['accepted']['names']);self.assertIn('names',state['domain_errors'])
 def test_binary_only_change_and_removed_mechanic_need_review(self):
  c=self.make(self.tables,tail=b'changed code, not executed');state,_=sync.assess(c,self.old,self.config)
  self.assertEqual(set(state['pending']),set(sync.routes()))
  t=deepcopy(self.tables);del t['en']['fixture.1'];state,_=sync.assess(self.make(t),self.old,self.config);self.assertTrue(state['pending'])
 def test_rollback_truncation_wrong_hash_and_schema_rejected(self):
  cases=[self.make(self.tables,version='0.399.0')];bad=self.make(self.tables);bad['fingerprints']={};cases.append(bad);bad=self.make(self.tables);bad['observed']['client_sha256']='bad';cases.append(bad);bad=self.make(self.tables);bad['domains']['races']['race.human.line2']=[float('nan')];cases.append(bad)
  for c in cases:
   with self.assertRaises(ValueError):sync.assess(c,self.old,self.config)
 def test_render_dates_metadata_and_scope_guard(self):
  with tempfile.TemporaryDirectory() as td:
   dest=Path(td);shutil.copytree(ROOT/'scripts',dest/'scripts',ignore=shutil.ignore_patterns('__pycache__'));(dest/'data').mkdir();(dest/'config').mkdir()
   for p in (ROOT/'data').glob('azeroth*.json'):shutil.copyfile(p,dest/'data'/p.name)
   for name in ['guide-images.json','content-dates.json','play-games.json','play-games-locales.json','game-sections.json']:shutil.copyfile(ROOT/'data'/name,dest/'data'/name)
   shutil.copyfile(ROOT/'config/azeroth-sync.json',dest/'config/azeroth-sync.json');shutil.copyfile(ROOT/'sitemap.xml',dest/'sitemap.xml')
   (dest/'data/azeroth-sync.json').write_text(json.dumps(self.old),encoding='utf8')
   names=json.loads((dest/'data/azeroth-spell-names.json').read_text(encoding='utf8'));names.update(version=self.old['accepted']['names']['version'],sha256=self.old['accepted']['names']['sha256']);(dest/'data/azeroth-spell-names.json').write_text(json.dumps(names,ensure_ascii=False),encoding='utf8')
   subprocess.run([sys.executable,str(dest/'scripts/build_azeroth_survivors.py')],cwd=dest,check=True,capture_output=True)
   dates=json.loads((dest/'data/content-dates.json').read_text(encoding='utf8'))
   for url in dates:
    if '/azeroth-survivors/' in url:dates[url]='2020-01-01'
   (dest/'data/content-dates.json').write_text(json.dumps(dates,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
   xml=(dest/'sitemap.xml').read_text(encoding='utf8');xml=re.sub(r'(<loc>https://megabonk.org/azeroth-survivors/[^<]*</loc>\s*<lastmod>)[^<]*(</lastmod>)',lambda m:m[1]+'2020-01-01'+m[2],xml);(dest/'sitemap.xml').write_text(xml,encoding='utf8')
   subprocess.run(['git','init','-q'],cwd=dest,check=True);subprocess.run(['git','-c','core.autocrlf=false','add','--','scripts','data','config','azeroth-survivors','sitemap.xml'],cwd=dest,check=True)
   with patch.object(gate,'ROOT',dest):before=gate.snapshot()
   meta=self.make(self.tables);meta['observed']['etag']='"new HTTP validator, identical source bytes"';meta['observed']['last_modified']='Sun, 01 Nov 2026 23:57:32 GMT';sync.apply(meta,root=dest)
   subprocess.run([sys.executable,str(dest/'scripts/build_azeroth_survivors.py')],cwd=dest,check=True,capture_output=True)
   with patch.object(gate,'ROOT',dest):gate.check(before)
   self.assertEqual(json.loads((dest/'data/content-dates.json').read_text(encoding='utf8')),dates);self.assertEqual((dest/'sitemap.xml').read_text(encoding='utf8'),xml)
   with patch.object(gate,'ROOT',dest):before=gate.snapshot()
   t=deepcopy(self.tables);t['en']['race.human.line2']='The Human Spirit: +25% experience';t['en']['ability.fireball.name']='Fire Orb'
   sync.apply(self.make(t),root=dest)
   subprocess.run([sys.executable,str(dest/'scripts/build_azeroth_survivors.py')],cwd=dest,check=True,capture_output=True)
   self.assertIn('25% additional experience',(dest/'azeroth-survivors/best-race/index.html').read_text(encoding='utf8'));self.assertIn('Fire Orb',(dest/'azeroth-survivors/abilities/index.html').read_text(encoding='utf8'))
   self.assertIn('Source changes detected:',(dest/'azeroth-survivors/builds/mage/index.html').read_text(encoding='utf8'))
   with patch.object(gate,'ROOT',dest):gate.check(before)
   updated=json.loads((dest/'data/content-dates.json').read_text(encoding='utf8'));self.assertNotEqual(updated['https://megabonk.org/azeroth-survivors/abilities/'],'2020-01-01');self.assertEqual(updated['https://megabonk.org/azeroth-survivors/builds/mage/'],'2020-01-01')
   p=dest/'azeroth-survivors/builds/mage/index.html';p.write_text(p.read_text(encoding='utf8').replace('<h1>','<h1>Changed ',1),encoding='utf8')
   with patch.object(gate,'ROOT',dest),self.assertRaises(ValueError):gate.check(before)
   p.write_text(p.read_text(encoding='utf8').replace('<h1>Changed ','<h1>',1),encoding='utf8');(dest/'unapproved.txt').write_text('outside publication scope',encoding='utf8')
   with patch.object(gate,'ROOT',dest),self.assertRaises(ValueError):gate.check(before)

if __name__=='__main__':unittest.main(verbosity=2)
