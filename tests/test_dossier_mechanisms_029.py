# coding: utf-8
import json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'04-知识库/标杆案例/2025-00-嫦娥钻取采样';sys.path.insert(0,str(ROOT/'scripts'))
from dossier_mechanisms import read_layer,read_explorations,render
from dossier_governance import capture,verify
class MechanismsTests(unittest.TestCase):
 def test_all_six_mechanisms_grounded(self):
  d=read_layer(P);self.assertEqual(len(d['items']),6)
  self.assertEqual(len(render(P)['body'].split('class="mechanism-unit'))-1,6)
  self.assertIn('S02',d['items'][3]['source_ids'])
 def test_explorations_are_not_verified_applications(self):
  d=read_explorations(P);self.assertEqual(len(d['items']),4)
  for x in d['items']:self.assertIsNone(x['target_project_id']);self.assertEqual(x['validation_evidence'],[])
 def test_rejects_broken_evidence_and_fake_completion(self):
  with tempfile.TemporaryDirectory(dir=str(ROOT/'tmp'))as name:
   p=Path(name);(p/'版本').symlink_to(P/'版本',target_is_directory=True)
   for f in ['机制解读.json','关联探索.json','AI推演.json']:(p/f).write_bytes((P/f).read_bytes())
   f=p/'机制解读.json';d=json.loads(f.read_text());d['items'][0]['source_ids']=['S_FAKE'];f.write_text(json.dumps(d))
   with self.assertRaises(AssertionError):read_layer(p)
   f=p/'关联探索.json';d=json.loads(f.read_text());d['items'][0]['status']='verified';f.write_text(json.dumps(d))
   with self.assertRaises(AssertionError):read_explorations(p)
 def test_facts_and_previous_ai_unchanged(self):
  previous=json.loads((P/'版本/0.5.0/snapshot.json').read_text());current=capture(P)
  for key in previous.keys()-{'version_declaration'}:self.assertEqual(previous[key],current[key],key)
  self.assertEqual(current['quality']['score'],55);verify(P)
 def test_reader_keeps_explorations_folded_and_out_of_hero(self):
  h=(P/'档案.html').read_text();self.assertIn('<details class="exploration-library" id="related-explorations">',h)
  self.assertNotIn('class="hero-graph"',h);self.assertIn('机制结构：6 / 6',h)
  self.assertIn('已验证迁移：0 项',h)
if __name__=='__main__':unittest.main()
