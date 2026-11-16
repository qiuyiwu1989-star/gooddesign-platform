import sys,unittest,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from mcp_research_services import quality_envelope,transfer_check
from mcp_delivery_ledger import record
import project_pipeline as pp


class ServiceTests(unittest.TestCase):
 def test_no_quality_promotion_or_mutation(self):
  original={'quality':'legacy','data':[{'value':'x'}]}
  result=quality_envelope(original,'read');self.assertEqual(original['quality'],'legacy');self.assertNotIn('service_metadata',original);self.assertEqual(result['service_metadata']['quality']['semantic_review'],'not_asserted_by_gateway')
 def test_transfer_needs_explicit_requirement(self):
  with self.assertRaises(ValueError):transfer_check(None,'x','x','x',{'text':'something'})
 def test_delivery_transitions_and_idempotency(self):
  with tempfile.TemporaryDirectory(dir=pp.ROOT/'output') as t:
   p=str(Path(t)/'test.sqlite')
   with self.assertRaises(ValueError):record(p,'KEY-12345678','client_verified','admin','R0')
   for i,state in enumerate(['issued','delivered','client_updated','client_verified']):record(p,'KEY-12345678',state,'admin','R'+str(i))
   self.assertEqual(record(p,'KEY-12345678','client_verified','admin','R3')['status'],'existing')
   record(p,'KEY-12345678','revoked','admin','R4')
   with self.assertRaises(ValueError):record(p,'KEY-12345678','issued','admin','R5')
 def test_no_token_identity(self):
  with self.assertRaises(ValueError):record('unused','gd_secret','issued','admin','R')


if __name__=='__main__':unittest.main()
