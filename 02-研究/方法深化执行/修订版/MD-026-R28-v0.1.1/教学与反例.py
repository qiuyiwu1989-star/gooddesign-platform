# -*- coding: utf-8 -*-
"""Bounded independently constructed teaching fixtures, not full method engines."""
from pathlib import Path
import json,copy,hashlib
D=Path(__file__).parent;ROOT=D.parents[3];BASE=ROOT/'02-研究/方法深化执行'
DIRS={'R28':D,'R18':D.parent/'MD-028-R18-v0.1.1'}
def put(r,n,v):
 p=DIRS[r]/'教学包'/n;p.parent.mkdir(exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2));return p
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
shared=BASE/'MD-001-R48/教学包/00-共享教学输入-v0.1.0.json'
assert sha(shared)=='c9d262d505656bcaf6c76edee99e3615440f5e2d1c6ef4067e9c1b15a2ddcd70'
context={'path':str(shared.relative_to(ROOT)),'sha256':sha(shared),'problem_version':'0.1.0','identity':'research_hypotheses_only_not_requirements','customer_approved':False,'engineering_validated':False}
AR={'fixture':'ARIZ-LIMITED-01','context':context,'version':'0.1.0','source_version':'ARIZ-85V Spanish Foundation translation','implemented_scope':['mini_problem','conflict_pair','zone_time_resources','physical_contradiction_hypothesis','reformulation_record'],'system':['contact element','workpiece','release actuator'],'main_process':'maintain relative position during constructed work stage','technical_conflicts':[{'action':'increase contact load','useful':'resist relative slip','harmful':'release burden may increase'},{'action':'reduce contact load','useful':'facilitate release','harmful':'holding resistance may decrease'}],'selected_conflict':0,'operating_zone':'contact interface','operating_times':{'work':'holding','release':'disengagement'},'physical_contradiction':{'same_element':'contact element','property':'normal load','state_A':'high','condition_A':'work stage','state_B':'low','condition_B':'release stage','status':'hypothesis_not_proven'},'resources':[{'item':'actuator state','availability':'unknown'},{'item':'workpiece surface information','availability':'unknown'}],'IFR':'seek stable holding then release without added burdens; desired direction only','threshold':None,'solution_status':'unsolved','reformulation':{'parent_version':None,'reason':None,'prior_model_preserved':True}}
ARBASE=copy.deepcopy(AR)
def ar(i):
 if i.get('version')!='0.1.0':raise ValueError('teaching_version_changed')
 if i['context']!=context:raise ValueError('context')
 for k in ['source_version','implemented_scope','system','main_process','technical_conflicts','selected_conflict','operating_zone','operating_times','physical_contradiction','resources','IFR']:
  if i[k]!=ARBASE[k]:raise ValueError('frozen_problem_or_scope_changed')
 if i['threshold']is not None or i['solution_status']!='unsolved':raise ValueError('invented_solution_or_threshold')
 if not i['reformulation']['prior_model_preserved']:raise ValueError('lost_reformulation_history')
 return {'conflict_model':i['technical_conflicts'][i['selected_conflict']],'physical_contradiction':i['physical_contradiction'],'resource_unknowns':[x['item']for x in i['resources']if x['availability']=='unknown'],'proposed_direction':'separate holding and release conditions; investigate actuator feasibility','status':'unsolved','completed_full_ARIZ':False,'engineering_pass':False,'limitations':['no full nine-part execution','no standard-solution lookup claimed','no real holding or release experiment']}
TR={'fixture':'TESE-LIMITED-01','context':context,'version':'0.1.0','records':[{'year':2021,'operations':8,'unit':'count/task','condition':'same constructed dry cleaning task','provenance':'synthetic'},{'year':2022,'operations':6,'unit':'count/task','condition':'same constructed dry cleaning task','provenance':'synthetic'},{'year':2023,'operations':5,'unit':'count/task','condition':'same constructed dry cleaning task','provenance':'synthetic'}],'route':'selective automation hypothesis','counterevidence':'automation may add setup and fault recovery; those costs absent in these counts','maturity':None,'future_performance':None,'inevitable':False,'customer_target':None}
TRBASE=copy.deepcopy(TR)
def tr(i):
 if i['context']!=context:raise ValueError('context')
 if i['records']!=TRBASE['records']:raise ValueError('source_observation_or_comparability_changed')
 if i['inevitable']or i['maturity']is not None or i['future_performance']is not None or i['customer_target']is not None:raise ValueError('unsupported_prediction')
 if not i['counterevidence']:raise ValueError('counterevidence_omitted')
 vals=[x['operations']for x in i['records']]
 return {'observed_constructed_changes':[vals[j]-vals[j-1]for j in range(1,len(vals))],'net_change':vals[-1]-vals[0],'route':i['route'],'counterevidence':i['counterevidence'],'status':'hypothesis_only','future_performance':None,'maturity':None,'ranking':None,'next':'obtain comparable field history, maintenance and recovery exposure before route comparison','not_a_curve_fit':True}
