import sys,unittest
from pathlib import Path
from unittest.mock import patch
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import mcp_method_assets as m
class AssetsTests(unittest.TestCase):
 def test_frozen_default_and_alias(self):
  x=m.read_asset('R17');self.assertEqual(x['profile'],'frozen');self.assertTrue(x['execution_available']);self.assertEqual(m.read_asset(x['asset']['method_id'])['sha256'],x['sha256'])
 def test_deep_partial(self):
  x=m.read_asset('WB01','deep');self.assertTrue(x['partial_ratings']);self.assertFalse(x['execution_available']);self.assertIn('content',x)
 def test_benchmarks_real(self):
  for rid in ['R17','R02','R52']:
   x=m.read_asset(rid,'benchmark');self.assertEqual(x['status'],'available');self.assertFalse(x['candidate_contract_activated'])
  self.assertEqual(m.read_asset('R48','benchmark')['status'],'profile_unavailable')
 def test_unknown(self):
  for rid,p in [('R99','frozen'),('R17','../private')]:
   with self.assertRaises(ValueError):m.read_asset(rid,p)
 def test_path_and_checksum(self):
  for p in ['../x','/tmp/x','private-sources/x','a\\b']:
   with self.assertRaises(ValueError):m._safe(m.ROOT,p)
  with self.assertRaises(ValueError):m._checked(m.BENCHMARK,'目录.json','wrong')
 def test_symlink_rejected(self):
  import tempfile
  with tempfile.TemporaryDirectory(dir=m.ROOT/'output') as folder:
   base=Path(folder);(base/'a').write_text('safe');(base/'link').symlink_to(base/'a')
   with self.assertRaises(ValueError):m._safe(base,'link')
 def test_white_lists(self):
  self.assertFalse(m.workflow_prompt('transfer_review')['executed']);self.assertEqual(m.schema_resource('method_profiles')['data']['default'],'frozen')
  for fn in [m.workflow_prompt,m.schema_resource]:
   with self.assertRaises(ValueError):fn('/etc/passwd')
if __name__=='__main__':unittest.main()
