#!/usr/bin/env python3
# coding: utf-8
"""Render the authored master document and its bidirectional indexes from one JSON."""
import json,html,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'04-知识库/标杆案例/2025-00-嫦娥钻取采样'
d=json.loads((P/'档案数据.json').read_text());m=json.loads((P/'主档案结构.json').read_text())
e=lambda s:html.escape(str(s if s is not None else '待补'))
S={s['id']:s for s in d['sources']};C={c['id']:c for c in d['claims']};T={t['id']:t for t in m['tag_vocabulary']}
R={r['id']:r for k in ['patents','papers','knowledge','events','stories','tasks'] for r in d[k]}
fields=[f for dim in m['dimensions'] for f in dim['fields']]
assert len({f['id'] for f in fields})==len(fields)
assert len({f['field_key'] for f in fields})==len(fields)
assert len(m['dimensions'])==12
for f in fields:
 assert f['record_id']==m['project_id']+':'+f['id']
 assert f['body'] and f['data_type']
 assert set(f['tags'])<=T.keys()
 assert set(f['claim_ids'])<=C.keys()
 assert set(f['record_refs'])<=R.keys()
 assert all(ev['source_id'] in S and ev['locator'] for ev in f['evidence'])
 if f['gap_id']:
  assert f['value'] is None or f['value_state'] in ['not_found','partial']
  assert f['task_ids'] and f['review_state']=='needs_information'
 elif f['content_nature']=='source_statement':assert f['evidence'], f['id']
assert not d['expert_reviewed']
index=[];reverse={s:[] for s in S}
for dim in m['dimensions']:
 for f in dim['fields']:
  rec=dict(f,dimension_id=dim['id'],dimension_title=dim['title'],path=[m['title'],dim['title'],f['title']],source_ids=list(dict.fromkeys(x['source_id'] for x in f['evidence'])))
  index.append(rec)
  for si in rec['source_ids']:reverse[si].append(f['id'])
(P/'字段索引.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n')
(P/'来源反向索引.json').write_text(json.dumps(reverse,ensure_ascii=False,indent=2)+'\n')
labels={'source_statement':'来源陈述','platform_analysis':'平台解读'}
type_labels={'text':'文字','object':'结构化对象','list':'列表','measurements':'指标表','record_list':'关联条目','timeline':'时间线','tasks':'任务集'}
read={'pdf_text':'PDF名单文字','full_web_text':'网页正文','full_article_text':'论文全文文字','full_pdf_text_and_tables':'全文文字及关键表格核读','abstract_only':'论文摘要','pdf_partial':'专利部分页面','patent_text':'专利文献网页','snippet_only':'仅检索摘要','partial_web_text':'部分网页','search_result_text':'搜索返回片段'}

def button_field(fid,label=None):return f'<button class="text-link" data-field="{e(fid)}">{e(label or fid)}</button>'
def source_link(si):return f'<a class="ref" data-source="{e(si)}" href="#source-{e(si)}">{e(si)}</a>'
def data_render(f):
 typ=f['data_type'];v=f['value']
 if typ=='measurements':
  return '<div class="table-wrap"><table><thead><tr><th>对象</th><th>样品量</th><th>单位</th><th>口径</th></tr></thead><tbody>'+''.join(f'<tr><td>{e(r["version"])}</td><td>{e(r.get("qualifier","")) if r.get("qualifier") else ""}{e(r["value"])}</td><td>{e(r["unit"])}</td><td>{e(f["scope"])}</td></tr>' for r in v)+'</tbody></table></div>'
 if typ=='timeline':
  return '<ol class="timeline">'+''.join(f'<li><time>{e(R[r]["date"])}</time><div><b>{e(R[r]["title"])}</b><p>{e(R[r]["detail"])}</p>{" ".join(source_link(si) for si in R[r]["source_ids"])}</div></li>' for r in v)+'</ol>'
 if typ=='record_list':
  if f['field_key'].endswith('patent_candidates'):
   return '<div class="table-wrap"><table><thead><tr><th>文献</th><th>技术主题</th><th>与项目关系</th></tr></thead><tbody>'+''.join(f'<tr><td><a data-record="{e(r)}" href="#record-{e(r)}">{e(R[r]["publication"])}</a></td><td>{e(R[r]["title"])}</td><td>技术候选，待项目方确认</td></tr>' for r in v)+'</tbody></table></div>'
  return '<ul class="related">'+''.join(f'<li><a data-record="{e(r)}" href="#record-{e(r)}">{e(R[r]["title"])}</a><small>阅读：{e(read.get(R[r].get("read_scope"),"待核"))}</small></li>' for r in v)+'</ul>'
 if typ=='tasks':
  return '<ol class="related">'+''.join(f'<li><b>{e(R[r]["title"])}</b><p>{e(R[r]["acceptance"])}</p><small>{e(R[r]["owner"])} · 尚未派发</small></li>' for r in v)+'</ol>'
 return ''

