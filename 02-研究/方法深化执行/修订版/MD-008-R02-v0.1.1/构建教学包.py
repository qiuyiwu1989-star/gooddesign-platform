# -*- coding: utf-8 -*-
"""Fixed teaching information-update, not field research or a universal Double Diamond engine."""
from pathlib import Path
import copy,hashlib,json,math
B=Path(__file__).resolve().parent;P=B/'教学包'
SP=B.parent/'MD-001-R48-v0.1.1/教学包/00-共享教学输入-v0.1.0.json'
SHA='c9d262d505656bcaf6c76edee99e3615440f5e2d1c6ef4067e9c1b15a2ddcd70'
assert hashlib.sha256(SP.read_bytes()).hexdigest()==SHA
BIND={'problem_id':'TAP-TEACH-001','version':'0.1.0','shared_sha256':SHA,'upstream_method_status':'first_batch_revised_context_only_not_customer_approved'}
def save(name,x):(P/name).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False))
def logged(x):
 if isinstance(x,float)and not math.isfinite(x):return {'python_nonfinite_value':str(x),'note':'native Python probe value; tagged for valid JSON logging'}
 if isinstance(x,list):return [logged(v)for v in x]
 if isinstance(x,dict):return {k:logged(v)for k,v in x.items()}
 return x
brief={'schema':'fixed_double_diamond_information_fixture-1','binding':BIND,'origin':'constructed_teaching_not_customer_material','prompt':'构造委托：让设备工作更快；初始偏好是提高驱动速度。','frames':[{'id':'FRAME-NORMAL','text':'正常作业动作占主要负担','status':'competing_hypothesis'},{'id':'FRAME-RECOVERY','text':'异常恢复与清理占主要负担','status':'competing_hypothesis'}],'evidence_stage':'total_only','totals':[100],'segments':None,'unit':'synthetic_tick_not_seconds','team_votes':{'FRAME-NORMAL':5,'FRAME-RECOVERY':0},'customer_approved':False,'field_research_conducted':False,'findings':[]}
def examine(i):
 if i.get('binding')!=BIND:raise ValueError('binding_changed')
 if i.get('origin')!='constructed_teaching_not_customer_material'or i.get('customer_approved')or i.get('field_research_conducted')or i.get('findings'):raise ValueError('evidence_status_promoted')
 if i.get('frames')!=brief['frames']:raise ValueError('frame_missing_or_claimed_confirmed')
 if i.get('unit')!='synthetic_tick_not_seconds':raise ValueError('synthetic_unit_promoted')
 if not i.get('totals')or any(type(v)not in(int,float)or not math.isfinite(v)or v<0 for v in i['totals']):raise ValueError('invalid_total')
 if i['segments']is None:
  return {'state':'cannot_distinguish_frames','retained':['FRAME-NORMAL','FRAME-RECOVERY'],'reason':'total alone has multiple decompositions; votes do not identify observed burden','customer_approved':False,'next_action':'obtain_phase_defined_records','did_votes_confirm_need':False}
 if len(i['segments'])!=len(i['totals']):raise ValueError('missing_phase_record')
 sums={'normal':0,'recovery':0}
 for total,row in zip(i['totals'],i['segments']):
  if set(row)!={'normal','recovery'}:raise ValueError('phase_coverage_incomplete')
  if any(type(v)not in(int,float)or not math.isfinite(v)or v<0 for v in row.values()):raise ValueError('invalid_phase_value')
  if not math.isclose(sum(row.values()),total):raise ValueError('phase_total_mismatch')
  for k,v in row.items():sums[k]+=v
 den=sum(sums.values())
 if den==0:return {'state':'inconclusive_zero_observation','retained':['FRAME-NORMAL','FRAME-RECOVERY'],'customer_approved':False,'next_action':'check_observation_window'}
 focus='FRAME-RECOVERY'if sums['recovery']>sums['normal']else'FRAME-NORMAL'if sums['normal']>sums['recovery']else None
 return {'state':'constructed_partition_supports_provisional_focus'if focus else'inconclusive_equal_partition','phase_totals':sums,'recovery_fraction_in_constructed_table':sums['recovery']/den,'provisional_focus':focus,'real_customer_frame':None,'causal_finding':None,'next_action':'return_to_define_then_collect_real_context','does_not_prove':['actual_tapping_frequency','performance_gain','correct_solution','customer_priority']}
