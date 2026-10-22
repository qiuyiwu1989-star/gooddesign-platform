# coding: utf-8
"""051: read-only gold library readiness/depth inventory. Never scores or approves projects.
Only export() writes, and only into the explicitly supplied report directory.
"""
import argparse,hashlib,html,json,re
from collections import Counter
from pathlib import Path
import project_pipeline as pp
import project_ownership as ownership
import research_workflow as rw
import research_assessment as assessment
import research_reader_notes as notes
SCHEMA='gold-benchmark-readiness-1.0'
MODULES=[('identity','项目概况',{'project','award','organization','person'}),('system','需求与系统',{'problem','technology'}),('innovation','设计思路',{'innovation'}),('validation','指标与验证',{'metric','validation'}),('outputs','专利与论文',{'patent','paper','achievement'}),('history','历程与故事',{'event','story'}),('application','应用与价值',{'application'}),('maintenance','质量与维护',{'source','task'})]
GATE_LABELS={'catalog':'题录范围','originals':'原件与归属','machine_readable':'机器可读','published_version':'研究版本','identity':'项目身份','evidence_traceability':'冻结证据','mechanisms_constraints':'机制与约束','validation':'指标与验证','results_relations':'成果与项目关联','reader_documents':'导读与评估','mcp_data_contract':'MCP数据契约','expert_review':'专业审核'}
STATUS_LABELS={'registered_unverified':'题录待核','available':'已有材料','pending_or_missing':'待核或缺失','valid':'版本有效','not_published':'尚未发布','invalid':'检查异常','attention':'需要检查','recorded_needs_semantic_review':'已有记录，待内容复核','incomplete':'仍需补充','traceable':'可追溯','bounded_research_context':'可作有边界的研究上下文','recorded_with_context':'已记录验证条件','inventory_claims_recorded':'已登记清单与关联声明','version_bound':'已绑定研究版','data_available_protocol_not_tested':'数据可读，协议待实测','not_ready':'尚未就绪','not_verified_by_this_tool':'本工具不作专业核定','recorded_needs_content_review':'已记事实，待审深度','ai_only_not_fact_depth':'仅AI解读，事实待补','not_yet_recorded':'尚无事实记录'}
CONFIRMED_RELATIONS={'confirmed_project_result','confirmed_project_adoption','本项目成果已确认','项目实际采用已确认'}
COLLECTION_STATUSES={'queued','running','downloaded','reused_existing','reused_duplicate','failed'}
DRAFT_FILES={'输入快照.json','模型草稿.json','校验结果.json','研究草稿.md'}
DRAFT_STATUSES={'draft_ready_for_review','draft_ready_with_rejections'}
DEFAULT_DRAFTS=pp.ROOT/'output/research-051/deep-drafts'
DEFAULT_OUTPUT=pp.ROOT/'output/research-051/quality'

