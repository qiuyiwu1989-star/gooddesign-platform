# -*- coding: utf-8 -*-
from pathlib import Path
import copy,json,math
D=Path(__file__).resolve().parent;P=D/'教学包';P.mkdir(exist_ok=True)
def put(n,x):(P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False))
base={'origin':'constructed_preference_not_customer_interview','criteria':[{'id':'serviceability','group':'service','unit':'authored_value_0_to_1'},{'id':'mobility','group':'handling','unit':'authored_value_0_to_1'}],'value_basis':'explicit authored value functions; these are not raw measured performance','alternatives':[{'id':'A','values':[0.9,0.3],'hard_status':'assumed_pass_within_fixture'},{'id':'B','values':[0.4,0.8],'hard_status':'assumed_pass_within_fixture'},{'id':'C','values':[1,1],'hard_status':'fail_within_fixture'}],'weight_first_range':[0.2,0.8],'preference_record':{'kind':'authored_swing_tradeoff_scenarios','real_interviews':0,'customer_approved':False},'additive_separability_assumption':True}
def check(i):
 if i['origin']!=base['origin']or i['value_basis']!=base['value_basis']or i['preference_record']!=base['preference_record']:raise ValueError('provenance_or_preference_promoted')
 if not i['additive_separability_assumption']:return {'state':'inapplicable_additive_model','ranking':None}
 cs=i['criteria']
 if len(cs)!=2 or len({c['id']for c in cs})!=2 or len({c['group']for c in cs})!=2:raise ValueError('duplicate_preference_or_criterion')
 if cs!=base['criteria']:raise ValueError('unversioned_value_scale')
 w=i['weight_first_range']
 if len(w)!=2 or any(type(v)not in(int,float)or not math.isfinite(v)for v in w)or not 0<=w[0]<=w[1]<=1:raise ValueError('invalid_weights')
 rows=i['alternatives'];ids=[a['id']for a in rows]
 if len(set(ids))!=len(ids)or set(ids)!={'A','B','C'}:raise ValueError('alternative_identity')
 valid=[];excluded=[];unknown=[]
 for a in rows:
  if a['hard_status']=='fail_within_fixture':excluded.append(a['id']);continue
  if a['hard_status']=='unknown':unknown.append(a['id']);continue
  if a['hard_status']!='assumed_pass_within_fixture':raise ValueError('hard_status')
  if any(v is None for v in a['values']):unknown.append(a['id']);continue
  if len(a['values'])!=2 or any(type(v)not in(int,float)or not math.isfinite(v)or not 0<=v<=1 for v in a['values']):raise ValueError('value_invalid')
  valid.append(a)
 if unknown:return {'state':'needs_evidence','unknown':unknown,'excluded':excluded,'ranking':None}
 scores=[]
 for weight in [w[0],sum(w)/2,w[1]]:
  ss={a['id']:weight*a['values'][0]+(1-weight)*a['values'][1]for a in valid};mx=max(ss.values());scores.append({'weight_service':weight,'scores':ss,'winners':[k for k,v in ss.items()if abs(v-mx)<1e-10]})
 A=next(a for a in valid if a['id']=='A')['values'];B=next(a for a in valid if a['id']=='B')['values'];den=(A[0]-A[1])-(B[0]-B[1]);cross=(B[1]-A[1])/den if den else None
 return {'state':'preference_sensitive','excluded':excluded,'scenarios':scores,'A_B_crossover_weight':cross,'unique_robust_winner':None,'customer_decision':None,'performance_evidence':'synthetic_only','qualification':'weighted value model under declared additive assumption, not calibrated customer preference'}
put('01-输入与偏好记录.json',base);put('02-敏感性与排除输出.json',check(base));cases=[]
def t(name,kind,mut,expected):
 q=copy.deepcopy(base);mut(q)
 try:o=check(q);state=o['state']
 except(ValueError,KeyError,TypeError)as e:o={'error':str(e)};state='rejected'
 cases.append({'name':name,'class':kind,'input':q,'output':o,'actual':state,'expected':expected,'pass':state==expected})
t('normal','正常',lambda x:None,'preference_sensitive');t('missing_value','缺材料',lambda x:x['alternatives'][0]['values'].__setitem__(0,None),'needs_evidence');t('duplicate_mass_handling_preference','冲突',lambda x:x['criteria'][1].update(group='service'),'rejected');t('unknown_hard_constraint','缺材料',lambda x:x['alternatives'][0].update(hard_status='unknown'),'needs_evidence');t('equal_weight_tie','边界',lambda x:x.update(weight_first_range=[0.5,0.5]),'preference_sensitive');t('nonadditive','不适用',lambda x:x.update(additive_separability_assumption=False),'inapplicable_additive_model');t('negative_weight','冲突',lambda x:x.update(weight_first_range=[-1,0.8]),'rejected');t('invent_interview','冲突',lambda x:x['preference_record'].update(real_interviews=3),'rejected')
assert all(x['pass']for x in cases);put('03-实际检查.json',cases)
put('04-迁移桌面检查.json',{'context':'document delivery tool choice','criteria':['retrieval_effort','auditability'],'value_functions':'not elicited','weights':None,'ranking':None,'actual_scope':'desk transfer; must elicit tradeoffs and avoid counting file size plus linear storage cost twice','customer_decision':None})
print('R37:8 checks passed')
