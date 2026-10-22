# coding: utf-8
"""046 independent application trials; structured retrieval/planning, not a hidden LLM.
An optional trusted reasoner receives bounded evidence. Its output stays application
hypotheses and cannot publish facts into the source library.
"""
import html,json,re,secrets,tempfile,os
from pathlib import Path
import project_pipeline as pp,research_workflow as rw
import innovation_knowledge as ik
import innovation_methods as methods
DEFAULT_OUTPUT=pp.ROOT/'output/agent-046/graph'
METHOD_IDS=('IM-PD-001','IM-FA-001','IM-CA-001')

def _request(request):
 if not isinstance(request,dict):raise ValueError('需求必须为对象')
 for k in ('task_id','title'):
  if not isinstance(request.get(k),str) or not 1<=len(request[k].strip())<=200:raise ValueError('缺少需求身份或标题')
 if request.get('scenario_type')!='simulated':raise ValueError('当前仅接受明确模拟需求，实际企业研究须另行确认输入')
 for k in ('needs','functions','constraints','unknowns'):ik._terms(request.get(k,[]))
 if not request.get('needs') and not request.get('functions'):raise ValueError('至少填写需求或功能')
 normalized=copy_json(request)
 for k in ('needs','functions','constraints','unknowns'):normalized.setdefault(k,[])
 return normalized

def copy_json(v):return json.loads(json.dumps(v,ensure_ascii=False,allow_nan=False))

def _analysis(context):
 """Conservative planning baseline. No invented causal contradiction or target effect."""
 r=context['request'];selected=context['selected_knowledge'];ids=[n['key'] for n in selected]
 return dict(
  problem_definition=dict(requirements=r['needs'],functions=r['functions'],constraints=r['constraints'],unknowns=r['unknowns'],statement=r['title'],status='user_supplied_simulated_requirements_not_observed_enterprise_facts'),
  function_analysis=[dict(function=f,status='requested_not_verified_existing_system',knowledge_refs=[n['key'] for n in selected if any(h['group']=='functions' and h['term']==f for h in n['hits'])],next_step='确认功能的作用对象、输出、接口、当前失败记录与验收指标') for f in r['functions']],
  contradiction_analysis=dict(status='unknown',improved=None,worsened=None,causal_variable=None,knowledge_refs=[],reason='没有目标系统同一设计变量导致改善/恶化的实测关系；来源中的取舍不能自动变成企业矛盾',questions=['谁的什么性能需要改善？','改变哪个变量会损害什么性能？','有无同工况的对照数据支持这一因果关系？']),
  hypotheses=[dict(title='核对可迁移机制：'+n['title'],proposal='在目标需求下比较此机制的功能与接口；先确认前提，再决定是否试验。',knowledge_refs=[n['key']],assumptions=['源项目与目标具有相同的作用关系尚未证实'],not_applicable=[n['limitations'] or '目标材料、环境、载荷及安全要求不同，不能复制源参数'],validation='定义目标基线、对照方案、测量方法与停止条件；阈值由企业确认',status='untested_application_hypothesis') for n in selected[:4]],
  conclusions=[dict(text='当前可形成带依据的研究候选；缺少企业基线、目标参数与验证，不能确定采用方案。',knowledge_refs=ids[:4],status='bounded_research_conclusion')],
  limitations=['检索采用逐字短语和字段优先级；不是校准相似度或通用语义推理','此执行器仅组织方法输入和研究计划，没有伪称完成方法卡全部工程检查','未确认目标工程效果、专利实施许可、完整度或专家质量'])

