import sys,unittest,concurrent.futures,json
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import test_research_pipeline_038 as base
import test_semantic_agent_046 as semantic_tests
from semantic_service import Service
from semantic_agent import SemanticQueue
from archive_steward import Steward
import project_pipeline as pp,research_workflow as rw
class ServiceTests(unittest.TestCase):
 setUp=base.ResearchTests.setUp
 response=semantic_tests.SemanticTests.response
 def tearDown(self):
  if hasattr(self,'store'):self.store.pool.shutdown(wait=True);self.store.steward.close()
  base.ResearchTests.tearDown(self)
 def service(self,reader=None):
  q=SemanticQueue(self.lib,self.root/'semantic',reader or(lambda p,f:self.response()))
  self.store=SimpleNamespace(lib=self.lib,inbox=self.inbox,folder=self.lib/'.file-admin',pool=concurrent.futures.ThreadPoolExecutor(max_workers=1),steward=Steward(self.lib,self.inbox))
  return Service(self.store,q)
 def test_ready_after_restart_handed_off_once(self):
  s=self.service();s.queue.enqueue('sample',[self.sid]);s.queue.step();s.pump();first=s.state()['receipts']['1'];s.pump();self.assertEqual(s.state()['receipts']['1'],first);self.assertEqual(first['status'],'submitted_to_evidence_gate');self.store.steward.tick();self.assertEqual(rw.dataset(self.p)['records'][0]['cells']['doi']['value'],'10.1234/test.2026');self.assertFalse(rw.dataset(self.p)['expert_reviewed'])
 def test_failed_receipt_does_not_block_explicit_retry(self):
  def fail(*args):raise RuntimeError('offline')
  s=self.service(fail);s.queue.enqueue('sample',[self.sid]);s.queue.step();self.assertEqual(s.receipt('sample',1)['status'],'failed');s.queue.reader=lambda p,f:self.response();s.queue.retry(1,'sample','显式重试');s.queue.step();self.assertEqual(s.receipt('sample',1)['status'],'submitted_to_evidence_gate')
 def test_risks_never_submitted(self):
  s=self.service(lambda p,f:self.response(risks=['原文口径待澄清']));s.queue.enqueue('sample',[self.sid]);s.queue.step();s.pump();self.assertEqual(s.state()['receipts']['1']['status'],'needs_review');self.assertFalse(rw.current(self.p)['candidates'])
 def test_pause_and_budget_new_files_only(self):
  s=self.service();s.configure('sample',True,1);self.assertFalse(s.queue.status('sample')['jobs'])
  for i in range(2):
   f=self.root/('new%d.txt'%i);f.write_text('new source '+str(i));pp.ingest(self.p,f)
  s.discover();self.assertEqual(len(s.queue.status('sample')['jobs']),1);s.discover();self.assertEqual(len(s.queue.status('sample')['jobs']),1);self.store.steward.pause(True);s.pump();self.assertIsNone(s.future)
  with self.assertRaises(ValueError):s.result('other',1)
 def test_expired_lease_without_queued_work_is_recovered(self):
  s=self.service();s.queue.enqueue('sample',[self.sid])
  with s.queue.connect()as db:db.execute("UPDATE jobs SET status='running',attempts=1,lease=0")
  s.pump();s.future.result(timeout=5);self.assertEqual(s.queue.get(1)['status'],'needs_attention')
if __name__=='__main__':unittest.main()
