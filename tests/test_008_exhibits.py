import unittest,json,tempfile,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from build_explore import build,SRC
class ExhibitTests(unittest.TestCase):
 def test_all_fields_have_exact_sources(self):
  with tempfile.TemporaryDirectory() as t:
   build(Path(t));data=json.loads((Path(t)/'explore/deep.json').read_text())
   self.assertTrue({'2025-00','2015-02'}.issubset(data))
   for pid,ex in data.items():
    self.assertEqual({f['key'] for f in ex['fields']},{'problem','constraints','method','evidence'})
    for f in ex['fields']:
     s=f['source'];raw=(SRC/s['url'].lstrip('/')).read_bytes()
     self.assertEqual(json.loads(raw)[s['field']][s['start']:s['end']],f['quote'])
     self.assertEqual(hashlib.sha256(raw).hexdigest(),s['sha256'])
    self.assertIn(ex['activity']['evidence_key'],[f['key'] for f in ex['fields']])
    self.assertEqual(len(ex['activity']['options']),3)
    self.assertEqual(len({o['feedback'] for o in ex['activity']['options']}),3)
   self.assertIn('未附完整',data['2015-02']['fields'][3]['text'])
if __name__=='__main__':unittest.main()
