"""RC-08/11：推理画布状态服务与 GDRP 导出。"""
import http.client
import json
import os
import tempfile
import threading
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class CanvasStateAndGDRPTests(unittest.TestCase):
    def setUp(self):
        import sys
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import reasoning_canvas_server as srv
        self.srv = srv
        self.tmp = tempfile.TemporaryDirectory()
        self.db = os.path.join(self.tmp.name, "canvas.sqlite3")
        self.state = {
            "selected": "n6",
            "statuses": {"n1": "done", "n2": "done", "n3": "done", "n4": "done", "n5": "review", "n6": "doing", "n7": "todo"},
            "evMarks": {"K1": "trust", "K2": "doubt"},
            "killed": {"B": True},
            "redteam": ["accept", None, "reject", None, None],
            "redteamReasons": ["", "", "证据不能外推", "", ""],
            "priorities": {"A": "优先做台架原型"},
            "reasons": {"main": "先验证门槛"},
            "notes": {"n6": [{"who": "我", "text": "先不上活树", "time": "11/9 10:00"}]},
            "committed": False,
            "intent": [],
            "subproblems": [],
            "searchLog": [],
            "extraEvidence": [],
            "engineDecisions": {},
            "engineConfirmed": [],
            "positions": {},
            "flow": {"runs": 1, "log": [{"run": 1, "time": "t", "summary": "固定"}], "dirty": False},
        }

    def tearDown(self):
        self.tmp.cleanup()

    def test_state_append_read_restart_and_conflict(self):
        first = self.srv.append_state("demo", self.state, 0, self.db)
        self.assertEqual(first["revision"], 1)
        latest = self.srv.read_latest("demo", self.db)
        self.assertEqual(latest["state"]["selected"], "n6")
        with self.assertRaises(self.srv.RevisionConflict):
            self.srv.append_state("demo", self.state, 0, self.db)
        changed = dict(self.state, committed=True)
        second = self.srv.append_state("demo", changed, 1, self.db)
        self.assertEqual(second["revision"], 2)
        self.assertEqual(len(self.srv.list_revisions("demo", self.db)), 2)
        self.assertEqual(self.srv.read_latest("demo", self.db)["state"]["committed"], True)

    def test_canvas_gdrp_mapper_validates_schema_and_preserves_boundaries(self):
        import canvas_gdrp_mapper
        saved = self.srv.append_state("demo", self.state, 0, self.db)
        pack = canvas_gdrp_mapper.map_canvas_to_gdrp(self.state, "demo", saved["revision"])
        self.assertEqual(pack["execution"]["model_calls"]["count"], 0)
        self.assertEqual(pack["execution"]["status"], "draft")
        self.assertEqual(pack["review"]["overall"], "pending_review")
        self.assertEqual(pack["summary"]["recommendation_status"], "no_recommendation")
        self.assertEqual(pack["comparison"]["recommendations"], [])
        self.assertEqual(pack["domain_extension"]["product"]["reasoning_canvas"]["workspace_kind"], "reasoning_canvas")
        self.assertIn("B", pack["domain_extension"]["product"]["reasoning_canvas"]["killed_directions"])
    def test_frontend_workspace_controls_and_error_code_are_present(self):
        html = open(os.path.join(ROOT, "extensions", "reasoning-canvas", "index.html"), encoding="utf-8").read()
        js = open(os.path.join(ROOT, "extensions", "reasoning-canvas", "reasoning-canvas.js"), encoding="utf-8").read()
        for marker in ('id="rc-save"', 'id="rc-gdrp"', 'id="rc-workspace-status"'):
            self.assertIn(marker, html)
        for marker in ('persistRemote', 'restoreWorkspace', "Object.assign(new Error", "{ code: j.code }"):
            self.assertIn(marker, js)


class CanvasStateHttpTests(unittest.TestCase):
    def setUp(self):
        import socketserver
        import sys
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import reasoning_canvas_server as srv
        self.srv = srv
        self.tmp = tempfile.TemporaryDirectory()
        self.srv.STATE_DB = os.path.join(self.tmp.name, "canvas.sqlite3")
        handler = lambda *a, **kw: srv.Handler(*a, directory=ROOT, **kw)
        socketserver.TCPServer.allow_reuse_address = True
        self.httpd = socketserver.TCPServer(("127.0.0.1", 0), handler)
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()
        self.port = self.httpd.server_address[1]

    def tearDown(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        self.tmp.cleanup()

    def _request(self, method, path, payload=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=15)
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        headers = {"Content-Type": "application/json"} if payload is not None else {}
        conn.request(method, path, body=body, headers=headers)
        resp = conn.getresponse()
        raw = resp.read()
        conn.close()
        return resp.status, json.loads(raw.decode("utf-8"))

    def test_state_and_gdrp_http_flow(self):
        status, missing = self._request("GET", "/api/rc/state?workspace_id=http-demo")
        self.assertEqual(status, 404)
        state = {"selected": "n7", "statuses": {}, "evMarks": {}, "killed": {}, "redteam": [], "redteamReasons": [], "priorities": {}, "reasons": {}, "notes": {}, "committed": True, "intent": [], "subproblems": [], "searchLog": [], "extraEvidence": [], "engineDecisions": {}, "engineConfirmed": [], "positions": {}, "flow": {"runs": 0, "log": [], "dirty": False}}
        status, saved = self._request("POST", "/api/rc/state", {"workspace_id": "http-demo", "base_revision": 0, "state": state})
        self.assertEqual(status, 200)
        self.assertEqual(saved["result"]["revision"], 1)
        status, loaded = self._request("GET", "/api/rc/state?workspace_id=http-demo")
        self.assertEqual(status, 200)
        self.assertTrue(loaded["result"]["state"]["committed"])
        status, revisions = self._request("GET", "/api/rc/revisions?workspace_id=http-demo")
        self.assertEqual(status, 200)
        self.assertEqual(len(revisions["result"]), 1)
        status, pack = self._request("GET", "/api/rc/gdrp?workspace_id=http-demo")
        self.assertEqual(status, 200)
        self.assertEqual(pack["result"]["research_pack"]["execution"]["status"], "review_pending")
        self.assertTrue(pack["result"]["manifest"]["files"]["research-pack.json"])

    def test_invalid_json_and_conflict(self):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        conn.request("POST", "/api/rc/state", body="not-json", headers={"Content-Type": "application/json"})
        resp = conn.getresponse()
        payload = json.loads(resp.read().decode("utf-8"))
        conn.close()
        self.assertEqual(resp.status, 400)
        self.assertFalse(payload["ok"])
        state = {"selected": "n1"}
        self._request("POST", "/api/rc/state", {"workspace_id": "conflict", "base_revision": 0, "state": state})
        status, conflict = self._request("POST", "/api/rc/state", {"workspace_id": "conflict", "base_revision": 0, "state": state})
        self.assertEqual(status, 409)
        self.assertEqual(conflict["code"], "revision_conflict")


if __name__ == "__main__":
    unittest.main()
