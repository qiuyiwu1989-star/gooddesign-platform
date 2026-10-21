import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import test_research_pipeline_038 as base
import project_pipeline as pp,archive_case_images as images
class ManifestTests(unittest.TestCase):
 setUp=base.ResearchTests.setUp
 tearDown=base.ResearchTests.tearDown
 def test_missing_hash_uses_existing_source_keeps_curated_labels(self):
  old=dict(items=[dict(library_source_id=self.sid,title='人工核对的说明',review_status='selected_visual_read',locations=[dict(page=1)])]);before=pp.state(self.p)['sources'][self.sid];a=images.existing_assets(self.p,old)[before['sha256']];self.assertEqual(a['title'],'人工核对的说明');self.assertEqual(a['review_status'],'selected_visual_read');self.assertEqual(a['original'],before['original']);self.assertNotIn('sha256',old['items'][0])
 def test_wrong_or_unresolvable_identity_is_not_dropped(self):
  for row in [dict(library_source_id='missing'),dict(library_source_id=self.sid,sha256='wrong')]:
   with self.assertRaises(ValueError):images.existing_assets(self.p,dict(items=[row]))
if __name__=='__main__':unittest.main()
