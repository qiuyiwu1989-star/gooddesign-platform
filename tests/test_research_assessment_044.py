# coding: utf-8
import copy,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import test_research_pipeline_038 as base
import project_pipeline as pp,research_workflow as rw,research_assessment as ra,archive_mcp,workspace_ui
import build_research_handoff as export
from research_handoff_check import check
class AssessmentTests(unittest.TestCase):
 setUp=base.ResearchTests.setUp
 tearDown=base.ResearchTests.tearDown
 candidate=base.ResearchTests.candidate
 approve=base.ResearchTests.approve
 def payload(self):
  c=self.candidate();self.approve(c);rw.publish(self.lib,'sample','tester','首版');vf,_=rw.check_version(self.p,'research-000001')
  return dict(schema=ra.SCHEMA,project_id='sample',version='0.1.0',research_revision='research-000001',dataset_sha256=pp.sha((vf/'档案.json').read_bytes()),content_nature='ai_research_review',summary='研究仍需补证 <script>unsafe()</script>',dimensions=[dict(key=k,stage='partial',basis='已有部分原文',record_ids=['A01'],gaps=['原始试验记录未取得'])for k,_ in ra.DIMENSIONS],priorities=[dict(priority='P0',title='核对原件',why='确保来源可追溯',next_step='查找原始试验报告',record_ids=['A01'])])
 def test_freeze_idempotent_not_score_or_facts(self):
  a=self.payload();before=rw.dataset(self.p);r=ra.freeze(self.lib,'sample',a,'Agent');self.assertEqual(r,ra.freeze(self.lib,'sample',a,'Agent'));self.assertEqual(before,rw.dataset(self.p));report=r['report'];self.assertEqual(report['evidence_audit']['traceable_known_cells'],1);self.assertIsNone(report['quality_score']);self.assertFalse(report['expert_reviewed']);self.assertFalse(report['full_research_complete'])
  a['summary']='改写'
  with self.assertRaises(ValueError):ra.freeze(self.lib,'sample',a,'Agent')
 def test_identity_binding_and_references(self):
  a=self.payload()
  for change in [dict(project_id='wrong'),dict(dataset_sha256='bad'),dict(content_nature='source_statement')]:
   b=copy.deepcopy(a);b.update(change)
   with self.assertRaises(ValueError):ra.freeze(self.lib,'sample',b,'Agent')
  a['dimensions'][0]['record_ids']=['missing']
  with self.assertRaises(ValueError):ra.freeze(self.lib,'sample',a,'Agent')
 def test_frozen_evidence_and_current_scope_are_checked(self):
  self.payload();d=rw.dataset(self.p);self.assertEqual(ra.audit(self.p,d)['status'],'traceable');pp.save(self.p/'资料归属.json',dict(version=1,assignments={self.sid:dict(scope='shared')},url_rules={}));a=ra.audit(self.p,d);self.assertEqual(a['status'],'attention');self.assertEqual(a['traceable_known_cells'],0)
  pp.save(self.p/'资料归属.json',dict(version=2,assignments={},url_rules={}));x=pp.state(self.p)['sources'][self.sid];(self.p/x['chunks']).write_text('[]');self.assertEqual(ra.audit(self.p,d)['status'],'attention')
 def test_ai_boundary_missing_and_missing_fact_evidence(self):
  self.payload();d=rw.dataset(self.p);c=d['records'][0]['cells']['doi'];d['interpretations']=[dict(c['evidence'],record_id='AI',field='mechanism',content_nature='ai_interpretation',conditions='',limitations='缺少限制')];self.assertEqual(ra.audit(self.p,d)['traceable_bounded_ai_items'],0)
  c.pop('evidence');self.assertEqual(ra.audit(self.p,d)['traceable_known_cells'],0)
 def test_tamper_and_new_version_do_not_silently_reuse(self):
  a=self.payload();ra.freeze(self.lib,'sample',a,'Agent');f=ra.folder(self.p,'research-000001')/'0.1.0/评估.json';before=f.read_bytes();f.write_text('{}');self.assertEqual(ra.safe_read(self.p,'research-000001')['status'],'invalid');f.write_bytes(before)
  c=self.candidate(field='findings',value='满足试验需求',quote='满足试验需求');self.approve(c);rw.publish(self.lib,'sample','tester','新版');self.assertEqual(ra.safe_read(self.p,'research-000002')['status'],'not_available');self.assertEqual(ra.read(self.p,'research-000001')['status'],'available')
 def test_render_escape_and_mcp_fixed_version(self):
  a=self.payload();ra.freeze(self.lib,'sample',a,'Agent');html=workspace_ui.dossier('sample',self.lib);self.assertIn('&lt;script&gt;unsafe()&lt;/script&gt;',html);self.assertIn('AI研究评估',html);self.assertIn('data-review-record="A01"',html)
  with patch.object(archive_mcp,'LIB',self.lib):
   short=archive_mcp.gd_project_overview('sample','research-000001')['research_assessment'];full=archive_mcp.gd_project_overview('sample','research-000001',review_detail=True)['research_assessment'];self.assertEqual(short['status'],'available');self.assertEqual(short['detail_level'],'summary');self.assertNotIn('basis',short['report']['judgment']['dimensions'][0]);self.assertIn('basis',full['report']['judgment']['dimensions'][0]);self.assertLess(len(json.dumps(short)),len(json.dumps(full)))
 def test_current_damage_surfaces_but_frozen_review_not_rewritten(self):
  a=self.payload();ra.freeze(self.lib,'sample',a,'Agent');f=ra.folder(self.p,'research-000001')/'0.1.0/评估.json';before=f.read_bytes();x=pp.state(self.p)['sources'][self.sid];(self.p/x['original']).write_text('damaged');r=ra.safe_read(self.p,'research-000001');self.assertEqual(r['status'],'available');self.assertEqual(r['current_evidence_audit']['status'],'attention');self.assertEqual(r['report']['evidence_audit']['status'],'traceable');self.assertEqual(f.read_bytes(),before)
 def test_interrupted_freeze_does_not_publish_partial(self):
  a=self.payload();save=pp.save
  def broken(path,value):
   if path.name=='manifest.json':raise OSError('中断')
   return save(path,value)
  with patch.object(pp,'save',side_effect=broken):
   with self.assertRaises(OSError):ra.freeze(self.lib,'sample',a,'Agent')
  self.assertEqual(ra.read(self.p,'research-000001')['status'],'not_available');self.assertEqual(ra.freeze(self.lib,'sample',a,'Agent')['status'],'available')
 def test_http_frozen_review_download_and_path_rejection(self):
  import threading,urllib.request,urllib.error,file_admin
  a=self.payload();ra.freeze(self.lib,'sample',a,'Agent');srv=file_admin.server(self.lib,self.inbox,0);thread=threading.Thread(target=srv.serve_forever,daemon=True);thread.start()
  try:
   url='http://127.0.0.1:'+str(srv.server_port)+'/api/research-document?project=sample&document=review&revision=research-000001&review_version='
   with urllib.request.urlopen(url+'0.1.0')as response:self.assertEqual(response.read(),(ra.folder(self.p,'research-000001')/'0.1.0/评估.md').read_bytes())
   with self.assertRaises(urllib.error.HTTPError)as error:urllib.request.urlopen(url+'../../private')
   self.assertEqual(error.exception.code,400)
  finally:srv.shutdown();srv.server_close();srv.store.pool.shutdown(wait=True);srv.store.steward.close();thread.join()
 def test_export_includes_bound_review_and_still_checks(self):
  a=self.payload();ra.freeze(self.lib,'sample',a,'Agent');result=export.build(self.lib,'sample',self.root/'out');p=Path(result['folder']);self.assertTrue((p/'研究评估/评估.md').exists());self.assertEqual(pp.load(p/'交付概览.json')['review_version'],'0.1.0');self.assertEqual(check(p)['records'],1)
if __name__=='__main__':unittest.main()
