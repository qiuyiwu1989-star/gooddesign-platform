# -*- coding: utf-8 -*-
"""Bounded technical-contradiction modeling; no complete matrix acquired, no lookup executed."""
from pathlib import Path
import copy,hashlib,json
B=Path(__file__).resolve().parent;P=B/'教学包';SP=B.parent/'MD-001-R48-v0.1.1/教学包/00-共享教学输入-v0.1.0.json';SHA='c9d262d505656bcaf6c76edee99e3615440f5e2d1c6ef4067e9c1b15a2ddcd70';assert hashlib.sha256(SP.read_bytes()).hexdigest()==SHA
BIND={'problem_id':'TAP-TEACH-001','problem_version':'0.1.0','sha256':SHA,'use':'analogical_contact_fixture_not_target_evidence'}
CONDITION={'id':'COND-PROXY-A','configuration':'CONTACT-PROXY-A','material':None,'geometry':None,'environment':None,'status':'assumed_common_condition_not_measured'}
PARAMS={'ACT-FORCE':{'quantity':'normal_force','unit':'N','role':'changed_action_parameter','direction':'increase','measured_value':None},'P-SLIP':{'quantity':'relative_slip_magnitude','unit':'mm','role':'desired_improvement','direction':'decrease','measured_value':None},'P-MARK':{'quantity':'indentation_depth','unit':'mm','role':'unwanted_worsening','direction':'increase','measured_value':None}}
data={'binding':BIND,'origin':'authored_conditional_contact_model','condition':CONDITION,'native_parameters':PARAMS,'IF':{'action':'increase_normal_force','parameter':'ACT-FORCE','condition_id':'COND-PROXY-A'},'THEN':{'parameter':'P-SLIP','condition_id':'COND-PROXY-A'},'BUT':{'parameter':'P-MARK','condition_id':'COND-PROXY-A'},'causal_relation_status':'teaching_hypothesis_not_measured','parameter_mapping':{'status':'unresolved','search_labels':['减少相对滑移／维持作用位置','减少接触损伤／变形副作用'],'official_parameter_ids':[],'note':'these are platform search phrases, not verified parameters in any named matrix'},'matrix':{'version':None,'authorized_complete_content_acquired':False,'lookup_performed':False,'cell':None,'principle_hits':[]},'customer_approved':False,'engineering_validated':False}
def save(n,o):(P/n).write_text(json.dumps(o,ensure_ascii=False,indent=2))
def check(d):
 if d.get('binding')!=BIND or d.get('origin')!='authored_conditional_contact_model':raise ValueError('context_or_provenance_changed')
 if d.get('condition')!=CONDITION or d.get('native_parameters')!=PARAMS:raise ValueError('native_quantity_unit_direction_or_unknown_changed')
 if d.get('causal_relation_status')!='teaching_hypothesis_not_measured'or d.get('customer_approved')is not False or d.get('engineering_validated')is not False:raise ValueError('relation_or_approval_promoted')
 for key,pid in [('IF','ACT-FORCE'),('THEN','P-SLIP'),('BUT','P-MARK')]:
  z=d.get(key,{})
  if z.get('parameter')!=pid or z.get('condition_id')!=CONDITION['id']:raise ValueError('contradiction_role_or_condition_mismatch')
 if d['IF'].get('action')!='increase_normal_force':raise ValueError('action_changed_without_new_model')
 if d.get('parameter_mapping')!=data['parameter_mapping']:raise ValueError('unverified_mapping_resolved_or_relabelled')
 if d.get('matrix')!={'version':None,'authorized_complete_content_acquired':False,'lookup_performed':False,'cell':None,'principle_hits':[]}:raise ValueError('matrix_lookup_or_hit_not_supported')
 return {'binding':BIND,'scenario':'conditional contact proxy','model':'IF increase assumed normal force, THEN assumed slip decrease, BUT assumed indentation increase','native_parameter_ledger':PARAMS,'same_condition':'declared common label only; material/geometry/environment remain unknown','parameter_mapping':'unresolved_no_verified_official_ids','lookup_status':'not_performed_missing_complete_versioned_matrix','principle_hits':[],'source_cell':None,'has_solution_claim':False,'engineering_candidates':[],'next_tasks':['核真实作用关系与同工况资料','固定矩阵版本、参数定义和可用权限','比较多种参数映射并保留歧义','实际查表才记录单元格、原理及机制转译'],'completion_scope':'problem_model_and_mapping_gap_only_not_complete_contradiction_matrix_method'}
save('01-矛盾句与原量纲输入.json',data);out=check(data);save('02-建模结果与未查表状态.json',out)
save('03-提议与查表结果分开.json',{'binding':BIND,'matrix_derived_principles':[],'host_ideation':[{'proposal':'研究接触作用分配或可逆接触方式','source':'original_platform_ideation_not_matrix_hit','not_claimed':'未给原理编号，未证明能解决滑移或损伤'}],'rejected_shortcuts':['没有矩阵却填原理编号','把映射猜测当正式参数','把空命中列表当真实单元格为空或无解'],'required_lookup_log':['matrix version and actual cell','original parameter definitions and mapping reasons','read/lookup evidence','principle identity and meaning','mechanism proposal and secondary problems']})
cases=[]
def probe(n,k,mut,expected):
 a=copy.deepcopy(data);mut(a)
 try:o=check(a);r='accepted'
 except ValueError as e:o={'error':str(e)};r='rejected'
 assert r==expected,(n,r);cases.append({'name':n,'class':k,'input':a,'expected':expected,'actual':r,'output':o})
probe('normal-model-only','正常',lambda x:None,'accepted')
probe('missing-IF','缺材料',lambda x:x.pop('IF'),'rejected')
probe('pretend-matrix-query','不适用',lambda x:x['matrix'].update(lookup_performed=True),'rejected')
probe('zero-is-not-unknown','边界',lambda x:x['native_parameters']['P-SLIP'].update(measured_value=0),'rejected')
probe('mixed-conditions','冲突',lambda x:x['BUT'].update(condition_id='OTHER'),'rejected')
probe('wrong-unit','冲突',lambda x:x['native_parameters']['P-SLIP'].update(unit='N'),'rejected')
probe('mapping-ID-invented','缺材料',lambda x:x['parameter_mapping'].update(official_parameter_ids=[1,2]),'rejected')
probe('principle-hit-invented','不适用',lambda x:x['matrix'].update(principle_hits=[10]),'rejected')
probe('assumed-model-as-measured','边界',lambda x:x.update(causal_relation_status='measured'),'rejected')
probe('swap-improve-worsen','冲突',lambda x:x['THEN'].update(parameter='P-MARK'),'rejected')
save('04-实际检查结果.json',{'executed':True,'passed':len(cases),'checks':cases,'actual_matrix_queries':0,'actual_engineering_trials':0,'method_scope':'partial_modeling_no_claimed_matrix_completion'})
t={'scenario':'DOC-TC-TEACH-001','origin':'constructed_desktop','IF':'增加交接核对环节','THEN':'在假设模型中减少版本误发','BUT':'增加人工动作或等待','same_condition_evidence':'not_acquired','matrix_lookup_performed':False,'principle_hits':[],'next':'先核同流程/同资料量下的改善与代价，不凭句式确认矛盾或查表'};assert not t['matrix_lookup_performed']and t['principle_hits']==[];save('05-迁移桌面检查.json',t)
print(json.dumps({'method':'R22','tests':len(cases),'matrix_queries':0,'principle_hits':[],'completion':'partial_modeling'},ensure_ascii=False))
