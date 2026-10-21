import sys,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import test_research_pipeline_038 as base
import project_pipeline as pp,research_workflow as rw,archive_mcp as mcp
class EvidenceTests(unittest.TestCase):
 setUp=base.ResearchTests.setUp
 tearDown=base.ResearchTests.tearDown
 candidate=base.ResearchTests.candidate
 approve=base.ResearchTests.approve
 def first(self):
  a=self.candidate();self.approve(a);rw.publish(self.lib,'sample','tester','first');return a
 def test_supporting_evidence_from_prior_source_still_readable(self):
  self.first();raw=self.root/'new.txt';raw.write_text('DOI:10.1234/test.2026 新的公开来源');sid=pp.ingest(self.p,raw)['source_id'];a=self.candidate(source_id=sid,chunk_id='B0001');self.approve(a);rw.publish(self.lib,'sample','tester','support')
  with patch.object(mcp,'LIB',self.lib):r=mcp.gd_read_evidence('sample',self.sid,'research-000002')
  self.assertTrue(r['data']);self.assertEqual(r['source_id'],self.sid)
 def test_multiple_text_revisions_can_be_selected_by_frozen_hash_only(self):
  a=self.first();state=pp.state(self.p);old=state['sources'][self.sid]['chunks'];new='衍生/reclean/chunks.json';blocks=pp.load(self.p/old);blocks[0]['text']+=' new text';pp.save(self.p/new,blocks);state['sources'][self.sid]['chunks']=new;pp.commit(self.p,state,'reclean');b=self.candidate(quote='10.1234/test.2026');self.approve(b);rw.publish(self.lib,'sample','tester','new evidence')
  with patch.object(mcp,'LIB',self.lib):
   menu=mcp.gd_read_evidence('sample',self.sid,'research-000002');self.assertTrue(menu['requires_chunks_sha256']);self.assertEqual(len(menu['available_text_revisions']),2)
   old_read=mcp.gd_read_evidence('sample',self.sid,'research-000002',chunks_sha256=a['chunks_sha256']);new_read=mcp.gd_read_evidence('sample',self.sid,'research-000002',chunks_sha256=b['chunks_sha256']);self.assertNotEqual(old_read['chunks_sha256'],new_read['chunks_sha256'])
   with self.assertRaises(ValueError):mcp.gd_read_evidence('sample',self.sid,'research-000002',chunks_sha256='../../private')
   with self.assertRaises(ValueError):mcp.gd_read_evidence('sample',self.sid,chunks_sha256=a['chunks_sha256'])
 def test_current_scope_still_blocks_historical_support(self):
  self.first();pp.save(self.p/'资料归属.json',dict(version=1,assignments={self.sid:dict(scope='shared')},url_rules={}))
  with patch.object(mcp,'LIB',self.lib),self.assertRaises(ValueError):mcp.gd_read_evidence('sample',self.sid,'research-000001')
if __name__=='__main__':unittest.main()
