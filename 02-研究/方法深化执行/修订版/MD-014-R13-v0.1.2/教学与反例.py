# -*- coding: utf-8 -*-
"""Fixed second-batch teaching models. All new outputs only in MD014/015/016.
Representation collisions, declared logic and evidence bookkeeping are not human/engineering validation.
"""
from pathlib import Path
import copy,hashlib,json
ROOT=Path(__file__).resolve().parents[4];P=Path(__file__).resolve().parent
DIRS={'R13':P}
def save(rid,name,o):
 p=DIRS[rid]/'教学包'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2));return p
SHA=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
shared=ROOT/'02-研究/方法深化执行/MD-001-R48/教学包/00-共享教学输入-v0.1.0.json'
expected='c9d262d505656bcaf6c76edee99e3615440f5e2d1c6ef4067e9c1b15a2ddcd70'
assert SHA(shared)==expected
CONTEXT={'problem_id':'TAP-TEACH-001','version':'0.1.0','sha256':expected,'path':str(shared.relative_to(ROOT)),'status':'constructed_research_not_customer_evidence'}
# The second batch consumes only the frozen shared context; first-batch method outputs remain pending corrections.
FIRST={'R36':'MD-005-R36/教学包/02-主链逐格比较与补证队列.json','R44':'MD-006-R44/教学包/02-能力与解释分支计划.json','R42':'MD-007-R42/教学包/02-未就绪计划与证据边界.json'}
first=[{'method':rid,'path':str((ROOT/'02-研究/方法深化执行'/rel).relative_to(ROOT)),'sha256':SHA(ROOT/'02-研究/方法深化执行'/rel),'use':'read_only_context_of_pending_fidelity_corrections_not_validated_dependency','status':'pending_root_coordinated_revision'}for rid,rel in FIRST.items()]
base13={'schema':'R13-fixed-lesson-1','binding':CONTEXT,'first_batch_status_reference':first,'provenance':'constructed_teaching_not_field_observation','population':{'target_population_known':False,'participants':None,'anthropometric_parameters':None,'experience_groups':['novice_hypothesis','experienced_hypothesis']},'tasks':[{'id':'HF-T01','phase':'normal_monitoring','action':'识别当前作业状态','information':['state','measurement_freshness'],'physical_demands':'unknown','cognitive_demands':'监视与状态解释，实际负荷未知'},{'id':'HF-T02','phase':'abnormal_takeover','action':'识别陈旧信息并请求抑制','information':['measurement_freshness','validity','stop_request_ack'],'physical_demands':'unknown','cognitive_demands':'从监视切换为异常判断，能力与时限未知'},{'id':'HF-T03','phase':'abnormal_takeover','action':'核对停止状态与恢复前提','information':['actual_stop','residual_energy','reauthorization'],'physical_demands':'unknown','cognitive_demands':'区分请求与实际状态，实际表现未知'},{'id':'HF-T04','phase':'maintenance','action':'清理与更换后交接','information':['isolation_status','maintenance_scope','reauthorization'],'physical_demands':'姿态、力、可达性均未知','cognitive_demands':'维护责任与交接，实际负荷未知'}],'states':[{'id':'S-CURRENT','semantic':'current_information'},{'id':'S-STALE','semantic':'stale_information'}],'representations':{'A':{'S-CURRENT':'绿灯','S-STALE':'绿灯'},'B':{'S-CURRENT':'绿灯；当前记录','S-STALE':'绿灯；记录陈旧，状态待核'}} ,'records':[],'conclusion':'not_empirically_evaluated','engineering_validated':False}
TASK_EXPECT={x['id']:(x['phase'],x['action'],tuple(x['information']))for x in base13['tasks']}
def check13(d):
 if d['binding']!=CONTEXT:raise ValueError('context_binding_changed')
 if d['provenance']!='constructed_teaching_not_field_observation':raise ValueError('provenance_changed')
 if d['population']!=base13['population']:raise ValueError('unsupported_population_claim')
 got={x['id']:(x['phase'],x['action'],tuple(x['information']))for x in d['tasks']}
 if got!=TASK_EXPECT or d['tasks']!=base13['tasks'] or len(d['tasks'])!=len(TASK_EXPECT):raise ValueError('task_or_information_mapping_changed')
 if d['states']!=base13['states']:raise ValueError('fixed_state_semantics_changed')
 if not isinstance(d['representations'],dict)or set(d['representations'])!={'A','B'}:raise ValueError('representation_variant_coverage_changed')
 if any(set(x)!= {'S-CURRENT','S-STALE'}for x in d['representations'].values()):raise ValueError('state_representation_missing')
 if any(type(v)is not str or not v.strip()for m in d['representations'].values()for v in m.values()):raise ValueError('blank_or_nontext_representation')
 if d['records']or d['conclusion']!='not_empirically_evaluated'or d['engineering_validated']:raise ValueError('fabricated_user_or_engineering_result')
 comparisons=[]
 for variant,r in d['representations'].items():
  collision=len(set(r.values()))<len(r);comparisons.append({'variant':variant,'representation_collision':collision,'can_distinguish_declared_states_by_encoding':not collision,'human_understanding':'unknown','workload':'unknown','reaction_time':None})
 return {'method':'R13','state':'research_design_only','tasks':d['tasks'],'representation_analysis':comparisons,'measured_user_outcomes':[],'target_population_known':False,'research_questions':['目标角色能否理解时效标记','异常时能否区分请求与实际停止','维护姿态/力/可达性与职责是什么'],'not_claimed':['B更易用','新手反应更快','设备更安全'],'pending':['现场人群与任务记录','实际负荷与姿态数据','角色资格及参与同意','专业/用户复核']}
