"""064 authenticated remote READ-ONLY facade; local MCP remains unchanged."""
import os,json,hashlib,secrets,functools
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
import innovation_gateway_mcp as local
import innovation_gateway as g

MCP=FastMCP('gooddesign-innovation-remote',stateless_http=True,json_response=True,max_request_body_size=131072,transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=True,allowed_hosts=['opendesign.cc','haoshejiguan.com','www.haoshejiguan.com','mcp.haosheji.cc','127.0.0.1:18779','localhost:18779'],allowed_origins=['https://opendesign.cc','https://haoshejiguan.com','https://www.haoshejiguan.com','https://mcp.haosheji.cc']))
READ={'readOnlyHint':True,'destructiveHint':False,'idempotentHint':True,'openWorldHint':False}
@MCP.tool(annotations=READ)
def inno_capabilities()->dict:
 """远程统一入口：12项只读工具，数据在服务器，不依赖客户端硬盘。"""
 from mcp_research_services import quality_envelope
 return quality_envelope(dict(version='1.0-research-readonly',transport='streamable_http',tools=12,read_only=True,workflow=['inno_search_projects / inno_search_methods','inno_read_project / inno_read_method','inno_search_fields / inno_read_evidence','inno_prepare_research'],model_calls=0,persistent_plan_or_private_history_available=False,notice='研究包是上下文与步骤，不是自动研究或工程结论。'),'inno_capabilities')
def scrub(value):
 if isinstance(value,dict):return {k:scrub(v)for k,v in value.items()if k not in {'chunks_path','original_path','raw_path','local_path','workspace_path','actor','reviewer'}}
 if isinstance(value,list):return [scrub(x)for x in value]
 if isinstance(value,str):
  if value.startswith(('/Volumes/','/Users/','/var/lib/','/var/www/')):return '[内部路径不提供]'
  import re
  return re.sub(r'\]\(<?/(?:Volumes|Users|var/lib|var/www)/[^)\n]+>?\)', ']([内部文档链接省略])', value)
 return value

def remote_call(fn):
 @functools.wraps(fn)
 def wrapped(*args,**kwargs):
  try:result=scrub(fn(*args,**kwargs))
  except Exception as e:
   if isinstance(e,ValueError)and not any(x in str(e)for x in ['/Volumes/','/Users/','/var/lib/','/var/www/']):raise
   raise ValueError('读取未完成，请检查项目ID、版本和资料范围；'+type(e).__name__)from None
  if isinstance(result,dict)and 'packet'in result:
   result['packet']['access_profile']='remote_read_only_no_saved_history';result['packet_sha256']=g.digest(result['packet'])
  from mcp_research_services import quality_envelope
  return g.bounded(quality_envelope(result,fn.__name__))
 return wrapped

for name in ['inno_search_projects','inno_search_methods','inno_read_project','inno_search_fields','inno_read_method','inno_prepare_research','inno_read_claim_evidence','inno_read_mechanism','inno_prepare_transfer','inno_read_method_asset']:
 MCP.add_tool(remote_call(getattr(local,name)),name=name,annotations=READ)

@MCP.tool(annotations=READ)
def inno_read_evidence(project_id:str,source_id:str,revision:str,offset:int=0,limit:int=2,chunks_sha256:str|None=None)->dict:
 """远程仅返回此发布版本实际引用的逐字证据片段，不开放整份原文块或原件下载。"""
 if not g.re.fullmatch(r'research-[0-9]{6}',revision):raise ValueError('须指定research-六位数字版本')
 g.projects.bounds(offset,limit)
 p=g.pp.project(g.projects.LIB,project_id);g.rw.source(p,source_id)
 from research_handoff_check import evidence_nodes
 data=g.rw.dataset(p,revision=revision);refs=[x for x in evidence_nodes(data)if x['source_id']==source_id]
 if chunks_sha256:refs=[x for x in refs if x['chunks_sha256']==chunks_sha256]
 if not refs:raise ValueError('此版本没有引用该来源或文本指纹，不能读取整份资料')
 variants={x['chunks_sha256']for x in refs}
 if len(variants)>1:raise ValueError('来源有多个文本修订，请传记录中的chunks_sha256')
 seen=set();quotes=[]
 for e in refs:
  path=g.pp.safe(p,e['chunks_path']);assert g.pp.sha(path.read_bytes())==e['chunks_sha256'],'冻结文本指纹不符'
  blocks=g.pp.load(path);block=next((x for x in blocks if x['id']==e['chunk_id']),None)
  if not block or e['quote']not in block['text']:raise ValueError('冻结引用与原文不一致')
  key=(e['chunk_id'],e['quote'])
  if key in seen:continue
  seen.add(key);quotes.append(dict(chunk_id=e['chunk_id'],quote=e['quote'],locator=block.get('locator'),source_sha256=e['source_sha256'],chunks_sha256=e['chunks_sha256']))
 from mcp_research_services import quality_envelope
 return g.bounded(quality_envelope(dict(project_id=project_id,source_id=source_id,revision=revision,scope='published_quoted_excerpts_only_not_full_source',**g.projects.page(quotes,offset,limit)),'inno_read_evidence'))

