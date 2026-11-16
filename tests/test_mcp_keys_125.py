"""125：密钥注册表、网关鉴权与使用记录、管理台边界。

运行：.runtime/pipeline/bin/python3 -m unittest tests.test_mcp_keys_125 -v
"""
import asyncio
import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import mcp_key_registry as reg


class RegistryCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = reg.connect(os.path.join(self.tmp.name, "r.sqlite3"))

    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()

    def test_apply_approve_issue_once(self):
        app_id = reg.apply(self.db, "王某", "", "评估项目库", "local", 30)
        key_id, token = reg.approve(self.db, app_id, "qiuyiwu")
        self.assertTrue(token.startswith("gd_"))
        # 明文不落库：注册表只存哈希
        raw = self.db.execute("SELECT token_sha256 FROM keys WHERE key_id=?", (key_id,)).fetchone()[0]
        self.assertEqual(raw, hashlib.sha256(token.encode()).hexdigest())
        self.assertNotIn(token, json.dumps(reg.list_keys(self.db), ensure_ascii=False))
        # 已处理的申请不能重复批准
        with self.assertRaises(ValueError):
            reg.approve(self.db, app_id, "qiuyiwu")

    def test_reject_keeps_reason(self):
        app_id = reg.apply(self.db, "李某", "", "试用", "agent", 30)
        reg.reject(self.db, app_id, "qiuyiwu", "用途不清")
        row = self.db.execute("SELECT status,note FROM applications WHERE app_id=?", (app_id,)).fetchone()
        self.assertEqual(row[0], "rejected")
        self.assertEqual(row[1], "用途不清")

    def test_resolve_revoke_rotate_expire(self):
        key_id, token = reg.issue(self.db, "陈某", "正式接入", "server", 90, "qiuyiwu")
        self.assertEqual(reg.resolve(self.db, token), (key_id, "active"))
        reg.revoke(self.db, key_id, "qiuyiwu", "合作结束")
        self.assertEqual(reg.resolve(self.db, token)[1], "revoked")
        # 轮换：旧废新立
        key2, token2 = reg.issue(self.db, "赵某", "评估", "local", 30, "qiuyiwu")
        new_id, new_token = reg.rotate(self.db, key2, "qiuyiwu")
        self.assertEqual(reg.resolve(self.db, token2)[1], "revoked")
        self.assertEqual(reg.resolve(self.db, new_token), (new_id, "active"))
        # 过期：直接改到期时间模拟
        self.db.execute("UPDATE keys SET expires_at='2000-01-01T00:00:00+00:00' WHERE key_id=?", (new_id,))
        self.assertEqual(reg.resolve(self.db, new_token)[1], "expired")

    def test_usage_log_and_summary(self):
        key_id, token = reg.issue(self.db, "王某", "评估", "local", 30, "qiuyiwu")
        reg.log_usage(self.db, key_id, "inno_search_projects", "query=割胶", 200, 45)
        reg.log_usage(self.db, key_id, "inno_search_methods", "query=分离", 200, 30)
        s = reg.usage_summary(self.db, key_id)
        self.assertEqual(s["total"], 2)
        self.assertEqual(dict(s["by_tool"])["inno_search_projects"], 1)
        self.assertIn("割胶", json.dumps(s["recent"], ensure_ascii=False))

    def test_import_keys_json_keeps_existing_working(self):
        token = "legacy-token-abc"
        kj = Path(self.tmp.name) / "keys.json"
        kj.write_text(json.dumps({"keys": [{"sha256": hashlib.sha256(token.encode()).hexdigest(), "enabled": True, "label": "旧部署"}]}))
        n = reg.import_keys_json(self.db, kj, "qiuyiwu")
        self.assertEqual(n, 1)
        key_id, status = reg.resolve(self.db, token)
        self.assertEqual(status, "active")
        # 重复导入不产生重复
        self.assertEqual(reg.import_keys_json(self.db, kj, "qiuyiwu"), 0)


