# coding: utf-8
import copy,sys,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import test_research_pipeline_038 as base
import project_pipeline as pp,research_workflow as rw,research_reader_notes as rn,workspace_ui,archive_mcp
class NotesTests(unittest.TestCase):
 setUp=base.ResearchTests.setUp
 tearDown=base.ResearchTests.tearDown
 candidate=base.ResearchTests.candidate
 approve=base.ResearchTests.approve
 def payload(self):
  c=self.candidate();self.approve(c);rw.publish(self.lib,'sample','测试','研究首版');vf,_=rw.check_version(self.p,'research-000001')
  return dict(schema=rn.SCHEMA,project_id='sample',version='0.1.0',research_revision='research-000001',dataset_sha256=pp.sha((vf/'档案.json').read_bytes()),content_nature='ai_reading_guide',overview='AI导读 <script>invalid()</script>',modules=[dict(module_id=i,summary='模块导读',record_ids=['A01']if i==5 else[],gaps=['仍需专业复核'])for i in range(1,9)])
 def test_freeze_is_idempotent_and_not_fact_or_score_change(self):
  payload=self.payload();before=rw.dataset(self.p);a=rn.freeze(self.lib,'sample',payload,'Agent');b=rn.freeze(self.lib,'sample',payload,'Agent');self.assertEqual(a,b);self.assertEqual(before,rw.dataset(self.p));self.assertFalse(a['manifest']['expert_reviewed']);self.assertFalse(a['manifest']['quality_score_changed'])
  changed=copy.deepcopy(payload);changed['overview']='改写旧版'
  with self.assertRaises(ValueError):rn.freeze(self.lib,'sample',changed,'Agent')
 def test_missing_and_cross_module_reference_rejected(self):
  payload=self.payload();payload['modules'][4]['record_ids']=['missing']
  with self.assertRaises(ValueError):rn.freeze(self.lib,'sample',payload,'Agent')
  payload['modules'][4]['record_ids']=[];payload['modules'][0]['record_ids']=['A01']
  with self.assertRaises(ValueError):rn.freeze(self.lib,'sample',payload,'Agent')
 def test_stale_dataset_and_wrong_project_rejected(self):
  payload=self.payload();payload['dataset_sha256']='wrong'
  with self.assertRaises(ValueError):rn.freeze(self.lib,'sample',payload,'Agent')
  payload['project_id']='other'
  with self.assertRaises(ValueError):rn.freeze(self.lib,'sample',payload,'Agent')
 def test_tamper_fails_closed_but_dossier_still_readable(self):
  payload=self.payload();rn.freeze(self.lib,'sample',payload,'Agent');path=rn.folder(self.p,'research-000001')/'0.1.0/导读.json';path.write_text('tampered');self.assertEqual(rn.safe_read(self.p,'research-000001')['status'],'invalid');self.assertIn('10.1234/test.2026',workspace_ui.dossier('sample',self.lib))
 def test_new_publication_does_not_reuse_older_guide(self):
  payload=self.payload();rn.freeze(self.lib,'sample',payload,'Agent');c=self.candidate(field='findings',value='满足试验需求',quote='满足试验需求');self.approve(c);rw.publish(self.lib,'sample','测试','新研究')
  self.assertEqual(rn.read(self.p,'research-000002')['status'],'not_available');self.assertEqual(rn.read(self.p,'research-000001')['status'],'available');self.assertNotIn('AI阅读导读 0.1.0',workspace_ui.dossier('sample',self.lib))
  with patch.object(archive_mcp,'LIB',self.lib):
   self.assertEqual(archive_mcp.gd_project_overview('sample')['reading_guide']['status'],'not_available')
   self.assertEqual(archive_mcp.gd_project_overview('sample',revision='research-000001')['reading_guide']['status'],'available')
 def test_render_and_mcp_keep_ai_tag_and_bound_revision(self):
  payload=self.payload();rn.freeze(self.lib,'sample',payload,'Agent');html=workspace_ui.dossier('sample',self.lib);self.assertIn('&lt;script&gt;invalid()&lt;/script&gt;',html);self.assertEqual(html.count('class="research-guide"'),8);self.assertIn('id="record-A01"',html)
  with patch.object(archive_mcp,'LIB',self.lib):out=archive_mcp.gd_project_overview('sample')
  self.assertEqual(out['reading_guide']['notes']['research_revision'],out['publication_revision']);self.assertFalse(out['expert_reviewed']);self.assertIn('未评',out['quality'])
 def test_interrupted_write_leaves_no_published_partial_version(self):
  payload=self.payload();save=pp.save
  def fail(path,value):
   if Path(path).name=='manifest.json':raise OSError('模拟中断')
   return save(path,value)
  with patch.object(pp,'save',side_effect=fail):
   with self.assertRaises(OSError):rn.freeze(self.lib,'sample',payload,'Agent')
  self.assertEqual(rn.read(self.p,'research-000001')['status'],'not_available');self.assertEqual(rn.freeze(self.lib,'sample',payload,'Agent')['status'],'available')
 def test_malformed_modules_rejected_before_write(self):
  payload=self.payload()
  for bad in [[],[None]*8,[dict(module_id=True)]*8]:
   data=dict(payload,modules=bad)
   with self.assertRaises(ValueError):rn.freeze(self.lib,'sample',data,'Agent')
 def test_http_download_uses_frozen_markdown_and_rejects_path_escape(self):
  import threading,urllib.request,urllib.error,file_admin
  rn.freeze(self.lib,'sample',self.payload(),'Agent');srv=file_admin.server(self.lib,self.inbox,0);thread=threading.Thread(target=srv.serve_forever,daemon=True);thread.start()
  try:
   url='http://127.0.0.1:'+str(srv.server_port)+'/api/research-document?project=sample&document=guide&revision=research-000001&guide_version='
   with urllib.request.urlopen(url+'0.1.0')as response:self.assertEqual(response.read(),(rn.folder(self.p,'research-000001')/'0.1.0/导读.md').read_bytes())
   with self.assertRaises(urllib.error.HTTPError)as error:urllib.request.urlopen(url+'../../private')
   self.assertEqual(error.exception.code,400)
  finally:srv.shutdown();srv.server_close();srv.store.pool.shutdown(wait=True);srv.store.steward.close();thread.join()
if __name__=='__main__':unittest.main()