def render_field(f):
 nature='资料缺口' if f['gap_id'] else labels[f['content_nature']]
 ev='<ul>'+''.join(f'<li>{source_link(x["source_id"])} {e(x["locator"])}'+(f' · <a data-record="{e(x["claim_id"])}" href="#record-{e(x["claim_id"])}">{e(x["claim_id"])}</a>' if x['claim_id'] else '')+'</li>' for x in f['evidence'])+'</ul>' if f['evidence'] else '<p>此项为管理说明或资料缺口，未作为已核实项目事实。</p>'
 tags=''.join(f'<button class="tag" data-tag="{e(t)}">{e(T[t]["label"])}</button>' for t in f['tags'])
 values=''
 if f['data_type'] in ['object','list'] and f['value'] is not None:
  values=f'<details class="typed"><summary>查看结构化值</summary><pre>{e(json.dumps(f["value"],ensure_ascii=False,indent=2))}</pre></details>'
 return f'<article class="field" id="field-{e(f["id"])}" tabindex="-1"><div class="field-heading"><span class="code">{e(f["display_code"])}</span><h3>{e(f["title"])}</h3><span class="nature {"gap" if f["gap_id"] else ""}">{e(nature)}</span></div><p>{e(f["body"])}</p>{data_render(f)}<details class="field-meta"><summary>字段 {e(f["id"])} · 标签与依据</summary><div class="meta-content"><p class="key">{e(f["record_id"])}<br>{e(f["field_key"])}</p><div>{tags}</div>{ev}<p class="small">类型：{e(type_labels.get(f["data_type"],f["data_type"]))} · 口径：{e(f["scope"] or "见正文")} · 单位：{e(f["unit"] or "不适用或见数据项")}</p>{values}</div></details></article>'

chapters=''.join(f'<section class="chapter" id="chapter-{e(dim["id"])}"><div class="chapter-heading"><span>{dim["order"]:02d}</span><h2>{e(dim["title"])}</h2></div><p class="lead">{e(dim["lead"])}</p>'+''.join(render_field(f) for f in dim['fields'])+'</section>' for dim in m['dimensions'])
nav=''.join(f'<a data-chapter="{e(dim["id"])}" href="#chapter-{e(dim["id"])}"><span>{dim["order"]:02d}</span>{e(dim["title"])}</a>' for dim in m['dimensions'])
rows=[]
for f in index:
 searchable=' '.join([f['id'],f['record_id'],f['field_key'],f['dimension_title'],f['title'],f['body'],json.dumps(f['value'],ensure_ascii=False),' '.join(T[t]['label'] for t in f['tags']),' '.join(f['claim_ids']+f['source_ids']),json.dumps([R[r] for r in f['record_refs']],ensure_ascii=False)])
 tags=' '.join(T[t]['label'] for t in f['tags'])
 rows.append(f'<article class="index-row" data-dimension="{e(f["dimension_id"])}" data-tags="{e(" ".join(f["tags"]))}" data-search="{e(searchable.lower())}"><div class="index-path">{e(f["dimension_title"])} / {e(f["display_code"])}</div><h3>{button_field(f["id"],f["title"])}</h3><p>{e(f["body"])}</p><small>{e(f["id"])} · {e(f["field_key"])} · {e("资料缺口" if f["gap_id"] else labels[f["content_nature"]])}</small><p class="tag-text">{e(tags)}</p><div>{button_field(f["id"],"定位正文 →")} {" ".join(source_link(si) for si in f["source_ids"])}</div></article>')
