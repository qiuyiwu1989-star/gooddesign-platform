# coding: utf-8
"""Reader acceptance: reconcile counts, preserve evidence boundaries and versions."""
import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'04-知识库/标杆案例/2025-00-嫦娥钻取采样'
sys.path.insert(0,str(ROOT/'scripts'))
from dossier_governance import capture
read=lambda n:json.loads((P/n).read_text())
class ReaderTests(unittest.TestCase):
 def test_each_record_and_cell_counted_once(self):
  a=read('原子字段档案.json');s=read('字段规范.json');r=read('阅读统计.json')
  blocks={x['key']:x['block']for x in s['entities']}
  self.assertEqual(len(r['modules']),8)
  for m in r['modules']:
   records=[x for x in a['records']if blocks[x['entity']]==m['id']]
   cells=[c for x in records for c in x['cells'].values()]
   self.assertEqual(m['records'],len(records));self.assertEqual(m['total'],len(cells))
   self.assertEqual(m['known'],sum(c['value_state']=='known'for c in cells))
  self.assertEqual(sum(m['records']for m in r['modules']),len(a['records']))
  self.assertEqual(r['totals']['known'],read('质量评估.json')['metrics']['known_slots'])
 def test_paper_interpretations_do_not_upgrade_reading_scope(self):
  c=read('阅读内容.json');d=read('档案数据.json');sources={s['id']for s in d['sources']}
  self.assertEqual({x['paper_id']for x in c['papers']},{x['id']for x in d['papers']})
  byid={x['paper_id']:x for x in c['papers']}
  for x in c['papers']:self.assertTrue(set(x['source_ids'])<=sources);self.assertTrue(x['boundary'])
  self.assertIsNone(byid['A02']['finding'])
  for pid in ['A02','A03']:self.assertIn('仅核读摘要',byid[pid]['boundary'])
 def test_interpretation_versioned_without_changing_project_facts(self):
  current=json.loads((P/'版本/0.2.1/snapshot.json').read_text());self.assertIn('reader_content',current)
  old=json.loads((P/'版本/0.2.0/snapshot.json').read_text())
  for key in ['evidence','atomic','document','quality']:
   self.assertEqual(current[key],old[key])
 def test_reader_is_primary_and_research_is_preserved(self):
  html=(P/'档案.html').read_text()
  self.assertIn('else switchView(\'reader\')',html)
  reader=html.split('<div id="reader-view">',1)[1].split('<div id="library-view"',1)[0]
  for term in ['待研究','cell-proof','data-source=','high','F001']:self.assertNotIn(term,reader)
  self.assertIn('aria-label="暂无资料"',reader)
  self.assertIn('研究与维护工具',html)
  for anchor in ['reader-overview','reader-governance','paper-A01','source-S01','field-F001','block-overview']:self.assertIn('id="'+anchor+'"',html)
if __name__=='__main__':unittest.main()
