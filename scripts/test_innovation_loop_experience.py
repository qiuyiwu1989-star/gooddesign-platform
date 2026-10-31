import copy
import unittest
from pathlib import Path
from innovation_loop_experience import load_experiences,validate_experience,search_experiences
P=Path(__file__).resolve().parents[1]/'output/innovation-loop-024/experience/experiences-v0.3.0.json'
class ExperienceTests(unittest.TestCase):
 def setUp(self): self.rows=load_experiences(P)
 def test_six_samples_three_projects(self):
  self.assertEqual(len(self.rows),6);self.assertEqual(len({r['evidence_refs'][0]['project_id'] for r in self.rows}),4)
 def test_unknown_requires_reason(self):
  r=copy.deepcopy(self.rows[0]);r['tradeoffs']['missing_reason']=''
  with self.assertRaises(ValueError):validate_experience(r)
 def test_dangling_reference_rejected(self):
  r=copy.deepcopy(self.rows[0]);r['mechanism']['evidence_ids']=['absent']
  with self.assertRaises(ValueError):validate_experience(r)
 def test_no_public_upgrade(self):
  r=copy.deepcopy(self.rows[0]);r['visibility']='public'
  with self.assertRaises(ValueError):validate_experience(r)
 def test_search_and_no_knowledge_claim(self):
  self.assertEqual(search_experiences(self.rows,'洗涤液')['total'],0)
  fixtures=copy.deepcopy(self.rows)
  for r in fixtures:
   for e in r['evidence_refs']:e['authorization']={'purpose':'internal_research','status':'granted','origin_kind':'public_excerpt','basis':'Constructed test-only grant; no actual sample authorization.'}
  self.assertGreater(search_experiences(fixtures,'洗涤液')['total'],0)
  self.assertEqual(search_experiences(self.rows,'NONEXISTENT')['total'],0)
  with self.assertRaises(ValueError):search_experiences(self.rows,'')
 def test_bad_sha(self):
  r=copy.deepcopy(self.rows[0]);r['evidence_refs'][0]['source_sha256']='x'*64
  with self.assertRaises(ValueError):validate_experience(r)
 def test_return_is_detached(self):
  x=validate_experience(self.rows[0]);x['mechanism']['value']='modified';self.assertNotEqual(x,self.rows[0])
 def test_nontext_claim(self):
  for value in ({'bad':'value'},True,[],5):
   r=copy.deepcopy(self.rows[0]);r['mechanism']['value']=value
   with self.assertRaises(ValueError):validate_experience(r)
 def test_missing_or_ambiguous_permission(self):
  r=copy.deepcopy(self.rows[0]);r['evidence_refs'][0].pop('authorization')
  with self.assertRaises(ValueError):validate_experience(r)
  r=copy.deepcopy(self.rows[0]);r['evidence_refs'][0]['permission']='public'
  with self.assertRaises(ValueError):validate_experience(r)
 def test_denied_not_callable(self):
  r=copy.deepcopy(self.rows[0]);r['evidence_refs'][0]['authorization']['status']='denied'
  self.assertEqual(search_experiences([r],'洗涤液')['total'],0)
if __name__=='__main__':unittest.main()
