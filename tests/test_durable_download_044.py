# coding: utf-8
import json,sys,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import test_file_admin_033 as base
import project_pipeline as pp,file_admin as fa
class DownloadTests(unittest.TestCase):
 setUp=base.FileAdminTests.setUp
 tearDown=base.FileAdminTests.tearDown
 request=base.FileAdminTests.request
 def fetch(self):
  with patch.object(pp,'public_url'):
   status,data,_=self.request('/api/fetch?project=demo-01',json.dumps(dict(url='https://example.org/article')).encode())
  self.assertEqual(status,202);return data
 def test_api_download_is_durable_deduplicated_and_restartable(self):
  a=self.fetch();self.assertTrue(a['durable']);self.assertEqual(a['id'],self.fetch()['id']);self.assertEqual(self.srv.store.jobs,[])
  old=self.srv.store;old.pool.shutdown(wait=True);self.srv.store=fa.Store(self.lib,self.inbox)
  self.assertEqual(self.request('/api/jobs?project=demo-01')[1]['jobs'][0]['id'],a['id'])
  path=self.root/'paper.txt';path.write_text('actual saved original',encoding='utf-8');x=pp.ingest(self.lib/'demo-01',path)
  with patch.object(pp,'fetch',return_value=dict(status='duplicate',source_id=x['source_id']))as fetch:
   self.srv.store.steward.tick();self.assertEqual(fetch.call_count,1)
  job=self.request('/api/jobs?project=demo-01')[1]['jobs'][0];self.assertEqual(job['status'],'completed');self.assertEqual(job['result']['source_id'],x['source_id']);self.assertIn('steward_task_id',job['result'])
 def test_api_failure_waits_then_explicit_retry_preserves_identity(self):
  a=self.fetch();s=self.srv.store.steward
  with patch.object(pp,'fetch',side_effect=OSError('下载中断')):
   for _ in range(3):
    self.assertTrue(s.tick())
    with s.connect()as db:db.execute('UPDATE tasks SET due=0')
  job=self.request('/api/jobs?project=demo-01')[1]['jobs'][0];self.assertEqual(job['status'],'failed');self.assertEqual(job['attempts'],3)
  _,new,_=self.request('/api/retry?project=demo-01',json.dumps(dict(job_id=a['id'])).encode());self.assertEqual(new['id'],a['id']);self.assertEqual(new['attempts'],0)
  self.assertEqual(self.request('/api/retry?project=demo-01',json.dumps(dict(job_id=a['id'])).encode())[0],400)
 def test_retry_does_not_accept_other_kinds_or_projects(self):
  s=self.srv.store.steward;t=s.enqueue('demo-01',dict(kind='source',source_id='dummy'))
  with s.connect()as db:db.execute("UPDATE tasks SET status='failed' WHERE id=?",(t['id'],))
  self.assertEqual(self.request('/api/retry?project=demo-01',json.dumps(dict(job_id='steward-'+str(t['id']))).encode())[0],400)
  with s.connect()as db:self.assertEqual(db.execute('SELECT status FROM tasks WHERE id=?',(t['id'],)).fetchone()[0],'failed')
  a=self.fetch()
  with s.connect()as db:db.execute("UPDATE tasks SET project='other',status='failed' WHERE id=?",(int(a['id'].split('-')[1]),))
  self.assertEqual(self.request('/api/retry?project=demo-01',json.dumps(dict(job_id=a['id'])).encode())[0],400)
 def test_existing_legacy_jobs_still_visible_without_replaying(self):
  self.srv.store.jobs=[dict(id='legacy',project_id='demo-01',kind='fetch',args=dict(url='https://example.org/old'),status='interrupted',created_at=pp.now(),error='历史中断',result=None)]
  a=self.fetch();rows=self.request('/api/jobs?project=demo-01')[1]['jobs'];self.assertEqual({j['id']for j in rows},{a['id'],'legacy'});self.assertEqual(self.srv.store.jobs[0]['status'],'interrupted')
 def test_old_duplicate_can_be_retrieved_beyond_recent_window(self):
  a=self.fetch();s=self.srv.store.steward
  for n in range(102):s.enqueue('demo-01',dict(kind='fetch',url='https://example.org/'+str(n)))
  self.assertEqual(self.fetch()['id'],a['id']);self.assertEqual(len(s.fetch_jobs('demo-01')),100)
 def test_fetch_identity_ignores_title_and_processor_upgrade(self):
  s=self.srv.store.steward
  with patch.object(pp,'public_url'):
   a=s.enqueue_fetch('demo-01','https://example.org/same','旧标题')
   with patch('archive_steward.VERSION','future-processor'):
    b=s.enqueue_fetch('demo-01','https://example.org/same','新标题')
  self.assertEqual(a['id'],b['id'])
if __name__=='__main__':unittest.main()
