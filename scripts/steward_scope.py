# coding: utf-8
"""044f reversible task holds for current source ownership, with durable audit."""
import json
import project_pipeline as pp
import project_ownership as own
PENDING=('queued','retry','failed','awaiting_agent','needs_attention')
def scope(p,payload,sources=None,reg=None):
 sources=sources if sources is not None else pp.state(p)['sources'];reg=reg if reg is not None else own.registry(p)
 if payload['kind']=='source':
  sid=payload['source_id']
  if sid not in sources:return dict(scope='pending',reason='来源记录暂缺，需核对后恢复')
  return own.assignment(p,sid,sources,reg)
 if payload['kind']=='fetch':return own.assignment(p,'url',{'url':dict(origin=dict(url=payload['url']))},reg)
 return dict(scope='project',reason='候选提交另按逐项证据核对')
def hold(steward,task,entry,registry_version,allow_running=False):
 with steward.connect()as db:
  db.execute('BEGIN IMMEDIATE');row=db.execute('SELECT * FROM tasks WHERE id=?',(task['id'],)).fetchone()
  if not row or row['status']=='scope_hold':return False
  if row['status']=='running'and not allow_running:return False
  if row['status']not in PENDING+('running',):return False
  previous=dict(row)
  if previous['status']=='running':previous.update(status='queued',attempts=max(0,previous['attempts']-1),lease=0)
  db.execute('INSERT OR REPLACE INTO scope_holds(task_id,previous)VALUES(?,?)',(row['id'],json.dumps(previous,ensure_ascii=False)))
  note=dict(note='资料已不属于本项目自动处理范围；原件与历史保留，归属恢复后继续原状态',scope=entry['scope'],reason=entry.get('reason',''),ownership_version=registry_version)
  db.execute("UPDATE tasks SET status='scope_hold',result=?,error=NULL,lease=0,finished=? WHERE id=?",(json.dumps(note,ensure_ascii=False),pp.now(),row['id']))
  db.execute('INSERT INTO controls(at,actor,action,project,task_id,previous)VALUES(?,?,?,?,?,?)',(pp.now(),'资料管家/归属巡检','scope_hold',row['project'],row['id'],json.dumps(dict(task=dict(row),ownership=entry,registry_version=registry_version),ensure_ascii=False)))
 return True
def reconcile(steward,pid):
 p=pp.project(steward.lib,pid);sources=pp.state(p)['sources'];reg=own.registry(p)
 with steward.connect()as db:rows=[dict(x)for x in db.execute("SELECT * FROM tasks WHERE project=? AND status IN ('queued','retry','failed','awaiting_agent','needs_attention','scope_hold')",(pid,))]
 changes=[]
 for row in rows:
  payload=json.loads(row['payload'])
  if payload['kind']not in ('source','fetch'):continue
  entry=scope(p,payload,sources,reg)
  if entry['scope']!='project':
   if hold(steward,row,entry,reg.get('version',0)):changes.append(dict(task_id=row['id'],action='scope_hold'))
  elif row['status']=='scope_hold':
   with steward.connect()as db:
    db.execute('BEGIN IMMEDIATE');saved=db.execute('SELECT previous FROM scope_holds WHERE task_id=?',(row['id'],)).fetchone()
    current=db.execute('SELECT status FROM tasks WHERE id=?',(row['id'],)).fetchone()
    if not saved or current['status']!='scope_hold':continue
    previous=json.loads(saved['previous'])
    db.execute('UPDATE tasks SET status=?,attempts=?,due=?,lease=0,finished=?,result=?,error=? WHERE id=?',(previous['status'],previous['attempts'],previous['due'],previous['finished'],previous['result'],previous['error'],row['id']))
    db.execute('DELETE FROM scope_holds WHERE task_id=?',(row['id'],))
    db.execute('INSERT INTO controls(at,actor,action,project,task_id,previous)VALUES(?,?,?,?,?,?)',(pp.now(),'资料管家/归属巡检','scope_restore',pid,row['id'],saved['previous']))
   changes.append(dict(task_id=row['id'],action='scope_restore',restored_status=previous['status']))
 return changes

def contexts(p):
 out={};sources=pp.state(p)['sources']
 for file,kind,key in [('论文原文管理/论文原件清单.json','论文','paper_id'),('专利原文管理/专利原件清单.json','专利','patent_id')]:
  if not(p/file).exists():continue
  for x in pp.load(p/file)['items']:
   ids=list(dict.fromkeys(s for s in [x.get('library_source_id'),x.get('pdf_source_id')]+x.get('related_source_ids',[])if s in sources))
   for sid in ids:out[sid]=dict(document_id=x[key],document_kind=kind,title=x['title'],related_source_ids=ids,format=sources[sid]['original'].rsplit('.',1)[-1],reading_note='同篇文献的格式分别保留阅读状态；HTML已读不等于PDF图表已核对')
 return out
