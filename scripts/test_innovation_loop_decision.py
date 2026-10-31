import copy
import unittest
from innovation_loop_decision import *

class DecisionTests(unittest.TestCase):
    def setUp(self):
        self.req={'schema_version':'0.1.0','id':'RQ-DEMO','revision':1,'status':'proposed','goal':'教学：研究胶路维护','budget':None,'operating_context':None,'acceptance_threshold':None,'missing_reason':{k:'未取得客户输入' for k in ('budget','operating_context','acceptance_threshold')}}
        self.routes=[{'schema_version':'0.1.0','id':'R'+str(i),'revision':1,'requirement_ref':{'id':'RQ-DEMO','revision':1},'mechanism':m,'conditions':['待研究假设，非客户事实'],'next_action':'核对清理与接触边界','constraint_status':'unknown','cost':None,'missing_reason':{'cost':'无报价'}} for i,m in enumerate(['接口分离','时序分离','独立感知'])]
    def test_unknown_is_preserved(self):
        original=copy.deepcopy(self.routes); x=compare_routes(self.req,self.routes)
        self.assertIsNone(x['ranking']); self.assertIsNone(x['routes'][0]['cost']);self.assertEqual(original,self.routes)
    def test_budget_validation(self):
        for b in (-1, True, {'value':True,'unit':'CNY'}, {'value':-1,'unit':'CNY'}, {'value':1,'unit':''}):
            self.req['budget']=b
            with self.assertRaises(ValueError):validate_requirement(self.req)
        self.req['budget']={'value':0,'unit':'CNY'}
        self.assertEqual(validate_requirement(self.req)['budget']['value'],0)
    def test_confirmation_requires_evidence(self):
        self.req['status']='confirmed'
        with self.assertRaises(ValueError):validate_requirement(self.req)
    def test_missing_reason(self):
        self.req['missing_reason']={}
        with self.assertRaises(ValueError):validate_requirement(self.req)
    def test_revision_diff(self):
        new=copy.deepcopy(self.req);new.update(revision=2,goal='新目标')
        self.assertTrue(diff_requirements(self.req,new)['route_review_required'])
        with self.assertRaises(ValueError):diff_requirements(new,new)
    def test_stale_route(self):
        self.routes[0]['requirement_ref']['revision']=2
        with self.assertRaises(ValueError):compare_routes(self.req,self.routes)
    def test_conflict_no_ranking(self):
        self.routes[1]['constraint_status']='conflict'; x=compare_routes(self.req,self.routes,{'actor':'教学用户','criteria':['周期']})
        self.assertEqual(x['blocked_route_ids'],['R1']);self.assertIsNone(x['ranking']);self.assertEqual(x['conditional_suggestions'][1]['status'],'blocked_by_constraint_conflict');self.assertFalse(x['conditional_suggestions'][1]['execution_authorized'])
    def test_duplicate_and_nonfinite(self):
        with self.assertRaises(ValueError):compare_routes(self.req,[self.routes[0]]*2)
        self.req['budget']=float('nan')
        with self.assertRaises(ValueError):validate_requirement(self.req)
    def test_feedback(self):
        f={'schema_version':'0.1.0','id':'F1','revision':1,'kind':'opinion','actor_role':'教学评审','basis':'构造反馈','authorization':{'internal_research':True,'public':False,'training':False},**{k:{'id':'DEMO','revision':1} for k in ('requirement_ref','route_ref','claim_ref')}}
        self.assertEqual(validate_feedback(f)['processing_status'],'pending_review')
        f['apply_to_facts']=True
        with self.assertRaises(ValueError):validate_feedback(f)
    def test_feedback_exact_version(self):
        with self.assertRaises(ValueError):validate_feedback({'schema_version':'0.1.0','id':'F','revision':1})

if __name__=='__main__':unittest.main()
