import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import mcp_access_diagnostics as d

class DiagnosticsTests(unittest.TestCase):
    def test_server_ids_unique_and_header_safe(self):
        ids = {d.new_request_id() for _ in range(100)}
        self.assertEqual(len(ids),100)
        self.assertTrue(all(d.valid_request_id(x) for x in ids))
        for x in [None,42,'bad\r\nAuthorization: secret','mcp-'+'f'*33]:
            self.assertFalse(d.valid_request_id(x))

    def test_all_reasons_indistinguishable_publicly(self):
        rid=d.new_request_id(); bodies=[]
        for reason in d.REASONS:
            logs=[];out=d.deny(reason,logs.append,rid)
            self.assertFalse(out['allowed']);self.assertEqual(out['http_status'],401)
            self.assertTrue(out['audit_written']);self.assertEqual(json.loads(logs[0])['reason'],reason)
            bodies.append(out['body'])
        self.assertTrue(all(b==bodies[0] for b in bodies))

    def test_unknown_payload_is_not_logged(self):
        logs=[];out=d.deny({'Authorization':'Bearer SECRET','body':'customer text'},logs.append)
        self.assertNotIn('SECRET',logs[0]);self.assertNotIn('customer',logs[0])
        self.assertEqual(json.loads(logs[0])['reason'],'registry_unavailable')
        self.assertEqual(set(json.loads(logs[0])),{'event','request_id','reason','http_status','at'})

    def test_log_failure_remains_denied_without_exception_leak(self):
        def fail(line):raise RuntimeError('secret filesystem token')
        out=d.deny('revoked',fail)
        self.assertFalse(out['allowed']);self.assertFalse(out['audit_written'])
        self.assertNotIn('filesystem',json.dumps(out))
        self.assertEqual(out['headers']['X-Request-ID'],out['body']['request_id'])

    def test_invalid_optional_id_replaced(self):
        out=d.deny('unknown',request_id='customer token\n')
        self.assertTrue(d.valid_request_id(out['body']['request_id']))
        self.assertNotIn('customer token',json.dumps(out))
        with self.assertRaises(ValueError):d.public_denial('bad')

if __name__=='__main__':unittest.main()
