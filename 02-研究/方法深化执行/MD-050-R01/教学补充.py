# -*- coding: utf-8 -*-
from pathlib import Path
import json,hashlib,copy,math
D=Path(__file__).resolve().parent;ROOT=D.parents[2];P=D/'教学包';P.mkdir(exist_ok=True)
def put(n,x):(P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False))
UP=ROOT/'output/method-reader-review/upgrades/R01-v0.2.1-proposal';bindings={n:hashlib.sha256((UP/n).read_bytes()).hexdigest()for n in['case.json','verification.json','manifest.json']}
base={'origin':'supplement_to_existing_055_constructed_fixture','prior_package':{'path':str(UP.relative_to(ROOT)),'sha256':bindings,'status':'pending_independent_review_not_engineering'},'requirement':{'id':'RQ-RELEASE-TEACH','version':'1','min_free_gap_mm':5,'basis':'new_authored_geometric_constraint_not_customer_requirement'},'principles':['P-SCREW','P-LEVER'],'layouts':[{'id':'LAY-v1','principle':'P-LEVER','gap_mm':2,'manufacturing_simplicity':'hypothesis'},{'id':'LAY-v2','principle':'P-LEVER','gap_mm':6,'manufacturing_simplicity':'unknown'}],'manufacturing_release':False,'actual_tests':[]}
def check(i):
 if i['origin']!=base['origin']or i['prior_package']!=base['prior_package']or i['requirement']!=base['requirement']:raise ValueError('binding_or_requirement_changed')
 if i['principles']!=base['principles']or i['manufacturing_release']or i['actual_tests']:raise ValueError('scope_or_false_release')
 ls=i['layouts']
 if len({x['id']for x in ls})!=len(ls)or not ls:raise ValueError('layout_identity')
 rows=[]
 for x in ls:
  if x['principle']not in i['principles']:raise ValueError('dangling_principle')
  gap=x['gap_mm']
  if gap is None:state='unknown'
  elif type(gap)not in(int,float)or not math.isfinite(gap)or gap<0:raise ValueError('invalid_gap')
  else:state='local_gap_rule_pass'if gap>=5 else'return_principle_or_interface'
  rows.append({'layout':x['id'],'requirement':i['requirement']['id'],'gap_state':state,'engineering_pass':False,'change_impact':['release geometry','actuation envelope','contact/load path','manufacturing access'],'retained_unknowns':['force','damage','three-dimensional swept volume']})
 return {'local_reviews':rows,'detail_definition':'held_no_manufacturing_release','customer_baseline':False,'qualification':'additional declared geometry checkpoint, does not replace existing055 stages'}
put('01-旧包绑定与新释放规则.json',base);put('02-回返及局部继续.json',check(base));cases=[]
def t(n,k,mut,exp):
 q=copy.deepcopy(base);mut(q)
 try:o=check(q);state='accepted'
 except(ValueError,KeyError,TypeError)as e:o={'error':str(e)};state='rejected'
 cases.append({'name':n,'class':k,'input':q,'output':o,'actual':state,'expected':exp,'pass':state==exp})
t('normal_v1_return_v2_local_only','正常',lambda x:None,'accepted');t('missing_gap','缺材料',lambda x:x['layouts'][0].update(gap_mm=None),'accepted');t('equal_boundary','边界',lambda x:x['layouts'][1].update(gap_mm=5),'accepted');t('manufacturing_release','不适用',lambda x:x.update(manufacturing_release=True),'rejected');t('unlinked_principle','冲突',lambda x:x['layouts'][1].update(principle='NO'),'rejected');t('bool_gap','冲突',lambda x:x['layouts'][0].update(gap_mm=True),'rejected');t('erase_original_requirement','冲突',lambda x:x['requirement'].update(min_free_gap_mm=0),'rejected')
assert all(x['pass']for x in cases);put('03-实际检查.json',cases)
put('04-迁移桌面检查.json',{'context':'document template design','needs':['readability','editable source','export access'],'principles':['HTML','DOCX'],'layout_change':'fixed typography may simplify printing but break editing/access','return_reason':'do not release based on visual polish alone','actual_scope':'desk mapping; no user test'})
print('R01 supplemental7 checks passed; prior055 not rewritten')
