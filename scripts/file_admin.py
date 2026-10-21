# coding: utf-8
"""033: loopback-only private source file manager. No public deployment."""
import argparse,concurrent.futures,json,re,mimetypes,os,secrets,threading,time,urllib.parse,subprocess
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import project_pipeline as pipe
import project_ownership as ownership
import research_workflow as research
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
   if j['kind']in ('ocr','extract','process'):
    result=getattr(research,j['kind'])(self.lib,j['project_id'],j['args']['source_id'],j['args'].get('actor','后台操作员'))
   elif j['kind']=='method_demo':
    if j['project_id']!='2025-00':raise ValueError('当前固定示例仅使用嫦娥项目')
    execution=subprocess.run([str(ROOT/'.runtime/pipeline/bin/python'),str(ROOT/'scripts/run_method_case_demo.py')],cwd=str(ROOT),capture_output=True,text=True,timeout=180)
    if execution.returncode:raise ValueError('双库示例运行失败，请检查版本/证据或查看脚本日志：'+execution.stderr[-900:])
    result=json.loads(execution.stdout)
   elif j['kind']=='publish':result=research.publish(self.lib,j['project_id'],j['args']['actor'],j['args']['reason'])
   else:
    with pipe.lock(self.lib):
     if j['kind']=='fetch':result=pipe.fetch(self.lib,self.inbox,j['project_id'],j['args']['url'])
     elif j['kind']=='ingest':result=pipe.ingest(pipe.project(self.lib,j['project_id']),Path(j['args']['path']),j['args'].get('origin'),retry=j['args'].get('retry',False))
     else:raise ValueError('未知任务类型')
   if j['kind']in ('ingest','fetch')and result.get('source_id'):
    try:result['research']=research.process(self.lib,j['project_id'],result['source_id'],'后台自动处理（未审核）')
    except Exception as exc:result['research_error']=str(exc)
   status='failed'if result['status']in ('conversion_failed','empty_needs_review','unsupported_needs_review','partial_text_needs_review')else 'completed'
   # Conversion states are also visible per file; completed means the requested operation finished.
   if result['status']not in ('text_extracted','duplicate','completed','published','no_changes'):status='needs_attention'
   if result.get('research_error'):status='needs_attention'
   with self.mutex:j.update(status=status,result=result,finished_at=pipe.now());self.persist()
  except Exception as exc:
   with self.mutex:j.update(status='failed',error=str(exc)[:1000],finished_at=pipe.now());self.persist()
 def start_watch(self):
  cursor_file=self.folder/'research-watch.json'
  cursor=pipe.load(cursor_file)if cursor_file.exists()else {}
  # First launch establishes a cursor, rather than silently researching the entire old library.
  for row in pipe.load(self.lib/'项目索引.json')['projects']:
   if row['id']not in cursor:cursor[row['id']]=list(pipe.state(pipe.project(self.lib,row['id']))['sources'])
  pipe.save(cursor_file,cursor);self.watch_stop=threading.Event()
  def watch():
   while not self.watch_stop.is_set():
    try:
     with pipe.lock(self.lib):pipe.scan(self.lib,self.inbox)
     for row in pipe.load(self.lib/'项目索引.json')['projects']:
      pid=row['id'];p=pipe.project(self.lib,pid);active=ownership.select(p,pipe.state(p)['sources']);seen=set(cursor.get(pid,[]))
      for sid,x in active.items():
       if sid not in seen:
        self.submit(pid,'process',source_id=sid,actor='投递箱自动处理（未审核）');seen.add(sid)
      cursor[pid]=sorted(seen)
     pipe.save(cursor_file,cursor);pipe.save(self.lib/'监听状态.json',dict(pid=os.getpid(),heartbeat=pipe.now(),inbox=str(self.inbox),service='file_admin_with_research_pipeline'))
    except Exception as exc:pipe.save(self.folder/'watch-error.json',dict(time=pipe.now(),error=str(exc)))
    self.watch_stop.wait(4)
  self.watch_thread=threading.Thread(target=watch,daemon=True);self.watch_thread.start()
 def upload(self,pid,name,data):
  current_p=pipe.project(self.lib,pid)
  existing=pipe.state(current_p)['sources'];sid='S'+pipe.sha(data)[:16]
  if sid in existing and ownership.assignment(current_p,sid,existing)['scope']!='project':raise ValueError('相同文件已登记在公共参考、其他项目或待确认范围，请先查看资料归属记录')
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
 def files(self,pid,scope='project'):
  p=pipe.project(self.lib,pid);s=pipe.state(p);rows=[]
  paperpath=p/'论文原文管理/论文原件清单.json';papers=pipe.load(paperpath)['items']if paperpath.exists()else [];paper_map={x.get('library_source_id'):x for x in papers if x.get('library_source_id')}
  patentpath=p/'专利原文管理/专利原件清单.json';patents=pipe.load(patentpath)['items']if patentpath.exists()else [];patent_map={sid:v for v in patents for sid in [v['library_source_id']]+v.get('related_source_ids',[])}
  imagepath=p/'图片素材/图片清单.json';images=pipe.load(imagepath)['items']if imagepath.exists()else [];image_map={v['library_source_id']:v for v in images}
  mapping=pipe.load(p/'资料关联.json').get('source_titles',{})if (p/'资料关联.json').exists()else {}
  for x in s['sources'].values():
   origin=x.get('origin',{});name=origin.get('filename')or x['title'];paper=paper_map.get(x['id']);ext=Path(x['original']).suffix.lower().lstrip('.')
   rows.append(dict(id=x['id'],name=paper['title']+'.'+ext if paper else (mapping[origin['url']]+'.'+ext if origin.get('kind')!='source_reference'and origin.get('url')in mapping else name),format=ext,bytes=x['bytes'],status=x['status'],error=x.get('error'),chunks=x['chunk_count'],imported_at=x['imported_at'],url=origin.get('url')or origin.get('requested_url'),kind='source_reference'if origin.get('kind')=='source_reference'else 'paper'if paper else 'file',sha256=x['sha256'],read_scope=x['read_scope'],review_status=x['review_status'],origin=origin,paper_id=paper['paper_id']if paper else None))
   patent=patent_map.get(x['id'])
   if patent and origin.get('kind')!='source_reference':rows[-1].update(kind='patent',name=patent['publication']+'-'+patent['title']+'.'+ext,patent_id=patent['patent_id'],publication=patent['publication'],project_relation='技术关联候选；获奖项目成果归属待确认，实际装机未知',document_role='专利文本PDF'if ext=='pdf'else '专利检索网页')
   image=image_map.get(x['id'])
   if not image and ext in ['png','jpg','jpeg','webp','gif','bmp','tif','tiff']:
    try:
     from PIL import Image
     with Image.open(pipe.safe(p,x['original']))as im:im.load();width,height=im.size
     image=dict(title=name,kind='web_image'if origin.get('url')else 'uploaded_image',width=width,height=height,locations=[dict(source_id=x['id'],image_url=origin.get('url'),method='uploaded_or_downloaded_original')],preview_status='ready')
    except Exception:pass
   if image:rows[-1].update(kind='image',name=image['title'],status='image_archived'if image.get('preview_status','ready')=='ready'else 'image_needs_review',image_preview_status=image.get('preview_status','ready'),image_preview_error=image.get('preview_error'),conversion_status=x['status'],image_kind=image['kind'],image_width=image['width'],image_height=image['height'],image_locations=image['locations'])
  reg=ownership.registry(p);counts={key:0 for key in ownership.SCOPES}
  for row in rows:
   entry=ownership.assignment(p,row['id'],s['sources'],reg);row['ownership']=entry;counts[entry['scope']]+=1
  if scope not in ownership.SCOPES:raise ValueError('资料范围无效')
  rows=[x for x in rows if x['ownership']['scope']==scope]
  return dict(scope=scope,ownership_counts=counts,ownership_version=reg.get('version',0),project_id=pid,revision='ingest-%06d'%s['revision'],files=rows,papers=papers,patents=patents,merge_required=s.get('document_merge_required',[]))
 def asset(self,pid,sid,kind,scope='project'):
  p=pipe.project(self.lib,pid);x=pipe.state(p)['sources'].get(sid)
  if not x:raise ValueError('来源不存在')
  if sid not in ownership.select(p,pipe.state(p)['sources'],scope):raise ValueError('该资料不属于当前资料范围，请从正确项目或归属记录查看')
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
  csp="default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'none'"
  if isinstance(body,str)and not ctype.startswith('application/json'):body=body.encode('utf-8')
  if not isinstance(body,bytes):body=json.dumps(body,ensure_ascii=False).encode()
  if ctype.startswith('text/html'):
   # Only trusted application templates are served as HTML. Raw uploads remain attachments.
   nonce=secrets.token_urlsafe(24);text=body.decode('utf-8')
   text=re.sub(r'<(style|script)(?=[\s>])',lambda m:'<'+m[1]+' nonce="'+nonce+'"',text)
   body=text.encode('utf-8');csp="default-src 'self'; script-src 'self' 'nonce-"+nonce+"'; style-src 'self' 'nonce-"+nonce+"'; img-src 'self' data:; connect-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'none'"
  self.send_response(status);self.send_header('Content-Type',ctype);self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.send_header('X-Frame-Options','DENY');self.send_header('Referrer-Policy','no-referrer');self.send_header('Content-Security-Policy',csp)
  for k,v in (extra or {}).items():self.send_header(k,v)
  self.end_headers();self.wfile.write(body)
 def guard(self,write=False):
  expected='127.0.0.1:'+str(self.server.server_port)
  if self.headers.get('Host')!=expected:raise PermissionError('仅允许本地地址访问')
  if write and (self.headers.get('Origin')!='http://'+expected or not secrets.compare_digest(self.headers.get('X-CSRF-Token',''),self.server.store.token)):raise PermissionError('写入请求需从本地后台发起')
 def do_GET(self):
  try:
   self.guard();u=urllib.parse.urlsplit(self.path);q=urllib.parse.parse_qs(u.query);one=lambda k,d='':q.get(k,[d])[0];store=self.server.store
   if u.path=='/api/health':self.send(200,dict(service='gooddesign-archive-pipeline',version='1.0.0',research_policy=research.POLICY,ocr_available=(ROOT/'.runtime/vision-ocr').exists(),watcher_running=bool(getattr(store,'watch_thread',None)and store.watch_thread.is_alive())));return
   if u.path=='/favicon.ico':self.send(204,b'','image/x-icon');return
   if u.path in ('/','/app.js','/style.css','/workflow.js','/workflow.css','/workspace.css','/workspace.js'):
    name={'/':'index.html','/app.js':'app.js','/style.css':'style.css','/workflow.js':'workflow.js','/workflow.css':'workflow.css','/workspace.css':'workspace.css','/workspace.js':'workspace.js'}[u.path];p=ROOT/'extensions/file-admin'/name;
    if u.path=='/':
     import workspace_ui
     self.send(200,workspace_ui.admin(p.read_text(encoding='utf-8'),one('project','2025-00')),'text/html; charset=utf-8');return
    self.send(200,p.read_bytes(),mimetypes.guess_type(name)[0]+'; charset=utf-8');return
   if u.path=='/dossier/graph/':
    import workspace_ui
    self.send(200,workspace_ui.graph(),'text/html; charset=utf-8');return
   if u.path=='/dossier/':
    import workspace_ui
    pid=one('project','2025-00');pipe.project(store.lib,pid)
    self.send(200,workspace_ui.dossier(pid),'text/html; charset=utf-8');return
   if u.path.startswith('/methods/'):
    import innovation_methods as methods
    if u.path=='/methods/' and one('project','2025-00')!='2025-00':
     import workspace_ui
     pid=one('project');pipe.project(store.lib,pid)
     self.send(200,workspace_ui.empty(pid,'research','这个项目还没有应用研究','当前固定示例基于嫦娥采样资料。先完成本项目档案，再建立独立的应用研究。'),'text/html; charset=utf-8');return
    if u.path=='/methods/' and one('run','latest')=='latest' and not (methods.RUNS/'latest.json').is_file():
     import workspace_ui
     self.send(200,workspace_ui.empty('2025-00','research','还没有生成应用研究记录','先整理案例资料，再运行示例。已有项目档案和资料文件可以继续阅读。'),'text/html; charset=utf-8');return
    run_id=one('run','latest');data=methods.read_run(run_id,'full');folder=methods.RUNS/data['run_id']
    name={'/methods/':'联动报告.html','/methods/style.css':'style.css','/methods/app.js':'app.js'}.get(u.path)
    if not name:raise ValueError('方法页面不存在')
    path=folder/name;self.send(200,path.read_bytes(),mimetypes.guess_type(name)[0]+'; charset=utf-8');return
   if u.path=='/api/methods':
    import innovation_methods as methods
    self.send(200,methods.search_methods(one('query'),int(one('offset','0')),int(one('limit','10'))));return
   if u.path=='/api/method':
    import innovation_methods as methods
    self.send(200,methods.read_method(one('method_id'),one('version')or None,one('level','overview')));return
   if u.path=='/api/innovation-run':
    import innovation_methods as methods
    self.send(200,methods.read_run(one('run','latest'),one('section','overview')));return
   if u.path=='/api/projects':self.send(200,dict(projects=pipe.load(store.lib/'项目索引.json')['projects'],token=store.token));return
   if u.path=='/api/research':self.send(200,research.status(store.lib,one('project','2025-00')));return
   if u.path=='/api/research-document':
    p=pipe.project(store.lib,one('project','2025-00'));w=research.current(p)
    if not w['revision']:raise ValueError('还没有已发布的研究版本')
    folder,_=research.check_version(p,one('revision')or'research-%06d'%w['revision'])
    names={'archive':'01-项目档案.md','library':'02-资料与解读.md','assessment':'03-档案评估.md','data':'档案.json','changes':'changes.json'}
    if one('document','archive')not in names:raise ValueError('文档名称无效')
    f=folder/names[one('document','archive')];self.send(200,f.read_bytes(),'text/plain; charset=utf-8');return
   if u.path=='/api/files':self.send(200,store.files(one('project','2025-00'),one('scope','project')));return
   if u.path=='/api/jobs':
    with store.mutex:rows=[dict(j)for j in store.jobs if j['project_id']==one('project','2025-00')][-100:][::-1]
    current_p=pipe.project(store.lib,one('project','2025-00'));current_s=pipe.state(current_p);reg=ownership.registry(current_p);requested_scope=one('scope','project')
    if requested_scope not in ownership.SCOPES:raise ValueError('资料范围无效')
    rows=[j for j in rows if ownership.assignment(current_p,j.get('result',{}).get('source_id','')if j.get('result')else '',current_s['sources']if j.get('result')else {'':{'origin':{'url':j['args'].get('url')}}},reg)['scope']==requested_scope]
    # Internal filesystem paths are not needed by the client.
    self.send(200,dict(jobs=[dict(j,args={k:v for k,v in j['args'].items()if k!='path'})for j in rows]));return
   if u.path=='/api/image':
    import io,warnings
    from PIL import Image,ImageOps
    path,x=store.asset(one('project'),one('source'),'original',one('scope','project'))
    with warnings.catch_warnings():
     warnings.simplefilter('error',Image.DecompressionBombWarning)
     with Image.open(path)as original:
      image=ImageOps.exif_transpose(original);image.thumbnail((120,120)if one('thumb')=='1'else (1600,1600));out=io.BytesIO();image.convert('RGB').save(out,format='PNG');self.send(200,out.getvalue(),'image/png');return
   if u.path in ('/api/pdf-info','/api/pdf-page'):
    import fitz
    path,x=store.asset(one('project'),one('source'),'original',one('scope','project'))
    if path.suffix.lower()!='.pdf':raise ValueError('此文件不是PDF')
    with fitz.open(str(path))as doc:
     if u.path=='/api/pdf-info':self.send(200,dict(pages=len(doc)));return
     number=int(one('page','0'))
     if not 0<=number<len(doc):raise ValueError('页码超出范围')
     page=doc[number];scale=min(1.5,1200/max(page.rect.width,1),1600/max(page.rect.height,1));pixels=page.get_pixmap(matrix=fitz.Matrix(scale,scale),alpha=False)
     self.send(200,pixels.tobytes('png'),'image/png');return
   if u.path=='/api/preview':
    path,x=store.asset(one('project'),one('source'),'chunks',one('scope','project'));blocks=pipe.load(path);self.send(200,dict(blocks=blocks[:200],total=len(blocks),truncated=len(blocks)>200));return
   if u.path=='/asset':
    path,x=store.asset(one('project'),one('source'),one('kind','original'),one('scope','project'));name=x['origin'].get('filename',x['title'])if x.get('origin')else x['title'];name=next((f['name']for f in store.files(one('project'),one('scope','project'))['files']if f['id']==x['id']),name)if one('kind','original')=='original'else path.name
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
   if one('scope','project')!='project':raise ValueError('请先切换到本项目资料再提交处理任务')
   if u.path=='/api/upload':self.send(202,store.upload(pid,one('name'),data));return
   args=json.loads(data)
   if u.path=='/api/fetch':
    url=args.get('url','');pipe.public_url(url);self.send(202,store.submit(pid,'fetch',url=url));return
   if u.path=='/api/method-demo':
    if pid!='2025-00':raise ValueError('当前示例固定为嫦娥知识迁移模拟任务')
    self.send(202,store.submit(pid,'method_demo',actor=args.get('actor','本地用户重放固定示例')));return
   if u.path in ('/api/ocr','/api/extract','/api/process'):
    research.source(pipe.project(store.lib,pid),args['source_id']);self.send(202,store.submit(pid,u.path.rsplit('/',1)[1],source_id=args['source_id'],actor=args.get('actor','后台操作员')));return
   if u.path=='/api/candidate':self.send(201,research.propose(store.lib,pid,args['candidate'],args['actor']));return
   if u.path=='/api/review':self.send(200,research.review(store.lib,pid,args['candidate_id'],args['decision'],args['actor'],args['reason']));return
   if u.path=='/api/publish':self.send(202,store.submit(pid,'publish',actor=args['actor'],reason=args['reason']));return
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
 srv.store.start_watch()
 try:srv.serve_forever()
 finally:
  srv.store.watch_stop.set();srv.store.watch_thread.join(timeout=10);srv.server_close();srv.store.pool.shutdown(wait=True)
