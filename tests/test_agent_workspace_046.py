import sys,json,unittest,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import test_file_admin_033 as admin
from unittest.mock import patch
class WorkspaceTests(unittest.TestCase):
 setUp=admin.FileAdminTests.setUp
 tearDown=admin.FileAdminTests.tearDown
 request=admin.FileAdminTests.request
 def test_semantic_controls_and_guard(self):
  status,d,_=self.request('/api/semantic?project=demo-01');self.assertEqual(status,200);self.assertEqual(d['jobs'],[])
  status,d,_=self.request('/api/semantic/control?project=demo-01',json.dumps(dict(action='configure',enabled=True,daily_limit=1)).encode());self.assertEqual(status,200);self.assertTrue(d['configuration']['enabled'])
  self.assertEqual(self.request('/api/semantic/control?project=demo-01',b'{"action":"configure","enabled":true,"daily_limit":999}')[0],400)
  self.assertEqual(self.request('/api/semantic/enqueue?project=demo-01',b'{"source_ids":["wrong"]}')[0],400)
  self.assertEqual(self.request('/api/semantic/control?project=demo-01',b'{"action":"pause"}',headers={'X-CSRF-Token':'bad'})[0],403)
 def test_workspace_and_immutable_update_empty(self):
  status,body,headers=self.request('/innovation/?project=demo-01');self.assertEqual(status,200);self.assertIn('nonce-',headers['Content-Security-Policy']);self.assertIn('问题定义',body.decode());self.assertIn('use-model',body.decode());self.assertEqual(self.request('/api/research-updates?project=demo-01')[1]['status'],'not_published')
  status,script,_=self.request('/agent.js');self.assertEqual(status,200);self.assertIn(b'semantic/enqueue',script)
 def test_bad_application_input_rejected(self):
  self.assertEqual(self.request('/api/innovation/create?project=demo-01',b'{"projects":[{}],"request":{}}')[0],400)
  self.assertEqual(self.request('/api/innovation/run?project=demo-01&run=../../secret')[0],400)
 def test_application_failure_does_not_fake_success(self):
  req=dict(task_id='demo',title='测试需求',scenario_type='simulated',needs=['取样'])
  with patch('innovation_application.run_application',side_effect=RuntimeError('模型不可用')):
   status,j,_=self.request('/api/innovation/create?project=demo-01',json.dumps(dict(request=req)).encode());self.assertEqual(status,202)
   for _ in range(40):
    row=next(x for x in self.srv.store.jobs if x['id']==j['id'])
    if row['status']=='failed':break
    time.sleep(.05)
   self.assertEqual(row['status'],'failed');self.assertIn('模型不可用',row['error'])
if __name__=='__main__':unittest.main()
