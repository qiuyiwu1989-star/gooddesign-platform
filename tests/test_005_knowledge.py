import unittest, json, hashlib, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build_knowledge_index import build, SRC, meaningful
class KnowledgeTests(unittest.TestCase):
 def test_provenance_and_links(self):
  with tempfile.TemporaryDirectory() as tmp:
   data=build(Path(tmp))
   self.assertEqual(len(data['projects']),560)
   self.assertEqual(len({p['id'] for p in data['projects']}),560)
   for p in data['projects']:
    self.assertTrue((SRC/p['project_url'].lstrip('/')).exists())
    self.assertTrue((SRC/p['knowledge_url'].lstrip('/')).exists())
   for m in data['mechanisms']:
    s=m['source']; raw=(SRC/s['url'].lstrip('/')).read_bytes()
    self.assertEqual(hashlib.sha256(raw).hexdigest(),s['sha256'])
    self.assertEqual(json.loads(raw)[s['field']][s['start']:s['end']],m['excerpt'])
    self.assertIsNone(m['triz_mapping'])
    self.assertIsNone(m['validation_result'])
 def test_placeholders(self):
  for value in ['', ' 无 ', '待补充',None]: self.assertFalse(meaningful(value))
  self.assertTrue(meaningful('实际技术描述'))
 def test_original_home(self):
  self.assertEqual((SRC/'index.html').read_bytes(),(ROOT/'original-app/public/index.html').read_bytes())
if __name__=='__main__':unittest.main()
