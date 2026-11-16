#!/usr/bin/env python3
"""125：MCP 密钥注册表。SQLite，只存哈希，不存明文。

CLI：
  python3 mcp_key_registry.py apply --applicant 王某 --purpose 评估项目库 --env local --days 30
  python3 mcp_key_registry.py approve APP-xxxx --by qiuyiwu        # 打印一次明文 token
  python3 mcp_key_registry.py issue --owner 李某 --purpose 正式接入 --env agent --days 90
  python3 mcp_key_registry.py revoke KEY-xxxxxxxx --by qiuyiwu --reason 合作结束
  python3 mcp_key_registry.py rotate KEY-xxxxxxxx --by qiuyiwu
  python3 mcp_key_registry.py list [--json]
  python3 mcp_key_registry.py usage KEY-xxxxxxxx
  python3 mcp_key_registry.py import-keys-json /etc/innovation-mcp/keys.json

注册表路径：环境变量 GOODDESIGN_MCP_REGISTRY，默认 /etc/innovation-mcp/registry.sqlite3。
"""
import argparse
import hashlib
import json
import os
import secrets
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REGISTRY = Path(os.environ.get("GOODDESIGN_MCP_REGISTRY", "/var/lib/innovation-mcp/registry.sqlite3"))
SCHEMA = """
CREATE TABLE IF NOT EXISTS keys (
  key_id TEXT PRIMARY KEY,
  token_sha256 TEXT NOT NULL UNIQUE,
  owner TEXT NOT NULL,
  purpose TEXT NOT NULL,
  environment TEXT NOT NULL,
  issued_at TEXT NOT NULL,
  expires_at TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'active',
  decided_by TEXT,
  note TEXT DEFAULT '',
  replaced_by TEXT
);
CREATE TABLE IF NOT EXISTS applications (
  app_id TEXT PRIMARY KEY,
  applicant TEXT NOT NULL,
  contact TEXT DEFAULT '',
  purpose TEXT NOT NULL,
  environment TEXT NOT NULL,
  days INTEGER NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending',
  created_at TEXT NOT NULL,
  decided_at TEXT,
  decided_by TEXT,
  note TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS usage (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts TEXT NOT NULL,
  key_id TEXT NOT NULL,
  tool TEXT DEFAULT '',
  args_summary TEXT DEFAULT '',
  http_status INTEGER,
  latency_ms INTEGER,
  client TEXT DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_usage_key ON usage(key_id, ts);
CREATE TABLE IF NOT EXISTS ops (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts TEXT NOT NULL,
  actor TEXT NOT NULL,
  action TEXT NOT NULL,
  target TEXT NOT NULL,
  detail TEXT DEFAULT ''
);
"""

def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def connect(path=None):
    p = Path(path or REGISTRY)
    p.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(str(p))
    db.executescript(SCHEMA)
    return db

def sha(token):
    return hashlib.sha256(token.encode()).hexdigest()

def _op(db, actor, action, target, detail=""):
    db.execute("INSERT INTO ops(ts,actor,action,target,detail) VALUES(?,?,?,?,?)",
               (now(), actor, action, target, detail))

def apply(db, applicant, contact, purpose, environment, days):
    app_id = "APP-" + secrets.token_hex(4)
    db.execute("INSERT INTO applications(app_id,applicant,contact,purpose,environment,days,created_at) VALUES(?,?,?,?,?,?,?)",
               (app_id, applicant, contact, purpose, environment, days, now()))
    db.commit()
    return app_id

def _issue_row(db, owner, purpose, environment, days, actor, note=""):
    token = "gd_" + secrets.token_urlsafe(32)
    key_id = "KEY-" + secrets.token_hex(4)
    expires = (datetime.now(timezone.utc) + timedelta(days=days)).isoformat(timespec="seconds")
    db.execute("INSERT INTO keys(key_id,token_sha256,owner,purpose,environment,issued_at,expires_at,decided_by,note) VALUES(?,?,?,?,?,?,?,?,?)",
               (key_id, sha(token), owner, purpose, environment, now(), expires, actor, note))
    _op(db, actor, "issue", key_id, f"owner={owner} days={days}")
    db.commit()
    return key_id, token

def issue(db, owner, purpose, environment, days, actor):
    return _issue_row(db, owner, purpose, environment, days, actor)