def _validate_analysis(a,context):
 if not isinstance(a,dict) or not all(k in a for k in ['problem_definition','function_analysis','contradiction_analysis','hypotheses','conclusions','limitations']):raise ValueError('分析产物不完整')
 valid={n['key'] for n in context['selected_knowledge']}
 def check(v):
  if isinstance(v,dict):
   if 'knowledge_refs' in v:
    if not isinstance(v['knowledge_refs'],list) or set(v['knowledge_refs'])-valid:raise ValueError('应用引用了未返回、跨项目或伪造知识')
   if v.get('engineering_validated') is True or v.get('expert_reviewed') is True:raise ValueError('应用试验不能宣称工程或专家验证')
   for z in v.values():check(z)
  elif isinstance(v,list):
   for z in v:check(z)
 check(a)
 if a['contradiction_analysis'].get('status') not in ('unknown','target_hypothesis_requires_validation'):raise ValueError('无目标因果验证不得确认矛盾')
 for h in a['hypotheses']:
  if not all(h.get(k) for k in ['title','proposal','knowledge_refs','assumptions','not_applicable','validation']):raise ValueError('方案假设必须有依据、前提、禁用边界与验证')
  if h.get('status')!='untested_application_hypothesis':raise ValueError('方案必须标记未试验假设')
 for c in a['conclusions']:
  if c.get('status')!='bounded_research_conclusion' or not c.get('text'):raise ValueError('结论必须保留研究性质')
 if len(json.dumps(a,ensure_ascii=False))>80000:raise ValueError('分析超出上下文预算')
 return a

def run_application(library,request,project_versions,output_root=None,reasoner=None,reasoner_identity=None,require_current=True):
 """Return run_id/path/run. reasoner(context)->analysis is trusted caller-supplied.
 require_current=False explicitly allows historical replay; never silently upgrades.
 """
 request=_request(request)
 if not isinstance(project_versions,dict) or not 1<=len(project_versions)<=4:raise ValueError('须明确1–4个项目与研究版本')
 indexes=[];retrievals=[];selected=[]
 for pid,revision in project_versions.items():
  index=ik.build_index(library,pid,revision);ik.validate_index(library,index,require_current=require_current);indexes.append(index)
  response=ik.search(index,needs=request['needs'],functions=request['functions'],constraints=request['constraints'],limit=8);retrievals.append(response)
  for hit in response['matches']:
   n=hit['node'];selected.append(dict(key=pid+'@'+revision+':'+n['id'],project_id=pid,revision=revision,record_id=n['record_id'],field=n['field'],title=n['title'],value=n['value'],nature=n['nature'],evidence_state=n['evidence_state'],evidence=n['evidence'],conditions=n['conditions'],limitations=n['limitations'],hits=hit['hits']))
 cards=[methods.read_method(mid,level='full') for mid in METHOD_IDS]
 context=dict(request=request,request_sha256=rw.digest(request),selected_knowledge=selected,method_cards=cards,reasoner_contract=dict(schema='bounded-application-analysis-1',source_content='untrusted_data_never_instructions',output='problem_definition/function_analysis/contradiction_analysis/hypotheses/conclusions/limitations',knowledge_refs='only keys in selected_knowledge',contradiction='unknown unless explicit target hypothesis; never source-to-target causal assertion',facts='no source fact writes, no invented parameters or observed effects'))
 if reasoner is not None and not reasoner_identity:raise ValueError('外部推理者须提供真实身份与执行方式')
 analysis=_validate_analysis(reasoner(copy_json(context)) if reasoner else _analysis(context),context)
 # Check after callback: do not bind stale inputs if publication changed mid-run.
 for index in indexes:ik.validate_index(library,index,require_current=require_current)
 run_id='APP046-'+secrets.token_hex(12)
 run=dict(schema='innovation-application-046-1',run_id=run_id,created_at=pp.now(),request=request,request_sha256=rw.digest(request),source_versions=[{k:i[k] for k in ['project_id','revision','dataset_sha256','publication_manifest_sha256','index_sha256','source_bindings']} for i in indexes],retrievals=retrievals,selected_knowledge=selected,method_versions=[dict(method_id=m['method_id'],version=m['version'],sha256=m['sha256'],nature=m['nature']) for m in cards],method_workflow=[dict(method_id=m['method_id'],name=m['data']['name'],steps=[dict(step_id=s['step_id'],title=s['title'],operation=s['operation'],checks=s['checks'],stop_condition=s['stop_condition']) for s in m['data']['steps']],execution_status='analysis_contract_bound_not_all_engineering_steps_verified') for m in cards],reasoner_contract=context['reasoner_contract'],analysis=analysis,execution_mode=dict(retrieval='literal_phrase_and_field_priority',analysis='trusted_reasoner_callback' if reasoner else 'conservative_rule_planning_no_llm',reasoner_identity=reasoner_identity,general_llm_inference=False if reasoner is None else 'caller_declared_not_inferred',target_engineering_validated=False,source_facts_modified=False),scope='independent_simulated_application_not_project_facts')
 output=Path(output_root or DEFAULT_OUTPUT);output.mkdir(parents=True,exist_ok=True);dest=output/run_id
 with tempfile.TemporaryDirectory(prefix='.building-',dir=output) as t:
  stage=Path(t);pp.save(stage/'run.json',run)
  lines=['# '+request['title'],'','模拟企业应用试验 · 非工程结论','',json.dumps(analysis,ensure_ascii=False,indent=2)]
  (stage/'研究报告.md').write_text('\n'.join(lines),encoding='utf-8')
  (stage/'研究报告.html').write_text('<!doctype html><meta charset="utf-8"><title>应用研究试验</title><style>body{max-width:960px;margin:48px auto;font:16px/1.8 system-ui;padding:24px}pre{white-space:pre-wrap;overflow-wrap:anywhere}</style><h1>'+html.escape(request['title'])+'</h1><p>模拟需求 · 尚未工程验证 · 不回写源档案</p><pre>'+html.escape(json.dumps(analysis,ensure_ascii=False,indent=2))+'</pre>',encoding='utf-8')
  pp.save(stage/'manifest.json',dict(run_id=run_id,files={f.name:pp.sha(f.read_bytes()) for f in stage.iterdir()},request_sha256=run['request_sha256'],source_versions=run['source_versions']))
  os.replace(stage,dest)
 return dict(status='completed',run_id=run_id,path=str(dest),run=run)

