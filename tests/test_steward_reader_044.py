# coding: utf-8
import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(ROOT/'tests'))
import test_research_pipeline_038 as base
import workspace_ui,research_workflow as rw
class ReaderTests(unittest.TestCase):
 setUp=base.ResearchTests.setUp
 tearDown=base.ResearchTests.tearDown
 candidate=base.ResearchTests.candidate
 approve=base.ResearchTests.approve
 def test_unpublished_project_preserves_empty_reader(self):
  self.assertIn('还有待整理',workspace_ui.dossier('sample',self.lib))
 def test_eight_modules_all_views_and_sources(self):
  c=self.candidate();self.approve(c);rw.publish(self.lib,'sample','测试员','首版');html=workspace_ui.dossier('sample',self.lib)
  self.assertEqual(html.count('<details class="reader-section reader-module" id="reader-'),8)
  for text in ['资料与解读','档案评估','research-000001','10.1234/test.2026','查看出处与原文','下载保存的原件','质量分：未评'] :self.assertIn(text,html)
  self.assertIn('project=sample',html);self.assertNotIn('project=2025-00',html)
 def test_values_are_escaped_and_ai_not_facts(self):
  c=self.candidate(field='findings',value='<script>bad()</script>',content_nature='ai_hypothesis',conditions='需检查',limitations='未验证');self.approve(c);rw.publish(self.lib,'sample','测试','解读');html=workspace_ui.dossier('sample',self.lib);self.assertIn('&lt;script&gt;bad()&lt;/script&gt;',html);self.assertIn('AI解读 · 未经工程验证',html);self.assertIn('0 个有值字段',html)
if __name__=='__main__':unittest.main()
