import argparse
import mimetypes
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

from gooddesign_assets import content_type, path as asset_path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'output/reports/项目进展汇报-2026-11-04.html'
EVIDENCE = {
    '/research-088/audit-summary.json': ROOT / 'output/research-088/audit-summary.json',
    '/research-088/queues.json': ROOT / 'output/research-088/queues.json',
    '/research-089/material-inventory.csv': ROOT / 'output/research-089/material-inventory.csv',
    '/research-079/2019-s19/publish-result.json': ROOT / 'output/research-079/2019-s19/publish-result.json',
    '/reports/项目进展数据-2026-11-04.json': ROOT / 'output/reports/项目进展数据-2026-11-04.json',
}


class Handler(SimpleHTTPRequestHandler):
    def send_file(self, path, content_type):
        body = path.read_bytes()
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.headers.get('Host') not in {f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'}:
            self.send_error(403)
            return
        path = unquote(urlsplit(self.path).path)
        if path in ('/', '/index.html'):
            self.send_file(REPORT, 'text/html; charset=utf-8')
            return
        if path in EVIDENCE:
            target = EVIDENCE[path]
            content = mimetypes.guess_type(str(target))[0] or 'application/octet-stream'
            if target.suffix == '.json':
                content = 'application/json; charset=utf-8'
            elif target.suffix == '.csv':
                content = 'text/csv; charset=utf-8'
            self.send_file(target, content)
            return
        if path.startswith('/inno/portal/'):
            name = path[len('/inno/portal/'):]
            try:
                target = asset_path(name)
                self.send_file(target, content_type(name))
            except (ValueError, OSError):
                self.send_error(404)
            return
        self.send_error(404)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8896)
    args = parser.parse_args()
    handler = lambda *items, **kwargs: Handler(*items, directory=str(ROOT), **kwargs)
    ThreadingHTTPServer(('127.0.0.1', args.port), handler).serve_forever()
