import unittest
from unittest.mock import patch
from pathlib import Path
from archive_knowledge_search import search
class RetrievalTest(unittest.TestCase):
 def test_requires_query_and_known_scope(self):
  with self.assertRaises(ValueError):search(Path('.'),' ')
  with patch('archive_knowledge_search.pp.load',return_value={'projects':[{'id':'P'}]}):
   with self.assertRaises(ValueError):search(Path('.'),'x',['unknown'])
 def test_only_evidence_cells_with_pagination_and_filters(self):
  data={'records':[{'id':'R','entity':'patent','cells':{'title':{'value':'pump','evidence':{'source_id':'S'}},'note':{'value':'pump','evidence':None}}}],'interpretations':[{'text':'pump'}]}
  with patch('archive_knowledge_search.pp.load',return_value={'projects':[{'id':'P'}]}),patch('archive_knowledge_search.pp.project',return_value=Path('.')),patch('archive_knowledge_search.rw.current',return_value={'revision':2}),patch('archive_knowledge_search.rw.dataset',return_value=data):
   x=search(Path('.'),'pump',entity='patent');self.assertEqual(x['total'],1);self.assertEqual(x['data'][0]['revision'],'research-000002');self.assertEqual(search(Path('.'),'pump',field='missing')['total'],0)
 def test_corrupt_project_not_reported_as_zero(self):
  with patch('archive_knowledge_search.pp.load',return_value={'projects':[{'id':'P'}]}),patch('archive_knowledge_search.pp.project',side_effect=ValueError('broken')):
   self.assertEqual(len(search(Path('.'),'pump')['issues']),1)
if __name__=='__main__':unittest.main()