source_rows=[]
for s in d['sources']:
 uses=' '.join(button_field(fid,fid+' '+next(f['title'] for f in fields if f['id']==fid)) for fid in reverse[s['id']]) or '<span class="small">未直接用于正文；保留为背景、选例或后续研究线索。</span>'
 source_rows.append(f'<article class="source-entry" id="source-{e(s["id"])}" tabindex="-1"><div class="code">{e(s["id"])} · {e(read[s["read_scope"]])}</div><h3>{e(s["title"])}</h3><p>{e(s["summary"])}</p><p class="small">定位：{e(s["locator"])}<br>边界：{e(s["limits"] or "按具体陈述判断")}</p><p><a href="{e(s["url"])}" target="_blank" rel="noopener">查看原始资料 ↗</a></p><div class="used-by"><b>被哪些字段引用</b><div>{uses}</div></div></article>')
evidence=[]
for c in d['claims']:
 evidence.append(f'<article class="evidence-entry" id="record-{e(c["id"])}" tabindex="-1"><span class="code">{e(c["id"])}</span><h3>{e(c["value"])}</h3><p>{e(c["note"])}</p><p class="small">原文位置：{e(c["locator"])}</p>{" ".join(source_link(si) for si in c["source_ids"])}</article>')
for p in d['patents']:
 evidence.append(f'<article class="evidence-entry" id="record-{e(p["id"])}" tabindex="-1"><span class="code">{e(p["id"])} · 技术候选</span><h3>{e(p["publication"])} {e(p["title"])}</h3><p>申请号：{e(p["application_number"])}；申请日：{e(p["filing_date"])}。</p><p>{e(p["relationship_evidence"])}</p><p class="small">当前权属、法律状态、同族和型号实施均待核验。</p>{" ".join(source_link(si) for si in p["source_ids"])}</article>')
for p in d['papers']:
 evidence.append(f'<article class="evidence-entry" id="record-{e(p["id"])}" tabindex="-1"><span class="code">{e(p["id"])} · {e(read[p["read_scope"]])}</span><h3>{e(p["title"])}</h3><p>DOI：{e(p["doi"])}</p><p>{" ".join(source_link(si) for si in p["source_ids"])}</p></article>')
