# coding: utf-8
"""029: project-native interpretations and independently indexed exploration records."""
import html,json
FIELDS=('problem','principle','functional_chain','alternatives','tradeoff','risks','conditions','boundary','matching_questions','validation_plan')
def read_layer(p):
 from dossier_governance import digest
 layer=json.loads((p/'机制解读.json').read_text());basis=layer['basis_archive']
 frozen=json.loads((p/'版本'/basis['content_version']/'snapshot.json').read_text())
 assert digest(frozen)==basis['snapshot_sha256']
 assert layer['schema_version']=='mechanism-interpretation-1.0' and layer['project_id']=='2025-00'
 d=frozen['evidence'];knowledge={x['id']:x for x in d['knowledge']};claims={x['id']:x for x in d['claims']};sources={x['id']for x in d['sources']}
 rows=layer['items'];assert len({x['id']for x in rows})==len(rows)
 assert {x['knowledge_id']for x in rows}==set(knowledge) and len(rows)==len(knowledge)
 for x in rows:
  assert x['content_type']=='ai_interpretation' and x['review_status']=='pending_review' and x['validation_status']=='not_validated'
  assert x['authored_by'] and x['created_at'] and x['revision']
  assert all(x[f]for f in FIELDS)
  for f in ['functional_chain','risks','conditions','matching_questions','validation_plan']:assert isinstance(x[f],list) and all(isinstance(v,str)and v.strip()for v in x[f])
  k=knowledge[x['knowledge_id']];assert x['claim_ids']==k['claim_ids'] and set(k['source_ids'])<=set(x['source_ids'])
  assert set(x['source_ids'])<=sources
  for cid in x['claim_ids']:assert cid in claims and set(claims[cid]['source_ids'])<=set(x['source_ids'])
 return layer

def read_explorations(p):
 from dossier_reasoning import read_layer as reasoning
 ai=reasoning(p);data=json.loads((p/'关联探索.json').read_text())
 assert data['schema_version']=='related-explorations-1.0' and data['project_id']==ai['project_id']
 rows=data['items'];assert len({x['id']for x in rows})==len(rows)
 assert {x['reasoning_id']for x in rows}=={x['id']for x in ai['items']} and len(rows)==len(ai['items'])
 for x in rows:
  assert x['relationship']=='proposed_transfer' and x['status']=='idea'
  assert x['target_project_id'] is None and x['validation_evidence']==[] and x['review_status']=='pending_review'
 return data

