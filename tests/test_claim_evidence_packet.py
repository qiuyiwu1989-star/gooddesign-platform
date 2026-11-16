import sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import claim_evidence_packet as m
class PacketTests(unittest.TestCase):
 def test_requires_version(self):
  with self.assertRaises(ValueError):m.read(Path('.'),'A',None,'R','f')
 def test_unknown_field(self):
  with patch.object(m.pp,'project',return_value=Path('.')),patch.object(m.rw,'check_version',return_value=(Path('.'),{})),patch.object(m.rw,'dataset',return_value={'records':[]}):
   with self.assertRaises(ValueError):m.read(Path('.'),'A','research-000001','R','f')
 def test_ai_not_fact(self):
  data={'records':[{'id':'R','cells':{'f':{'value_state':'known','content_nature':'ai_interpretation'}}}]}
  with patch.object(m.pp,'project',return_value=Path('.')),patch.object(m.rw,'check_version',return_value=(Path('.'),{})),patch.object(m.rw,'dataset',return_value=data):
   with self.assertRaises(ValueError):m.read(Path('.'),'A','research-000001','R','f')
if __name__=='__main__':unittest.main()
