import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from method_engine import Engine, ROOT
from method_engine_contracts import META, contract
from method_engine_store import Store
from method_engine_fixtures import teaching_task, teaching_artifacts
from method_case_adapter import normalize


def task():
    return dict(task_id='T1', revision='t1', object='fixture tool', desired_outcome='hold safely', boundary='bench only', stage='frame')


def brief():
    return dict(artifact_id='A1', revision='a1', task_id='T1', task_revision='t1', type='ProblemBrief', scope='bench only',
                conditions=[], evidence_refs=[], payload=dict(actor='operator', object='tool', boundary='bench only', desired_outcome='hold',
                requirements=[dict(id='Q1', text='hold', hard=True, acceptance='to be confirmed', status='proposed', evidence_refs=[])],
                conditions=[], unknowns=['force']))


class EngineTests(unittest.TestCase):
    def setUp(self): self.engine=Engine()

    def test_registry_and_all_schemas(self):
        from jsonschema import Draft202012Validator
        for rid in META:
            Draft202012Validator.check_schema(contract(rid)['schema'])
            self.assertTrue(self.engine.get(rid)['execution_available'])
        self.assertFalse(self.engine.get('R35')['execution_available'])

    def test_plan_graph_and_reuse(self):
        plan=self.engine.plan(task())
        self.assertEqual([n['node_id'] for n in plan['nodes']],['R48','R14','R17','R36','R44','R42'])
        reused=self.engine.plan(task(),artifacts=[brief()])
        self.assertEqual(reused['nodes'][0]['node_id'],'R14')
        self.assertEqual(reused['nodes'][-1]['bindings'][0]['source']['artifact_id'],'A1')

    def test_missing_task_and_bad_input_block(self):
        self.assertEqual(self.engine.plan({})['status'],'blocked')
        a=brief();a['task_revision']='old'
        self.assertEqual(self.engine.plan(task(),artifacts=[a])['status'],'blocked')

    def test_schema_not_content_certification(self):
        result=self.engine.check_artifact('R48',brief(),task=task())
        self.assertEqual(result['status'],'structure_and_declared_consistency_passed')
        self.assertFalse(result['engineering_validated'])
        a=brief();a['payload']['requirements'][0]['status']='confirmed'
        self.assertEqual(self.engine.check_artifact('R48',a)['status'],'blocked')
        a=brief();a['payload']['unexpected']='result'
        self.assertEqual(self.engine.check_artifact('R48',a)['status'],'blocked')

    def test_evidence_hash_and_reference(self):
        a=brief();a['evidence_refs']=['E1']
        ev=dict(id='E1',server='case',project_id='P1',source_id='S1',source_revision='s1',locator='p1',text='source',text_sha256=hashlib.sha256(b'source').hexdigest())
        self.assertNotEqual(self.engine.check_artifact('R48',a,[ev])['status'],'blocked')
        ev['text']='changed';self.assertEqual(self.engine.check_artifact('R48',a,[ev])['status'],'blocked')
        self.assertEqual(self.engine.check_artifact('R48',a,[])['status'],'blocked')

    def test_handoff_type_and_revision(self):
        self.assertEqual(self.engine.check_handoff('R14',brief(),task())['status'],'compatible_input_type')
        self.assertEqual(self.engine.check_handoff('R48',brief(),task())['status'],'blocked')
        self.assertEqual(self.engine.check_handoff('R36',brief(),task())['remaining_required_types'],['ConceptSet'])

    def test_store_restart_cas_and_idempotency(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'output') as temp:
            path=Path(temp)/'runs.db';store=Store(path)
            run=store.create(task());rid=run['run_id']
            saved=store.submit(rid,0,'key1','R48',brief())
            self.assertEqual(saved['revision'],1)
            restarted=Store(path)
            self.assertEqual(restarted.get(rid)['revision'],1)
            self.assertEqual(restarted.submit(rid,0,'key1','R48',brief()),saved)
            a=brief();a['scope']='changed'
            with self.assertRaisesRegex(ValueError,'idempotency'):restarted.submit(rid,1,'key1','R48',a)
            with self.assertRaisesRegex(ValueError,'stale'):restarted.submit(rid,0,'key2','R48',brief())
            with self.assertRaisesRegex(ValueError,'dependencies'):restarted.submit(rid,1,'key3','R17',brief())

    def test_invalid_submission_does_not_advance(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'output') as temp:
            store=Store(Path(temp)/'runs.db');run=store.create(task())
            a=brief();a['payload']['requirements'][0]['status']='confirmed'
            self.assertEqual(store.submit(run['run_id'],0,'k','R48',a)['status'],'blocked')
            self.assertEqual(store.get(run['run_id'])['revision'],0)

    def test_six_teaching_artifacts(self):
        for rid,a in teaching_artifacts().items():
            with self.subTest(method=rid):
                self.assertNotEqual(self.engine.check_artifact(rid,a,task=teaching_task())['status'],'blocked')

    def test_model_and_combination_negative_cases(self):
        fixtures=teaching_artifacts()
        a=copy.deepcopy(fixtures['R14']);a['payload']['flows'][0]['to_function']='F-absent'
        self.assertEqual(self.engine.check_artifact('R14',a)['status'],'blocked')
        a=copy.deepcopy(fixtures['R17']);a['payload']['combinations'][0]['option_ids']=['O1']
        self.assertEqual(self.engine.check_artifact('R17',a)['status'],'blocked')
        a=copy.deepcopy(fixtures['R17']);a['payload']['combinations'][0]['status']='candidate';a['payload']['compatibility'][0]['status']='incompatible'
        self.assertEqual(self.engine.check_artifact('R17',a)['status'],'blocked')

    def test_unknown_hard_gate_and_fabricated_plan_result(self):
        fixtures=teaching_artifacts()
        a=copy.deepcopy(fixtures['R36']);a['payload']['recommendations']=['C1']
        self.assertEqual(self.engine.check_artifact('R36',a)['status'],'blocked')
        for rid in ('R44','R42'):
            a=copy.deepcopy(fixtures[rid]);a['payload']['measured_success']=True
            self.assertEqual(self.engine.check_artifact(rid,a)['status'],'blocked')
        a=copy.deepcopy(fixtures['R42']);a['payload']['uncovered_requirements']=['Q1']
        self.assertIn('uncovered_requirements_already_in_matrix',[x['code'] for x in self.engine.check_artifact('R42',a)['issues']])

    def test_duplicate_artifact_selection_is_not_silent(self):
        self.assertEqual(self.engine.plan(task(),artifacts=[brief(),brief()])['status'],'blocked')

    def test_missing_solver_and_result_level_are_not_ignored(self):
        t=task();t['required_capabilities']=['structural_solver']
        self.assertEqual(self.engine.plan(t)['status'],'blocked')
        t=task();t['delivery_level']='validated'
        self.assertEqual(self.engine.match(t)['recommended'],[])

    def test_cross_method_baseline_and_coverage(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'output') as temp:
            store=Store(Path(temp)/'runs.db');run=store.create(teaching_task());fixtures=teaching_artifacts()
            revision=0
            for rid,a in fixtures.items():
                if rid=='R42':break
                result=store.submit(run['run_id'],revision,rid,rid,a);revision=result['revision']
            a=copy.deepcopy(fixtures['R42']);a['payload']['requirements_revision']='old'
            self.assertEqual(store.submit(run['run_id'],revision,'wrong-rev','R42',a)['status'],'blocked')
            a=copy.deepcopy(fixtures['R42']);a['payload']['matrix'][0]['requirement_id']='Q-unknown'
            self.assertEqual(store.submit(run['run_id'],revision,'wrong-id','R42',a)['status'],'blocked')
            self.assertEqual(store.submit(run['run_id'],revision,'correct','R42',fixtures['R42'])['revision'],6)

    def test_comparison_cannot_omit_or_downgrade_requirement_gates(self):
        fixtures=teaching_artifacts();upstream=[fixtures[r] for r in ('R48','R14','R17')]
        for change,code in [({'requirement_ids':[]},'comparison_hard_or_unresolved_requirement_not_gated:Q1'),
                            ({'hard':False},'comparison_hard_or_unresolved_requirement_not_gated:Q1'),
                            ({'requirement_ids':['invented']},'comparison_unknown_requirement_reference')]:
            artifact=copy.deepcopy(fixtures['R36']);artifact['payload']['criteria'][0].update(change)
            checked=self.engine.check_output('R36',artifact,teaching_task(),upstream)
            self.assertIn(code,[x['code'] for x in checked['issues']])
            self.assertEqual(self.engine.plan(teaching_task(),artifacts=upstream+[artifact])['status'],'blocked')
        artifact=copy.deepcopy(fixtures['R36']);artifact['payload']['requirements_revision']='old'
        self.assertIn('comparison_requirement_baseline_revision_mismatch',[x['code'] for x in self.engine.check_output('R36',artifact,teaching_task(),upstream)['issues']])
        # Even a locally passing comparison cannot rank while source hardness is unresolved.
        upstream=copy.deepcopy(upstream);upstream[0]['payload']['requirements'][0]['hard']=None
        upstream[2]['payload']['combinations'][0]['status']='candidate'
        upstream[2]['payload']['compatibility'][0]['status']='compatible'
        ev=dict(id='E1',server='case',project_id='P1',source_id='S1',source_revision='s1',locator='p1',text='source',text_sha256=hashlib.sha256(b'source').hexdigest())
        artifact=copy.deepcopy(fixtures['R36']);artifact['payload']['recommendations']=['C1']
        artifact['payload']['judgments'][0].update(value='pass',evidence_refs=['E1'])
        self.assertNotEqual(self.engine.check_artifact('R36',artifact,[ev])['status'],'blocked')
        checked=self.engine.check_output('R36',artifact,teaching_task(),upstream,[ev])
        self.assertIn('comparison_requirement_hardness_unresolved:Q1',[x['code'] for x in checked['issues']])

    def test_case_adapter_revision_and_truncation(self):
        response={'source_id':'S1','source_sha256':'file-hash','chunks_sha256':'chunk-file-hash','revision':'current_ingest',
                  'read_scope':'partial','data':[{'id':'B1','text':'x'*100,'locator':'p1'}]}
        result=normalize('P1','S1',response,max_chars=50)['evidence'][0]
        self.assertTrue(result['truncated']);self.assertEqual(result['source_revision'],'chunk-file-hash')
        self.assertEqual(result['support_review'],'not_reviewed')
        with self.assertRaises(ValueError):normalize('P1','wrong',response)
        self.assertEqual(normalize('P1','S1',{'requires_chunks_sha256':True})['status'],'needs_text_revision_choice')


if __name__=='__main__':unittest.main()
