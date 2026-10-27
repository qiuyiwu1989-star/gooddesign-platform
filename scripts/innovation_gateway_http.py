"""064 authenticated remote READ-ONLY facade; local MCP remains unchanged."""
import os,json,hashlib,secrets,functools
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
import innovation_gateway_mcp as local
import innovation_gateway as g

MCP=FastMCP('gooddesign-innovation-remote',stateless_http=True,json_response=True,max_request_body_size=131072,transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=True,allowed_hosts=['opendesign.cc','127.0.0.1:18779','localhost:18779'],allowed_origins=['https://opendesign.cc']))
READ={'readOnlyHint':True,'destructiveHint':False,'idempotentHint':True,'openWorldHint':False}
@MCP.tool(annotations=READ)
def inno_capabilities()->dict:
 """远程统一入口：8项只读工具，数据在服务器，不依赖客户端硬盘。"""
 return dict(version='0.1.0-remote',transport='streamable_http',tools=8,read_only=True,workflow=['inno_search_projects / inno_search_methods','inno_read_project / inno_read_method','inno_search_fields / inno_read_evidence','inno_prepare_research'],model_calls=0,persistent_plan_or_private_history_available=False,notice='研究包是上下文与步骤，不是自动研究或工程结论。')
def scrub(value):
 if isinstance(value,dict):return {k:scrub(v)for k,v in value.items()if k not in {'chunks_path','original_path','raw_path','local_path','workspace_path','actor','reviewer'}}
 if isinstance(value,list):return [scrub(x)for x in value]
 if isinstance(value,str)and value.startswith(('/Volumes/','/Users/','/var/lib/','/var/www/')):return '[内部路径不提供]'
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
  return g.bounded(result)
 return wrapped

for name in ['inno_search_projects','inno_search_methods','inno_read_project','inno_search_fields','inno_read_method','inno_prepare_research']:
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
 return g.bounded(dict(project_id=project_id,source_id=source_id,revision=revision,scope='published_quoted_excerpts_only_not_full_source',**g.projects.page(quotes,offset,limit)))

class BearerAuth:
 def __init__(self,app,keys_file):self.app=app;self.keys_file=Path(keys_file)
 def allowed(self,headers):
  h={k.lower():v for k,v in headers};value=h.get(b'authorization',b'')
  if not value.startswith(b'Bearer ')or not 1<=len(value[7:])<=256:return False
  supplied=hashlib.sha256(value[7:]).hexdigest()
  try:entries=json.loads(self.keys_file.read_text())['keys']
  except (OSError,ValueError,KeyError,TypeError):return False
  if not isinstance(entries,list):return False
  return any(isinstance(x,dict)and x.get('enabled')is True and isinstance(x.get('sha256'),str)and g.re.fullmatch(r'[0-9a-f]{64}',x['sha256'])and secrets.compare_digest(supplied,x['sha256'])for x in entries)
 async def __call__(self,scope,receive,send):
  if scope['type']=='http' and not self.allowed(scope.get('headers',[])):
   body=b'{"error":"access_key_required","message":"Configure Authorization: Bearer <your access key>."}'
   await send({'type':'http.response.start','status':401,'headers':[(b'content-type',b'application/json'),(b'cache-control',b'no-store'),(b'www-authenticate',b'Bearer realm="OpenDesign MCP"')]});await send({'type':'http.response.body','body':body});return
  await self.app(scope,receive,send)

def app(keys_file):return BearerAuth(MCP.streamable_http_app(),keys_file)
if __name__=='__main__':
 import uvicorn
 keys=os.environ.get('GOODDESIGN_MCP_KEYS_FILE','/etc/innovation-mcp/keys.json')
 if not Path(keys).is_file():raise SystemExit('Remote MCP access-key registry missing; refusing to start')
 uvicorn.run(app(keys),host='127.0.0.1',port=18779,access_log=False,proxy_headers=False)
