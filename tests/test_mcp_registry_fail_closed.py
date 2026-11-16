import sys,json,tempfile,hashlib,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from innovation_gateway_http import BearerAuth
class RegistryBoundary(unittest.TestCase):
 def test_missing_registry_must_not_revive_legacy(self):
  import project_pipeline as pp
  with tempfile.TemporaryDirectory(dir=pp.ROOT/'output') as t:
   p=Path(t);keys=p/'keys.json';keys.write_text(json.dumps({'keys':[{'enabled':True,'sha256':hashlib.sha256(b'old-token').hexdigest()}]}))
   auth=BearerAuth(None,keys,p/'missing.sqlite')
   self.assertEqual(auth.identify([(b'authorization',b'Bearer old-token')]),(None,'registry_unavailable'))
   self.assertEqual(BearerAuth(None,keys).identify([(b'authorization',b'Bearer old-token')]),('legacy',None))
 def test_corrupt_registry_refuses_without_exception(self):
  import project_pipeline as pp
  with tempfile.TemporaryDirectory(dir=pp.ROOT/'output') as t:
   p=Path(t);(p/'broken').write_text('not a database')
   self.assertEqual(BearerAuth(None,p/'keys',p/'broken').identify([(b'authorization',b'Bearer x')]),(None,'registry_unavailable'))
if __name__=='__main__':unittest.main()