def approve(db, app_id, actor):
    row = db.execute("SELECT * FROM applications WHERE app_id=?", (app_id,)).fetchone()
    if not row:
        raise ValueError("申请不存在：" + app_id)
    if row[6] != "pending":
        raise ValueError("申请已处理：" + row[6])
    key_id, token = _issue_row(db, row[1], row[3], row[4], row[5], actor, note="from " + app_id)
    db.execute("UPDATE applications SET status='approved',decided_at=?,decided_by=? WHERE app_id=?", (now(), actor, app_id))
    _op(db, actor, "approve", app_id, "签发 " + key_id)
    db.commit()
    return key_id, token

def reject(db, app_id, actor, reason):
    row = db.execute("SELECT status FROM applications WHERE app_id=?", (app_id,)).fetchone()
    if not row or row[0] != "pending":
        raise ValueError("申请不存在或已处理")
    db.execute("UPDATE applications SET status='rejected',decided_at=?,decided_by=?,note=? WHERE app_id=?",
               (now(), actor, reason, app_id))
    _op(db, actor, "reject", app_id, reason)
    db.commit()

def revoke(db, key_id, actor, reason=""):
    row = db.execute("SELECT status FROM keys WHERE key_id=?", (key_id,)).fetchone()
    if not row:
        raise ValueError("密钥不存在：" + key_id)
    if row[0] != "active":
        raise ValueError("密钥当前状态：" + row[0])
    db.execute("UPDATE keys SET status='revoked',note=? WHERE key_id=?", (reason, key_id))
    _op(db, actor, "revoke", key_id, reason)
    db.commit()

def rotate(db, key_id, actor, days=None):
    row = db.execute("SELECT owner,purpose,environment FROM keys WHERE key_id=?", (key_id,)).fetchone()
    if not row:
        raise ValueError("密钥不存在：" + key_id)
    # days 未直接存；按剩余期或默认 90 天
    d = days or 90
    new_id, token = _issue_row(db, row[0], row[1], row[2], d, actor, note="rotates " + key_id)
    db.execute("UPDATE keys SET status='revoked', replaced_by=? WHERE key_id=?", (new_id, key_id))
    _op(db, actor, "rotate", key_id, "新 key " + new_id)
    db.commit()
    return new_id, token

def key_status(row):
    if row["status"] != "active":
        return row["status"]
    if row["expires_at"] < now():
        return "expired"
    return "active"

def resolve(db, token):
    """网关鉴权：返回 (key_id, status)；status 非 active 即拒绝。"""
    row = db.execute("SELECT key_id,status,expires_at FROM keys WHERE token_sha256=?", (sha(token),)).fetchone()
    if not row:
        return None, "unknown"
    status = key_status({"status": row[1], "expires_at": row[2]})
    return (row[0], status)

def log_usage(db, key_id, tool, args_summary, http_status, latency_ms, client=""):
    db.execute("INSERT INTO usage(ts,key_id,tool,args_summary,http_status,latency_ms,client) VALUES(?,?,?,?,?,?,?)",
               (now(), key_id, tool, args_summary[:300], http_status, latency_ms, client))
    db.commit()

def usage_summary(db, key_id):
    total = db.execute("SELECT COUNT(*), MAX(ts) FROM usage WHERE key_id=?", (key_id,)).fetchone()
    by_tool = db.execute("SELECT tool, COUNT(*) c FROM usage WHERE key_id=? GROUP BY tool ORDER BY c DESC", (key_id,)).fetchall()
    recent = db.execute("SELECT ts,tool,args_summary,http_status,latency_ms FROM usage WHERE key_id=? ORDER BY id DESC LIMIT 20", (key_id,)).fetchall()
    return {"total": total[0], "last_active": total[1], "by_tool": by_tool, "recent": recent}

