# coding: utf-8
"""016: protect source scopes and units when deepening the benchmark."""
import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'04-知识库/标杆案例/2025-00-嫦娥钻取采样'
def read(name):return json.loads((P/name).read_text())
class ResearchTests(unittest.TestCase):
 def setUp(self):
  self.d=read('档案数据.json');self.a=read('原子字段档案.json');self.r={x['id']:x for x in self.a['records']}
 def test_ground_error_and_component_units(self):
  for rid,value,unit in [('MET-05',4.31,'%'),('MET-06',850,'N'),('MET-07',40,'N·m'),('MET-09',38,'mm')]:
   self.assertEqual(self.r[rid]['cells']['value']['value'],value);self.assertEqual(self.r[rid]['cells']['unit']['value'],unit)
  self.assertEqual(self.r['MET-05']['cells']['value']['source_ids'],['S07'])
  self.assertNotEqual(self.r['MET-09']['cells']['subject']['value'],'整机')
 def test_ten_observations_keep_original_units_and_groups(self):
  study=next(v for v in self.d['validations']if v['id']=='V02');rows=study['trials'];self.assertEqual(len(rows),10)
  self.assertEqual(sum(r['group']=='SY01'for r in rows),5);self.assertEqual(sum(r['group']=='SY02'for r in rows),5)
  self.assertEqual(rows[0]['sample_mass_g'],383);self.assertEqual(rows[-1]['sample_length_mm'],1510)
  self.assertIn('50 r/min',rows[0]['setting_original']);self.assertNotIn('mm/min',rows[0]['setting_original'])
  for r in rows:self.assertEqual(r['source_ids'],['S23']);self.assertTrue(r['locator'])
 def test_paper_reading_and_bibliography_are_distinct(self):
  self.assertEqual(self.r['A03']['cells']['year']['value'],2021);self.assertEqual(self.r['A03']['cells']['year']['source_ids'],['S23'])
  self.assertEqual(self.r['A03']['cells']['reading_scope']['value'],'摘要')
  self.assertEqual(self.r['A04']['cells']['project_relation']['content_nature'],'platform_analysis')
  self.assertGreaterEqual(self.a['counts']['paper_full_text_read'],2);self.assertEqual(self.a['counts']['paper_records_found'],len(self.d['papers']))
 def test_flight_depth_is_distinct_from_ground_depth(self):
  self.assertEqual(self.r['MET-11']['cells']['value']['value'],1009);self.assertEqual(self.r['MET-12']['cells']['value']['value'],1035)
  m=read('主档案结构.json');f={x['id']:x for d in m['dimensions']for x in d['fields']}
  self.assertEqual(f['F023']['value']['2025_ground_test']['drilling_depth_mm'],2000)
  self.assertIsNone(f['F014']['value']['mass']);self.assertIsNone(f['F014']['value']['power']);self.assertEqual(f['F014']['value_state'],'partial')
 def test_score_is_self_assessment_with_open_gates(self):
  q=read('质量评估.json');self.assertEqual(q['assessment_type'],'platform_document_self_assessment_not_expert_review')
  self.assertFalse(q['gates']['expert_review_complete']);self.assertFalse(q['gates']['full_research_complete'])
  self.assertIsNone(self.a['counts']['patent_project_confirmed'])
if __name__=='__main__':unittest.main()
