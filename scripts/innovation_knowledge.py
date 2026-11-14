# coding: utf-8
"""046 read-only, version-bound innovation knowledge projection and literal retrieval.
Co-location in a record is never interpreted as causality. Historical authored
references remain reference-only rather than being upgraded to frozen evidence.
"""
import copy,json,re
from pathlib import Path
import project_pipeline as pp
import research_workflow as rw
import project_ownership as own

SCHEMA='innovation-knowledge-046-1'
FIELDS={
 'problem':{'title','scenario','pain_point','goal','user_group'},
 'constraint':{'constraints','tradeoffs','environment','risks'},
 'choice':{'measure','original_solution','baseline','alternatives','selection_reason'},
 'mechanism':{'mechanism','principle','function','interfaces','components'},
 'verification':{'method','result','conditions','criterion','conclusion'},
 'boundary':{'applicable_conditions','failure_boundary','limitations','scope_included','scope_excluded'}}
LINKS={'problem_id':'addresses_problem','result_metric_ids':'references_metric','evidence_ids':'references_record','technology_ids':'references_technology'}

def _present(c):return c.get('value_state')=='known' and c.get('value') is not None

def _evidence(p,item):
 from research_handoff_check import evidence_nodes
 result=[]
 for e in evidence_nodes(item):
  x=rw.source(p,e['source_id'])
  if x['sha256']!=e['source_sha256'] or pp.sha(pp.safe(p,x['original']).read_bytes())!=e['source_sha256']:raise ValueError('原件指纹或项目归属不符')
  path=pp.safe(p,e['chunks_path'])
  if pp.sha(path.read_bytes())!=e['chunks_sha256']:raise ValueError('冻结文本指纹不符')
  block=next((b for b in pp.load(path) if b['id']==e['chunk_id']),None)
  if not block or not e.get('quote') or e['quote'] not in block['text'] or pp.sha(e['quote'].encode())!=e['quote_sha256']:raise ValueError('坏引用：引文无法定位')
  if x.get('origin',{}).get('kind')=='project_json_row':
   from source_json_row import validate
   validate(p,x)
  if x.get('origin',{}).get('kind')=='project_source_excerpt':
   from source_excerpt import selected_text
   if e['quote'] not in selected_text(p,x):raise ValueError('引文超出选录范围')
  result.append(copy.deepcopy(e))
 return result

