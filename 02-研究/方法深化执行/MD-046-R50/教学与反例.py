# -*- coding: utf-8 -*-
from pathlib import Path
import copy,json,math
P=Path(__file__).parent;B=P.parent;DIR={'R50':P,'R51':B/'MD-047-R51','R52':B/'MD-048-R52','R07':B/'MD-049-R07'}
def put(r,n,v):
 p=DIR[r]/'教学包'/n;p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2))
blue={'id':'BLUE-TEACH-001','version':'0.1.0','identity':'future_hypothetical_shift_not_observed_current_service','customer_approved':False,'steps':[{'id':i,'user':u,'frontstage':f,'backstage':ba,'support':su,'evidence_object':e,'owner_role':ow,'wait_s':None,'failure':fail,'recovery':rec}for i,u,f,ba,su,e,ow,fail,rec in [('BP1','接班核对','显示交接记录身份','核工单与版本','记录服务','交接记录','班组协调角色待指派','记录不全','暂停接班并回查记录'),('BP2','发起作业请求','区分请求与实际状态','核任务授权及反馈','控制/供能服务','请求与状态分列','现场控制角色待指派','反馈陈旧','抑制新动作请求并交异常处理'),('BP3','报告异常等待处理','显示尚未恢复','派发异常并保留上下文','维护支持','异常单','维护协调角色待指派','无人接单','升级协调并保持恢复未授权'),('BP4','清理检修后交接','显示检修范围与未决项','核维护记录与隔离/恢复前提','备件/工具支持','维护与隔离记录','维护执行角色待指派','缺恢复证据','禁止以检修完成替代恢复授权'),('BP5','班末交班','显示任务完成身份与未决项','核账与安排后续','档案支持','班末未决清单','交接责任角色待指派','未决被遗失','保留开放异常并交明确接收角色')]],'actual_observations':[],'measured_waits':False}
BL=copy.deepcopy(blue)
def check50(x):
 if x!=BL:raise ValueError('fixed_future_blueprint_identity_roles_or_recovery_changed')
 return {'layers':['user','frontstage','backstage','support','evidence_object'],'visibility_boundary':'frontstage_vs_backstage_not_organization_rank','step_count':5,'open_waits':5,'actual_current_state_evidence':[],'measured_savings':None,'recoveries':[{'step':s['id'],'owner':s['owner_role'],'action':s['recovery']}for s in x['steps']],'status':'future_research_map_only'}
stpa={'id':'STPA-TEACH-001','version':'0.1.0','scope':'hypothetical_local_contact_process_not_full_robot_safety_analysis','losses':[{'id':'L1','text':'不可接受的组织或人员损伤（研究假设）'}],'hazards':[{'id':'H1','text':'未知组织边界或恢复前提下仍有危险相对接触作用','losses':['L1']}],'control_structure':{'controller':'local_controller','controlled_process':'contact_action','actions':['enable','inhibit'],'feedback':['actual_motion','data_timestamp','residual_state'],'process_model':['boundary_known','actual_stop','recovery_authorized']},'ucas':[{'id':i,'class':cl,'action':a,'context':co,'hazards':['H1'],'constraint':c}for i,cl,a,co,c in [('U1','not_provided','inhibit','边界信息已失效但未发抑制','边界信息失效应触发抑制请求与实际状态确认研究'),('U2','provided','enable','恢复前提未确认却使能','未确认恢复前提不得使能'),('U3','timing_order','enable','在实际停止/恢复审查之前过早使能','顺序应依据实际状态与授权，而非请求应答'),('U4','duration','inhibit','危险条件仍存在但过早终止抑制','解除抑制需有恢复条件依据')]],'scenarios':[{'id':'SC1','uca':'U2','mechanism':'陈旧反馈被过程模型当成当前停止，控制算法据错误信念使能','control_flaw':'timestamp_validity_not_checked','not_necessarily_component_failure':True,'derived_requirement':'拟分开反馈时点、停止状态及恢复授权','status':'candidate_not_approved'}],'safety_certified':False,'frequencies':None}
ST=copy.deepcopy(stpa)
def check51(x):
 if x!=ST:raise ValueError('fixed_control_context_or_trace_changed')
 return {'loss_hazard_constraint_trace':[{'uca':u['id'],'hazards':u['hazards'],'constraint':u['constraint']}for u in x['ucas']],'four_classes_present':len({u['class']for u in x['ucas']})==4,'scenario':x['scenarios'],'status':'partial_constructed_hazard_analysis','complete_system_analysis':False,'safety_certified':False,'handoff':'R05 feedback/control authority; R42 verification evidence; R40 complementary failure analysis'}
