import argparse
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import project_pipeline as pipeline
import project_portal

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = '/extensions/design-system/catalog.json'


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.headers.get('Host') not in {f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'}:
            self.send_error(403)
            return
        if self.path == CATALOG_PATH:
            body = json.dumps(project_portal.catalog(pipeline.LIB), ensure_ascii=False).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8891)
    args = parser.parse_args()
    handler = lambda *items, **kwargs: Handler(*items, directory=str(ROOT), **kwargs)
    ThreadingHTTPServer(('127.0.0.1', args.port), handler).serve_forever()
