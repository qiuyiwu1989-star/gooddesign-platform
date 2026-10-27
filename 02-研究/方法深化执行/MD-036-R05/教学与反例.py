# -*- coding: utf-8 -*-
from pathlib import Path
import json,copy,math
P=Path(__file__).parent;B=P.parent;D={'R05':P,'R47':B/'MD-037-R47'}
def put(r,n,v):
 p=D[r]/'教学包'/n;p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2))
base05={'id':'V-IF-TEACH-001','provenance':'independent_constructed_interface_not_robot','version':'0.1.0','customer_approved':False,'mechanical':{'unit':'mm','positive':'outward','frame':'fixture-frame'},'software':{'unit':'mm','positive':'inward','frame':'fixture-frame'},'transform':{'scale':-1,'offset':0,'verified_status':'declared_teaching_relation_only'},'sample':{'value':2,'timestamp_ms':80,'now_ms':100,'clock':'same_constructed_monotonic_clock','age_limit_ms':30},'command':{'software_value':-1,'controller_owner':'motion_controller','other_writers':[]},'timeout':{'limit_ms':30,'response':'inhibit_new_motion_and_request_stop','actual_stop_confirmed':False,'safe_state':'unconfirmed_pending_actual_motion_and_residual_energy_observation'},'trace':[{'left':'L1-use-context-intent','right':'T1-context-observation','evidence':'planned_not_executed'},{'left':'L2-system-interface','right':'T2-sign-unit-time-authority-integration','evidence':'constructed_check_only'},{'left':'L3-domain-coordinate','right':'T3-domain-unit-check','evidence':'declared_local_check_not_field'}],'engineering_validated':False}
EXPECT=copy.deepcopy(base05)
def check05(x):
 if x['provenance']!=EXPECT['provenance']or x['customer_approved']or x['engineering_validated']:raise ValueError('scope_or_approval')
 if x['mechanical']!=EXPECT['mechanical']or x['software']!=EXPECT['software']:raise ValueError('frame_unit_or_direction_changed')
 tr=x['transform']
 if tr!=EXPECT['transform']:raise ValueError('coordinate_transform_conflict')
 if x['trace']!=EXPECT['trace']:raise ValueError('left_right_trace_or_evidence_changed')
 s=x['sample'];c=x['command'];t=x['timeout']
 if s['clock']!=EXPECT['sample']['clock']:raise ValueError('unsynchronized_clock')
 if any(type(s[k])not in(int,float)or not math.isfinite(s[k])for k in ['value','timestamp_ms','now_ms','age_limit_ms']):raise ValueError('invalid_time_or_value')
 if s['age_limit_ms']!=30 or t!=EXPECT['timeout']:raise ValueError('fixed_timeout_or_safe_state_claim_changed')
 if s['now_ms']<s['timestamp_ms']:raise ValueError('future_timestamp')
 if c['controller_owner']!='motion_controller'or c['other_writers']:raise ValueError('multiple_or_unknown_control_authority')
 age=s['now_ms']-s['timestamp_ms'];stale=age>=s['age_limit_ms']
 return {'left_right_pairs':x['trace'],'age_ms':age,'stale':stale,'measured_position_software_mm':-s['value'],'command_mechanical_mm':-c['software_value'],'decision':'request_inhibit_stop_actual_state_unknown'if stale else'interface_fixture_consistent_only','engineering_validated':False,'safe_state_confirmed':False,'not_a_real_test':True}
base47={'id':'SBCE-GRID-TEACH-001','provenance':'synthetic_domains_not_customer_budgets','version':'0.1.0','units':{'mass':'kg','power':'W','coupling':'kg*W'},'mass_grid':[1,2,3],'power_grid':[10,20,30],'constraints':[{'id':'E-MECH','owner':'mechanical','predicate':'mass<=2','status':'constructed_assumption','source':'teaching-definition-v0.1.0'},{'id':'E-ELEC','owner':'electrical','predicate':'power<=20','status':'constructed_assumption','source':'teaching-definition-v0.1.0'},{'id':'E-IF','owner':'interface','predicate':'mass*power<=30','status':'constructed_assumption','source':'teaching-definition-v0.1.0'}],'real_latex_boundary':'unknown','customer_approved':False,'commitment':False}
EX47=copy.deepcopy(base47)
def check47(x,limit=30):
 if x['provenance']!=EX47['provenance']or x['customer_approved']or x['commitment']:raise ValueError('unsupported_commitment')
 for k in ['units','mass_grid','power_grid','constraints','real_latex_boundary']:
  if x[k]!=EX47[k]:raise ValueError('domain_or_evidence_basis_changed')
 if limit not in[30,40]:raise ValueError('unversioned_interface_change')
 rows=[]
 for m in x['mass_grid']:
  for p in x['power_grid']:
   reasons=[]
   if m>2:reasons.append('E-MECH')
   if p>20:reasons.append('E-ELEC')
   if m*p>limit:reasons.append('E-IF')
   rows.append({'mass_kg':m,'power_W':p,'constructed_response_index':2*m+p/10,'index_not_real_robot_performance':True,'excluded_by':reasons,'status':'excluded_within_teaching_model'if reasons else'conditional_research','unresolved':['real_latex_boundary'],'engineering_pass':False})
 return {'version':'0.1.0'if limit==30 else'0.1.1-interface-change','interface_bound':limit,'rows':rows,'intersection':[[r['mass_kg'],r['power_W']]for r in rows if not r['excluded_by']],'commitment':False,'why_not_commit':'unknown target field and no engineering evidence','continuous_feasibility_claim':False}
