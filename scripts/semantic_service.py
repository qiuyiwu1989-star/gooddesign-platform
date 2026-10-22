# coding: utf-8
"""046 bounded local integration: real model jobs, receipts, and opt-in new-file reading."""
import datetime,threading,time
from zoneinfo import ZoneInfo
import project_ownership as ownership
from pathlib import Path
import project_pipeline as pp,research_workflow as rw
from semantic_agent import SemanticQueue
class Service:
 def __init__(self,store,queue=None):
  self.store=store;self.queue=queue or SemanticQueue(store.lib);self.file=store.folder/'semantic-control.json';self.lock=threading.RLock();self.future=None
 def state(self):return pp.load(self.file)if self.file.exists()else dict(projects={},receipts={})
 def configure(self,pid,enabled,daily_limit=3):
  p=pp.project(self.store.lib,pid)
  if type(enabled)is not bool or type(daily_limit)is not int or not 1<=daily_limit<=10:raise ValueError('自动深读开关或每日预算无效（1–10份）')
  with self.lock:
   state=self.state();old=state['projects'].get(pid,{})
   if not old:old=dict(seen={sid:x.get('chunks_sha256')for sid,x in ownership.select(p,pp.state(p)['sources']).items()})
   old.update(enabled=enabled,daily_limit=daily_limit);state['projects'][pid]=old;pp.save(self.file,state)
  return self.status(pid)
 def status(self,pid):
  pp.project(self.store.lib,pid);q=self.queue.status(pid)
  with self.lock:state=self.state()
  jobs=[]
  for job in q['jobs']:
   item={k:v for k,v in job.items()if k!='result_path'};item['publication']=state['receipts'].get(str(job['id']));jobs.append(item)
  return dict(project_id=pid,backend=q['backend'],paused=q['paused'],configuration={k:v for k,v in state['projects'].get(pid,dict(enabled=False,daily_limit=3)).items()if k!='seen'},jobs=jobs,mode='real_model_with_evidence_gate',limits='每批最多3份，每份一次模型调用；只覆盖所列文本块，不代表全文/专家审核')
 def enqueue(self,pid,sids):
  if not isinstance(sids,list)or not 1<=len(sids)<=3 or any(not isinstance(x,str)for x in sids):raise ValueError('请选择1–3个本项目来源编号')
  result=self.queue.enqueue(pid,sids,max_sources=3,max_calls=3,max_chars=24000);self.pump();return dict(project_id=pid,jobs=[{k:v for k,v in j.items()if k!='result_path'}for j in result['jobs']])
 def receipt(self,pid,job_id):
  job=self.queue.get(job_id)
  if job['project_id']!=pid:raise ValueError('语义任务不属于当前项目')
  with self.lock:
   state=self.state();key=str(job_id)
   old=state['receipts'].get(key)
   token=dict(attempts=job['attempts'],queue_status=job['status'],result_sha256=pp.sha(Path(job['result_path']).read_bytes())if job.get('result_path')and Path(job['result_path']).is_file()else None)
   if old and old.get('queue_token')==token:return old
   if job['status']=='no_candidates':result=dict(status='no_candidates',note='本轮未提出可入档候选，不代表全文已研究完成')
   elif job['status']in ('needs_review','needs_attention','failed'):result=dict(status=job['status'],note='保留模型风险/冲突/失败，不自动提交')
   elif job['status']=='ready':
    bundle=self.queue.bundle(job_id,pid)
    if bundle.get('semantic_agent',{}).get('requires_review'):return dict(status='needs_review')
    # Exact quotes are necessary, not proof of semantic correctness. Known risks never auto-publish.
    task=self.store.steward.submit_bundle(pid,bundle,'046语义管家/证据门禁')
    result=dict(status='submitted_to_evidence_gate',steward_task_id=task['id'],note='仅通过现有门禁的增量入档；敏感/冲突继续待判断')
   else:return dict(status=job['status'])
   result['queue_token']=token;state['receipts'][key]=result;pp.save(self.file,state);return result
 def result(self,pid,job_id):
  job=self.queue.get(job_id)
  if job['project_id']!=pid:raise ValueError('语义任务不属于当前项目')
  bundle=self.queue.bundle(job_id,pid)if job['status']in ('ready','needs_review')else None
  return dict(job={k:v for k,v in job.items()if k!='result_path'},bundle=bundle)
 def discover(self):
  with self.lock:
   state=self.state();today=datetime.datetime.now(ZoneInfo('Asia/Seoul')).date().isoformat()
   for pid,cfg in state['projects'].items():
    if not cfg['enabled']:continue
    p=pp.project(self.store.lib,pid);jobs=self.queue.status(pid)['jobs'];used=sum(datetime.datetime.fromisoformat(j['created']).astimezone(ZoneInfo('Asia/Seoul')).date().isoformat()==today for j in jobs)
    if used>=cfg['daily_limit']:continue
    active=ownership.select(p,pp.state(p)['sources']);seen=cfg['seen']
    if isinstance(seen,list):seen={sid:active[sid].get('chunks_sha256')for sid in seen if sid in active}
    for sid in active:
     if sid in seen and seen[sid]==active[sid].get('chunks_sha256'):continue
     try:self.queue.enqueue(pid,[sid],max_sources=1,max_calls=1,max_chars=24000)
     except ValueError as exc:cfg['last_attention']=str(exc);continue
     cfg.pop('last_attention',None);seen[sid]=active[sid].get('chunks_sha256');used+=1
     if used>=cfg['daily_limit']:break
    cfg['seen']=seen
   pp.save(self.file,state)
 def _step(self):
  row=self.queue.step()
  if row.get('id')and row['status']in ('ready','needs_review','no_candidates','failed','needs_attention'):self.receipt(row['project_id'],row['id'])
  return row
 def pump(self):
  with self.lock:
   if self.future and not self.future.done():return
   if self.store.steward.summary('2025-00'if(self.store.lib/'2025-00').exists()else pp.load(self.store.lib/'项目索引.json')['projects'][0]['id'])['paused']:return
   self.discover()
   if self.queue.status()['paused']:return
   # Recover result-to-publication handoffs after a process crash, independently of queued work.
   with self.queue.connect()as db:
    done=[dict(r)for r in db.execute("SELECT id,project_id FROM jobs WHERE status IN ('ready','needs_review','no_candidates','failed','needs_attention')")]
    available=db.execute("SELECT 1 FROM jobs WHERE status='queued' OR (status='running' AND lease<?) LIMIT 1",(time.time(),)).fetchone()
   for row in done:self.receipt(row['project_id'],row['id'])
   if available:self.future=self.store.pool.submit(self._step)
