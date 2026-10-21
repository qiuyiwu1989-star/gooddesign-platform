# coding: utf-8
"""044 durable local archive steward. Semantic research comes from an external Agent.
Raw documents never create instructions or approve their own claims.
"""
import argparse,contextlib,json,sqlite3,time,threading
from collections import Counter
from pathlib import Path
import project_pipeline as pp
import project_ownership as own
import research_workflow as rw
import steward_scope
VERSION='steward-0.5.2'
AGENT_METHOD='agent_evidence_extract_v1'
PROTECTED=rw.RESTRICTED|{'completion_org_ids','completion_person_ids','award_list_confirmed','review_status'}
class Steward:
 def __init__(self,lib,inbox):
  self.lib=Path(lib);self.inbox=Path(inbox);self.folder=self.lib/'.file-admin';self.folder.mkdir(exist_ok=True)
  self.db=self.folder/'steward.sqlite3';self.stop=threading.Event()
  with self.connect()as db:
   db.executescript('''CREATE TABLE IF NOT EXISTS tasks(
    id INTEGER PRIMARY KEY, project TEXT NOT NULL, key TEXT UNIQUE NOT NULL,
    payload TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'queued', attempts INTEGER DEFAULT 0,
    due REAL DEFAULT 0, lease REAL DEFAULT 0, created TEXT NOT NULL, finished TEXT, result TEXT, error TEXT);
    CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS controls(id INTEGER PRIMARY KEY,at TEXT NOT NULL,actor TEXT NOT NULL,action TEXT NOT NULL,project TEXT,task_id INTEGER,previous TEXT);
    CREATE TABLE IF NOT EXISTS scope_holds(task_id INTEGER PRIMARY KEY,previous TEXT NOT NULL);
    CREATE INDEX IF NOT EXISTS task_due ON tasks(status,due);
   ''')
 @contextlib.contextmanager
 def connect(self):
  db=sqlite3.connect(self.db,timeout=15);db.row_factory=sqlite3.Row
  try:
   with db:yield db
  finally:db.close()
 def enqueue(self,pid,payload,key=None):
  pp.project(self.lib,pid)
  key=key or rw.digest(dict(project=pid,payload=payload,processor=VERSION))
  with self.connect()as db:
   db.execute('INSERT OR IGNORE INTO tasks(project,key,payload,created)VALUES(?,?,?,?)',(pid,key,json.dumps(payload,ensure_ascii=False),pp.now()))
   return dict(db.execute('SELECT * FROM tasks WHERE key=?',(key,)).fetchone())
 def enqueue_source(self,pid,sid):
  p=pp.project(self.lib,pid);s=rw.source(p,sid)
  return self.enqueue(pid,dict(kind='source',source_id=sid,source_sha256=s['sha256'],chunks_sha256=pp.sha(pp.safe(p,s['chunks']).read_bytes()),parser_version=s.get('parser_version'),processor=VERSION))
 def enqueue_fetch(self,pid,url,title=''):
  pp.public_url(url)
  pp.project(self.lib,pid)
  # Keep the identity across processor upgrades and title edits, including pre-044d tasks.
  with self.connect()as db:
   old=db.execute("SELECT * FROM tasks WHERE project=? AND json_extract(payload,'$.kind')='fetch' AND json_extract(payload,'$.url')=? ORDER BY id LIMIT 1",(pid,url)).fetchone()
  if old:return dict(old)
  key=rw.digest(dict(kind='fetch',project=pid,url=url,identity_version=1))
  return self.enqueue(pid,dict(kind='fetch',url=url,title=title,processor=VERSION),key=key)
 def fetch_jobs(self,pid,task_id=None):
  pp.project(self.lib,pid)
  with self.connect()as db:
   query="SELECT * FROM tasks WHERE project=? AND json_extract(payload,'$.kind')='fetch'";args=[pid]
   if task_id is not None:query+=' AND id=?';args.append(task_id)
   rows=[dict(x)for x in db.execute(query+' ORDER BY id DESC LIMIT 100',args)]
  jobs=[]
  for row in rows:
   payload=json.loads(row['payload']);out=json.loads(row['result'])if row['result']else{}
   result=out.get('download')
   if result:result=dict(result,steward_task_id=out.get('source_task_id'))
   jobs.append(dict(id='steward-'+str(row['id']),project_id=pid,kind='fetch',args=dict(url=payload['url']),status=row['status'],created_at=row['created'],finished_at=row['finished'],error=row['error'],result=result,durable=True,attempts=row['attempts']))
  return jobs
 def enqueue_candidates(self,pid,ids):
  if not ids or len(set(ids))!=len(ids):raise ValueError('研究候选集合无效')
  known={c['id']for c in rw.current(pp.project(self.lib,pid))['candidates']}
  if set(ids)-known:raise ValueError('研究候选不存在')
  return self.enqueue(pid,dict(kind='candidates',candidate_ids=sorted(ids),processor=VERSION))
 def submit_bundle(self,pid,payload,actor):
  if payload.get('project_id')!=pid or not isinstance(payload.get('candidates'),list)or not payload['candidates']:raise ValueError('研究提交项目身份或内容无效')
  # Validate all entries before saving any of the batch. Caller is a trusted local Agent, not the source file.
  with pp.lock(self.lib):
   p=pp.project(self.lib,pid);w=rw.current(p);ids=[]
   for c in payload['candidates']:
    c=dict(c);c['extraction_method']=AGENT_METHOD;ids.append(rw.add_candidate(p,w,c,actor)['id'])
   if len(set(ids))!=len(ids):raise ValueError('研究提交有重复候选')
   rw.save(p,w)
  return self.enqueue_candidates(pid,ids)
 def pause(self,value,actor='本地操作员'):
  with self.connect()as db:
   old=db.execute('SELECT value FROM settings WHERE key=?',('paused',)).fetchone()
   db.execute('INSERT OR REPLACE INTO settings VALUES(?,?)',('paused','1'if value else'0'))
   db.execute('INSERT INTO controls(at,actor,action,previous)VALUES(?,?,?,?)',(pp.now(),actor,'pause'if value else'resume',old['value']if old else'0'))
 def retry(self,pid,task_id,actor='本地操作员'):
  pp.project(self.lib,pid)
  if type(task_id)is not int:raise ValueError('任务编号无效')
  with self.connect()as db:
   db.execute('BEGIN IMMEDIATE')
   old=db.execute('SELECT * FROM tasks WHERE id=? AND project=?',(task_id,pid)).fetchone()
   if not old or old['status']!='failed':raise ValueError('仅可重试本项目已失败的任务；冲突内容需核对，不自动放行')
   db.execute('INSERT INTO controls(at,actor,action,project,task_id,previous)VALUES(?,?,?,?,?,?)',(pp.now(),actor,'retry',pid,task_id,json.dumps(dict(old),ensure_ascii=False)))
   db.execute("UPDATE tasks SET status='queued',attempts=0,due=0,lease=0,finished=NULL,error=NULL,result=NULL WHERE id=?",(task_id,))
  return dict(task_id=task_id,status='queued')
 def summary(self,pid):
  p=pp.project(self.lib,pid);contexts=steward_scope.contexts(p);sources=pp.state(p)['sources'];imagefile=p/'图片素材/图片清单.json'
  image_titles={x['library_source_id']:x['title']for x in pp.load(imagefile)['items']}if imagefile.exists()else{}
  mapping=pp.load(p/'资料关联.json').get('source_titles',{})if(p/'资料关联.json').exists()else{}
  with self.connect()as db:
   rows=[dict(x)for x in db.execute('SELECT id,status,attempts,created,finished,payload,result,error FROM tasks WHERE project=? ORDER BY id DESC LIMIT 10',(pid,))]
   controls=[dict(x)for x in db.execute('SELECT id,at,actor,action,project,task_id FROM controls WHERE project=? OR project IS NULL ORDER BY id DESC LIMIT 10',(pid,))]
   counts=dict(Counter(x['status']for x in db.execute('SELECT status FROM tasks WHERE project=?',(pid,))))
   paused=db.execute('SELECT value FROM settings WHERE key=?',('paused',)).fetchone()
   maintenance_issue=db.execute('SELECT value FROM settings WHERE key=?',('maintenance_error:'+pid,)).fetchone()
  for r in rows:
   r['result']=json.loads(r['result'])if r['result']else None
   payload=json.loads(r.pop('payload'));r['kind']=payload['kind'];r['subject']=payload.get('title')or payload.get('url')or payload.get('source_id')or'研究内容增量'
   sid=payload.get('source_id');context=contexts.get(sid)
   if context:r.update(document_context=context,subject=context['title']+' · '+context['format'].upper())
   elif sid in image_titles:r['subject']=image_titles[sid]
   elif sid in sources:
    origin=sources[sid].get('origin',{});r['subject']=mapping.get(origin.get('url'))or origin.get('filename')or sources[sid]['title']
  return dict(processor=VERSION,paused=bool(paused and paused['value']=='1'),maintenance_attention=bool(maintenance_issue),counts=counts,recent=rows,controls=controls,semantic_mode='external_agent_submission',embedded_model_connected=False)
 def claim(self):
  with self.connect()as db:
   db.execute('BEGIN IMMEDIATE')
   p=db.execute('SELECT value FROM settings WHERE key=?',('paused',)).fetchone()
   if p and p['value']=='1':return None
   now=time.time()
   # Expired work is resumed using the same idempotent source/candidate payload.
   db.execute("UPDATE tasks SET status='retry',due=? WHERE status='running' AND lease<?",(now,now))
   row=db.execute("SELECT * FROM tasks WHERE status IN ('queued','retry') AND due<=? ORDER BY id LIMIT 1",(now,)).fetchone()
   if not row:return None
   db.execute("UPDATE tasks SET status='running',attempts=attempts+1,lease=? WHERE id=?",(now+600,row['id']))
   out=dict(row);out['attempts']+=1;out['payload']=json.loads(out['payload']);return out
 def finish(self,t,status,result=None,error=None):
  with self.connect()as db:db.execute('UPDATE tasks SET status=?,result=?,error=?,finished=?,lease=0,due=? WHERE id=?',(status,json.dumps(result,ensure_ascii=False)if result else None,error,pp.now(),time.time()+min(300,10*2**t['attempts']),t['id']))
 def consolidate(self,pid,ids):
  p=pp.project(self.lib,pid);w=rw.current(p);data=rw.dataset(p,w);chosen=[c for c in w['candidates']if c['id']in ids and c['status']in ('pending','approved')]
  eligible=[];exceptions=[];groups={}
  for c in chosen:groups.setdefault((c['record_id'],c['field']),[]).append(c)
  for c in chosen:
   why=None;machine=c.get('extraction_method')in ('conservative_rules_v1',rw.RULE_METHOD);agent=c.get('extraction_method')==AGENT_METHOD
   if c.get('reviewer_kind','human')=='human'and c['status']=='approved':why='人工已确认内容留给人工入档，不夹带发布'
   elif not(machine or agent):why='未登记的提炼方式，保留人工判断'
   elif c.get('operation','set')!='set':why='撤回或清空已有事实需人工判断'
   elif c['field']in PROTECTED:why='归属、权属或审核结论需人工判断'
   elif c['entity']=='metric'and c['field']in ('value','baseline_value'):why='关键指标数值需人工核对对象和工况'
   elif len({rw.digest(x['value'])for x in groups[(c['record_id'],c['field'])]})>1:why='同一字段出现不同候选值'
   elif c['content_nature']=='source_statement':
    previous=rw.cell(data,c['record_id'],c['field'])
    if previous and previous.get('value_state')=='known'and previous.get('value')!=c['value']:why='与已入档事实不一致，保留新旧内容待判断'
    elif machine:
     # Rules can only auto-admit identifiers for already indexed literature, never guessed DOC records.
     if c['field']not in ('doi','publication_number','grant_number')or c['record_id'].startswith('DOC-'):why='规则提取仅自动登记已关联文献的编号'
     else:
      try:target=rw.indexed_document(p,c['source_id'])
      except ValueError as exc:target=None;why=str(exc)
      if not why and(not target or target[:2]!=(c['record_id'],c['entity'])):why='无法核对文献关联身份'
      elif not why and rw.indexed_identifier(target,c['field'],data)!=c['value']:why='编号未与清单或已入档本件编号一致，保留核对'
   if not why:
    try:
     rw.evidence(p,c)
     if rw.digest(rw.cell(data,c['record_id'],c['field']))!=c['base_cell_sha256']:why='字段已经更新，需重新提炼'
    except Exception as exc:why=str(exc)
   if not why and any(x['record_id']==c['record_id']and x['field']==c['field']for x in eligible):why='同字段重复证据，本次先保留一项，其余待合并'
   if why:exceptions.append(dict(candidate_id=c['id'],record_id=c['record_id'],field=c['field'],reason=why));continue
   eligible.append(c)
  approved=[]
  for c in eligible:
   kind='rule'if c['extraction_method']in ('conservative_rules_v1',rw.RULE_METHOD)else'agent'
   rw.review(self.lib,pid,c['id'],'approved','资料管家/'+kind,'证据与类型检查通过；无已知字段冲突；仅研究入档，非专家确认',reviewer_kind=kind,expected_status=c['status']);approved.append(c['id'])
  published=rw.publish(self.lib,pid,'资料管家','自动整理合格增量；原件与旧版保留',expected_candidate_ids=approved,selected_candidate_ids=approved)if approved else dict(status='no_changes',revision='research-%06d'%rw.current(p)['revision'])
  return dict(publication=published,accepted=approved,exceptions=exceptions,processor=VERSION,expert_reviewed=False)
 def tick(self):
  t=self.claim()
  if not t:return False
  try:
   payload=t['payload'];pid=t['project'];p=pp.project(self.lib,pid)
   entry=steward_scope.scope(p,payload)
   if entry['scope']!='project':
    steward_scope.hold(self,t,entry,own.registry(p).get('version',0),allow_running=True);return True
   if payload['kind']=='fetch':
    with pp.lock(self.lib):
     fetched=pp.fetch(self.lib,self.inbox,pid,payload['url'])
     if payload.get('title'):
      path=p/'资料关联.json';mapping=pp.load(path)if path.exists()else{}
      mapping.setdefault('source_titles',{})[payload['url']]=payload['title'];pp.save(path,mapping)
    entry=own.assignment(p,fetched['source_id'],pp.state(p)['sources']);child=self.enqueue_source(pid,fetched['source_id'])if entry['scope']=='project'else None
    self.finish(t,'completed',dict(download=fetched,source_task_id=child['id']if child else None,scope=entry['scope'],processor=VERSION))
    return True
   if payload['kind']=='source':
    x=rw.source(p,payload['source_id'])
    if x['sha256']!=payload['source_sha256']:raise ValueError('来源已变化，请新建增量任务')
    result=rw.process(self.lib,pid,x['id'],'资料管家/自动文字与规则处理')
    ids=result.get('extraction',{}).get('candidates',result.get('candidates',[]))
    # process() has a stable nested extract result; do not scan unrelated pending candidates.
    if not ids:ids=result.get('extract',{}).get('candidates',[])
    out=self.consolidate(pid,ids)if ids else dict(publication=dict(status='no_changes'),accepted=[],exceptions=[],note='原件已保存；未提取到可入档字段，等待Agent阅读',processor=VERSION)
    out['processing']=result
   else:out=self.consolidate(pid,payload['candidate_ids'])
   if payload['kind']=='candidates'and out['accepted']:
    w=rw.current(p);source_ids={c['source_id']for c in w['candidates']if c['id']in out['accepted']}
    with self.connect()as db:
     for old in db.execute("SELECT id,payload,result FROM tasks WHERE project=? AND status='awaiting_agent'",(pid,)).fetchall():
      old_payload=json.loads(old['payload'])
      if old_payload.get('source_id')in source_ids:
       previous=json.loads(old['result']);previous['research_task_id']=t['id'];previous['note']='本来源已有Agent研究内容入档；不代表全篇每项信息均已提取'
       db.execute("UPDATE tasks SET status='completed',result=?,finished=? WHERE id=?",(json.dumps(previous,ensure_ascii=False),pp.now(),old['id']))
   self.finish(t,'needs_attention'if out['exceptions']else'awaiting_agent'if out.get('note')else'completed',out)
  except Exception as exc:
   self.finish(t,'failed'if t['attempts']>=3 else'retry',error=str(exc)[:1000])
  return True
 def reconcile_identifiers(self,pid):
  closed=rw.close_duplicate_identifiers(self.lib,pid);w=rw.current(pp.project(self.lib,pid))
  resolved={c['id']:c['resolution']for c in w['candidates']if c['status']=='rejected'and c.get('reviewer_kind')=='rule'and c.get('resolution',{}).get('kind')=='duplicate_identifier'}
  researched={c['source_id']for c in w['candidates']if c['status']=='published'and c.get('extraction_method')==AGENT_METHOD}
  with self.connect()as db:
   rows=[dict(r)for r in db.execute("SELECT * FROM tasks WHERE project=? AND status='needs_attention'",(pid,))]
   for row in rows:
    payload=json.loads(row['payload']);result=json.loads(row['result'])if row['result']else{};ids={x['candidate_id']for x in result.get('exceptions',[])}
    if payload['kind']!='source'or not ids or not ids<=resolved.keys():continue
    result['previous_exceptions']=result['exceptions'];result['exceptions']=[];result['identifier_resolution']={cid:resolved[cid]for cid in sorted(ids)}
    result['note']='重复编号线索已归入标准文献记录；原候选和证据保留，文件核读范围不变'
    status='completed'if payload['source_id']in researched else'awaiting_agent'
    changed=db.execute("UPDATE tasks SET status=?,result=?,finished=? WHERE id=? AND status='needs_attention'",(status,json.dumps(result,ensure_ascii=False),pp.now(),row['id'])).rowcount
    if changed:db.execute('INSERT INTO controls(at,actor,action,project,task_id,previous)VALUES(?,?,?,?,?,?)',(pp.now(),'资料管家/编号去重','identifier_resolution',pid,row['id'],json.dumps(row,ensure_ascii=False)))
  return closed
 def start(self):
  def run():
   last_scope_scan=0
   while not self.stop.is_set():
    try:
     if time.monotonic()-last_scope_scan>15:
      with self.connect()as db:projects=[r['project']for r in db.execute('SELECT DISTINCT project FROM tasks')]
      for pid in projects:
       try:
        steward_scope.reconcile(self,pid);self.reconcile_identifiers(pid)
        with self.connect()as db:db.execute('DELETE FROM settings WHERE key=?',('maintenance_error:'+pid,))
       except Exception as exc:
        with self.connect()as db:db.execute('INSERT OR REPLACE INTO settings VALUES(?,?)',('maintenance_error:'+pid,json.dumps(dict(at=pp.now(),error=str(exc)[:500]),ensure_ascii=False)))
      last_scope_scan=time.monotonic()
     busy=self.tick()
    except Exception:busy=False
    if not busy:self.stop.wait(2)
  self.thread=threading.Thread(target=run,daemon=True);self.thread.start()
 def close(self):
  self.stop.set()
  if hasattr(self,'thread'):self.thread.join(timeout=15)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('action',choices=['status','source','fetch','submit','tick','pause','resume']);ap.add_argument('project',nargs='?',default='2025-00');ap.add_argument('--source');ap.add_argument('--url');ap.add_argument('--title',default='');ap.add_argument('--file',type=Path);ap.add_argument('--actor',default='Codex研究Agent');args=ap.parse_args();s=Steward(pp.LIB,pp.INBOX)
 if args.action=='status':out=s.summary(args.project)
 elif args.action=='source':out=s.enqueue_source(args.project,args.source)
 elif args.action=='fetch':out=s.enqueue_fetch(args.project,args.url,args.title)
 elif args.action=='submit':
  out=s.submit_bundle(args.project,pp.load(args.file),args.actor)
 elif args.action in ('pause','resume'):s.pause(args.action=='pause');out=dict(paused=args.action=='pause')
 else:out=dict(worked=s.tick())
 print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
