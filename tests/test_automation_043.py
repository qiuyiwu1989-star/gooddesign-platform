# coding: utf-8
"""043 reports live intake status, without claiming or running a semantic agent."""
import sys,time,unittest
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(ROOT/'tests'))
import test_file_admin_033 as base
import project_pipeline as pp
class AutomationTests(unittest.TestCase):
 setUp=base.FileAdminTests.setUp
 tearDown=base.FileAdminTests.tearDown
 request=base.FileAdminTests.request
 def read(self):
  status,data,_=self.request('/api/automation?project=demo-01');self.assertEqual(status,200);return data
 def test_historical_heartbeat_does_not_mean_running(self):
  pp.save(self.lib/'监听状态.json',dict(heartbeat=pp.now()))
  d=self.read();self.assertEqual(d['state'],'stopped');self.assertFalse(d['semantic_agent_connected']);self.assertTrue(d['automatic_publication']);self.assertFalse(d['steward']['embedded_model_connected'])
 def test_live_states(self):
  store=self.srv.store;store.watch_thread=SimpleNamespace(is_alive=lambda:True)
  self.assertEqual(self.read()['state'],'starting')
  store.watch_last_success=time.time();self.assertEqual(self.read()['state'],'running')
  store.watch_last_success=time.time()-40;self.assertEqual(self.read()['state'],'delayed')
  store.watch_error='private file path';d=self.read();self.assertEqual(d['state'],'error');self.assertNotIn('private file path',str(d))
 def test_counts_are_project_scoped_and_readonly(self):
  store=self.srv.store
  store.jobs=[dict(project_id=pid,status=state)for pid,state in [('demo-01','running'),('demo-01','queued'),('demo-01','failed'),('other','failed'),('other','queued')]]
  before=list(store.jobs);d=self.read();self.assertEqual((d['running'],d['queued'],d['attention_records']),(1,1,1));self.assertEqual(store.jobs,before)
 def test_unknown_project_and_path_rejected(self):
  for pid in ['missing','../demo-01']:self.assertEqual(self.request('/api/automation?project='+pid)[0],400)
 def test_ui_explains_capability_boundary(self):
  html=self.request('/')[1].decode();self.assertIn('自动整理状态',html);self.assertIn('后台尚未接入独立推理模型',html);self.assertIn('id="wf-extract"',html)
if __name__=='__main__':unittest.main()
