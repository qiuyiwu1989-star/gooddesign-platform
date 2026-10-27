# -*- coding: utf-8 -*-
from pathlib import Path
import json,hashlib,copy
D=Path(__file__).resolve().parent;ROOT=D.parents[2];P=D/'教学包';P.mkdir(exist_ok=True)
def put(n,x):(P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2))
UP=ROOT/'output/method-reader-review/upgrades/R04-v0.2.1-proposal';bindings={n:hashlib.sha256((UP/n).read_bytes()).hexdigest()for n in['case.json','verification.json','manifest.json']}
base={'origin':'055_supplement_independent_architecture_change_fixture','prior_binding':bindings,'usage_need':{'id':'NEED-OBSERVE','state':'research_not_approved'},'selected_architecture':'ARCH-B','architectures':{'ARCH-A':{'sensor':'SENSOR-A','derived_requirement':'DR-A-LATENCY','budget_ms':300},'ARCH-B':{'sensor':'SENSOR-B','derived_requirement':'DR-B-LATENCY','budget_ms':100}},'active_derived_requirement':'DR-B-LATENCY','evidence':{'id':'EV-A','sensor':'SENSOR-A','architecture':'ARCH-A','actual_status':'constructed_plan_not_executed'},'claim_evidence_reused':False,'interface_closed':False,'engineering_pass':False}
def check(i):
 if i['origin']!=base['origin']or i['prior_binding']!=bindings or i['usage_need']!=base['usage_need']or i['architectures']!=base['architectures']:raise ValueError('fixed_context_or_derived_budget_changed')
 a=i['selected_architecture']
 if a not in i['architectures']:raise ValueError('architecture_identity')
 spec=i['architectures'][a]
 if i['active_derived_requirement']!=spec['derived_requirement']:raise ValueError('stale_derived_requirement')
 if i['evidence']!=base['evidence']:raise ValueError('invented_evidence_identity_or_status')
 if i['claim_evidence_reused']or i['interface_closed']or i['engineering_pass']:raise ValueError('unsupported_reuse_or_closure')
 return {'trace':{'need':'NEED-OBSERVE','architecture':a,'sensor':spec['sensor'],'derived_requirement':spec['derived_requirement'],'budget_ms':spec['budget_ms'],'budget_basis':'authored_configuration_specific_not_customer_limit'},'retire_or_reassess':['DR-A-LATENCY']if a=='ARCH-B'else[],'evidence_applicable':False,'reason':'old sensor/configuration and unexecuted plan cannot verify new architecture','open_interfaces':['timestamp','identity','clock','authority','actual latency distribution'],'next':['define new evidence/configuration binding','review architecture-derived constraints','plan integration check'],'engineering_pass':False}
put('01-架构变更输入与旧包绑定.json',base);put('02-双向追溯与撤回.json',check(base));cases=[]
def t(n,k,mut,exp):
 q=copy.deepcopy(base);mut(q)
 try:o=check(q);state='accepted'
 except(ValueError,KeyError,TypeError)as e:o={'error':str(e)};state='rejected'
 cases.append({'name':n,'class':k,'input':q,'output':o,'actual':state,'expected':exp,'pass':state==exp})
t('normal_changed_sensor','正常',lambda x:None,'accepted');t('old_budget_requirement','冲突',lambda x:x.update(active_derived_requirement='DR-A-LATENCY'),'rejected');t('reuse_old_evidence','冲突',lambda x:x.update(claim_evidence_reused=True),'rejected');t('missing_architecture','缺材料',lambda x:x.update(selected_architecture=None),'rejected');t('pretend_closed','边界',lambda x:x.update(interface_closed=True),'rejected');t('real_pass','不适用',lambda x:x.update(engineering_pass=True),'rejected');t('derived_to_original_need','冲突',lambda x:x['usage_need'].update(state='approved_latency_100ms'),'rejected')
assert all(x['pass']for x in cases);put('03-实际检查.json',cases)
put('04-迁移桌面检查.json',{'context':'replace document export engine','retained_need':'deliver readable revision','derived_constraint':'new renderer format/font/runtime identities','evidence':'old renderer screenshot does not verify new export','actual_scope':'desk version binding comparison only'})
print('R04 supplemental7 checks passed; prior055 not rewritten')
