from pathlib import Path
import json,copy,hashlib
P=Path(__file__).resolve().parent
def assess(d):
 lock=json.loads((P/'检索来源与未知锁定.json').read_text())
 sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 if sha(P/lock['queries_file'])!=lock['queries_sha256']:raise ValueError('query log artifact changed')
 q=d.get('query_log')
 if type(q)is not list or not q or len(q)!=len(set(q))or not set(q)<=set(lock['allowed_query_ids']):raise ValueError('query ID closure failed')
 source=lock['selected_source']
 if source['query_id']not in q or d.get('source_binding')!=source:raise ValueError('source/query binding mismatch')
 if sha(P/source['raw_path'])!=source['raw_sha256']:raise ValueError('primary bytes changed')
 if d.get('source_locator')!=source['locator']or d.get('evidence_level')!=source['evidence_level']:raise ValueError('source identity or evidence level changed')
 if d.get('target_properties')!=lock['contexts'].get(d.get('id'))or d.get('id')not in lock['contexts']:raise ValueError('target unknown registry changed or unsupported property evidence')
 if not d.get('query_log')or not d.get('source_locator'):return {'status':'missing_search_or_primary_locator'}
 if d['source_function']!=d['generalized_function']:return {'status':'functional_mismatch'}
 if d['evidence_level']not in ['model_only','original_experiment','abstract_only']:raise ValueError('unknown evidence level')
 if not d.get('transfer_differences'):return {'status':'missing_transfer_analysis'}
 if d.get('meets_customer_target')is not None:raise ValueError('no customer target/evidence in this packet')
 unresolved=[k for k,v in d['target_properties'].items()if v is None]
 return {'status':'transfer_research_only','unknown_target_properties':unresolved,'source_evidence':d['evidence_level'],'source_success_not_target_success':True,'ranking':'not_established'}
base={'id':'FOS-LIQUID-TEACH-001','generalized_function':'transport liquid along defined path','source_function':'transport liquid along defined path','source_binding':json.loads((P/'检索来源与未知锁定.json').read_text())['selected_source'],'query_log':['Q01','Q02','Q03'],'source_locator':'Li et al2018 Results/Methods, distilled water and impact conditions','evidence_level':'original_experiment','target_properties':{'viscosity_Pa_s':None,'wetting_contact_angle_deg':None,'required_flow_m3_s':None,'coagulation_time_s':None,'cleaning_acceptance':None},'transfer_differences':['water to uncharacterized field latex','drop impact to continuous collection','clean microstructure to residue exposure','source topography to manufacturable washable surface','source orientation to variable orientation'],'meets_customer_target':None}
cases=[]
def add(n,d,e):
 r=assess(d);assert r['status']==e;cases.append({'name':n,'input':d,'actual':r,'passed':True})
add('正常研究候选未知保持',base,'transfer_research_only')

x=copy.deepcopy(base);x['source_function']='form solid rubber microfluidic device';add('词相似作用不匹配',x,'functional_mismatch')
x=copy.deepcopy(base);x['transfer_differences']=[];add('遗漏迁移差异边界',x,'missing_transfer_analysis')
try:x=copy.deepcopy(base);x['meets_customer_target']=True;assess(x);raise AssertionError('unsupported target accepted')
except ValueError:cases.append({'name':'把原领域成功当客户达标冲突','actual':'rejected','passed':True})
x=copy.deepcopy(base);x['id']='INK-TEACH-001';x['target_properties']={'viscosity_Pa_s':None,'pigment_particles':None,'drying_time_s':None};x['transfer_differences']=['water to unknown pigment ink','source structure to cleanable writing channel'];add('不同情境墨水迁移',x,'transfer_research_only')
for n,mut in [('missing-search',lambda d:d.update(query_log=[])),('old-fictitious-query',lambda d:d.update(query_log=['NO_SUCH_QUERY'])),('old-erased-unknowns',lambda d:d.update(target_properties={})),('old-latex-property-number',lambda d:d['target_properties'].update(viscosity_Pa_s=.1)),('new-missing-single-unknown',lambda d:d['target_properties'].pop('coagulation_time_s')),('new-other-source-id',lambda d:d['source_binding'].update(source_id='H99')),('new-unbound-query-for-source',lambda d:d.update(query_log=['Q01'])),('new-source-hash',lambda d:d['source_binding'].update(raw_sha256='0'*64))]:
 q=copy.deepcopy(base);mut(q)
 try:assess(q);raise AssertionError(n+' accepted')
 except ValueError as e:cases.append({'name':n,'actual':'rejected','reason':str(e),'passed':True})
(P/'教学包/04-实际检查.json').write_text(json.dumps({'cases':cases,'count':len(cases),'scope':'explicit metadata and transfer gating, not autonomous scientific equivalence checker'},ensure_ascii=False,indent=2)+'\n')
print(len(cases),'passed')
