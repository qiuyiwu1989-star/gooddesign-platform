import unittest,tempfile,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from build_explore import build
class SourceTests(unittest.TestCase):
 def test_scoped_evidence_and_teacher_assets(self):
  with tempfile.TemporaryDirectory() as t:
   build(Path(t));p=Path(t)/'explore';d=json.loads((p/'deep.json').read_text());self.assertEqual(len(d),6)
   for ex in d.values():
    s=ex['external_source'];self.assertTrue(s['url'].startswith('https://'));self.assertTrue(s['supports'] and s['boundary'] and s['kind'])
   self.assertIn('正文访问失败',d['2023-00']['external_source']['access'])
   self.assertIn('总样品量',d['2025-00']['external_source']['boundary'])
   self.assertIn('2023年',d['2024-02']['external_source']['boundary'])
   for f in ['teacher.html','teacher.js','teacher.css']:self.assertTrue((p/f).is_file())
if __name__=='__main__':unittest.main()
