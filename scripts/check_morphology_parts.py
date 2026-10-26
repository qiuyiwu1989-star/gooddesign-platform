"""ML-008 deterministic fixtures: never report injected readers as real inference."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from method_workbench_morphology import inputs,progress,generate_function,assemble,validate_combinations,PartGenerationError

ROOT=Path(__file__).resolve().parents[1]

def state():
    return {'task':{'task_id':'fixture','revision':'r1','object':'fixture object','desired_outcome':'test only','boundary':'fixture'},
        'plan':{'nodes':[{'node_id':'R17','contract_sha256':'fixture-contract','method_content_sha256':'fixture-method'}],'implementation_hashes':{}},
        'submissions':[{'artifact':{'type':'ProblemBrief','payload':{'requirements':[]}}},
                       {'artifact':{'type':'FunctionModel','payload':{'functions':[{'id':'F1','verb_object':'function one'},{'id':'F2','verb_object':'function two'}],'flows':[]}}}]}

class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=ROOT/'output/method-workbench-check')
        self.s=state()
    def tearDown(self):self.tmp.cleanup()
    def part(self,fid):
        def fake(prompt,folder):
            return {'function_id':fid,'alternatives':[{'principle':'fixture alternative A','conditions':['unverified fixture'],'evidence_refs':[]},{'principle':'fixture alternative B','conditions':['unverified fixture'],'evidence_refs':[]}],'unknowns':['fixture unknown']}
        return generate_function(self.s,[],fid,self.tmp.name,reader=fake)
    def test_fragment_id_and_progress(self):
        p=self.part('F1');q=self.part('F1')
        self.assertEqual([o['id'] for o in p['options']],[o['id'] for o in q['options']])
        jobs=[{'state':'part','result':p}]
        m=progress(self.s,[],jobs)
        self.assertEqual(m['ready'],1);self.assertEqual(m['next_function'],'F2')
        self.assertEqual(p['model_mode'],'injected_reader_not_real_model')
    def test_input_changes_invalidate_cache(self):
        jobs=[{'state':'part','result':self.part('F1')}]
        self.s['task']['boundary']='changed'
        self.assertEqual(progress(self.s,[],jobs)['ready'],0)
    def test_missing_parts_fail_before_model(self):
        with self.assertRaisesRegex(ValueError,'片段缺失'):
            assemble(self.s,[],{'F1':self.part('F1')},self.tmp.name,reader=lambda *a:self.fail('must not call model'))
    def test_assemble_complete_fixture(self):
        parts={fid:self.part(fid) for fid in ['F1','F2']}
        def fake(prompt,folder):
            return {'combinations':[{'id':'C1','option_ids':[parts[fid]['options'][0]['id'] for fid in ['F1','F2']],'status':'unknown','reason':'fixture combo A'},{'id':'C2','option_ids':[parts[fid]['options'][1]['id'] for fid in ['F1','F2']],'status':'unknown','reason':'fixture combo B'}],'unknowns':['fixture unknown']}
        result=assemble(self.s,[],parts,self.tmp.name,reader=fake)
        self.assertEqual(result['artifact']['payload']['function_ids'],['F1','F2'])
        self.assertEqual(len(result['artifact']['payload']['options']),4)
        self.assertFalse(result['expert_certified'])
    def test_duplicate_and_missing_function_combos(self):
        options=[{'id':'A','function_id':'F1'},{'id':'B','function_id':'F2'},{'id':'D','function_id':'F1'}]
        with self.assertRaises(ValueError):validate_combinations([{'id':'C1','option_ids':['A','D'],'status':'unknown'}],options,['F1','F2'])
        with self.assertRaises(ValueError):validate_combinations([{'id':'C1','option_ids':['A','B'],'status':'compatible'}],options,['F1','F2'])
        with self.assertRaises(ValueError):validate_combinations([{'id':'C1','option_ids':['A','B'],'status':'unknown'},{'id':'C2','option_ids':['A','B'],'status':'unknown'}],options,['F1','F2'])
    def test_unknown_evidence_and_part_stamp(self):
        parts={fid:self.part(fid) for fid in ['F1','F2']}
        parts['F1']['options'][0]['evidence_refs']=['missing']
        with self.assertRaisesRegex(ValueError,'未知证据'):assemble(self.s,[],parts,self.tmp.name,reader=lambda *a:self.fail('no model'))
        parts['F1']['input_fingerprint']='old'
        with self.assertRaisesRegex(ValueError,'版本已改变'):assemble(self.s,[],parts,self.tmp.name,reader=lambda *a:self.fail('no model'))

    def test_provider_error_classification_preserves_audit(self):
        def fake(prompt,folder):
            (folder/'model-stderr.log').write_text('fixture HTTP status 429; retrying transport')
            (folder/'termination.json').write_text(json.dumps({'reason':'timeout'}))
            raise TimeoutError('fixture only')
        with self.assertRaises(PartGenerationError) as result:
            generate_function(self.s,[],'F1',self.tmp.name,reader=fake)
        record=result.exception.record
        self.assertEqual(record['transport_status_codes'],[429])
        self.assertEqual(record['local_termination'],'timeout')
        self.assertFalse(record['application_retry_started'])
        self.assertEqual(record['model_mode'],'injected_reader_not_real_model')

if __name__=='__main__':unittest.main(verbosity=2)
