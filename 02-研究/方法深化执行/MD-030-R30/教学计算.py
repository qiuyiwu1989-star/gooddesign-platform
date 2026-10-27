# -*- coding: utf-8 -*-
from pathlib import Path
import copy,json,math,hashlib
D=Path(__file__).resolve().parent;P=D/'教学包';P.mkdir(exist_ok=True)
def put(n,x):(P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False))
shared=D.parent/'修订版/MD-001-R48-v0.1.1/教学包/00-共享教学输入-v0.1.0.json'
SHA=hashlib.sha256(shared.read_bytes()).hexdigest();assert SHA=='c9d262d505656bcaf6c76edee99e3615440f5e2d1c6ef4067e9c1b15a2ddcd70'
BIND={'problem':'TAP-TEACH-001','input_version':'0.1.0','shared_sha256':SHA,'identity':'constructed_research_context_only'}
base={'binding':BIND,'origin':'independent_ideal_local_model','FR':[{'id':'FR1','name':'holding force increment','unit':'N'},{'id':'FR2','name':'release clearance increment','unit':'mm'}],'DP':[{'id':'DP1','name':'adjuster1 increment','unit':'mm'},{'id':'DP2','name':'adjuster2 increment','unit':'mm'}],'workpoint':{'DP1_mm':0,'DP2_mm':0,'load':'ideal_declared_model_only'},'A':[[2,0],[0.5,3]],'matrix_evidence':'analytical_derivatives_of_authored_linear_model_not_measured','delta_target':[2,4],'information_probability':None,'customer_approved':False}
def model(dp):return [2*dp[0],0.5*dp[0]+3*dp[1]]
def examine(i):
 if i['binding']!=BIND or i['origin']!=base['origin']:raise ValueError('context_or_model_origin')
 for k in ['FR','DP','workpoint','matrix_evidence']:
  if i[k]!=base[k]:raise ValueError('fixed_workpoint_units_or_evidence_changed')
 if i['information_probability']is not None or i['customer_approved']:raise ValueError('unsupported_probability_or_approval')
 A=i['A']
 if len(A)!=2 or any(len(r)!=2 for r in A):raise ValueError('matrix_shape')
 if any(x is None for r in A for x in r):return {'classification':'unknown','adjustment_order':None,'reason':'unknown entry cannot be replaced by zero','information_content':None,'engineering_pass':False}
 if any(type(x)not in(int,float)or not math.isfinite(x)for r in A for x in r):raise ValueError('invalid_matrix_value')
 if A!=base['A']:raise ValueError('matrix_disagrees_with_authored_model')
 t=i['delta_target']
 if len(t)!=2 or any(type(x)not in(int,float)or not math.isfinite(x)for x in t):raise ValueError('target_vector_invalid')
 d1=t[0]/A[0][0];d2=(t[1]-A[1][0]*d1)/A[1][1]
 intermediate=model([d1,0]);final=model([d1,d2]);eps=1e-5
 J=[[(model([eps if j==0 else 0,eps if j==1 else 0])[k]-model([0,0])[k])/eps for j in range(2)]for k in range(2)]
 assert all(math.isclose(J[a][b],A[a][b],abs_tol=1e-8)for a in range(2)for b in range(2))
 return {'classification':'decoupled_in_declared_local_model','adjustment_order':['DP1','DP2'],'delta_DP_mm':[d1,d2],'after_DP1':intermediate,'after_DP2':final,'finite_difference_J':J,'information_content':None,'engineering_pass':False,'scope':'linear mathematical fixture; no physical independence proof'}
put('01-输入.json',base);put('02-中间与输出.json',examine(copy.deepcopy(base)))
checks=[]
def test(name,kind,mut,expect):
 q=copy.deepcopy(base);mut(q)
 try:o=examine(q);actual=o.get('classification','accepted')
 except (ValueError,KeyError,TypeError)as e:o={'error':str(e)};actual='rejected'
 checks.append({'name':name,'class':kind,'input':q,'actual':actual,'expected':expect,'pass':actual==expect,'output':o})
test('positive','正常',lambda x:None,'decoupled_in_declared_local_model')
test('unknown_not_zero','缺材料',lambda x:x['A'][0].__setitem__(1,None),'unknown')
test('unknown_claimed_zero_disagrees_model','冲突',lambda x:x['A'][1].__setitem__(0,0),'rejected')
test('changed_load','不适用',lambda x:x['workpoint'].update(load='real_tree_load'),'rejected')
test('zero_increment','边界',lambda x:x.update(delta_target=[0,0]),'decoupled_in_declared_local_model')
test('bool_coefficient','冲突',lambda x:x['A'][0].__setitem__(1,False),'rejected')
test('invent_probability','缺材料',lambda x:x.update(information_probability=0.95),'rejected')
test('unit_change','冲突',lambda x:x['FR'][0].update(unit='kN'),'rejected')
assert all(x['pass']for x in checks);put('03-实际检查.json',checks)
put('04-迁移桌面检查.json',{'context':'two independent document layout controls','possible_FR':['title width','body width'],'required':'test whether styles share a variable and obtain local dependency evidence','matrix':[[None,None],[None,None]],'classification':'unknown','result':'cannot reuse mechanical coefficient or call CSS independence proved','actual_scope':'desk mapping only'})
print(json.dumps({'checks':len(checks),'all_pass':True}))
