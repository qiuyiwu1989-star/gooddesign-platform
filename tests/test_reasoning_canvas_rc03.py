"""RC-03/05 桥接回归：端点结构、真实检索、冻结样例、写方法拒绝。

须用仓库运行时：.runtime/pipeline/bin/python3 -m unittest tests.test_reasoning_canvas_rc03 -v
"""
import http.client
import json
import os
import threading
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _start_server():
    import socketserver
    import sys
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    import reasoning_canvas_server as srv
    handler = lambda *a, **kw: srv.Handler(*a, directory=ROOT, **kw)
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, httpd.server_address[1]


class TestReasoningCanvasBridge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd, cls.port = _start_server()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def _get(self, path, method="GET"):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=15)
        conn.request(method, path)
        resp = conn.getresponse()
        body = resp.read()
        conn.close()
        return resp.status, body

    def _get_json(self, path):
        status, body = self._get(path)
        return status, json.loads(body.decode("utf-8"))

    def test_static_index_served(self):
        status, body = self._get("/extensions/reasoning-canvas/index.html")
        self.assertEqual(status, 200)
        self.assertIn("推理画布".encode("utf-8"), body)

    def test_search_methods_real_hit(self):
        status, j = self._get_json("/api/rc/search_methods?q=%E5%88%86%E7%A6%BB")
        self.assertEqual(status, 200)
        self.assertTrue(j["ok"])
        ids = [r.get("research_id") for r in j["result"]["data"]]
        self.assertIn("R23", ids)

    def test_search_projects_total(self):
        status, j = self._get_json("/api/rc/search_projects?q=")
        self.assertEqual(status, 200)
        self.assertTrue(j["ok"])
        self.assertGreaterEqual(j["result"]["total"], 500)

    def test_engine_candidates_frozen_sample(self):
        status, j = self._get_json("/api/rc/engine_candidates")
        self.assertEqual(status, 200)
        self.assertTrue(j["ok"])
        r = j["result"]
        self.assertEqual(r["engine_version"], "GD-CRE-0.1")
        self.assertEqual(r["status"], "review_pending")
        self.assertEqual(len(r["options"]), 28)
        self.assertEqual(len(r["functions"]), 7)
        self.assertTrue(r["pack_sha256"])

    def test_write_methods_rejected(self):
        status, j = self._get_json("/api/rc/search_methods?q=") if False else (None, None)
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        conn.request("POST", "/api/rc/search_methods")
        resp = conn.getresponse()
        payload = json.loads(resp.read().decode("utf-8"))
        conn.close()
        self.assertEqual(resp.status, 405)
        self.assertFalse(payload["ok"])

    def test_unknown_endpoint_404(self):
        status, j = self._get_json("/api/rc/nope")
        self.assertEqual(status, 404)
        self.assertFalse(j["ok"])


if __name__ == "__main__":
    unittest.main()
