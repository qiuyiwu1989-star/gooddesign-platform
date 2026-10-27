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
            rows=app.pipe.load(self.server.store.lib/'项目索引.json')['projects']
            esc=lambda v:html.escape(str(v),quote=True)
            cards=''.join('<article><small>'+esc(x.get('year',''))+' · '+esc(x.get('award',''))+'</small><h2><a href="/inno/dossier/?project='+urllib.parse.quote(x['id'])+'">'+esc(x['name'])+'</a></h2><p>'+esc(x.get('unit',''))+'</p></article>' for x in rows)
            body='<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>项目库 · 好设计</title><style>body{font:16px/1.7 system-ui;background:#f7f8fa;color:#263044;margin:0}main{max-width:1160px;margin:auto;padding:40px 24px}h1{font-size:36px}a{color:inherit}input{padding:14px;border:1px solid #ccd1da;border-radius:10px;width:min(90%,480px);font:inherit}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:20px;margin-top:28px}article{background:white;padding:22px;border-radius:14px;border:1px solid #e4e7ed}h2{font-size:19px}small,p{color:#687386}</style></head><body><main><p>好设计 / 项目库</p><h1>探索项目与设计知识</h1><p>项目介绍与档案可直接阅读。资料下载与管理需要登录；研究整理不等于专家审核或工程验证。</p><input id="search" aria-label="检索项目" placeholder="搜索项目、年份或单位"><div class="grid">'+cards+'</div><p><a href="/inno/admin/">资料管理（需登录）</a></p></main><script>document.getElementById("search").oninput=function(){const q=this.value.toLowerCase();document.querySelectorAll("article").forEach(x=>x.hidden=!x.textContent.toLowerCase().includes(q))}</script></body></html>'
            self.send(200,body,'text/html; charset=utf-8');return
        if path=='/admin/':self.path='/'+(('?'+self.path.split('?',1)[1]) if '?' in self.path else '')
        super().do_GET()
    def do_POST(self):self.send(403,dict(error='云端是只读资料快照；上传、清洗与研究发布请使用本机后台。'))
    do_PUT=do_PATCH=do_DELETE=do_POST
    def send(self,status,body,ctype='application/json; charset=utf-8',extra=None):
        if ctype.startswith(('text/html','text/javascript','application/javascript')):
            if isinstance(body,bytes):body=body.decode('utf-8')
            if isinstance(body,str):
                body=prefixed(body)
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
