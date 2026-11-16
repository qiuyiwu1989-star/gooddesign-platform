import base64
import hashlib
import hmac
import html
import json
import os
import secrets
import time
import urllib.parse
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from gooddesign_assets import links
from gooddesign_chrome import footer, navigation

COOKIE = 'gd_inno_session'
MAX_AGE = 8 * 60 * 60
KEY_FILE = Path(os.environ.get('GOODDESIGN_AUTH_KEY_FILE', '/etc/innovation-auth/session.key'))
USERS_FILE = Path(os.environ.get('GOODDESIGN_AUTH_USERS_FILE', '/etc/nginx/inno.htpasswd'))
ATTEMPTS = {}


def safe_next(value):
    if not isinstance(value, str) or not value.startswith('/') or value.startswith('//') or '\\' in value:
        return '/loop/'
    return value


def signing_key():
    KEY_FILE.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if not KEY_FILE.exists():
        KEY_FILE.write_bytes(secrets.token_bytes(32))
        KEY_FILE.chmod(0o600)
    return KEY_FILE.read_bytes()


def issue(username):
    payload = f'{username}|{int(time.time()) + MAX_AGE}|{secrets.token_urlsafe(16)}'.encode()
    signature = hmac.new(signing_key(), payload, hashlib.sha256).hexdigest()
    return base64.urlsafe_b64encode(payload).decode() + '.' + signature


def verify(token):
    try:
        raw, supplied = token.rsplit('.', 1)
        payload = base64.urlsafe_b64decode(raw.encode())
        expected = hmac.new(signing_key(), payload, hashlib.sha256).hexdigest()
        if not secrets.compare_digest(supplied, expected):
            return None
        username, expires, _ = payload.decode().split('|', 2)
        if int(expires) < int(time.time()):
            return None
        return username
    except (ValueError, UnicodeDecodeError, TypeError):
        return None


def check_password(username, password):
    if not isinstance(username, str) or not isinstance(password, str) or not 1 <= len(username) <= 80 or not 1 <= len(password) <= 256:
        return False
    try:
        lines = USERS_FILE.read_text().splitlines()
    except OSError:
        return False
    for line in lines:
        user, sep, stored = line.partition(':')
        if not sep or not secrets.compare_digest(user, username):
            continue
        parts = stored.split('$')
        if stored.startswith('$6$'):
            algorithm, salt = '-6', parts[2]
        elif stored.startswith('$apr1$'):
            algorithm, salt = '-apr1', parts[2]
        elif stored.startswith('$1$'):
            algorithm, salt = '-1', parts[2]
        else:
            return False
        import subprocess
        result = subprocess.run(['openssl', 'passwd', algorithm, '-salt', salt, '-stdin'], input=password + '\n', text=True, capture_output=True, timeout=5)
        return result.returncode == 0 and secrets.compare_digest(result.stdout.strip(), stored)
    return False


