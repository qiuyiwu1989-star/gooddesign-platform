# -*- coding: utf-8 -*-
"""Declared model readiness/routing fixture; does not invent contradictions or solve TRIZ."""
from pathlib import Path
import copy,hashlib,json
B=Path(__file__).resolve().parent;P=B/'教学包';SP=B.parent/'MD-001-R48-v0.1.1/教学包/00-共享教学输入-v0.1.0.json';SHA='c9d262d505656bcaf6c76edee99e3615440f5e2d1c6ef4067e9c1b15a2ddcd70';assert hashlib.sha256(SP.read_bytes()).hexdigest()==SHA
BIND={'problem_id':'TAP-TEACH-001','problem_version':'0.1.0','sha256':SHA,'scope':'constructed_context_only'}
base={'binding':BIND,'origin':'authored_problem_model_fixture','main_function':'在指定边界对目标施加受控作用','defect_or_goal':'需研究有用作用、残留和损伤的关系','technical_contradiction':None,'su_field':None,'tools_executed':[],'solution_principles':[],'numerical_route_score':None,'customer_approved':False,'engineering_validated':False}
tc={'IF':'在构造模型中提高压紧作用','THEN':{'parameter':'slip','direction':'decrease','condition':'COND-TEACH-A'},'BUT':{'parameter':'indentation','direction':'increase','condition':'COND-TEACH-A'},'condition':'COND-TEACH-A','status':'hypothetical_not_empirically_established'}
sf={'substances':['TOOL','TARGET'],'field':'mechanical_contact','problem_tag':'insufficient_useful_or_harmful_action','status':'declared_model_not_validated'}
def put(n,o):(P/n).write_text(json.dumps(o,ensure_ascii=False,indent=2))
def route(d):
 if d.get('binding')!=BIND or d.get('origin')!='authored_problem_model_fixture':raise ValueError('context_or_provenance_changed')
 if d.get('tools_executed')!=[]or d.get('solution_principles')!=[]or d.get('numerical_route_score')is not None or d.get('customer_approved')is not False or d.get('engineering_validated')is not False:raise ValueError('route_promoted_to_execution_or_validation')
 if not d.get('main_function')or not d.get('defect_or_goal'):return {'state':'return_to_problem_definition','suggested':['R48','R14'],'rejected_routes':[{'method':'R22','reason':'no contradiction established'},{'method':'R25','reason':'no action model established'}],'executed':[]}
 suggestions=[];rejected=[]
 t=d.get('technical_contradiction')
 if t:
  if any(type(t.get(k,{}).get('direction'))is not str or t[k]['direction']not in {'increase','decrease'} for k in ['THEN','BUT']):raise ValueError('technical_direction_enum_required')
  if t.get('status')!='hypothetical_not_empirically_established'or not t.get('IF')or any(not t.get(k,{}).get('parameter')or not t[k].get('direction')for k in ['THEN','BUT']):raise ValueError('technical_model_incomplete_or_promoted')
  if not t.get('condition')or any(t[k].get('condition')!=t['condition']for k in ['THEN','BUT']):raise ValueError('technical_model_conditions_mismatch')
  if t['THEN']['parameter']==t['BUT']['parameter']:rejected.append({'method':'R22','reason':'same property is not a two-parameter technical model; examine conditions and possible R23 model separately'})
  else:suggestions.append({'method':'R22','reason':'declared same-condition IF/THEN/BUT with distinct parameters','status':'research_model_only_matrix_version_still_required'})
 else:rejected.append({'method':'R22','reason':'no explicit IF/THEN/BUT; do not invent one to force a route'})
 s=d.get('su_field')
 if s:
  if s.get('status')!='declared_model_not_validated'or len(s.get('substances',[]))!=2 or len(set(s['substances']))!=2 or not s.get('field')or not s.get('problem_tag'):raise ValueError('su_field_model_incomplete')
  suggestions.append({'method':'R25','reason':'declared interacting substances, field and action defect','status':'research_model_only_specific_standard_prerequisite_unread'})
 else:rejected.append({'method':'R25','reason':'interaction model absent'})
 if not suggestions:suggestions.append({'method':'R27','reason':'function/goal known but mechanism/model unresolved; search functions/effects without fabricating contradiction','status':'research_search_only'})
 return {'state':'research_route_suggestions','suggested':suggestions,'rejected_routes':rejected,'executed':[],'automatic_solver':False,'numerical_score':None,'next_action':'human/Agent review problem representation and required source/input before invoking a specific tool'}