def _load(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def _hash(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def _known(cell):return isinstance(cell,dict)and cell.get('value_state')=='known'and cell.get('value')is not None
def _value(record,field):
 cell=record.get('cells',{}).get(field,{})
 return cell.get('value')if _known(cell)else None
def _fields(records,entity,fields):
 return [r['id']for r in records if r.get('entity')==entity and all(_value(r,f)is not None for f in fields)]
def _gate(status,basis,missing=None):return dict(status=status,basis=basis,missing=missing or[])
def _relative(root,rel):
 p=(Path(root)/str(rel)).resolve();base=Path(root).resolve()
 if p!=base and base not in p.parents:raise ValueError('路径超出项目目录')
 return p

def _publication(p):
 """Do not recover/advance pointers or call rw.current, even when later folders exist."""
 statefile=p/'研究工作区/工作状态.json'
 if not statefile.exists():return dict(status='not_published',revision=None,data=None,issues=[])
 try:
  w=_load(statefile);n=w.get('revision')
  if type(n)is not int or n<0:raise ValueError('研究版本指针无效')
  if n==0:return dict(status='not_published',revision=None,data=None,issues=[])
  revision='research-%06d'%n;folder,_=rw.check_version(p,revision);data=_load(folder/'档案.json')
  if data.get('project_id')!=p.name or data.get('publication_revision')!=revision:raise ValueError('项目/版本身份不符')
  if not isinstance(data.get('records'),list)or not isinstance(data.get('interpretations',[]),list):raise ValueError('研究数据结构无效')
  if any(not isinstance(r,dict)or not isinstance(r.get('entity'),str)for r in data['records'])or any(not isinstance(x,dict)for x in data.get('interpretations',[])):raise ValueError('记录/AI结构无效')
  ids=[r.get('id')for r in data['records']]
  if any(not isinstance(x,str)or not x for x in ids)or len(ids)!=len(set(ids)):raise ValueError('记录身份无效或重复')
  for r in data['records']:
   if r.get('project_id')not in (None,p.name)or not isinstance(r.get('cells'),dict):raise ValueError('记录越过项目或字段结构无效')
   if any(not isinstance(c,dict)for c in r['cells'].values()):raise ValueError('字段单元结构无效')
  issues=[]
  if n<=128:
   for i in range(1,n):rw.check_version(p,'research-%06d'%i)
  else:issues.append('历史版本超过128，本工具未逐版全检')
  # A later immutable folder does not silently become current in this audit.
  if (p/'研究工作区/版本'/('research-%06d'%(n+1))).exists():issues.append('存在未被当前指针采纳的下一版，需正式工作流恢复确认')
  return dict(status='valid'if not issues else'attention',revision=revision,data=data,dataset_sha256=_hash(folder/'档案.json'),issues=issues)
 except (ValueError,KeyError,TypeError,OSError,json.JSONDecodeError)as exc:
  return dict(status='invalid',revision=None,data=None,issues=[str(exc)[:240]])

def _module_inventory(data):
 records=data.get('records',[])if data else[];ai=data.get('interpretations',[])if data else[];out=[]
 for key,label,entities in MODULES:
  rs=[r for r in records if r.get('entity')in entities];known=[r for r in rs if any(_known(c)for c in r.get('cells',{}).values())]
  out.append(dict(key=key,label=label,known_fact_records=len(known),known_fact_cells=sum(_known(c)for r in rs for c in r.get('cells',{}).values()),ai_items=sum(x.get('entity')in entities for x in ai),state='recorded_needs_content_review'if known else'ai_only_not_fact_depth'if any(x.get('entity')in entities for x in ai)else'not_yet_recorded'))
 return out

def _relation_gate(records,entity):
 rs=[r for r in records if r.get('entity')==entity and any(_known(c)for c in r.get('cells',{}).values())]
 confirmed=[r['id']for r in rs if isinstance(_value(r,'project_relation'),str)and _value(r,'project_relation')in CONFIRMED_RELATIONS and _value(r,'relation_evidence')is not None]
 candidates=[r['id']for r in rs if r['id']not in confirmed]
 return dict(records=len(rs),confirmed_relation_records=confirmed,unconfirmed_relation_records=candidates,status='confirmed_relation_claims_need_evidence_review'if rs and not candidates else'candidate_relations_not_confirmed'if rs else'not_obtained',meaning='同团队、相似技术、已公开专利或论文都不自动证明本项目采用/归属；本工具不判断法律状态。')

def read_draft_status(drafts_root,pid):
 """Manifest integrity only. No draft content is promoted into facts or published versions."""
 pp.valid_id(pid);root=Path(drafts_root)
 try:base=_relative(root,pid)
 except ValueError:return dict(status='invalid',ready=False,manifest_hash_verified=False,issues=['草稿目录越界'],published=False)
 if not base.is_dir():return dict(status='not_available',ready=False,published=False)
 jobs=[];invalid=[]
 for file in sorted(base.glob('*/manifest.json'))[:500]:
  try:
   dest=file.parent;_relative(base,dest.relative_to(base));m=_load(file)
   if m.get('schema')!='gold-deep-draft-1.0'or m.get('project_id')!=pid or m.get('status')not in DRAFT_STATUSES:raise ValueError('草稿身份/状态无效')
   if m.get('expert_reviewed')is not False or m.get('published')is not False:raise ValueError('草稿不能自封专家通过或已发布')
   files=m.get('files')
   if not isinstance(files,dict)or set(files)!=DRAFT_FILES:raise ValueError('草稿清单不完整')
   for name,digest in files.items():
    if not isinstance(digest,str)or not re.fullmatch(r'[0-9a-f]{64}',digest)or _hash(_relative(dest,name))!=digest:raise ValueError('草稿文件指纹不符')
   result=_load(dest/'校验结果.json')
   if not isinstance(result,dict):raise ValueError('草稿校验结果无效')
   def count(key):
    value=result.get(key,[])
    if isinstance(value,list):return len(value)
    if type(value)is int and value>=0:return value
    raise ValueError('草稿候选统计无效')
   jobs.append(dict(job_id=dest.name,status=m['status'],created_at=m.get('created_at'),valid_candidates=count('valid_candidates'),rejected_candidates=count('rejected_candidates')))
  except (ValueError,KeyError,TypeError,OSError,json.JSONDecodeError):invalid.append(dict(job_id=file.parent.name,reason='草稿清单、身份或文件指纹未通过'))
 return dict(status='draft_ready'if jobs else'invalid'if invalid else'not_available',ready=bool(jobs),manifest_hash_verified=bool(jobs),jobs=jobs,invalid_jobs=invalid,published=False,expert_reviewed=False,meaning='仅有可复核草稿及清单指纹，不是事实已审核、研究已发布或MCP正式档案可读')

def audit_project(library,row,benchmark_modules=None,draft_status=None):
 lib=Path(library);pid=pp.valid_id(row['id']);p=_relative(lib,row.get('path',pid))
 if p.name!=pid:raise ValueError('项目目录与ID不一致')
 statefile=p/'数据/管道状态.json';before={f:_hash(f)for f in [statefile,p/'资料归属.json',p/'研究工作区/工作状态.json']if f.is_file()}
 issues=[]
 try:
  state=_load(statefile);sources=state.get('sources',{});reg=ownership.registry(p)
  if state.get('project',{}).get('id')!=pid:raise ValueError('管道状态项目ID不符')
  if not isinstance(sources,dict):raise ValueError('来源结构无效')
 except (ValueError,KeyError,TypeError,OSError,json.JSONDecodeError)as exc:
  sources={};reg={'version':0,'assignments':{},'url_rules':{}};issues.append('资料状态无效：'+str(exc)[:160])
 counts=Counter();originals=[]
 for sid,x in sources.items():
  try:
   if not isinstance(x,dict):raise ValueError('来源元数据无效')
   scope=ownership.assignment(p,sid,sources,reg).get('scope','pending');counts[scope]+=1
   origin=x.get('origin')or{}
   if not isinstance(origin,dict):raise ValueError('来源身份无效')
   kind=origin.get('kind','');legacy=kind=='legacy_archive'or str(origin.get('filename','')).endswith(pid+'.json')
   derived=kind in ('project_source_excerpt','project_json_row');counts['legacy_catalog']+=legacy;counts['derived_selections']+=derived
   if not legacy and not derived:
    exists=_relative(p,x['original']).is_file();counts['original_files_present']+=exists;counts['missing_originals']+=not exists
    if scope=='project'and exists:
     originals.append(sid);counts['project_originals']+=1
     readable=x.get('chunk_count',0)>0 and _relative(p,x['document']).is_file()and _relative(p,x['chunks']).is_file()
     counts['project_machine_readable_originals']+=readable
   counts['needs_ocr_or_conversion']+=x.get('status')in ('needs_ocr','partial_needs_ocr','empty_needs_review','unsupported_needs_conversion','conversion_failed')
  except (ValueError,KeyError,TypeError,OSError):counts['invalid_source_metadata']+=1
 publication=_publication(p);data=publication.get('data')or dict(project_id=pid,records=[],interpretations=[]);records=data['records'];modules=_module_inventory(data)
 evidence=None
 if publication.get('data')is not None:
  try:evidence=assessment.audit(p,data)
  except (ValueError,KeyError,TypeError,OSError,json.JSONDecodeError)as exc:issues.append('冻结证据检查失败：'+str(exc)[:160])
 legacy_known=sum(_known(c)and not c.get('evidence')for r in records for c in r.get('cells',{}).values())
 known=sum(_known(c)for r in records for c in r.get('cells',{}).values());traceable=bool(evidence and evidence['known_cells']>0 and evidence['status']=='traceable')
 project_identity=bool(_fields(records,'project',['canonical_name']));award_identity=bool(_fields(records,'award',['award_name','level']))
 problem=bool(_fields(records,'problem',['pain_point'])or _fields(records,'problem',['goal']));constraints=bool(_fields(records,'problem',['constraints']))
 tech=bool(_fields(records,'technology',['function'])or _fields(records,'technology',['principle']))
 mechanism=bool(_fields(records,'innovation',['mechanism'])or _fields(records,'innovation',['measure']))
 bounded_ai=[x for x in data.get('interpretations',[])if x.get('entity')in ('innovation','technology','problem','application')and x.get('conditions')and x.get('limitations')and x.get('content_nature')in ('ai_interpretation','ai_hypothesis')]
 validation=bool(_fields(records,'validation',['method','result']));validation_context=bool(_fields(records,'validation',['environment']))
 metric_gaps=[]
 for r in records:
  if r.get('entity')!='metric'or _value(r,'value')is None:continue
  cell=r['cells']['value'];missing=[f for f in ('subject','unit','conditions')if _value(r,f)is None and not cell.get({'subject':'object'}.get(f,f))]
  if missing:metric_gaps.append(dict(record_id=r['id'],missing=missing))
 patents=_relation_gate(records,'patent');papers=_relation_gate(records,'paper')
 unconfirmed_relations=len(patents['unconfirmed_relation_records'])+len(papers['unconfirmed_relation_records'])
 complete_list=any(_value(r,'item_list_obtained')is True and _value(r,'count_basis')is not None for r in records if r.get('entity')=='achievement')
 guide=dict(status='not_available');review=dict(status='not_available')
 if publication.get('revision'):
  try:guide=notes.read(p,publication['revision'])
  except (ValueError,KeyError,TypeError,OSError,json.JSONDecodeError):guide=dict(status='invalid')
  try:review=assessment.read(p,publication['revision'])
  except (ValueError,KeyError,TypeError,OSError,json.JSONDecodeError):review=dict(status='invalid')
 gates={
  'catalog':_gate('registered_unverified','原题录范围；年份/奖项对象仍需官方依据'),
  'originals':_gate('available'if counts['project_originals']else'pending_or_missing','项目归属原件库存，存在不等于全文核读',[]if counts['project_originals']else['核对待确认原件归属或补第一手资料']),
  'machine_readable':_gate('available'if counts['project_machine_readable_originals']else'pending_or_missing','机器文本与块文件可用，不代表人工核读'),
  'published_version':_gate(publication['status'],'固定研究版与历史文件指纹检查',publication['issues']),
  'identity':_gate('recorded_needs_semantic_review'if project_identity and award_identity else'incomplete','需项目名称及奖项记录；字面字段存在不代替对象/年份/单位复核',[]if project_identity and award_identity else['补获奖对象、正式名称及奖项出处']),
  'evidence_traceability':_gate('traceable'if traceable else'attention'if known else'not_published','只核原件/块/引用/当前归属，不证明原文真实',([]if traceable else['补冻结引文或修证据/归属链；人工旧引用单列，不伪装新契约通过'])),
  'mechanisms_constraints':_gate('bounded_research_context'if problem and constraints and tech and(mechanism or bounded_ai)else'incomplete','问题/约束/技术事实和有边界机制解读齐备后可供方法研究；不是工程迁移验证',[]if problem and constraints and tech and(mechanism or bounded_ai)else['补需求/工况约束、技术机理与设计取舍；AI与团队真实方法分开']),
  'validation':_gate('recorded_with_context'if validation and validation_context and not metric_gaps else'incomplete','需试验方法/结果/环境，数值指标需对象/单位/工况；公开报道不等于独立重现',[]if validation and validation_context and not metric_gaps else['补原始试验、环境/基线/样本/不确定度；复核指标条件']),
  'results_relations':_gate('inventory_claims_recorded'if complete_list and not unconfirmed_relations else'incomplete','成果清单、项目关联、现权属/法律状态分别核验',[]if complete_list and not unconfirmed_relations else['补成果明细与逐项项目关联；同团队专利/论文不可自动算本项目成果']),
  'reader_documents':_gate('version_bound'if guide['status']=='available'and review['status']=='available'else'incomplete','八模块导读与六维评估须绑定同一发布版，AI评估不代替专家',[]if guide['status']=='available'and review['status']=='available'else['补/修复同研究版的八模块导读与六维评估']),
  'mcp_data_contract':_gate('data_available_protocol_not_tested'if publication['status']=='valid'else'not_ready','本工具只核固定数据契约；实际MCP协议、调用者权限与逐字读取需单独端到端验收'),
  'expert_review':_gate('not_verified_by_this_tool','无独立可核的专家身份、范围和签署记录，本工具不封专业核定；文件expert_reviewed标志也不自动采信')}
 depth_gaps=[]
 if benchmark_modules:
  baseline={x['key']:x for x in benchmark_modules}
  for m in modules:
   ref=baseline[m['key']];m['benchmark_inventory']=dict(known_fact_records=ref['known_fact_records'],known_fact_cells=ref['known_fact_cells'],ai_items=ref['ai_items']);m['comparison_meaning']='库存定位，不是数量竞赛、质量比例或完成率'
   if ref['known_fact_records']and not m['known_fact_records']:depth_gaps.append(m['label']+'尚无已入档事实记录；先补关键事实，不用AI填充代替')
 required=('originals','machine_readable','published_version','identity','evidence_traceability','mechanisms_constraints','validation','results_relations','reader_documents')
 accepted={'available','valid','recorded_needs_semantic_review','traceable','bounded_research_context','recorded_with_context','inventory_claims_recorded','version_bound'}
 benchmark_candidate=all(gates[k]['status']in accepted for k in required)and not issues
 next_actions=[]
 for key in ('originals','identity','published_version','evidence_traceability','mechanisms_constraints','validation','results_relations','reader_documents'):
  g=gates[key]
  if g['status']not in accepted:next_actions.extend(g['missing']or[g['basis']])
 if not next_actions:next_actions=['做独立内容/适用边界评审，并实际走MCP调用验收；不自动专业核定']
 # Dynamic collection modifies source states while the report runs; disclose this, never retry/write.
 concurrent=[str(f.relative_to(p))for f,digest in before.items()if not f.exists()or _hash(f)!=digest]
 if concurrent:issues.append('审计期间以下登记文件变化：'+', '.join(concurrent));benchmark_candidate=False
 legacy_reader=dict(status='not_available')
 if pid=='2025-00'and lib.resolve()==pp.LIB.resolve():
  file=pp.ROOT/'04-知识库/标杆案例/2025-00-嫦娥钻取采样/档案.html'
  if file.is_file():legacy_reader=dict(status='legacy_manual_reader_available',meaning='人工整合阅读页存在；不据此声称新版导读/证据契约已通过')
 draft=draft_status or dict(status='not_checked',meaning='未读取/推断任意草稿文件；草稿不算已发布研究版')
 report=dict(project_id=pid,name=row.get('name',''),catalog_year=row.get('year'),catalog_award=row.get('award'),checked_at=pp.now(),publication_revision=publication.get('revision'),dataset_sha256=publication.get('dataset_sha256'),source_counts=dict(counts),facts=dict(records=len(records),known_cells=known,legacy_or_unfrozen_known_cells=legacy_known),ai_items=len(data.get('interpretations',[])),gates=gates,modules=modules,depth_gaps_to_benchmark=depth_gaps,patents=patents,papers=papers,metric_context_gaps=metric_gaps,reading_guide_status=guide['status'],assessment_status=review['status'],draft=draft,legacy_reader=legacy_reader,statuses=dict(research_readable=publication['status']=='valid'and guide['status']=='available',frozen_evidence_traceable=traceable,bounded_method_context=gates['mechanisms_constraints']['status']=='bounded_research_context',benchmark_candidate=benchmark_candidate,professionally_approved=False),quality_score=None,expert_reviewed=False,concurrent_change_files=concurrent,issues=issues,next_actions=list(dict.fromkeys(next_actions))[:6],reader_url='/dossier/?project='+pid,meaning='分层就绪与库存差距；本工具从不批准质量、专利关系、工程适用性或专家状态。')
 if evidence:
  report['evidence_audit']={k:v for k,v in evidence.items()if k not in ('issues','per_entity')};report['evidence_audit']['issue_count']=len(evidence['issues']);report['evidence_audit']['issue_sample']=evidence['issues'][:12]
 return report

def audit(library=pp.LIB,benchmark_id='2025-00',draft_statuses=None,drafts_root=DEFAULT_DRAFTS):
 library=Path(library);catalog=_load(library/'项目索引.json')['projects'];rows=[x for x in catalog if x.get('award')=='金奖'];ref=next((x for x in rows if x['id']==benchmark_id),None)
 benchmark=audit_project(library,ref)if ref else None;modules=benchmark['modules']if benchmark else None
 projects=[audit_project(library,row,modules,(draft_statuses or{}).get(row['id'])or read_draft_status(drafts_root,row['id']))for row in rows]
 summary=dict(catalog_gold_projects=len(rows),with_published_revision=sum(bool(x['publication_revision'])for x in projects),draft_ready=sum(x['draft'].get('ready')is True and x['draft'].get('manifest_hash_verified')is True for x in projects),research_readable=sum(x['statuses']['research_readable']for x in projects),reader_available_including_legacy=sum(x['statuses']['research_readable']or x['legacy_reader']['status']=='legacy_manual_reader_available'for x in projects),frozen_evidence_traceable=sum(x['statuses']['frozen_evidence_traceable']for x in projects),bounded_method_context=sum(x['statuses']['bounded_method_context']for x in projects),benchmark_candidates=sum(x['statuses']['benchmark_candidate']for x in projects),professionally_approved=0,with_pending_sources=sum(x['source_counts'].get('pending',0)>0 for x in projects),concurrent_change_projects=sum(bool(x['concurrent_change_files'])for x in projects),attention_projects=sum(bool(x['issues'])or any(g['status']in ('invalid','attention')for g in x['gates'].values())for x in projects))
 return dict(schema=SCHEMA,generated_at=pp.now(),summary=summary,benchmark_reference=dict(project_id=benchmark_id,publication_revision=benchmark.get('publication_revision')if benchmark else None,meaning='比较结构深度与读者库存，不预设参考项目已专业核定或符合所有新证据契约'),projects=projects,limitations=['不执行网络请求、模型调用、rw.current、资料恢复、归属修改或事实发布','每项目登记变化会显式标记，动态源数仅为本次读取快照','已保存/机器转换/冻结证据可追溯/内容可信/工程可迁移/专家审核是不同层次','AI草稿与已发布研究版分开；当前工具不提供自动质量总分'])

def export(report,output):
 """Explicit report-only mutation. Caller owns output; never writes library or snapshots."""
 output=Path(output);output.mkdir(parents=True,exist_ok=True);(output/'金奖标杆就绪审计.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 lines=['# 金奖标杆就绪审计','',report['generated_at'],'','本表是结构、证据与阅读就绪检查，不是项目技术评分或专家验收。','',json.dumps(report['summary'],ensure_ascii=False),'','| 项目 | 研究版 | 阅读 | 冻结证据 | 方法上下文 | 标杆候选 | 下一步 |','|---|---|---|---|---|---|---|']
 esc=lambda x:str(x).replace('|','／').replace('\n',' ')
 cards=[];h=lambda x:html.escape(str(x),quote=True)
 for p in report['projects']:
  st=p['statuses'];lines.append('| '+' | '.join(map(esc,[p['project_id']+' '+p['name'],p['publication_revision']or'未发布','可读'if st['research_readable']else'待补','可追溯'if st['frozen_evidence_traceable']else'待核','有边界研究'if st['bounded_method_context']else'待补','候选待内容评审'if st['benchmark_candidate']else'未就绪',p['next_actions'][0]]))+' |')
  gates=''.join('<li><b>'+h(GATE_LABELS[k])+'</b> · '+h(STATUS_LABELS.get(g['status'],g['status']))+'<p>'+h(g['basis'])+'</p></li>'for k,g in p['gates'].items());actions=''.join('<li>'+h(x)+'</li>'for x in p['next_actions']);depth=''.join('<li>'+h(m['label'])+'：事实记录 '+str(m['known_fact_records'])+'；AI '+str(m['ai_items'])+'；'+h(STATUS_LABELS.get(m['state'],m['state']))+'</li>'for m in p['modules'])
  cards.append('<details data-key="'+h(p['project_id']+p['name'])+'"><summary><b>'+h(p['project_id'])+' '+h(p['name'])+'</b><small>'+h(p['publication_revision']or'未发布研究版')+' · '+('研究可读'if st['research_readable']else'人工阅读页可用，新版导读待补'if p['legacy_reader']['status']=='legacy_manual_reader_available'else'阅读待完善')+' · '+('冻结证据可追溯'if st['frozen_evidence_traceable']else'证据/旧引用待核')+'</small></summary><h3>下一步</h3><ul>'+actions+'</ul><h3>八模块内容库存（非质量分）</h3><ul>'+depth+'</ul><h3>分层验收</h3><ul>'+gates+'</ul></details>')
 (output/'金奖标杆就绪审计.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
 page='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>金奖档案 · 标杆就绪与缺口</title><style>body{max-width:1100px;margin:40px auto;padding:0 20px;font:15px/1.7 system-ui;color:#27283c;background:#f7f7fc}details{border:1px solid #e2e3ee;background:white;border-radius:12px;padding:18px;margin:12px 0}summary{cursor:pointer}small{display:block;color:#72768a}input{padding:10px;font:inherit;border:1px solid #ddd;border-radius:8px}li,p{overflow-wrap:anywhere}.stats{padding:16px;background:#eeebff;border-radius:12px}</style><h1>金奖档案：标杆就绪与缺口</h1><p>参考嫦娥的结构深度与阅读体验，逐层看资料、证据、创新机制和应用边界。来源数、字段数、AI草稿都不等同质量。</p><p>'+h(report['generated_at'])+'</p><div class="stats">'+h('金奖题录 '+str(report['summary']['catalog_gold_projects'])+' · 已发布 '+str(report['summary']['with_published_revision'])+' · 阅读入口 '+str(report['summary']['reader_available_including_legacy'])+' · 冻结证据可追溯 '+str(report['summary']['frozen_evidence_traceable'])+' · 标杆候选 '+str(report['summary']['benchmark_candidates']))+'</div><p>当前没有本工具核定的专业审核通过项目；冻结证据检查不替代内容真实性或工程适用性。</p><input id="q" aria-label="搜索项目" placeholder="项目名称或编号">'+''.join(cards)+'<script>document.querySelector("#q").oninput=e=>document.querySelectorAll("details").forEach(d=>d.hidden=!d.dataset.key.includes(e.target.value.trim()))</script></html>'
 (output/'金奖标杆就绪审计.html').write_text(page,encoding='utf-8');return dict(output=str(output),summary=report['summary'])
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--library',type=Path,default=pp.LIB);ap.add_argument('--output',type=Path,default=DEFAULT_OUTPUT);ap.add_argument('--drafts',type=Path,default=DEFAULT_DRAFTS);args=ap.parse_args();print(json.dumps(export(audit(args.library,drafts_root=args.drafts),args.output),ensure_ascii=False,indent=2))
