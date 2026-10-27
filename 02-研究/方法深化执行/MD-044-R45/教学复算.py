from pathlib import Path
import copy,json,math
P=Path(__file__).resolve().parent
base={'id':'R45-LIFE-COST-TEACH-001','origin':'synthetic_cost_units_not_quotes','necessary_functions':['provide controlled action','support maintainable recovery'],'function_quality_status':'assumed_equivalent_for_cost_arithmetic_only','hard_requirements_waived':[],'service_events':5,'alternatives':[{'id':'A','purchase_CU':100.,'user_maintenance_per_event_CU':20.,'function_cost_shares':[.6,.4]},{'id':'B','purchase_CU':80.,'user_maintenance_per_event_CU':30.,'function_cost_shares':[.6,.4]}],'cost_unit':'arbitrary_CU_not_currency_or_real_quote','scope':'undiscounted same service, user burden included; not a validated VE recommendation'}
def calc(d):
 if d.get('origin')!='synthetic_cost_units_not_quotes'or d.get('cost_unit')!='arbitrary_CU_not_currency_or_real_quote':raise ValueError('cost provenance unsupported')
 if d.get('necessary_functions')!=base['necessary_functions']or d.get('hard_requirements_waived')!=[]:raise ValueError('necessary function/hard requirement erased')
 if d.get('function_quality_status')!='assumed_equivalent_for_cost_arithmetic_only':return {'status':'function_quality_not_comparable','value_recommendation':None}
 n=d.get('service_events')
 if type(n)is not int or n<0:raise ValueError('nonnegative integer service count required')
 rows=[]
 for a in d['alternatives']:
  vals=[a.get('purchase_CU'),a.get('user_maintenance_per_event_CU')]
  if any(v is None for v in vals):return {'status':'cost_unknown','value_recommendation':None}
  if any(type(v)not in(int,float)or not math.isfinite(v)or v<0 for v in vals):raise ValueError('invalid costs')
  shares=a.get('function_cost_shares')
  if type(shares)is not list or len(shares)!=2 or any(type(v)not in(int,float)or v<0 for v in shares)or not math.isclose(sum(shares),1):raise ValueError('function allocation not closed')
  total=vals[0]+n*vals[1];rows.append({'id':a['id'],'purchase_function_costs_CU':[vals[0]*s for s in shares],'purchase_CU':vals[0],'user_life_maintenance_CU':n*vals[1],'total_cost_arithmetic_CU':total})
 return {'status':'cost_model_only','rows':rows,'cost_order':[r['id']for r in sorted(rows,key=lambda r:r['total_cost_arithmetic_CU'])],'value_recommendation':None,'why':'equal function/quality only assumed; no real costs or acceptance; no numeric Function/Cost value score'}
cases=[]
def add(n,d,e):
 r=calc(d);assert r['status']==e;cases.append({'name':n,'input':d,'actual':r,'passed':True})
add('正常全寿命成本包含用户负担',base,'cost_model_only');assert cases[-1]['actual']['cost_order']==['A','B']
x=copy.deepcopy(base);x['alternatives'][1]['user_maintenance_per_event_CU']=None;add('缺用户成本不填零',x,'cost_unknown')
x=copy.deepcopy(base);x['function_quality_status']='recovery_function_lost';add('删必要作用不适用价值改善',x,'function_quality_not_comparable')
x=copy.deepcopy(base);x['service_events']=2;add('恰等费用边界',x,'cost_model_only');assert cases[-1]['actual']['rows'][0]['total_cost_arithmetic_CU']==cases[-1]['actual']['rows'][1]['total_cost_arithmetic_CU']
x=copy.deepcopy(base);x['service_events']=1;add('维护频度敏感性反转',x,'cost_model_only');assert cases[-1]['actual']['cost_order']==['B','A']
for n,mut in [('费用分派不守恒',lambda d:d['alternatives'][0].update(function_cost_shares=[1,1])),('偏好豁免硬条件',lambda d:d.update(hard_requirements_waived=['safety'])),('布尔当维护次数',lambda d:d.update(service_events=True))]:
 x=copy.deepcopy(base);mut(x)
 try:calc(x);raise AssertionError(n+' accepted')
 except ValueError as e:cases.append({'name':n,'actual':'rejected','reason':str(e),'passed':True})
x=copy.deepcopy(base);x['id']='DOC-SERVICE-TEACH';x['function_quality_status']='unknown_notification_and_receipt_preserved';add('资料服务另一情境必要作用未知',x,'function_quality_not_comparable')
(P/'教学包/01-功能费用输入.json').write_text(json.dumps(base,ensure_ascii=False,indent=2)+'\n');(P/'教学包/02-实际复算.json').write_text(json.dumps({'cases':cases,'count':len(cases),'cost_shift_counterexample':'purchase80<100 but five user service events make230>200; synthetic only','real_costs':{'quotes':None,'volume':None,'discount_rate':None,'downtime':None,'end_of_life':None},'actual_value_improvement':None},ensure_ascii=False,indent=2)+'\n');print(len(cases),'passed')
