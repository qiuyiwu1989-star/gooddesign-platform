import argparse
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit
from urllib.request import Request, urlopen

import project_pipeline as pipeline
import project_portal
import workspace_ui

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/inno-preview/gooddesign-site'
CANVAS = ROOT / 'extensions/reasoning-canvas'
CANVAS_API = 'http://127.0.0.1:8978/api/rc'


class Handler(SimpleHTTPRequestHandler):
    def send_json(self, value, status=200):
        body = json.dumps(value, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(body)

    def send_html(self, text):
        body = text.encode()
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(body)

    def valid_host(self):
        return self.headers.get('Host') in {f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'}

    def translate_path(self, path):
        parsed = urlsplit(path)
        for prefix in ('/canvas/', '/inno/canvas/'):
            if parsed.path == prefix or parsed.path.startswith(prefix):
                relative = parsed.path[len(prefix):] or 'index.html'
                candidate = (CANVAS / relative).resolve()
                if candidate == CANVAS or CANVAS not in candidate.parents:
                    return str(CANVAS / '__not_found__')
                return str(candidate)
        return super().translate_path(path)

    def proxy_canvas(self, method):
        parsed = urlsplit(self.path)
        prefix = '/inno/canvas/api/rc'
        if not parsed.path.startswith(prefix + '/'):
            return False
        target = CANVAS_API + parsed.path[len(prefix):]
        if parsed.query:
            target += '?' + parsed.query
        body = None
        headers = {}
        if method == 'POST':
            length = int(self.headers.get('Content-Length', '0'))
            if length > 2 * 1024 * 1024 + 4096:
                self.send_json({'ok': False, 'error': '请求过大'}, 413)
                return True
            body = self.rfile.read(length)
            headers['Content-Type'] = self.headers.get('Content-Type', 'application/json')
        request = Request(target, data=body, headers=headers, method=method)
        try:
            with urlopen(request, timeout=30) as response:
                status = response.status
                content_type = response.headers.get('Content-Type', 'application/json; charset=utf-8')
                payload = response.read()
        except HTTPError as error:
            status = error.code
            content_type = error.headers.get('Content-Type', 'application/json; charset=utf-8')
            payload = error.read()
        except OSError as error:
            self.send_json({'ok': False, 'code': 'canvas_service_unavailable', 'error': f'画布服务不可用：{error}'}, 503)
            return True
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(payload)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(payload)
        return True

    def do_POST(self):
        if not self.valid_host():
            self.send_error(403)
            return
        if not self.proxy_canvas('POST'):
            self.send_error(405)

    def do_GET(self):
        if not self.valid_host():
            self.send_error(403)
            return
        if self.proxy_canvas('GET'):
            return
        parsed = urlsplit(self.path)
        redirects = {
            '/inno/learn/': '/inno/museum/#education',
            '/inno/needs-v2/': '/inno/needs/',
            '/inno/projects/': '/inno/',
            '/inno/admin/': 'http://127.0.0.1:8893/',
            '/inno/workbench/': 'http://127.0.0.1:8894/',
            '/inno/loop/': 'http://127.0.0.1:8895/',
        }
        if parsed.path in redirects:
            self.send_response(302)
            self.send_header('Location', redirects[parsed.path])
            self.end_headers()
            return
        if parsed.path == '/api/health':
            self.send_json({'ok': True, 'preview': True, 'llm': False})
            return
        root_pages = {
            '/projects/': '/inno/index.html',
            '/museum/': '/inno/museum/index.html',
            '/apps/': '/inno/apps/index.html',
            '/lab/': '/inno/lab/index.html',
            '/quest/': '/inno/quest/index.html',
            '/studio/': '/inno/studio/index.html',
            '/transfer/': '/inno/transfer/index.html',
            '/needs/': '/inno/needs-v2/index.html',
            '/report/': '/inno/report/index.html',
            '/mcp/': '/inno/mcp/index.html',
            '/about/': '/inno/about/index.html',
            '/model/': '/inno/model/index.html',
            '/guide/': '/inno/guide/index.html',
            '/museum/zones': '/categories.html',
            '/museum/hall': '/hall.html',
            '/museum/x-ray': '/x-ray.html',
            '/museum/playground': '/playground.html',
            '/museum/laureates': '/laureates.html',
            '/museum/assistant': '/assistant.html',
            '/museum/connect': '/connect.html',
            '/museum/award': '/award.html',
        }
        asset_aliases = {
            '/inno/method-workbench/vendor/tokens.css': '/inno/portal/tokens.css',
            '/inno/method-workbench/vendor/design-system.css': '/inno/portal/design-system.css',
            '/inno/design-system/gooddesign.css': '/inno/portal/gooddesign.css',
        }
        if parsed.path in root_pages:
            self.path = root_pages[parsed.path]
        elif parsed.path in asset_aliases:
            self.path = asset_aliases[parsed.path]
        elif parsed.path.startswith('/inno/legacy/'):
            self.path = '/' + parsed.path[len('/inno/legacy/'):]
        elif parsed.path.startswith('/cases/'):
            self.path = '/inno/cases/' + parsed.path[len('/cases/'):]
        elif parsed.path.startswith('/methods/'):
            self.path = '/inno/methods/' + parsed.path[len('/methods/'):]
        elif parsed.path == '/dossier/' or parsed.path.startswith('/dossier/?'):
            self.path = '/inno/dossier/' + ('?' + parsed.query if parsed.query else '')
            parsed = urlsplit(self.path)
        if parsed.path in ('/inno/catalog.json', '/inno/portal/catalog.json', '/inno/projects/catalog.json'):
            self.send_json(project_portal.catalog(pipeline.LIB))
            return
        if parsed.path in ('/inno/dossier', '/inno/dossier/'):
            project = parse_qs(parsed.query).get('project', ['2025-00'])[0]
            try:
                self.send_html(workspace_ui.dossier(project, pipeline.LIB))
            except ValueError as error:
                self.send_error(400, str(error))
            return
        super().do_GET()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8892)
    args = parser.parse_args()
    handler = lambda *items, **kwargs: Handler(*items, directory=str(OUT), **kwargs)
    ThreadingHTTPServer(('127.0.0.1', args.port), handler).serve_forever()
