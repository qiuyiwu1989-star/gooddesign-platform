import unittest,copy
from unittest.mock import patch
from pathlib import Path
from archive_knowledge_search import search
SCHEMA={'patent':{'title':{}},'technology':{'principle':{}}}
def fact(value='pump'):
 return {'value':value,'value_state':'known','content_nature':'source_statement','evidence':{'source_id':'S','chunks_sha256':'hash'}}
class RetrievalTest(unittest.TestCase):
 def setUp(self):
  self.p=patch('archive_knowledge_search.rw.schema',return_value=SCHEMA);self.p.start();self.addCleanup(self.p.stop)
 def run_search(self,data,**kwargs):
  with patch('archive_knowledge_search.pp.load',return_value={'projects':[{'id':'P'}]}),patch('archive_knowledge_search.pp.project',return_value=Path('.')),patch('archive_knowledge_search.rw.current',return_value={'revision':2}),patch('archive_knowledge_search.rw.dataset',return_value=data):return search(Path('.'),'pump',**kwargs)
 def test_requires_query_and_known_scope(self):
  with self.assertRaises(ValueError):search(Path('.'),' ')
  with patch('archive_knowledge_search.pp.load',return_value={'projects':[{'id':'P'}]}):
   with self.assertRaises(ValueError):search(Path('.'),'x',['unknown'])
 def test_only_evidence_cells_with_pagination_and_filters(self):
  data={'records':[{'id':'R','entity':'patent','cells':{'title':fact(),'note':dict(fact(),evidence=None)}}],'interpretations':[{'text':'pump'}],'pending':[{'value':'pump'}]}
  x=self.run_search(data,entity='patent');self.assertEqual(x['total'],1);self.assertEqual(x['data'][0]['revision'],'research-000002');self.assertIn('not_snapshot',x['pagination_consistency'])
 def test_invalid_entity_field_and_pair_rejected(self):
  for args in [dict(entity='wrong'),dict(field='wrong'),dict(entity='patent',field='principle')]:
   with self.assertRaises(ValueError):self.run_search({'records':[]},**args)
 def test_ai_and_nonknown_with_evidence_rejected(self):
  cells={'ok':fact(),'ai':dict(fact(),content_nature='ai_interpretation'),'hyp':dict(fact(),content_nature='ai_hypothesis'),'unknown':dict(fact(),value_state='unknown'),'old_unknown':dict(fact(),value_state='not_researched'),'missing_state':{'value':'pump','evidence':{'source_id':'S'},'content_nature':'source_statement'}}
  x=self.run_search({'records':[{'id':'R','entity':'patent','cells':cells}]});self.assertEqual([r['field']for r in x['data']],['ok'])
 def test_safe_citation_allowlist_omits_paths_and_unknown_metadata(self):
  c=fact();c['evidence'].update(chunks_path='/private/secret.json',original='/Users/private.pdf',future_secret='secret');x=self.run_search({'records':[{'id':'R','entity':'patent','cells':{'title':c}}]})['data'][0]['evidence'];self.assertEqual(x,{'source_id':'S','chunks_sha256':'hash'})
 def test_pages_preserve_order_with_same_snapshot(self):
  data={'records':[{'id':'R'+str(i),'entity':'patent','cells':{'title':fact()}}for i in range(3)]};a=self.run_search(data,limit=2);b=self.run_search(data,limit=2,offset=a['next_offset']);self.assertEqual([r['record_id']for r in a['data']+b['data']],['R0','R1','R2']);self.assertIsNone(b['next_offset'])
 def test_strict_bounds_and_project_shape(self):
  for args in [dict(limit=21),dict(offset=-1),dict(offset=True),dict(limit=1.5),dict(project_ids='P'),dict(project_ids=['P','P']),dict(project_ids=[{}])]:
   with self.assertRaises(ValueError):self.run_search({'records':[]},**args)
 def test_corrupt_project_not_reported_as_zero(self):
  with patch('archive_knowledge_search.pp.load',return_value={'projects':[{'id':'P'}]}),patch('archive_knowledge_search.pp.project',side_effect=ValueError('broken')):
   self.assertEqual(len(search(Path('.'),'pump')['issues']),1)
if __name__=='__main__':unittest.main()
