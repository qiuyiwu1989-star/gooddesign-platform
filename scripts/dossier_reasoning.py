# coding: utf-8
"""028: separately versioned AI interpretations, never substituted for factual cells."""
import html,json

def read_layer(p):
 file=p/'AI推演.json'
 if not file.exists():return None
 layer=json.loads(file.read_text())
 from dossier_governance import digest
 basis=layer['basis_archive'];assert basis['content_version']=='0.4.2'
 frozen=json.loads((p/'版本'/basis['content_version']/'snapshot.json').read_text());assert digest(frozen)==basis['snapshot_sha256']
 d=frozen['evidence'];knowledge={x['id']for x in d['knowledge']};claims={x['id']:x for x in d['claims']};sources={x['id']for x in d['sources']}
 assert layer['project_id']=='2025-00' and layer['schema_version']=='ai-reasoning-1.0'
 ids=[x['id']for x in layer['items']];assert len(ids)==len(set(ids))
 for x in layer['items']:
  assert x['module']=='applications' and x['content_type']=='ai_hypothesis'
  assert x['review_status']=='pending_review' and x['validation_status']=='not_validated'
  assert x['confidence'] is None and x['authored_by'] and x['created_at'] and x['revision']
  assert x['knowledge_ids'] and set(x['knowledge_ids'])<=knowledge
  assert x['claim_ids'] and set(x['claim_ids'])<=set(claims)
  assert x['source_ids'] and set(x['source_ids'])<=sources
  for cid in x['claim_ids']:assert set(claims[cid]['source_ids'])<=set(x['source_ids'])
  assert [s['type']for s in x['reasoning_chain']]==['source_basis','analogy','hypothesis']
  for name in ['scenario','value_hypothesis','conditions','boundaries','validation_plan']:assert x[name]
 return layer

def render(p):
 layer=read_layer(p)
 if not layer:return dict(body='',css='',js='',count=0)
 e=lambda x:html.escape(str(x));cards=[]
 for x in layer['items']:
  list_html=lambda rows:'<ul>'+''.join('<li>'+e(r)+'</li>'for r in rows)+'</ul>'
  chain='<ol class="reasoning-chain">'+''.join('<li><span>'+label+'</span><p>'+e(step['text'])+'</p></li>'for label,step in zip(['资料依据','类比思路','应用假设'],x['reasoning_chain']))+'</ol>'
  refs=''.join('<button class="reader-link" data-reasoning-source="'+e(sid)+'">查看依据 '+e(sid)+' ↗</button>'for sid in x['source_ids'])
  cards.append('<article class="reasoning-card" id="reasoning-'+e(x['id'])+'"><div class="reasoning-card-meta"><span class="ai-label">AI推演</span><span>待审核 · 未验证</span></div><h3>'+e(x['title'])+'</h3><p class="reasoning-scenario">'+e(x['scenario'])+'</p><div class="reasoning-value"><b>潜在价值</b><p>'+e(x['value_hypothesis'])+'</p></div><details class="reader-expand reasoning-details"><summary>为什么这样想，怎样验证</summary>'+chain+'<h4>成立的前提</h4>'+list_html(x['conditions'])+'<h4>哪些不能照搬</h4>'+list_html(x['boundaries'])+'<h4>下一步怎样验证</h4>'+list_html(x['validation_plan'])+'<div class="reasoning-refs">'+refs+'</div><p class="reader-note">依据支持原项目的事实与研究；不证明上述应用已经有效。AI推演 · '+e(x['created_at'])+' · 依据档案 '+e(layer['basis_archive']['content_version'])+' · 修订 '+e(x['revision'])+'</p></details></article>')
 body='<section class="reasoning-layer" aria-labelledby="reasoning-heading"><div class="reasoning-heading"><div><span class="ai-label">AI 推理补充</span><h3 id="reasoning-heading">这些经验，还可能用在哪里？</h3></div><button class="reasoning-toggle" id="reasoning-toggle" data-count="'+str(len(layer['items']))+'" type="button" aria-pressed="true" aria-controls="reasoning-cards">显示AI推演</button></div><p class="reasoning-intro"><span id="reasoning-count">'+str(len(cards))+' 条推演 · 均待验证</span>。基于现有档案提出方向，未记为已发生的应用。</p><div class="reasoning-cards" id="reasoning-cards">'+''.join(cards)+'</div><p id="reasoning-hidden-note" class="reader-note" hidden>当前仅查看资料记录。可打开“显示AI推演”探索应用假设。</p></section>'
 return dict(body=body,css=CSS,js=JS,count=len(cards))