def build_index(library,project_id,revision=None):
 """Read one immutable research revision; no disk writes and no LLM calls."""
 p=pp.project(Path(library),project_id);w=rw.current(p)
 revision=revision or 'research-%06d'%w['revision']
 folder,_=rw.check_version(p,revision);d=rw.dataset(p,revision=revision)
 if d.get('project_id')!=project_id:raise ValueError('研究版本项目身份不符')
 ids={r['id'] for r in d['records']};nodes=[];edges=[];gaps=[];source_bindings=[]
 legacy_refs=set();legacy_binding=None
 if project_id=='2025-00':
  f=pp.ROOT/'04-知识库/标杆案例/2025-00-嫦娥钻取采样/档案数据.json'
  legacy_refs={x['id'] for x in pp.load(f)['sources']};legacy_binding=dict(sha256=pp.sha(f.read_bytes()),role='legacy_citation_catalog_not_frozen_evidence')
 for r in d['records']:
  if r.get('project_id',project_id)!=project_id:raise ValueError('记录跨项目')
  if r['entity'] not in ('problem','technology','innovation','validation','application'):continue
  for field,c in r['cells'].items():
   kinds=[kind for kind,fields in FIELDS.items() if field in fields]
   if not kinds:continue
   node_id=r['id']+'.'+field
   if not _present(c):
    gaps.append(dict(record_id=r['id'],field=field,dimensions=kinds,status=c.get('value_state','unknown')));continue
   es=_evidence(p,c);refs=c.get('source_ids',[])
   if not es and refs:
    # Only known legacy citation IDs are allowed; no source text is inferred.
    if not set(refs)<=legacy_refs:raise ValueError('字段引用没有冻结证据或有效旧引用')
   nature=c.get('content_nature','unknown')
   status='source_statement' if nature=='source_statement' else 'ai_interpretation' if nature in ('ai_interpretation','ai_hypothesis','platform_analysis') else 'metadata_or_unclassified'
   nodes.append(dict(id=node_id,project_id=project_id,record_id=r['id'],entity=r['entity'],title=r.get('title',r['id']),field=field,dimensions=kinds,value=c['value'],nature=status,original_nature=nature,evidence_state='frozen_traceable' if es else 'legacy_reference_only' if refs else 'unverified',evidence=es,source_ids=refs,locator=c.get('locator'),conditions=c.get('conditions') or None,limitations=c.get('limitations') or None))
  for field,relation in LINKS.items():
   c=r['cells'].get(field,{})
   if not _present(c):continue
   targets=c['value'] if isinstance(c['value'],list) else [c['value']]
   for target in targets:
    if target not in ids:raise ValueError('关系引用未知记录:'+str(target))
    _evidence(p,c)
    edges.append(dict(source=r['id'],target=target,relation=relation,declared_by=field,status='explicit_record_reference_not_causal_proof'))
 for i in d.get('interpretations',[]):
  es=_evidence(p,i)
  if not es or not i.get('conditions') or not i.get('limitations'):raise ValueError('AI解读缺少可定位依据或边界')
  if i.get('content_nature') not in ('ai_interpretation','ai_hypothesis'):raise ValueError('AI类型无效')
  nodes.append(dict(id='AI.'+i['id'],project_id=project_id,record_id=i['record_id'],entity=i['entity'],title=i.get('title',i['record_id']),field=i['field'],dimensions=['mechanism','boundary'],value=i['value'],nature=i['content_nature'],evidence_state='frozen_traceable',evidence=es,source_ids=[e['source_id'] for e in es],locator=i.get('locator'),conditions=i['conditions'],limitations=i['limitations']))
 if project_id=='2025-00':
  # This declared AI sidecar is separately bound, NOT passed off as research facts.
  from dossier_mechanisms import read_layer
  base=pp.ROOT/'04-知识库/标杆案例/2025-00-嫦娥钻取采样'
  layer=read_layer(base)
  binding=dict(kind='authored_ai_mechanisms_sidecar',file='机制解读.json',sha256=pp.sha((base/'机制解读.json').read_bytes()),basis_archive=layer['basis_archive'],research_revision_membership=False)
  source_bindings.append(binding)
  dimensions={'problem':'problem','tradeoff':'constraint','alternatives':'choice','principle':'mechanism','functional_chain':'mechanism','validation_plan':'verification','conditions':'boundary','boundary':'boundary'}
  for item in layer['items']:
   unit=[]
   for field,dimension in dimensions.items():
    nid='MI.'+item['id']+'.'+field
    nodes.append(dict(id=nid,project_id=project_id,record_id=item['knowledge_id'],entity='ai_mechanism_unit',title=item['title'],field=field,dimensions=[dimension],value=item[field],nature='ai_interpretation',original_nature='ai_interpretation',evidence_state='legacy_reference_only',evidence=[],source_ids=item['source_ids'],locator='机制解读/'+item['id']+'/'+field,conditions=item['conditions'],limitations=item['boundary'],sidecar_binding_sha256=binding['sha256'],validation_status='not_validated',review_status='pending_review'))
    unit.append(nid)
   for source,target in zip(unit,unit[1:]):edges.append(dict(source=source,target=target,relation='ai_explanatory_link',declared_by=item['id'],status='authored_ai_explanation_not_team_decision_or_proven_causality'))
 result=dict(schema=SCHEMA,project_id=project_id,revision=revision,dataset_sha256=pp.sha((folder/'档案.json').read_bytes()),publication_manifest_sha256=pp.sha((folder/'manifest.json').read_bytes()),legacy_citation_binding=legacy_binding,source_bindings=source_bindings,nodes=nodes,edges=edges,gaps=gaps,relationship_policy='only_explicit_record_references; same-record nodes are context, not causality',quality='traceability_not_truth_or_engineering_approval')
 result['index_sha256']=rw.digest(result)
 return result

