#!/usr/bin/env python3
"""RC-03/05/08/11：推理画布本机服务（loopback）。

静态文件 + API：
  GET  /api/rc/search_methods?q=   64 方法目录检索
  GET  /api/rc/search_projects?q=  560 项目目录检索
  GET  /api/rc/engine_candidates   GD-CRE-0.1 冻结样例候选
  GET  /api/rc/state?workspace_id=...      当前画布状态
  POST /api/rc/state                       追加不可覆盖状态修订
  GET  /api/rc/revisions?workspace_id=...  修订列表
  GET  /api/rc/gdrp?workspace_id=...       由当前状态生成 GDRP 研究包

运行（须用仓库运行时，依赖 mcp/jsonschema 与私有项目库）：
  .runtime/pipeline/bin/python3 scripts/reasoning_canvas_server.py --port 8978
"""
import argparse
import hashlib
import json
import sqlite3
import socketserver
import sys
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

FROZEN_RUN = ROOT / "output" / "engine-runs" / "RUBBER-20261026" / "run-20261105T140200Z"
STATE_DB = ROOT / "output" / "reasoning-canvas-private" / "canvas-state.sqlite3"
MAX_QUERY = 200
MAX_STATE_BYTES = 2 * 1024 * 1024


def _engine_candidates():
    pack_path = FROZEN_RUN / "research-pack.json"
    manifest_path = FROZEN_RUN / "manifest.json"
    if not pack_path.is_file() or not manifest_path.is_file():
        raise FileNotFoundError("冻结样例不在本机（output/engine-runs 不入 Git）")
    pack = json.loads(pack_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    exe = pack.get("execution", {})
    fm = pack.get("function_model", {})
    cs = pack.get("concept_set", {})
    return {
        "engine_version": exe.get("engine_version"),
        "run_id": manifest.get("run_id"),
        "task_id": manifest.get("task_id"),
        "mode": exe.get("mode"),
        "status": exe.get("status"),
        "pack_sha256": manifest.get("files", {}).get("research-pack.json"),
        "functions": [{"id": f.get("id"), "name": f.get("verb_object")} for f in fm.get("functions", [])],
        "options": [
            {"id": o.get("id"), "function_id": o.get("function_id"),
             "principle": o.get("principle"), "evidence_refs": o.get("evidence_refs", [])}
            for o in cs.get("options", [])
        ],
        "note": "冻结样例只读；候选未经人确认不写入思考痕迹",
    }


def canonical_json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def connect(db_path=None):
    path = Path(db_path or STATE_DB)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS canvas_revisions (
      workspace_id TEXT NOT NULL,
      revision INTEGER NOT NULL,
      state_sha256 TEXT NOT NULL,
      state_json TEXT NOT NULL,
      created_at TEXT NOT NULL,
      PRIMARY KEY (workspace_id, revision)
    );
    CREATE TABLE IF NOT EXISTS canvas_latest (
      workspace_id TEXT PRIMARY KEY,
      revision INTEGER NOT NULL,
      state_sha256 TEXT NOT NULL,
      updated_at TEXT NOT NULL
    );
    """)
    return conn


def read_latest(workspace_id, db_path=None):
    with connect(db_path) as conn:
        row = conn.execute(
            "SELECT r.revision, r.state_sha256, r.state_json, r.created_at FROM canvas_revisions r JOIN canvas_latest l ON l.workspace_id=r.workspace_id AND l.revision=r.revision WHERE r.workspace_id=?",
            (workspace_id,),
        ).fetchone()
    if not row:
        return None
    return {"revision": row[0], "sha256": row[1], "state": json.loads(row[2]), "updated_at": row[3]}


def list_revisions(workspace_id, db_path=None):
    with connect(db_path) as conn:
        rows = conn.execute(
            "SELECT revision, state_sha256, created_at FROM canvas_revisions WHERE workspace_id=? ORDER BY revision DESC",
            (workspace_id,),
        ).fetchall()
    return [{"revision": r[0], "sha256": r[1], "created_at": r[2]} for r in rows]


def append_state(workspace_id, state, base_revision, db_path=None):
    raw = canonical_json(state)
    sha = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    now = utc_now()
    with connect(db_path) as conn:
        latest = conn.execute("SELECT revision FROM canvas_latest WHERE workspace_id=?", (workspace_id,)).fetchone()
        current = latest[0] if latest else 0
        if base_revision != current:
            raise RevisionConflict(f"base_revision {base_revision} != current {current}")
        revision = current + 1
        conn.execute(
            "INSERT INTO canvas_revisions(workspace_id, revision, state_sha256, state_json, created_at) VALUES (?,?,?,?,?)",
            (workspace_id, revision, sha, raw, now),
        )
        conn.execute(
            "INSERT INTO canvas_latest(workspace_id, revision, state_sha256, updated_at) VALUES (?,?,?,?) ON CONFLICT(workspace_id) DO UPDATE SET revision=excluded.revision,state_sha256=excluded.state_sha256,updated_at=excluded.updated_at",
            (workspace_id, revision, sha, now),
        )
    return {"workspace_id": workspace_id, "revision": revision, "sha256": sha, "updated_at": now}


class RevisionConflict(Exception):
    pass


class Handler(SimpleHTTPRequestHandler):
    server_version = "ReasoningCanvas/0.2"

    def log_message(self, *args):
        pass

    def _send_json(self, payload, status=200, headers=None):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        try:
            length = int(self.headers.get("Content-Length") or "0")
        except ValueError:
            raise ValueError("Content-Length 非法")
        if length <= 0:
            raise ValueError("请求体为空")
        if length > MAX_STATE_BYTES:
            raise ValueError("请求体超过 2MB")
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except json.JSONDecodeError:
            raise ValueError("JSON 非法")

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/rc/state":
            return self._send_json({"ok": False, "error": "仅 /api/rc/state 接受画布状态写入"}, status=405)
        try:
            payload = self._read_body()
            workspace_id = str(payload.get("workspace_id") or "").strip()
            state = payload.get("state")
            base_revision = payload.get("base_revision", 0)
            if not workspace_id:
                raise ValueError("workspace_id 必填")
            if not isinstance(state, dict):
                raise ValueError("state 必须是对象")
            if not isinstance(base_revision, int):
                raise ValueError("base_revision 必须是整数")
            result = append_state(workspace_id, state, base_revision)
            return self._send_json({"ok": True, "result": result})
        except RevisionConflict as e:
            return self._send_json({"ok": False, "error": str(e), "code": "revision_conflict"}, status=409)
        except ValueError as e:
            return self._send_json({"ok": False, "error": str(e)}, status=400)
        except Exception as e:
            return self._send_json({"ok": False, "error": f"{type(e).__name__}: {e}"}, status=500)

    do_PUT = do_DELETE = do_PATCH = do_POST

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/rc/"):
            return self._api(parsed)
        return super().do_GET()

    def _workspace(self, parsed):
        qs = parse_qs(parsed.query)
        workspace_id = (qs.get("workspace_id", [""])[0] or "").strip()
        if not workspace_id:
            raise ValueError("workspace_id 必填")
        return workspace_id

    def _api(self, parsed):
        qs = parse_qs(parsed.query)
        q = (qs.get("q", [""])[0] or "").strip()
        if len(q) > MAX_QUERY:
            return self._send_json({"ok": False, "error": f"查询词最长 {MAX_QUERY} 字"}, status=400)
        try:
            if parsed.path == "/api/rc/search_methods":
                import innovation_gateway as gw
                return self._send_json({"ok": True, "domain": "methods", "query": q,
                                        "result": gw.search_methods(q, limit=8)})
            if parsed.path == "/api/rc/search_projects":
                import archive_mcp
                return self._send_json({"ok": True, "domain": "projects", "query": q,
                                        "result": archive_mcp.gd_search_projects(q, limit=8)})
            if parsed.path == "/api/rc/engine_candidates":
                return self._send_json({"ok": True, "result": _engine_candidates()})
            if parsed.path == "/api/rc/state":
                workspace_id = self._workspace(parsed)
                result = read_latest(workspace_id)
                if not result:
                    return self._send_json({"ok": False, "error": "workspace 不存在", "code": "workspace_not_found"}, status=404)
                return self._send_json({"ok": True, "result": result})
            if parsed.path == "/api/rc/revisions":
                workspace_id = self._workspace(parsed)
                return self._send_json({"ok": True, "result": list_revisions(workspace_id)})
            if parsed.path == "/api/rc/gdrp":
                workspace_id = self._workspace(parsed)
                latest = read_latest(workspace_id)
                if not latest:
                    return self._send_json({"ok": False, "error": "workspace 不存在", "code": "workspace_not_found"}, status=404)
                import canvas_gdrp_mapper
                pack = canvas_gdrp_mapper.map_canvas_to_gdrp(latest["state"], workspace_id, latest["revision"])
                manifest = canvas_gdrp_mapper.package_manifest(pack)
                return self._send_json({"ok": True, "result": {"research_pack": pack, "manifest": manifest, "revision": latest["revision"]}})
            if parsed.path == "/api/rc/gdrp_package":
                workspace_id = self._workspace(parsed)
                latest = read_latest(workspace_id)
                if not latest:
                    return self._send_json({"ok": False, "error": "workspace 不存在", "code": "workspace_not_found"}, status=404)
                import build_gdrp_report
                import canvas_gdrp_mapper
                pack = canvas_gdrp_mapper.map_canvas_to_gdrp(latest["state"], workspace_id, latest["revision"])
                report_html = build_gdrp_report.render(pack)
                build_gdrp_report.self_check(pack, report_html)
                report_md = build_gdrp_report.render_md(pack)
                if "—" in report_md or "–" in report_md:
                    raise ValueError("Markdown 含禁用破折号字符")
                manifest = canvas_gdrp_mapper.package_full_manifest(pack, report_html, report_md)
                return self._send_json({"ok": True, "result": {"research_pack": pack, "report_html": report_html, "report_md": report_md, "manifest": manifest, "revision": latest["revision"]}})
            return self._send_json({"ok": False, "error": "未知端点"}, status=404)
        except ValueError as e:
            return self._send_json({"ok": False, "error": str(e)}, status=400)
        except Exception as e:  # 如实返回失败原因，不伪装结果
            return self._send_json({"ok": False, "error": f"{type(e).__name__}: {e}"}, status=500)


def main():
    global STATE_DB
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8978)
    parser.add_argument("--state-db", default=str(STATE_DB))
    args = parser.parse_args()
    STATE_DB = Path(args.state_db)
    handler = lambda *a, **kw: Handler(*a, directory=str(ROOT), **kw)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", args.port), handler) as httpd:
        print(f"推理画布服务: http://127.0.0.1:{args.port}/extensions/reasoning-canvas/")
        print("API: search_methods, search_projects, engine_candidates, state, revisions, gdrp, gdrp_package")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
