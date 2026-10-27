from pathlib import Path
import json,copy
P=Path(__file__).resolve().parent
def route(d):
 if d.get('object_hard_to_change')is not True:return {'status':'unknown','reason':'selected rule requires object difficult to change'}
 if d['classification']not in ['incomplete','harmful','insufficient','unknown']:raise ValueError('classification')
 if d['classification']!='incomplete':return {'status':'not_applicable_to_selected_1.1.1','rule':'1.1.1','reason':'only missing-element synthesis subset implemented'}
 if any(d.get(k)is None for k in ['can_introduce_substance','can_introduce_field']):return {'status':'unknown','rule':'1.1.1','reason':'introduction constraints not known'}
 if not all(type(d[k])is bool for k in ['can_introduce_substance','can_introduce_field']):raise ValueError('explicit booleans required')
 if not d['can_introduce_substance']or not d['can_introduce_field']:return {'status':'blocked_by_selected_rule_precondition','rule':'1.1.1','next':'inspect actual restrictions; do not invent alternate standard text'}
 required={'S1','S2','F'};missing=required-set(d['elements'])
 if not missing:return {'status':'model_not_incomplete','rule':'1.1.1'}
 return {'status':'missing_element_research_prompt','rule':'1.1.1','missing':sorted(missing),'action':'identify candidate missing roles and mechanism, not automatically select hardware','engineering_validated':False}
base={'object_hard_to_change':True,'id':'R25-SUFIELD-TEACH-001','classification':'incomplete','elements':{'S1':'object whose state is to change'},'can_introduce_substance':True,'can_introduce_field':True,'origin':'independent constructed abstract exercise; not tapping robot'}
cases=[]
def add(n,d,expected):
 r=route(d);assert r['status']==expected;cases.append({'name':n,'input':d,'actual':r,'passed':True})
add('正常构造缺失角色',base,'missing_element_research_prompt')
x=copy.deepcopy(base);x['can_introduce_substance']=None;add('缺限制资料',x,'unknown')
x=copy.deepcopy(base);x['classification']='harmful';add('有害作用不套补全',x,'not_applicable_to_selected_1.1.1')
x=copy.deepcopy(base);x['elements'].update(S2='tool',F='mechanical interaction');add('完整模型边界',x,'model_not_incomplete')
x=copy.deepcopy(base);x['can_introduce_field']=False;add('禁止增场冲突',x,'blocked_by_selected_rule_precondition')
x=copy.deepcopy(base);x['id']='TAP-RESEARCH-UNKNOWN';x['elements']={'S1':'tree local tissue','S2':'working tool','F':'mechanical action'};x['classification']='unknown';x['can_introduce_substance']=None;x['can_introduce_field']=None;add('割胶不能虚称缺物场',x,'not_applicable_to_selected_1.1.1')
x=copy.deepcopy(base);x['id']='HEATING-TEACH-001';x['elements']={'S1':'dry inert test block','S2':'resistive heater'};add('另一情境缺能量场角色',x,'missing_element_research_prompt')
(P/'教学包/01-规则门禁实际检查.json').write_text(json.dumps({'cases':cases,'count':len(cases),'scope':'selected1.1.1 preconditions, not all76 standards'},ensure_ascii=False,indent=2)+'\n')
(P/'教学包/02-变换与机制研究.json').write_text(json.dumps({'before':base,'after_roles':{'S1':'same target','S2':'unknown candidate carrier','F':'unknown interaction field'},'not_a_solution':'role completion is neither actual mechanism nor sufficient useful interaction','prohibited_change_checks':['target biological state','contamination','new energy hazard','existing useful contact'],'tapping_status':'already two substances plus mechanical action in declared model; insufficiency/harm unknown, not diagnosed incomplete','handoff':'obtain actual action diagram/evidence before selecting any other standard'},ensure_ascii=False,indent=2)+'\n')
print(len(cases),'passed')
