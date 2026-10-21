# coding: utf-8
"""040 versioned method reads and auditable simulated run artifacts (not general AI inference)."""
import json,os,re,hashlib
from pathlib import Path
import project_pipeline as pp
ROOT=pp.ROOT;LIB=ROOT/'04-知识库/创新方法库';RUNS=Path(os.environ.get('GOODDESIGN_RUNS',str(ROOT/'output/innovation-runs')))
CONTRACTS={
 'problem_brief':dict(required=['task_id','actor','object','desired_outcome','boundary','requirements','constraints','unknowns','decision_level']),
 'function_model':dict(required=['boundary','nodes','functions','interactions','priority_issues']),
 'enterprise_brief':dict(required=['task_id','decision_level','directions','questions','validation_plan','limitations'])}
def validate_card(m):
 required=['method_id','version','name','purpose','provenance','inputs','steps','knowledge_queries','outputs','quality_checks','failure_cases','evaluations']
 if any(not m.get(k)for k in required):raise ValueError('方法卡必需字段缺失')
 if m['provenance']['nature']!='platform_adaptation':raise ValueError('本批方法须明确平台改编性质')
 if not m['provenance']['sources']:raise ValueError('方法缺少原始出处')
 for s in m['provenance']['sources']:
  if not all(s.get(k)for k in ['url','publisher','locator','basis','rights']):raise ValueError('出处缺少定位或权利说明')
 known=set();outputs=set(i['key']for i in m['inputs']);queries={q['query_id']for q in m['knowledge_queries']}
 for step in m['steps']:
  if step['step_id']in known or not set(step['depends_on'])<=known:raise ValueError('步骤依赖错误或有环')
  if not set(step['input_refs'])<=outputs:raise ValueError('步骤输入没有前序产物或方法输入')
  if not set(step['knowledge_query_ids'])<=queries:raise ValueError('步骤引用未知检索规则')
  if not all(step.get(k)for k in ['title','operation','checks','stop_condition','output_key']):raise ValueError('步骤缺少操作/检查/停止条件')
  known.add(step['step_id']);outputs.add(step['output_key'])
 if not {o['key']for o in m['outputs']}<=outputs:raise ValueError('方法输出没有步骤产物')
 return dict(status='passed',steps=len(known),sources=len(m['provenance']['sources']))
def catalog():return pp.load(LIB/'方法目录.json')
def read_method(method_id,version=None,level='overview',step_id=None,offset=0,limit=5):
 if not re.fullmatch(r'IM-[A-Z]{2}-\d{3}',method_id):raise ValueError('方法ID格式无效')
 row=next((m for m in catalog()['methods']if m['method_id']==method_id),None)
 if row is None:raise ValueError('方法未登记')
 version=version or row['version']
 if not re.fullmatch(r'\d+\.\d+\.\d+',version):raise ValueError('方法版本格式无效')
 f=pp.safe(LIB,'方法/'+method_id+'/'+version+'/方法卡.json');m=pp.load(f);validate_card(m)
 if row['version']==version and row.get('sha256')and row['sha256']!=pp.sha(f.read_bytes()):raise ValueError('方法版本指纹不符')
 if not 0<=offset or not 1<=limit<=20:raise ValueError('offset>=0，limit须1–20')
 base=dict(method_id=method_id,version=version,sha256=pp.sha(f.read_bytes()),nature='platform_adaptation',review_status=m['review_status'],validation_status=m['validation_status'])
 if level=='overview':base['data']={k:m[k]for k in ['name','purpose','preconditions','exclusions','missing_input_questions','inputs','outputs','provenance','quality_checks']}
 elif level=='steps':
  rows=[s for s in m['steps']if not step_id or s['step_id']==step_id];base.update(data=rows[offset:offset+limit],total=len(rows),next_offset=offset+limit if offset+limit<len(rows)else None)
 elif level=='full':base['data']=m
 else:raise ValueError('level须overview/steps/full')
 return base
def search_methods(query='',offset=0,limit=10):
 if offset<0 or not 1<=limit<=20:raise ValueError('分页参数无效')
 q=query.lower();rows=[x for x in catalog()['methods']if q in json.dumps(x,ensure_ascii=False).lower()]
 return dict(data=rows[offset:offset+limit],total=len(rows),next_offset=offset+limit if offset+limit<len(rows)else None,search_type='catalog_keyword_not_semantic')
def task_gate(task):
 missing=[k for k in ['task_id','actor','object','desired_outcome','boundary']if not task.get(k)]
 if missing:raise ValueError('任务关键输入缺失:'+','.join(missing))
 if task.get('scenario_type')!='simulated':raise ValueError('当前执行器仅用于已编写的模拟研究示例，不接受真实企业任务冒充通用自动推理')
 return dict(decision_level='concept_only_requires_confirmation',unknowns=[k for k,v in task.get('target_parameters',{}).items()if v is None])
def filter_directions(directions,constraints):
 out=[]
 for d in directions:
  d=dict(d);d['status']='conditional';d['blocked_by']=[]
  for key in d.get('requires',[]):
   if constraints.get(key)is False:d['blocked_by'].append(key)
  if d['blocked_by']:d['status']='excluded'
  d['engineering_validated']=False;out.append(d)
 return out