CSS='''
.reasoning-layer{margin-top:32px;border-top:1px solid var(--line);padding-top:28px}.reasoning-heading{display:flex;gap:20px;align-items:center;justify-content:space-between}.reasoning-heading h3{font-size:20px;margin:12px 0 0}.ai-label{font-size:11px;font-weight:500;display:inline-flex;align-items:center;gap:6px;color:var(--accent);padding:4px 9px;border:1px solid var(--line);border-radius:999px;background:var(--pale)}.ai-label:before{content:'◇';font-size:12px}.reasoning-toggle{min-height:44px;border:1px solid var(--line);border-radius:999px;padding:8px 16px;background:var(--ui-surface);color:var(--muted);font-size:12px;white-space:nowrap}.reasoning-toggle[aria-pressed=true]{color:var(--accent);border-color:var(--accent);background:var(--pale)}.reasoning-intro{font-size:12px;color:var(--muted);line-height:1.8;margin:16px 0 24px}.reasoning-cards{display:grid;grid-template-columns:1fr 1fr;gap:16px}.reasoning-card{min-width:0;background:var(--ui-soft);border:1px solid var(--line);border-radius:14px;padding:20px}.reasoning-card-meta{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:16px}.reasoning-card-meta>span:last-child{font-size:11px;color:var(--muted)}.reasoning-card h3{font-size:17px;line-height:1.6}.reasoning-scenario{font-size:14px;line-height:1.85;color:var(--ink);margin:12px 0 20px}.reasoning-value{border-left:2px solid var(--accent);padding-left:12px}.reasoning-value b{font-size:12px;font-weight:500;color:var(--accent)}.reasoning-value p{font-size:13px;color:var(--muted);line-height:1.85;margin:8px 0}.reasoning-details{margin:16px 0 0}.reasoning-details summary{font-size:12px;min-height:44px}.reasoning-details h4{font-size:13px;font-weight:600;margin:20px 0 8px}.reasoning-details ul{padding-left:20px;font-size:12px;line-height:1.85;color:var(--muted)}.reasoning-details li{margin:8px 0}.reasoning-chain{list-style:none;padding:0;counter-reset:steps}.reasoning-chain li{border-left:1px solid var(--line);padding-left:16px;margin:16px 0}.reasoning-chain span{font-size:11px;color:var(--accent)}.reasoning-chain p{font-size:13px;line-height:1.85;margin:6px 0}.reasoning-refs{display:flex;gap:12px;flex-wrap:wrap;border-top:1px solid var(--line);margin-top:20px;padding-top:8px}.reasoning-refs button{font-size:11px}.reasoning-accounting{font-size:12px;color:var(--muted);padding:14px 16px;border-radius:12px;background:var(--pale);margin:20px 0}.reasoning-fact-heading{font-size:16px;margin:0 0 16px}.reasoning-unknown-note{font-size:12px;color:var(--muted);margin:16px 0;max-width:680px}@media(max-width:850px){.reasoning-cards{grid-template-columns:1fr}.reasoning-heading{gap:16px;align-items:flex-start}.reasoning-heading h3{font-size:18px}.reasoning-toggle{font-size:11px;padding:8px 12px}.reasoning-card{padding:18px}}@media(max-width:640px){.reasoning-heading{display:grid;grid-template-columns:1fr auto;gap:12px}.reasoning-heading>div{display:contents}.reasoning-heading .ai-label{grid-column:1;grid-row:1;justify-self:start}.reasoning-heading h3{grid-column:1/-1;grid-row:2;margin-top:0}.reasoning-toggle{grid-column:2;grid-row:1}}@media print{.reasoning-toggle{display:none}.reasoning-cards{grid-template-columns:1fr 1fr}.reasoning-card{break-inside:avoid}.ai-label{font-size:8pt}.reasoning-scenario,.reasoning-value p{font-size:9pt}.reasoning-details{font-size:9pt}}
'''
JS='''
const reasoningToggle=document.getElementById('reasoning-toggle');
if(reasoningToggle)reasoningToggle.addEventListener('click',()=>{const show=reasoningToggle.getAttribute('aria-pressed')!=='true';reasoningToggle.setAttribute('aria-pressed',String(show));document.getElementById('reasoning-cards').hidden=!show;document.getElementById('reasoning-hidden-note').hidden=show;document.getElementById('reasoning-count').textContent=show?reasoningToggle.dataset.count+' 条推演 · 均待验证':'AI推演已隐藏'});
document.querySelectorAll('[data-reasoning-source]').forEach(b=>b.addEventListener('click',()=>locate('evidence','source-'+b.dataset.reasoningSource)));
'''
