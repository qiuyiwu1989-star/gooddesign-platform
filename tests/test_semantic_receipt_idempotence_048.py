import concurrent.futures,copy,json,sys,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import test_research_pipeline_038 as base
import test_semantic_agent_046 as semantic_tests
import archive_steward as ast,project_pipeline as pp,research_workflow as rw
from semantic_agent import SemanticQueue
from semantic_service import Service

class SubmissionReceiptTests(unittest.TestCase):
 setUp=base.ResearchTests.setUp
 tearDown=base.ResearchTests.tearDown
 response=semantic_tests.SemanticTests.response
 def bundle(self):
  return dict(project_id='sample',candidates=[dict(entity='paper',record_id='A01',title='测试论文',field='doi',value='10.1234/test.2026',source_id=self.sid,chunk_id='B0001',quote='DOI:10.1234/test.2026')])
 def steward(self):return ast.Steward(self.lib,self.inbox)
 def service(self):
  steward=self.steward();queue=SemanticQueue(self.lib,self.root/'semantic',lambda p,f:self.response());store=SimpleNamespace(lib=self.lib,folder=steward.folder,steward=steward);return Service(store,queue)
 def test_actual_publication_then_lost_json_receipt_reuses_task_before_revalidation(self):
  service=self.service();service.queue.enqueue('sample',[self.sid]);service.queue.step();save=pp.save
  def crash_receipt(path,value):
   if Path(path)==service.file:raise OSError('simulated crash before semantic-control receipt')
   return save(path,value)
  with patch.object(pp,'save',side_effect=crash_receipt),self.assertRaises(OSError):service.receipt('sample',1)
  self.assertTrue(service.store.steward.tick());self.assertEqual(rw.current(self.p)['revision'],1);snapshot=rw.workspace(self.p)/'版本/research-000001/档案.json';before=pp.sha(snapshot.read_bytes())
  restarted=Service(SimpleNamespace(lib=self.lib,folder=service.store.folder,steward=self.steward()),service.queue)
  with patch.object(rw,'add_candidate',side_effect=AssertionError('must not recompute candidates after publication')):receipt=restarted.receipt('sample',1)
  self.assertEqual(receipt['status'],'submitted_to_evidence_gate');self.assertFalse(restarted.store.steward.tick());self.assertEqual(rw.current(self.p)['revision'],1);self.assertEqual(len(rw.current(self.p)['candidates']),1);self.assertEqual(pp.sha(snapshot.read_bytes()),before)
 def test_same_key_same_payload_after_publish_returns_original_task(self):
  steward=self.steward();bundle=self.bundle();first=steward.submit_bundle('sample',bundle,'Agent',submission_key='key-1');steward.tick()
  with patch.object(rw,'add_candidate',side_effect=AssertionError('must not propose again')):second=self.steward().submit_bundle('sample',bundle,'new process',submission_key='key-1')
  self.assertEqual(first['id'],second['id']);self.assertEqual(second['status'],'completed');self.assertEqual(rw.current(self.p)['revision'],1)
 def test_prepared_intent_survives_crash_before_working_state_save(self):
  steward=self.steward();bundle=self.bundle()
  with patch.object(rw,'save',side_effect=OSError('save interrupted')),self.assertRaises(OSError):steward.submit_bundle('sample',bundle,'Agent',submission_key='prepared')
  self.assertFalse(rw.current(self.p)['candidates'])
  with steward.connect()as db:self.assertEqual(db.execute('SELECT COUNT(*) FROM submissions WHERE task_id IS NULL').fetchone()[0],1)
  with patch.object(rw,'add_candidate',side_effect=AssertionError('frozen candidate must be reused')):task=self.steward().submit_bundle('sample',bundle,'retry process',submission_key='prepared')
  self.assertEqual(len(rw.current(self.p)['candidates']),1);self.assertTrue(steward.tick());self.assertEqual(rw.current(self.p)['revision'],1)
 def test_prepared_intent_survives_work_save_before_task_transaction(self):
  steward=self.steward();bundle=self.bundle()
  with patch.object(steward,'_finish_submission',side_effect=OSError('task commit interrupted')),self.assertRaises(OSError):steward.submit_bundle('sample',bundle,'Agent',submission_key='work-saved')
  self.assertEqual(len(rw.current(self.p)['candidates']),1)
  with patch.object(rw,'add_candidate',side_effect=AssertionError('no new base_cell calculation')):task=self.steward().submit_bundle('sample',bundle,'retry',submission_key='work-saved')
  self.assertTrue(steward.tick());self.assertFalse(steward.tick());self.assertEqual(rw.current(self.p)['revision'],1)
 def test_concurrent_same_identity_serializes_into_one_task(self):
  bundle=self.bundle()
  with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:
   results=list(pool.map(lambda _:self.steward().submit_bundle('sample',bundle,'parallel Agent',submission_key='same-concurrent'),range(4)))
  self.assertEqual(len({r['id']for r in results}),1);self.assertEqual(len(rw.current(self.p)['candidates']),1);steward=self.steward();self.assertTrue(steward.tick());self.assertFalse(steward.tick());self.assertEqual(rw.current(self.p)['revision'],1)
 def test_same_key_changed_payload_or_project_is_rejected_before_propose(self):
  steward=self.steward();bundle=self.bundle();steward.submit_bundle('sample',bundle,'Agent',submission_key='collision');changed=copy.deepcopy(bundle);changed['candidates'][0]['quote']='10.1234/test.2026'
  with patch.object(rw,'add_candidate',side_effect=AssertionError('must reject identity collision first')):
   with self.assertRaises(ValueError):steward.submit_bundle('sample',changed,'Agent',submission_key='collision')
  catalog=self.root/'other-catalog.json';pp.save(catalog,dict(projects=[dict(id='other',name='Other')]));pp.bootstrap(self.lib,self.inbox,catalog,self.root/'archive');other=copy.deepcopy(bundle);other['project_id']='other'
  with self.assertRaises(ValueError):steward.submit_bundle('other',other,'Agent',submission_key='collision')
  self.assertEqual(len(rw.current(self.p)['candidates']),1)
 def test_bad_new_payload_and_shared_source_do_not_reserve_identity(self):
  steward=self.steward();invalid=self.bundle();invalid['candidates'].append(dict(invalid['candidates'][0],field='not_a_field'))
  with self.assertRaises(ValueError):steward.submit_bundle('sample',invalid,'Agent',submission_key='invalid')
  pp.save(self.p/'资料归属.json',dict(version=1,assignments={self.sid:dict(scope='shared')},url_rules={}))
  with self.assertRaises(ValueError):steward.submit_bundle('sample',self.bundle(),'Agent',submission_key='shared')
  self.assertFalse(rw.current(self.p)['candidates'])
  with steward.connect()as db:self.assertEqual(db.execute('SELECT COUNT(*) FROM submissions').fetchone()[0],0)
 def test_prepared_old_scope_cannot_bypass_evidence_gate(self):
  steward=self.steward();bundle=self.bundle()
  with patch.object(rw,'save',side_effect=OSError('interrupted')),self.assertRaises(OSError):steward.submit_bundle('sample',bundle,'Agent',submission_key='scope-after-intent')
  pp.save(self.p/'资料归属.json',dict(version=1,assignments={self.sid:dict(scope='shared')},url_rules={}))
  steward.submit_bundle('sample',bundle,'retry',submission_key='scope-after-intent');steward.tick();self.assertEqual(rw.current(self.p)['revision'],0);self.assertEqual(steward.summary('sample')['counts']['needs_attention'],1)
 def test_old_failure_receipt_does_not_block_new_attempt_identity(self):
  service=self.service()
  def fail(*args):raise RuntimeError('model unavailable')
  service.queue.reader=fail;service.queue.enqueue('sample',[self.sid]);service.queue.step();self.assertEqual(service.receipt('sample',1)['status'],'failed');service.queue.retry(1,'sample','explicit additional budget');service.queue.reader=lambda p,f:self.response();service.queue.step();receipt=service.receipt('sample',1);self.assertEqual(receipt['status'],'submitted_to_evidence_gate');self.assertEqual(receipt['queue_token']['attempts'],2);self.assertTrue(service.store.steward.tick());self.assertEqual(rw.current(self.p)['revision'],1)
 def test_unkeyed_calls_remain_compatible(self):
  steward=self.steward();task=steward.submit_bundle('sample',self.bundle(),'legacy Agent');self.assertTrue(steward.tick());self.assertEqual(rw.current(self.p)['revision'],1)
  with steward.connect()as db:self.assertEqual(db.execute('SELECT COUNT(*) FROM submissions').fetchone()[0],0)
 def test_distinct_attempt_keys_do_not_alias_each_other(self):
  steward=self.steward();bundle=self.bundle();first=steward.submit_bundle('sample',bundle,'Agent',submission_key='job-1-attempt-1-result-A');second=steward.submit_bundle('sample',bundle,'Agent',submission_key='job-1-attempt-2-result-B');self.assertNotEqual(first['id'],second['id']);self.assertEqual(len(rw.current(self.p)['candidates']),1);steward.tick();steward.tick();self.assertEqual(rw.current(self.p)['revision'],1)
 def test_existing_task_without_submission_ledger_fails_before_new_candidates(self):
  steward=self.steward();steward.enqueue('sample',dict(kind='source',source_id=self.sid),key=steward._submission_task_key('orphan'))
  with patch.object(rw,'add_candidate',side_effect=AssertionError('task identity must be checked first')),self.assertRaises(ValueError):steward.submit_bundle('sample',self.bundle(),'Agent',submission_key='orphan')
  self.assertFalse(rw.current(self.p)['candidates'])
 def test_corrupt_submission_snapshot_is_not_recomputed_as_a_new_submission(self):
  steward=self.steward();bundle=self.bundle();steward.submit_bundle('sample',bundle,'Agent',submission_key='corrupt-ledger')
  with steward.connect()as db:db.execute("UPDATE submissions SET candidates_sha256='corrupt' WHERE key='corrupt-ledger'")
  with patch.object(rw,'add_candidate',side_effect=AssertionError('must not replace damaged ledger')),self.assertRaises(ValueError):steward.submit_bundle('sample',bundle,'retry',submission_key='corrupt-ledger')
  self.assertEqual(len(rw.current(self.p)['candidates']),1)
if __name__=='__main__':unittest.main()
