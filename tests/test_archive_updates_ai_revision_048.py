import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import test_research_pipeline_038 as base
from test_interpretation_revision_048 import InterpretationRevisionTests as Helpers
import archive_updates as updates

class UpdateLedgerTests(unittest.TestCase):
 setUp=base.ResearchTests.setUp
 tearDown=base.ResearchTests.tearDown
 propose=Helpers.propose
 approve=Helpers.approve
 publish=Helpers.publish
 initial=Helpers.initial
 def test_replacement_label_and_before_after_context_remain_ai(self):
  old=self.initial();new=self.propose('更正后的解释',replaces_interpretation_id=old['id'],conditions='2026来源日期，<script>不执行</script>');self.approve(new);self.publish()
  result=updates.read(self.lib,'sample');row=result['changes'][0]
  self.assertEqual(result['counts'],{'ai_corrected':1});self.assertEqual(row['replaces_interpretation_id'],old['id']);self.assertEqual(row['before'],old['value']);self.assertEqual(row['after_context']['conditions'],new['conditions']);self.assertEqual(row['content_nature'],'ai_interpretation')
  html=updates.render(self.lib,'sample');self.assertIn('修订AI解读',html);self.assertIn('适用前提与限制',html);self.assertNotIn('<script>',html);self.assertIn('&lt;script&gt;',html)
  historical=updates.read(self.lib,'sample',revision='research-000001');self.assertEqual(historical['counts'],{'ai_added':1})
 def test_independent_append_keeps_original_added_classification(self):
  self.initial();new=self.propose('第二个角度');self.approve(new);self.publish();self.assertEqual(updates.read(self.lib,'sample')['counts'],{'ai_added':1})
# Do not collect the imported helper TestCase as a duplicate test suite.
del Helpers
if __name__=='__main__':unittest.main()