from render_structured_case import build as build_structured
atomic_views=build_structured(ROOT,P)
css='''
:root{--paper:#f7f5ef;--ink:#252a23;--muted:#6d7468;--line:#dadfd3;--accent:#526647;--pale:#edf0e7;--gold:#a78145}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;color:var(--ink);background:var(--paper);font:15px/1.95 -apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei',sans-serif}a{color:var(--accent);text-underline-offset:4px}button,input,select{font:inherit;color:inherit}button,a{touch-action:manipulation}button{cursor:pointer}header{max-width:1260px;margin:auto;padding:22px 32px;border-bottom:1px solid var(--line);display:flex;justify-content:space-between;gap:20px}header span{color:var(--muted);font-size:12px}header b{letter-spacing:.1em}.shell{max-width:1260px;margin:auto;display:grid;grid-template-columns:200px minmax(0,1fr);gap:54px;padding:0 32px}.shell.wide{grid-template-columns:minmax(0,1fr)}.shell.wide main{max-width:980px;width:100%;margin-inline:auto}.toc{position:sticky;top:24px;align-self:start;padding-top:46px;max-height:calc(100vh - 30px);overflow:auto}.toc>b{font-size:11px;color:var(--gold)}.toc a{display:block;font-size:12px;color:var(--muted);text-decoration:none;padding:7px 0}.toc a span{margin-right:12px;color:var(--gold)}main{min-width:0}.hero{padding:54px 0 25px}.eyebrow{font-size:11px;letter-spacing:.14em;color:var(--accent)}h1{font:500 clamp(28px,3.8vw,47px)/1.5 'Songti SC',STSong,serif;letter-spacing:-.02em;margin:16px 0 20px}h2{font:500 27px/1.6 'Songti SC',STSong,serif;margin:0}h3{font-size:17px;font-weight:600;line-height:1.7;margin:0}.summary{font-size:17px;line-height:2;max-width:820px}.hero-meta{font-size:12px;color:var(--muted);padding:16px 0;border-top:1px solid var(--line);margin-top:25px}.view-bar{display:flex;gap:8px;flex-wrap:wrap;padding:0 0 25px}.view-bar button,.filter button{border:1px solid var(--line);padding:8px 15px;background:transparent;border-radius:4px;font-size:13px}.view-bar button[aria-pressed=true]{background:var(--accent);color:white;border-color:var(--accent)}.view-bar #print{margin-left:auto}.chapter{border-top:1px solid var(--line);padding:35px 0;scroll-margin-top:24px}.chapter-heading{display:flex;align-items:baseline;gap:20px}.chapter-heading>span,.code{font-size:11px;color:var(--gold)}.lead{font-size:16px;color:#58634f;margin:16px 0 28px;line-height:2}.field{padding:20px 0;border-top:1px solid #e5e8df;scroll-margin-top:25px;outline-offset:6px}.field-heading{display:flex;gap:12px;align-items:baseline;flex-wrap:wrap}.field-heading h3{flex:1;min-width:180px}.field p{margin:12px 0}.nature{font-size:11px;color:var(--muted);white-space:nowrap}.nature.gap{color:#8a6935}.field-meta{font-size:12px;color:var(--muted);margin-top:14px}.field-meta>summary{cursor:pointer;color:var(--accent);padding:4px 0}.meta-content{margin:8px 0;padding:15px;background:#f0f2eb;border-left:2px solid #c2cbb9}.key{overflow-wrap:anywhere;font-family:ui-monospace,monospace;font-size:11px}.ref{display:inline-block;font-size:11px;border:1px solid var(--line);border-radius:3px;text-decoration:none;padding:0 7px;margin:3px 4px 3px 0}.tag{font-size:11px;border:1px solid #ced8c5;padding:2px 8px;color:var(--accent);background:transparent;border-radius:20px;margin:3px 4px 3px 0}.small,small{font-size:12px;color:var(--muted)}.table-wrap{overflow-x:auto;margin:18px 0}table{border-collapse:collapse;width:100%;font-size:13px;text-align:left}th,td{padding:12px 10px;border-bottom:1px solid var(--line);vertical-align:top;min-width:65px}th{color:var(--accent);white-space:nowrap}td{overflow-wrap:anywhere}.timeline{padding:0;list-style:none;margin:24px 0}.timeline li{display:grid;grid-template-columns:110px minmax(0,1fr);gap:15px;border-left:1px solid #bbc7b2;padding:0 0 24px 18px}.timeline time{font-size:12px;color:var(--accent)}.timeline p{font-size:13px;margin:6px 0}.related{padding-left:20px}.related li{padding:8px 0}.related p{font-size:13px}.related small{display:block}.typed pre{font-size:11px;white-space:pre-wrap;overflow-wrap:anywhere}.filter{display:grid;grid-template-columns:1fr 1fr;gap:12px;padding:20px;background:var(--pale);margin:20px 0}.filter label{font-size:12px;display:grid;gap:5px}.filter label:first-child{grid-column:1/-1}.filter input,.filter select{width:100%;min-width:0;padding:10px;background:white;border:1px solid var(--line);border-radius:3px;font-size:13px}.filter button{justify-self:start}#index-status{font-size:12px;color:var(--muted)}.index-row{border-top:1px solid var(--line);padding:22px 0}.index-path{font-size:11px;color:var(--gold)}.index-row h3{margin:6px 0}.index-row p{font-size:14px;margin:8px 0}.text-link{border:0;padding:0;color:var(--accent);text-align:left;background:transparent;font:inherit;text-decoration:underline;text-underline-offset:4px}.tag-text{color:var(--muted);font-size:12px!important}.source-entry,.evidence-entry{padding:24px 0;border-top:1px solid var(--line);scroll-margin-top:20px;overflow-wrap:anywhere}.source-entry p,.evidence-entry p{font-size:14px}.used-by{padding:14px;background:var(--pale);margin-top:16px;font-size:12px}.used-by .text-link{display:inline-block;margin:5px 14px 5px 0}.appendix-block{margin:24px 0}.appendix-block>summary{font-size:20px;cursor:pointer;font-family:'Songti SC',serif}.appendix-block>div{padding-top:15px}.layer-map{font-size:13px;border-left:2px solid var(--gold);padding:12px 16px;background:var(--pale);margin:20px 0}.print-sources{display:none}footer{font-size:12px;color:var(--muted);border-top:1px solid var(--line);padding:26px 0 45px}[hidden]{display:none!important}:focus-visible{outline:3px solid var(--gold);outline-offset:4px}@media(max-width:850px){.shell{display:block;padding:0 22px}header{padding:18px 22px}.toc{position:static;max-height:none;padding:20px 0;display:grid;grid-template-columns:1fr 1fr;gap:0 15px}.toc>b{grid-column:1/-1}.toc a{padding:4px 0;font-size:11px}.hero{padding:25px 0}.summary{font-size:15px}.chapter{padding:28px 0}.chapter-heading{gap:12px}h2{font-size:24px}.field-heading h3{font-size:16px}.field-heading .nature{margin-left:42px}.filter{padding:15px;grid-template-columns:1fr}.filter label:first-child{grid-column:auto}.timeline li{grid-template-columns:82px minmax(0,1fr);padding-left:13px;gap:10px}.view-bar #print{margin-left:0}.view-bar button{padding:7px 11px}th,td{padding:9px 7px;font-size:12px}}@media print{@page{size:A4;margin:17mm}body{background:white;font-size:10pt}header,.toc,.view-bar,.filter,#index-view,#evidence-view{display:none!important}.shell{display:block;padding:0}#document-view{display:block!important}.hero{padding:0 0 20px}h1{font-size:25pt}.summary{font-size:12pt}.chapter{padding:22px 0}h2{font-size:19pt}h3{font-size:12pt}.field{padding:14px 0;break-inside:auto}.field-heading,.field-meta,.table-wrap,.timeline li{break-inside:avoid}.field p,.lead{font-size:10pt}h2,h3{break-after:avoid}.field-meta{font-size:8pt}.print-sources{display:block!important;font-size:8pt;overflow-wrap:anywhere}.print-sources li{padding:5px 0}.field-meta .typed{display:none}.tag{border:0}.source-entry{break-inside:avoid}}
'''
js='''
const views=['structured','document','schema','index','evidence'];
function switchView(name){if(!views.includes(name))name='structured';document.querySelector('.shell').classList.toggle('wide',!['structured','document'].includes(name));views.forEach(v=>document.getElementById(v+'-view').hidden=v!==name);document.querySelectorAll('[data-view]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.view===name)));document.getElementById('toc').hidden=!['structured','document'].includes(name);document.getElementById('toc-structured').hidden=name!=='structured';document.getElementById('toc-document').hidden=name!=='document'}
function locate(view,id,hash=true){switchView(view);const target=document.getElementById(id);if(!target)return;let parent=target.parentElement;while(parent){if(parent.tagName==='DETAILS')parent.open=true;parent=parent.parentElement}if(hash)history.replaceState(null,'','#'+id);target.scrollIntoView({behavior:'instant',block:'start'});target.focus({preventScroll:true})}
function handleHash(){const id=decodeURIComponent(location.hash.slice(1));if(id.startsWith('schema-')){resetSchema();locate('schema',id,false)}else if(id.startsWith('atomic-')||id.startsWith('block-'))locate('structured',id,false);else if(id.startsWith('field-')||id.startsWith('chapter-'))locate('document',id,false);else if(id.startsWith('source-')||id.startsWith('record-'))locate('evidence',id,false)}
document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>{switchView(b.dataset.view);history.replaceState(null,'','#view-'+b.dataset.view);document.getElementById('view-bar').scrollIntoView({behavior:'instant'})}));
document.querySelectorAll('[data-field]').forEach(b=>b.addEventListener('click',()=>locate('document','field-'+b.dataset.field)));
document.querySelectorAll('[data-source]').forEach(a=>a.addEventListener('click',ev=>{ev.preventDefault();locate('evidence','source-'+a.dataset.source)}));
document.querySelectorAll('[data-record]').forEach(a=>a.addEventListener('click',ev=>{ev.preventDefault();locate('evidence','record-'+a.dataset.record)}));
document.querySelectorAll('[data-chapter]').forEach(a=>a.addEventListener('click',ev=>{ev.preventDefault();locate('document','chapter-'+a.dataset.chapter)}));
const q=document.getElementById('index-q'),dim=document.getElementById('index-dimension'),tag=document.getElementById('index-tag'),rows=[...document.querySelectorAll('.index-row')];
function filter(){const text=q.value.trim().toLocaleLowerCase();let count=0;rows.forEach(r=>{const ok=(!text||r.dataset.search.includes(text))&&(dim.value==='all'||r.dataset.dimension===dim.value)&&(tag.value==='all'||r.dataset.tags.split(' ').includes(tag.value));r.hidden=!ok;if(ok)count++});document.getElementById('index-status').textContent=`找到 ${count} / ${rows.length} 个字段。点击字段可返回正文；来源编号可进入证据附录。`;document.getElementById('no-results').hidden=count!==0}
q.addEventListener('input',filter);dim.addEventListener('change',filter);tag.addEventListener('change',filter);document.getElementById('clear-index').addEventListener('click',()=>{q.value='';dim.value='all';tag.value='all';filter()});
document.querySelectorAll('[data-tag]').forEach(b=>b.addEventListener('click',()=>{q.value='';dim.value='all';tag.value=b.dataset.tag;filter();switchView('index');history.replaceState(null,'','#view-index');document.getElementById('index-view').scrollIntoView({behavior:'instant'})}));
window.addEventListener('hashchange',handleHash);filter();
let printState=[];window.addEventListener('beforeprint',()=>{printState=[...document.querySelectorAll('.field-meta')].map(el=>[el,el.open]);printState.forEach(([el])=>el.open=true)});window.addEventListener('afterprint',()=>printState.forEach(([el,open])=>el.open=open));document.getElementById('print').addEventListener('click',()=>window.print());
'''
css+=atomic_views['css']+'\n.toc>div:not([hidden]){display:contents}.toc b{grid-column:1/-1}'
js+=atomic_views['js']+"\nif(location.hash.startsWith('#view-'))switchView(location.hash.slice(6));else if(location.hash)handleHash();else switchView('structured');"
options_dim=''.join(f'<option value="{e(x["id"])}">{x["order"]:02d} {e(x["title"])}</option>' for x in m['dimensions'])
options_tag=''.join(f'<option value="{e(x["id"])}">{e(x["axis"])} / {e(x["label"])}</option>' for x in m['tag_vocabulary'])
print_sources='<section class="print-sources"><h2>来源目录</h2><ol>'+''.join(f'<li>{e(s["id"])} {e(s["title"])} — {e(s["url"])}。读取：{e(read[s["read_scope"]])}。</li>' for s in d['sources'])+'</ol></section>'
page=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>嫦娥钻取采样｜结构化项目档案</title><link rel="icon" href="data:,"><style>{css}</style></head><body><header><b>好设计<span style="color:#a78145">。</span></b><span>结构化项目档案 · 2025-00 · v3.0</span></header><div class="shell"><aside class="toc" id="toc" aria-label="主档案目录"><div id="toc-structured"><b>项目 / 八个数据板块</b>{atomic_views["nav"]}</div><div id="toc-document" hidden><b>项目 / 十二个档案维度</b>{nav}</div></aside><main><div class="hero"><div class="eyebrow">项目全貌 · 设计过程 · 证据索引</div><h1>{e(m['title'])}</h1><p class="summary">{e(m['summary'])}</p><p class="small">摘要为平台整合与解读，依据字段中的来源陈述。</p><div class="hero-meta">2025 第十届好设计奖金奖 · 8 个数据板块 · {atomic_views["count"]} 个原子字段规范 · 公开资料截至 {e(m['research_as_of'])}<br>字段与依据逐项关联；未取得或尚未研究的信息保留明确状态。</div></div><div class="view-bar" id="view-bar" role="group" aria-label="档案阅读方式"><button data-view="structured" aria-pressed="true">分板块档案</button><button data-view="document" aria-pressed="false">完整正文</button><button data-view="schema" aria-pressed="false">研究字段规范</button><button data-view="index" aria-pressed="false">正文标签索引</button><button data-view="evidence" aria-pressed="false">证据与资料附录</button><button id="print">打印 / 保存 PDF</button></div>{atomic_views["board"]}<div id="document-view" hidden>{chapters}{print_sources}</div>{atomic_views["glossary"]}<div id="index-view" hidden><h2>字段与标签索引</h2><div class="layer-map">项目 2025-00 → 档案维度 → 字段（F 编号）→ 事实 / 分析条目 → 来源（S 编号）</div><p class="small">每个字段只有一份正文与结构化值。索引是同一档案的定位入口，可从标签找到相关内容。</p><div class="filter"><label for="index-q">查字段、数值、单位、条目或来源<input type="search" id="index-q" placeholder="例如：260、g、软袋、CN107503698、F020、S02"></label><label for="index-dimension">按档案维度<select id="index-dimension"><option value="all">全部维度</option>{options_dim}</select></label><label for="index-tag">按数据标签<select id="index-tag"><option value="all">全部标签</option>{options_tag}</select></label><button id="clear-index">清除筛选</button></div><p id="index-status" role="status" aria-live="polite"></p><p id="no-results" hidden>没有匹配字段，请调整关键词或清除筛选。</p>{''.join(rows)}</div><div id="evidence-view" hidden><h2>证据与资料附录</h2><p class="lead">正文先完成项目整合，附录保留事实记录、原始出处和使用关系。来源可反向定位引用字段。</p><details class="appendix-block" id="source-appendix" open><summary>资料目录与反向索引 · {len(S)} 份</summary><div>{''.join(source_rows)}</div></details><details class="appendix-block" id="record-appendix"><summary>事实、专利与论文条目 · {len(evidence)} 项</summary><div>{''.join(evidence)}</div></details></div><footer>结构化视图 v3.0 · 主档案正文 v2.0｜基于已登记公开资料整理。<br>专利候选未确认为完整项目清单；项目方和领域专家审核尚待安排。</footer></main></div><script>{js}</script></body></html>'''
(P/'档案.html').write_text(page)
# Markdown is authored structure + evidence references, not an evidence-card concatenation.
md=[f'# {m["title"]}｜标准项目主档案 v2.0\n',m['summary']+'\n',f'研究截止：{m["research_as_of"]}。正文整合完成，资料与专业审核待补。\n','## 档案索引规则\n','层级：项目 → 维度 → 字段 → 事实/分析条目 → 来源。record_id稳定，display_code用于当前章节定位。\n']
for dim in m['dimensions']:
 md += [f'## {dim["order"]:02d} {dim["title"]}\n',dim['lead']+'\n']
 for f in dim['fields']:
  md += [f'### {f["display_code"]} {f["title"]}\n',f['body']+'\n',f'字段：`{f["record_id"]}` · `{f["field_key"]}`；性质：'+('资料缺口' if f['gap_id'] else labels[f['content_nature']])+'。\n','标签：'+'、'.join(T[t]['label'] for t in f['tags'])+'。\n']
  if f['data_type'] in ['measurements','object','list'] and f['value'] is not None:md+=['```json\n'+json.dumps(f['value'],ensure_ascii=False,indent=2)+'\n```\n']
  if f['data_type'] in ['record_list','timeline','tasks']:
   for rid in f['value']:
    rec=R[rid];title=rec.get('title',rid);extra=rec.get('detail',rec.get('acceptance',rec.get('relationship_evidence',rec.get('doi',''))))
    md += [f'- {rid} {rec.get("date",rec.get("publication",""))} **{title}**：{extra}']
  md += [f'- 依据：[{ev["source_id"]}]({S[ev["source_id"]]["url"]})；定位：{ev["locator"]}'+(f'；事实{ev["claim_id"]}' if ev['claim_id'] else '') for ev in f['evidence']]
  md += ['\n']
md += ['## 附录：字段目录\n','| 字段 | 维度 / 名称 | 语义键 |\n|---|---|---|']+[f'| {f["id"]} | {f["dimension_title"]} / {f["title"]} | {f["field_key"]} |' for f in index]
md += ['\n## 附录：来源与反向索引\n']
for s in d['sources']:md += [f'- [{s["id"]} {s["title"]}]({s["url"]})；读取：{read[s["read_scope"]]}；引用字段：'+('、'.join(reverse[s['id']]) or '背景/参照，未直接用于正文')+'。']
(P/'档案.md').write_text('\n'.join(md)+'\n')
report=dict(spec='012',status='pass_structural_self_check',dimensions=len(m['dimensions']),fields=len(fields),tags=len(T),checked=['stable_unique_ids','unique_field_keys','typed_values','claim_record_source_refs','source_locators','gap_task_links','bidirectional_index'],master_sha256=hashlib.sha256((P/'主档案结构.json').read_bytes()).hexdigest(),expert_reviewed=False)
(P/'主档案验收.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))
