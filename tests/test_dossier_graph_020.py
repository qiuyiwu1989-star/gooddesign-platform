# coding: utf-8
"""020: typed evidence, bounded analogy and application data isolation."""
import sys,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'04-知识库/标杆案例/2025-00-嫦娥钻取采样';sys.path.insert(0,str(ROOT/'scripts'))
from build_project_graph_demo import build
from dossier_governance import digest
read=lambda n:json.loads((P/n).read_text())
class GraphTests(unittest.TestCase):
 def test_graph_relations_and_ids_are_consistent(self):
  build(P);g=read('项目图谱.json');ids={n['id']for n in g['nodes']}
  self.assertEqual(len(ids),len(g['nodes']))
  for e in g['edges']:self.assertIn(e['source'],ids);self.assertIn(e['target'],ids)
  self.assertEqual(sum(e['relation']=='analogy_hypothesis'for e in g['edges']),3)
  self.assertEqual(sum(e['relation']=='excluded_direct_transfer'for e in g['edges']),1)
  for e in g['edges']:
   if e['relation']=='analogy_hypothesis':self.assertFalse(e['verified_transfer'])
 def test_target_task_and_thresholds_are_explicitly_hypothetical(self):
  d=read('割胶机器人-迁移试读.json');self.assertEqual(d['target']['nature'],'user_hypothetical_task');self.assertIsNone(d['target']['acceptance_thresholds'])
  self.assertTrue(d['novelty']);self.assertEqual(len(d['sources']),2)
  for path in d['paths']:self.assertTrue(path['difference']);self.assertTrue(path['questions']);self.assertTrue(path['cannot_copy'])
 def test_inference_is_distinct_from_domain_fact(self):
  d=read('割胶机器人-迁移试读.json');claims={c['id']:c for c in d['external_claims']}
  self.assertEqual(claims['RC01']['nature'],'source_summary');self.assertEqual(claims['RC04']['nature'],'platform_inference')
  self.assertEqual(next(s for s in d['sources']if s['id']=='RS02')['read_scope'],'abstract_only')
  self.assertEqual(next(p for p in d['paths']if p['id']=='P04')['status'],'excluded_direct_transfer')
 def test_context_pins_archive_and_preserves_evidence(self):
  c=read('图谱调用样例.json');snapshot=read('版本/0.4.0/snapshot.json')
  self.assertEqual(c['archive_sha256'],digest(snapshot));self.assertEqual(c['archive_revision'],'0.4.0')
  data=c['ordered_context'][2]['data'];sources={s['id']for s in data['citations']}
  claims={x['id']for x in data['claims']}
  for k in data['knowledge']:self.assertTrue(set(k['source_ids'])<=sources);self.assertTrue(k['boundary']);self.assertTrue(set(k['claim_ids'])<=claims)
  for claim in data['claims']:self.assertTrue(set(claim['source_ids'])<=sources)
  self.assertTrue(data['test_contexts']);self.assertTrue(data['validations'])
  self.assertEqual([x['priority']for x in c['ordered_context']],[1,2,3,4])
 def test_supplement_does_not_rewrite_archive_or_raise_score(self):
  old=read('版本/0.4.0/snapshot.json');new=read('版本/0.4.1/snapshot.json')
  for key in old.keys()-{'version_declaration'}:self.assertEqual(old[key],new[key])
  self.assertEqual(new['quality']['score'],55);self.assertNotIn('割胶',json.dumps(new['evidence'],ensure_ascii=False))
  self.assertIsNone(read('图谱验收.json')['calibrated_similarity_score'])
if __name__=='__main__':unittest.main()
