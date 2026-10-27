# -*- coding: utf-8 -*-
from pathlib import Path
import json,copy,math
D=Path(__file__).resolve().parent;P=D/'教学包';P.mkdir(exist_ok=True)
def put(n,x):(P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2))
base={'origin':'constructed_gate_advice_not_organizational_authorization','gate':'G-RESEARCH-001','hard_safety':'unknown','business_case':'promising_hypothesis','evidence_state':'incomplete','scope_requested':'physical_prototype','resource_proposal':{'unit':'synthetic_person_hour_not_actual_budget','cap':24,'owner_role':'research_lead_unassigned','review_trigger':'before any physical actuation or new evidence'},'actual_gatekeepers':[],'actual_authorization':False,'score_override':False}
def check(i):
 if i['origin']!=base['origin']or i['gate']!=base['gate']or i['actual_gatekeepers']or i['actual_authorization']or i['score_override']:raise ValueError('false_authorization_or_score_waiver')
 r=i['resource_proposal']
 if r!=base['resource_proposal']:raise ValueError('unbound_resources_owner_or_review')
 if i['hard_safety']not in['unknown','fail_in_fixture','pass_in_fixture']or i['evidence_state']not in['incomplete','revisable','sufficient_in_fixture']or i['business_case']not in['promising_hypothesis','no_value_in_fixture']:raise ValueError('state_identity')
 if i['scope_requested']not in['physical_prototype','paper_research']:raise ValueError('scope_identity')
 if i['business_case']=='no_value_in_fixture':advice='Kill';reason='constructed value rationale absent; organizational decision still required'
 elif i['evidence_state']=='revisable'or i['hard_safety']=='fail_in_fixture':advice='Recycle';reason='return to revise task/model before new commitment'
 elif i['scope_requested']=='physical_prototype'and i['hard_safety']!='pass_in_fixture':advice='Hold';reason='unknown hard safety cannot be offset by forecast benefit'
 elif i['evidence_state']=='sufficient_in_fixture'and i['hard_safety']=='pass_in_fixture':advice='Go';reason='only within declared fixed fixture, not real authorization'
 else:advice='Hold';reason='incomplete research packet; may propose bounded paper work separately'
 return {'advisory_outcome':advice,'reason':reason,'proposed_resource_limit':r,'authorized_resource':None,'actual_gate_decision':None,'scope_permitted_by_this_script':None,'reviewer_needed':'cross_functional_authority_and_domain_review','not_a_safety_waiver':True}
put('01-关口证据与资源提议.json',base);put('02-建议与组织决定分离.json',check(base));cases=[]
def t(n,k,mut,expected):
 q=copy.deepcopy(base);mut(q)
 try:o=check(q);state=o['advisory_outcome']
 except(ValueError,KeyError,TypeError)as e:o={'error':str(e)};state='rejected'
 cases.append({'name':n,'class':k,'input':q,'output':o,'actual':state,'expected':expected,'pass':state==expected})
t('normal_unknown_hazard','正常',lambda x:None,'Hold');t('revisable_packet','缺材料',lambda x:x.update(evidence_state='revisable'),'Recycle');t('no_constructed_value','边界',lambda x:x.update(business_case='no_value_in_fixture'),'Kill');t('all_fixture_assumptions_met','边界',lambda x:x.update(hard_safety='pass_in_fixture',evidence_state='sufficient_in_fixture'),'Go');t('profit_cannot_override_safety','冲突',lambda x:x.update(score_override=True),'rejected');t('actual_authorization','不适用',lambda x:x.update(actual_authorization=True),'rejected');t('erase_owner','缺材料',lambda x:x['resource_proposal'].update(owner_role=''),'rejected');t('physical_scope_drift','冲突',lambda x:x.update(scope_requested='market_release'),'rejected')
assert all(x['pass']for x in cases);put('03-实际检查.json',cases)
put('04-迁移桌面检查.json',{'context':'publish document-based application','gate_evidence':['source permissions','version binding','release scope'],'hard_unknown':'publication authority','advice':'Hold release; propose bounded internal paper review separately','actual_permission':False,'actual_scope':'desktop analogy only'})
print('R06:8 fixed advisory checks passed')
