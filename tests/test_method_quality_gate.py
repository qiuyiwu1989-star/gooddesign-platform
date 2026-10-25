import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from method_quality_gate import assess, DIMENSIONS


def packet():
    return dict(level='concept', revision='p2', task_revision='t1', method_versions=['m1'], scope='fixture-concept', author_id='a',
                claims=[dict(text='教学判断', kind='fact', critical=True, evidence_refs=['e'])],
                evidence=[dict(id='e', source_revision='s1', locator='p1', support_review='supported')],
                hard_constraints_checked=True, reviews=[dict(reviewer_id='b', scope='fixture-concept', qualification_checked=True,
                packet_revision='p2', revision='r1', outcome='accept')],
                ratings={d:dict(score=3, basis='测试评审记录，不是真实专家') for d in DIMENSIONS})


class GateTests(unittest.TestCase):
    def test_normal_is_not_certified(self):
        result=assess(packet());self.assertEqual(result['status'],'eligible_for_controlled_release');self.assertFalse(result['expert_certified'])

    def test_failures(self):
        cases=[('hard_constraints_checked',False),('reviews',[]),('level','validated'),('evidence',[]),('ratings',{}),
               ('issues',[dict(severity='major',status='open')]),('hard_constraint_violations',['unsafe'])]
        for field,value in cases:
            with self.subTest(field=field):
                p=packet();p[field]=value;self.assertEqual(assess(p)['status'],'blocked')

    def test_self_and_stale_reviews(self):
        for field,value in [('reviewer_id','a'),('packet_revision','old'),('qualification_checked',False)]:
            p=packet();p['reviews'][0][field]=value;self.assertEqual(assess(p)['status'],'blocked')

    def test_hypothesis_cannot_be_fact(self):
        p=packet();p['claims']=[dict(text='假设',kind='hypothesis',critical=True)]
        self.assertIn('hypothesis_without_test',assess(p)['issues'])

    def test_duplicate_evidence(self):
        p=packet();p['evidence']*=2;self.assertIn('duplicate_or_empty_evidence_id',assess(p)['issues'])

    def test_missing_packet_revision_and_malformed_review(self):
        p=packet();del p['revision']
        self.assertEqual(assess(p)['status'],'blocked')
        for invalid in (None,{'reviews':['not-a-review']},{'ratings':{'problem':3}}):
            self.assertEqual(assess(invalid)['status'],'blocked')


if __name__=='__main__':unittest.main()
