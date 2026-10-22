# coding: utf-8
"""049: authenticated nginx-only cloud snapshot; no write routes or watcher.
nginx must authenticate every /inno/ request and proxy Host to the loopback port.
"""
import argparse,re
from http.server import ThreadingHTTPServer
import file_admin as app

PREFIX='/inno'
ROOTS=r'(?:api(?:/|\?)|asset(?:\?|/)|dossier/|methods/|innovation/|(?:app|workflow|workspace|agent)\.js|(?:style|workflow|workspace)\.css|favicon\.ico|\?)'

def prefixed(text):
    text=re.sub(r'([\"\x27`])/(?='+ROOTS+r')',lambda m:m[1]+PREFIX+'/',text)
    return text.replace('href="/"','href="/inno/"').replace("href='/'","href='/inno/'")

class Handler(app.Handler):
    def do_POST(self):self.send(403,dict(error='云端是只读资料快照；上传、清洗与研究发布请使用本机后台。'))
    do_PUT=do_PATCH=do_DELETE=do_POST
    def send(self,status,body,ctype='application/json; charset=utf-8',extra=None):
        if ctype.startswith(('text/html','text/javascript','application/javascript')):
            if isinstance(body,bytes):body=body.decode('utf-8')
            if isinstance(body,str):
                body=prefixed(body)
                if ctype.startswith('text/html'):
                    banner='<div role="note" class="cloud-readonly-notice">OpenDesign · 受保护的只读快照 · 2026-10-22发布 · 上传、清洗和研究发布在本机后台进行。</div>'
                    body=body.replace('</head>','<link rel="icon" href="data:,"><style>.cloud-readonly-notice{padding:10px 24px;background:#f0edff;color:#5145a0;font:13px/1.6 system-ui}</style></head>',1)
                    body=body.replace('<body>','<body>'+banner,1).replace('● 本地私有','● 登录可见 · 只读')
        if isinstance(body,dict) and body.get('service')=='gooddesign-archive-pipeline':body.update(cloud_read_only=True,watcher_running=False)
        super().send(status,body,ctype,extra)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=18776);args=parser.parse_args()
    server=ThreadingHTTPServer(('127.0.0.1',args.port),Handler)
    server.store=app.Store(app.pipe.LIB,app.pipe.INBOX)
    print('OpenDesign authenticated read-only snapshot on loopback',flush=True)
    try:server.serve_forever()
    finally:
        server.store.steward.close();server.store.pool.shutdown(wait=True);server.server_close()
if __name__=='__main__':main()
