"""QFD research deployment with unknowns. No fabricated weights, scores or targets."""
from pathlib import Path
import copy,hashlib,itertools,json
P=Path(__file__).resolve().parent;ROOT=P.parents[2];O=P/'教学包';O.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,d):p=O/n;p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');return p
SP=ROOT/'02-研究/方法深化执行/MD-001-R48/教学包/00-共享教学输入-v0.1.0.json';S=json.loads(SP.read_text());assert sha(SP)=='c9d262d505656bcaf6c76edee99e3615440f5e2d1c6ef4067e9c1b15a2ddcd70'
binding={'path':str(SP.relative_to(ROOT)),'problem_id':S['problem_id'],'version':S['version'],'sha256':sha(SP),'review_state':'first_batch_changes_requested_not_expert_approved'}
responses=[{'id':i,'type':'research_response_not_frozen_engineering_requirement','text':t,'measurement_unit':None,'target':None,'direction':None,'target_source':None,'responsibility_role':r,'appointment_status':'not_assigned_to_real_person','acceptance_status':'not_defined'}for i,t,r in [('HOW-T01','研究允许组织边界与可观测信号的对应及测量误差','技术/组织专业共同研究'),('HOW-T02','分开定义异常触发、停止、退出、恢复事件并取得记录','现场/控制研究'),('HOW-T03','研究操作决策所需状态、测量时点及理解方式','人因/信息研究'),('HOW-T04','梳理清理维护与转场的任务责任、资源和等待','服务/使用研究')]]
needs=copy.deepcopy(S['needs']);matrix=[{'need_id':n['id'],'response_id':h['id'],'state':'unknown','strength':None,'evidence_refs':[],'rationale_question':'该响应对本需要的作用、条件及责任应由材料或专业判断明确，不能因名称相似填强相关'}for n,h in itertools.product(needs,responses)]
case={'schema':'qfd-research-deployment-0.1.0','problem_id':S['problem_id'],'mode':'research_unknowns_only','source_binding':binding,'source_needs':needs,'source_unknowns':S['unknowns'],'response_actions':responses,'relationships':matrix,'importance':[{'need_id':n['id'],'scale':'not_elicited','value':None,'source':None}for n in needs],'customer_approved':False,'hard_requirement_waivers':[],'assumption':'仅建立需要到研究响应的追溯结构；不是填完质量屋或完成ISO16355实施'}
save('01-需要响应输入.json',case)
def check(d):
 if d.get('source_binding')!=binding or d.get('problem_id')!=S['problem_id']:raise ValueError('upstream_identity_mismatch')
 if d.get('mode')!='research_unknowns_only'or d.get('customer_approved')is not False:raise ValueError('unsupported_approval_or_execution_mode')
 if d.get('source_needs')!=S['needs']or d.get('source_unknowns')!=S['unknowns']:raise ValueError('shared_needs_or_unknowns_changed')
 if d.get('hard_requirement_waivers')!=[]:raise ValueError('preferences_cannot_waive_hard_requirement')
 nids={n['id']for n in S['needs']};hids=[r['id']for r in d['response_actions']]
 if len(hids)!=len(set(hids))or not hids:raise ValueError('invalid_response_ids')
 for h in d['response_actions']:
  if not {'measurement_unit','target','direction','target_source','responsibility_role','appointment_status','acceptance_status'}<=set(h):raise ValueError('missing_explicit_response_fields')
  if any(h.get(k)is not None for k in ['measurement_unit','target','direction','target_source']):raise ValueError('unsupported_target_or_unit_injected')
  if not h.get('responsibility_role')or h.get('appointment_status')!='not_assigned_to_real_person':raise ValueError('responsibility_or_appointment_misrepresented')
 expected=set(itertools.product(nids,hids));seen=set()
 for r in d['relationships']:
  k=(r['need_id'],r['response_id'])
  if k not in expected or k in seen:raise ValueError('dangling_or_duplicate_relationship')
  seen.add(k)
  if 'strength'not in r or r.get('state')!='unknown'or r.get('strength')is not None:raise ValueError('unfounded_relationship_score')
  if r.get('evidence_refs')!=[]:raise ValueError('unsupported_relationship_evidence')
 if seen!=expected:raise ValueError('relationship_grid_incomplete')
 im=d['importance']
 if {x['need_id']for x in im}!=nids or len(im)!=len(nids):raise ValueError('importance_coverage_mismatch')
 if any(x['value']is not None or x['scale']!='not_elicited'or x.get('source')is not None for x in im):raise ValueError('unelicited_preference_score')
 return {'status':'research_deployment_trace_only','needs':len(nids),'responses':len(hids),'unknown_relationships':len(seen),'priority_scores':None,'ranking':None,'target_values_generated':False,'reason':'未取得关系、可用偏好尺度及目标来源，不能聚合或反推阈值','next_actions':['核源需要','核响应/关系依据','取得偏好尺度和硬要求','独立定义工程目标及验收口径'],'full_qfd_or_standard_compliance':False}
