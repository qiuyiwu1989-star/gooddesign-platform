# coding: utf-8
"""044j version-bound research review, separate from facts and expert scoring."""
import json,os,re,tempfile
from pathlib import Path
import project_pipeline as pp,research_workflow as rw
import project_ownership as own
SCHEMA='research-assessment-1.0'
DIMENSIONS=[('identity','身份与边界'),('evidence','资料与证据'),('technical','技术与验证'),('transfer','方法与迁移'),('rights','成果与权利'),('maintenance','版本与维护')]
STAGES={'partial':'已有部分依据','unconfirmed':'关键依据待补','usable_with_limits':'可在边界内研究'}

def audit(p,data):
 from research_handoff_check import evidence_nodes
 sources=pp.state(p)['sources'];reg=own.registry(p);issues=[];cache={}
 def trace(e):
  key=rw.digest(e)
  if key in cache:return cache[key]
  try:
   x=sources.get(e['source_id'])
   if not x or own.assignment(p,e['source_id'],sources,reg)['scope']!='project':raise ValueError('引用来源不属当前项目')
   if x['sha256']!=e['source_sha256']or pp.sha(pp.safe(p,x['original']).read_bytes())!=e['source_sha256']:raise ValueError('原件指纹不符')
   path=pp.safe(p,e['chunks_path'])
   if pp.sha(path.read_bytes())!=e['chunks_sha256']:raise ValueError('冻结证据块指纹不符')
   b=next((b for b in pp.load(path)if b['id']==e['chunk_id']),None)
   if not b or not e['quote']or e['quote']not in b['text']or pp.sha(e['quote'].encode())!=e['quote_sha256']:raise ValueError('引文位置或指纹不符')
   if x.get('origin',{}).get('kind')=='project_json_row':
    from source_json_row import validate as validate_json_row
    validate_json_row(p,x)
   if x.get('origin',{}).get('kind')=='project_source_excerpt':
    from source_excerpt import selected_text
    if e['quote']not in selected_text(p,x):raise ValueError('选录引文超出父件范围')
   answer=None
  except (ValueError,KeyError,TypeError,OSError,json.JSONDecodeError)as exc:answer=str(exc)if isinstance(exc,ValueError)else'证据文件缺失或格式异常'
  cache[key]=answer;return answer
 known=0;traced=0;ai_ok=0;slots=0;states={};per_entity={}
 for r in data['records']:
  metrics=per_entity.setdefault(r['entity'],dict(records=0,registered_cells=0,known_cells=0,traceable_cells=0));metrics['records']+=1
  for field,c in r['cells'].items():
   slots+=1;metrics['registered_cells']+=1;state=c.get('value_state','unknown');states[state]=states.get(state,0)+1
   if state!='known':continue
   known+=1;metrics['known_cells']+=1;es=list(evidence_nodes(c));errors=[trace(e)for e in es];errors=[x for x in errors if x]
   if not es:errors.append('缺少冻结证据')
   if c.get('content_nature')!='source_statement':errors.append('事实层性质不符')
   if errors:issues.append(dict(record_id=r['id'],field=field,kind='fact',problems=sorted(set(errors))))
   else:traced+=1;metrics['traceable_cells']+=1
 for i in data.get('interpretations',[]):
  es=list(evidence_nodes(i));errors=[trace(e)for e in es];errors=[x for x in errors if x]
  if not es:errors.append('AI解读缺少依据')
  if i.get('content_nature')not in ('ai_interpretation','ai_hypothesis')or not i.get('conditions')or not i.get('limitations'):errors.append('AI性质/适用前提/限制不完整')
  if errors:issues.append(dict(record_id=i.get('record_id'),field=i.get('field'),kind='ai',problems=sorted(set(errors))))
  else:ai_ok+=1
 return dict(checked_at=pp.now(),scope='frozen_dataset_evidence_and_current_ownership_at_assessment_time',status='traceable'if not issues else'attention',records=len(data['records']),registered_cells=slots,known_cells=known,traceable_known_cells=traced,ai_items=len(data.get('interpretations',[])),traceable_bounded_ai_items=ai_ok,unique_evidence=len(cache),value_states=states,per_entity=per_entity,issues=issues,meaning='检查引文和文件可追溯性；不判断原文陈述真实、工程适用性、专家审核或研究完整度。')

