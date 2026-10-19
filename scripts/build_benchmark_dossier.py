#!/usr/bin/env python3
# coding: utf-8
"""Build an offline research dossier; never changes production original-app/."""
import json, html, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'04-知识库/标杆案例/2025-00-嫦娥钻取采样'
DATA=OUT/'档案数据.json'
d=json.loads(DATA.read_text())
esc=lambda x:html.escape(str(x or '待补充'))
read_labels={'pdf_text':'PDF名单文字','full_web_text':'网页正文','full_article_text':'论文全文文字','abstract_only':'论文摘要','pdf_partial':'专利部分页面','patent_text':'专利文献网页','snippet_only':'仅检索摘要','partial_web_text':'部分网页','search_result_text':'搜索返回片段'}
scope_labels={'project':'获奖项目','technical_lineage':'技术路线研究','CE5_drilling':'嫦娥五号钻取子系统','CE6_drilling':'嫦娥六号钻取子系统','CE5_mission_context':'嫦娥五号整任务背景','CE6_mission_context':'嫦娥六号整任务背景','ground_research':'地面研究试验','CE6_ground_support':'嫦娥六号地面支持','CE6_softbag':'嫦娥六号取芯软袋','team_history':'团队前期研究','patent_publication':'专利公开文本当时记录','reported_team':'报道涉及团队','award_project':'获奖项目','mission_context':'整任务背景','research':'研究论文'}
relation_labels={'direct_technical_relation_not_award_list_confirmed':'技术直接相关，未由获奖成果清单确认','external_technical_reference':'外部技术参照，不计为项目论文成果','task_related_not_award_list_confirmed':'任务相关，获奖项目归属待确认'}
sources={s['id']:s for s in d['sources']}
claims={c['id']:c for c in d['claims']}
knowledge={k['id']:k for k in d['knowledge']}
all_records=sum((d[k] for k in ['sources','claims','patents','knowledge','events','papers','stories','gaps','tasks']),[])
ids=[v['id'] for v in all_records]
assert len(ids)==len(set(ids)), 'Duplicate record IDs'
for rec in all_records:
 for s in rec.get('source_ids',[]):assert s in sources,(rec['id'],s)
 for c in rec.get('claim_ids',[]):assert c in claims,(rec['id'],c)
 for k in rec.get('mechanism_ids',[]):assert k in knowledge,(rec['id'],k)
for t in d['tasks']:assert t['gap_id'] in {g['id'] for g in d['gaps']}
for c in d['claims']:assert c['source_ids'] and c['locator'] and c['expert_reviewed'] is False
for p in d['patents']:
 assert p['current_legal_status']=='not_officially_verified'
 assert p['association_review']=='pending_project_team_confirmation'
assert d['expert_reviewed'] is False and d['depth']=='D2_candidate'
logs=json.loads((OUT/'研究日志.json').read_text())
for log in logs:
 for s in log['source_ids']:assert s in sources
for s in sources.values():assert (OUT/'来源卡'/f"{s['id']}.md").is_file()

def refs(keys):
 return ' '.join(f'<a class="ref" href="#source-{esc(i)}">{esc(i)}</a>' for i in keys)
def card(kind,id,title,body,badge=''):
 return f'<article class="record" data-kind="{kind}" id="{esc(id)}"><div class="meta">{esc(id)} · {esc(badge)}</div><h3>{esc(title)}</h3>{body}</article>'
def para(t,cls=''):return f'<p class="{cls}">{esc(t)}</p>'
def section(id,num,title,intro,body):
 return f'<section id="{id}"><div class="section-head"><span>{num}</span><h2>{title}</h2></div><p class="intro">{intro}</p>{body}</section>'

