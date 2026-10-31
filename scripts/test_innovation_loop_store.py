import copy,json,tempfile,unittest
from pathlib import Path
from innovation_loop_store import LoopStore,ROOT
class TestStore(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(dir=ROOT/'output/innovation-loop-024');self.s=LoopStore(Path(self.tmp.name)/'test.sqlite3')
  self.sample=json.loads((ROOT/'output/innovation-loop-024/decision/sample.json').read_text());self.r=self.sample['requirement'];self.s.put('requirement',self.r)
 def tearDown(self):self.tmp.cleanup()
 def test_immutable_and_idempotent(self):
  self.assertEqual(self.s.put('requirement',self.r)['status'],'already_saved');r=copy.deepcopy(self.r);r['goal']='other'
  with self.assertRaises(ValueError):self.s.put('requirement',r)
 def test_revision_conflict(self):
  r=copy.deepcopy(self.r);r['revision']=2
  with self.assertRaises(ValueError):self.s.put('requirement',r,0)
  self.s.put('requirement',r,1);self.assertEqual(self.s.get('requirement',r['id'],1),self.r)
 def test_feedback_links(self):
  route=self.sample['comparison']['routes'][0];self.s.put('route',route)
  c={'schema_version':'0.1.0','id':'C1','revision':1,'route_ref':{'id':route['id'],'revision':1},'text':'candidate only','nature':'hypothesized','basis':'constructed teaching'};self.s.put('claim',c)
  f={'schema_version':'0.1.0','id':'F1','revision':1,'requirement_ref':route['requirement_ref'],'route_ref':c['route_ref'],'claim_ref':{'id':'C1','revision':1},'kind':'opinion','actor_role':'internal_reviewer','basis':'test only','authorization':{'internal_research':True,'public':False,'training':False}}
  self.s.put('feedback',f);self.assertEqual(self.s.get('feedback','F1',1)['processing_status'],'pending_review')
  f['id']='F2';f['claim_ref']['id']='missing'
  with self.assertRaises(ValueError):self.s.put('feedback',f)
 def test_action_and_transfer_dangling(self):
  sample=json.loads((ROOT/'output/innovation-loop-024/decision/transfer-action-sample.json').read_text())
  with self.assertRaises(ValueError):self.s.put('transfer',sample['transfer'])
  with self.assertRaises(ValueError):self.s.put('action',sample['research_action'])
  self.s.put('route',self.sample['comparison']['routes'][1]);self.s.put('action',sample['research_action'])
  self.assertFalse(self.s.get('action','ACT1',1)['execution_authorized'])
 def test_claim_rejects_boolean_text(self):
  route=self.sample['comparison']['routes'][0];self.s.put('route',route)
  c={'schema_version':'0.1.0','id':'BAD','revision':1,'route_ref':{'id':route['id'],'revision':1},'text':True,'nature':'hypothesized','basis':'constructed'}
  with self.assertRaises(ValueError):self.s.put('claim',c)
if __name__=='__main__':unittest.main()
