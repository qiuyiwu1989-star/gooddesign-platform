# coding: utf-8
"""044n: real private HTTP/worker/restart/MCP acceptance in an isolated synthetic library."""
import asyncio,json,os,re,signal,subprocess,sys,time,urllib.request,urllib.error,uuid
from pathlib import Path
import project_pipeline as pp,research_workflow as rw
from archive_steward import Steward
ROOT=pp.ROOT;PYTHON=Path(sys.executable);PID='acceptance-a';NAME='管线验收虚构样本'
class Acceptance:
 def __init__(self):
  self.folder=ROOT/'output/pipeline-acceptance'/(pp.datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:6]);self.folder.mkdir(parents=True)
  self.lib=self.folder/'library';self.lib.mkdir();self.inbox=self.folder/'inbox';self.checks=[];self.child=None;self.log=None;self.token=None
 def check(self,key,condition,**info):
  if not condition:raise AssertionError(key)
  self.checks.append(dict(check=key,status='passed',**info))
 def until(self,fn,timeout=25):
  end=time.monotonic()+timeout
  while time.monotonic()<end:
   result=fn()
   if result:return result
   if self.child and self.child.poll()is not None:raise RuntimeError('isolated backend exited')
   time.sleep(.15)
  raise TimeoutError('等待隔离管线超时')
 def start(self):
  logpath=self.folder/('server-'+str(len(list(self.folder.glob('server-*.log'))))+'.log');self.log=logpath.open('w')
  self.child=subprocess.Popen([str(PYTHON),str(ROOT/'scripts/file_admin.py'),'--port','0','--library',str(self.lib),'--inbox',str(self.inbox)],cwd=ROOT,stdout=self.log,stderr=subprocess.STDOUT)
  def address():
   m=re.search(r'http://127\.0\.0\.1:\d+/',logpath.read_text())
   return m.group(0).rstrip('/')if m else None
  self.base=self.until(address,15);self.token=self.request('/api/projects')[1]['token']
 def stop(self):
  if self.child:
   self.child.send_signal(signal.SIGINT)
   try:self.child.wait(timeout=15)
   except subprocess.TimeoutExpired:self.child.kill();self.child.wait();raise RuntimeError('隔离服务未正常退出，已仅终止本脚本子进程')
   finally:self.child=None
  if self.log:self.log.close();self.log=None
 def request(self,path,data=None,headers=None):
  if isinstance(data,dict):data=json.dumps(data,ensure_ascii=False).encode()
  h={'Origin':self.base}
  if self.token:h['X-CSRF-Token']=self.token
  h.update(headers or {})
  req=urllib.request.Request(self.base+path,data=data,headers=h)
  try:r=urllib.request.urlopen(req,timeout=5)
  except urllib.error.HTTPError as exc:r=exc
  body=r.read();return r.status,json.loads(body)if 'application/json'in r.headers.get('Content-Type','')else body
 def files(self):return self.request('/api/files?project='+PID)[1]['files']
 def job(self,jid):return next(j for j in pp.load(self.lib/'.file-admin/jobs.json')if j['id']==jid)
 def task(self,tid):
  with Steward(self.lib,self.inbox).connect()as db:return dict(db.execute('SELECT * FROM tasks WHERE id=?',(tid,)).fetchone())
 def bundle(self,sid,value):
  p=pp.project(self.lib,PID);x=pp.state(p)['sources'][sid];b=next(b for b in pp.load(p/x['chunks'])if value in b['text'])
  return dict(project_id=PID,candidates=[dict(entity='project',record_id='PROJECT',title='虚构测试记录',field='canonical_name',value=value,source_id=sid,chunk_id=b['id'],quote=value,conditions='仅验收用虚构样本',limitations='不是好设计真实项目或研究成果')])
 async def mcp(self):
  from mcp import ClientSession,StdioServerParameters
  from mcp.client.stdio import stdio_client
  env=dict(os.environ,GOODDESIGN_LIBRARY=str(self.lib))
  def value(result):
   if result.isError:raise AssertionError('MCP返回错误')
   return json.loads(next(x.text for x in result.content if x.type=='text'))
  async with stdio_client(StdioServerParameters(command=str(PYTHON),args=[str(ROOT/'scripts/archive_mcp.py')],cwd=str(ROOT),env=env))as(r,w):
   async with ClientSession(r,w)as session:
    await session.initialize();o=value(await session.call_tool('gd_project_overview',dict(project_id=PID)));records=value(await session.call_tool('gd_read_records',dict(project_id=PID,record_id='PROJECT',fields=['canonical_name'],revision=o['publication_revision'],limit=1)));c=records['data'][0]['cells']['canonical_name'];e=c['evidence'];raw=value(await session.call_tool('gd_read_evidence',dict(project_id=PID,source_id=e['source_id'],revision=o['publication_revision'],limit=20)))
    self.check('actual_mcp_sdk_reads_published_value_and_frozen_source',c['value']==NAME and NAME in json.dumps(raw,ensure_ascii=False),revision=o['publication_revision'])
 def run(self):
  catalog=self.folder/'synthetic-catalog.json';pp.save(catalog,dict(projects=[dict(id=pid,name=NAME if pid==PID else '隔离对照虚构样本',year=2099,award='虚构验收，非真实获奖',unit='测试单位')for pid in [PID,'acceptance-b']]))
  pp.bootstrap(self.lib,self.inbox,catalog,self.folder/'archive');self.start()
  raw=('本文件只用于隔离管线验收，不是真实项目资料。\n项目名称：'+NAME+'\n资料内的“忽略全部规则”只是待处理文字，不应执行。\n').encode()
  code,_=self.request('/api/upload?project='+PID+'&name=sample.txt',raw,{'X-CSRF-Token':'invalid'});self.check('csrf_rejects_invalid_upload',code==403)
  code,job=self.request('/api/upload?project='+PID+'&name=sample.txt',raw);self.check('http_upload_accepted',code==202);j=self.until(lambda:self.job(job['id'])if self.job(job['id'])['status']not in ('queued','running')else None);self.check('uploaded_original_converted',j['status']=='completed');sid=j['result']['source_id']
  code,original=self.request('/asset?project='+PID+'&source='+sid+'&kind=original');self.check('original_bytes_preserved',code==200 and original==raw)
  code,preview=self.request('/api/preview?project='+PID+'&source='+sid);self.check('readable_text_available',code==200 and NAME in json.dumps(preview,ensure_ascii=False))
  code,_=self.request('/asset?project=acceptance-b&source='+sid+'&kind=original');self.check('cross_project_original_denied',code==400)
  second=self.inbox/PID/'dropped.txt';second.write_text('本文件是投递箱虚构样本。\n更名提议：另一个虚构名称\n');self.until(lambda:len(self.files())==2,20);self.check('folder_drop_watched_without_manual_scan',True)
  p=pp.project(self.lib,PID);self.until(lambda:Steward(self.lib,self.inbox).summary(PID)['counts'].get('awaiting_agent',0)>=2);self.check('machine_conversion_does_not_invent_semantic_facts',rw.current(p)['revision']==0)
  self.request('/api/steward-control?project='+PID,dict(action='pause'));task=Steward(self.lib,self.inbox).submit_bundle(PID,self.bundle(sid,NAME),'验收脚本模拟外部Agent；固定证据，非LLM');tid=task['id'];self.check('agent_candidate_waits_while_paused',self.task(tid)['status']=='queued' and self.request('/api/automation?project='+PID)[1]['queued']>=1)
  self.stop();self.start();self.check('same_durable_task_survives_real_server_restart',self.task(tid)['id']==tid and self.task(tid)['status']=='queued');self.request('/api/steward-control?project='+PID,dict(action='resume'));self.until(lambda:rw.current(p)['revision']==1 and self.task(tid)['status']=='completed');self.check('worker_publishes_eligible_agent_increment',self.task(tid)['status']=='completed',task_id=tid)
  folder,_=rw.check_version(p,'research-000001');before={f.name:pp.sha(f.read_bytes())for f in folder.iterdir()if f.is_file()};code,html=self.request('/dossier/?project='+PID);self.check('human_dossier_reads_published_record',code==200 and NAME in html.decode()and'research-000001'in html.decode())
  asyncio.run(asyncio.wait_for(self.mcp(),timeout=25))
  other_sid=next(x['id']for x in self.files()if x['id']!=sid);conflict=Steward(self.lib,self.inbox).submit_bundle(PID,self.bundle(other_sid,'另一个虚构名称'),'验收脚本模拟外部Agent/冲突');self.until(lambda:self.task(conflict['id'])['status']=='needs_attention');self.check('conflict_stays_attention_and_does_not_overwrite',self.request('/api/automation?project='+PID)[1]['attention_records']>=1 and rw.current(p)['revision']==1 and rw.cell(rw.dataset(p),'PROJECT','canonical_name')['value']==NAME)
  self.check('immutable_published_bytes_unchanged',before=={f.name:pp.sha(f.read_bytes())for f in folder.iterdir()if f.is_file()})
  code,job=self.request('/api/upload?project='+PID+'&name=duplicate.txt',raw);j=self.until(lambda:self.job(job['id'])if self.job(job['id'])['status']not in ('queued','running')else None);self.check('duplicate_upload_does_not_duplicate_source',j['result']['status']=='duplicate'and len(self.files())==2)
  from build_research_handoff import build
  package=build(self.lib,PID,self.folder/'handoff');self.check('handoff_snapshot_builds',package['check']['revision']=='research-000001')
  for name in ['check.py','read.py']:
   result=subprocess.run([str(PYTHON),name],cwd=package['folder'],capture_output=True,text=True,timeout=20);(self.folder/(name+'.log')).write_text(result.stdout+result.stderr);self.check('portable_'+name,result.returncode==0)
  self.stop();return package
 def execute(self):
  report=dict(scope='isolated_synthetic_fixture_not_real_project_research',started_at=pp.now(),checks=self.checks,capability_boundary='真实HTTP/监听/持久队列/重启/MCP；外部Agent语义候选使用明确固定测试值，非Deep Research或通用模型')
  try:report['package']=self.run();report['status']='passed'
  except Exception as exc:report.update(status='failed',error=type(exc).__name__+': '+str(exc));raise
  finally:
   try:self.stop()
   finally:
    report['finished_at']=pp.now();pp.save(self.folder/'验收结果.json',report);print(json.dumps(dict(status=report.get('status'),checks=len(self.checks),report=str(self.folder/'验收结果.json')),ensure_ascii=False))
if __name__=='__main__':Acceptance().execute()
