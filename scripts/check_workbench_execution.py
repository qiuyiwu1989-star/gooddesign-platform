"""ML-007 durable job and baseline gate checks without spending model quota."""
import json
import tempfile
import time
import unittest
from pathlib import Path
from method_workbench_execution import Execution, ROOT, alignment

class Checks(unittest.TestCase):
    def setUp(self):
        folder=ROOT/'output/method-workbench-check'
        folder.mkdir(exist_ok=True)
        self.tmp=tempfile.TemporaryDirectory(dir=folder)
        self.path=Path(self.tmp.name)/'execution.sqlite'
        self.store=Execution(self.path)
    def tearDown(self):self.tmp.cleanup()
    def test_single_active_and_persistence(self):
        r={'run_id':'run-test','method':'R48','action':'propose'}
        j=self.store.enqueue(r,spawn=False)
        with self.assertRaises(FileExistsError):self.store.enqueue(r,spawn=False)
        restored=Execution(self.path)
        self.assertEqual(restored.listing('run-test')[0]['state'],'queued')
        restored.finish(j['job_id'],'failed',{'error':'test fixture failure, not real model output'})
        self.assertNotEqual(restored.enqueue(r,spawn=False)['job_id'],j['job_id'])
    def test_interruption_no_auto_retry(self):
        j=self.store.enqueue({'run_id':'run-test','method':'R48','action':'propose'},spawn=False)
        with self.store.connect() as db:db.execute('UPDATE jobs SET updated=?',(time.time()-400,))
        self.assertEqual(self.store.listing('run-test')[0]['state'],'interrupted')
        self.assertEqual(len(self.store.listing('run-test')),1)
    def test_alignment_preserves_baseline(self):
        task={'demand_snapshot':{'requirements':[{'id':'N01','hard_proposal':None,'acceptance_proposal':'original'}]}}
        a={'payload':{'requirements':[{'id':'N01','hard':None,'status':'proposed','acceptance':'original'}]}}
        self.assertEqual(alignment(task,'R48',a),[])
        a['payload']['requirements'][0]['hard']=False
        self.assertEqual(alignment(task,'R48',a)[0]['code'],'baseline_requirement_hardness_changed')
        a['payload']['requirements']=[]
        self.assertEqual(alignment(task,'R48',a)[0]['code'],'baseline_requirement_missing')
    def test_acceptance_and_approval_cannot_change(self):
        task={'demand_snapshot':{'requirements':[{'id':'N01','hard_proposal':True,'acceptance_proposal':'original'}]}}
        a={'payload':{'requirements':[{'id':'N01','hard':True,'status':'confirmed','acceptance':'rewritten'}]}}
        self.assertEqual(len(alignment(task,'R48',a)),2)
    def test_evidence_immutable_during_active_job(self):
        self.store.enqueue({'run_id':'run-test','method':'R48','action':'propose'},spawn=False)
        with self.assertRaises(FileExistsError):self.store.attach('run-test',[])

    def test_preview_scope_and_restart(self):
        ident=self.store.preview('run-test',[{'text':'frozen test excerpt'}])
        restored=Execution(self.path)
        self.assertEqual(restored.preview('run-test',ident=ident)[0]['text'],'frozen test excerpt')
        with self.assertRaises(ValueError):restored.preview('other-run',ident=ident)

    def test_exact_excerpt_dedup_and_identity_conflict(self):
        import hashlib
        e={'id':'E1','project_id':'fixture','source_id':'S1','source_revision':'r1','chunk_id':'B1','text':'fixture excerpt','text_sha256':hashlib.sha256(b'fixture excerpt').hexdigest()}
        self.assertEqual(len(self.store.attach('run-test',[e])),1)
        duplicate=dict(e,id='E2')
        self.assertEqual(len(self.store.attach('run-test',[duplicate])),1)
        changed=dict(e,text='changed',text_sha256=hashlib.sha256(b'changed').hexdigest())
        with self.assertRaises(ValueError):self.store.attach('run-test',[changed])

if __name__=='__main__':unittest.main(verbosity=2)
