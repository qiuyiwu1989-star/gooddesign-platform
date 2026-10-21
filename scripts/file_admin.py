# coding: utf-8
"""033: loopback-only private source file manager. No public deployment."""
import argparse,concurrent.futures,json,mimetypes,os,secrets,threading,urllib.parse
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import project_pipeline as pipe
ROOT=Path(__file__).resolve().parents[1]
class Store:
 def __init__(self,lib,inbox):
  self.lib=lib;self.inbox=inbox;self.folder=lib/'.file-admin';self.folder.mkdir(exist_ok=True);self.file=self.folder/'jobs.json';self.mutex=threading.RLock();self.pool=concurrent.futures.ThreadPoolExecutor(max_workers=2);self.token=secrets.token_urlsafe(32)
  self.jobs=pipe.load(self.file)if self.file.exists()else []
  for j in self.jobs:
   if j['status']in ('queued','running'):j.update(status='interrupted',error='服务上次停止，任务中断；请重试')
  self.persist()
 def persist(self):pipe.save(self.file,self.jobs)
 def submit(self,pid,kind,**args):
  pipe.project(self.lib,pid)
  with self.mutex:
   j=dict(id=secrets.token_hex(8),project_id=pid,kind=kind,args=args,status='queued',created_at=pipe.now(),error=None,result=None);self.jobs.append(j);self.persist()
  self.pool.submit(self.run,j['id']);return dict(j)
 def run(self,jid):
  with self.mutex:
   j=next(j for j in self.jobs if j['id']==jid);j.update(status='running',started_at=pipe.now());self.persist()
  try:
   with pipe.lock(self.lib):
    if j['kind']=='fetch':result=pipe.fetch(self.lib,self.inbox,j['project_id'],j['args']['url'])
    elif j['kind']=='ingest':result=pipe.ingest(pipe.project(self.lib,j['project_id']),Path(j['args']['path']),j['args'].get('origin'),retry=j['args'].get('retry',False))
    else:raise ValueError('未知任务类型')
   status='failed'if result['status']in ('conversion_failed','empty_needs_review','unsupported_needs_review','partial_text_needs_review')else 'completed'
   # Conversion states are also visible per file; completed means the requested operation finished.
   if result['status']not in ('text_extracted','duplicate'):status='needs_attention'
   with self.mutex:j.update(status=status,result=result,finished_at=pipe.now());self.persist()
  except Exception as exc:
   with self.mutex:j.update(status='failed',error=str(exc)[:1000],finished_at=pipe.now());self.persist()
 def upload(self,pid,name,data):
  pipe.project(self.lib,pid)
  if not name or '/'in name or '\\'in name or any(ord(c)<32 for c in name)or len(name)>200:raise ValueError('文件名无效')
  if len(data)>pipe.MAX_BYTES:raise ValueError('单个文件最多30MB')
  ext=Path(name).suffix.lower()
  if len(ext)>12:raise ValueError('扩展名过长')
  folder=self.inbox/pid;folder.mkdir(parents=True,exist_ok=True)
  dest=folder/('upload-'+pipe.sha(data)[:16]+ext)
  origin=dict(kind='local_upload',filename=name,uploaded_at=pipe.now())
  with pipe.lock(self.lib):
   pipe.save(dest.with_name(dest.name+'.origin.json'),origin);part=dest.with_name('.'+dest.name+'.part');part.write_bytes(data);os.replace(part,dest)
  return self.submit(pid,'ingest',path=str(dest),origin=origin)
 def files(self,pid):
  p=pipe.project(self.lib,pid);s=pipe.state(p);rows=[]
  paperpath=p/'论文原文管理/论文原件清单.json';papers=pipe.load(paperpath)['items']if paperpath.exists()else [];paper_map={x.get('library_source_id'):x for x in papers if x.get('library_source_id')}
  mapping=pipe.load(p/'资料关联.json').get('source_titles',{})if (p/'资料关联.json').exists()else {}
  for x in s['sources'].values():
   origin=x.get('origin',{});name=origin.get('filename')or x['title'];paper=paper_map.get(x['id']);ext=Path(x['original']).suffix.lower().lstrip('.')
   rows.append(dict(id=x['id'],name=paper['title']+'.'+ext if paper else (mapping[origin['url']]+'.'+ext if origin.get('kind')!='source_reference'and origin.get('url')in mapping else name),format=ext,bytes=x['bytes'],status=x['status'],error=x.get('error'),chunks=x['chunk_count'],imported_at=x['imported_at'],url=origin.get('url')or origin.get('requested_url'),kind='source_reference'if origin.get('kind')=='source_reference'else 'paper'if paper else 'file',sha256=x['sha256'],read_scope=x['read_scope'],review_status=x['review_status'],origin=origin,paper_id=paper['paper_id']if paper else None))
  return dict(project_id=pid,revision='ingest-%06d'%s['revision'],files=rows,papers=papers,merge_required=s.get('document_merge_required',[]))
 def asset(self,pid,sid,kind):
  p=pipe.project(self.lib,pid);x=pipe.state(p)['sources'].get(sid)
  if not x:raise ValueError('来源不存在')
  if kind not in ('original','document','chunks','metadata'):raise ValueError('文件类型无效')
  rel=str(Path(x['original']).parent/'metadata.json')if kind=='metadata'else x[kind]
  path=pipe.safe(p,rel)
  if not path.is_file():raise ValueError('文件不存在')
  return path,x