BIO={'fixture':'BIO-TRANSFER-01','context':context,'version':'0.1.0','source':'Bohn and Federle 2004 PNAS DOI10.1073/pnas.0405885101','organism':'Nepenthes bicalcarata / Oecophylla smaragdina friction experiment','evidence_scope':'selected methods, wet/dry comparisons and attachment-structure distinction','mechanisms':[{'condition':'wet peristome','affected_structure':'soft adhesive pad','effect':'water-film attachment disruption'},{'condition':'anisotropic peristome topography','affected_structure':'claw','effect':'direction-dependent friction'}],'abstraction':'fluid film and surface geometry interact with contact structure; conditions matter','target':'explore cleanable contact interface in tapping research','differences':[{'variable':'fluid','nature':'aqueous wetting','target':'latex rheology and coagulation unknown'},{'variable':'contact','nature':'insect pad/claw','target':'tool/material pair unknown'},{'variable':'film stability','nature':'wet peristome','target':'field contamination and replenishment unknown'}],'engineering_gain':None,'verified_transfer':False,'test_plan':['characterize actual fluid and material pair','compare wet/dry and geometry controls under matched exposure','record maintenance and adverse contact effects'],'target_threshold':None}
BIOBASE=copy.deepcopy(BIO)
def bio(i):
 if i.get('version')!='0.1.0':raise ValueError('teaching_version_changed')
 if i['context']!=context:raise ValueError('context')
 for k in ['source','organism','evidence_scope','mechanisms','abstraction','target','differences']:
  if i[k]!=BIOBASE[k]:raise ValueError('natural_mechanism_or_transfer_mapping_changed')
 if i['engineering_gain']is not None or i['verified_transfer']or i['target_threshold']is not None:raise ValueError('unsupported_engineering_transfer')
 if not isinstance(i['test_plan'],list)or len(i['test_plan'])<3 or any(not isinstance(x,str)or not x.strip()for x in i['test_plan']):raise ValueError('missing_controls')
 return {'evidence_chain':['original biological experiment','condition-bound mechanism','domain-neutral abstraction','unverified target hypothesis'],'unresolved_transfer_variables':[x['variable']for x in i['differences']],'engineering_concept':'investigate condition-specific surface/interface strategy','performance_gain':None,'status':'requires_target_experiment','biological_observations_are_not_engineering_results':True}
FBS={'fixture':'FBS-LIMITED-01','context':context,'version':'0.1.0','source_scope':'author/publisher abstract only; no full situated eight-process reconstruction','F':'support stable holding in a constructed fixture','Be':{'quantity':'normal force','target':None,'unit':'N','customer_approved':False},'S':{'concept':'ideal linear spring','stiffness':10,'stiffness_unit':'N/mm','deflection':2,'deflection_unit':'mm','provenance':'independent synthetic teaching values'},'analysis_assumptions':['linear elastic range','quasi-static','no losses or geometry transformation'],'Bs_provenance':'analytical calculation, not measured','actual_measurement':None,'engineering_pass':False,'situated_worlds_implemented':False}
FBSBASE=copy.deepcopy(FBS)
def fbs(i):
 if i['context']!=context:raise ValueError('context')
 for k in ['source_scope','F','Be','S','analysis_assumptions','Bs_provenance','situated_worlds_implemented']:
  if i[k]!=FBSBASE[k]:raise ValueError('fixed_model_semantics_or_units_changed')
 if i['actual_measurement']is not None or i['engineering_pass']:raise ValueError('analysis_is_not_measurement_or_approval')
 bs=i['S']['stiffness']*i['S']['deflection']
 return {'F':i['F'],'Be':i['Be'],'S':i['S'],'Bs':{'value':bs,'unit':'N','basis':'k*x under stated ideal assumptions','type':'analytical_not_measured'},'comparison':'cannot_determine_compliance_target_unknown','reformulation_option':'obtain supported expected behaviour or revise model with recorded reason','engineering_pass':False,'full_situated_FBS':False}
