"""ML024 private loopback preview, no generic file serving or production deployment."""
import json
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlparse,parse_qs
from innovation_loop_store import LoopStore,ROOT,digest
from innovation_loop_evidence import verify_experience_files
from innovation_loop_experience import load_experiences
from innovation_loop_decision import compare_routes
from innovation_loop_page import page

def checked_experiences():
 records=load_experiences(ROOT/'output/innovation-loop-024/experience/active-experience-catalog-v1.json')
 for record in records:verify_experience_files(record)
 return records

def bundle(task_id='rubber-v1'):
 from innovation_loop_tasks import load_task,list_tasks
 from method_engine_cognition import read_deep_method
 task=load_task(task_id);s=LoopStore();r=task['requirement'];rq=s.get('requirement',r['id'],r['revision'])
 routes=[s.get('route',r['id'],r['revision']) for r in task['routes']]
 if digest(rq)!=digest(task['requirement']) or any(digest(a)!=digest(b) for a,b in zip(routes,task['routes'])):raise ValueError('task_store_version_mismatch')
 ref={'id':rq['id'],'revision':rq['revision']};ids={r['id'] for r in routes}
 methods=[]
 for mid in ['R48','R14','R17']:
  m=read_deep_method(mid);methods.append({k:m[k] for k in ['method_id','name','content_sha256','scope']})
 return {'tasks':list_tasks(),'current_task_id':task_id,'requirement':rq,'routes':routes,'comparison':compare_routes(rq,routes),'experiences':checked_experiences(),'feedback':[f for f in s.list_records('feedback') if f['requirement_ref']==ref],'claims':[c for c in s.list_records('claim') if c['route_ref']['id'] in ids],'methods':methods,'transfer':{'notice':'本任务尚未逐项完成双侧机制语义验证；不继承教学迁移的适用结论'},'research_action':[s.get('action',a['id'],a['revision']) for a in task['actions']],'notice':task['input_status']+'：当前为平台研究提案，原客户逐字需求和领域批准未取得；经验展示不表示与本任务相关，方法正文未自动执行。'}
class Handler(BaseHTTPRequestHandler):
 def allowed(self):return self.headers.get('Host')==f'127.0.0.1:{self.server.server_port}'
 def respond(self,status,value,ctype='application/json; charset=utf-8'):
  data=value.encode() if isinstance(value,str) else json.dumps(value,ensure_ascii=False,allow_nan=False).encode()
  self.send_response(status);self.send_header('Content-Type',ctype);self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.send_header('X-Frame-Options','DENY');self.end_headers();self.wfile.write(data)
 def do_GET(self):
  if not self.allowed():return self.respond(403,{'error':'invalid_host'})
  try:
   parsed=urlparse(self.path);query=parse_qs(parsed.query);task_id=query.get('task',['rubber-v1'])[0]
   if parsed.path=='/':return self.respond(200,page(bundle(task_id)),'text/html; charset=utf-8')
   if parsed.path=='/api/bundle':return self.respond(200,bundle(task_id))
   if self.path in ['/inno/','/inno/projects/','/inno/methods/','/inno/needs/','/inno/report/','/inno/mcp/','/inno/about/']:
    self.send_response(302);self.send_header('Location','https://opendesign.cc'+self.path);self.end_headers();return
   if self.path=='/inno/portal/system.css':return self.respond(200,(ROOT/'extensions/inno/system.css').read_text(),'text/css; charset=utf-8')
   return self.respond(404,{'error':'not_found'})
  except FileNotFoundError:return self.respond(503,{'error':'资料缺失或外置盘不可读，请恢复资料后重试'})
  except ValueError as e:return self.respond(400,{'error':str(e)})
 def do_POST(self):
  origin=f'http://127.0.0.1:{self.server.server_port}'
  if not self.allowed() or self.headers.get('Origin')!=origin:return self.respond(403,{'error':'invalid_origin'})
  if self.path!='/api/feedback':return self.respond(404,{'error':'not_found'})
  try:
   if self.headers.get('Content-Type','').split(';')[0]!='application/json':raise ValueError('json_required')
   length=int(self.headers.get('Content-Length','0'))
   if not 0<length<=32768:raise ValueError('invalid_length')
   data=json.loads(self.rfile.read(length))
   if not isinstance(data,dict):raise ValueError('object_required')
   return self.respond(200,LoopStore().put('feedback',data, data.get('revision',1)-1))
  except (ValueError,TypeError,KeyError) as e:return self.respond(400,{'error':str(e)})
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=18784);args=p.parse_args();ThreadingHTTPServer(('127.0.0.1',args.port),Handler).serve_forever()
