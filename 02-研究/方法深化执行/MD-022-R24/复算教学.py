from pathlib import Path
import math,json,copy
P=Path(__file__).resolve().parent
# Conventional gravity arithmetic; authored illustration, not ARIZ algorithm or robot measurement.
def assess(d):
 keys=['mass_kg','g_m_s2','stroke_m','efficiency','required_work_J','window_s','required_time_s','orientation_deg']
 if any(d.get(k)is None for k in keys):return {'status':'unknown','reason':'missing_budget_or_orientation'}
 if any(type(d[k])not in (int,float)or not math.isfinite(d[k])for k in keys):raise ValueError('finite real numbers required, booleans rejected')
 if min(d[k]for k in keys[:3]+['required_work_J','window_s','required_time_s'])<0 or not 0<d['efficiency']<=1:raise ValueError('invalid budget')
 if abs(d['orientation_deg'])>90:return {'status':'resource_direction_conflict'}
 available=d['mass_kg']*d['g_m_s2']*d['stroke_m']*d['efficiency']*math.cos(math.radians(d['orientation_deg']))
 margin=available-d['required_work_J']
 if margin<=0:return {'status':'budget_insufficient_or_no_margin','available_J':available,'margin_J':margin}
 if d['window_s']<=d['required_time_s']:return {'status':'time_window_not_established','available_J':available}
 return {'status':'budget_only_research_candidate','available_J':available,'margin_J':margin,'engineering_validated':False,'unresolved':['force versus position','acceleration and impact','friction variation','reset energy and labor','failure orientation']}
base={'id':'R24-GRAVITY-TEACH-001','mode':'independent_constructed_budget','mass_kg':1,'g_m_s2':10,'stroke_m':.1,'efficiency':.5,'required_work_J':.2,'window_s':3,'required_time_s':1,'orientation_deg':0,'number_origin':'arbitrary illustrative values, g rounded to 10 for arithmetic; not local measured gravity or robot parameters'}
cases=[]
def add(n,d,expected):
 r=assess(d);assert r['status']==expected;cases.append({'name':n,'input':d,'actual':r,'passed':True})
add('正常预算',base,'budget_only_research_candidate')
x=copy.deepcopy(base);x['efficiency']=None;add('缺效率',x,'unknown')
x=copy.deepcopy(base);x['orientation_deg']=180;add('方向相反不适用',x,'resource_direction_conflict')
x=copy.deepcopy(base);x['required_work_J']=.5;add('等能量无余量边界',x,'budget_insufficient_or_no_margin')
x=copy.deepcopy(base);x['required_work_J']=.6;add('需求功冲突',x,'budget_insufficient_or_no_margin')
x=copy.deepcopy(base);x['required_time_s']=3;add('时间窗口边界',x,'time_window_not_established')
x=copy.deepcopy(base);x['id']='DOC-HANDOFF-TEACH-001';x['mass_kg']=None;add('文档任务无机械资源预算不能硬套',x,'unknown')
x=copy.deepcopy(base);x['id']='DISPLAY-COVER-TEACH-001';x['orientation_deg']=60;x['required_work_J']=.1;add('不同情境展柜盖板斜向回落',x,'budget_only_research_candidate')
try:x=copy.deepcopy(base);x['mass_kg']=True;assess(x);raise AssertionError('bool accepted')
except ValueError:cases.append({'name':'布尔不冒充数值','actual':'rejected','passed':True})
resources=[{'kind':'material','item':'existing moving assembly','amount':None,'unit':'kg','at_required_location_time':'unknown'},{'kind':'energy','item':'gravitational potential','amount':None,'unit':'J','orientation':'unknown','note':'main robot chain unknown, separate illustrative .5 J is not assigned here'},{'kind':'information','item':'existing state/time record','amount':None,'unit':None,'validity':'unknown'},{'kind':'time','item':'abnormal stop interval','amount':None,'unit':'s','availability':'unknown'}]
for n,d in [('01-构造预算输入.json',base),('02-资源账与副作用.json',{'resource_ledger':resources,'ideal_goal':'在保留退出作用的条件下探索减少新增回位驱动','goal_status':'platform_research_aspiration_not_customer_requirement','new_burdens':['reset lifting energy','orientation restriction','impact protection','maintenance labor','contamination and wear'],'robot_quantity_budget':'unknown, do not import illustrative values'}),('03-实际检查.json',{'cases':cases,'count':len(cases),'scope':'explicit arithmetic only, not resource sufficiency of real mechanism'})]:
 (P/'教学包'/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
print(len(cases),'passed')
