# coding: utf-8
"""Structured sections and field research dictionary for the dossier renderer."""
import json,html,shutil
from pathlib import Path

def build(root,p):
 schema=json.loads((root/'04-知识库/项目档案标准-v1/原子字段字典-v3.json').read_text());data=json.loads((p/'原子字段档案.json').read_text())
 for ext in ['json','csv']:shutil.copyfile(root/f'04-知识库/项目档案标准-v1/原子字段字典-v3.{ext}',p/f'字段规范.{ext}')
 E={en['key']:en for en in schema['entities']};F={f['key']:f for f in schema['fields']};R={r['id']:r for r in data['records']}
 e=lambda v:html.escape(str(v if v is not None else '待补'))
 def sid(key):return 'schema-'+key.replace('.','-')
 def fieldbutton(key):return f'<button class="field-label" data-schema="{e(key)}" title="查看字段定义与研究要求">{e(F[key]["label"])}</button><code class="machine-key">{e(key)}</code>'
 def val(c):
  if c['value'] is None:return '<span class="missing">'+{'not_researched':'待研究','not_obtained':'待取得资料','not_applicable':'不适用','conflicting':'存在冲突'}.get(c['value_state'],'待补')+'</span>'
  v=c['value']
  if isinstance(v,bool):return '是' if v else '否'
  if isinstance(v,list):return '、'.join(e(R[x]['title'] if isinstance(x,str) and x in R else x) for x in v) or '<span class="missing">未登记条目</span>'
  if isinstance(v,dict):return e(json.dumps(v,ensure_ascii=False))
  return e(v)
 def prop(r,name):
  key=r['entity']+'.'+name;c=r['cells'][name]
  refs=' '.join(f'<a data-source="{e(x)}" href="#source-{e(x)}">{e(x)}</a>' for x in c['source_ids'])
  nature={'source_statement':'来源陈述','platform_analysis':'平台分析','platform_metadata':'平台登记'}.get(c['content_nature'],c['content_nature'])
  verification={'source_read_pending_review':'已读取来源，待复核','platform_metadata':'平台登记','pending':'待核验'}.get(c['verification_state'],c['verification_state'])
  proof=f'<details class="cell-proof"><summary>依据与状态</summary><p>{e(nature)} · {e(verification)}<br>{refs}<br>{e(c["locator"])}<br>{e(c.get("derivation",""))}</p></details>' if c['value'] is not None else ''
  return f'<div class="property" id="atomic-{e(r["id"])}-{e(name)}" tabindex="-1"><dt>{fieldbutton(key)}</dt><dd>{val(c)}{proof}</dd></div>'
 def footer(r):
  sources=list(dict.fromkeys(s for c in r['cells'].values() for s in c['source_ids']))
  return '<div class="record-foot">'+''.join(f'<a data-source="{e(s)}" href="#source-{e(s)}">{e(s)}</a>' for s in sources)+''.join(f'<button data-field="{e(fid)}">相关正文 ↗</button>' for fid in r['narrative_refs'][:1])+'</div>'
 def card(r,names,open_detail=False):
  more=[f['name'] for f in E[r['entity']]['fields'] if f['name'] not in names]
  missing=sum(r['cells'][n]['value'] is None for n in more)
  return f'<article class="data-card" id="atomic-record-{e(r["id"])}" tabindex="-1"><div class="card-kicker">{e(E[r["entity"]]["label"])}</div><h3>{e(r["title"])}</h3><dl class="properties">'+''.join(prop(r,n) for n in names)+'</dl>'+(f'<details class="more-fields" {"open" if open_detail else ""}><summary>其余 {len(more)} 个字段 · {missing} 项待补</summary><dl class="properties">'+''.join(prop(r,n) for n in more)+'</dl></details>' if more else '')+footer(r)+'</article>'
 def group(entity):return [r for r in data['records'] if r['entity']==entity]
 def cards(entity,names):return '<div class="data-grid">'+''.join(card(r,names) for r in group(entity))+'</div>'
 def table(entity,cols):
  rows=[]
  for r in group(entity):
   cells=[]
   for k in cols:
    content=val(r['cells'][k])
    if entity=='metric' and k=='value' and r['cells']['qualifier']['value']=='小于':content='&lt;'+content
    if k in ['title','name']:content=f'<a data-atomic-record="{e(r["id"])}" href="#atomic-record-{e(r["id"])}">{content}</a>'
    cells.append('<td>'+content+'</td>')
   rows.append('<tr>'+''.join(cells)+'</tr>')
  return '<div class="table-wrap structured-table"><table><thead><tr>'+''.join('<th>'+fieldbutton(entity+'.'+k)+'</th>' for k in cols)+'</tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>'
 def record_library(entity,names):
  return f'<details class="record-library"><summary>逐条查看{e(E[entity]["label"])}与待补字段 · {len(group(entity))} 条</summary>'+cards(entity,names)+'</details>'
 blocks=[]
 def block(id,num,title,lead,body):blocks.append(f'<section class="structured-block" id="block-{id}" tabindex="-1"><div class="chapter-heading"><span>{num:02d}</span><h2>{title}</h2></div><p class="lead">{lead}</p>{body}</section>')
 block('overview',1,'身份、获奖与团队','获奖记录、机构与人员分别建档，同一个项目可以关联多个年份的奖项和多个完成单位。',cards('award',['year','award_name','edition','level','official_number','completion_org_ids'])+'<h3 class="subhead">完成单位</h3>'+cards('organization',['name_original','project_role','contribution'])+'<h3 class="subhead">公开报道涉及人员</h3>'+cards('person',['name','project_role','award_list_confirmed'])+record_library('project',['project_id','canonical_name']))
 block('technical',2,'需求与技术系统','问题、设计目标、约束、原理、材料和接口各自有字段；未取得的原方案及参数不以分析补齐。',cards('problem',['scenario','goal','constraints','baseline'])+cards('technology',['function','principle','materials','interfaces']))
 block('innovation',3,'创新机制与方法','用“问题—措施—机制—结果—边界”形成可研究的记录。当前机制属于平台分析，尚待专业校准。',cards('innovation',['measure','mechanism','tradeoffs','failure_boundary']))
 block('validation',4,'指标与验证','数值必须同时说明对象、版本、单位和性质。整任务、钻取子系统与地面试验的数据单列。',table('metric',['name','subject','version_id','value','unit','value_kind'])+record_library('metric',['name','value','unit','qualifier','conditions'])+cards('validation',['objective','material_apparatus','control','result','limitations']))
 ip_summary='''<div class="count-grid"><article><h3>专利</h3><div class="count-line"><span><b>50</b>官网披露件数</span><span><b>6</b>本轮技术候选</span><span><b>待确认</b>项目已确认关联</span></div><p>50件未取得完整清单；6条不代表完整项目资产，也不代表型号采用。</p></article><article><h3>论文</h3><div class="count-line"><span><b>60</b>官网披露篇数</span><span><b>3</b>本轮技术文献</span><span><b>1 / 2</b>全文 / 摘要核读</span></div><p>3篇含外部参照，不能直接计为获奖项目已确认论文。统计截止日期仍待补。</p></article></div>'''
 block('ip',5,'专利、论文与成果','披露总量、已找到条目、项目关联和法律状态分别登记，数量口径可以追溯。',ip_summary+'<h3 class="subhead">专利文献目录</h3>'+table('patent',['title','application_number','publication_number','grant_number','project_relation'])+record_library('patent',['application_number','publication_number','grant_number','filing_date','publication_holder','project_relation'])+'<h3 class="subhead">论文目录</h3>'+table('paper',['title','year','venue','doi','reading_scope','project_relation'])+record_library('paper',['authors','year','venue','doi','reading_scope','project_relation'])+record_library('achievement',['kind','count','count_unit','count_basis','statistics_as_of','item_list_obtained']))
 block('history',6,'发展历程与设计故事','研究、承研、任务应用与获奖是不同类型的事件；故事和正式完成人名单也各自保留证据边界。',table('event',['date','title','entity_scope','occurrence'])+record_library('event',['date','date_precision','entity_scope','result'])+cards('story',['narrative','interview_status']))
 block('applications',7,'应用、价值与迁移','先登记已经有来源的历史应用。收益、规模和许可条件分别补证；迁移建议可回到完整正文继续阅读。',cards('application',['scenario','version_id','status','benefit_value','benefit_unit','benefit_basis'])+'<div class="application-links">'+''.join(f'<button data-field="{f}">{label} ↗</button>' for f,label in [('F038','企业迁移机制'),('F039','展馆讲解'),('F040','科技教育'),('F041','远程设备类比')])+'</div>')
 block('governance',8,'证据与持续维护','每个值保留信息状态和出处。未知不是零；资料、审核与项目实际进展分开管理。','<div class="governance-note">20 张来源卡 · 8 项维护任务 · 项目方及专业审核待安排。可从任意来源反查正文。</div>'+record_library('source',['title','publisher','url','reading_scope'])+table('task',['title','priority','status','acceptance'])+record_library('task',['task_type','owner','due_at','reviewer'])+'<div class="download-row"><a href="原子字段档案.json" download>下载本例结构化档案 JSON</a><a href="字段规范.csv" download>下载研究字段 CSV</a></div>')
 # Machine dictionary + actual value examples share the same semantic key.
 uses={f['key']:[] for f in schema['fields']}
 for r in data['records']:
  for name,c in r['cells'].items():uses[r['entity']+'.'+name].append((r,name,c))
 schema_items=[]
 for f in schema['fields']:
  examples=uses[f['key']];known=[(r,n,c) for r,n,c in examples if c['value'] is not None]
  links=' '.join(f'<button class="text-link" data-atomic="{e(r["id"])}-{e(n)}">{e(r["title"])}：{val(c)}</button>' for r,n,c in known[:2])
  if f['key'].startswith('meta.'):links='每个字段值的证据属性保存在结构化档案的值对象中，不重复作为业务字段。'
  if not links:links='<span class="missing">本例尚无已知值；按定义继续调查或记录不适用。</span>'
  text=' '.join([f['key'],f['label'],f['research_question'],f['evidence_requirement']]+[json.dumps(c['value'],ensure_ascii=False) for _,_,c in examples if c['value'] is not None]).lower()
  en=f['key'].split('.')[0]
  schema_items.append(f'<article class="schema-item" id="{sid(f["key"])}" tabindex="-1" data-entity="{e(en)}" data-priority="{f["priority"]}" data-scope="{f["scope"]}" data-text="{e(text)}"><span class="index-path">{e(E[en]["label"] if en in E else "通用证据字段" if en=="meta" else "领域扩展")} · {f["priority"]} · {"通用" if f["scope"]=="common" else "领域扩展"}</span><h3>{e(f["label"])}</h3><code>{e(f["key"])}</code><p><b>研究问题：</b>{e(f["research_question"])}</p><p class="small">数据类型：{e(f["type"])}。{e(f["missing_rule"])}</p><details><summary>证据要求与本例取值</summary><p>{e(f["evidence_requirement"])}</p><div class="schema-examples">{links}</div></details></article>')
 ent_options=''.join(f'<option value="{en["key"]}">{e(en["label"])}</option>' for en in schema['entities'])+'<option value="meta">通用证据字段</option><option value="lunar_sampling">月球采样扩展</option>'
 glossary=f'''<div id="schema-view" hidden><h2>研究字段规范</h2><p class="lead">17 类实体 · {len(schema['fields'])} 个原子字段。对适用实体先调查P0，再按资料条件补充P1；不是要求每个项目填满全部字段。</p><div class="schema-filter"><label>查字段或本例取值<input id="schema-q" type="search" placeholder="年份、申请号、DOI、专利、260…"></label><label>记录类型<select id="schema-entity"><option value="all">全部类型</option>{ent_options}</select></label><label>研究优先级<select id="schema-priority"><option value="all">全部优先级</option><option value="P0">P0 · 适用时必须调查</option><option value="P1">P1 · 补充研究</option></select></label><label>适用范围<select id="schema-scope"><option value="all">全部范围</option><option value="common">通用字段</option><option value="domain_extension">领域扩展</option></select></label><button id="schema-reset">清除筛选</button></div><p id="schema-status" role="status" aria-live="polite"></p><p id="schema-empty" hidden>没有匹配字段，请调整筛选。</p><div class="download-row"><a href="字段规范.csv" download>下载字段字典 CSV</a><a href="字段规范.json" download>下载字段字典 JSON</a></div>{''.join(schema_items)}</div>'''
 nav=''.join(f'<a data-block="{b["id"]}" href="#block-{b["id"]}"><span>{i:02d}</span>{e(b["title"])}</a>' for i,b in enumerate(schema['blocks'],1))
 board='<div id="structured-view"><div class="structured-intro"><p>按板块查看项目数据。点击字段名称可查看研究定义，展开记录可检查缺口与出处。</p><button id="show-keys" aria-pressed="false">显示标准字段名</button></div>'+''.join(blocks)+'</div>'
 css='''
.cell-proof{font-size:11px;color:var(--muted);margin-top:5px}.cell-proof summary{cursor:pointer}.cell-proof p{font-size:11px;overflow-wrap:anywhere}.structured-intro{display:flex;justify-content:space-between;align-items:center;gap:15px;padding:0 0 22px;color:var(--muted);font-size:13px}.structured-intro button,.schema-filter button{border:1px solid var(--line);background:transparent;border-radius:4px;padding:7px 12px;white-space:nowrap;font-size:12px}.structured-block{padding:35px 0;border-top:1px solid var(--line);scroll-margin-top:20px}.data-grid{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin:20px 0}.data-grid>.data-card:only-child{grid-column:1/-1}.data-card{background:#fff;border:1px solid var(--line);border-radius:6px;padding:23px;min-width:0;scroll-margin-top:20px}.card-kicker{font-size:11px;letter-spacing:.1em;color:var(--gold);margin-bottom:8px}.data-card h3{font-size:18px;margin-bottom:15px}.properties{margin:0}.property{border-top:1px solid #e9ece3;padding:11px 0;display:grid;grid-template-columns:minmax(90px,.8fr) minmax(0,1.6fr);gap:15px;scroll-margin-top:25px}.property dt{font-size:12px;color:var(--muted)}.property dd{margin:0;font-size:14px;overflow-wrap:anywhere}.field-label{background:none;border:0;border-bottom:1px dotted #abb8a1;padding:0;text-align:left;color:inherit;font-size:inherit;line-height:1.7}.field-label:hover{color:var(--accent);border-bottom-style:solid}.machine-key{display:none;font:10px/1.6 ui-monospace,monospace;color:var(--muted);overflow-wrap:anywhere;margin-top:4px}.show-field-keys .machine-key{display:block}.missing{color:#949b8c;font-size:12px}.more-fields{font-size:12px;color:var(--muted);margin-top:15px}.more-fields summary{cursor:pointer;padding:7px 0}.more-fields .properties{margin-top:10px}.record-foot{margin-top:14px;padding-top:12px;border-top:1px solid var(--line);font-size:11px;display:flex;gap:10px;flex-wrap:wrap}.record-foot button{border:0;background:none;color:var(--accent);padding:0;font-size:11px}.subhead{margin:28px 0 10px}.record-library{margin:20px 0;font-size:13px}.record-library>summary{padding:12px 0;cursor:pointer;color:var(--accent);border-bottom:1px solid var(--line)}.structured-table table{font-size:12px}.structured-table td{min-width:95px}.structured-table td:first-child{min-width:180px}.structured-table th{white-space:normal;min-width:100px}.count-grid{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin:22px 0}.count-grid article{padding:22px;background:var(--pale);border-top:2px solid var(--accent)}.count-grid h3{font-size:20px}.count-line{display:flex;gap:20px;margin:15px 0}.count-line span{flex:1;font-size:11px;color:var(--muted)}.count-line b{display:block;font:28px/1.7 Georgia,'Songti SC',serif;color:var(--accent)}.count-grid p{font-size:12px;color:var(--muted)}.schema-filter{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;background:var(--pale);padding:20px;margin:20px 0}.schema-filter label{font-size:12px;display:grid;gap:6px}.schema-filter label:first-child{grid-column:1/-1}.schema-filter input,.schema-filter select{font:inherit;background:white;padding:10px;min-width:0;width:100%;border:1px solid var(--line);border-radius:3px}.schema-filter button{justify-self:start}#schema-status{font-size:12px;color:var(--muted)}.schema-item{border-top:1px solid var(--line);padding:22px 0;scroll-margin-top:25px;overflow-wrap:anywhere}.schema-item h3{margin:6px 0}.schema-item>code{font-size:11px;color:var(--muted)}.schema-item p{font-size:14px;margin:10px 0}.schema-item details{font-size:12px;color:var(--muted)}.schema-examples .text-link{display:block;margin:8px 0;overflow-wrap:anywhere}.download-row,.application-links{display:flex;gap:16px;flex-wrap:wrap;padding:16px 0;font-size:12px}.application-links button{background:var(--pale);border:1px solid var(--line);padding:10px 14px;color:var(--accent);border-radius:4px}.governance-note{padding:16px;background:var(--pale);font-size:13px;margin:20px 0}@media(max-width:850px){.data-grid,.count-grid{grid-template-columns:1fr}.data-card{padding:18px}.count-line{gap:12px}.schema-filter{grid-template-columns:1fr}.schema-filter label:first-child{grid-column:auto}.structured-intro{align-items:flex-start;flex-direction:column}.property{grid-template-columns:minmax(85px,.8fr) minmax(0,1.4fr);gap:10px}.view-bar{gap:7px}.view-bar button{font-size:12px}}@media print{#structured-view,#schema-view{display:none!important}}
'''
 js='''
const schemaQ=document.getElementById('schema-q'),schemaEntity=document.getElementById('schema-entity'),schemaPriority=document.getElementById('schema-priority'),schemaScope=document.getElementById('schema-scope'),schemaItems=[...document.querySelectorAll('.schema-item')];
function filterSchema(){let n=0;const q=schemaQ.value.trim().toLocaleLowerCase();schemaItems.forEach(el=>{const ok=(!q||el.dataset.text.includes(q))&&(schemaEntity.value==='all'||el.dataset.entity===schemaEntity.value)&&(schemaPriority.value==='all'||el.dataset.priority===schemaPriority.value)&&(schemaScope.value==='all'||el.dataset.scope===schemaScope.value);el.hidden=!ok;if(ok)n++});document.getElementById('schema-status').textContent=`显示 ${n} / ${schemaItems.length} 个字段；字段名可用于其他项目。`;document.getElementById('schema-empty').hidden=n!==0}
function resetSchema(){schemaQ.value='';schemaEntity.value='all';schemaPriority.value='all';schemaScope.value='all';filterSchema()}
[schemaQ,schemaEntity,schemaPriority,schemaScope].forEach(el=>el.addEventListener(el===schemaQ?'input':'change',filterSchema));document.getElementById('schema-reset').addEventListener('click',resetSchema);
document.querySelectorAll('[data-schema]').forEach(b=>b.addEventListener('click',()=>{resetSchema();locate('schema','schema-'+b.dataset.schema.replaceAll('.','-'))}));
document.querySelectorAll('[data-atomic]').forEach(b=>b.addEventListener('click',()=>locate('structured','atomic-'+b.dataset.atomic)));
document.querySelectorAll('[data-atomic-record]').forEach(a=>a.addEventListener('click',ev=>{ev.preventDefault();locate('structured','atomic-record-'+a.dataset.atomicRecord)}));
document.querySelectorAll('[data-block]').forEach(a=>a.addEventListener('click',ev=>{ev.preventDefault();locate('structured','block-'+a.dataset.block)}));
document.getElementById('show-keys').addEventListener('click',ev=>{const on=document.body.classList.toggle('show-field-keys');ev.target.setAttribute('aria-pressed',String(on));ev.target.textContent=on?'隐藏标准字段名':'显示标准字段名'});filterSchema();
'''
 return dict(board=board,glossary=glossary,nav=nav,css=css,js=js,count=len(schema['fields']))