FIX={'R28':(AR,ar),'R29':(TR,tr),'R18':(BIO,bio),'R49':(FBS,fbs)}
ATTACKS={
'R28':[('missing_resource',lambda x:x['resources'].pop()),('reverse_time_condition',lambda x:x['physical_contradiction'].update(condition_A='release stage')),('claim_solution',lambda x:x.update(solution_status='solved')),('invent_target',lambda x:x.update(threshold=0.5)),('lose_prior_model',lambda x:x['reformulation'].update(prior_model_preserved=False)),('claim_full_ARIZ',lambda x:x['implemented_scope'].append('full_ARIZ_certified'))],
'R29':[('unit_changed',lambda x:x['records'][1].update(unit='seconds')),('condition_changed',lambda x:x['records'][1].update(condition='different wet task')),('invent_maturity',lambda x:x.update(maturity=0.8)),('inevitable_future',lambda x:x.update(inevitable=True)),('omit_counterevidence',lambda x:x.update(counterevidence='')),('invent_customer_target',lambda x:x.update(customer_target=2))],
'R18':[('wrong_contact_structure',lambda x:x['mechanisms'][0].update(affected_structure='claw')),('dry_generalization',lambda x:x['mechanisms'][0].update(condition='any dry surface')),('omit_transfer_gap',lambda x:x['differences'].pop()),('invent_gain',lambda x:x.update(engineering_gain=0.5)),('claim_verified',lambda x:x.update(verified_transfer=True)),('omit_controls',lambda x:x.update(test_plan=[]))],
'R49':[('unit_mismatch',lambda x:x['S'].update(deflection_unit='m')),('turn_Bs_to_measurement',lambda x:x.update(actual_measurement=20)),('invent_Be',lambda x:x['Be'].update(target=20)),('claim_situated',lambda x:x.update(situated_worlds_implemented=True)),('omit_model_assumptions',lambda x:x.update(analysis_assumptions=[])),('claim_pass',lambda x:x.update(engineering_pass=True))]}
FIX={k:v for k,v in FIX.items()if k in DIRS}
for rid,(i,fn)in FIX.items():
 output=fn(copy.deepcopy(i));put(rid,'01-固定构造输入.json',i);put(rid,'02-中间推理与输出.json',output)
 rows=[{'name':'fixed_positive','expected':'accept','actual':'accept','pass':True}]
 for name,mut in ATTACKS[rid]:
  q=copy.deepcopy(i);mut(q)
  try:fn(q);actual='accept';err=None
  except (ValueError,KeyError)as e:actual='reject';err=str(e)
  rows.append({'name':name,'expected':'reject','actual':actual,'reason':err,'pass':actual=='reject'})
  put(rid,'探针-'+name+'.json',q)
 assert all(x['pass']for x in rows),(rid,rows)
 put(rid,'03-实际检查汇总.json',{'executed_cases':len(rows),'passed':sum(x['pass']for x in rows),'rows':rows,'qualification':'fixed fixture structure/arithmetic checks, not general semantic or engineering validation'})
transfer={
'R28':{'context':'document sharing workflow','contradiction':'high access availability for authorized work, low access for unauthorized exposure','conditions':['authorized context','unauthorized context'],'result':'condition separation is a direction only; no access-control implementation or guarantee'},
'R29':{'context':'document approval workflow','history':[8,6,5],'omitted_cost':'exception rework may increase with automation','result':'counts do not establish total benefit or inevitable automation'},
'R18':{'context':'packaging release surface','changed_contact':'adhesive/polymer instead of insect pad/claw','result':'original experiment does not establish packaging release force or durability'},
'R49':{'context':'document delivery','F':'make readable artifact available','Be':'recipient can open intended revision; criterion unknown','S':'exported file plus delivery route','Bs':'no compatible inspection or recipient observation','result':'delivery record cannot imply readable recipient experience'}}
for rid,t in transfer.items():
 if rid not in DIRS:continue
 t['actual_scope']='desk comparison of changed conditions only; no field experiment';t['claim_supported']=False;put(rid,'04-另一情境迁移核查.json',t)
print(json.dumps({'methods':list(FIX),'checks':14,'passed':14,'no_engineering_or_user_validation':True}))

for rid,field,val in [('R28','version','99'),('R18','test_plan',['','',''])]:
 i,fn=FIX[rid];q=copy.deepcopy(i);q[field]=val
 try:fn(q);raise AssertionError('review attack accepted')
 except ValueError as e:put(rid,'05-修订攻击实际检查.json',{'input':q,'rejected':True,'reason':str(e)})
