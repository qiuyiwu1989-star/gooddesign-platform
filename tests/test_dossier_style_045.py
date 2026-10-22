# coding: utf-8
import sys,unittest,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import test_research_pipeline_038 as base
import workspace_ui,research_workflow as rw,project_pipeline as pp
from dossier_reader_ui import CSS as STANDARD_CSS
from dossier_layout import KEYS
class StyleTests(unittest.TestCase):
 setUp=base.ResearchTests.setUp
 tearDown=base.ResearchTests.tearDown
 candidate=base.ResearchTests.candidate
 approve=base.ResearchTests.approve
 def test_shared_design_and_pending_project(self):
  text=workspace_ui.dossier('sample',self.lib)
  self.assertIn(STANDARD_CSS,text)
  for key in KEYS:self.assertIn('id="reader-'+key+'"',text)
  for key in ['toc-reader','library-view','assessment-view','view-bar']:self.assertIn('id="'+key+'"',text)
  self.assertIn('暂无登记字段',text);self.assertNotIn('project=2025-00',text)
 def test_render_does_not_change_research_or_raise_quality(self):
  c=self.candidate();self.approve(c);rw.publish(self.lib,'sample','测试','首版');folder,_=rw.check_version(self.p,'research-000001')
  before={f.name:hashlib.sha256(f.read_bytes()).hexdigest()for f in folder.iterdir()if f.is_file()}
  text=workspace_ui.dossier('sample',self.lib)
  self.assertEqual(before,{f.name:hashlib.sha256(f.read_bytes()).hexdigest()for f in folder.iterdir()if f.is_file()})
  for fragment in ['查看出处与原文','data-reader-tab="library"','data-reader-tab="assessment"','id="record-A01"','data-print="true"','质量分：未评','暂无资料']:self.assertIn(fragment,text)
  self.assertIn('10.1234/test.2026',text);self.assertNotIn('软袋',text)
if __name__=='__main__':unittest.main()