def validate_run(run):
 task_gate(run['task']);evidence={e['evidence_id']:e for e in run['evidence']};steps=set();method_ids={m['method_id']:m for m in run['method_versions']}
 for e in evidence.values():
  if pp.sha(e['text'].encode())!=e['text_sha256']:raise ValueError('证据正文指纹不符')
  if not all(e.get(k)for k in ['source_id','chunk_id','locator','source_sha256','canonical_source_id']):raise ValueError('证据定位不完整')
 completed_outputs={}
 retrievals={t['id']:t for t in run['retrievals']}
 for t in retrievals.values():
  if t['response_sha256']!=pp.sha(json.dumps(t['response'],ensure_ascii=False,sort_keys=True,allow_nan=False).encode()):raise ValueError('MCP结果指纹不符')
 for e in evidence.values():
  returned=[(t,b)for t in retrievals.values()if t['tool']=='gd_read_evidence'and t['arguments'].get('source_id')==e['source_id']for b in t['response']['data']if b['id']==e['chunk_id']]
  if not any(b['text']==e['text']and t['response']['source_sha256']==e['source_sha256']for t,b in returned):raise ValueError('证据与实际MCP返回内容不一致')
 frozen_inputs={'task@'+run['task']['version']:run['task'],'case.problem':run['case_records']['problem'],'case.innovation':run['case_records']['innovation'],'case.evidence':run['evidence']}
 for stage in run['stages']:
  mid=stage['method_id'];m=read_method(mid,method_ids[mid]['version'],'full')
  if m['sha256']!=method_ids[mid]['sha256']:raise ValueError('方法内容自运行后变化')
  expected={s['step_id']:s for s in m['data']['steps']}
  bindings=stage.get('input_bindings',{})
  if not {i['key']for i in m['data']['inputs']if i['required']}<=set(bindings):raise ValueError('方法缺少必需输入绑定')
  for key,b in bindings.items():
   if b.get('from_method'):
    prior=completed_outputs.get((b['from_method'],b['output_key']))
    if prior is None or b['sha256']!=pp.sha(json.dumps(prior,ensure_ascii=False,sort_keys=True,allow_nan=False).encode()):raise ValueError('方法交接产物指纹不符')
   else:
    if b.get('from_ref')not in frozen_inputs:raise ValueError('方法输入引用没有冻结内容')
    if b['sha256']!=pp.sha(json.dumps(frozen_inputs[b['from_ref']],ensure_ascii=False,sort_keys=True,allow_nan=False).encode()):raise ValueError('输入/证据自方法调用后变化')
  for s in stage['steps']:
   if s['step_id']not in expected:raise ValueError('运行使用未知方法步骤')
   if not set(s['evidence_ids'])<=set(evidence):raise ValueError('步骤引用缺失证据')
   if not set(s.get('depends_on',[]))<=steps:raise ValueError('运行依赖步骤未执行')
   if not s.get('output'):raise ValueError('缺少中间产物')
   queries={q['query_id']:q for q in m['data']['knowledge_queries']}
   for qid in expected[s['step_id']]['knowledge_query_ids']:
    calls=s.get('knowledge_retrievals',{}).get(qid,[])
    if not calls:raise ValueError('方法知识查询未实际执行')
    if any(c not in retrievals or retrievals[c]['tool']!='gd_read_records'or retrievals[c]['arguments'].get('entity')!=queries[qid]['entity']for c in calls):raise ValueError('方法知识查询与调用轨迹不匹配')
   steps.add(s['step_id'])
  if {s['step_id']for s in stage['steps']}!=set(expected):raise ValueError('方法未逐步完成')
  key=stage['final_output_key']
  if key in CONTRACTS and not set(CONTRACTS[key]['required'])<=set(stage['output']):raise ValueError('阶段输出契约不完整')
  completed_outputs[(mid,key)]=stage['output']
 for section in ['source_case','directions']:
  if section=='directions':
   for d in run['enterprise_output']['directions']:
    if not set(d['evidence_ids'])<=set(evidence)or not set(d['method_step_ids'])<=steps:raise ValueError('企业方向缺少依据')
    if d.get('engineering_validated'):raise ValueError('模拟演示不能标工程验证通过')
 expected_filter=filter_directions(run['enterprise_output']['directions'],run['task']['constraints'])
 if [d['status']for d in expected_filter]!=[d['status']for d in run['enterprise_output']['directions']]:raise ValueError('硬约束未反映到方向筛选')
 if run['enterprise_output']['decision_level']!='concept_only_requires_confirmation':raise ValueError('缺参任务不得升级工程定型建议')
 return dict(status='passed',methods=len(method_ids),steps=len(steps),evidence_blocks=len(evidence),decisions='concept_hypotheses_only')
def read_run(run_id='latest',section='overview'):
 if run_id=='latest':run_id=pp.load(RUNS/'latest.json')['run_id']
 if not re.fullmatch(r'RUN-\d{8}T\d{6}-[a-f0-9]{6}',run_id):raise ValueError('运行ID无效')
 folder=pp.safe(RUNS,run_id);manifest=pp.load(folder/'manifest.json')
 for name,h in manifest['files'].items():
  if pp.sha(pp.safe(folder,name).read_bytes())!=h:raise ValueError('运行归档校验失败')
 run=pp.load(folder/'run.json')
 if section=='overview':return {k:run[k]for k in ['run_id','task','source_case','method_versions','execution_mode','validation','enterprise_output']}
 if section not in ['stages','evidence','enterprise_output','retrievals','full']:raise ValueError('运行读取层级无效')
 return run if section=='full'else run[section]
