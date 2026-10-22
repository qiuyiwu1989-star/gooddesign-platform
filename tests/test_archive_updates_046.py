import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import test_research_pipeline_038 as base
import research_workflow as rw,archive_updates as updates
class UpdateTests(unittest.TestCase):
 setUp=base.ResearchTests.setUp
 tearDown=base.ResearchTests.tearDown
 candidate=base.ResearchTests.candidate
 approve=base.ResearchTests.approve
 def test_add_and_ai_separate_without_score(self):
  c=self.candidate();self.approve(c);rw.publish(self.lib,'sample','测试','首版');d=updates.read(self.lib,'sample');self.assertEqual(d['counts'],{'added':1});self.assertFalse(d['quality_score_changed']);self.assertFalse(d['expert_reviewed'])
  ai=self.candidate(field='findings',value='测试假设',content_nature='ai_hypothesis',conditions='待核',limitations='不可直接采用');self.approve(ai);rw.publish(self.lib,'sample','测试','分析');self.assertEqual(updates.read(self.lib,'sample')['counts'],{'ai_added':1})
  self.assertEqual(updates.read(self.lib,'sample','research-000001')['counts'],{'added':1})
 def test_correction_and_withdrawal_are_explicit(self):
  c=self.candidate(value='10.1234/test.202',quote='DOI:10.1234/test.2026');self.approve(c);rw.publish(self.lib,'sample','测试','虚构旧值')
  c=self.candidate();self.approve(c);rw.publish(self.lib,'sample','测试','纠正虚构旧值');self.assertEqual(updates.read(self.lib,'sample')['counts'],{'corrected':1})
  c=self.candidate(operation='clear',value=None,limitations='虚构验收撤回，不代表来源真实性判断');self.approve(c);rw.publish(self.lib,'sample','测试','撤回');self.assertEqual(updates.read(self.lib,'sample')['counts'],{'withdrawn':1});self.assertEqual(updates.read(self.lib,'sample')['changes'][0]['before'],'10.1234/test.2026')
 def test_pending_not_mixed_into_past(self):
  c=self.candidate();self.approve(c);rw.publish(self.lib,'sample','测试','首版');ai=self.candidate(field='findings',value='判断',content_nature='ai_hypothesis',conditions='待核',limitations='待核');self.approve(ai);rw.publish(self.lib,'sample','测试','分析');self.candidate(record_id='A02');self.assertEqual(updates.read(self.lib,'sample')['pending_count'],1);self.assertEqual(updates.read(self.lib,'sample','research-000001')['pending_count'],0)
 def test_escaping_and_input_guards(self):
  c=self.candidate();self.approve(c);rw.publish(self.lib,'sample','测试','首版');text=updates.inject('<section id="assessment-view" hidden></section>',self.lib,'sample');self.assertIn('archive-updates',text);self.assertIn('project=sample',text)
  for rev in ['../../secrets','research-999999']:
   with self.assertRaises((ValueError,FileNotFoundError)):updates.read(self.lib,'sample',rev)
  with self.assertRaises(ValueError):updates.read(self.lib,'sample',limit=100)
if __name__=='__main__':unittest.main()
