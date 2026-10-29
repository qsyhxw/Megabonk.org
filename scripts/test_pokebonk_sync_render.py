"""Exercise a synthetic price change through the real generators in isolation."""
from pathlib import Path
import json,re,shutil,subprocess,sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1]
class RenderTest(unittest.TestCase):
 def test_lab_change_reaches_all_calculators(self):
  with tempfile.TemporaryDirectory()as temp:
   root=Path(temp);(root/'scripts').mkdir();(root/'data').mkdir()
   for p in (ROOT/'scripts').glob('*.py'):shutil.copyfile(p,root/'scripts'/p.name)
   for p in (ROOT/'data').glob('pokebonk*.json'):shutil.copyfile(p,root/'data'/p.name)
   path=root/'data/pokebonk-sync.json';state=json.loads(path.read_text(encoding='utf8'));row=next(x for x in state['accepted']['lab']['data']if x['id']=='slot-move');row['costs'][0]+=17;expected=row['costs'][0];path.write_text(json.dumps(state),encoding='utf8')
   subprocess.run([sys.executable,'scripts/build_pokebonk.py'],cwd=root,check=True,stdout=subprocess.DEVNULL)
   for slug,ids in [('lab',['task-data','decision-data','progression-data']),('build-planner',['task-data','progression-data'])]:
    html=(root/f'pokebonk/{slug}/index.html').read_text(encoding='utf8')
    for id in ids:
     m=re.search(r'<script[^>]*id="'+id+r'"[^>]*>(.*?)</script>',html,re.S);self.assertIsNotNone(m,id);data=json.loads(m[1]);data=data.get('current',data);self.assertEqual(next(x for x in data['lab']if x['id']=='slot-move')['costs'][0],expected,(slug,id))
if __name__=='__main__':unittest.main()
