# coding: utf-8
import json,sys,unittest,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'04-知识库/标杆案例/2025-00-嫦娥钻取采样';sys.path.insert(0,str(ROOT/'scripts'))
from dossier_reasoning import read_layer,render
from dossier_governance import capture
class ReasoningTests(unittest.TestCase):
 def test_references_and_epistemic_state(self):
  layer=read_layer(P);self.assertEqual(len(layer['items']),4)
  for item in layer['items']:
   self.assertEqual(item['content_type'],'ai_hypothesis');self.assertEqual(item['validation_status'],'not_validated');self.assertIsNone(item['confidence'])
   self.assertEqual([s['type']for s in item['reasoning_chain']],['source_basis','analogy','hypothesis'])
   for key in ['conditions','boundaries','validation_plan']:self.assertTrue(item[key])
 def test_bad_references_and_fake_confidence_rejected(self):
  (ROOT/'tmp').mkdir(exist_ok=True)
  with tempfile.TemporaryDirectory(dir=str(ROOT/'tmp'))as folder:
   p=Path(folder);(p/'版本').symlink_to(P/'版本',target_is_directory=True);data=json.loads((P/'AI推演.json').read_text())
   data['items'][0]['claim_ids']=['C_DOES_NOT_EXIST'];(p/'AI推演.json').write_text(json.dumps(data))
   with self.assertRaises(AssertionError):read_layer(p)
   data=json.loads((P/'AI推演.json').read_text());data['items'][0]['confidence']=.99;(p/'AI推演.json').write_text(json.dumps(data))
   with self.assertRaises(AssertionError):read_layer(p)
 def test_ai_addition_does_not_fill_facts_or_raise_quality(self):
  old=json.loads((P/'版本/0.4.2/snapshot.json').read_text());current=capture(P)
  for key in old.keys()-{'version_declaration'}:self.assertEqual(old[key],current[key],key)
  self.assertEqual(current['quality']['score'],55);self.assertEqual(current['atomic']['counts'],old['atomic']['counts'])
  self.assertEqual(current['ai_reasoning']['basis_archive']['content_version'],'0.4.2')
 def test_every_card_is_labeled_and_counts_are_separate(self):
  result=render(P);self.assertEqual(result['count'],4);self.assertEqual(result['body'].count('class="ai-label">AI推演'),4)
  self.assertIn('aria-controls="reasoning-cards"',result['body']);self.assertIn('data-count="4"',result['body'])
  html=(P/'档案.html').read_text();self.assertIn('不增加事实字段填充率或质量自评',html)
if __name__=='__main__':unittest.main()
