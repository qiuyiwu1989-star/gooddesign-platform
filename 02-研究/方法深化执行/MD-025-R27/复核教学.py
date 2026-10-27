from pathlib import Path
import json,copy
P=Path(__file__).resolve().parent
def assess(d):
 if not d.get('query_log')or not d.get('source_locator'):return {'status':'missing_search_or_primary_locator'}
 if d['source_function']!=d['generalized_function']:return {'status':'functional_mismatch'}
 if d['evidence_level']not in ['model_only','original_experiment','abstract_only']:raise ValueError('unknown evidence level')
 if not d.get('transfer_differences'):return {'status':'missing_transfer_analysis'}
 if d.get('meets_customer_target')is not None:raise ValueError('no customer target/evidence in this packet')
 unresolved=[k for k,v in d['target_properties'].items()if v is None]
 return {'status':'transfer_research_only','unknown_target_properties':unresolved,'source_evidence':d['evidence_level'],'source_success_not_target_success':True,'ranking':'not_established'}
base={'id':'FOS-LIQUID-TEACH-001','generalized_function':'transport liquid along defined path','source_function':'transport liquid along defined path','query_log':['Q01','Q02','Q03'],'source_locator':'Li et al2018 Results/Methods, distilled water and impact conditions','evidence_level':'original_experiment','target_properties':{'viscosity_Pa_s':None,'wetting_contact_angle_deg':None,'required_flow_m3_s':None,'coagulation_time_s':None,'cleaning_acceptance':None},'transfer_differences':['water to uncharacterized field latex','drop impact to continuous collection','clean microstructure to residue exposure','source topography to manufacturable washable surface','source orientation to variable orientation'],'meets_customer_target':None}
cases=[]
def add(n,d,e):
 r=assess(d);assert r['status']==e;cases.append({'name':n,'input':d,'actual':r,'passed':True})
add('正常研究候选未知保持',base,'transfer_research_only')
x=copy.deepcopy(base);x['query_log']=[];add('缺真实检索链',x,'missing_search_or_primary_locator')
x=copy.deepcopy(base);x['source_function']='form solid rubber microfluidic device';add('词相似作用不匹配',x,'functional_mismatch')
x=copy.deepcopy(base);x['transfer_differences']=[];add('遗漏迁移差异边界',x,'missing_transfer_analysis')
try:x=copy.deepcopy(base);x['meets_customer_target']=True;assess(x);raise AssertionError('unsupported target accepted')
except ValueError:cases.append({'name':'把原领域成功当客户达标冲突','actual':'rejected','passed':True})
x=copy.deepcopy(base);x['id']='INK-TEACH-001';x['target_properties']={'viscosity_Pa_s':None,'pigment_particles':None,'drying_time_s':None};x['transfer_differences']=['water to unknown pigment ink','source structure to cleanable writing channel'];add('不同情境墨水迁移',x,'transfer_research_only')
(P/'教学包/04-实际检查.json').write_text(json.dumps({'cases':cases,'count':len(cases),'scope':'explicit metadata and transfer gating, not autonomous scientific equivalence checker'},ensure_ascii=False,indent=2)+'\n')
print(len(cases),'passed')
