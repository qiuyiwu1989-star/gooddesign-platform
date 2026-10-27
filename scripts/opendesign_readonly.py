# coding: utf-8
"""049: authenticated nginx-only cloud snapshot; no write routes or watcher.
nginx must authenticate every /inno/ request and proxy Host to the loopback port.
"""
import argparse,re,html,urllib.parse
from http.server import ThreadingHTTPServer
import file_admin as app

PREFIX='/inno'
ROOTS=r'(?:api(?:/|\?)|asset(?:\?|/)|dossier/|methods/|innovation/|(?:app|workflow|workspace|agent)\.js|(?:style|workflow|workspace)\.css|favicon\.ico|\?)'

def prefixed(text):
    text=re.sub(r'([\"\x27`])/(?='+ROOTS+r')',lambda m:m[1]+PREFIX+'/',text)
    return text.replace('href="/"','href="/inno/"').replace("href='/'","href='/inno/'")

class Handler(app.Handler):
    def do_GET(self):
        path=self.path.split('?')[0]
        if path in ('/','/projects','/projects/'):
            self.guard()
            import project_portal
            self.send(200,project_portal.home(),'text/html; charset=utf-8');return
        if path=='/report/':
            self.guard();import data_report_page
            self.send(200,data_report_page.page(),'text/html; charset=utf-8');return
        if path=='/mcp/':
            self.guard();import innovation_gateway_page
            self.send(200,innovation_gateway_page.page(),'text/html; charset=utf-8');return
        if path=='/about/':
            self.guard();import project_portal
            self.send(200,project_portal.about(),'text/html; charset=utf-8');return
        if path.startswith('/portal/'):
            self.guard();import project_portal
            rel=path[len('/portal/'):]
            if rel=='system.css':
                self.send(200,(project_portal.ROOT/'extensions/inno/system.css').read_bytes(),'text/css; charset=utf-8');return
            if rel=='catalog.json':self.send(200,project_portal.catalog(self.server.store.lib));return
            if rel in ('portal.css','portal.js','mcp-guide.js','data-report.css','data-report.js') or re.fullmatch(r'covers/case-[A-Za-z0-9_-]+\.jpg',rel):
                target=project_portal.ASSETS/rel
                if target.is_file():
                    import mimetypes
                    self.send(200,target.read_bytes(),mimetypes.guess_type(str(target))[0] or 'application/octet-stream');return
            self.send(404,dict(error='未找到公开页面资源'));return
        if path=='/admin/':self.path='/'+(('?'+self.path.split('?',1)[1]) if '?' in self.path else '')
        super().do_GET()
    def do_POST(self):self.send(403,dict(error='云端是只读资料快照；上传、清洗与研究发布请使用本机后台。'))
    do_PUT=do_PATCH=do_DELETE=do_POST
    def send(self,status,body,ctype='application/json; charset=utf-8',extra=None):
        if ctype.startswith(('text/html','text/javascript','application/javascript')):
            if isinstance(body,bytes):body=body.decode('utf-8')
            if isinstance(body,str):
                body=prefixed(body)
                if self.path.split('?')[0]=='/dossier/':
                    import project_portal
                    body=re.sub(r'<header class="workspace-header">.*?</header>',lambda m:project_portal.navigation(),body,count=1,flags=re.S)
                    body=body.replace('</head>','<link rel="stylesheet" href="/inno/portal/portal.css"><link rel="stylesheet" href="/inno/portal/system.css"></head>',1)
                    if '<footer class="pp-footer">' not in body:
                        body=body.replace('</body>',project_portal.footer()+'</body>',1) if '</body>' in body else body.replace('</html>',project_portal.footer()+'</html>',1)
                if ctype.startswith('text/html'):
                    body=body.replace('● 本地私有','● 登录可见 · 只读')
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
