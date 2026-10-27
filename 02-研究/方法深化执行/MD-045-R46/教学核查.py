from pathlib import Path
import copy,json,hashlib
P=Path(__file__).resolve().parent
registry=json.loads((P/'教学包/02-来源锁定与筛选.json').read_text());queries=json.loads((P/'教学包/01-实际查询与边界.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base={'scope':'bounded_rubber_tapping_robot_publication_sample','query_ids':['Q01','Q02','Q03','Q04'],'documents':registry['documents'],'FTO_conclusion':None,'legal_clearance':None,'unsearched_is_blank_space':False}
def check(d):
 if d.get('FTO_conclusion')is not None or d.get('legal_clearance')is not None or d.get('unsearched_is_blank_space')is not False:raise ValueError('landscape is not legal clearance or technology absence')
 if d.get('scope')!='bounded_rubber_tapping_robot_publication_sample':return {'status':'outside_executed_search_scope','complete_landscape':False,'FTO':None}
 q=d.get('query_ids')
 if type(q)is not list or not q or not set(q)<={r['id']for r in queries['queries']}:return {'status':'query_material_missing','complete_landscape':False,'FTO':None}
 docs=d.get('documents')
 if type(docs)is not list:raise ValueError('document registry shape')
 if not docs:return {'status':'no_selected_documents_not_no_patents','complete_landscape':False,'FTO':None}
 if len({x['publication']for x in docs})!=len(docs):raise ValueError('duplicate publication')
 allowed={x['publication']:x for x in registry['documents']};groups={};excluded=[]
 for x in docs:
  if x!=allowed.get(x['publication']):raise ValueError('unbound publication or classification/source drift')
  if sha(P/x['raw_path'])!=x['raw_sha256']:raise ValueError('bound primary bytes differ')
  if x['include']:groups.setdefault(x['application'],[]).append(x['publication'])
  else:excluded.append(x['publication'])
 return {'status':'bounded_corpus_trace_only','selected_publications':sum(map(len,groups.values())),'domestic_application_groups':groups,'group_count':len(groups),'excluded_boundary_documents':excluded,'extended_family_count':None,'claim_coverage':None,'legal_status_verified':False,'FTO':None,'technology_gap':None,'complete_landscape':False,'search_recall':None}
cases=[]
def add(n,d,e):
 r=check(d);assert r['status']==e;cases.append({'name':n,'input':d,'actual':r,'passed':True})
add('正常归并A/B不双计发明',base,'bounded_corpus_trace_only');assert cases[-1]['actual']['selected_publications']==3 and cases[-1]['actual']['group_count']==2
x=copy.deepcopy(base);x['query_ids']=[];add('缺检索资料',x,'query_material_missing')
x=copy.deepcopy(base);x['scope']='document_version_management_patents_not_searched';add('另一情境未执行不能硬套',x,'outside_executed_search_scope')
x=copy.deepcopy(base);x['documents']=[];add('零命中不等不存在边界',x,'no_selected_documents_not_no_patents')
for n,mut in [('专利少推自由实施',lambda d:d.update(FTO_conclusion='free_to_operate')),('虚构公开号',lambda d:d['documents'][0].update(publication='CN0000000A')),('同族单据重复',lambda d:d['documents'].append(d['documents'][0])),('把手工刀具换为机器人',lambda d:d['documents'][-1].update(include=True)),('未查官方状态冒有效',lambda d:d['documents'][1].update(legal_status='active_verified'))]:
 x=copy.deepcopy(base);mut(x)
 try:check(x);raise AssertionError(n+' accepted')
 except ValueError as e:cases.append({'name':n,'actual':'rejected','reason':str(e),'passed':True})
(P/'教学包/03-归并实际结果与检查.json').write_text(json.dumps({'cases':cases,'count':len(cases),'scope':'actual small publication sample/trace, no exhaustive landscape/FTO'},ensure_ascii=False,indent=2)+'\n');print(len(cases),'passed')
