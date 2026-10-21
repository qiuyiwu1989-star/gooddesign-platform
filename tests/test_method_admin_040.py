# coding: utf-8
import json,sys,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
import test_file_admin_033 as base
class MethodAdminTests(base.FileAdminTests):
 def test_methods_page_assets_and_read_api(self):
  code,d,_=self.request('/api/methods?query=TRIZ');self.assertEqual(code,200);self.assertEqual(d['total'],1)
  code,d,_=self.request('/api/method?method_id=IM-FA-001&level=steps');self.assertEqual(len(d['data']),5)
  code,html,headers=self.request('/methods/');self.assertEqual(code,200);self.assertIn('企业建议'.encode(),html);self.assertIn('模拟企业需求'.encode(),html);self.assertIn('script-src',headers['Content-Security-Policy'])
  self.assertEqual(self.request('/methods/style.css')[0],200);self.assertEqual(self.request('/methods/app.js')[0],200)
  self.assertEqual(self.request('/api/innovation-run?section=overview')[1]['task']['scenario_type'],'simulated')
 def test_supported_replay_job_is_separate_from_source_archive(self):
  from types import SimpleNamespace
  import project_pipeline as pp
  cat=self.root/'case-catalog.json';pp.save(cat,dict(projects=[dict(id='2025-00',name='隔离嫦娥模拟项目')]))
  pp.bootstrap(self.lib,self.inbox,cat,self.root/'empty-archive')
  fake=SimpleNamespace(returncode=0,stdout=json.dumps(dict(status='completed',run_id='RUN-20261021T000000-abcdef')),stderr='')
  with patch.object(base.fa.subprocess,'run',return_value=fake)as command:
   code,j,_=self.request('/api/method-demo?project=2025-00',json.dumps(dict(actor='隔离测试重放')).encode());self.assertEqual(code,202);done=self.wait(j);self.assertEqual(done['status'],'completed');self.assertEqual(done['result']['run_id'],'RUN-20261021T000000-abcdef');self.assertEqual(len(pp.state(self.lib/'2025-00')['sources']),0);command.assert_called_once()
 def test_paths_and_demo_write_guard(self):
  self.assertEqual(self.request('/api/method?method_id=../../bad')[0],400);self.assertEqual(self.request('/methods/../../bad')[0],400)
  self.assertEqual(self.request('/api/innovation-run?run=../../secret')[0],400)
  self.assertEqual(self.request('/api/method-demo?project=demo-01',b'{}')[0],400)
  self.assertEqual(self.request('/api/method-demo?project=demo-01',b'{}',headers={'X-CSRF-Token':'bad'})[0],403)
