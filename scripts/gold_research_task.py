# coding: utf-8
"""050: durable acquisition task for gold catalog projects, not an autonomous web search engine."""
import argparse,html,json,sqlite3,time,urllib.parse,fcntl
from pathlib import Path
import project_pipeline as pp
import project_ownership as own
DIMENSIONS={
 'identity':('奖项与对象','好设计 金奖 获奖 完成单位'),
 'team':('团队与单位','团队 设计者 研制单位'),
 'needs':('背景与需求','需求 痛点 研制 背景'),
 'system':('系统与技术','原理 系统 结构 技术'),
 'mechanisms':('创新机制','创新 设计 方法 技术突破'),
 'validation':('指标与验证','试验 测试 指标 验证'),
 'patents':('专利','专利 公开号 申请人'),
 'papers':('论文','论文 DOI 研究'),
 'applications':('应用与效果','应用 采用 用户 运行 效果'),
 'history_media':('历程与图像','研制 历程 访谈 图片 视频')}
STATUS_LABELS={'queued':'待采集','running':'采集中','downloaded':'原件已保存 · 待核','reused_existing':'复用既有原件','reused_duplicate':'相同内容复用','failed':'获取失败 · 待处理'}
DEFAULT=pp.ROOT/'04-知识库/历史素材登记/金奖全量采集任务'
class Task:
 def __init__(self,folder=DEFAULT,lib=pp.LIB,root=pp.ROOT):
  self.folder=Path(folder);self.lib=Path(lib);self.root=Path(root);self.folder.mkdir(parents=True,exist_ok=True);self.db=self.folder/'采集任务.sqlite3'
  with self.connect()as c:c.executescript('''
   CREATE TABLE IF NOT EXISTS searches(id INTEGER PRIMARY KEY,project TEXT,dimension TEXT,query TEXT,at TEXT,results_json TEXT,status TEXT);
   CREATE TABLE IF NOT EXISTS projects(id TEXT PRIMARY KEY,catalog TEXT NOT NULL,created TEXT NOT NULL);
   CREATE TABLE IF NOT EXISTS dimensions(project TEXT,dimension TEXT,query TEXT,status TEXT DEFAULT 'not_searched',PRIMARY KEY(project,dimension));
   CREATE TABLE IF NOT EXISTS sources(id INTEGER PRIMARY KEY,project TEXT NOT NULL,url TEXT NOT NULL,title TEXT,discovery TEXT NOT NULL,discovery_query TEXT,dimension TEXT,status TEXT DEFAULT 'queued',attempts INTEGER DEFAULT 0,lease REAL DEFAULT 0,result TEXT,error TEXT,created TEXT,finished TEXT,UNIQUE(project,url));
  ''')
 def connect(self):
  c=sqlite3.connect(self.db,timeout=30);c.row_factory=sqlite3.Row;return c
 def init(self):
  catalog=pp.load(self.lib/'项目索引.json')['projects'];gold=[x for x in catalog if x.get('award')=='金奖']
  path=self.root/'99-历史项目快照/good-design/.build/enrich.json';old=pp.load(path)if path.exists()else{}
  with self.connect()as c:
   for row in gold:
    pid=row['id'];c.execute('INSERT OR IGNORE INTO projects VALUES(?,?,?)',(pid,json.dumps(row,ensure_ascii=False),pp.now()))
    for dimension,(_,suffix)in DIMENSIONS.items():c.execute('INSERT OR IGNORE INTO dimensions(project,dimension,query) VALUES(?,?,?)',(pid,dimension,f'"{row["name"]}" {suffix}'))
  for row in gold:
   for source in old.get(row['id'],[]):
    if source.get('url','').startswith(('http://','https://')):self.add(dict(project_id=row['id'],url=source['url'],title=source.get('title',''),discovery_kind='legacy_unverified_link'))
  return self.export()['summary']
 def add(self,row):
  pid=row['project_id'];url=row['url'];u=urllib.parse.urlsplit(url)
  if u.scheme not in ('http','https')or not u.hostname or u.username or u.password:raise ValueError('需无凭据HTTP(S)链接')
  url=urllib.parse.urlunsplit((u.scheme,u.netloc,u.path,u.query,''));dimension=row.get('dimension')
  if dimension is not None and dimension not in DIMENSIONS:raise ValueError('未知研究维度')
  with self.connect()as c:
   if not c.execute('SELECT 1 FROM projects WHERE id=?',(pid,)).fetchone():raise ValueError('非本任务金奖项目')
   kind=row.get('discovery_kind','agent_discovered_unverified');query=row.get('discovery_query')
   c.execute('INSERT OR IGNORE INTO sources(project,url,title,discovery,discovery_query,dimension,created)VALUES(?,?,?,?,?,?,?)',(pid,url,row.get('title',''),kind,query,dimension,pp.now()))
   # Preserve original seed identity; a new search finding is recorded separately in query metadata.
   if query:
    c.execute('UPDATE sources SET discovery_query=?,dimension=? WHERE project=? AND url=?',(query,dimension,pid,url))
    if dimension:c.execute("UPDATE dimensions SET status='search_leads_found_not_complete' WHERE project=? AND dimension=?",(pid,dimension))
   return c.execute('SELECT id FROM sources WHERE project=? AND url=?',(pid,url)).fetchone()[0]
 def record_search(self,row):
  pid=row['project_id'];dimension=row.get('dimension','identity');results=row.get('results',[])
  if dimension not in DIMENSIONS:raise ValueError('未知维度')
  with self.connect()as c:
   if not c.execute('SELECT 1 FROM projects WHERE id=?',(pid,)).fetchone():raise ValueError('非本任务金奖项目')
   status=row.get('status','leads_found'if results else'no_leads')
   c.execute('INSERT INTO searches(project,dimension,query,at,results_json,status)VALUES(?,?,?,?,?,?)',(pid,dimension,row['query'],row.get('searched_at',pp.now()),json.dumps(results,ensure_ascii=False),status))
   if status!='search_failed':c.execute('UPDATE dimensions SET status=? WHERE project=? AND dimension=?',('search_leads_found_not_complete'if results else'searched_no_leads',pid,dimension))
  for item in results:self.add(dict(project_id=pid,url=item['url'],title=item.get('title',''),dimension=dimension,discovery_query=row['query'],discovery_kind='live_web_search_20261023_unverified_relevance'))
  return len(results)
 def claim(self):
  with self.connect()as c:
   c.execute('BEGIN IMMEDIATE');c.execute("UPDATE sources SET status='queued',lease=0 WHERE status='running' AND lease<?",(time.time(),))
   row=c.execute("SELECT * FROM sources WHERE status='queued' ORDER BY (discovery_query IS NOT NULL) DESC,id LIMIT 1").fetchone()
   if not row:return None
   c.execute("UPDATE sources SET status='running',attempts=attempts+1,lease=? WHERE id=?",(time.time()+600,row['id']))
   return dict(row)
 def acquire(self,row):
  p=pp.project(self.lib,row['project']);url=row['url'];before=pp.state(p)['sources']
  for sid,source in before.items():
   origin=source.get('origin')or{}
   if url in (origin.get('url'),origin.get('requested_url'))and pp.safe(p,source['original']).is_file():
    return dict(status='reused_existing',source_id=sid,sha256=source['sha256'],ownership=own.assignment(p,sid,before)['scope'],meaning='已有原件复用；不代表本轮下载或核读')
  # Fetcher's redirects/DNS/size restrictions remain effective. Original is never a fact approval.
  with pp.lock(self.lib):
   before=set(pp.state(p)['sources']);result=pp.fetch(self.lib,self.root/'01-原始资料/项目投递箱',row['project'],url,initial_scope='pending')
   sid=result['source_id'];state=pp.state(p);source=state['sources'][sid]
   return dict(status='downloaded'if result['status']!='duplicate'else'reused_duplicate',source_id=sid,sha256=source['sha256'],conversion_status=source['status'],ownership=own.assignment(p,sid,state['sources'])['scope'],meaning='原件保存/机器转换；不是全文核读或结构化事实审核')
 def run(self,limit=8,max_seconds=900):
  started=time.monotonic();done=0
  while done<limit and time.monotonic()-started<max_seconds:
   row=self.claim()
   if not row:break
   try:result=self.acquire(row);status=result['status'];error=None
   except Exception as exc:result=None;status='failed';error=str(exc)[:1200]
   with self.connect()as c:c.execute('UPDATE sources SET status=?,result=?,error=?,finished=?,lease=0 WHERE id=?',(status,json.dumps(result,ensure_ascii=False)if result else None,error,pp.now(),row['id']))
   done+=1;self.export();time.sleep(1);print(json.dumps(dict(id=row['id'],project=row['project'],status=status,error=error),ensure_ascii=False),flush=True)
  return self.export()['summary']
 def export(self):
  with (self.folder/'.export.lock').open('a')as lock:
   fcntl.flock(lock,fcntl.LOCK_EX)
   try:return self._export()
   finally:fcntl.flock(lock,fcntl.LOCK_UN)
 def _export(self):
  with self.connect()as c:
   projects=[dict(x)for x in c.execute('SELECT * FROM projects ORDER BY id DESC')];sources=[dict(x)for x in c.execute('SELECT * FROM sources ORDER BY id')];dims=[dict(x)for x in c.execute('SELECT * FROM dimensions')];searches=[dict(x)for x in c.execute('SELECT * FROM searches')]
  counts={s:sum(x['status']==s for x in sources)for s in ('queued','running','downloaded','reused_existing','reused_duplicate','failed')}
  summary=dict(projects=len(projects),candidate_urls=len(sources),projects_searched=len({x['project']for x in searches if x['status']!='search_failed'}),search_events=len(searches),**counts,query_dimensions=len(dims),unexecuted_queries=sum(x['status']=='not_searched'for x in dims),full_research_complete=0,meaning='采集进度非深研质量；98为当前题录金奖待复核，不宣称官方全量已核')
  for row in projects:
   row['search_history']=[dict(x,results=json.loads(x['results_json']))for x in searches if x['project']==row['id']]
   row.update(catalog=json.loads(row['catalog']),sources=[dict(x,result=json.loads(x['result'])if x['result']else None)for x in sources if x['project']==row['id']],dimensions=[x for x in dims if x['project']==row['id']],expert_reviewed=False)
  report=dict(schema='gold-research-task-1.0',generated_at=pp.now(),summary=summary,projects=projects,limitations=['旧链接未经关联核验，新采集先待确认','2016题录仅8项及跨届年份待核，不擅自补造项目','查询清单不等于已执行搜索；网页/PDF保存不等于全文核读','无付费绕过、无自动事实发布、无云端同步、无模型调用预算'])
  pp.save(self.folder/'金奖采集进度.json',report)
  lines=['# 全部金奖项目网络采集任务','',f'更新：{report["generated_at"]}',json.dumps(summary,ensure_ascii=False),'','| 项目 | 年份 | 链接候选 | 已保存或复用 | 失败 | 查询未执行 |','|---|---:|---:|---:|---:|---:|']
  e=lambda x:html.escape(str(x),quote=True);cards=[]
  for row in projects:
   cat=row['catalog'];src=row['sources'];saved=sum(x['status']in ('downloaded','reused_existing','reused_duplicate')for x in src);failed=sum(x['status']=='failed'for x in src);pending=sum(x['status']=='not_searched'for x in row['dimensions'])
   lines.append(f'| {row["id"]} {cat["name"].replace("|","／")} | {cat.get("year","")} | {len(src)} | {saved} | {failed} | {pending}/10 |')
   queries=''.join('<li><b>'+e(DIMENSIONS[x['dimension']][0])+'</b> · '+('尚未检索'if x['status']=='not_searched'else'已检索，暂无新线索'if x['status']=='searched_no_leads'else'已发现线索，未穷尽')+'<p>'+e(x['query'])+'</p></li>'for x in row['dimensions'])
   links=''.join('<li><a href="'+e(x['url'])+'" target="_blank" rel="noopener noreferrer">'+e(x['title']or x['url'])+'</a><small>'+e(STATUS_LABELS.get(x['status'],x['status']))+(' · '+e(x['error'])if x['error']else'')+'</small></li>'for x in src)
   cards.append('<details data-name="'+e(cat['name']+row['id'])+'"><summary><b>'+e(row['id'])+'　'+e(cat['name'])+'</b><span>保存/复用 '+str(saved)+' / '+str(len(src))+' · 失败 '+str(failed)+' · 未检索 '+str(pending)+'/10</span></summary><p>题录年份 '+e(cat.get('year'))+' · 金奖 · 来源关联与档案内容待核</p><h3>分维检索任务</h3><ol>'+queries+'</ol><h3>网络来源与获取状态</h3><ul>'+links+'</ul></details>')
  (self.folder/'金奖采集进度.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
  page='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>金奖项目 · 网络采集进度</title><style>body{font:15px/1.7 system-ui;background:#f7f7fc;color:#27283c;max-width:1100px;margin:40px auto;padding:0 20px}h1{font-size:28px}small,span{display:block;color:#6e7387}details{background:white;border:1px solid #e2e3ee;border-radius:12px;margin:12px 0;padding:18px}summary{cursor:pointer}a{color:#5c4bdd}li{margin:12px 0;overflow-wrap:anywhere}input,button{font:inherit;padding:10px;border:1px solid #d8d9e8;border-radius:8px}p{overflow-wrap:anywhere}.stats{padding:18px;background:#eeebff;border-radius:12px}</style><h1>金奖项目网络采集任务</h1><p>原件保存 → 归属核对 → 清洗提炼 → 档案审核。各阶段分别记录，不用下载数冒充档案质量。</p><div class="stats">'+e(summary['projects'])+' 项金奖题录 · 已首轮检索 '+e(summary['projects_searched'])+' 项 · '+e(summary['candidate_urls'])+' 个候选链接 · 本轮下载 '+e(summary['downloaded'])+' · 既有复用 '+e(summary['reused_existing']+summary['reused_duplicate'])+' · 失败 '+e(summary['failed'])+'<small>待采集 '+e(summary['queued'])+' · 正在采集 '+e(summary['running'])+'</small><small>当前任务新生成并验收的完整档案：0；已有研究版本仍保留，不等同全部完成。</small></div><p>更新 '+e(report['generated_at'])+'　<button onclick="location.reload()">刷新进度</button></p><input id="find" placeholder="搜索项目名称或编号" aria-label="搜索项目"><p>98项来自当前题录；2016仅8项与跨届年份将继续核对。来源未核读、关系未确认的保留待核，不自动写进事实。</p>'+''.join(cards)+'<script>document.querySelector("#find").oninput=e=>document.querySelectorAll("details").forEach(d=>d.hidden=!d.dataset.name.includes(e.target.value.trim()))</script></html>'
  (self.folder/'金奖采集进度.html').write_text(page,encoding='utf-8');return report
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('action',choices=['init','add','search','run','status','export']);ap.add_argument('--folder',type=Path,default=DEFAULT);ap.add_argument('--input',type=Path);ap.add_argument('--limit',type=int,default=8);ap.add_argument('--max-seconds',type=int,default=900);a=ap.parse_args();t=Task(a.folder)
 if a.action=='init':out=t.init()
 elif a.action=='add':out=[t.add(x)for x in pp.load(a.input)];t.export()
 elif a.action=='search':out=[t.record_search(x)for x in pp.load(a.input)];t.export()
 elif a.action=='run':
  if not 1<=a.limit<=1000 or not 1<=a.max_seconds<=7200:raise SystemExit('limit 1–1000；max-seconds 1–7200')
  out=t.run(a.limit,a.max_seconds)
 else:out=t.export()['summary']
 print(json.dumps(out,ensure_ascii=False,indent=2))