voi={'id':'VOI-TEACH-001','provenance':'independent_teaching_probabilities_losses_not_customer_estimates','states':['good','bad'],'actions':['A','B'],'prior':[.5,.5],'loss':{'A':[0.,100.],'B':[40.,0.]},'signal_positive_likelihood':[.8,.2],'study_cost':2.,'delay_loss':1.,'loss_unit':'synthetic_loss_units','hard_requirement_waiver':False}
def check52(x):
 if x['provenance']!=voi['provenance']or x['hard_requirement_waiver']:raise ValueError('provenance_or_hard_waiver')
 if x['prior']is None:return {'status':'cannot_compute_missing_probability','EVPI':None,'EVSI':None}
 if x['states']!=['good','bad']or x['actions']!=['A','B']or set(x['loss'])!={'A','B'}:raise ValueError('unsupported_identity')
 arrays=[x['prior'],x['signal_positive_likelihood'],*x['loss'].values()]
 if any(not isinstance(a,list)or len(a)!=2 for a in arrays):raise ValueError('two_state_arrays_required')
 if any(type(z)not in(int,float)or not math.isfinite(z)for a in arrays for z in a):raise ValueError('nonfinite_or_boolean')
 pr=x['prior'];lk=x['signal_positive_likelihood'];loss=x['loss']
 if any(not 0<=p<=1 for p in pr+lk)or not math.isclose(sum(pr),1):raise ValueError('probability_domain')
 if any(z<0 for a in loss.values()for z in a):raise ValueError('negative_loss_not_supported')
 if any(type(x[k])not in(int,float)or not math.isfinite(x[k])or x[k]<0 for k in ['study_cost','delay_loss']):raise ValueError('invalid_cost')
 risks={a:sum(p*l for p,l in zip(pr,loss[a]))for a in x['actions']};current=min(risks.values());perfect=sum(pr[s]*min(loss[a][s]for a in x['actions'])for s in range(2));post=[];expected=0
 for label,lik in [('positive',lk),('negative',[1-z for z in lk])]:
  joint=[pr[s]*lik[s]for s in range(2)];prob=sum(joint)
  if prob==0:post.append({'signal':label,'probability':0,'posterior':None,'action':None});continue
  posterior=[p/prob for p in joint];rr={a:sum(p*l for p,l in zip(posterior,loss[a]))for a in x['actions']};act=min(rr,key=rr.get);expected+=prob*rr[act];post.append({'signal':label,'probability':prob,'posterior':posterior,'conditional_risks':rr,'action':act})
 evpi=current-perfect;evsi=current-expected;assert -1e-10<=evsi<=evpi+1e-10
 return {'status':'teaching_decision_model_only','current_risks':risks,'current_action':min(risks,key=risks.get),'posterior_actions':post,'expected_risk_after_sample':expected,'EVPI':evpi,'EVSI':evsi,'net_sample_value':evsi-x['study_cost']-x['delay_loss'],'engineering_recommendation':None,'real_customer_probabilities':False}
dfss={'id':'DFSS-TEACH-001','version':'0.1.0','mode':'new_design_research','framework':'selected_DMADV_family_not_single_algorithm','voice':'希望作用边界可理解并可核对（构造假设）','ctq':[{'id':'CTQ1','need':'N-T01','candidate':'边界信息与允许作用的对应','operational_definition':'拟定义参考信号、组织对象、时点、测量过程与误差；当前尚未确认','target':None,'unit':None,'approved':False}],'measurement_plan':{'measurand':'同一构造参考件位置读数，仅教学测量计划非组织边界验证','parts':['P1','P2','P3'],'operators':['O1','O2'],'repeats':2,'order':'randomized_and_blinded_proposed','calibration':'unknown','environment':'record_conditions_proposed','raw_observations':[],'implemented':False},'design_response':'先研究测量原理与误差来源，再安排候选设计试验','confirmation_plan':'需真实场景/对象与专业判据；未实施','sigma_level':None,'Cp':None,'Cpk':None,'engineering_validated':False}
DF=copy.deepcopy(dfss)
def check07(x):
 if x!=DF:raise ValueError('fixed_CTQ_measurement_identity_or_validation_changed')
 cells=[{'part':p,'operator':o,'repeat':r,'value':None}for p in x['measurement_plan']['parts']for o in x['measurement_plan']['operators']for r in range(1,3)]
 return {'status':'measurement_readiness_not_established','planned_reading_cells':cells,'planned_cells_count':len(cells),'actual_readings':0,'repeatability':None,'reproducibility':None,'bias':None,'stability':None,'capability':None,'sigma_level':None,'reason':'measurement and specifications unconfirmed; DFSS phases do not establish quality level'}
