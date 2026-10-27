from pathlib import Path
import copy,json
P=Path(__file__).resolve().parent
records=[{'id':'HZ01','phase':'normal','task':'人员可能靠近构造作业头','hazard':'运动刀具/夹持区域','exposure':'operator_or_bystander','consequence':'割伤/挤压可能性，严重度与频率未评估'},{'id':'HZ02','phase':'abnormal','task':'构造卡阻后准备介入','hazard':'残余能量及意外再启动','exposure':'operator','consequence':'意外运动伤害，未实测'},{'id':'HZ03','phase':'maintenance','task':'构造清洁换件','hazard':'电源/弹性/重力等能量状态未定','exposure':'maintainer','consequence':'接触和释放能量伤害，未实测'},{'id':'HZ04','phase':'foreseeable_misuse','task':'为观察状态可能跨越防护边界','hazard':'人在危险区时动作仍可能存在','exposure':'operator_or_bystander','consequence':'危险接近，非真实用户行为记录'}]
for h in records:h.update(design_review='candidate_elimination_or_reduced_energy_under_study',safeguard_review='candidate_guarding_and_access_control_under_study',information_review='residual_information_under_study',verification='not_executed',residual_risk='unknown',risk_score=None)
base={'id':'R41-TASK-TEACH-001','origin':'constructed_not_hazard_acceptance','market':None,'machine_use_classification':'agricultural_or_forestry_unresolved','standard_applicability':'not_confirmed','customer_approved':False,'safety_approved':False,'hazards':records}
def check(d):
 if d.get('origin')!='constructed_not_hazard_acceptance'or d.get('customer_approved')is not False or d.get('safety_approved')is not False:raise ValueError('unsupported approval/provenance')
 if d.get('standard_applicability')!='not_confirmed':raise ValueError('no standards applicability certification')
 hs=d.get('hazards');phases={'normal','abnormal','maintenance','foreseeable_misuse'}
 if type(hs)is not list or {h.get('phase')for h in hs}!=phases:return {'status':'incomplete_task_coverage','safe_to_use':False}
 if len({h['id']for h in hs})!=len(hs):raise ValueError('duplicate hazard identity')
 for h in hs:
  if any(not isinstance(h.get(k),str)or not h[k].strip()for k in ['task','hazard','exposure','consequence']):return {'status':'missing_hazard_chain','safe_to_use':False}
  if h.get('design_review')!='candidate_elimination_or_reduced_energy_under_study'or h.get('safeguard_review')!='candidate_guarding_and_access_control_under_study':return {'status':'insufficient_risk_reduction_review','safe_to_use':False}
  if h.get('risk_score')is not None or h.get('verification')!='not_executed'or h.get('residual_risk')!='unknown':raise ValueError('risk or verification invented')
 return {'status':'hazard_research_chain_only','tasks_covered':sorted(phases),'risk_acceptance':None,'safe_to_use':False,'missing':['target jurisdiction','machine/use boundary','exposure and severity evidence','measure design details','validated stopping/isolation/energy assumptions','competent review'],'not_claimed':'standard compliance or machine safety'}
cases=[]
def add(n,d,e):
 r=check(d);assert r['status']==e;cases.append({'name':n,'input':d,'actual':r,'passed':True})
add('正常危险链仍未放行',base,'hazard_research_chain_only')
x=copy.deepcopy(base);x['hazards'].pop();add('缺误用任务',x,'incomplete_task_coverage')
x=copy.deepcopy(base);x['hazards'][0]['design_review']='not_considered';x['hazards'][0]['safeguard_review']='not_considered';x['hazards'][0]['information_review']='warning_label_only';add('仅警告不适用完成安全',x,'insufficient_risk_reduction_review')
x=copy.deepcopy(base);x['hazards'][2]['exposure']='';add('暴露身份边界缺失',x,'missing_hazard_chain')
for n,mut in [('臆造风险零',lambda x:x['hazards'][0].update(risk_score=0)),('无证据残余可接受',lambda x:x['hazards'][0].update(residual_risk='accepted')),('农业标准自动套林业',lambda x:x.update(standard_applicability='ISO18497_compliant'))]:
 x=copy.deepcopy(base);mut(x)
 try:check(x);raise AssertionError(n+' accepted')
 except ValueError as e:cases.append({'name':n,'actual':'rejected','reason':str(e),'passed':True})
x=copy.deepcopy(base);x['id']='DISPLAY-FOLD-TEACH';x['hazards'][0].update(task='折叠展架动作附近有人',hazard='折叠夹点');add('另一情境折叠展示机构',x,'hazard_research_chain_only')
for n,d in [('01-任务危险输入.json',base),('02-实际检查.json',{'cases':cases,'count':len(cases),'scope':'fixed task-chain/status checks; not standards conformity or actual risk estimation'})]:(P/'教学包'/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
print(len(cases),'passed')
