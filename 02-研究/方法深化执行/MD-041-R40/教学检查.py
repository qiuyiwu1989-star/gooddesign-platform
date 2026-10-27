# -*- coding: utf-8 -*-
from pathlib import Path
import copy,json
D=Path(__file__).resolve().parent;P=D/'教学包';P.mkdir(exist_ok=True)
def put(n,x):(P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2))
base={'origin':'constructed_research_architecture_not_actual_machine','configuration':'TAP-FMEA-DRAFT-001','phase':'abnormal_motion_inhibition','scale_reference':{'document':'GSFC-HDBK-8004','revision':'Baseline2024-08-20','locator':'Table1 PDFp23','applicability_to_target':'not_approved','transfer_numeric_ratings':False},'components':[{'id':'S1','power':'PWR-A'},{'id':'S2','power':'PWR-A'},{'id':'CTRL','power':'PWR-A'}],'failure_chain':{'id':'FM1','function':'provide timely boundary-related observation','mode':'stale output treated as current','mechanism':'validity gate fails to discriminate stale sample','causes':['clock mismatch hypothesis','shared supply disturbance hypothesis'],'local_effect':'invalid observation persists','higher_effect':'motion inhibition may not be requested','end_effect':'uncontrolled contact hypothesis; consequence not assessed'},'controls':[{'id':'CT1','kind':'staleness gate','state':'planned','effectiveness_evidence':[]},{'id':'CT2','kind':'second observation channel','state':'planned','effectiveness_evidence':[]}],'claimed_independent_redundancy':False,'single_point_review':'shared PWR-A requires assessment; no complete fault model','ratings':{'severity':None,'occurrence':None,'detection_prevention':None},'residual_risk':None,'actions':[{'id':'A1','control':'CT1','owner_role':'controls_research_role','task':'define clock/age and fault-injection study','completion':'not_executed'},{'id':'A2','control':'CT2','owner_role':'system_architecture_role','task':'investigate supply independence/common cause and latent faults','completion':'not_executed'}],'customer_approved':False,'engineering_validated':False}
def check(i):
 if i['origin']!=base['origin']or i['configuration']!=base['configuration']or i['phase']!=base['phase']:raise ValueError('configuration_or_scope')
 if i['scale_reference']!=base['scale_reference']:raise ValueError('unapproved_scale_transfer')
 if i['failure_chain']!=base['failure_chain']or i['components']!=base['components']:raise ValueError('failure_chain_or_power_topology_changed')
 if i['customer_approved']or i['engineering_validated']or i['residual_risk']is not None or any(v is not None for v in i['ratings'].values())or set(i['ratings'])!=set(base['ratings']):raise ValueError('unearned_rating_or_residual_claim')
 if i['claimed_independent_redundancy']:raise ValueError('shared_power_not_independent')
 if i['controls']!=base['controls']:raise ValueError('planned_control_has_no_effectiveness_evidence')
 ids={c['id']for c in i['controls']}
 if len(ids)!=len(i['controls'])or len(i['actions'])!=2 or any(a['control']not in ids or not a['owner_role']or a['completion']!='not_executed'for a in i['actions']):raise ValueError('action_reference_or_execution_claim')
 groups={}
 for c in i['components']:groups.setdefault(c['power'],[]).append(c['id'])
 return {'failure_mode':i['failure_chain']['id'],'common_cause_groups':groups,'independent_backup_demonstrated':False,'single_point_failure_status':'requires_system_model_not_proved_away','control_effectiveness':'unknown','ratings':i['ratings'],'residual_risk':None,'action_queue':i['actions'],'release_decision':None,'engineering_validated':False,'reason':'configuration-bound hypotheses, no control evidence or applicable calibrated rating basis'}
put('01-配置失效链与控制输入.json',base);put('02-共因与行动输出.json',check(base));cases=[]
def t(name,kind,mut,expected):
 q=copy.deepcopy(base);mut(q)
 try:o=check(q);state='accepted'
 except(ValueError,KeyError,TypeError)as e:o={'error':str(e)};state='rejected'
 cases.append({'name':name,'class':kind,'input':q,'output':o,'actual':state,'expected':expected,'pass':state==expected})
t('normal','正常',lambda x:None,'accepted');t('shared_supply_as_independent','冲突',lambda x:x.update(claimed_independent_redundancy=True),'rejected');t('proposed_control_as_proven','缺材料',lambda x:x['controls'][0].update(state='effective'),'rejected');t('residual_zero_without_evidence','边界',lambda x:x.update(residual_risk=0),'rejected');t('cross_industry_scale','不适用',lambda x:x['scale_reference'].update(document='automotive_1to10'),'rejected');t('missing_action_reference','缺材料',lambda x:x['actions'][0].update(control='MISSING'),'rejected');t('fake_lower_detection_score','冲突',lambda x:x['ratings'].update(detection_prevention=1),'rejected');t('changed_configuration','不适用',lambda x:x.update(configuration='PRODUCTION-V2'),'rejected')
assert all(x['pass']for x in cases);put('03-实际检查.json',cases)
put('04-迁移桌面检查.json',{'context':'document archive reliability','failure_mode':'backup unavailable when primary storage fails','common_cause':'both copies on same physical disk','actual_desk_check':'two directory names share one declared device identity; distinct names do not imply independence','ratings':None,'actions':['identify failure domains','exercise restore separately from checking backup exists'],'real_restore_test':False})
print('R40:8 checks passed')