def folder(p,revision):
 if not re.fullmatch(r'research-\d{6}',revision):raise ValueError('研究版本无效')
 return rw.workspace(p)/'研究评估'/revision

def validate(p,payload):
 if not isinstance(payload,dict)or payload.get('schema')!=SCHEMA or payload.get('project_id')!=p.name or payload.get('content_nature')!='ai_research_review':raise ValueError('评估身份无效')
 if not re.fullmatch(r'\d{1,3}\.\d{1,3}\.\d{1,3}',payload.get('version','')):raise ValueError('评估版本无效')
 vf,_=rw.check_version(p,payload.get('research_revision',''));data=pp.load(vf/'档案.json')
 if payload.get('dataset_sha256')!=pp.sha((vf/'档案.json').read_bytes()):raise ValueError('评估数据绑定不符')
 ids={r['id']for r in data['records']}
 def text(v,n=600):
  if not isinstance(v,str)or not v.strip()or len(v)>n:raise ValueError('评估文字无效')
 def refs(v):
  if not isinstance(v,list)or len(v)>12 or not all(isinstance(x,str)for x in v)or set(v)-ids:raise ValueError('评估记录引用无效')
 text(payload.get('summary'),400);ds=payload.get('dimensions',[])
 if not isinstance(ds,list)or not all(isinstance(d,dict)for d in ds)or [d.get('key')for d in ds]!=[k for k,_ in DIMENSIONS]:raise ValueError('评估维度不完整')
 for d in ds:
  if d.get('stage')not in STAGES:raise ValueError('评估阶段无效')
  text(d.get('basis'));refs(d.get('record_ids'))
  if not isinstance(d.get('gaps'),list)or not 1<=len(d['gaps'])<=4:raise ValueError('维度缺口无效')
  for v in d['gaps']:text(v,220)
 priorities=payload.get('priorities',[])
 if not isinstance(priorities,list)or not 1<=len(priorities)<=10:raise ValueError('优先级建议无效')
 for i in priorities:
  if not isinstance(i,dict):raise ValueError('优先级建议无效')
  if i.get('priority')not in ('P0','P1','P2'):raise ValueError('优先级无效')
  text(i.get('title'),100);text(i.get('why'),240);text(i.get('next_step'),240);refs(i.get('record_ids'))
 return data

def markdown(report):
 j=report['judgment'];a=report['evidence_audit'];lines=['# 项目研究评估','',f"AI研究判断 · {j['research_revision']} · 评估{j['version']}",'','质量总分：未评。专家审核：未完成。','',j['summary'],'','## 证据检查','',f"检查时间：{a['checked_at']}；已知字段可追溯 {a['traceable_known_cells']}/{a['known_cells']}，带前提与限制的AI依据可追溯 {a['traceable_bounded_ai_items']}/{a['ai_items']}。",'',a['meaning'],'']
 for d,(_,label)in zip(j['dimensions'],DIMENSIONS):
  lines.extend(['## '+label+' · '+STAGES[d['stage']],'',d['basis'],'','待补：']);lines.extend('- '+x for x in d['gaps']);lines.extend(['','记录索引：'+('、'.join(d['record_ids'])or'暂无对应事实记录'),''])
 lines.extend(['## 补证优先级建议','','以下为研究建议，未自动下派，也不表示已经完成。',''])
 for i in j['priorities']:lines.extend(['### '+i['priority']+' '+i['title'],'',i['why'],'','下一步：'+i['next_step'],''])
 return '\n'.join(lines)

def freeze(lib,pid,payload,actor):
 with pp.lock(lib):
  p=pp.project(lib,pid);data=validate(p,payload);dest=folder(p,payload['research_revision'])/payload['version']
  if dest.exists():
   old=read(p,payload['research_revision'],payload['version'])
   if old['report']['judgment']!=payload:raise ValueError('已存在评估版本，禁止覆盖')
   return old
  report=dict(schema=SCHEMA,judgment=payload,evidence_audit=audit(p,data),quality_score=None,expert_reviewed=False,full_research_complete=False,actor=actor)
  dest.parent.mkdir(parents=True,exist_ok=True)
  with tempfile.TemporaryDirectory(prefix='.building-',dir=dest.parent)as temp:
   stage=Path(temp);pp.save(stage/'评估.json',report);(stage/'评估.md').write_text(markdown(report),encoding='utf-8');pp.save(stage/'manifest.json',dict(schema=SCHEMA,files={f.name:pp.sha(f.read_bytes())for f in stage.iterdir()if f.is_file()},created_at=pp.now(),actor=actor));os.replace(stage,dest)
 return read(p,payload['research_revision'],payload['version'])

