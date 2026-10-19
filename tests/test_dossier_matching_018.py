# coding: utf-8
"""018: conditions, provenance, revision binding and conservative benchmark gates."""
import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'04-知识库/标杆案例/2025-00-嫦娥钻取采样'
sys.path.insert(0,str(ROOT/'scripts'))
from dossier_matching import evaluate,context_pack,build
from dossier_governance import capture,read
class MatchingTests(unittest.TestCase):
 def setUp(self):
  self.m=read(P/'匹配知识.json');self.cards={c['id']:c for c in self.m['cards']};self.positive=next(f for f in self.m['fixtures']if f['id']=='MC02-positive')
 def test_positive_negative_and_unknown_fixtures(self):
  self.assertEqual(len(self.m['fixtures']),7)
  for f in self.m['fixtures']:self.assertEqual(evaluate(self.cards[f['card_id']],f)['status'],f['expected'])
 def test_conflict_wins_over_other_unknown_conditions(self):
  request=dict(self.positive,conditions={'load_feedback_allowed':False,'motion_adjustable':None})
  result=evaluate(self.cards['MC02'],request)
  self.assertEqual(result['status'],'excluded');self.assertTrue(result['conflicts']);self.assertTrue(result['questions'])
 def test_unknown_is_not_false_or_true(self):
  for condition in [{},{'load_feedback_allowed':None}]:
   self.assertEqual(evaluate(self.cards['MC02'],dict(self.positive,conditions=condition))['status'],'needs_clarification')
  for bad in [0,1,'yes',[],{}]:
   with self.assertRaises(ValueError):evaluate(self.cards['MC02'],dict(self.positive,conditions={'load_feedback_allowed':bad}))
 def test_inspiration_does_not_grant_implementation_or_partner_access(self):
  for mode in ['implementation','partner']:
   result=evaluate(self.cards['MC02'],dict(self.positive,task=mode))
   self.assertEqual(result['status'],'needs_validation');self.assertTrue(result['verification_required'])
  self.assertEqual(evaluate(self.cards['MC02'],dict(self.positive,problem_key='unrelated'))['status'],'different_problem')
 def test_context_keeps_boundaries_and_citations_with_frozen_version(self):
  c=copy.deepcopy(self.cards['MC02']);c['missing']=['fake current value']
  pack=context_pack(P,c,self.positive,'0.3.0')
  self.assertEqual(pack['revision'],'0.3.0')
  self.assertEqual([x['priority']for x in pack['ordered_context']],[1,2,3,4])
  data=pack['ordered_context'][1]['data'];self.assertIsNone(data['migration_validation']);self.assertNotIn('fake current value',data['target_unknowns'])
  self.assertTrue(data['source_boundary']);self.assertTrue(data['tradeoffs'])
  for claim in pack['ordered_context'][2]['data']['claim_records']:self.assertTrue(claim['locator']);self.assertTrue(claim['source_ids']);self.assertTrue(claim['nature'])
  citations=pack['ordered_context'][2]['data']['citations'];self.assertEqual(len(citations),len({x['source_id']for x in citations}))
  for citation in citations:self.assertTrue(citation['locator']);self.assertTrue(citation['reading_scope'])
  self.assertEqual(set(pack['ordered_context'][0]['data']),{'task','problem_key','conditions'})
 def test_no_matching_card_is_faked_in_earlier_revision(self):
  for revision in ['0.2.1','99.0.0','../0.3.0']:
   with self.assertRaises(ValueError):context_pack(P,self.cards['MC02'],self.positive,revision)
 def test_trial_quality_and_data_are_not_promoted(self):
  _,report=build(P);self.assertEqual(report['status'],'trial_not_certified')
  self.assertFalse(report['ready_for_controlled_replication']);self.assertFalse(report['ready_to_scale'])
  current=capture(P);prior=read(P/'版本/0.2.1/snapshot.json')
  for key in ['evidence','atomic','document','quality','reader_content']:self.assertEqual(current[key],prior[key])
  self.assertEqual(current['matching_knowledge'],self.m)
  v=current['version_declaration'];self.assertEqual(v['content_target'],'0.3.0');self.assertEqual(v['field_schema'],current['field_schema']['version'])
if __name__=='__main__':unittest.main()