out13=check13(base13);save('R13','01-构造任务与信息输入.json',base13);save('R13','02-表征区分实际分析.json',out13)

rows=[]
for name,value in [('normal',None),('empty-variants',{}),('only-B',{'B':base13['representations']['B']}),('only-A',{'A':base13['representations']['A']})]:
 q=copy.deepcopy(base13)
 if value is not None:q['representations']=value
 try:o=check13(q);accepted=True
 except ValueError as e:o={'error':str(e)};accepted=False
 assert accepted==(value is None)
 rows.append({'name':name,'accepted':accepted,'expected_accept':value is None,'pass':True})
 save('R13','检查/'+name+'-输入.json',q);save('R13','检查/'+name+'-输出.json',o)
save('R13','04-修订实际检查.json',{'cases':rows,'passed':4,'scope':'variant identity and coverage only; encoding distinction not human usability'})
print('R13 four revision checks passed; not usability evidence')

original=[('normal',lambda q:None,True),('missing-task',lambda q:q['tasks'].pop(1),False),('production',lambda q:q.update(provenance='production_user_study'),False),('invent-body',lambda q:q['population'].update(anthropometric_parameters={'reach_mm':700}),False),('claim-usability',lambda q:q.update(conclusion='B_has_better_usability'),False),('missing-state',lambda q:q['representations']['B'].pop('S-STALE'),False),('change-info',lambda q:q['tasks'][0].update(information=['actual_stop']),False)]
for name,mut,expected_accept in original:
 q=copy.deepcopy(base13);mut(q)
 try:o=check13(q);accepted=True
 except ValueError as e:o={'error':str(e)};accepted=False
 assert accepted==expected_accept
 rows.append({'name':'replay-'+name,'accepted':accepted,'expected_accept':expected_accept,'pass':True})
 save('R13','检查/replay-'+name+'-输入.json',q);save('R13','检查/replay-'+name+'-输出.json',o)
save('R13','04-修订实际检查.json',{'cases':rows,'passed':11,'scope':'fixed original7 plus4 variant checks; not human usability validation'})

q=copy.deepcopy(base13);q['representations']['B']['S-STALE']=''
try:check13(q);raise AssertionError('empty representation accepted')
except ValueError as e:save('R13','05-空串修订检查.json',{'input':q,'rejected':True,'reason':str(e)})
