"""原创条件表检查，非TRIZ全部规则求解器；秒/牛顿均为独立构造数。"""
from pathlib import Path
import json,copy,math
P=Path(__file__).resolve().parent
def assess(d):
 if d['mode']!='constructed_teaching' or d['customer_approved']is not False:raise ValueError('scope')
 demands=d.get('demands')
 if type(demands)is not list or len(demands)!=2 or any(type(a)is not dict for a in demands):raise ValueError('two explicit demand mappings required')
 if any(a.get('direction')not in {'high','low'}for a in demands):raise ValueError('supported opposite domain is high/low only')
 for a in demands:
  interval=a.get('interval_s')
  if interval is not None and (type(interval)is not list or len(interval)!=2 or any(type(t)not in(int,float)or not math.isfinite(t)or t<0 for t in interval)or interval[0]>interval[1]):raise ValueError('invalid finite nonnegative ordered interval')
 st=d.get('switch_time_s')
 if st is not None and(type(st)not in(int,float)or not math.isfinite(st)or st<0):raise ValueError('invalid switch time')
 a,b=demands
 if a['object']!=b['object']or a['parameter']!=b['parameter']or a['unit']!=b['unit']:return {'status':'not_same_parameter','next':'reformulate'}
 if a['direction']==b['direction']:return {'status':'not_opposite_demands'}
 if any(x.get('interval_s')is None for x in [a,b])or d.get('switch_time_s')is None:return {'status':'unknown','reason':'conditions_or_switch_unknown'}
 t1,t2=sorted([a['interval_s'],b['interval_s']]);overlap=max(0,min(t1[1],t2[1])-max(t1[0],t2[0]));gap=t2[0]-t1[1]
 if gap<0:return {'status':'time_separation_not_established','overlap_s':overlap,'next':'inspect_space_relation_system_level_or_reformulate'}
 if gap<=d['switch_time_s']:return {'status':'transition_not_established','gap_s':gap,'switch_time_s':d['switch_time_s'],'reason':'equality lacks margin; residual energy and uncertainty unchecked'}
 return {'status':'time_separation_research_candidate','gap_s':gap,'switch_time_s':d['switch_time_s'],'engineering_validated':False,'required_checks':['residual energy','switch sensing','failure state','orientation and load','tolerance and margin']}
base={'id':'R23-CLAMP-TEACH-001','mode':'constructed_teaching','customer_approved':False,'demands':[{'object':'same constructed clamp','parameter':'holding_force','unit':'N','direction':'high','interval_s':[0,4],'target':None},{'object':'same constructed clamp','parameter':'holding_force','unit':'N','direction':'low','interval_s':[6,8],'target':None}],'switch_time_s':1,'numerical_status':'arbitrary teaching timing; not robot/customer values'}
cases=[]
def add(name,d,expected):
 r=assess(d);assert r['status']==expected;(cases.append({'name':name,'input':d,'actual':r,'expected_status':expected,'passed':True}))
add('正常构造条件',base,'time_separation_research_candidate')
x=copy.deepcopy(base);x['switch_time_s']=None;add('缺切换证据',x,'unknown')
x=copy.deepcopy(base);x['demands'][1]['parameter']='mass';add('两参数不适用',x,'not_same_parameter')
x=copy.deepcopy(base);x['switch_time_s']=2;add('切换恰等窗口边界',x,'transition_not_established')
x=copy.deepcopy(base);x['demands'][1]['interval_s']=[3,7];add('同地同时相反要求',x,'time_separation_not_established')
x=copy.deepcopy(base);x['demands'][1]['direction']='high';add('非相反方向',x,'not_opposite_demands')
x=copy.deepcopy(base);x['id']='DOC-RELEASE-TEACH-001'
for a in x['demands']:a.update(object='same constructed editable record',parameter='write_permission',unit='boolean')
x['demands'][0]['interval_s']=[0,10];x['demands'][1]['interval_s']=[14,20];x['switch_time_s']=1;add('不同情境文档写权限',x,'time_separation_research_candidate')
for n,mut in [('old-arbitrary-directions',lambda d:[a.update(direction=v)for a,v in zip(d['demands'],['banana','orange'])]),('old-negative-switch',lambda d:d.update(switch_time_s=-100)),('old-reversed-interval',lambda d:d['demands'][0].update(interval_s=[4,0])),('new-bool-time',lambda d:d.update(switch_time_s=True)),('new-nan-interval',lambda d:d['demands'][0].update(interval_s=[0,float('nan')]))]:
 q=copy.deepcopy(base);mut(q)
 try:assess(q);raise AssertionError(n+' accepted')
 except ValueError as e:cases.append({'name':n,'actual':'rejected','reason':str(e),'passed':True})
(P/'教学包/01-输入.json').write_text(json.dumps(base,ensure_ascii=False,indent=2)+'\n')
(P/'教学包/02-条件表与实际检查.json').write_text(json.dumps({'cases':cases,'count':len(cases),'scope':'fixed declared interval checks; not semantic proof or mechanism implementation'},ensure_ascii=False,indent=2)+'\n')
(P/'教学包/03-研究输出.json').write_text(json.dumps({'time_candidate':cases[0]['actual'],'space_candidate':{'idea':'保持区与人工释放界面探索不同位置','status':'unknown','missing':'是否仍为同一受力界面及残能路径'},'relation_candidate':{'idea':'探索不同交互对象的选择响应','status':'unknown','missing':'实际对象和选择机制'},'system_level_candidate':{'idea':'局部保持与系统可释放研究分层','status':'unknown','missing':'功能接管与失效传播'},'not_claimed':'clamp or tapping robot solution; no threshold approved','handoff':['R32 mechanism realization','R38 switching experiments','R41 transitional hazards']},ensure_ascii=False,indent=2)+'\n')
print(len(cases),'checks passed')