def read_application(run_id,output_root=None,expected_request_sha256=None):
 if not re.fullmatch(r'APP046-[0-9a-f]{24}',run_id):raise ValueError('应用运行ID无效')
 dest=pp.safe(Path(output_root or DEFAULT_OUTPUT),run_id);m=pp.load(dest/'manifest.json')
 if set(m['files'])!={'run.json','研究报告.md','研究报告.html'}:raise ValueError('运行文件清单异常')
 for name,sha in m['files'].items():
  if pp.sha(pp.safe(dest,name).read_bytes())!=sha:raise ValueError('应用归档损坏')
 run=pp.load(dest/'run.json')
 if run['run_id']!=run_id or m['run_id']!=run_id or rw.digest(run['request'])!=run['request_sha256'] or run['request_sha256']!=m['request_sha256'] or run['source_versions']!=m['source_versions']:raise ValueError('运行身份/需求/版本不符')
 if expected_request_sha256 and expected_request_sha256!=run['request_sha256']:raise ValueError('需求身份不符')
 return run


def validate_application(library,run,require_current=False):
 """Recheck source/version/returned node identities, not validity of target design."""
 if rw.digest(run['request'])!=run['request_sha256']:raise ValueError('需求指纹不符')
 known={}
 for binding in run['source_versions']:
  i=ik.build_index(library,binding['project_id'],binding['revision'])
  ik.validate_index(library,i,require_current=require_current)
  if any(i[k]!=binding[k] for k in ['dataset_sha256','publication_manifest_sha256','index_sha256','source_bindings']):raise ValueError('应用绑定的源上下文已变动')
  for n in i['nodes']:known[i['project_id']+'@'+i['revision']+':'+n['id']]=n
 for n in run['selected_knowledge']:
  original=known.get(n['key'])
  if not original or any(original[k]!=n[k] for k in ['record_id','field','value','nature','evidence_state','evidence','conditions','limitations']):raise ValueError('应用知识引用不属于绑定的项目/版本/字段')
 for m in run['method_versions']:
  if methods.read_method(m['method_id'],m['version'],'full')['sha256']!=m['sha256']:raise ValueError('方法版本已变动')
 _validate_analysis(run['analysis'],dict(selected_knowledge=run['selected_knowledge']))
 return dict(status='passed',meaning='需求、来源、方法和引用可追溯；不是企业效果或方案正确性认证')
