# coding: utf-8
import sys,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import test_file_admin_033 as base
import project_pipeline as pp
from archive_steward import Steward
class ControlTests(unittest.TestCase):
 setUp=base.FileAdminTests.setUp
 tearDown=base.FileAdminTests.tearDown
 request=base.FileAdminTests.request
 wait=base.FileAdminTests.wait
 def post(self,body,**kw):return self.request('/api/steward-control?project=demo-01',json.dumps(body).encode(),**kw)
 def test_pause_persists_and_audits_global_scope(self):
  self.assertEqual(self.post({'action':'pause'})[0],200)
  s=Steward(self.lib,self.inbox);d=s.summary('demo-01');self.assertTrue(d['paused']);self.assertEqual(d['controls'][0]['action'],'pause');self.assertIsNone(d['controls'][0]['project'])
  self.assertEqual(self.post({'action':'resume'})[0],200);self.assertFalse(s.summary('demo-01')['paused']);self.assertEqual(len(s.summary('demo-01')['controls']),2)
 def task(self,status='failed',project='demo-01'):
  s=self.srv.store.steward;t=s.enqueue('demo-01',dict(kind='fetch',url='https://example.org/a'))
  with s.connect()as db:db.execute('UPDATE tasks SET project=?,status=?,attempts=3,error=? WHERE id=?',(project,status,'网络中断',t['id']))
  return t['id']
 def test_retry_retains_previous_failure_and_same_identity(self):
  tid=self.task();self.assertEqual(self.post({'action':'retry','task_id':tid})[0],202)
  s=self.srv.store.steward
  with s.connect()as db:
   task=dict(db.execute('SELECT * FROM tasks WHERE id=?',(tid,)).fetchone());old=json.loads(db.execute("SELECT previous FROM controls WHERE action='retry'").fetchone()[0])
  self.assertEqual((task['status'],task['attempts']),('queued',0));self.assertEqual((old['error'],old['attempts']),('网络中断',3));self.assertEqual(task['key'],old['key'])
  self.assertEqual(self.post({'action':'retry','task_id':tid})[0],400)
 def test_cannot_retry_conflicts_active_or_other_project(self):
  for state in ['running','queued','needs_attention','awaiting_agent','completed']:
   tid=self.task(state);self.assertEqual(self.post({'action':'retry','task_id':tid})[0],400)
  tid=self.task(project='other');self.assertEqual(self.post({'action':'retry','task_id':tid})[0],400)
  for invalid in [True,'1',None,-1]:self.assertEqual(self.post({'action':'retry','task_id':invalid})[0],400)
 def test_control_requires_csrf_and_origin(self):
  for h in [{'X-CSRF-Token':'bad'},{'Origin':'https://evil.example'},{'Host':'evil.example'}]:self.assertEqual(self.post({'action':'pause'},headers=h)[0],403)
  self.assertFalse(self.srv.store.steward.summary('demo-01')['paused'])
  self.assertEqual(self.post({'action':'approve_everything'})[0],400)
 def test_controls_visible_but_no_retry_conflict_button(self):
  html=self.request('/')[1].decode();self.assertIn('steward-toggle',html);self.assertIn('作用于全库',html)
 def test_related_fulltext_is_classified_with_same_paper(self):
  _,j,_=self.request('/api/upload?project=demo-01&name=full.txt',b'full original');sid=self.wait(j)['result']['source_id']
  pp.save(self.lib/'demo-01/论文原文管理/论文原件清单.json',dict(items=[dict(paper_id='A01',title='同一论文',library_source_id='HTML-primary',related_source_ids=[sid],archive_status='full_text_archived')]))
  d=self.request('/api/files?project=demo-01')[1];self.assertEqual(d['files'][0]['kind'],'paper');self.assertEqual(d['files'][0]['paper_id'],'A01');self.assertEqual(d['papers'][0]['archive_status'],'full_text_archived')
if __name__=='__main__':unittest.main()
