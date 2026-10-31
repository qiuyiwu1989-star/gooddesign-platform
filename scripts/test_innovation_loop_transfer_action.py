import unittest,copy
from innovation_loop_decision import *
from test_innovation_loop_decision import DecisionTests
class TransferActionTests(unittest.TestCase):
 def setUp(self):
  self.transfer={'schema_version':'0.1.0','id':'TR1','revision':1,'nature':'hypothesized','source_anchor':{'id':'SRC1','revision':1,'locator':'mechanism paragraph'},'target_anchor':{'id':'RQ1','revision':1,'locator':'constraint proposal'},'differences':['工况待对照'],'assumptions':['结构作用可能类比'],'falsification':['若接口损失不可接受则放弃'],'transfer_kind':'structure_hypothesis','copy_parameter':False}
  self.action={'schema_version':'0.1.0','id':'ACT1','revision':1,'route_ref':{'id':'R1','revision':1},'question':'区分损失来自接口还是管路','hypotheses':['接口损失','管路阻力'],'resources':None,'responsible_actor':None,'missing_reason':{'resources':'尚无台架清单','responsible_actor':'待项目方指定'},'observation':'记录代理件各段残留','decision_rule':'量测能力确认后制定判别阈值，当前不可执行','stop_condition':'量测不确定性无法区分两解释时停止','professional_approval':{'status':'required'}}
 def test_transfer(self):self.assertEqual(validate_route_transfer(self.transfer)['semantic_review_status'],'pending')
 def test_bad_transfer(self):
  for key,value in [('copy_parameter',True),('source_anchor',{}),('differences',[]),('nature','source_statement')]:
   t=copy.deepcopy(self.transfer);t[key]=value
   with self.assertRaises(ValueError):validate_route_transfer(t)
 def test_action(self):self.assertFalse(validate_research_action(self.action)['execution_authorized'])
 def test_bad_action(self):
  for key,value in [('missing_reason',{}),('professional_approval',{'status':'approved'}),('stop_condition',True),('route_ref',{'id':123,'revision':1})]:
   t=copy.deepcopy(self.action);t[key]=value
   with self.assertRaises(ValueError):validate_research_action(t)
 def test_confirmation(self):
  t=DecisionTests();t.setUp();r=t.req;r['status']='confirmed';r['confirmation']={'actor':'构造客户','at':'not-date','evidence_ref':{'id':'E','revision':1}}
  with self.assertRaises(ValueError):validate_requirement(r)
  r['confirmation']['at']='2026-10-31T20:00:00+09:00';self.assertEqual(validate_requirement(r)['status'],'confirmed')
  r['confirmation']['evidence_ref']['id']=123
  with self.assertRaises(ValueError):validate_requirement(r)
if __name__=='__main__':unittest.main()
