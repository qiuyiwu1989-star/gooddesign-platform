from pathlib import Path
import copy,json,math
P=Path(__file__).resolve().parent
base={'id':'R34-SEAL-TEACH-001','origin':'independent_constructed_not_shopfloor','bom':[{'id':'HOUSING','qty':1,'relative_motion':False,'different_material':True,'assembly_disassembly_separate':True},{'id':'SEAL','qty':1,'relative_motion':False,'different_material':True,'assembly_disassembly_separate':True},{'id':'CAP','qty':1,'relative_motion':False,'different_material':False,'assembly_disassembly_separate':True}],'assembly_datum':'declared housing seating face; actual tolerances unknown','actions':[{'id':'A1','action':'orient housing','time_s':4.},{'id':'A2','action':'insert seal and inspect','time_s':4.},{'id':'A3','action':'fit cover','time_s':2.}],'time_origin':'arbitrary teaching numbers, no measured or proprietary DFA tables','service_requires_replaceable_seal':True,'seal_replaceable':True,'cost_components':{'material':None,'process_setup':None,'unit_processing':None,'tooling_amortization':None,'inspection':None,'assembly_labor':None,'service':None,'scrap':None},'production_volume':None}
def calc(d):
 if d['origin']!='independent_constructed_not_shopfloor':raise ValueError('not actual observations')
 if type(d.get('bom'))is not list or not d['bom']:raise ValueError('nonempty BOM required')
 if any(type(b.get('qty'))is not int or b['qty']<=0 for b in d['bom']):raise ValueError('positive nonboolean integer quantity required')
 if any(type(d.get(k))is not bool for k in ['service_requires_replaceable_seal','seal_replaceable']):
  if any(d.get(k)is None for k in ['service_requires_replaceable_seal','seal_replaceable']):return {'status':'unknown_service_constraint','cycle_time_s':None}
  raise ValueError('explicit service booleans required')
 for b in d['bom']:
  if any(type(b.get(k))is not bool for k in ['relative_motion','different_material','assembly_disassembly_separate']):return {'status':'unknown_part_necessity','cycle_time_s':None}
 if d.get('service_requires_replaceable_seal')is None or d.get('seal_replaceable')is None:return {'status':'unknown_service_constraint','cycle_time_s':None}
 if d['service_requires_replaceable_seal']and not d['seal_replaceable']:return {'status':'reject_service_conflict','cycle_time_s':None,'part_count':sum(b['qty']for b in d['bom'])}
 times=[a.get('time_s')for a in d['actions']]
 if any(t is None for t in times):return {'status':'unknown_cycle_time','cycle_time_s':None,'part_count':sum(b['qty']for b in d['bom'])}
 if any(type(t)not in (int,float)or not math.isfinite(t)or t<0 for t in times):raise ValueError('invalid teaching time')
 return {'status':'constructed_action_sum_only','part_count':sum(b['qty']for b in d['bom']),'candidate_consolidation_ids':[b['id']for b in d['bom']if not any(b[k]for k in ['relative_motion','different_material','assembly_disassembly_separate'])],'cycle_time_s':sum(times),'line_takt_time_s':None,'total_cost':None,'engineering_validated':False,'not_included':['parallel work','queues','yield','rework','tool availability','operator fatigue','real cycle observations']}
cases=[]
def add(n,d,e):
 r=calc(d);assert r['status']==e;cases.append({'name':n,'input':d,'actual':r,'passed':True})
add('正常分件服务',base,'constructed_action_sum_only')
x=copy.deepcopy(base);x['actions'][0]['time_s']=None;add('缺动作时长',x,'unknown_cycle_time')
x=copy.deepcopy(base);x['bom'][1]['different_material']=None;add('缺必要性不适用合并判断',x,'unknown_part_necessity')
x=copy.deepcopy(base);x['bom']=x['bom'][:2];x['actions']=[{'id':'B1','action':'orient integrated part','time_s':10.},{'id':'B2','action':'difficult access fasten','time_s':10.}];add('少一件但更慢的边界',x,'constructed_action_sum_only');assert cases[-1]['actual']['cycle_time_s']>cases[0]['actual']['cycle_time_s']
x=copy.deepcopy(base);x['seal_replaceable']=False;x['bom']=x['bom'][:2];add('一体密封不可更换冲突',x,'reject_service_conflict')
x=copy.deepcopy(base);x['id']='ACCESS-COVER-TEACH';x['service_requires_replaceable_seal']=False;x['assembly_datum']='declared document scanner access cover mating face';add('检修盖不同情境',x,'constructed_action_sum_only')
for n,mut in [('old-negative-quantity',lambda d:d['bom'][0].update(qty=-1)),('quantity-zero',lambda d:d['bom'][0].update(qty=0)),('quantity-bool',lambda d:d['bom'][0].update(qty=True)),('quantity-string',lambda d:d['bom'][0].update(qty='2')),('quantity-fraction',lambda d:d['bom'][0].update(qty=1.5)),('old-service-string',lambda d:d.update(service_requires_replaceable_seal='false')),('replaceable-string',lambda d:d.update(seal_replaceable='true')),('time-NaN',lambda d:d['actions'][0].update(time_s=float('nan'))),('time-Inf',lambda d:d['actions'][0].update(time_s=float('inf'))),('time-bool',lambda d:d['actions'][0].update(time_s=True))]:
 q=copy.deepcopy(base);mut(q)
 try:calc(q);raise AssertionError(n+' accepted')
 except ValueError as e:cases.append({'name':n,'actual':'rejected','reason':str(e),'passed':True})
(P/'教学包/01-BOM动作服务输入.json').write_text(json.dumps(base,ensure_ascii=False,indent=2)+'\n');(P/'教学包/02-实际检查与分量成本.json').write_text(json.dumps({'cases':cases,'count':len(cases),'cost_status':'all component costs unknown; no invented unit/lifecycle savings','minimum_part_count_is_not_measured_takt':True},ensure_ascii=False,indent=2)+'\n');print(len(cases),'passed')
