# coding: utf-8
import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import innovation_methods as im
from run_method_case_demo import build_analysis
class MethodLibraryTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.run_data=im.read_run('latest','full')
 def test_three_complete_cards(self):
  rows=im.catalog()['methods'];self.assertEqual(len(rows),3);total=0
  for row in rows:
   m=im.read_method(row['method_id'],level='full')['data'];total+=im.validate_card(m)['steps'];self.assertTrue(m['provenance']['sources']);self.assertEqual(m['provenance']['nature'],'platform_adaptation')
  self.assertEqual(total,16)
 def test_alias_search_and_layered_read(self):
  self.assertEqual(im.search_methods('TRIZ')['data'][0]['method_id'],'IM-CA-001');d=im.read_method('IM-PD-001',level='steps',limit=2);self.assertEqual(len(d['data']),2);self.assertEqual(d['next_offset'],2)
 def test_method_dependencies_and_paths(self):
  m=im.read_method('IM-FA-001',level='full')['data'];m['steps'][0]['depends_on']=[m['steps'][-1]['step_id']]
  with self.assertRaises(ValueError):im.validate_card(m)
  for mid in ['../../secret','IM-FA-001/../../']:
   with self.assertRaises(ValueError):im.read_method(mid)
 def test_run_valid_and_handoffs_have_values(self):
  self.assertEqual(im.validate_run(self.run_data)['steps'],16);self.assertEqual(len(self.run_data['handoffs']),3);self.assertGreaterEqual(len(self.run_data['retrievals']),20)
 def test_changed_evidence_is_rejected(self):
  run=copy.deepcopy(self.run_data);run['evidence'][0]['text']+=' forged'
  with self.assertRaises(ValueError):im.validate_run(run)
 def test_missing_evidence_and_handoff_are_rejected(self):
  run=copy.deepcopy(self.run_data);run['stages'][1]['steps'][1]['evidence_ids']=['MISSING']
  with self.assertRaises(ValueError):im.validate_run(run)
  run=copy.deepcopy(self.run_data);run['stages'][1]['input_bindings']['problem_brief']['sha256']='bad'
  with self.assertRaises(ValueError):im.validate_run(run)
 def test_query_plan_is_actually_executed(self):
  run=copy.deepcopy(self.run_data);run['stages'][0]['steps'][3]['knowledge_retrievals']={}
  with self.assertRaises(ValueError):im.validate_run(run)
 def test_forged_mcp_result_is_rejected(self):
  run=copy.deepcopy(self.run_data);run['retrievals'][0]['response']['total']=999
  with self.assertRaises(ValueError):im.validate_run(run)
 def test_missing_task_input_stops(self):
  task=copy.deepcopy(self.run_data['task']);task['object']=None
  with self.assertRaises(ValueError):im.task_gate(task)
 def test_unknown_values_remain_unknown(self):
  run=self.run_data;self.assertTrue(all(v is None for v in run['task']['target_parameters'].values()));self.assertEqual(run['enterprise_output']['decision_level'],'concept_only_requires_confirmation');self.assertTrue(all(v['thresholds']is None and v['result']=='not_tested'for v in run['enterprise_output']['validation_plan']))
 def test_hard_constraint_blocks_matching_direction(self):
  constraints=dict(self.run_data['task']['constraints'],flexible_contact_allowed=False,load_sensing_allowed=False);directions=im.filter_directions(self.run_data['enterprise_output']['directions'],constraints);self.assertEqual(directions[0]['status'],'excluded');self.assertEqual(directions[2]['status'],'excluded');self.assertEqual(directions[1]['status'],'conditional')
 def test_cannot_claim_engineering_success(self):
  run=copy.deepcopy(self.run_data);run['enterprise_output']['directions'][0]['engineering_validated']=True
  with self.assertRaises(ValueError):im.validate_run(run)
 def test_normal_phase_change_not_counted_as_confirmed_invention(self):
  stage=self.run_data['stages'][2];physical=stage['steps'][2]['output'];self.assertEqual(physical[1]['status'],'ordinary_sequence_possible_not_counted_as_inventive_conflict');self.assertFalse(stage['steps'][3]['output']['matrix_used']);self.assertEqual(stage['steps'][3]['output']['selected_principle_numbers'],[])
 def test_fixed_scenario_is_not_general_inference(self):
  task=copy.deepcopy(self.run_data['task']);task['object']='液体药物'
  with self.assertRaises(ValueError):build_analysis(task,{}, {},self.run_data['evidence'])
if __name__=='__main__':unittest.main()
