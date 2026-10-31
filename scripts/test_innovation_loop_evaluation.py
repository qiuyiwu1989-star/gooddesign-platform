import copy
import unittest
from innovation_loop_evaluation import ARMS, validate_protocol, build_run_matrix, audit_completeness

def fixture():
    return dict(schema_version='0.1.0', id='ML024-P1', revision=1, status='draft',
        tasks=[dict(id=i, input_sha256=None, input_status='research_proposal') for i in ['rubber','gear','polish']],
        arms=copy.deepcopy(ARMS), replicates=2, failure_policy='retain_all_no_best_of', network_allowed=False,
        model=None,budget=None,reviewers=None,business_effect_threshold=None,randomization_seed=None,
        missing_reason='Actual inputs, model, budget and reviewers not frozen')

class EvaluationTests(unittest.TestCase):
    def test_draft_not_ready(self):
        self.assertFalse(validate_protocol(fixture())['execution_ready'])
    def test_cannot_freeze_pending(self):
        p=fixture();p['status']='frozen'
        with self.assertRaises(ValueError):validate_protocol(p)
    def test_matrix(self):
        m=build_run_matrix(fixture());self.assertEqual(len(m['runs']),24)
        self.assertEqual(len({x['run_id'] for x in m['runs']}),24)
        self.assertEqual(m['runs'][0]['additional_materials'],[])
    def test_missing_not_hidden(self):
        self.assertEqual(len(audit_completeness(fixture(),[])['missing']),24)
    def test_all_failed_still_accounted(self):
        p=fixture();m=build_run_matrix(p)
        rows=[dict(run_id=r['run_id'],protocol_sha256=m['protocol_sha256'],status='failed',failure_reason='fixture failure') for r in m['runs']]
        a=audit_completeness(p,rows);self.assertTrue(a['complete']);self.assertEqual(a['failed'],24)
        self.assertFalse(a['effectiveness_established'])
        rows.append(rows[0]);self.assertFalse(audit_completeness(p,rows)['complete'])
    def test_wrong_protocol_and_empty_success(self):
        a=audit_completeness(fixture(),[dict(run_id='ML024-P1:rubber:A:1',status='succeeded',protocol_sha256='wrong')])
        self.assertEqual(len(a['errors']),2)
    def test_invalid_design(self):
        for key,value in [('replicates',True),('network_allowed',True),('arms',{})]:
            p=fixture();p[key]=value
            with self.assertRaises(ValueError):validate_protocol(p)
    def test_does_not_mutate(self):
        p=fixture();before=copy.deepcopy(p);build_run_matrix(p);self.assertEqual(p,before)

if __name__=='__main__':unittest.main()

class AnonymousTests(unittest.TestCase):
    def test_separation_reproducible(self):
        import json
        from innovation_loop_evaluation import build_anonymous_package
        rows=[dict(run_id='secret-A',text='Route one',source_path='/private/secret.md',source_filename='secret.md'),dict(run_id='secret-B',text='Route two')]
        p=build_anonymous_package(rows,42)
        self.assertEqual(p,build_anonymous_package(rows,42))
        public=json.dumps(p['reviewer_package'])
        self.assertNotIn('secret',public);self.assertNotIn('seed',public)
        self.assertEqual(len(p['private_mapping']['mapping']),2)
    def test_reject_leaks_and_duplicates(self):
        from innovation_loop_evaluation import build_anonymous_package
        for rows in [[dict(run_id='x',text='/Users/name/private.md')],[dict(run_id='x',text='body'),dict(run_id='x',text='body')],[dict(run_id='x',text='secret.md',source_filename='secret.md')]]:
            with self.assertRaises(ValueError):build_anonymous_package(rows,1)

class FreezeGateTests(unittest.TestCase):
    def test_empty_nonnull_not_ready(self):
        p=fixture();p.update(status='frozen',model={},budget={},reviewers=[],business_effect_threshold='x',randomization_seed=1)
        for t in p['tasks']:t['input_sha256']='a'*64
        with self.assertRaises(ValueError):validate_protocol(p)
    def test_bad_id_revision_sha(self):
        for key,value in [('id',1),('revision',True)]:
            p=fixture();p[key]=value
            with self.assertRaises(ValueError):validate_protocol(p)
        p=fixture();p['tasks'][0]['input_sha256']='bad'
        with self.assertRaises(ValueError):validate_protocol(p)

class ArtifactTests(unittest.TestCase):
    def test_bytes_paths_and_hash(self):
        import hashlib,tempfile
        from pathlib import Path
        from innovation_loop_evaluation import audit_artifacts
        with tempfile.TemporaryDirectory(dir='output/innovation-loop-024/evaluation') as folder:
            p=fixture();m=build_run_matrix(p);root=Path(folder);(root/'x.md').write_text('test')
            row=dict(run_id=m['runs'][0]['run_id'],protocol_sha256=m['protocol_sha256'],status='succeeded',output_ref='x.md',output_sha256=hashlib.sha256(b'test').hexdigest())
            self.assertTrue(audit_artifacts(p,[row],root)['artifact_bytes_verified'])
            for ref,sha in [('../x.md',row['output_sha256']),('/tmp/x',row['output_sha256']),('absent.md',row['output_sha256']),('x.md','b'*64)]:
                bad=dict(row,output_ref=ref,output_sha256=sha)
                self.assertFalse(audit_artifacts(p,[bad],root)['artifact_bytes_verified'])
            (root/'link.md').symlink_to(root.resolve()/'x.md')
            self.assertFalse(audit_artifacts(p,[dict(row,output_ref='link.md')],root)['artifact_bytes_verified'])
    def test_reviewers_need_unique_and_non_author(self):
        p=fixture();p.update(status='frozen',model={'id':'m','version':'1'},budget={'max_output_chars':1,'max_seconds':1,'max_tokens':1},reviewers=[{'id':'r','role':'AI','independence_statement':'test','is_author':False}]*2,business_effect_threshold='descriptive',randomization_seed=1)
        for t in p['tasks']:t['input_sha256']='a'*64
        with self.assertRaises(ValueError):validate_protocol(p)
        p['reviewers'][1]=dict(p['reviewers'][0],id='r2',is_author=True)
        with self.assertRaises(ValueError):validate_protocol(p)
        p['reviewers'][1]['is_author']=False
        self.assertTrue(validate_protocol(p)['execution_ready'])