class GatewayAuthCase(unittest.TestCase):
    """BearerAuth 接注册表：active 放行并记录使用，revoked/unknown 401。"""

    def setUp(self):
        import innovation_gateway_http as gw
        self.gw = gw
        self.tmp = tempfile.TemporaryDirectory()
        self.registry = os.path.join(self.tmp.name, "r.sqlite3")
        db = reg.connect(self.registry)
        self.key_id, self.token = reg.issue(db, "测试", "验收", "local", 90, "test")
        db.close()
        self.keys_json = Path(self.tmp.name) / "keys.json"
        self.keys_json.write_text(json.dumps({"keys": []}))

    def tearDown(self):
        self.tmp.cleanup()

    def _call(self, token, body=b'{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"inno_capabilities","arguments":{}}}'):
        async def inner(scope, receive, send):
            while True:
                msg = await receive()
                if msg["type"] == "http.request" and not msg.get("more_body"):
                    break
            await send({"type": "http.response.start", "status": 200, "headers": []})
            await send({"type": "http.response.body", "body": b"{}"})

        app = self.gw.BearerAuth(inner, self.keys_json, self.registry)
        scope = {"type": "http", "headers": [(b"authorization", b"Bearer " + token.encode())]}
        msgs = [{"type": "http.request", "body": body, "more_body": False}]
        sent = []

        async def receive():
            return msgs.pop(0) if msgs else {"type": "http.request", "body": b"", "more_body": False}

        async def send(m):
            sent.append(m)

        asyncio.run(app(scope, receive, send))
        return next((m["status"] for m in sent if m["type"] == "http.response.start"), None)

    def test_active_passes_and_logs(self):
        self.assertEqual(self._call(self.token), 200)
        db = reg.connect(self.registry)
        s = reg.usage_summary(db, self.key_id)
        db.close()
        self.assertEqual(s["total"], 1)
        self.assertEqual(s["by_tool"][0][0], "inno_capabilities")

    def test_revoked_401(self):
        db = reg.connect(self.registry)
        reg.revoke(db, self.key_id, "test", "验收")
        db.close()
        self.assertEqual(self._call(self.token), 401)

    def test_unknown_401(self):
        self.assertEqual(self._call("gd_not-a-real-token"), 401)

    def test_malformed_401(self):
        self.assertEqual(self._call(""), 401)

    def test_replay_delegates_disconnect(self):
        """消费完缓存体后 receive 委派原始通道；否则 SSE 断连轮询会自旋（生产实证过）。"""
        async def inner(scope, receive, send):
            seen = []
            for _ in range(3):
                msg = await receive()
                seen.append(msg["type"])
                if msg["type"] == "http.disconnect":
                    break
            await send({"type": "http.response.start", "status": 200, "headers": []})
            await send({"type": "http.response.body", "body": b"{}"})
            assert "http.disconnect" in seen, seen

        app = self.gw.BearerAuth(inner, self.keys_json, self.registry)
        scope = {"type": "http", "headers": [(b"authorization", b"Bearer " + self.token.encode())]}
        msgs = [{"type": "http.request", "body": b"{}", "more_body": False},
                {"type": "http.disconnect"}]

        async def receive():
            return msgs.pop(0)

        async def send(m):
            pass

        asyncio.run(asyncio.wait_for(app(scope, receive, send), timeout=5))


class AdminCase(unittest.TestCase):
    def test_admin_imports_and_pages(self):
        import mcp_key_admin as admin
        self.assertTrue(admin.CSRF)
        db = reg.connect(os.path.join(tempfile.mkdtemp(), "r.sqlite3"))
        html = admin.view_home(db)
        self.assertIn("登记新申请", html)
        self.assertIn("密钥列表", html)
        db.close()

    def test_new_domain_allowed(self):
        import innovation_gateway_http as gw
        settings = gw.MCP.settings.transport_security
        self.assertIn("mcp.haosheji.cc", settings.allowed_hosts)
        self.assertIn("https://mcp.haosheji.cc", settings.allowed_origins)


if __name__ == "__main__":
    unittest.main()
