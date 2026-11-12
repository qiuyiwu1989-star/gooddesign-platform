"""RC-09/12：推理画布本地角色权限与 GDRP 人读报告包。"""
import http.client
import json
import os
import tempfile
import threading
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXT = os.path.join(ROOT, "extensions", "reasoning-canvas")


class ReasoningCanvasRoleAndReportTests(unittest.TestCase):
    def test_role_matrix_is_defined_and_enforced_in_ui(self):
        js = open(os.path.join(EXT, "reasoning-canvas.js"), encoding="utf-8").read()
        html = open(os.path.join(EXT, "index.html"), encoding="utf-8").read()
        for marker in ("ROLE_PERMS", "designer", "advisor", "expert", "ROLE_NOTE_WHO", "applyRoleChrome"):
            self.assertIn(marker, js)
        self.assertIn('id="rc-role"', html)
        for marker in ("can('status')", "can('evidence')", "can('concept')", "can('priority')", "can('commit')"):
            self.assertIn(marker, js)
        self.assertIn("expert: { status: false", js)
        self.assertIn("advisor: { status: false", js)

    def test_report_button_is_present(self):
        html = open(os.path.join(EXT, "index.html"), encoding="utf-8").read()
        js = open(os.path.join(EXT, "reasoning-canvas.js"), encoding="utf-8").read()
        self.assertIn('id="rc-report"', html)
        self.assertIn("RC_API", js)
        self.assertIn("gdrp_package", js)
        self.assertIn("report_html", js)


class ReasoningCanvasReportHttpTests(unittest.TestCase):
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

    def test_gdrp_package_returns_html_md_and_manifest(self):
        status, missing = self._request("GET", "/api/rc/gdrp_package?workspace_id=report-demo")
        self.assertEqual(status, 404)
        state = {"selected": "n7", "statuses": {}, "evMarks": {}, "killed": {}, "redteam": [], "redteamReasons": [], "priorities": {}, "reasons": {}, "notes": {}, "committed": True, "intent": [], "subproblems": [], "searchLog": [], "extraEvidence": [], "engineDecisions": {}, "engineConfirmed": [], "positions": {}, "flow": {"runs": 1, "log": [], "dirty": False}}
        status, saved = self._request("POST", "/api/rc/state", {"workspace_id": "report-demo", "base_revision": 0, "state": state})
        self.assertEqual(status, 200)
        status, package = self._request("GET", "/api/rc/gdrp_package?workspace_id=report-demo")
        self.assertEqual(status, 200)
        result = package["result"]
        self.assertEqual(result["research_pack"]["execution"]["status"], "review_pending")
        self.assertIn("<html", result["report_html"])
        self.assertIn("# 割胶机器人", result["report_md"])
        self.assertEqual(set(result["manifest"]["files"]), {"research-pack.json", "report.html", "report.md"})
        self.assertNotIn("—", result["report_html"])
        self.assertNotIn("–", result["report_html"])


if __name__ == "__main__":
    unittest.main()