def validate_index(library,index,require_current=False):
 fresh=build_index(library,index['project_id'],index['revision'])
 if fresh!=index:raise ValueError('索引内容或证据已变动，请重建')
 if require_current:
  p=pp.project(Path(library),index['project_id'])
  if index['revision']!='research-%06d'%rw.current(p)['revision']:raise ValueError('陈旧版本：当前应用需最新研究版')
 return dict(status='passed',project_id=index['project_id'],revision=index['revision'])

def _terms(v):
 if not isinstance(v,list) or len(v)>20 or any(not isinstance(t,str) or not 1<=len(t.strip())<=120 for t in v):raise ValueError('检索项须为最多20条非空短语')
 return [t.strip() for t in v]

def _norm(s):
 """123 匹配归一化：移除 JSON 转义空白序列与全部空白字符，跨行/排版差异不再丢命中。
 对匹配体与查询项施加同一变换，旧命中保持为子串（召回单调不减）；仍为逐字匹配。"""
 for esc in ('\\r\\n','\\n','\\r','\\t'):s=s.replace(esc,'')
 return ''.join(s.split()).casefold()

def search(index,needs=None,functions=None,constraints=None,limit=8):
 """Literal phrase matching with contextual field priority, not similarity scoring.
 A text hit in a source constraint does NOT assert target feasibility.
 """
 if not isinstance(limit,int) or not 1<=limit<=30:raise ValueError('limit须1–30')
 groups={k:_terms(v or []) for k,v in [('needs',needs),('functions',functions),('constraints',constraints)]}
 priority={'needs':['problem','mechanism','choice','verification','boundary','constraint'],'functions':['mechanism','choice','problem','verification','boundary','constraint'],'constraints':['boundary','constraint','verification','mechanism','choice','problem']}
 rows=[];all_terms={(g,t) for g,ts in groups.items() for t in ts};matched=set()
 for n in index['nodes']:
  body=_norm(json.dumps(n['value'],ensure_ascii=False)+' '+str(n.get('conditions') or '')+' '+str(n.get('limitations') or ''))
  hits=[dict(group=g,term=t) for g,ts in groups.items() for t in ts if _norm(t) in body]
  if not hits:continue
  matched.update((h['group'],h['term']) for h in hits)
  rank=min(priority[h['group']].index(k) for h in hits for k in n['dimensions'])
  rows.append(dict(node=copy.deepcopy(n),hits=hits,context_priority=rank,match_reason='输入短语在字段正文/适用前提/限制中命中（空白归一化后的逐字匹配，非相似度评分）',boundary_status='requires_target_validation',relationship_to_target='candidate_analogy_not_proven_transfer'))
 rows.sort(key=lambda r:(r['context_priority'],-len(r['hits']),r['node']['id']))
 return dict(project_id=index['project_id'],revision=index['revision'],index_sha256=index['index_sha256'],query=groups,retrieval_type='literal_phrase_with_explicit_context_priority_not_calibrated_similarity',context_priority=priority,matches=rows[:limit],total_matches=len(rows),unmatched=[dict(group=g,term=t,status='no_literal_evidence_not_proof_of_irrelevance') for g,t in sorted(all_terms-matched)],gaps=index['gaps'],limitations=['仅逐字检索（空白归一化，不扩展同义词），未命中不代表没有相关知识；不会补造关系','来源约束和目标约束必须人工/Agent重新比较，命中不等于相容','历史引用仅保留题录定位，不能与冻结原文核验等同','索引为只读视图，不修改源项目事实或专家评分'])