facts=''.join(card('fact',c['id'],c['value'],para('范围：'+scope_labels.get(c['scope'],c['scope']))+para('定位：'+c['locator'],'small')+para(c['note'],'small')+refs(c['source_ids']),'来源陈述 · 未经专家审核') for c in d['claims'])
ks=''.join(card('knowledge',k['id'],k['title'],''.join(para(label+'：'+k[key]) for label,key in [('问题','problem'),('设计措施','measure'),('机制解读','mechanism'),('取舍','tradeoffs'),('迁移机会','transfer'),('适用边界','boundary'),('验证建议','validation')])+refs(k['source_ids']),'平台分析 · 迁移尚待验证') for k in d['knowledge'])
stories=''.join(card('knowledge',s['id'],s['title'],para(s['narrative'])+para(s['limit'],'small')+refs(s['source_ids']),'报道梳理与平台解读') for s in d['stories'])
ps=''.join(card('patent',p['id'],p['publication']+' · '+p['title'],para('申请号：'+p['application_number']+'｜申请日：'+p['filing_date'])+para('授权公告日：'+(p['grant_publication_date'] or '本轮未核实授权文献'))+para('关系判断：'+p['relationship_evidence'])+para('已核读：'+p['reading_level'],'small')+para('公开文本当时中文权利人：'+(p['publication_holder_zh'] or '待原始中文著录核验'),'small')+para('当前法律状态、权属、同族：待官方核验。是否用于飞行型号：待项目方确认。','small')+refs(p['source_ids'])+(f'<a class="ref" href="{esc(p["official_publication_url"])}" target="_blank" rel="noopener">原始公开文本</a>' if p['official_publication_url'] else ''),'技术候选 · 非项目已确认清单') for p in d['patents'])
papers=''.join(card('patent',p['id'],p['title'],para('DOI：'+p['doi'])+para('作者：'+'、'.join(p['authors']))+para('阅读范围：'+read_labels.get(p['read_scope'],p['read_scope'])+'；归属：'+relation_labels.get(p['relation'],p['relation']),'small')+refs(p['source_ids']),'论文线索') for p in d['papers'])
events=''.join(card('event',e['id'],e['date']+' · '+e['title'],para(e['detail'])+para('时间精度：'+e['date_precision']+'；范围：'+scope_labels.get(e['scope'],e['scope']),'small')+refs(e['source_ids']),'有来源事件') for e in d['events'])
ss=''.join(card('source','source-'+s['id'],s['title'],para(s['summary'])+para('类型：'+s['type']+'｜读取：'+read_labels.get(s['read_scope'],s['read_scope']),'small')+para('定位：'+s['locator'],'small')+para('发布日期：'+(s['published_at'] or '未核实')+'｜本轮访问：'+s['accessed_at'],'small')+para(s['limits'] or '按具体断言判断证据支持范围。','small')+f'<a href="{esc(s["url"])}" target="_blank" rel="noopener">{esc(s["id"])} · 查看原始来源 ↗</a>','原始出处与研究摘要') for s in d['sources'])
tasks=''.join(card('task',t['id'],t['title'],para('下一步：'+t['acceptance'])+para('优先级：'+t['priority']+'｜'+t['owner']+'｜尚未派发','small'),'缺口任务 · 待安排') for t in d['tasks'])
module_rows=[('身份与奖项','已核读','S01正式编号与完成单位'),('人物与组织','部分','报道角色可追溯，完整完成人及分工待确认'),('背景与需求','已形成','约束与研究对象明确'),('技术与设计','部分','原理与公开技术可读，工程指标表待补'),('创新机制','分析稿','4条有来源的平台分析，待专家校准'),('知识产权','候选池','6条专利候选、3篇论文；完整清单未取得'),('发展历程','首版','10个有来源节点，区分团队/任务/获奖对象'),('验证与应用','部分','模拟试验与任务应用分开；原始工况待补'),('人物故事','报道梳理','2条故事主题，未开展访谈'),('产业迁移','建议','迁移机会与最小验证，尚无合作或收益证据'),('资料与素材','已登记','20张来源卡；未取得图片再发布授权'),('维护与治理','待协作','8项任务，责任人待指定，尚未建立自动监测')]
coverage='<div class="table-wrap"><table><thead><tr><th>档案模块</th><th>状态</th><th>边界与下一步</th></tr></thead><tbody>'+''.join(f'<tr><td>{esc(a)}</td><td>{esc(b)}</td><td>{esc(c)}</td></tr>' for a,b,c in module_rows)+'</tbody></table></div>'
constructs='<div class="note"><h3>五大构成如何使用</h3>'+para('科技：围绕层序保持、接口和验证分析；人本：关注科学研究者的数据需求和远程操作者判断；艺术：可探索面向公众的原理可视化；商业：现有资料不足以核定经济收益或许可条件；文化：可组织长期协作的创新故事。以上为平台分析，不是奖项评分，资料不足的维度保留缺口。')+'</div>'
apps='<div class="note"><h3>同一档案，支撑三种应用</h3>'+para('展馆：围绕“为什么取到土还不够”组织层序保持的解释。教育：以彩色分层颗粒比较不同取样方式，作为课堂建议，未试教。企业：把“减少相对运动、保护关键接口、分层验证”带入真实课题，再重新确认工况和指标。')+'</div>'
sections=''
sections+=section('overview','01','对象清楚，才有可信档案','本例研究的是获奖钻取采样方法与系统。整器任务、前期研究和关联技术在各自范围内记录。',coverage)
sections+=section('facts','02','事实档案与结果口径','每条关键陈述都能返回来源；官网陈述与独立验证分别标记。','<div class="alert">260 / 320 克：项目官网披露的钻取量。约 1731 / 1935.3 克：国家航天局披露的任务总量。两组数据不可混用。</div><div class="grid">'+facts+'</div>')
sections+=section('innovation','03','理解创新，再讨论迁移','从问题到机制，留下条件和代价。技术分析、故事叙事与已验证结果分别呈现。','<div class="grid">'+ks+stories+'</div>'+constructs+apps)
sections+=section('patents','04','专利与论文：先确证关联','项目官网披露50件授权发明专利；本轮整理6条技术候选，没有取得完整项目清单。','<div class="grid">'+ps+papers+'</div>')
sections+=section('timeline','05','一个系统，多个发展阶段','研究起点、正式承研、任务应用和获奖是不同事件。日期精度按来源记录。','<div class="grid">'+events+'</div>')
sections+=section('sources','06','证据库：读到了哪里，也写清楚','保存出处、定位与阅读范围。原始来源和图片可能受访问或授权条件限制。','<div class="grid">'+ss+'</div>')
sections+=section('maintenance','07','档案继续生长的下一步','公开资料研究已形成首版，项目方确认和领域审核仍待安排。任务为建议，尚未派发。','<div class="grid">'+tasks+'</div><p class="intro">项目真实进展：历史任务应用已有来源；最新产品状态待确认。档案状态：D2候选，未通过专业审核；持续管理D3尚未验收。</p>')
css='''
:root{--bg:#f7f5ef;--ink:#242721;--muted:#687065;--line:#d9ded3;--green:#526647;--gold:#a78145;--pale:#edf0e7}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.85 -apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif}a{color:var(--green);text-underline-offset:4px}header{max-width:1240px;margin:auto;padding:22px 32px;display:flex;justify-content:space-between;border-bottom:1px solid var(--line);gap:20px}header b{letter-spacing:.08em}header span{color:var(--muted);font-size:12px}.layout{max-width:1240px;margin:auto;display:grid;grid-template-columns:180px 1fr;gap:42px;padding:0 32px}aside{padding-top:60px}nav{position:sticky;top:26px;display:grid;gap:14px;font-size:13px}nav a{text-decoration:none;color:var(--muted)}nav b{font-size:11px;color:var(--gold);letter-spacing:.12em;margin-bottom:8px}.hero{padding:58px 0 38px}.eyebrow{font-size:12px;letter-spacing:.15em;color:var(--green)}h1{font:500 clamp(29px,4vw,48px)/1.45 'Songti SC',STSong,serif;max-width:850px;margin:18px 0}h2{font:500 27px/1.5 'Songti SC',STSong,serif;margin:0}h3{font-size:17px;line-height:1.65;margin:7px 0 12px;font-weight:600}.hero p{max-width:780px;color:var(--muted)}.badge{display:inline-block;font-size:12px;padding:4px 11px;border:1px solid var(--line);border-radius:4px;margin:0 5px 7px 0}.stats{display:grid;grid-template-columns:repeat(4,1fr);margin-top:26px;border-block:1px solid var(--line)}.stats div{padding:18px 0}.stats b{display:block;font:32px/1.4 Georgia,serif;color:var(--green)}.stats span{font-size:12px;color:var(--muted)}.controls{padding:18px 0 26px;display:flex;gap:10px;flex-wrap:wrap;align-items:center}.controls input{flex:1;min-width:180px}.controls input,.controls select,button{font:inherit;font-size:14px;padding:11px 13px;background:white;border:1px solid var(--line);border-radius:4px;color:var(--ink)}button{cursor:pointer}button:hover{background:var(--pale)}#search-status{width:100%;font-size:12px;color:var(--muted);margin:0}section{padding:35px 0;border-top:1px solid var(--line);scroll-margin-top:24px}.section-head{display:flex;gap:18px;align-items:baseline}.section-head span{font-size:12px;color:var(--gold)}.intro{color:var(--muted);font-size:14px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}.record{background:#fff;border:1px solid var(--line);padding:22px;border-radius:5px;scroll-margin-top:24px;overflow-wrap:anywhere}.record p{font-size:14px;margin:9px 0}.record .small,.meta{font-size:12px;color:var(--muted)}.ref{display:inline-block;font-size:12px;margin:8px 8px 0 0;padding:2px 7px;border:1px solid var(--line);border-radius:3px}.alert{padding:17px 20px;margin:20px 0;background:var(--pale);border-left:3px solid var(--green);font-size:14px}.note{padding:22px 0 8px;border-top:1px solid var(--line);margin-top:25px}.note p{font-size:14px;color:var(--muted)}.table-wrap{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:13px;text-align:left}th,td{padding:13px 10px;border-bottom:1px solid var(--line);vertical-align:top}th{color:var(--green);white-space:nowrap}td:first-child{min-width:105px}td:nth-child(2){min-width:70px}footer{padding:32px 0 50px;border-top:1px solid var(--line);font-size:12px;color:var(--muted)}[hidden]{display:none!important}:focus-visible{outline:3px solid var(--gold);outline-offset:3px}#empty{background:var(--pale);padding:18px} @media(max-width:850px){.layout{display:block;padding:0 22px}header{padding:18px 22px}aside{padding-top:20px}nav{position:static;display:flex;flex-wrap:wrap;gap:9px 16px}nav b{width:100%}.hero{padding:32px 0 20px}.grid{grid-template-columns:1fr}.controls input{flex-basis:calc(100% - 82px)}.stats{grid-template-columns:repeat(2,1fr)}h2{font-size:23px}header{flex-wrap:wrap}section{padding:28px 0}.record{padding:18px}} @media print{@page{size:A4;margin:16mm}body{background:white;font-size:10pt}.layout{display:block;max-width:none;padding:0}aside,.controls,header{display:none}.hero{padding:10px 0 20px}h1{font-size:26pt}.grid{display:block}.record{break-inside:avoid;margin-bottom:12px;border-radius:0;padding:12px}.record[hidden]{display:block!important}h2,h3{break-after:avoid}section{padding:20px 0}.record p,.intro{font-size:10pt}.record a[href^="http"]:after{content:' (' attr(href) ')';font-size:8pt;overflow-wrap:anywhere}.stats b{font-size:20pt}}
'''
js='''
const query=document.getElementById('query'),kind=document.getElementById('kind'),records=[...document.querySelectorAll('.record')];
function filter(){const q=query.value.trim().toLocaleLowerCase();let n=0;records.forEach(r=>{const match=(!q||r.textContent.toLocaleLowerCase().includes(q))&&(kind.value==='all'||r.dataset.kind===kind.value);r.hidden=!match;if(match)n++});document.getElementById('search-status').textContent=`显示 ${n} / ${records.length} 条记录。事实、专利、来源、机制、事件与任务均可检索。`;document.getElementById('empty').hidden=n!==0}
query.addEventListener('input',filter);kind.addEventListener('change',filter);document.getElementById('reset').addEventListener('click',()=>{query.value='';kind.value='all';filter();query.focus()});document.querySelectorAll('a.ref[href^="#"]').forEach(a=>a.addEventListener('click',()=>{query.value='';kind.value='all';filter()}));document.getElementById('print').addEventListener('click',()=>window.print());filter();
'''
nav=''.join(f'<a href="#{i}">{n}</a>' for i,n in [('overview','01 档案结构'),('facts','02 事实与结果'),('innovation','03 创新与故事'),('patents','04 专利与论文'),('timeline','05 发展历程'),('sources','06 证据来源'),('maintenance','07 持续维护')])
page=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>嫦娥钻取采样｜好设计标杆档案</title><link rel="icon" href="data:,"><style>{css}</style></head><body><header><b>好设计<span style="color:#a78145">。</span></b><span>项目档案 · BENCHMARK 001 · 2026.10.19</span></header><div class="layout"><aside><nav aria-label="档案导航"><b>项目全貌 / 研究首版</b>{nav}</nav></aside><main><div class="hero"><div class="eyebrow">从真实项目，到可迁移的创新知识</div><h1>{esc(d['title'])}</h1><span class="badge">2025 第十届 · 金奖</span><span class="badge">项目 2025-00</span><span class="badge">公开资料深研 · 待专业审核</span><p>核心问题：如何在未知月壤与严苛工程约束下，取到有科学价值的分层样品，并完成可靠收纳与交接？</p><p>哈尔滨工业大学 · 北京圣视环宇科技有限公司。获奖身份依据官方名单核读；本页将事实、平台分析和待验证线索分别标记。</p><div class="stats"><div><b>{len(sources)}</b><span>来源卡 · 含摘要及选例线索</span></div><div><b>{len(claims)}</b><span>有出处的关键陈述</span></div><div><b>{len(d['patents'])}</b><span>专利技术候选 · 未确证清单</span></div><div><b>{len(d['knowledge'])}</b><span>创新机制分析</span></div></div></div><div class="controls"><label for="query">档案检索</label><input id="query" type="search" placeholder="输入：软袋、1935.3、CN107503698、邓宗全…"><label for="kind">范围</label><select id="kind"><option value="all">全部记录</option><option value="fact">事实</option><option value="knowledge">机制与故事</option><option value="patent">专利与论文</option><option value="event">发展事件</option><option value="source">来源</option><option value="task">任务</option></select><button id="reset">重置</button><button id="print">打印 / 保存 PDF</button><p id="search-status" role="status" aria-live="polite"></p></div><p id="empty" hidden>没有匹配记录，请更换关键词或重置筛选。</p>{sections}<footer>档案版本 benchmark-v1｜截至 2026-10-19｜依据公开资料研究，无项目方或领域专家审核背书。<br>研究与维护任务尚待指定负责人；图片与第三方全文未在本页再发布。</footer></main></div><script>{js}</script></body></html>'''
(OUT/'研究台账.html').write_text(page)
# Readable text export shares the authoritative data, not a separate manually edited report.
md=[f"# {d['title']}｜标杆档案\n",f"截至 {d['as_of']}；{d['status']}。\n",'## 1. 身份与边界\n',f"项目ID：{d['project_id']}；2025年第十届金奖，官方编号12025070107。完成单位：哈尔滨工业大学、北京圣视环宇科技有限公司。[S01]。\n",'研究范围：'+ '、'.join(d['scope']['included'])+'。\n','排除：'+'、'.join(d['scope']['excluded'])+'。\n','## 2. 十二模块覆盖\n','| 模块 | 状态 | 边界 |\n|---|---|---|']
md += [f'| {a} | {b} | {c} |' for a,b,c in module_rows]
md+=['\n## 3. 关键事实与证据\n']
for c in d['claims']:md += [f"### {c['id']} {c['value']}\n",f"范围：{c['scope']}；性质：{c['nature']}；状态：{c['review_status']}。定位：{c['locator']}。{c['note']} 来源：{', '.join(c['source_ids'])}。\n"]
md+=['## 4. 创新机制与可迁移知识（平台分析）\n']
for k in d['knowledge']:
 md += [f"### {k['id']} {k['title']}\n"]+[f"- {label}：{k[key]}" for label,key in [('问题','problem'),('措施','measure'),('机制','mechanism'),('取舍','tradeoffs'),('迁移','transfer'),('边界','boundary'),('验证建议','validation')]]+[f"- 来源：{', '.join(k['source_ids'])}\n"]
md+=['## 5. 专利候选与论文\n','官网披露的50件授权专利未取得逐项清单。本轮六条是技术候选，未认定为型号采用或项目确认。现时法律状态、权属与同族待核。\n']
for p in d['patents']:md += [f"- **{p['publication']} {p['title']}**：申请号{p['application_number']}，申请日{p['filing_date']}。{p['relationship_evidence']} 来源：{', '.join(p['source_ids'])}。\n"]
for p in d['papers']:md += [f"- {p['title']}，DOI {p['doi']}。阅读：{p['read_scope']}；归属：{p['relation']}。来源：{', '.join(p['source_ids'])}。\n"]
md+=['## 6. 发展历程\n']+[f"- {e['date']} **{e['title']}**：{e['detail']} [{', '.join(e['source_ids'])}]" for e in d['events']]
md+=['\n## 7. 项目故事\n']+[f"### {s['title']}\n{s['narrative']}\n\n边界：{s['limit']} [{', '.join(s['source_ids'])}]\n" for s in d['stories']]
md+=['## 8. 五大构成与应用\n','科技侧重机制与验证；人本侧重科学数据需求和远程判断；艺术侧重原理可视化的策展建议；商业收益及许可条件缺证；文化侧重长期协作故事。以上为平台分析，不代表获奖评审分数。\n','应用建议：展馆解释层序为何重要；教育比较分层颗粒的取样效果（未试教）；企业研究关键接口与分层验证（未开展转化试验）。\n','## 9. 待补事项与持续维护\n']
md += [f"- **{t['id']} {t['title']}**：{t['acceptance']} {t['owner']}，尚未派发。" for t in d['tasks']]
md+=['\n## 10. 来源索引\n']
for s in sources.values():md += [f"- [{s['id']} {s['title']}]({s['url']})；读取：{s['read_scope']}；定位：{s['locator']}；访问：{s['accessed_at']}。"]
md+=['\n## 11. 本轮版本\n','benchmark-v1：公开资料研究与结构自检。专业审核、真实协作、持续更新和全量成果关联尚未完成。完整检索范围见研究日志.json。']
(OUT/'研究台账.md').write_text('\n'.join(md)+'\n')
report={'spec':'011','date':'2026-10-19','result':'pass_structural_self_check','counts':{key:len(d[key]) for key in ['sources','claims','patents','knowledge','events','papers','stories','gaps','tasks']},'checks':['unique_record_ids','source_claim_knowledge_references','search_log_source_references','gap_task_links','claim_source_and_locator','no_fake_expert_review','patent_status_not_inferred','source_cards_exist'],'data_sha256':hashlib.sha256(DATA.read_bytes()).hexdigest(),'limits':['不是事实独立核验或专家审核','浏览器验收另行记录','原始工程材料及专利登记未取得']}
(OUT/'验收报告.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report['counts'],ensure_ascii=False))
print(OUT/'档案.html')

# The authored master document remains the primary reading entry.
import runpy
if (OUT/'主档案结构.json').exists():
 runpy.run_path(str(ROOT/'scripts/build_case_field_standard.py'))
 runpy.run_path(str(ROOT/'scripts/build_case_atomic_data.py'))
 from dossier_governance import quality
 quality(OUT)
 runpy.run_path(str(ROOT/'scripts/render_master_dossier.py'))
