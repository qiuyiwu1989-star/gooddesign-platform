from pathlib import Path
import copy,json,math
P=Path(__file__).resolve().parent
FU={'service':'provide same hypothetical fixture function','duration_years':10.,'work_cycles':100000,'performance_equivalence':'assumed_only_for_separate_teaching_math'}
BOUND=['production','transport','use','repair','end_of_life']
base={'id':'R43-REPLACE-TEACH-001','origin':'synthetic_burden_units_not_emission_database','functional_unit':FU,'boundary':BOUND,'allocation':'no_coproduct_in_constructed_model','impact_unit':'arbitrary_BU_not_kgCO2e','alternatives':[{'id':'A','functional_unit':FU,'boundary':BOUND,'service_life_years':5.,'per_device_production_BU':100.,'total_service_other_BU':{'transport':0.,'use':0.,'repair':0.,'end_of_life':0.}},{'id':'B','functional_unit':FU,'boundary':BOUND,'service_life_years':2.,'per_device_production_BU':60.,'total_service_other_BU':{'transport':0.,'use':0.,'repair':0.,'end_of_life':0.}}],'numbers':'arbitrary arithmetic counterexample, zero other burdens are explicit toy assumptions, not missing field data'}
def calc(d):
 if d.get('origin')!='synthetic_burden_units_not_emission_database'or d.get('impact_unit')!='arbitrary_BU_not_kgCO2e':raise ValueError('no measured environmental claim')
 if d.get('boundary')!=BOUND or d.get('functional_unit')!=FU:return {'status':'goal_boundary_not_comparable','ranking':None}
 rows=[]
 for a in d['alternatives']:
  if a.get('functional_unit')!=FU or a.get('boundary')!=BOUND:return {'status':'goal_boundary_not_comparable','ranking':None}
  life=a.get('service_life_years');prod=a.get('per_device_production_BU');other=a.get('total_service_other_BU')
  if life is None or prod is None or type(other)is not dict or set(other)!=set(BOUND)-{'production'}or any(v is None for v in other.values()):return {'status':'inventory_unknown','ranking':None}
  if any(type(v)not in(int,float)or not math.isfinite(v)or v<0 for v in [life,prod,*other.values()])or life==0:raise ValueError('invalid lifecycle quantities')
  units=math.ceil(FU['duration_years']/life);rows.append({'id':a['id'],'whole_devices_for_service':units,'production_for_FU_BU':units*prod,'other_for_FU_BU':sum(other.values()),'total_constructed_BU':units*prod+sum(other.values())})
 return {'status':'synthetic_boundary_calculation_only','rows':rows,'arithmetic_rank':[r['id']for r in sorted(rows,key=lambda r:r['total_constructed_BU'])],'real_environmental_ranking':None,'climate_benefit_kgCO2e':None,'not_ISO_LCA_compliance':True}
cases=[]
def add(n,d,e):
 r=calc(d);assert r['status']==e;cases.append({'name':n,'input':d,'actual':r,'passed':True})
add('全服务替换反转只看机身结论',base,'synthetic_boundary_calculation_only');assert cases[-1]['actual']['arithmetic_rank']==['A','B']
x=copy.deepcopy(base);x['alternatives'][1]['service_life_years']=5.;add('寿命敏感性反转',x,'synthetic_boundary_calculation_only');assert cases[-1]['actual']['arithmetic_rank']==['B','A']
x=copy.deepcopy(base);x['alternatives'][1]['total_service_other_BU']['use']=None;add('缺使用清单不能零填',x,'inventory_unknown')
x=copy.deepcopy(base);x['alternatives'][1]['functional_unit']={**FU,'work_cycles':1000};add('服务不同不适用',x,'goal_boundary_not_comparable')
x=copy.deepcopy(base);x['alternatives'][0]['service_life_years']=10.;add('恰一台边界',x,'synthetic_boundary_calculation_only');assert cases[-1]['actual']['rows'][0]['whole_devices_for_service']==1
x=copy.deepcopy(base);x['alternatives'][1]['boundary']=['production'];add('删边界冲突',x,'goal_boundary_not_comparable')
x=copy.deepcopy(base);x['id']='DISPLAY-REPLACE-TEACH';x['alternatives'][1]['service_life_years']=None;add('展示支架另一情境寿命未知',x,'inventory_unknown')
(P/'教学包/01-独立功能单位构造输入.json').write_text(json.dumps(base,ensure_ascii=False,indent=2)+'\n');(P/'教学包/02-实际复算.json').write_text(json.dumps({'cases':cases,'count':len(cases)},ensure_ascii=False,indent=2)+'\n')
(P/'教学包/03-真实项目数据缺口.json').write_text(json.dumps({'actual_project_functional_unit':'not_customer_defined','real_inventory':{p:None for p in BOUND},'data_quality':{'geography':None,'time':None,'technology':None,'completeness':None,'measurement_source':None},'impact_categories':['climate','resource use','toxicity and other relevant categories not selected'], 'characterization_method':None,'allocation_rules':None,'review_required_for_public_comparison':'not_performed','environmental_improvement_claim':None,'critical_difference':'toy BU arithmetic cannot be imported as actual carbon or full LCA result'},ensure_ascii=False,indent=2)+'\n')
print(len(cases),'passed')
