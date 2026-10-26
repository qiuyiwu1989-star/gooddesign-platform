"""ML-009 fixtures test review semantics, not engineering compatibility."""
import copy
import unittest
from method_workbench_review import review

class Checks(unittest.TestCase):
    def state(self):
        return {'submissions':[{'artifact':{'type':'ConceptSet','payload':{'options':[{'id':x} for x in 'ABC'], 'combinations':[{'id':'C1','option_ids':['A','B']}], 'compatibility':[{'option_ids':['B','A'],'status':'unknown','reason':'test'},{'option_ids':['A','C'],'status':'incompatible'}]}}}, {'artifact':{'type':'ComparisonRecord','payload':{'criteria':[{'id':'N1','hard':True},{'id':'N2','hard':None},{'id':'N3','hard':False}],'judgments':[{'candidate_id':'C1','criterion_id':'N1','value':'unknown'}]}}}]}
    def test_empty(self):
        self.assertFalse(review({},[])['available'])
    def test_internal_pairs_only(self):
        c=review(self.state(),[])['candidates'][0]
        self.assertEqual(c['pair_count'],1)
        self.assertEqual(c['pair_counts']['unknown'],1)
        self.assertEqual(c['pair_counts']['incompatible'],0)
    def test_absent_not_conflict(self):
        s=self.state();s['submissions'][0]['artifact']['payload']['compatibility']=[]
        self.assertEqual(review(s,[])['candidates'][0]['pair_counts']['unreviewed'],1)
    def test_conflicting_duplicate_not_verified(self):
        s=self.state();p=s['submissions'][0]['artifact']['payload'];p['compatibility'] += [{'option_ids':['A','B'],'status':'compatible'}]*2
        self.assertEqual(review(s,[])['candidates'][0]['pair_counts']['disputed'],1)
        self.assertFalse(review(s,[])['expert_certified'])
    def test_dangling_reference(self):
        s=self.state();p=s['submissions'][0]['artifact']['payload'];p['options'][0]['evidence_refs']=['E1'];p['compatibility'].append({'option_ids':['A','Z'],'status':'compatible'})
        self.assertEqual(len(review(s,[])['anomalies']),2)
        self.assertEqual(len(review(s,[{'id':'E1'}])['anomalies']),1)
    def test_hard_unknown_and_missing(self):
        self.assertEqual(review(self.state(),[])['candidates'][0]['hard_unresolved'],2)
    def test_fingerprint_and_no_mutation(self):
        s=self.state();old=copy.deepcopy(s);a=review(s,[])
        self.assertEqual(old,s)
        self.assertEqual(a['input_sha256'],review(s,[])['input_sha256'])
        s['submissions'][0]['artifact']['payload']['combinations'][0]['reason']='changed'
        self.assertNotEqual(a['input_sha256'],review(s,[])['input_sha256'])

if __name__=='__main__': unittest.main(verbosity=2)