def render(p):
 layer=read_layer(p);explorations=read_explorations(p);e=lambda s:html.escape(str(s));cards=[]
 def list_html(v):return '<ul>'+''.join('<li>'+e(x)+'</li>'for x in v)+'</ul>'
 def paragraph(title,v):return '<div class="mechanism-field"><h4>'+title+'</h4>'+(list_html(v)if isinstance(v,list)else '<p>'+e(v)+'</p>')+'</div>'
 for x in layer['items']:
  flow='<div class="mechanism-flow" aria-label="功能关系">'+''.join('<span>'+e(v)+'</span>'+('<b aria-hidden="true">→</b>'if i<len(x['functional_chain'])-1 else '')for i,v in enumerate(x['functional_chain']))+'</div>'
  refs=''.join('<button class="reader-link" data-reasoning-source="'+e(sid)+'">资料依据 '+e(sid)+' ↗</button>'for sid in x['source_ids'])
  cards.append('<details class="mechanism-unit reader-expand" id="mechanism-'+e(x['knowledge_id'])+'"><summary><span class="ai-label">AI 解读</span><strong>'+e(x['title'])+'</strong><span class="mechanism-status">待专业复核</span></summary><div class="mechanism-body"><p class="reader-note">以下为基于资料的分析。方案比较、风险和验证建议不代表团队真实决策或已完成试验。</p>'+flow+'<div class="mechanism-grid">'+''.join(paragraph(label,x[field])for label,field in [('解决什么问题','problem'),('为什么可能有效','principle'),('可比较的方案','alternatives'),('需要付出的代价','tradeoff'),('可能的风险','risks'),('适用条件','conditions'),('适用边界','boundary'),('匹配前先问','matching_questions'),('建议怎样验证','validation_plan')])+'</div><div class="reasoning-refs">'+refs+'</div><p class="reader-note">'+e(x['knowledge_id'])+' · AI解读修订 '+e(x['revision'])+' · 依据档案 '+e(layer['basis_archive']['content_version'])+'</p></div></details>')
 n=len(cards);complete=sum(all(x[f]for f in FIELDS)for x in layer['items'])
 body='<div class="mechanism-overview"><h3>读懂这个项目的六项设计机制</h3><p>从问题读到原理，再看取舍、边界与验证。点开一个主题深入阅读。</p><span class="ai-label">AI 解读 · 待专业复核</span></div><div class="mechanism-list">'+''.join(cards)+'</div>'
 assessment='<div class="reasoning-accounting"><h3>解读与关联探索</h3><p>机制结构：'+str(complete)+' / '+str(n)+' 项已整理十类内容；这是结构覆盖，不是正确性评分。</p><p>专业复核：0 / '+str(n)+' 项。关联探索：'+str(len(explorations['items']))+' 项设想，已验证迁移：0 项。</p><p>新增解读不增加事实字段填充率或质量自评。验证结果进入独立应用记录，经审核后关联回本项目。</p></div>'
 return dict(body=body,assessment=assessment,count=n,css=CSS)
CSS='''
.mechanism-overview{margin:0 0 24px}.mechanism-overview h3{font-size:20px}.mechanism-overview p{color:var(--muted);font-size:14px;line-height:1.8}.mechanism-unit{border:1px solid var(--line);border-radius:14px;margin:12px 0;background:var(--ui-surface)}.mechanism-unit>summary{display:flex;gap:12px;align-items:center;padding:20px;cursor:pointer;flex-wrap:wrap}.mechanism-unit>summary:after{content:'＋';margin-left:auto;color:var(--accent)}.mechanism-unit[open]>summary:after{content:'−'}.mechanism-unit>summary strong{flex:1;font-size:15px;min-width:180px}.mechanism-status{font-size:11px;color:var(--muted)}.mechanism-body{padding:0 20px 20px}.mechanism-flow{display:flex;gap:10px;align-items:center;margin:20px 0;flex-wrap:wrap}.mechanism-flow span{background:var(--pale);color:var(--accent);padding:8px 12px;border-radius:8px;font-size:12px}.mechanism-flow b{color:var(--muted)}.mechanism-grid{display:grid;grid-template-columns:1fr 1fr;gap:20px 28px}.mechanism-field{border-top:1px solid var(--line);padding-top:14px;min-width:0}.mechanism-field h4{font-size:12px;color:var(--accent);margin:0 0 10px}.mechanism-field p,.mechanism-field li{font-size:13px;color:var(--ink);line-height:1.9}.mechanism-field p{margin:0}.mechanism-field ul{padding-left:18px;margin:0}.exploration-library{margin-top:28px;border:1px solid var(--line);border-radius:12px;padding:16px}.exploration-library>summary{cursor:pointer;font-size:14px;color:var(--accent);min-height:24px}.exploration-library .reasoning-layer{border-top:0;margin-top:0}.mechanism-unit>summary:focus-visible{outline:2px solid var(--accent);outline-offset:3px}@media(max-width:640px){.mechanism-grid{grid-template-columns:1fr}.mechanism-status{display:none}.mechanism-unit>summary{padding:16px;gap:10px}.mechanism-unit>summary strong{min-width:150px}.mechanism-body{padding:0 16px 16px}}@media print{.mechanism-grid{grid-template-columns:1fr 1fr}.mechanism-unit>summary:after{display:none}.mechanism-unit{break-inside:auto}.mechanism-field{break-inside:avoid}}
'''
