"""063 evidence-bound public reporting snapshot; no private text exported."""
from pathlib import Path
import json,hashlib,collections,datetime
from zoneinfo import ZoneInfo
import project_pipeline as pp
import research_workflow as rw
import project_ownership as own
from method_library_catalog import catalog,public_document_base
ROOT=Path(__file__).resolve().parents[1];RESEARCH=ROOT/'output/research-051';MR=ROOT/'output/method-reader-review'
load=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def build():
 roster=load(pp.LIB/'项目索引.json')['projects'];coverage=load(RESEARCH/'coverage-round2/全量覆盖队列.json');assessment=load(RESEARCH/'assessment-098/逐案内容评估汇总.json');am={x['project_id']:x for x in assessment['items']}
 gold_ids={x['project_id']for x in coverage['items']}
 deep={}
 for f in sorted((RESEARCH/'deepening-round1').glob('batch*/index.json')):
  for c in load(f).get('cases',[]):
   p=ROOT/c['report'];assert p.is_file()
   expected=c.get('report_sha256')or c.get('sha256');assert expected and sha(p)==expected
   report=load(p);assert c['project_id'] in gold_ids and report.get('project_id')==c['project_id']
   assert type(report.get('actual_queries')) is int and report['actual_queries']>0
   deep[c['project_id']]=True
 projects=[];records=known=source_entries=published=0;states=collections.Counter()
 for item in coverage['items']:
  pid=item['project_id'];p=pp.project(pp.LIB,pid);w=rw.current(p);revision='research-%06d'%w['revision'];data=rw.dataset(p,w);fingerprint=None
  if w['revision']:
   folder,_=rw.check_version(p,revision);fingerprint=sha(folder/'档案.json');published+=1
  recs=len(data['records']);cells=sum(c.get('value')is not None and c.get('value_state')=='known' for r in data['records']for c in r['cells'].values());sources=len(own.select(p,pp.state(p)['sources']));records+=recs;known+=cells;source_entries+=sources
  a=am.get(pid,{});score=a.get('display_score');status=a.get('content_assessment_status','待内容评估');score_revision=a.get('revision')
  aligned=fingerprint==a.get('dataset_sha256') and revision==score_revision
  if not aligned:score=None;status='版本变更，待复评'
  elif '版本已变' in status:status='版本变更，待复评';score=None
  elif score is None:status='待补证与内容评估'
  elif '独立校准' in status and '待独立'not in status:status='独立Agent校准，非专家'
  else:status='Agent初评，待校准'
  states[status]+=1
  projects.append(dict(id=pid,name=item['name'],revision=revision if w['revision']else None,coverage=item['stage'].startswith('coverage_executed'),deepening=pid in deep,records=recs,known_cells=cells,source_entries=sources,score=score,score_revision=score_revision if score is not None else None,quality_status=status,gaps=a.get('gaps',[])[:3]))
 methods=[];ms=collections.Counter()
 for row in catalog()['methods']:
  rid=row['research_id'];raw=public_document_base(rid)/'档案'/rid/'档案.json';fingerprint=sha(raw);score=None;status='待校准';gaps=[]
  for folder in sorted((MR/'content-quality').glob('calibration*')):
   f=folder/(rid+'-calibration-v1.json')
   if f.is_file():
    c=load(f)
    if c.get('dataset_sha256')==fingerprint:score=c['calibrated_total'];status='独立Agent校准，非专家'
  for folder in sorted((MR/'content-quality').glob('batch*')):
   f=folder/(rid+'-assessment.json')
   if f.is_file():
    a=load(f)
    if a.get('dataset_sha256')==fingerprint:gaps=[a.get('primary_research_task','继续补原典与实际方法产物')]
  ms[status]+=1;methods.append(dict(id=rid,name=row['name'],category=row['category'],version=row['version'],score=score,quality_status=status,gaps=gaps))
 upgrades=[]
 for rid,folder in [('R17','R17-composite-v2-calibration'),('R36','R36-composite-v1-calibration'),('R44','R44-composite-v1-calibration')]:
  c=load(MR/'reviews'/folder/'calibration.json');upgrades.append(dict(id=rid,score=c['calibrated_total'],scope='教学增补组合版本，独立Agent校准；不替换冻结基线'))
 native=[];f=RESEARCH/'root/deepening01-published.json'
 if f.exists():
  for x in load(f)['projects']:native.append(dict(id=x['project_id'],revision=x['result']['revision'],fields=x['result']['changes'],scope='相关专利题录参考，不是采用证明'))
 ps=[x['score']for x in projects if x['score']is not None and x['quality_status']=='独立Agent校准，非专家'];mt=[x['score']for x in methods if x['score']is not None]
 d=dict(schema='gooddesign-data-report-1.0',generated_at=datetime.datetime.now(ZoneInfo('Asia/Seoul')).isoformat(timespec='seconds'),assessment_snapshot_at=assessment.get('generated_at'),scope='项目字段与来源数量仅统计98金奖当前库；560是题录总数。基线、增补、检索、发布、评估、达标分别统计。',summary=dict(catalog_entries=len({x['id']for x in roster}),gold_projects=len(projects),published_research=published,basic_coverage=sum(x['coverage']for x in projects),deepening_reports=len(deep),fact_records=records,known_cells=known,project_source_entries=source_entries,methods=len(methods),method_calibrated=len(mt),incremental_projects=len(native),incremental_fields=sum(x['fields']for x in native)),project_quality_counts=dict(states),method_quality_counts=dict(ms),project_calibrated_range=[min(ps),max(ps)]if ps else None,method_baseline_range=[min(mt),max(mt)]if mt else None,projects=projects,methods=methods,method_upgrades=upgrades,incremental_admissions=native,capabilities=[dict(title='项目资料与版本管线',status='已可运行',detail='资料归属、证据候选、审核发布、不可覆盖版本；机器转换与专业核读分别记录。'),dict(title='项目阅读与检索',status='已上线',detail='项目首页、档案阅读、资料与解读、评估入口；原件与管理仍需登录。'),dict(title='64方法内容与可视化',status='已建立并校准基线',detail='分类检索、图标、结构图、展开阅读、来源与写入规范；内容质量仍需提升。'),dict(title='教学增补与独立复测',status='持续完善',detail='问题定义、功能分析、形态组合、Pugh、原型、V&V及系统设计等已形成增补；实际用户与工程验证仍有缺口。'),dict(title='统一MCP入口',status='本机已验收',detail='10显式工具连接两库，版本绑定组包及独立计划保存回读；不自动调用模型，未开放公网HTTP。')],next_actions=['消化已独立核读材料，完成精确选录、原生重绑、审核入档及当前版导读/评估。','逐案解决身份归属、一手正文、原始验证工况及成果采用证据缺口。','对当前版本进行独立内容复评；旧分失效不沿用，未评不补0。','继续补方法完整产物、反例和真实应用证据，分别验收内容、执行与专家状态。'],quality_notice='评分针对档案内容，不是项目技术价值或获奖水平。Agent校准不等于专家审核。尚无80分验收通过结论，不能按来源、字段或测试数量凑分。')
 assert all(x['score']is None or x['score']<80 for x in projects+methods+upgrades),'出现新的80分候选，须核查正式验收状态后更新文案'
 assert len(projects)==98 and len(methods)==64 and sum(states.values())==98
 out=ROOT/'extensions/project-portal/data-report.json';out.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');print(json.dumps(d['summary'],ensure_ascii=False));return d
if __name__=='__main__':build()