save('01-初始委托与竞争问题.json',brief)
before=examine(brief)
updated=copy.deepcopy(brief);updated.update(evidence_stage='constructed_segment_update',segments=[{'normal':40,'recovery':60}])
after=examine(updated)
save('02-区分性桌面检查.json',{'before_input':brief,'before':before,'constructed_update':updated,'after':after,'executed_activity':'arithmetic/declared-partition desk check, no physical observation','note':'80/20 and40/60 can share a total of100; only the declared phase split changes which focus is supported inside the table.'})
paths=[{'id':'PATH-SPEED','response_to':['N-T01'],'uncovered':['N-T02','N-T03','N-T04'],'status':'research_path','why_not_selected_as_solution':'No evidence that increased speed resolves recovery or is safe.'},{'id':'PATH-RECOVER','response_to':['N-T02','N-T03'],'uncovered':['N-T01','N-T04'],'status':'research_path','why_not_selected_as_solution':'Recovery sequence and states remain undefined.'},{'id':'PATH-SERVICE','response_to':['N-T04'],'uncovered':['N-T01','N-T02','N-T03'],'status':'research_path','why_not_selected_as_solution':'No observed full-shift service process.'}]
assert all(set(x['response_to'])|set(x['uncovered'])=={'N-T01','N-T02','N-T03','N-T04'}and not set(x['response_to'])&set(x['uncovered'])for x in paths)
save('03-暂定范围与第二钻计划.json',{'binding':BIND,'provisional_problem_version':'DD-DRAFT-0.1','statement':'先辨别完整作业各阶段负担及恢复需要，再决定是否改变驱动、恢复或服务。','source_of_change':'constructed arithmetic insight only','paths':paths,'delivery_plan':'设计实际记录各阶段与异常的低风险研究；真实材料到位后重新定义并比较','actual_user_tests':0,'observations':[],'final_solution':None})
cases=[]
def probe(name,kind,x,mut,expected):
 v=copy.deepcopy(x);mut(v)
 try:r=examine(v);observed=r['state']
 except ValueError as e:r={'error':str(e)};observed='rejected'
 assert observed==expected,(name,observed)
 cases.append({'name':name,'class':kind,'observed':observed,'expected':expected,'input':logged(v),'output':r})
probe('normal-partition-updates-focus','正常',updated,lambda x:None,'constructed_partition_supports_provisional_focus')
probe('total-only-no-convergence','缺材料',brief,lambda x:None,'cannot_distinguish_frames')
probe('votes-not-observation','不适用',brief,lambda x:x.update(team_votes={'FRAME-NORMAL':1000,'FRAME-RECOVERY':0}),'cannot_distinguish_frames')
probe('zero-window-not-success','边界',updated,lambda x:x.update(totals=[0],segments=[{'normal':0,'recovery':0}]),'inconclusive_zero_observation')
probe('incomplete-phase','冲突',updated,lambda x:x['segments'][0].pop('recovery'),'rejected')
probe('total-does-not-match','冲突',updated,lambda x:x['segments'][0].update(recovery=70),'rejected')
probe('not-customer-approved','边界',brief,lambda x:x.update(customer_approved=True),'rejected')
probe('finite-values-required','边界',updated,lambda x:x['segments'][0].update(normal=float('inf')),'rejected')
probe('no-silent-problem-change','冲突',brief,lambda x:x['binding'].update(problem_id='OTHER'),'rejected')
probe('do-not-rename-ticks-seconds','边界',updated,lambda x:x.update(unit='s'),'rejected')
save('04-实际检查结果.json',{'executed':True,'checks':cases,'passed':len(cases),'field_tests':0,'scope':'fixed arithmetic and state/partition guards; not semantic problem discovery'})
transfer={'scenario':'DOC-HANDOFF-TEACH-002','origin':'constructed_desk_only','initial_request':'让录入更快','competing_frames':['录入慢','资料核对/追补负担大'],'total_only':100,'two_compatible_partitions':[{'entry':90,'reconciliation':10},{'entry':30,'reconciliation':70}],'result':'total alone cannot select frame','no_actual_user_findings':True}
assert all(sum(x.values())==100 for x in transfer['two_compatible_partitions'])
save('05-迁移桌面检查.json',transfer)
print(json.dumps({'method':'R02','checks':len(cases),'before':before['state'],'after':after['provisional_focus'],'customer_approved':False},ensure_ascii=False))
