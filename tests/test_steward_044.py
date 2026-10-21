# coding: utf-8
import sys,time,unittest,json
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(ROOT/'tests'))
import test_research_pipeline_038 as base
import project_pipeline as pp,research_workflow as rw
from archive_steward import Steward,AGENT_METHOD
class StewardTests(unittest.TestCase):
 setUp=base.ResearchTests.setUp
 tearDown=base.ResearchTests.tearDown
 candidate=base.ResearchTests.candidate
 approve=base.ResearchTests.approve
 def steward(self):return Steward(self.lib,self.inbox)
 def agent(self,**extra):return self.candidate(extraction_method=AGENT_METHOD,**extra)
 def test_incremental_rule_auto_publication(self):
  s=self.steward();task=s.enqueue_source('sample',self.sid);self.assertEqual(s.enqueue_source('sample',self.sid)['id'],task['id']);self.assertTrue(s.tick());self.assertFalse(s.tick())
  data=rw.dataset(self.p);c=rw.cell(data,'A01','doi');self.assertEqual(c['value'],'10.1234/test.2026');self.assertEqual(c['verification_state'],'automated_evidence_checked_not_expert');self.assertFalse(data['expert_reviewed']);self.assertEqual(rw.current(self.p)['revision'],1)
 def test_agent_batch_no_manual_clicks(self):
  c=self.agent();s=self.steward();s.enqueue_candidates('sample',[c['id']]);s.tick();self.assertEqual(rw.current(self.p)['revision'],1);self.assertEqual(rw.current(self.p)['candidates'][0]['reviewer_kind'],'agent')
 def test_human_approved_not_piggybacked(self):
  manual=self.candidate(field='findings',value='满足试验需求',quote='满足试验需求');self.approve(manual)
  c=self.agent();s=self.steward();s.enqueue_candidates('sample',[c['id']]);s.tick();self.assertEqual(next(x for x in rw.current(self.p)['candidates']if x['id']==manual['id'])['status'],'approved');self.assertIsNone(rw.cell(rw.dataset(self.p),'A01','findings')['value'])
 def test_conflicting_candidates_remain_exception(self):
  a=self.agent();b=self.agent(value='10.1234/test.202',quote='DOI:10.1234/test.2026');s=self.steward();s.enqueue_candidates('sample',[a['id'],b['id']]);s.tick();d=s.summary('sample');self.assertEqual(d['counts']['needs_attention'],1);self.assertEqual(rw.current(self.p)['revision'],0);self.assertEqual(len(d['recent'][0]['result']['exceptions']),2)
 def test_existing_fact_not_overwritten(self):
  a=self.candidate();self.approve(a);rw.publish(self.lib,'sample','人','基线');b=self.agent(value='10.1234/test.202',quote='DOI:10.1234/test.2026');s=self.steward();s.enqueue_candidates('sample',[b['id']]);s.tick();self.assertEqual(rw.current(self.p)['revision'],1);self.assertEqual(s.summary('sample')['counts']['needs_attention'],1)
 def test_ai_kept_separate(self):
  c=self.agent(field='findings',value='可以探索远程取样',content_nature='ai_hypothesis',conditions='需重新识别介质',limitations='未经企业验证');s=self.steward();s.enqueue_candidates('sample',[c['id']]);s.tick();d=rw.dataset(self.p);self.assertEqual(d['records'],[]);self.assertEqual(len(d['interpretations']),1)
 def test_stale_evidence_rejected(self):
  c=self.agent();x=pp.state(self.p)['sources'][self.sid];blocks=pp.load(self.p/x['chunks']);blocks[0]['text']+='new';pp.save(self.p/x['chunks'],blocks);s=self.steward();s.enqueue_candidates('sample',[c['id']]);s.tick();self.assertEqual(rw.current(self.p)['revision'],0);self.assertEqual(s.summary('sample')['counts']['needs_attention'],1)
 def test_persisted_pause_and_expired_lease_resume(self):
  s=self.steward();t=s.enqueue_source('sample',self.sid);s.pause(True);self.assertIsNone(s.claim());s=Steward(self.lib,self.inbox);self.assertTrue(s.summary('sample')['paused']);s.pause(False);self.assertEqual(s.claim()['id'],t['id'])
  with s.connect()as db:db.execute('UPDATE tasks SET lease=?',(time.time()-1,))
  s=Steward(self.lib,self.inbox);self.assertTrue(s.tick());self.assertEqual(rw.current(self.p)['revision'],1)
 def test_bounded_retry(self):
  s=self.steward();s.enqueue_source('sample',self.sid)
  with patch.object(rw,'process',side_effect=OSError('暂时不可读')):
   for _ in range(3):
    self.assertTrue(s.tick())
    with s.connect()as db:db.execute('UPDATE tasks SET due=0')
  self.assertEqual(s.summary('sample')['counts']['failed'],1);self.assertFalse(s.tick())
 def test_job_project_scope_and_rejected_candidate(self):
  c=self.agent();rw.review(self.lib,'sample',c['id'],'rejected','人','不采用');s=self.steward();s.enqueue_candidates('sample',[c['id']]);s.tick();self.assertEqual(rw.current(self.p)['revision'],0)
  with self.assertRaises(ValueError):s.summary('../sample')
 def test_automatic_review_cannot_overwrite_human_rejection(self):
  c=self.agent();rw.review(self.lib,'sample',c['id'],'rejected','人','不采用')
  with self.assertRaises(ValueError):rw.review(self.lib,'sample',c['id'],'approved','管家','检查',reviewer_kind='agent',expected_status='pending')
 def test_agent_submit_is_all_or_nothing(self):
  c=self.candidate();valid={k:c[k]for k in ['entity','record_id','title','field','value','source_id','chunk_id','quote']}
  invalid=dict(valid,field='not_a_field');s=self.steward();before=len(rw.current(self.p)['candidates'])
  with self.assertRaises(ValueError):s.submit_bundle('sample',dict(project_id='sample',candidates=[valid,invalid]),'Agent')
  self.assertEqual(len(rw.current(self.p)['candidates']),before)
  t=s.submit_bundle('sample',dict(project_id='sample',candidates=[valid]),'Agent');s.tick();self.assertEqual(rw.current(self.p)['revision'],1)
 def test_unknown_candidate_is_rejected(self):
  with self.assertRaises(ValueError):self.steward().enqueue_candidates('sample',['CAND-not-found'])
 def test_multiple_fields_of_new_record_publish_together(self):
  a=self.agent();b=self.agent(field='findings',value='满足试验需求',quote='满足试验需求');s=self.steward();s.enqueue_candidates('sample',[a['id'],b['id']]);s.tick();self.assertEqual(rw.current(self.p)['revision'],1);d=rw.dataset(self.p);self.assertEqual(len(d['records']),1);self.assertEqual(rw.cell(d,'A01','findings')['value'],'满足试验需求')
if __name__=='__main__':unittest.main()
