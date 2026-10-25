import copy
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from method_engine import ROOT
from method_engine_reasoner import semantic_match, propose_artifact
from method_engine_fixtures import teaching_task, teaching_artifacts


class ReasonerTests(unittest.TestCase):
    def test_missing_inputs_do_not_spend_model_call(self):
        def never(*args):raise AssertionError('unexpected_model_call')
        result=propose_artifact('R17',teaching_task(),reader=never)
        self.assertEqual(result['status'],'blocked')

    def test_one_repair_preserves_failed_attempt(self):
        good=teaching_artifacts()['R48'];bad=copy.deepcopy(good);bad['payload']['requirements'][0]['status']='confirmed'
        responses=iter([bad,good]);calls=[]
        def reader(prompt,folder):calls.append(prompt);return next(responses)
        with tempfile.TemporaryDirectory(dir=ROOT/'output') as tmp:
            result=propose_artifact('R48',teaching_task(),reader=reader,folder=Path(tmp)/'step')
        self.assertEqual(len(calls),2);self.assertIn('REPAIR',calls[-1]);self.assertFalse(result['expert_certified'])
        self.assertEqual(result['attempts'][0]['check']['status'],'blocked')
        self.assertEqual(result['status'],'draft_requires_semantic_and_domain_review')

    def test_invalid_model_cannot_repair_forever(self):
        bad=teaching_artifacts()['R48'];bad['payload']['requirements'][0]['status']='confirmed'
        calls=[]
        def reader(prompt,folder):calls.append(prompt);return bad
        with tempfile.TemporaryDirectory(dir=ROOT/'output') as tmp:
            result=propose_artifact('R48',teaching_task(),reader=reader,folder=Path(tmp)/'step')
        self.assertEqual(result['status'],'blocked');self.assertEqual(len(calls),2)

    def test_model_cannot_claim_engineering(self):
        response={'selected_methods':['R48'],'stage':'frame','rationale':'fixture','missing_inputs':[],
                  'required_capabilities':[],'transfer_risks':[],'can_produce_engineering_result':True}
        with tempfile.TemporaryDirectory(dir=ROOT/'output') as tmp:
            with self.assertRaisesRegex(ValueError,'engineering_scope'):
                semantic_match('fixture',reader=lambda p,f:response,folder=Path(tmp)/'match')

    def test_unknown_catalog_ids_rejected(self):
        response={'selected_methods':['R99'],'stage':'frame','rationale':'fixture','missing_inputs':[],
                  'required_capabilities':[],'transfer_risks':[],'can_produce_engineering_result':False}
        from jsonschema import ValidationError
        with tempfile.TemporaryDirectory(dir=ROOT/'output') as tmp:
            with self.assertRaises(ValidationError):semantic_match('fixture',reader=lambda p,f:response,folder=Path(tmp)/'match')

    def test_cross_method_failure_is_visible_to_repair(self):
        fixtures=teaching_artifacts();good=fixtures['R42'];bad=copy.deepcopy(good);bad['payload']['requirements_revision']='old'
        responses=iter([bad,good])
        with tempfile.TemporaryDirectory(dir=ROOT/'output') as tmp:
            result=propose_artifact('R42',teaching_task(),[a for r,a in fixtures.items() if r!='R42'],
                                    reader=lambda p,f:next(responses),folder=Path(tmp)/'step')
        self.assertEqual(result['status'],'draft_requires_semantic_and_domain_review')
        self.assertIn('requirement_baseline_revision_mismatch',[x['code'] for x in result['attempts'][0]['check']['issues']])


if __name__=='__main__':unittest.main()
