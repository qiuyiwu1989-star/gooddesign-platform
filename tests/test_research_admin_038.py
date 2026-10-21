# coding: utf-8
import json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'));sys.path.insert(0,str(ROOT/'scripts'))
from test_file_admin_033 import FileAdminTests
import project_pipeline as pp
class ResearchAdminTests(FileAdminTests):
 def test_api_end_to_end_and_csrf(self):
  text='DOI:10.1234/api.2026\n摘要：针对载荷不稳定的问题，采用双绕组控制，进行样机试验。结果表明，满足试验需求。关键词：电机'
  _,j,_=self.request('/api/upload?project=demo-01&name=paper.txt',text.encode());job=self.wait(j);self.assertEqual(job['status'],'completed');self.assertIn('research',job['result'])
  d=self.request('/api/research?project=demo-01')[1];self.assertGreaterEqual(len(d['candidates']),4);c=next(c for c in d['candidates']if c['field']=='doi')
  data=dict(candidate_id=c['id'],decision='approved',actor='API测试员',reason='已核对原文DOI')
  self.assertEqual(self.request('/api/review?project=demo-01',json.dumps(data).encode(),headers={'X-CSRF-Token':'bad'})[0],403)
  self.assertEqual(self.request('/api/review?project=demo-01',json.dumps(data).encode())[0],200)
  _,j,_=self.request('/api/publish?project=demo-01',json.dumps(dict(actor='API测试员',reason='测试发布')).encode());self.assertEqual(self.wait(j)['status'],'completed')
  response=self.request('/api/research-document?project=demo-01&document=data');self.assertEqual(response[0],200);dataset=json.loads(response[1]);self.assertEqual(dataset['records'][0]['cells']['doi']['value'],'10.1234/api.2026')
  self.assertEqual(self.request('/api/research-document?project=demo-01&document=../../secret')[0],400)
 def test_folder_watch_pipeline_and_restart_cursor(self):
  self.srv.store.start_watch()
  try:
   path=self.inbox/'demo-01/folder-paper.txt';path.write_text('DOI:10.1234/folder.2026');import os;os.utime(path,(time.time()-10,time.time()-10))
   end=time.time()+20
   while time.time()<end:
    data=self.request('/api/research?project=demo-01')[1]
    if data['candidates']:break
    time.sleep(.2)
   self.assertTrue(data['candidates']);self.assertTrue((self.lib/'.file-admin/research-watch.json').exists());self.assertTrue((self.lib/'监听状态.json').exists())
  finally:self.srv.store.watch_stop.set();self.srv.store.watch_thread.join(timeout=10)
