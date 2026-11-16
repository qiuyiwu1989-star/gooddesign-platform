import sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import archive_knowledge_search as m
class SearchTests(unittest.TestCase):
 def run_search(self,snapshot=None,query='保持工件',offset=0):
  data={'records':[{'id':'R1','entity':'x','cells':{'f':{'value':'保持\n工件','value_state':'known','content_nature':'source_statement','evidence':{'source_id':'S1'}}}}]}
  with patch.object(m,'_evidence',return_value=[{'source_id':'S1'}]),patch.object(m.rw,'schema',return_value={'x':{'f'}}),patch.object(m.pp,'load',return_value={'projects':[{'id':'A'},{'id':'B'}]}),patch.object(m.pp,'project',side_effect=lambda lib,p:p),patch.object(m.rw,'current',side_effect=lambda p:{'revision':1 if p=='A' else 0}) as current,patch.object(m.rw,'dataset',return_value=data):
   result=m.search(Path('.'),query,offset=offset,snapshot=snapshot)
   if snapshot is not None:current.assert_not_called()
   return result
 def test_normalized_coverage_and_quality(self):
  r=self.run_search();self.assertEqual(r['total'],1);self.assertEqual(r['coverage']['searched'],1);self.assertEqual(len(r['coverage']['skipped']),1);self.assertEqual(r['data'][0]['quality_context']['semantic_review'],'not_asserted')
 def test_pinned_does_not_read_current(self):
  s=self.run_search()['snapshot']
  with patch.object(m.rw,'current',side_effect=AssertionError('latest read')):
   # run_search installs its own current mock; test actual pin by count below
   r=self.run_search(s)
  self.assertEqual(r['snapshot'],s)
 def test_query_change_rejected(self):
  s=self.run_search()['snapshot']
  with self.assertRaises(ValueError):self.run_search(s,query='other')
 def test_corrupt_snapshot_rejected(self):
  s=self.run_search()['snapshot'];s['revisions']['A']='research-000009'
  with self.assertRaises(ValueError):self.run_search(s)
if __name__=='__main__':unittest.main()