views=[]
for name,t,s in [('function_only',None,None),('technical_model',tc,None),('action_model',None,sf),('multiple_models',tc,sf)]:
 d=copy.deepcopy(base);d.update(technical_contradiction=t,su_field=s);views.append({'view':name,'input':d,'output':route(d)})
put('01-同题多种模型输入.json',{'binding':BIND,'views':views});put('02-实际路由与拒绝理由.json',{'model_routes':[{x['view']:x['output']}for x in views],'not_new_algorithms':['no contradiction-matrix lookup','no ARIZ execution','no scientific-effect feasibility validation'],'tool_family_note':'tools depend on problem model; different representations can yield several research paths, no universal ranking'})
put('03-交接前所需材料.json',{'R22':['same configuration and conditions','native quantities and directions','parameter/matrix version and actual query evidence'],'R25':['actual interaction object and useful/harmful action','specific standard text and prerequisites'],'R27':['domain-neutral function','scale/media/condition constraints','source and transfer differences'],'unready_case':'缺主功能/关键缺陷则回R48/R14，不硬分TRIZ路线'})
checks=[]
def probe(n,k,mut,expected):
 d=copy.deepcopy(base);mut(d)
 try:o=route(d);a=o['state']
 except ValueError as e:o={'error':str(e)};a='rejected'
 assert a==expected,(n,a);checks.append({'name':n,'class':k,'input':d,'expected':expected,'actual':a,'output':o})
probe('normal-function-search','正常',lambda x:None,'research_route_suggestions')
probe('missing-main-function','缺材料',lambda x:x.update(main_function=None),'return_to_problem_definition')
probe('no-contradiction-forced','不适用',lambda x:None,'research_route_suggestions');assert checks[-1]['output']['suggested'][0]['method']=='R27'
probe('same-condition-model','正常',lambda x:x.update(technical_contradiction=tc),'research_route_suggestions')
probe('mixed-condition-contradiction','冲突',lambda x:x.update(technical_contradiction={**tc,'BUT':{**tc['BUT'],'condition':'OTHER'}}),'rejected')
probe('incomplete-action-model','缺材料',lambda x:x.update(su_field={**sf,'substances':['TOOL']}),'rejected')
probe('same-property-not-technical-pair','边界',lambda x:x.update(technical_contradiction={**tc,'BUT':{**tc['BUT'],'parameter':'slip'}}),'research_route_suggestions');assert all(v['method']!='R22'for v in checks[-1]['output']['suggested'])
probe('no-numerical-ranking','边界',lambda x:x.update(numerical_route_score=0.99),'rejected')
probe('no-pretend-principle-hit','不适用',lambda x:x.update(solution_principles=[1,10]),'rejected')
probe('no-tool-execution','冲突',lambda x:x.update(tools_executed=['ARIZ']),'rejected')
put('04-实际检查结果.json',{'executed':True,'passed':len(checks),'checks':checks,'real_TRIZ_tool_executions':0,'scope':'declared readiness/route consistency, not semantic problem diagnosis or technology solving'})
t={'scenario':'DOC-TRIZ-TEACH-001','origin':'constructed_desktop','function':'将正确版本传给接收者','unknown':'传递机制及失败模型未定','route':'先明确对象/功能/缺陷，必要时检索机制；没有证据不编速度与准确性矛盾','engineering_validated':False};assert '未定'in t['unknown'];put('05-迁移桌面检查.json',t)
print(json.dumps({'method':'R21','tests':len(checks),'model_views':len(views),'tools_executed':[]},ensure_ascii=False))
