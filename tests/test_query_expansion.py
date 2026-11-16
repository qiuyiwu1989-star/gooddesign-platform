import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from innovation_query_expansion import expand,search
class ExpansionTests(unittest.TestCase):
 def index(self):
  return dict(project_id='fixture',revision='research-000001',index_sha256='fixture',gaps=[],nodes=[dict(id='N1',value='再生制动使能量回馈',conditions=None,limitations=None,dimensions=['mechanism']),dict(id='N2',value='制动能量回收',conditions=None,limitations=None,dimensions=['mechanism'])])
 def test_polarity_not_expanded(self):
  for q in ['不使用制动能量回收','without vibration compensation','禁止电机调速']:
   self.assertEqual(expand(q)['expansions'],[])
 def test_uncovered_not_invented(self):
  self.assertEqual(expand('树皮组织识别')['expansions'],[])
 def test_literal_first_and_dedup(self):
  x=search(self.index(),'制动能量回收');self.assertEqual([r['node']['id'] for r in x['matches']],['N2','N1']);self.assertEqual(x['matches'][1]['retrieval_route'],'vocabulary_expansion');self.assertEqual(x['matches'][1]['target_applicability'],'unverified')
 def test_no_source_mutation(self):
  import copy
  idx=self.index();old=copy.deepcopy(idx);search(idx,'制动能量回收');self.assertEqual(idx,old)
 def test_bounded_invalid_input(self):
  for q in ['', 'x'*201]:
   with self.assertRaises(ValueError):expand(q)
  with self.assertRaises(ValueError):search(self.index(),'能量',True)
if __name__=='__main__':unittest.main()