class Handler(BaseHTTPRequestHandler):
 def setup(self):
  super().setup();self.connection.settimeout(35)
 def log_message(self,*args):pass
 def send(self,status,body,ctype='application/json; charset=utf-8',extra=None):
  if not isinstance(body,bytes):body=json.dumps(body,ensure_ascii=False).encode()
  self.send_response(status);self.send_header('Content-Type',ctype);self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.send_header('X-Frame-Options','DENY');self.send_header('Referrer-Policy','no-referrer');self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'none'")
  for k,v in (extra or {}).items():self.send_header(k,v)
  self.end_headers();self.wfile.write(body)
 def guard(self,write=False):
  expected='127.0.0.1:'+str(self.server.server_port)
  if self.headers.get('Host')!=expected:raise PermissionError('仅允许本地地址访问')
  if write and (self.headers.get('Origin')!='http://'+expected or not secrets.compare_digest(self.headers.get('X-CSRF-Token',''),self.server.store.token)):raise PermissionError('写入请求需从本地后台发起')
 def do_GET(self):
  try:
   self.guard();u=urllib.parse.urlsplit(self.path);q=urllib.parse.parse_qs(u.query);one=lambda k,d='':q.get(k,[d])[0];store=self.server.store
   if u.path=='/favicon.ico':self.send(204,b'','image/x-icon');return
   if u.path in ('/','/app.js','/style.css'):
    name={'/':'index.html','/app.js':'app.js','/style.css':'style.css'}[u.path];p=ROOT/'extensions/file-admin'/name;self.send(200,p.read_bytes(),mimetypes.guess_type(name)[0]+'; charset=utf-8');return
   if u.path=='/api/projects':self.send(200,dict(projects=pipe.load(store.lib/'项目索引.json')['projects'],token=store.token));return
   if u.path=='/api/files':self.send(200,store.files(one('project','2025-00')));return
   if u.path=='/api/jobs':
    with store.mutex:rows=[dict(j)for j in store.jobs if j['project_id']==one('project','2025-00')][-100:][::-1]
    # Internal filesystem paths are not needed by the client.
    self.send(200,dict(jobs=[dict(j,args={k:v for k,v in j['args'].items()if k!='path'})for j in rows]));return
   if u.path in ('/api/pdf-info','/api/pdf-page'):
    import fitz
    path,x=store.asset(one('project'),one('source'),'original')
    if path.suffix.lower()!='.pdf':raise ValueError('此文件不是PDF')
    with fitz.open(str(path))as doc:
     if u.path=='/api/pdf-info':self.send(200,dict(pages=len(doc)));return
     number=int(one('page','0'))
     if not 0<=number<len(doc):raise ValueError('页码超出范围')
     page=doc[number];scale=min(1.5,1200/max(page.rect.width,1),1600/max(page.rect.height,1));pixels=page.get_pixmap(matrix=fitz.Matrix(scale,scale),alpha=False)
     self.send(200,pixels.tobytes('png'),'image/png');return
   if u.path=='/api/preview':
    path,x=store.asset(one('project'),one('source'),'chunks');blocks=pipe.load(path);self.send(200,dict(blocks=blocks[:200],total=len(blocks),truncated=len(blocks)>200));return
   if u.path=='/asset':
    path,x=store.asset(one('project'),one('source'),one('kind','original'));name=x['origin'].get('filename',x['title'])if x.get('origin')else x['title'];name=name if one('kind','original')=='original'else path.name
    self.send(200,path.read_bytes(),'application/octet-stream',{'Content-Disposition':"attachment; filename*=UTF-8''"+urllib.parse.quote(name,safe='')});return
   self.send(404,dict(error='页面不存在'))
  except PermissionError as exc:self.send(403,dict(error=str(exc)))
  except (ValueError,KeyError,FileNotFoundError)as exc:self.send(400,dict(error=str(exc)))
  except Exception:self.send(500,dict(error='读取失败，请检查文件与硬盘状态'))
 def do_POST(self):
  try:
   self.guard(True);u=urllib.parse.urlsplit(self.path);q=urllib.parse.parse_qs(u.query);one=lambda k,d='':q.get(k,[d])[0];store=self.server.store
   length=int(self.headers.get('Content-Length','-1'))
   if length<0 or length>pipe.MAX_BYTES:raise ValueError('请求大小需在30MB以内')
   data=self.rfile.read(length)
   if len(data)!=length:raise ValueError('上传未完成')
   pid=one('project','2025-00');pipe.project(store.lib,pid)
   if u.path=='/api/upload':self.send(202,store.upload(pid,one('name'),data));return
   args=json.loads(data)
   if u.path=='/api/fetch':
    url=args.get('url','');pipe.public_url(url);self.send(202,store.submit(pid,'fetch',url=url));return
   if u.path=='/api/retry':
    with store.mutex:old=next((j for j in store.jobs if j['id']==args.get('job_id')and j['project_id']==pid),None)
    if not old or old['status']in ('queued','running'):raise ValueError('任务不可重试')
    retry_args=dict(old['args'])
    if old['kind']=='ingest':retry_args['retry']=True
    self.send(202,store.submit(pid,old['kind'],**retry_args));return
   self.send(404,dict(error='操作不存在'))
  except PermissionError as exc:self.send(403,dict(error=str(exc)))
  except (ValueError,KeyError,TypeError)as exc:self.send(400,dict(error=str(exc)))
  except Exception:self.send(500,dict(error='处理失败，请检查文件与硬盘状态'))
def server(lib=pipe.LIB,inbox=pipe.INBOX,port=8776):
 srv=ThreadingHTTPServer(('127.0.0.1',port),Handler);srv.store=Store(lib,inbox);return srv
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--port',type=int,default=8776);a=ap.parse_args();srv=server(port=a.port);print('私有文件管理：http://127.0.0.1:%d/'%srv.server_port,flush=True)
 try:srv.serve_forever()
 finally:srv.server_close();srv.store.pool.shutdown(wait=True)