models={'R50':(blue,check50),'R51':(stpa,check51),'R52':(voi,check52),'R07':(dfss,check07)}
for rid,(x,fn)in models.items():put(rid,'01-固定构造输入.json',x);put(rid,'02-中间推理与输出.json',fn(copy.deepcopy(x)))
assert check52(voi)['EVPI']==20 and math.isclose(check52(voi)['EVSI'],6)
attacks={'R50':[('as-current',lambda x:x.update(identity='observed_current_service')),('invent-wait',lambda x:x['steps'][0].update(wait_s=10)),('delete-recovery',lambda x:x['steps'][2].update(recovery='')),('erase-owner',lambda x:x['steps'][2].update(owner_role='')),('fake-observation',lambda x:x['actual_observations'].append('done')),('version-drift',lambda x:x.update(version='99'))],'R51':[('drop-class',lambda x:x['ucas'].pop()),('erase-feedback',lambda x:x['control_structure'].update(feedback=[])),('no-context',lambda x:x['ucas'][0].update(context='')),('dangling-hazard',lambda x:x['ucas'][0].update(hazards=['NO'])),('claim-certified',lambda x:x.update(safety_certified=True)),('invent-frequency',lambda x:x.update(frequencies=.01))],'R52':[('probability-sum',lambda x:x.update(prior=[.8,.8])),('likelihood-outside',lambda x:x.update(signal_positive_likelihood=[1.2,.2])),('NaN-loss',lambda x:x['loss']['A'].__setitem__(0,float('nan'))),('negative-cost',lambda x:x.update(study_cost=-1)),('fake-customer',lambda x:x.update(provenance='customer_observed')),('hard-waiver',lambda x:x.update(hard_requirement_waiver=True))],'R07':[('invent-target',lambda x:x['ctq'][0].update(target=.1)),('fake-reading',lambda x:x['measurement_plan']['raw_observations'].append(1)),('fake-sigma',lambda x:x.update(sigma_level=6)),('as-existing-improvement',lambda x:x.update(mode='existing_process_DMAIC')),('erase-measurement',lambda x:x.update(measurement_plan={})),('claim-approved',lambda x:x['ctq'][0].update(approved=True))]}
for rid,(x,fn)in models.items():
 rows=[{'case':'normal','accepted':True,'pass':True}]
 for name,mut in attacks[rid]:
  q=copy.deepcopy(x);mut(q)
  try:out=fn(q);accepted=True
  except(ValueError,KeyError,TypeError)as e:out={'error':str(e)};accepted=False
  assert not accepted;rows.append({'case':name,'accepted':accepted,'pass':True});put(rid,'探针-'+name+'.json',{'input':q,'output':out})
 put(rid,'03-实际检查汇总.json',{'executed':7,'passed':7,'cases':rows,'scope':'fixed fixture checks only; no field tests/participants/professional certification'})
# Explicit study designs and delay sensitivity, not guessed field probabilities.
vs=[]
for name,lik,cost,delay in [('uninformative',[.5,.5],0,0),('perfect',[1.,0.],0,0),('costly',[.8,.2],7,0),('delay-sensitive',[.8,.2],2,5)]:
 q=copy.deepcopy(voi);q.update(signal_positive_likelihood=lik,study_cost=cost,delay_loss=delay);vs.append({'case':name,'output':check52(q)})
assert vs[0]['output']['EVSI']==0 and vs[1]['output']['EVSI']==20 and vs[2]['output']['net_sample_value']<0
put('R52','04-信息质量成本延误敏感性.json',vs)
transfers={'R50':{'context':'文档交付服务','user':'申请某版本','frontstage':'显示请求状态','backstage':'生成并核版本','support':'档案权限','failure':'源版本未知','owner':'交付角色待任命','recovery':'暂停宣称交付并核源版本','wait':None},'R51':{'context':'文档发布控制','control_action':'publish','unsafe_context':'未确认版本/授权时提供发布动作','feedback_gap':'已提交误作已审核','constraint':'未满足发布授权不得发布','not_security_certification':True},'R07':{'context':'文档导出质量','CTQ':'可读版本身份（假设）','measurement':'需不同环境与观察口径','specification':None,'actual_measurements':[],'capability':None}}
for rid,t in transfers.items():t['scope']='constructed desk mapping only, no actual service/user study';put(rid,'05-另一情境迁移.json',t)
q=copy.deepcopy(voi);q['id']='DOC-VOI-TEACH';q['loss_unit']='synthetic document rework units';put('R52','05-另一情境迁移.json',{'input':q,'actual_math_output':check52(q),'scope':'same constructed loss structure, not actual document probabilities'})
print('28 fixed checks plus4 VOI sensitivity runs; no field validation')
