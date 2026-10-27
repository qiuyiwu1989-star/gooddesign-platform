from pathlib import Path
import json,math,copy
P=Path(__file__).resolve().parent
base={'id':'WB04-JOINT-TEACH-001','origin':'independent_linear_joint_fixture_not_author_formula','function':'maintain controlled relative action, research assumption only','candidate':{'id':'A','mass_kg':2.,'stiffness_N_m':1000.,'damping_Ns_m':2.,'seal_replaceable':True},'excitation':{'force_N':1.,'omega_rad_s':math.sqrt(1000.)},'teaching_amplitude_limit_m':.003,'X':{'need_id':'TEACH-X-CLEAN','name':'replaceable contamination barrier','status':'constructed_special_requirement'},'customer_approved':False,'engineering_validated':False,'separate_optima_summed':False,'manufacturing_cost':None,'actual_function_evidence':None}
def calc(d):
 if d.get('origin')!=base['origin']or d.get('customer_approved')is not False or d.get('engineering_validated')is not False or d.get('separate_optima_summed')is not False:raise ValueError('unsupported approval or sum of separate optima')
 if 'actual_function_evidence'not in d or d['actual_function_evidence']is not None:raise ValueError('actual function evidence field unsupported; use independently reviewed new contract')
 if d.get('manufacturing_cost')is not None:raise ValueError('cost evidence unsupported in this model')
 if d.get('X')!=base['X']:raise ValueError('special need must keep source identity; not arbitrary X module')
 a=d.get('candidate',{});e=d.get('excitation',{});vals=[a.get(k)for k in ['mass_kg','stiffness_N_m','damping_Ns_m']]+[e.get('force_N'),e.get('omega_rad_s'),d.get('teaching_amplitude_limit_m')]
 if any(v is None for v in vals):return {'status':'unknown_joint_model','selected':None}
 if any(type(v)not in(int,float)or not math.isfinite(v)or v<=0 for v in vals):raise ValueError('positive finite nonboolean model quantities')
 if type(a.get('seal_replaceable'))is not bool:raise ValueError('explicit service property required')
 m,k,c,F,w,lim=vals;amp=F/math.hypot(k-m*w*w,c*w);wn=math.sqrt(k/m);viol=[]
 if amp>lim:viol.append('use_response_exceeds_constructed_limit')
 if not a['seal_replaceable']:viol.append('manufacturing_merge_breaks_X_service_requirement')
 return {'status':'joint_model_conflict'if viol else'joint_research_candidate_only','same_candidate_parameters_used':a,'natural_omega_rad_s':wn,'response_m':amp,'violations':viol,'separate_domain_scores_summed':False,'engineering_selected':None,'function_validated':False,'cost':None,'scope':'single linear mode and explicit teaching service property; not complete1+3+X solver'}
cases=[]
def add(n,d,e):
 r=calc(d);assert r['status']==e;cases.append({'name':n,'input':d,'actual':r,'passed':True})
add('正常共同参数联审',base,'joint_research_candidate_only')
x=copy.deepcopy(base);x['candidate']['mass_kg']=1.;add('只追减重移入共振冲突',x,'joint_model_conflict')
x=copy.deepcopy(base);x['candidate']['seal_replaceable']=False;add('制造合并破坏使用维护',x,'joint_model_conflict')
x=copy.deepcopy(base);x['excitation']['omega_rad_s']=None;add('缺激励资料',x,'unknown_joint_model')
for n,mut in [('分领域最优分数相加不适用',lambda d:d.update(separate_optima_summed=True)),('凑X无来源',lambda d:d['X'].update(need_id=None)),('布尔质量边界',lambda d:d['candidate'].update(mass_kg=True)),('伪功能已证',lambda d:d.update(engineering_validated=True))]:
 x=copy.deepcopy(base);mut(x)
 try:calc(x);raise AssertionError(n+' accepted')
 except ValueError as e:cases.append({'name':n,'actual':'rejected','reason':str(e),'passed':True})
x=copy.deepcopy(base);x['id']='DISPLAY-JOINT-TEACH';x['function']='research stable display support';x['candidate']['mass_kg']=3.;add('展示支架另一情境联审',x,'joint_research_candidate_only')
for n,mut in [('ignored-actual-function-evidence',lambda d:d.update(actual_function_evidence={'claimed':'verified'})),('ignored-manufacturing-cost',lambda d:d.update(manufacturing_cost=0)),('missing-function-evidence-unknown',lambda d:d.pop('actual_function_evidence'))]:
 q=copy.deepcopy(base);mut(q)
 try:calc(q);raise AssertionError(n+' accepted')
 except ValueError as e:cases.append({'name':n,'actual':'rejected','reason':str(e),'passed':True})
(P/'教学包/01-共同参数输入.json').write_text(json.dumps(base,ensure_ascii=False,indent=2)+'\n');(P/'教学包/02-跨域冲突实际复算.json').write_text(json.dumps({'cases':cases,'count':len(cases),'dependency_graph':['function->structure','same mass/stiffness->dynamic use response','manufacturing consolidation->serviceability','special need->service constraint'],'joint_review':'function, structural, use, manufacturing, special needs must refer same candidate/version; no overall score'},ensure_ascii=False,indent=2)+'\n');print(len(cases),'passed')