def import_keys_json(db, keys_json_path, actor):
    """把既有 keys.json 的哈希导入注册表（不知明文，归属标记 legacy）。"""
    data = json.loads(Path(keys_json_path).read_text())
    n = 0
    for e in data.get("keys", []):
        if not (isinstance(e, dict) and e.get("enabled") is True and isinstance(e.get("sha256"), str)):
            continue
        exists = db.execute("SELECT 1 FROM keys WHERE token_sha256=?", (e["sha256"],)).fetchone()
        if exists:
            continue
        key_id = "KEY-" + secrets.token_hex(4)
        expires = (datetime.now(timezone.utc) + timedelta(days=90)).isoformat(timespec="seconds")
        db.execute("INSERT INTO keys(key_id,token_sha256,owner,purpose,environment,issued_at,expires_at,decided_by,note) VALUES(?,?,?,?,?,?,?,?,?)",
                   (key_id, e["sha256"], e.get("label") or "legacy", "keys.json 迁移", "unknown", now(), expires, actor, "imported"))
        _op(db, actor, "import", key_id, "keys.json")
        n += 1
    db.commit()
    return n

def list_keys(db):
    rows = db.execute("SELECT key_id,owner,purpose,environment,issued_at,expires_at,status,note,replaced_by FROM keys ORDER BY issued_at DESC").fetchall()
    return [dict(zip(["key_id", "owner", "purpose", "environment", "issued_at", "expires_at", "status", "note", "replaced_by"], r),
                  effective_status=key_status({"status": r[6], "expires_at": r[5]})) for r in rows]

def main():
    ap = argparse.ArgumentParser(description="MCP 密钥注册表")
    ap.add_argument("--registry", default=str(REGISTRY))
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("apply"); a.add_argument("--applicant", required=True); a.add_argument("--contact", default=""); a.add_argument("--purpose", required=True); a.add_argument("--env", required=True); a.add_argument("--days", type=int, required=True)
    a = sub.add_parser("approve"); a.add_argument("app_id"); a.add_argument("--by", required=True)
    a = sub.add_parser("reject"); a.add_argument("app_id"); a.add_argument("--by", required=True); a.add_argument("--reason", required=True)
    a = sub.add_parser("issue"); a.add_argument("--owner", required=True); a.add_argument("--purpose", required=True); a.add_argument("--env", required=True); a.add_argument("--days", type=int, required=True); a.add_argument("--by", required=True)
    a = sub.add_parser("revoke"); a.add_argument("key_id"); a.add_argument("--by", required=True); a.add_argument("--reason", default="")
    a = sub.add_parser("rotate"); a.add_argument("key_id"); a.add_argument("--by", required=True); a.add_argument("--days", type=int)
    a = sub.add_parser("list"); a.add_argument("--json", action="store_true")
    a = sub.add_parser("usage"); a.add_argument("key_id")
    a = sub.add_parser("import-keys-json"); a.add_argument("path"); a.add_argument("--by", required=True)
    args = ap.parse_args()
    db = connect(args.registry)

    if args.cmd == "apply":
        print("申请已登记：" + apply(db, args.applicant, args.contact, args.purpose, args.env, args.days))
    elif args.cmd == "approve":
        key_id, token = approve(db, args.app_id, args.by)
        print(f"已批准并签发 {key_id}\n明文 token 只显示这一次：\n{token}")
    elif args.cmd == "reject":
        reject(db, args.app_id, args.by, args.reason); print("已驳回 " + args.app_id)
    elif args.cmd == "issue":
        key_id, token = issue(db, args.owner, args.purpose, args.env, args.days, args.by)
        print(f"已签发 {key_id}\n明文 token 只显示这一次：\n{token}")
    elif args.cmd == "revoke":
        revoke(db, args.key_id, args.by, args.reason); print("已吊销 " + args.key_id)
    elif args.cmd == "rotate":
        new_id, token = rotate(db, args.key_id, args.by, args.days)
        print(f"已轮换，旧 key 吊销，新 key {new_id}\n明文 token 只显示这一次：\n{token}")
    elif args.cmd == "list":
        keys = list_keys(db)
        if args.json:
            print(json.dumps(keys, ensure_ascii=False, indent=2))
        else:
            for k in keys:
                print(f"{k['key_id']}  {k['effective_status']}  {k['owner']}  {k['purpose']}  到期 {k['expires_at'][:10]}")
    elif args.cmd == "usage":
        print(json.dumps(usage_summary(db, args.key_id), ensure_ascii=False, indent=2))
    elif args.cmd == "import-keys-json":
        print(f"导入 {import_keys_json(db, args.path, args.by)} 把既有 key")

if __name__ == "__main__":
    main()
