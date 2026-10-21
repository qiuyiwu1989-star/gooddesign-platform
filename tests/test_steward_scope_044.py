# coding: utf-8
import json,sys,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import test_research_pipeline_038 as base
import project_pipeline as pp,research_workflow as rw,steward_scope as scope
from archive_steward import Steward
class ScopeTests(unittest.TestCase):
 setUp=base.ResearchTests.setUp
 tearDown=base.ResearchTests.tearDown
 def steward(self):return Steward(self.lib,self.inbox)
 def assign(self,state):pp.save(self.p/'资料归属.json',dict(version=1,assignments={self.sid:dict(scope=state,reason='测试归属变更')},url_rules={}))
 def row(self,s,tid):
  with s.connect()as db:return dict(db.execute('SELECT * FROM tasks WHERE id=?',(tid,)).fetchone())
 def test_hold_restore_pending_keeps_identity_and_audits(self):
  s=self.steward();t=s.enqueue_source('sample',self.sid);self.assign('shared');self.assertEqual(len(scope.reconcile(s,'sample')),1);self.assertEqual(self.row(s,t['id'])['status'],'scope_hold');self.assertFalse(s.tick())
  self.assign('project');scope.reconcile(s,'sample');r=self.row(s,t['id']);self.assertEqual(r['status'],'queued');self.assertEqual(r['key'],t['key']);self.assertEqual(r['attempts'],0)
  with s.connect()as db:self.assertEqual([r[0]for r in db.execute('SELECT action FROM controls ORDER BY id')],['scope_hold','scope_restore'])
 def test_claim_time_scope_check_never_processes_wrong_source(self):
  s=self.steward();t=s.enqueue_source('sample',self.sid);self.assign('pending')
  with patch.object(rw,'process')as process:self.assertTrue(s.tick());process.assert_not_called()
  self.assertEqual(self.row(s,t['id'])['status'],'scope_hold');self.assign('project');scope.reconcile(s,'sample');self.assertEqual(self.row(s,t['id'])['attempts'],0)
 def test_restore_awaiting_reading_does_not_mark_completed(self):
  s=self.steward();t=s.enqueue_source('sample',self.sid)
  with s.connect()as db:db.execute("UPDATE tasks SET status='awaiting_agent',result=?,attempts=1 WHERE id=?",(json.dumps(dict(note='still needs figures')),t['id']))
  self.assign('reassigned');scope.reconcile(s,'sample');self.assign('project');scope.reconcile(s,'sample');r=self.row(s,t['id']);self.assertEqual(r['status'],'awaiting_agent');self.assertEqual(json.loads(r['result'])['note'],'still needs figures');self.assertEqual(r['attempts'],1)
 def test_conflict_and_error_state_survive_roundtrip(self):
  s=self.steward();t=s.enqueue_source('sample',self.sid)
  with s.connect()as db:db.execute("UPDATE tasks SET status='needs_attention',error='original error',result=?,attempts=2 WHERE id=?",(json.dumps(dict(exceptions=['keep conflict'])),t['id']))
  self.assign('shared');scope.reconcile(s,'sample');self.assign('project');scope.reconcile(s,'sample');r=self.row(s,t['id']);self.assertEqual((r['status'],r['attempts'],r['error']),('needs_attention',2,'original error'));self.assertEqual(json.loads(r['result'])['exceptions'],['keep conflict'])
 def test_does_not_replay_completed_or_steal_running_work(self):
  s=self.steward();t=s.enqueue_source('sample',self.sid);self.assign('shared')
  for status in ['completed','running']:
   with s.connect()as db:db.execute('UPDATE tasks SET status=? WHERE id=?',(status,t['id']))
   self.assertEqual(scope.reconcile(s,'sample'),[]);self.assertEqual(self.row(s,t['id'])['status'],status)
 def test_public_url_rule_holds_fetch_without_network(self):
  s=self.steward()
  with patch.object(pp,'public_url'):t=s.enqueue_fetch('sample','https://example.org/a')
  pp.save(self.p/'资料归属.json',dict(version=1,assignments={},url_rules={'https://example.org/a':dict(scope='shared',reason='公共参考')}))
  with patch.object(pp,'fetch')as fetch:self.assertTrue(s.tick());fetch.assert_not_called()
  self.assertEqual(self.row(s,t['id'])['status'],'scope_hold')
 def test_summary_links_same_document_without_marking_read(self):
  second=self.root/'second.txt';second.write_text('second format text');sid2=pp.ingest(self.p,second)['source_id'];index=self.p/'论文原文管理/论文原件清单.json';listing=pp.load(index);listing['items'][0]['related_source_ids']=[sid2];pp.save(index,listing)
  s=self.steward();t=s.enqueue_source('sample',self.sid);before=self.row(s,t['id']);summary=s.summary('sample');r=summary['recent'][0];self.assertEqual(r['document_context']['document_id'],'A01');self.assertEqual(len(r['document_context']['related_source_ids']),2);self.assertIn('格式分别保留',r['document_context']['reading_note']);self.assertEqual(before,self.row(s,t['id']))
if __name__=='__main__':unittest.main()
