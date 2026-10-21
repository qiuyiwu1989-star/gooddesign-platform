import sys,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import test_research_pipeline_038 as base
import project_pipeline as pp,research_workflow as rw
from archive_steward import Steward,AGENT_METHOD
class ReviewedExceptions(unittest.TestCase):
 setUp=base.ResearchTests.setUp
 tearDown=base.ResearchTests.tearDown
 candidate=base.ResearchTests.candidate
 def fixture(self,extra=False):
  s=Steward(self.lib,self.inbox);c=self.candidate(record_id='DOC-'+self.sid,extraction_method='conservative_rules_v1');t=s.enqueue_source('sample',self.sid)
  exceptions=[dict(candidate_id=c['id'])]+([dict(candidate_id='other')]if extra else[])
  with s.connect()as d:d.execute("UPDATE tasks SET status='needs_attention',result=? WHERE id=?",(json.dumps(dict(exceptions=exceptions,kept='old')),t['id']))
  return s,c,t
 def state(self,s,t):
  with s.connect()as d:return dict(d.execute('SELECT * FROM tasks WHERE id=?',(t['id'],)).fetchone())
 def reject(self,c,kind='agent',decision='rejected'):rw.review(self.lib,'sample',c['id'],decision,'审读员','提取前缀不构成完整编号',reviewer_kind=kind)
 def test_explicit_rejection_closes_exception_but_keeps_agent_read_pending(self):
  s,c,t=self.fixture();self.reject(c);s.reconcile_identifiers('sample');row=self.state(s,t);self.assertEqual(row['status'],'awaiting_agent');result=json.loads(row['result']);self.assertEqual(result['kept'],'old');self.assertEqual(result['previous_exceptions'],[dict(candidate_id=c['id'])]);self.assertEqual(result['identifier_resolution'][c['id']]['reviewer_kind'],'agent');self.assertEqual(rw.current(self.p)['revision'],0)
 def test_researched_source_can_complete_and_action_is_idempotent(self):
  s,c,t=self.fixture();good=self.candidate(extraction_method=AGENT_METHOD);rw.review(self.lib,'sample',good['id'],'approved','Agent','按证据确认',reviewer_kind='agent');rw.publish(self.lib,'sample','发布','测试');self.reject(c,'human');before=rw.dataset(self.p);s.reconcile_identifiers('sample');self.assertEqual(self.state(s,t)['status'],'completed');controls=s.summary('sample')['controls'];s.reconcile_identifiers('sample');self.assertEqual(s.summary('sample')['controls'],controls);self.assertEqual(rw.dataset(self.p),before)
 def test_partial_needs_more_and_approved_do_not_close(self):
  s,c,t=self.fixture(extra=True);self.reject(c);s.reconcile_identifiers('sample');self.assertEqual(self.state(s,t)['status'],'needs_attention')
  for decision in ['needs_more','approved']:
   rw.review(self.lib,'sample',c['id'],decision,'人','继续核对');s.reconcile_identifiers('sample');self.assertEqual(self.state(s,t)['status'],'needs_attention')
 def test_stale_raw_and_task_identity_do_not_close(self):
  s,c,t=self.fixture();self.reject(c)
  with s.connect()as d:
   payload=json.loads(t['payload']);payload['source_sha256']='different';d.execute('UPDATE tasks SET payload=? WHERE id=?',(json.dumps(payload),t['id']))
  s.reconcile_identifiers('sample');self.assertEqual(self.state(s,t)['status'],'needs_attention')
  with s.connect()as d:d.execute('UPDATE tasks SET payload=? WHERE id=?',(t['payload'],t['id']))
  x=pp.state(self.p)['sources'][self.sid];(self.p/x['original']).write_bytes(b'changed');s.reconcile_identifiers('sample');self.assertEqual(self.state(s,t)['status'],'needs_attention')
if __name__=='__main__':unittest.main()
