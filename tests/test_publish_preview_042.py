# coding: utf-8
"""Publication must match the set of items the user explicitly previewed."""
import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
import test_research_pipeline_038 as base
rw=base.rw
class PreviewTests(unittest.TestCase):
 setUp=base.ResearchTests.setUp
 tearDown=base.ResearchTests.tearDown
 candidate=base.ResearchTests.candidate
 approve=base.ResearchTests.approve
 def test_exact_preview_publishes(self):
  c=self.candidate();self.approve(c);r=rw.publish(self.lib,'sample','核对员','预览后保存',[c['id']]);self.assertEqual(r['changes'],1);self.assertFalse(rw.dataset(self.p)['expert_reviewed'])
 def test_added_approved_item_invalidates_preview(self):
  c=self.candidate();self.approve(c);other=self.candidate(record_id='A02');self.approve(other)
  with self.assertRaisesRegex(ValueError,'重新预览'):rw.publish(self.lib,'sample','核对员','旧预览',[c['id']])
  self.assertEqual(rw.current(self.p)['revision'],0);self.assertEqual(len(rw.dataset(self.p)['records']),0)
 def test_removed_approved_item_invalidates_preview(self):
  c=self.candidate();self.approve(c);rw.review(self.lib,'sample',c['id'],'needs_more','核对员','补资料')
  with self.assertRaisesRegex(ValueError,'重新预览'):rw.publish(self.lib,'sample','核对员','旧预览',[c['id']])
 def test_malformed_or_duplicate_preview_rejected(self):
  c=self.candidate();self.approve(c)
  for ids in [c['id'],[c['id'],c['id']],[1],[]]:
   with self.subTest(ids=ids),self.assertRaises(ValueError):rw.publish(self.lib,'sample','核对员','错误预览',ids)
  self.assertEqual(rw.current(self.p)['revision'],0)
if __name__=='__main__':unittest.main()
