#!/usr/bin/env python3
"""125：MCP 密钥管理台（本机 loopback，不暴露公网）。

  .runtime/pipeline/bin/python3 scripts/mcp_key_admin.py --port 8788

申请、批准、驳回、吊销、轮换、延期查看与按 key 使用分析。
明文 token 只在签发/轮换结果显示一次，列表页永不出现。
"""
import argparse
import html
import secrets
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

import mcp_key_registry as reg

E = lambda v: html.escape(str(v), quote=True)
CSRF = secrets.token_urlsafe(16)

PAGE = """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>MCP 密钥管理台</title><style>
body{margin:0;font:14px/1.7 -apple-system,'PingFang SC',sans-serif;background:#f3f4f6;color:#1a1d24}
main{max-width:1000px;margin:0 auto;padding:28px 20px}
h1{font-size:22px}h2{font-size:16px;margin:28px 0 10px}
table{width:100%;border-collapse:collapse;background:#fff;border-radius:10px;overflow:hidden}
th,td{padding:8px 12px;text-align:left;font-size:13px;border-bottom:1px solid #eceff3;vertical-align:top}
th{background:#f8f9fb;font-weight:600;color:#5a6270}
form{display:inline}input,select{padding:7px 10px;border:1px solid #d3d9e0;border-radius:8px;font:inherit}
button{padding:7px 14px;border:1px solid #d3d9e0;border-radius:999px;background:#fff;cursor:pointer;font:inherit}
button.primary{background:#5b5bd6;color:#fff;border-color:#5b5bd6}
.token{display:block;margin:14px 0;padding:14px 16px;background:#fff7e6;border:1px solid #e8c468;border-radius:10px;font:13px ui-monospace,Menlo,monospace;word-break:break-all}
.warn{color:#b54708;font-size:13px}.badge{padding:2px 9px;border-radius:999px;font-size:12px}
.b-active{background:#e6f6ee;color:#0b7652}.b-revoked{background:#fdecec;color:#b82e38}.b-expired{background:#fff4e0;color:#87550b}.b-pending{background:#eef0f4;color:#5a6270}
.applyform{display:flex;gap:8px;flex-wrap:wrap;background:#fff;padding:14px;border-radius:10px}
a{color:#5b5bd6;text-decoration:none}
</style></head><body><main>"""

def page(title, inner):
    return PAGE + f"<h1>{E(title)}</h1>" + inner + "</main></body></html>"

def badge(status):
    return f'<span class="badge b-{E(status)}">{E(status)}</span>'

def hidden():
    return f'<input type="hidden" name="csrf" value="{CSRF}">'

def view_home(db):
    apps = db.execute("SELECT app_id,applicant,purpose,environment,days,created_at,status FROM applications ORDER BY created_at DESC").fetchall()
    keys = reg.list_keys(db)
    out = ["<h2>待处理申请</h2>"]
    pending = [a for a in apps if a[6] == "pending"]
    if not pending:
        out.append('<p class="warn">没有待处理申请。</p>')
    for a in pending:
        out.append(f"""<table><tr><th>{E(a[0])}</th><th>{E(a[1])}</th><th>{E(a[2])}</th><th>{E(a[3])}</th><th>{a[4]} 天</th><th>{E(a[5][:16])}</th></tr>
        <tr><td colspan="6"><form method="post" action="/approve">{hidden()}<input type="hidden" name="app_id" value="{E(a[0])}"><button class="primary">批准并签发</button></form>
        <form method="post" action="/reject">{hidden()}<input type="hidden" name="app_id" value="{E(a[0])}"><input name="reason" placeholder="驳回理由" required><button>驳回</button></form></td></tr></table>""")
    out.append("""<h2>登记新申请（代录入）</h2><form class="applyform" method="post" action="/apply">""" + hidden() +
               '<input name="applicant" placeholder="申请人" required><input name="purpose" placeholder="用途" required>' +
               '<select name="environment"><option value="local">本地客户端</option><option value="agent">常驻 Agent</option><option value="server">对方服务器</option></select>' +
               '<input name="days" type="number" value="30" min="1" max="365" style="width:80px"> 天<button class="primary">登记申请</button></form>')
    out.append("<h2>密钥列表</h2><table><tr><th>ID</th><th>对象</th><th>用途</th><th>环境</th><th>状态</th><th>到期</th><th>使用</th><th>操作</th></tr>")
    for k in keys:
        ops = ""
        if k["effective_status"] == "active":
            ops = (f'<form method="post" action="/revoke">{hidden()}<input type="hidden" name="key_id" value="{E(k["key_id"])}"><input name="reason" placeholder="吊销理由"><button>吊销</button></form>'
                   f'<form method="post" action="/rotate">{hidden()}<input type="hidden" name="key_id" value="{E(k["key_id"])}"><button>轮换</button></form>')
        out.append(f'<tr><td>{E(k["key_id"])}</td><td>{E(k["owner"])}</td><td>{E(k["purpose"])}</td><td>{E(k["environment"])}</td>'
                   f'<td>{badge(k["effective_status"])}</td><td>{E(k["expires_at"][:10])}</td>'
                   f'<td><a href="/usage?key={E(k["key_id"])}">查看</a></td><td>{ops}</td></tr>')
    out.append("</table>")
    return page("MCP 密钥管理台", "".join(out))

