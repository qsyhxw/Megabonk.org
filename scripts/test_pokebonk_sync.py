import unittest,json
from copy import deepcopy
from pathlib import Path
from pokebonk_sync import assess,read,ROOT

def fixture():
 state=read('pokebonk-sync.json');tools=read('pokebonk-tools-reference.json');policy=json.loads((ROOT/'config/pokebonk-sync.json').read_text(encoding='utf8'));roles=state['accepted']['league']['data'];species={f['id']:{'id':f['id'],'types':r['types'],'stats':f['raw']}for r in roles for f in r['forms']}
 return dict(schema=1,observed=state['observed'],**state['source'],adapter_ok=True,arches=read('pokebonk-progression-reference.json')['arches'],lab=state['accepted']['lab']['data'],items=state['accepted']['items']['data'],moves=state['accepted']['moves']['data'],alpha=state['accepted']['alpha']['data'],league=[dict(id=r['id'],role=r['role'],rank=r['rank'],start=r['start'],kit=[m['key']for m in r['kit']],passive=str(r['id']),challenge=policy['challenges'][str(r['id'])])for r in roles],passives={str(r['id']):r['passive']for r in roles},species=list(species.values()),news=[dict(version='0.8.76',title='Client update',notes=[])])

class SyncTests(unittest.TestCase):
 def setUp(self):self.c=fixture();self.base,_=assess(self.c)
 def test_identical_is_noop(self):self.assertEqual(assess(self.c,self.base)[0],self.base)
 def test_lab_price_updates_without_owning_upgrade(self):
  self.c['lab'][0]['costs'][0]+=10;s,domains=assess(self.c,self.base);self.assertIn('lab',domains);self.assertEqual(s['accepted']['lab']['data'][0]['costs'][0],self.c['lab'][0]['costs'][0]);self.assertNotIn('owned',s)
 def test_invalid_prices_preserve_state(self):
  saved=deepcopy(self.base);self.c['lab'][0]['costs'][0]=-1
  with self.assertRaises(ValueError):assess(self.c,self.base)
  self.assertEqual(saved,self.base)
 def test_missing_schedule_rejected(self):
  self.c['lab'][0]['costs']=[]
  with self.assertRaises(ValueError):assess(self.c,self.base)
 def test_duplicates_rejected(self):
  self.c['items'].append(self.c['items'][0])
  with self.assertRaises(ValueError):assess(self.c,self.base)
 def test_adapter_change_keeps_combat_but_accepts_lab(self):
  self.c['adapter_ok']=False;self.c['items'][0]['desc']='Unreviewed';self.c['lab'][0]['costs'][0]+=10;s,domains=assess(self.c,self.base);self.assertEqual(s['accepted']['items'],self.base['accepted']['items']);self.assertIn('lab',domains);self.assertTrue(s['pending'])
 def test_new_entity_does_not_create_page(self):
  self.c['items'].pop();s,_=assess(self.c,self.base);self.assertEqual(s['accepted']['items'],self.base['accepted']['items']);self.assertTrue(s['pending'])
 def test_changed_capture_requires_review(self):
  self.c['league'][0]['challenge']['goal']+=1;s,_=assess(self.c,self.base);self.assertEqual(s['accepted']['league'],self.base['accepted']['league']);self.assertTrue(s['pending'])
 def test_source_change_marks_prose_and_stays_pending(self):
  self.c['client_sha256']='a'*64;s,_=assess(self.c,self.base);self.assertTrue(s['pending']);self.assertEqual(assess(self.c,s)[0],s)
 def test_wrong_host_rejected(self):
  self.c['config']='https://other.example/a.js'
  with self.assertRaises(ValueError):assess(self.c,self.base)
 def test_nonfinite_rejected(self):
  self.c['lab'][0]['costs'][0]=float('nan')
  with self.assertRaises(ValueError):assess(self.c,self.base)
 def test_unknown_arch_rejected(self):
  self.c['moves'][0]['arch']='new-runtime'
  with self.assertRaises(ValueError):assess(self.c,self.base)

if __name__=='__main__':unittest.main()
