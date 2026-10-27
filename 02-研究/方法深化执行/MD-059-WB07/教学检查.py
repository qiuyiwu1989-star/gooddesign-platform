from pathlib import Path
import json,copy,math
P=Path(__file__).resolve().parent
base={'id':'WB07-INTELLIGENCE-TEACH-001','origin':'platform_semantic_branch_fixture_not_author_Agent_architecture','branch':'design_assistance','goal':'prepare traceable design alternatives','artifact_kind':'design_candidate_record','training_dataset':[],'real_model_inference_results':[],'product_operation_improved':False,'customer_approved':False,'engineering_validated':False,'unknowns':{'actual_latency_ms':None,'accuracy':None,'accepted_control_bound':None},'control_proxy':None}
proxy={'configuration':'independent_synthetic_age_gate','unit':'synthetic_tick_not_ms','now':10,'max_age':2,'threshold_origin':'arbitrary teaching bound, not customer control requirement','samples':[{'id':'S1','timestamp':8,'valid':True},{'id':'S2','timestamp':7,'valid':True},{'id':'S3','timestamp':8,'valid':None}]}
def check(d):
 if d.get('origin')!=base['origin']or d.get('product_operation_improved')is not False or d.get('customer_approved')is not False or d.get('engineering_validated')is not False:raise ValueError('unsupported operation/approval claim')
 if d.get('training_dataset')!=[]or d.get('real_model_inference_results')!=[]or d.get('unknowns')!=base['unknowns']:raise ValueError('unearned training/inference/metric evidence')
 if d.get('branch')=='design_assistance':
  if d.get('goal')!='prepare traceable design alternatives'or d.get('artifact_kind')!='design_candidate_record'or d.get('control_proxy')is not None:raise ValueError('design process and product control conflated')
  return {'status':'design_assistance_plan_only','product_intelligence_validated':False,'next':'trace inputs, compare independent engineering evidence and human review; no operational command'}
 if d.get('branch')!='product_operation':return {'status':'semantic_scope_unresolved','product_intelligence_validated':False}
 if d.get('goal')!='study availability of state for use'or d.get('artifact_kind')!='control_research_record':raise ValueError('operation goal/artifact mismatch')
 c=d.get('control_proxy')
 if c is None:return {'status':'control_material_missing','product_intelligence_validated':False}
 if c.get('configuration')!='independent_synthetic_age_gate'or c.get('unit')!='synthetic_tick_not_ms'or c.get('threshold_origin')!=proxy['threshold_origin']:raise ValueError('unversioned control condition/unit')
 if any(type(c.get(k))not in(int,float)or not math.isfinite(c[k])or c[k]<0 for k in ['now','max_age']):raise ValueError('invalid time model')
 rows=[]
 for s in c.get('samples',[]):
  t=s.get('timestamp');v=s.get('valid')
  if t is None or v is None:state='unknown'
  else:
   if type(v)is not bool or type(t)not in(int,float)or not math.isfinite(t)or t>c['now']:raise ValueError('invalid sample validity/time')
   state='invalid'if not v else'stale'if c['now']-t>c['max_age']else'within_constructed_age_only'
  rows.append({'sample':s['id'],'state':state,'machine_action':'not_authorized_by_this_research'})
 if not rows:return {'status':'control_material_missing','product_intelligence_validated':False}
 return {'status':'control_proxy_replayed_only','rows':rows,'product_intelligence_validated':False,'failure_feedback':['missing/invalid/stale data require new research record and control design review','real thresholds, response latency, independent sensing and abnormal recovery not verified'],'actual_model_training':False}
cases=[]
def add(n,d,e):
 r=check(d);assert r['status']==e;cases.append({'name':n,'input':d,'actual':r,'passed':True})
add('设计智能辅助非运行智能',base,'design_assistance_plan_only')
x=copy.deepcopy(base);x.update(branch='product_operation',goal='study availability of state for use',artifact_kind='control_research_record',control_proxy=proxy);add('产品运行研究分支代理回放',x,'control_proxy_replayed_only');assert [r['state']for r in cases[-1]['actual']['rows']]==['within_constructed_age_only','stale','unknown']
x=copy.deepcopy(x);x['control_proxy']=None;add('缺控制材料',x,'control_material_missing')
x=copy.deepcopy(base);x['branch']='unclear';add('语义未定不适用直接调用',x,'semantic_scope_unresolved')
for n,mut in [('加大模型就使用性能改进',lambda d:d.update(product_operation_improved=True)),('设计记录当控制输出',lambda d:d.update(artifact_kind='control_command')),('未知延迟填0边界',lambda d:d['unknowns'].update(actual_latency_ms=0)),('伪训练推理证据',lambda d:d['real_model_inference_results'].append('accurate'))]:
 x=copy.deepcopy(base);mut(x)
 try:check(x);raise AssertionError(n+' accepted')
 except ValueError as e:cases.append({'name':n,'actual':'rejected','reason':str(e),'passed':True})
x=copy.deepcopy(base);x['id']='DOC-ASSIST-TEACH';add('资料方案辅助另一情境',x,'design_assistance_plan_only')
for n,d in [('01-语义分支输入.json',base),('02-模型与代理数据实际检查.json',{'cases':cases,'count':len(cases),'applicability':'fixed proxy conditions only, no real model training or control execution','not_author_claim':'2003 authors distinguished two meanings; this JSON/Agent contract is platform authored'})]:(P/'教学包'/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
print(len(cases),'passed')