@MCP.resource('gooddesign://schemas/quality-envelope')
def quality_schema_resource()->str:
 from mcp_method_assets import schema_resource
 return json.dumps(schema_resource('quality_states'),ensure_ascii=False)

@MCP.prompt()
def evidence_review()->str:
 from mcp_method_assets import workflow_prompt
 return workflow_prompt('evidence_review')['text']

@MCP.prompt()
def method_application()->str:
 from mcp_method_assets import workflow_prompt
 return workflow_prompt('method_application')['text']

SAFE_ARGS={'query','project_ids','method_ids','keywords','section','revision','entity','limit'}
def args_summary(arguments):
 if not isinstance(arguments,dict):return ''
 parts=[]
 for k in SAFE_ARGS:
  if k in arguments:parts.append(f"{k}={str(arguments[k])[:120]}")
 return ';'.join(parts)[:300]

class BearerAuth:
 def __init__(self,app,keys_file,registry_path=None):
  self.app=app;self.keys_file=Path(keys_file)
  self.registry_path=Path(registry_path) if registry_path else None
 def identify(self,headers):
  """返回 (key_id 或 None, 拒绝原因或 None)。已配置注册表则必须可读且有效；仅未配置注册表时兼容 keys.json。"""
  h={k.lower():v for k,v in headers};value=h.get(b'authorization',b'')
  if not value.startswith(b'Bearer ')or not 1<=len(value[7:])<=256:return None,'malformed'
  token=value[7:]
  if self.registry_path:
   if not self.registry_path.is_file():return None,'registry_unavailable'
   import mcp_key_registry as reg
   try:
    db=reg.connect(self.registry_path)
    try:key_id,status=reg.resolve(db,token.decode())
    finally:db.close()
   except (OSError,ValueError,UnicodeError,reg.sqlite3.Error):return None,'registry_unavailable'
   if status=='active':return key_id,None
   return None,status
  supplied=hashlib.sha256(token).hexdigest()
  try:entries=json.loads(self.keys_file.read_text())['keys']
  except (OSError,ValueError,KeyError,TypeError):return None,'registry_unavailable'
  if not isinstance(entries,list):return None,'registry_unavailable'
  ok=any(isinstance(x,dict)and x.get('enabled')is True and isinstance(x.get('sha256'),str)and g.re.fullmatch(r'[0-9a-f]{64}',x['sha256'])and secrets.compare_digest(supplied,x['sha256'])for x in entries)
  return ('legacy',None) if ok else (None,'unknown')
 async def __call__(self,scope,receive,send):
  if scope['type']!='http':
   await self.app(scope,receive,send);return
  key_id,reason=self.identify(scope.get('headers',[]))
  if not key_id:
   import sys
   from mcp_access_diagnostics import deny
   denied=deny(reason,log=lambda line:print(line,file=sys.stderr))
   body=json.dumps(denied['body']).encode()
   headers=[(b'content-type',b'application/json')]+[(k.lower().encode(),v.encode()) for k,v in denied['headers'].items()]
   await send({'type':'http.response.start','status':401,'headers':headers});await send({'type':'http.response.body','body':body});return
  # 缓冲请求体以提取工具名与参数摘要（仅白名单字段），再回放给下游
  body_chunks=[];more=True
  while more:
   msg=await receive()
   if msg['type']!='http.request':break
   body_chunks.append(msg.get('body',b''));more=msg.get('more_body',False)
  raw=b''.join(body_chunks)
  sent=[False]
  async def replay():
   if not sent[0]:
    sent[0]=True
    return {'type':'http.request','body':raw,'more_body':False}
   return await receive()  # 后续调用（含 http.disconnect）交给原始通道，不能返回即时空消息，否则 SSE 轮询会自旋
  tool='';summary=''
  try:
   rpc=json.loads(raw) if raw else {}
   if rpc.get('method')=='tools/call':
    tool=str(rpc.get('params',{}).get('name',''))
    summary=args_summary(rpc.get('params',{}).get('arguments',{}))
  except ValueError:pass
  status=[0]
  async def send_capture(message):
   if message['type']=='http.response.start':status[0]=message['status']
   await send(message)
  import time
  t0=time.monotonic()
  try:
   await self.app(scope,replay,send_capture)
  finally:
   # 下游在响应完成后可能抛断连异常，使用记录必须仍然落库
   latency=int((time.monotonic()-t0)*1000)
   if self.registry_path and self.registry_path.is_file():
    try:
     import mcp_key_registry as reg
     db=reg.connect(self.registry_path)
     try:reg.log_usage(db,key_id,tool,summary,status[0],latency)
     finally:db.close()
    except Exception:pass  # 使用记录失败不阻断请求

def app(keys_file,registry_path=None):return BearerAuth(MCP.streamable_http_app(),keys_file,registry_path)
if __name__=='__main__':
 import uvicorn
 keys=os.environ.get('GOODDESIGN_MCP_KEYS_FILE','/etc/innovation-mcp/keys.json')
 registry=os.environ.get('GOODDESIGN_MCP_REGISTRY','/etc/innovation-mcp/registry.sqlite3')
 if not Path(registry).is_file() and not Path(keys).is_file():raise SystemExit('Remote MCP access-key registry missing; refusing to start')
 uvicorn.run(app(keys,registry),host='127.0.0.1',port=18779,access_log=False,proxy_headers=False)
