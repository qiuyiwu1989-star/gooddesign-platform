import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from method_application_adapter import prepare_request, application_envelope


class ApplicationAdapterTests(unittest.TestCase):
    def setUp(self):
        self.request={'task_id':'client-1','title':'hold a part','scenario_type':'customer_supplied','needs':['hold safely'],'unknowns':['force']}

    def test_binding_revision_and_unverified_scope(self):
        first=prepare_request(self.request,'clamp','bench only')
        self.assertEqual(first['status'],'prepared_unverified_client_context')
        self.assertFalse(first['expert_certified'])
        changed=copy.deepcopy(self.request);changed['needs'].append('release')
        second=prepare_request(changed,'clamp','bench only')
        self.assertEqual(first['task']['task_id'],second['task']['task_id'])
        self.assertNotEqual(first['task']['revision'],second['task']['revision'])
        result=application_envelope({'task':first['task'],'run_id':'run-1','revision':0,'submissions':[]})
        self.assertEqual(result['source_request']['sha256'],first['source_request_sha256'])
        self.assertFalse(result['writeback_performed'])
        self.assertFalse(result['engineering_validated'])

    def test_missing_scope_boundary_and_self_certification_rejected(self):
        for mutation in ({'scenario_type':'verified'},{'expert_certified':True},{'needs':[]}):
            request={**self.request,**mutation}
            with self.assertRaises(ValueError):prepare_request(request,'clamp','bench')
        with self.assertRaises(ValueError):prepare_request(self.request,'','bench')
        with self.assertRaises(ValueError):application_envelope({'task':{}})


if __name__=='__main__':unittest.main()
