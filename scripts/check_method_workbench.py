"""ML-006 meaningful persistence, CAS, HTTP and isolation checks; external-disk temp DB."""
import copy
import json
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from urllib.parse import quote
from method_workbench_server import ROOT, make_server


class WorkspaceChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        folder = ROOT / 'output/method-workbench-check'
        folder.mkdir(exist_ok=True)
        cls.tmp = tempfile.TemporaryDirectory(dir=folder)
        cls.db = Path(cls.tmp.name) / 'test.sqlite'
        cls.launch()

    @classmethod
    def launch(cls):
        cls.server = make_server(0, cls.db)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = 'http://127.0.0.1:' + str(cls.server.server_port)
        cls.token = cls.request('/api/session')[1]['csrf']

    @classmethod
    def request(cls, path, body=None, headers=None):
        h = {'Content-Type': 'application/json'}
        if body is not None:
            h['X-CSRF-Token'] = cls.token
        h.update(headers or {})
        req = Request(cls.base + quote(path, safe='/'), data=json.dumps(body).encode() if body is not None else None, headers=h)
        try:
            response = urlopen(req)
        except HTTPError as e:
            response = e
        raw = response.read()
        return response.status, json.loads(raw) if 'application/json' in response.headers.get('Content-Type', '') else raw

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.tmp.cleanup()

    def draft(self):
        d = copy.deepcopy(self.request('/api/demands/RUBBER-20261026')[1]['data'])
        d.update(id='TEST-' + self._testMethodName, expected_revision=0)
        return d

    def test_01_catalog_and_content(self):
        code, catalog = self.request('/api/methods')
        self.assertEqual(code, 200)
        self.assertEqual(len(catalog['methods']), 64)
        self.assertEqual(sum(m['executable_contract'] for m in catalog['methods']), 6)
        for m in catalog['methods']:
            self.assertEqual(self.request('/library/' + m['page'])[0], 200)
        for path in ['/library/library.css', '/reports/需求报告.html', '/reports/创新方案报告.html', '/reports/推理记录.html', '/']:
            self.assertEqual(self.request(path)[0], 200)

    def test_02_save_history_and_conflict(self):
        d = self.draft()
        a = self.request('/api/demands', d)
        self.assertEqual(a[0], 201)
        d.update(expected_revision=1, problem='改写问题')
        self.assertEqual(self.request('/api/demands', d)[0], 201)
        self.assertEqual(self.request('/api/demands', d)[0], 409)
        old = self.request('/api/demands/' + d['id'] + '/1')[1]
        self.assertNotEqual(old['data']['problem'], d['problem'])
        self.assertEqual(len(old['history']), 2)
        self.assertFalse(old['data']['approved'])

    def test_03_restart_and_restore_history_as_new(self):
        d = self.draft()
        self.request('/api/demands', d)
        self.server.shutdown()
        self.server.server_close()
        self.launch()
        saved = self.request('/api/demands/' + d['id'])[1]
        self.assertEqual(saved['revision'], 1)
        restored = saved['data']
        restored['expected_revision'] = 1
        self.assertEqual(self.request('/api/demands', restored)[1]['revision'], 2)
        self.assertEqual(self.request('/api/demands/' + d['id'] + '/1')[1]['revision'], 1)

    def test_04_origin_host_csrf(self):
        d = self.draft()
        self.assertEqual(self.request('/api/demands', d, {'Origin': 'https://evil.example'})[0], 403)
        self.assertEqual(self.request('/api/demands', d, {'X-CSRF-Token': 'bad'})[0], 403)
        self.assertEqual(self.request('/api/demands', headers={'Host': 'evil.example'})[0], 403)
        self.assertEqual(self.request('/api/session', headers={'Sec-Fetch-Site': 'cross-site'})[0], 403)

    def test_05_private_path_isolation(self):
        for p in ['/reports/private/cases.json', '/api/../AGENTS.md', '/library/../目录.json', '/reports/需求包.json', '/scripts/method_engine.py']:
            self.assertEqual(self.request(p)[0], 404)

    def test_06_validation(self):
        d = self.draft()
        d['requirements'][1]['id'] = d['requirements'][0]['id']
        self.assertEqual(self.request('/api/demands', d)[0], 400)
        d = self.draft()
        d['selected_methods'] = ['MISSING']
        self.assertEqual(self.request('/api/demands', d)[0], 400)
        d = self.draft()
        d['requirements'][0]['hard_proposal'] = 'true'
        self.assertEqual(self.request('/api/demands', d)[0], 400)

    def test_07_no_approval_or_false_lineage(self):
        d = self.draft()
        d['approved'] = True
        d['baseline_packet_sha256'] = 'fake'
        d['requirements'][0]['status'] = 'customer_approved'
        result = self.request('/api/demands', d)[1]['data']
        self.assertFalse(result['approved'])
        self.assertNotIn('baseline_packet_sha256', result)
        self.assertEqual(result['requirements'][0]['status'], 'research_proposed_not_customer_confirmed')

    def test_08_actual_mcp_case_and_run(self):
        code, found = self.request('/api/cases/search', {'query': '采样'})
        self.assertEqual(code, 200)
        self.assertIn('2025-00', [r['id'] for r in found['data']])
        d = self.draft()
        self.assertEqual(self.request('/api/demands', d)[0], 201)
        request = {'id': d['id'], 'revision': 1}
        code, run = self.request('/api/runs', request)
        self.assertEqual(code, 201)
        self.assertEqual(len(run['created']['plan']['nodes']), 6)
        self.assertFalse(run['automatic_generation'])
        again = self.request('/api/runs', request)
        self.assertEqual(again[0], 200)
        self.assertEqual(again[1]['created']['run_id'], run['created']['run_id'])
        self.assertEqual(self.request('/api/run/' + d['id'])[1]['demand_sha256'], run['demand_sha256'])
        # Verify the actual engine persistence contains the complete frozen demand.
        import sqlite3
        with sqlite3.connect(self.db.parent / 'engine.sqlite') as db:
            row = db.execute('SELECT task FROM runs WHERE id=?', (run['created']['run_id'],)).fetchone()
        task = json.loads(row[0])
        self.assertEqual(len(task['demand_snapshot']['requirements']), 15)
        self.assertEqual(task['demand_snapshot']['problem'], d['problem'])

    def test_09_execution_rejects_bad_draft_without_model(self):
        import time
        d=self.draft()
        self.assertEqual(self.request('/api/demands',d)[0],201)
        self.assertEqual(self.request('/api/runs',{'id':d['id'],'revision':1})[0],201)
        body={'id':d['id'],'revision':1,'action':'submit','artifact':{}}
        code,job=self.request('/api/execute',body)
        self.assertEqual(code,202)
        self.server.shutdown()
        self.server.server_close()
        self.launch()
        deadline=time.time()+15
        while time.time()<deadline:
            code,state=self.request('/api/execution/'+d['id'])
            latest=state['jobs'][-1]
            if latest['state'] not in ('queued','running'):break
            time.sleep(.2)
        self.assertEqual(latest['state'],'blocked')
        self.assertEqual(state['state']['revision'],0)
        self.assertEqual(latest['result']['issues'][0]['code'],'baseline_requirement_missing')
        self.assertEqual(self.request('/api/execution/note',{'id':d['id'],'revision':1,'text':'test note, not expert review'})[0],201)
        self.assertEqual(len(self.request('/api/execution/'+d['id'])[1]['notes']),1)
        self.assertEqual(self.request('/api/execute',body,{'X-CSRF-Token':'wrong'})[0],403)

    def test_10_selected_evidence_preview_is_not_attachment(self):
        d=self.draft()
        self.assertEqual(self.request('/api/demands',d)[0],201)
        self.assertEqual(self.request('/api/runs',{'id':d['id'],'revision':1})[0],201)
        body={'id':d['id'],'revision':1,'project_id':'2025-00','source_id':'Sc249f11de5b7c8a4','offset':2,'max_chars':400}
        code,preview=self.request('/api/evidence/preview',body)
        self.assertEqual(code,200)
        self.assertEqual(preview['offset'],2)
        self.assertEqual(preview['evidence'][0]['chunk_id'],'B0003')
        self.assertLessEqual(len(preview['evidence'][0]['text']),400)
        self.assertEqual(len(self.request('/api/execution/'+d['id'])[1]['evidence']),0)
        code,saved=self.request('/api/evidence/attach',{'id':d['id'],'revision':1,'preview_id':preview['preview_id']})
        self.assertEqual(code,200)
        self.assertEqual(saved['evidence'][0]['text'],preview['evidence'][0]['text'])
        body['max_chars']=100
        preview2=self.request('/api/evidence/preview',body)[1]
        self.assertNotEqual(preview2['evidence'][0]['id'],preview['evidence'][0]['id'])
        self.assertEqual(self.request('/api/evidence/attach',{'id':d['id'],'revision':1,'preview_id':'wrong'})[0],400)
        body['offset']=-1
        self.assertEqual(self.request('/api/evidence/preview',body)[0],400)
        body['offset']=2;body['chunks_sha256']='0'*64
        self.assertEqual(self.request('/api/evidence/preview',body)[0],400)


if __name__ == '__main__':
    unittest.main(verbosity=2)