save('02-展开与停止判断.json',check(case))
save('03-权重敏感性前置分析.json',{'executed_analysis':'input completeness and dominance-free underdetermination check; no fictitious numerical scoring','missing':['cardinal/ratio importance evidence','justified relationship mapping','independence/overlap handling','confirmed hard requirements'],'priority_expression':'P_j = sum_i(w_i * r_ij) is only an optional model, not generally justified by ordinal ratings','sensitivity_outcome':'not_identifiable_from_current_input','why':'w与r均未给，方向和量纲也未定；没有有依据的扰动区间，不能生成看似精确的排序稳健性','future_plan':['先证明量表可做对应运算','登记关系证据与相关指标重复计量问题','仅在充分输入后检查偏好/关系变化是否翻转结论'],'target_inference':'任何排序或关系量表均不推出切入深度等目标数值','is_actual_weight_sweep':False})
save('04-向功能与验证交接.json',{'source_binding':binding,'allowed':'R14可研究作用、R42可提出验证口径；上游仍未审核/批准','handoff_fields':['need_id','response_id','relationship_state','responsibility_role','target_source','scope and source SHA'],'not_allowed':['按空白或unknown填0','把9/3/1当物理阈值','用满意偏好豁免安全/硬要求','将已分配责任误写为实际任命'],'r11_relation':'Kano类别不是本包工程重要性分值；本轮没有客户Kano结果可导入'})
tests=[]
def run(name,kind,d,expect):
 f=save('检查输入-'+name+'.json',d)
 try:r=check(d);actual='accepted'
 except Exception as e:r={'error':str(e)};actual='rejected'
 assert actual==expect,(name,actual);tests.append({'id':name,'category':kind,'actual':actual,'expected':expect,'input':f.name,'input_sha256':sha(f),'output':r})
run('normal-unknown-matrix','normal',case,'accepted')
for name,kind,mut in [('missing-relationship','missing',lambda a:a['relationships'].pop()),('not-ranker','not_applicable',lambda a:a.update(mode='certified_prioritization')),('unknown-to-zero','boundary',lambda a:a['relationships'][0].update(strength=0)),('fake-target-from-nine','conflict',lambda a:a['response_actions'][0].update(target=9)),('unelicited-weight','boundary',lambda a:a['importance'][0].update(value=5)),('erase-source-unknowns','missing',lambda a:a.update(source_unknowns=[])),('source-version','conflict',lambda a:a['source_binding'].update(version='WRONG')),('hard-waiver','not_applicable',lambda a:a.update(hard_requirement_waivers=['unsafe_but_preferred']))]:
 a=copy.deepcopy(case);mut(a);run(name,kind,a,'rejected')
a=copy.deepcopy(case);a['relationships'][0]['evidence_refs']=['NO-SOURCE'];run('invented-relationship-evidence','conflict',a,'rejected')
a=copy.deepcopy(case);del a['response_actions'][0]['target'];run('missing-null-is-not-explicit-unknown','missing',a,'rejected')
# A structural subset of responses is legitimate only with full need grid retained.
a=copy.deepcopy(case);a['response_actions']=a['response_actions'][:2];a['relationships']=[x for x in a['relationships']if x['response_id']in{'HOW-T01','HOW-T02'}];run('narrow-response-study-with-needs-retained','boundary',a,'accepted')
save('05-实际检查记录.json',{'script_sha256':sha(Path(__file__)),'tests':tests,'passed':len(tests),'not_claimed':['general semantic sufficiency','real QFD deployment','numerical sensitivity sweep','expert validation']})
transfer={'id':'DOC-QFD-TEACH-001','scope':'independent_constructed_desktop_mapping_not_same_checker_generalization','need':'资料交接能核对版本（假设）','response_actions':['记录来源版本','显示差异与确认状态'],'relationship_strengths':[None,None],'importance':None,'target':None,'result':'可以建立待确认响应，不能从上述映射推导检索秒数或错误率目标','actual_assertion':'all importance/strength/target remain None'}
assert transfer['target']is None and all(x is None for x in transfer['relationship_strengths']);save('06-不同情境桌面迁移.json',transfer)
print('R12',len(tests),'checks; no ranking, numeric scores or targets invented')