def allowed_origin(handler):
    port = handler.server.server_port
    origin = handler.headers.get('Origin')
    if origin in {f'http://127.0.0.1:{port}', f'http://localhost:{port}', 'https://opendesign.cc', 'https://haoshejiguan.com', 'https://www.haoshejiguan.com'}:
        return True
    return origin == 'null' and handler.headers.get('Sec-Fetch-Site') == 'same-origin'


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def send(self, status, body=b'', ctype='text/html; charset=utf-8', extra=None):
        if isinstance(body, str):
            body = body.encode()
        self.send_response(status)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('Referrer-Policy', 'no-referrer')
        for key, value in (extra or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def valid_host(self):
        return self.headers.get('Host') in {f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'}

    def user(self):
        try:
            cookie = SimpleCookie(self.headers.get('Cookie', ''))
            return verify(cookie[COOKIE].value) if COOKIE in cookie else None
        except (ValueError, TypeError):
            return None

    def do_GET(self):
        if not self.valid_host():
            self.send(403, {'error': 'invalid_host'}, 'application/json; charset=utf-8')
            return
        path = urllib.parse.urlsplit(self.path).path
        if path == '/health':
            self.send(200, {'ok': True, 'users_file': USERS_FILE.is_file()}, 'application/json; charset=utf-8')
        elif path == '/auth/check':
            self.send(200 if self.user() else 401, b'', 'text/plain; charset=utf-8')
        elif path == '/logout/':
            self.send(303, b'', extra={'Location': '/projects/', 'Set-Cookie': f'{COOKIE}=; Max-Age=0; Path=/; Secure; HttpOnly; SameSite=Lax'})
        elif path == '/login/':
            query = urllib.parse.parse_qs(urllib.parse.urlsplit(self.path).query)
            self.send(200, login_page(safe_next(query.get('next', ['/loop/'])[0]), self.user() is not None))
        else:
            self.send(404, b'')

    def do_POST(self):
        if not self.valid_host() or not allowed_origin(self):
            self.send(403, b'')
            return
        if urllib.parse.urlsplit(self.path).path != '/login/':
            self.send(404, b'')
            return
        address = self.headers.get('X-Forwarded-For', self.client_address[0]).split(',')[0].strip()
        now = time.time()
        recent = [stamp for stamp in ATTEMPTS.get(address, []) if now - stamp < 300]
        if len(recent) >= 10:
            self.send(429, login_page('/loop/', False, '尝试次数较多，请稍后再试。'))
            return
        ATTEMPTS[address] = recent
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 4096:
                raise ValueError('invalid_length')
            if self.headers.get('Content-Type', '').split(';')[0] != 'application/x-www-form-urlencoded':
                raise ValueError('invalid_content_type')
            form = urllib.parse.parse_qs(self.rfile.read(length).decode(), max_num_fields=4)
            username = form.get('username', [''])[0]
            password = form.get('password', [''])[0]
            destination = safe_next(form.get('next', ['/loop/'])[0])
        except (ValueError, UnicodeDecodeError):
            self.send(400, login_page('/loop/', False, '请求内容不完整，请重新填写。'))
            return
        if not check_password(username, password):
            ATTEMPTS[address].append(now)
            self.send(200, login_page(destination, False, '账号或密码不正确，请重新核对。'))
            return
        self.send(303, b'', extra={'Location': destination, 'Set-Cookie': f'{COOKIE}={issue(username)}; Max-Age={MAX_AGE}; Path=/; Secure; HttpOnly; SameSite=Lax'})


AUTH_CSS = '.auth-shell{max-width:520px;margin:0 auto;padding:72px var(--page-gutter)}.auth-card{padding:30px;border:1px solid var(--bdrSoft);border-radius:22px;background:var(--card)}.auth-card h1{margin:10px 0 12px;font-size:30px}.auth-card p{color:var(--fg2);line-height:1.75}.auth-field{display:grid;gap:7px;margin-top:18px}.auth-field label{font-size:var(--fs-caption);font-weight:500}.auth-field input{min-height:46px;padding:10px 12px;border:1px solid var(--bdr);border-radius:12px;background:var(--surface-content);color:var(--fg)}.auth-submit{width:100%;margin-top:24px}.auth-error{padding:12px;border-radius:10px;background:var(--warn);color:var(--fg)!important}.auth-success{padding:12px;border-radius:10px;background:var(--acBg);color:var(--accentDeep)!important}.auth-next{margin-top:18px;font-size:var(--fs-caption)}@media(max-width:560px){.auth-shell{padding-top:36px}.auth-card{padding:22px}}'


def login_page(destination, authenticated=False, error=''):
    e = html.escape
    notice = '<p class="auth-success">当前已通过授权，可以继续进入工作台。</p>' if authenticated else ''
    error_html = f'<p class="auth-error" role="alert">{e(error)}</p>' if error else ''
    body = f'''{links()}<style>{AUTH_CSS}</style><main class="auth-shell" id="main"><section class="auth-card"><span class="gd-kicker">GoodDesign 授权工作区</span><h1>登录后继续研究</h1><p>企业创新工作台和资料管理需要授权。公开项目、方法和需求研究无需登录。</p>{notice}{error_html}<form method="post" action="/login/"><input type="hidden" name="next" value="{e(destination)}"><div class="auth-field"><label for="username">账号</label><input id="username" name="username" autocomplete="username" required autofocus></div><div class="auth-field"><label for="password">密码</label><input id="password" name="password" type="password" autocomplete="current-password" required></div><button class="gd-button gd-button--primary auth-submit" type="submit">登录并继续</button></form><p class="auth-next">MCP使用独立Bearer密钥，不使用此网页账号。</p></section></main>'''
    return '<!doctype html><html lang="zh-CN" data-theme="light" data-zw-mode="product"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>授权登录 · 好设计</title></head><body>' + navigation('about') + body + footer() + '</body></html>'


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=18785)
    args = parser.parse_args()
    ThreadingHTTPServer(('127.0.0.1', args.port), Handler).serve_forever()