def read(p,revision,version=None):
 base=folder(p,revision)
 if not base.exists():return dict(status='not_available',report=None)
 versions=[x.name for x in base.iterdir()if x.is_dir()and re.fullmatch(r'\d{1,3}\.\d{1,3}\.\d{1,3}',x.name)]
 if not versions:return dict(status='not_available',report=None)
 version=version or max(versions,key=lambda v:tuple(map(int,v.split('.'))))
 if version not in versions:raise ValueError('评估版本不存在')
 dest=base/version;m=pp.load(dest/'manifest.json')
 if m.get('schema')!=SCHEMA or set(m['files'])!={'评估.json','评估.md'}:raise ValueError('评估清单不符')
 for name,h in m['files'].items():
  if pp.sha(pp.safe(dest,name).read_bytes())!=h:raise ValueError('评估指纹不符')
 report=pp.load(dest/'评估.json');j=report['judgment'];validate(p,j)
 if j['version']!=version or j['research_revision']!=revision or report.get('quality_score')is not None or report.get('expert_reviewed')is not False:raise ValueError('评估声明不符')
 return dict(status='available',report=report)

def safe_read(p,revision):
 try:
  result=read(p,revision)
  if result['status']=='available':result['current_evidence_audit']=audit(p,rw.dataset(p,revision=revision))
  return result
 except (ValueError,KeyError,TypeError,OSError,json.JSONDecodeError):return dict(status='invalid',report=None)

def render(result,data,url):
 import html
 h=lambda x:html.escape(str(x),quote=True)
 if result['status']!='available':return ''
 report=result['report'];j=report['judgment'];a=result.get('current_evidence_audit')or report['evidence_audit'];titles={r['id']:r['title']for r in data['records']}
 def refs(ids):return '<details><summary>查看档案依据</summary>'+''.join('<p><a href="#record-'+h(r)+'" data-review-record="'+h(r)+'">'+h(titles[r])+' →</a></p>'for r in ids)+'</details>'if ids else''
 intro='<div class="research-box"><span class="research-tag">AI研究评估 · 非专家意见</span><p>'+h(j['summary'])+'</p><p class="research-note">绑定 '+h(j['research_revision'])+' · 评估 '+h(j['version'])+'。质量总分仍未评，不能据此判断技术水平或企业应用效果。</p><a download href="'+h(url('/api/research-document',document='review',revision=j['research_revision'],review_version=j['version']))+'">下载评估与补证建议</a></div>'
 intro+='<div class="research-box"><h3>资料能否追溯？</h3><p>已知字段：'+str(a['traceable_known_cells'])+' / '+str(a['known_cells'])+' 可追溯；AI解读：'+str(a['traceable_bounded_ai_items'])+' / '+str(a['ai_items'])+' 有可追溯依据及边界。</p><p class="research-note">截至 '+h(a['checked_at'][:16].replace('T',' '))+' UTC；这只检查文件与引文，不代表内容真实、研究完整或专家认可。</p>'+('<p>存在 '+str(len(a['issues']))+' 项需要检查，见下载报告。</p>'if a['issues']else'')+'</div>'
 for d,(_,label)in zip(j['dimensions'],DIMENSIONS):intro+='<details class="research-box"><summary>'+h(label)+'<small>'+h(STAGES[d['stage']])+'</small></summary><p>'+h(d['basis'])+'</p><h4>还需要补什么</h4><ul>'+''.join('<li>'+h(g)+'</li>'for g in d['gaps'])+'</ul>'+refs(d['record_ids'])+'</details>'
 intro+='<div class="research-box"><h3>下一步最值得补的资料</h3><p class="research-note">AI研究建议，尚未自动下派。</p>'
 for i in j['priorities']:intro+='<details><summary>'+h({'P0':'优先补齐','P1':'继续深研','P2':'后续完善'}[i['priority']])+' · '+h(i['title'])+'</summary><p>'+h(i['why'])+'</p><p>下一步：'+h(i['next_step'])+'</p>'+refs(i['record_ids'])+'</details>'
 return intro+'</div>'