def view_token(title, key_id, token):
    return page(title, f'<p>{E(key_id)} 已签发。</p><div class="token">{E(token)}</div>'
                       '<p class="warn">明文只显示这一次，请立即通过私密渠道交付；本页不保存、列表不显示。</p>'
                       '<p><a href="/">返回管理台</a></p>')

def view_usage(db, key_id):
    s = reg.usage_summary(db, key_id)
    rows = "".join(f"<tr><td>{E(r[0])}</td><td>{E(r[1])}</td><td>{E(r[2])}</td><td>{r[3]}</td><td>{r[4]}ms</td></tr>" for r in s["recent"])
    tools = "".join(f"<tr><td>{E(t[0] or '(transport)')}</td><td>{t[1]}</td></tr>" for t in s["by_tool"])
    inner = (f"<h2>{E(key_id)} 使用情况</h2><p>总调用 <b>{s['total']}</b> 次，最近活跃：{E(s['last_active'] or '从未')}</p>"
             f"<h2>工具分布</h2><table><tr><th>工具</th><th>次数</th></tr>{tools}</table>"
             f"<h2>最近 20 次（数据回流信号：在检索什么、组什么包）</h2><table><tr><th>时间</th><th>工具</th><th>参数摘要</th><th>状态</th><th>耗时</th></tr>{rows}</table>"
             '<p><a href="/">返回管理台</a></p>')
    return page("使用情况", inner)

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _db(self):
        return reg.connect(self.server.registry)

    def _send(self, text, status=200):
        body = text.encode()
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _forbidden_host(self):
        host = self.headers.get("Host", "")
        return not (host.startswith("127.0.0.1") or host.startswith("localhost"))

    def do_GET(self):
        if self._forbidden_host():
            return self._send("forbidden", 403)
        q = parse_qs(urlparse(self.path).query)
        db = self._db()
        try:
            if self.path.startswith("/usage"):
                key = q.get("key", [""])[0]
                return self._send(view_usage(db, key))
            return self._send(view_home(db))
        finally:
            db.close()

    def do_POST(self):
        if self._forbidden_host():
            return self._send("forbidden", 403)
        length = int(self.headers.get("Content-Length", 0) or 0)
        if length > 16384:
            return self._send("payload too large", 413)
        form = parse_qs(self.rfile.read(length).decode())
        if form.get("csrf", [""])[0] != CSRF:
            return self._send("csrf check failed", 403)
        db = self._db()
        try:
            path = urlparse(self.path).path
            g = lambda k, d="": form.get(k, [d])[0].strip()
            if path == "/apply":
                app_id = reg.apply(db, g("applicant"), "", g("purpose"), g("environment"), int(g("days", "30")))
                return self._send(page("已登记", f"<p>申请 {E(app_id)} 已登记。</p><p><a href='/'>返回</a></p>"))
            if path == "/approve":
                key_id, token = reg.approve(db, g("app_id"), "admin")
                return self._send(view_token("批准并签发", key_id, token))
            if path == "/reject":
                reg.reject(db, g("app_id"), "admin", g("reason"))
                return self._send(page("已驳回", f"<p>申请 {E(g('app_id'))} 已驳回。</p><p><a href='/'>返回</a></p>"))
            if path == "/revoke":
                reg.revoke(db, g("key_id"), "admin", g("reason"))
                return self._send(page("已吊销", f"<p>{E(g('key_id'))} 已吊销，网关即刻 401。</p><p><a href='/'>返回</a></p>"))
            if path == "/rotate":
                new_id, token = reg.rotate(db, g("key_id"), "admin")
                return self._send(view_token("轮换完成", new_id, token))
            return self._send("unknown", 404)
        except ValueError as e:
            return self._send(page("操作失败", f"<p class='warn'>{E(e)}</p><p><a href='/'>返回</a></p>"), 400)
        finally:
            db.close()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8788)
    ap.add_argument("--registry", default=str(reg.REGISTRY))
    args = ap.parse_args()
    srv = HTTPServer(("127.0.0.1", args.port), Handler)
    srv.registry = args.registry
    print(f"MCP 密钥管理台: http://127.0.0.1:{args.port}/ （仅本机）")
    print(f"CSRF token 已生成；注册表：{args.registry}")
    srv.serve_forever()

if __name__ == "__main__":
    main()
