# coding: utf-8
"""019: source conditions, dimensional checks, derived statistics and honest reassessment."""
import json,sys,unittest,copy,tempfile,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'04-知识库/标杆案例/2025-00-嫦娥钻取采样';sys.path.insert(0,str(ROOT/'scripts'))
from dossier_matching import evaluate,context_pack,evaluate_v1
from dossier_research import build
from dossier_reference_check import compare_reference
read=lambda n:json.loads((P/n).read_text())
class EngineTests(unittest.TestCase):
 def setUp(self):
  self.m=read('匹配知识.json');self.cards={x['id']:x for x in self.m['cards']};self.profiles=read('研究证据.json')['profiles'];self.base=copy.deepcopy(next(x for x in self.m['fixtures']if x['id']=='MC02-positive'))
 def request(self,value=400,unit='N',material='nominal_soil_simulant'):
  return dict(self.base,reference_check=dict(profile_id='EP02',material_key=material,measurements={'target_force':dict(value=value,unit=unit)}))
 def test_equivalent_units_do_not_certify_transfer(self):
  a=evaluate(self.cards['MC02'],self.request(400),profiles=self.profiles);b=evaluate(self.cards['MC02'],self.request(.4,'kN'),profiles=self.profiles)
  self.assertEqual(a['reference_check']['normalized'],b['reference_check']['normalized']);self.assertEqual(a['status'],'analogy_candidate');self.assertTrue(a['verification_required'])
 def test_material_and_outside_reported_point_require_validation(self):
  for request in [self.request(500),self.request(material='artificial_marble')]:self.assertEqual(evaluate(self.cards['MC02'],request,profiles=self.profiles)['status'],'needs_validation')
 def test_missing_value_or_unit_asks_instead_of_matching(self):
  for value,unit in [(None,'N'),(400,None)]:
   result=evaluate(self.cards['MC02'],self.request(value,unit),profiles=self.profiles);self.assertEqual(result['status'],'needs_clarification');self.assertTrue(result['questions'])
 def test_physical_quantity_and_nonfinite_values_are_rejected(self):
  for value,unit in [(True,'N'),(float('nan'),'N'),(float('inf'),'N'),(400,'r/min')]:
   with self.assertRaises(ValueError):evaluate(self.cards['MC02'],self.request(value,unit),profiles=self.profiles)
  req=self.request();req['reference_check']['measurements']={'loading_rot_speed':dict(value=120,unit='r/min')}
  with self.assertRaises(ValueError):evaluate(self.cards['MC02'],req,profiles=self.profiles)
 def test_discrete_levels_are_not_a_continuous_valid_range(self):
  req=copy.deepcopy(next(x for x in self.m['fixtures']if x['card_id']=='MC01'and x.get('reference_check')))
  self.assertEqual(evaluate(self.cards['MC01'],req,profiles=self.profiles)['status'],'needs_validation')
  req['reference_check']['measurements']['drill_rot_speed']['value']=90
  self.assertEqual(evaluate(self.cards['MC01'],req,profiles=self.profiles)['reference_check']['status'],'reported_settings_match')
 def test_boolean_conflict_still_has_priority(self):
  req=self.request();req['conditions']['load_feedback_allowed']=False
  self.assertEqual(evaluate(self.cards['MC02'],req,profiles=self.profiles)['status'],'excluded')
 def test_descriptive_stats_are_reproducible_and_not_significance(self):
  stats=build(P);a,b=stats['groups'];self.assertEqual((a['n'],b['n']),(5,5))
  self.assertEqual(a['metrics']['sample_mass_g']['mean'],324.8);self.assertEqual(b['metrics']['sample_mass_g']['mean'],427.4)
  self.assertEqual(b['metrics']['sample_length_mm']['mean'],1392)
  self.assertAlmostEqual(stats['comparisons'][0]['relative_difference_percent'],31.5887,places=4)
  self.assertIn('因果',''.join(stats['limits']));self.assertEqual(len(a['row_ids']+b['row_ids']),10)
 def test_operating_conditions_and_response_are_separate_from_coring(self):
  d=read('档案数据.json');studies={x['id']:x for x in d['validations']}
  self.assertEqual(studies['V04']['reported_setpoint_N'],400);self.assertEqual(studies['V06']['reported_settling_time_s'],8.2)
  self.assertIsNone(studies['V05']['reported_setpoint_N']);self.assertEqual(len(studies['V02']['trials']),10)
  self.assertNotIn('trials',studies['V04'])
 def test_only_supported_dimension_improves_under_same_policy(self):
  old=read('版本/0.3.0/snapshot.json')['quality'];new=read('质量评估.json')
  self.assertEqual(new['policy_version'],old['policy_version']);self.assertEqual(new['score']-old['score'],5)
  for a,b in zip(old['dimensions'],new['dimensions']):self.assertEqual(b['level']-a['level'],1 if a['key']=='technical'else 0)
  self.assertFalse(new['gates']['expert_review_complete']);self.assertFalse(new['gates']['full_research_complete'])
  self.assertEqual(len(read('引擎审计.json')['dimensions']),12)
 def test_frozen_policy_does_not_silently_change_and_new_context_is_complete(self):
  old=context_pack(P,self.cards['MC02'],self.base,'0.3.0')
  self.assertEqual(old['policy_version'],'matching-policy-0.1.0');self.assertEqual(old['decision'],evaluate_v1(self.cards['MC02'],self.base))
  new=context_pack(P,self.cards['MC02'],self.request(),'0.4.0');support=new['ordered_context'][2]['data']
  self.assertEqual(new['revision'],'0.4.0');self.assertIn('evidence_profiles',support);self.assertIn('derived_analysis',support)
  self.assertEqual(support['derived_analysis']['nature'],'platform_derived_not_original_measurement')
  self.assertTrue(support['evidence_profiles'][0]['limits'])
  self.assertNotIn('expected',new['ordered_context'][0]['data'])
 def test_caller_cannot_substitute_the_knowledge_relationship(self):
  forged=dict(self.cards['MC02'],knowledge_id='K01')
  pack=context_pack(P,forged,self.base,'0.4.0')
  self.assertIn('载荷反馈',pack['ordered_context'][1]['data']['mechanism'])
 def test_context_rejects_a_tampered_snapshot(self):
  with tempfile.TemporaryDirectory(dir=str(ROOT/'tmp'))as temp:
   p=Path(temp);(p/'版本').mkdir();shutil.copytree(P/'版本/0.4.0',p/'版本/0.4.0');shutil.copy2(P/'版本/版本索引.json',p/'版本/版本索引.json')
   snapshot=json.loads((p/'版本/0.4.0/snapshot.json').read_text());snapshot['quality']['score']=99
   (p/'版本/0.4.0/snapshot.json').write_text(json.dumps(snapshot,ensure_ascii=False))
   with self.assertRaisesRegex(ValueError,'integrity'):context_pack(p,self.cards['MC02'],self.base,'0.4.0')
if __name__=='__main__':unittest.main()