for rid,base,fn in [('R05',base05,check05),('R47',base47,check47)]:put(rid,'01-固定构造输入.json',base);put(rid,'02-中间核查与输出.json',fn(copy.deepcopy(base)))
a=check47(base47);z=check47(base47,40);old={tuple(x)for x in a['intersection']};new={tuple(x)for x in z['intersection']};assert old=={(1,10),(1,20),(2,10)}and new-old=={(2,20)}
put('R47','03-接口变更与重新打开.json',{'prior_version':'0.1.0','new_version':'0.1.1-interface-change','reason':'independent constructed interface bound changes30to40; not actual engineering change','old_history_preserved':a,'new_evaluation':z,'reopened_points':[list(x)for x in sorted(new-old)],'not_automatically_approved':True})
# The wrong transform anomaly is an actual software-fixture computation, not a device trial.
put('R05','03-构造集成异常记录.json',{'id':'ANOM-TEACH-01','kind':'executed_dictionary_arithmetic_not_physical_trial','local_unit_checks':'both independent domains can regard their own positive direction as internally consistent','sample_mechanical_mm':2,'expected_software_mm':-2,'faulty_identity_transform_software_mm':2,'observed_fixture_error_mm':4,'cause_scope':'constructed mapping conflict; no actual client incident','return_to':'L2-system-interface transform revision','physical_followup':'plan unloaded/simulated signed displacement and stop-state observation; not executed'})
attacks={'R05':[('missing-time',lambda x:x['sample'].pop('timestamp_ms')),('unit-conflict',lambda x:x['software'].update(unit='m')),('sign-conflict',lambda x:x['transform'].update(scale=1)),('double-writer',lambda x:x['command'].update(other_writers=['maintenance_controller'])),('fake-safe',lambda x:x['timeout'].update(actual_stop_confirmed=True)),('missing-left-right',lambda x:x['trace'].pop())],'R47':[('names-only',lambda x:x.update(mass_grid=['A','B'])),('delete-evidence',lambda x:x['constraints'].pop()),('unit-drift',lambda x:x['units'].update(mass='g')),('invent-commitment',lambda x:x.update(commitment=True)),('unknown-as-pass',lambda x:x.update(real_latex_boundary='pass')),('erase-domain',lambda x:x.update(power_grid=[]))]}
for r,base,fn in [('R05',base05,check05),('R47',base47,check47)]:
 rows=[{'name':'normal','pass':True,'actual':'accepted_bounded'}]
 for name,mut in attacks[r]:
  q=copy.deepcopy(base);mut(q)
  try:out=fn(q);actual='accepted'
  except(ValueError,KeyError,TypeError)as e:out={'error':str(e)};actual='rejected'
  assert actual=='rejected',(r,name);rows.append({'name':name,'pass':True,'actual':actual});put(r,'探针-'+name+'.json',{'input':q,'output':out})
 if r=='R05':
  q=copy.deepcopy(base);q['sample']['now_ms']=110;out=fn(q);assert out['stale'];put(r,'04-超时等边界实际检查.json',out);rows.append({'name':'age-equals-limit','pass':True,'actual':'stale_no_safe_confirmation'})
 else:rows.append({'name':'interface-reopen','pass':True,'actual':'2kg20W reopened conditional only'})
 put(r,'05-实际检查汇总.json',{'cases':rows,'executed':len(rows),'passed':len(rows),'scope':'fixed teaching only, no actual field or user trials'})
# Different context means changed model; only structural transfer, no invented customers.
put('R05','06-另一情境迁移.json',{'context':'document revision preview','interface':'preview revision vs saved revision, request ack vs persistence observation','different_conditions':['no mechanical frame','persistence clock and authority still required'],'actual_desk_check':{'preview_rev':2,'saved_rev':1,'equal':2==1},'result':'not_saved_revision_not_equal_preview','field_validation':False})
put('R47','06-另一情境迁移.json',{'context':'document delivery formats','producer_set':['PDF','HTML'],'reader_set':['PDF','DOCX'],'actual_intersection':sorted(set(['PDF','HTML'])&set(['PDF','DOCX'])),'remaining_unknown':'actual readability and access permission','result':'PDF common declared format not guaranteed readability','field_validation':False})
print('16 fixed checks passed; teaching only')
