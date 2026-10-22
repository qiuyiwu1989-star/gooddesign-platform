# coding: utf-8
"""045 project-scoped research data in the shared benchmark archive reader."""
import html,json,urllib.parse
import project_pipeline as pp
import research_workflow as rw
import project_ownership as own
from dossier_layout import CSS as READER_CSS,KEYS,icon,view_bar
MODULE_ENTITIES=[['project','award','organization','person'],['problem','technology'],['innovation'],['metric','validation'],['patent','paper','achievement'],['event','story'],['application'],['source','task']]
CSS='''
.research-record{margin:16px 0}.research-record>summary{font-weight:600}.research-record .reader-properties{display:block}.research-record .reader-properties>div{grid-template-columns:130px minmax(0,1fr)}.research-row dd details{margin-top:8px;font-size:12px}.research-row blockquote{margin:8px 0;padding:12px;background:var(--ui-soft);white-space:pre-wrap}.research-note{color:var(--muted);font-size:12px}.research-guide{padding:16px;background:var(--ui-soft);border-radius:12px;margin-bottom:24px}.research-guide p{margin:8px 0}.research-ai{padding:18px;border-left:3px solid var(--accent);background:var(--ui-soft);margin:20px 0}.research-tag{display:inline-flex;font-size:12px;padding:3px 10px;border-radius:999px;color:var(--accent);background:var(--pale)}.research-box{background:white;border:1px solid var(--line);border-radius:var(--ui-radius);padding:24px;margin:16px 0;overflow-wrap:anywhere}.research-box>summary{cursor:pointer;font-weight:600}.research-box small{display:block;font-weight:400;color:var(--muted);font-size:12px}.source-actions{display:flex;gap:20px;flex-wrap:wrap}.research-box p,.research-record p{overflow-wrap:anywhere}.generic-route{display:flex;gap:16px;flex-wrap:wrap;margin:20px 0}.generic-route a{display:inline-flex;gap:8px;align-items:center;text-decoration:none;padding:10px 14px;border:1px solid var(--line);border-radius:12px}.generic-route .ui-icon{width:18px}.module-title .module-summary{font-size:12px;margin-top:6px}.missing-fields dd{min-height:20px}@media(max-width:850px){.research-record .reader-properties>div{grid-template-columns:90px minmax(0,1fr)}.research-box{padding:20px}}@media print{.reader-shell [data-panel][hidden]{display:none!important}#reader-view:not([hidden]),#library-view:not([hidden]),#assessment-view:not([hidden]){display:block!important}.research-record{break-inside:auto}.research-box{box-shadow:none}.research-row blockquote{white-space:pre-wrap}}
'''
JS='''
const panels=[...document.querySelectorAll('[data-panel]')];
function show(name){panels.forEach(x=>x.hidden=x.dataset.panel!==name);document.querySelectorAll('[data-reader-tab]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.readerTab===name)));document.querySelectorAll('#toc-reader a').forEach(a=>a.removeAttribute('aria-current'));const a=document.querySelector(name==='archive'?'#toc-reader [data-reader-section="top"]':'#toc-reader [data-switch="'+name+'"]');if(a)a.setAttribute('aria-current','location');}
function openModule(el){document.querySelectorAll('.reader-module').forEach(m=>m.open=m===el);if(el){document.querySelectorAll('#toc-reader a').forEach(a=>a.removeAttribute('aria-current'));const a=document.querySelector('#toc-reader [data-reader-section="'+el.id.slice(7)+'"]');if(a)a.setAttribute('aria-current','location');}}
function locate(hash){const id=decodeURIComponent(hash.replace(/^#/,''));let el=document.getElementById(id);if(!el)return;const panel=el.closest('[data-panel]');if(panel)show(panel.dataset.panel);else show('archive');const module=el.closest('.reader-module');if(module)openModule(module);for(let p=el.parentElement;p;p=p.parentElement)if(p.tagName==='DETAILS')p.open=true;if(el.matches('details:not(.reader-module)'))el.open=true;requestAnimationFrame(()=>el.scrollIntoView({block:'start'}));}
document.querySelectorAll('[data-reader-tab]').forEach(b=>b.addEventListener('click',()=>{show(b.dataset.readerTab);const hash={archive:'#reader-top',library:'#library-view',assessment:'#assessment-view'}[b.dataset.readerTab];history.replaceState(null,'',hash);document.getElementById(hash.slice(1)).scrollIntoView({block:'start'});}));
document.querySelectorAll('.reader-module>summary').forEach(s=>s.addEventListener('click',e=>{e.preventDefault();const m=s.parentElement;const target=m.open?null:m;openModule(target);history.replaceState(null,'','#'+(target?m.id:'reader-top'));}));
document.querySelectorAll('a[href^="#"]').forEach(a=>a.addEventListener('click',e=>{e.preventDefault();const hash=a.getAttribute('href');history.replaceState(null,'',hash);locate(hash);}));
window.addEventListener('hashchange',()=>locate(location.hash));
document.querySelector('[data-print]').addEventListener('click',()=>window.print());
let printState=[];window.addEventListener('beforeprint',()=>{printState=[...document.querySelectorAll('details')].map(el=>[el,el.open]);printState.forEach(([el])=>{if(!el.closest('[hidden]'))el.open=true;});});window.addEventListener('afterprint',()=>printState.forEach(([el,open])=>el.open=open));show('archive');if(location.hash)locate(location.hash);
'''

def render(lib,pid,header,shared_css):
 p=pp.project(lib,pid);state=pp.state(p);meta=state['project'];w=rw.current(p)
 revision='research-%06d'%w['revision'];data=rw.dataset(p,w)if w['revision']else dict(records=[],interpretations=[])
 fields=rw.schema();records=data['records'];interpretations=data.get('interpretations',[])
 from research_reader_notes import safe_read
 guide=safe_read(p,revision)if w['revision']else dict(notes=None);notes=guide['notes'];module_notes={m['module_id']:m for m in notes['modules']}if notes else{}
 from research_assessment import safe_read as read_assessment,render as render_assessment
 review_html=render_assessment(read_assessment(p,revision),data,lambda path,**q:path+'?'+urllib.parse.urlencode(dict(project=pid,**q)))if w['revision']else''
 sources=own.select(p,state['sources']);mapping=pp.load(p/'资料关联.json').get('source_titles',{})if(p/'资料关联.json').exists()else{}
 image_titles={x['library_source_id']:x['title']for x in pp.load(p/'图片素材/图片清单.json')['items']}if(p/'图片素材/图片清单.json').exists()else{}
 h=lambda value:html.escape(str(value),quote=True)
 def url(path,**values):return path+'?'+urllib.parse.urlencode(dict(project=pid,**values))
 def val(value):return '、'.join(str(x)for x in value)if isinstance(value,list)else json.dumps(value,ensure_ascii=False)if isinstance(value,dict)else str(value)
 def known(r):return [(k,c)for k,c in r.get('cells',{}).items()if c.get('value_state')=='known'and c.get('value')is not None]
 def evidence(c):
  e=c.get('evidence',c);sid=e.get('source_id');quote=e.get('quote');locator=c.get('locator',e.get('locator',''))
  if not sid:return ''
  return '<details><summary>查看出处与原文</summary><p>'+h(locator)+' · <a href="#source-'+h(sid)+'">资料索引</a></p><blockquote>'+h(quote or'原文见对应资料')+'</blockquote></details>'
 def record(r):
  dictionary=fields.get(r['entity'],{});known_fields=known(r)
  rows=''.join('<div class="research-row"><dt>'+h(dictionary.get(k,{}).get('label',k))+'</dt><dd>'+h(val(c['value']))+evidence(c)+'</dd></div>'for k,c in known_fields)
  missing=[k for k,c in r.get('cells',{}).items()if c.get('value_state')!='known'or c.get('value')is None]
  blanks='<details class="missing-fields reader-expand"><summary>待补信息 · '+str(len(missing))+' 项</summary><dl class="reader-properties">'+''.join('<div><dt>'+h(dictionary.get(k,{}).get('label',k))+'</dt><dd><span class="blank-value" aria-label="暂无资料"></span></dd></div>'for k in missing)+'</dl></details>'if missing else''
  withdrawn=[c for c in r.get('cells',{}).values()if c.get('value_state')=='not_obtained'and c.get('evidence')]
  retired=not known_fields and bool(withdrawn)
  status=' · 已撤回旧记录'if retired else''
  explanation=('<p class="reader-note">这条旧记录已撤回，保留位置用于版本追溯。'+h(withdrawn[0].get('limitations')or'更正依据见档案评估中的更新记录。')+'</p>')if retired else''
  return '<details class="research-record reader-expand" id="record-'+h(r['id'])+'"><summary>'+h(r['title'])+status+'</summary>'+explanation+'<dl class="reader-properties">'+rows+'</dl>'+(''if retired else blanks)+'</details>'
 total=sum(len(r.get('cells',{}))for r in records);filled=sum(len(known(r))for r in records)
 module_html=[];assessment=[]
 for i,(name,entities,key)in enumerate(zip(pp.MODULES,MODULE_ENTITIES,KEYS),1):
  group=[r for r in records if r['entity']in entities];ai=[x for x in interpretations if x['entity']in entities];n=sum(len(known(r))for r in group);alln=sum(len(r.get('cells',{}))for r in group);percent=round(100*n/alln,1)if alln else None
  text=''.join(record(r)for r in group);note=module_notes.get(i)
  if note:
   text='<div class="research-guide"><span class="research-tag">AI阅读导读</span><p>'+h(note['summary'])+'</p><details class="reader-expand"><summary>继续完善的方向</summary><ul>'+''.join('<li>'+h(g)+'</li>'for g in note['gaps'])+'</ul></details></div>'+text
  if not group:text+='<p class="reader-note">这个项目的研究档案还有待整理，暂无已入档事实；请先补充本项目资料。</p>'
  for c in ai:text+='<details class="research-ai reader-expand"><summary><span class="research-tag">AI解读 · 未经工程验证</span> '+h(c['title'])+'</summary><p>'+h(val(c['value']))+'</p><p>适用前提：'+h(c['conditions'])+'</p><p>限制：'+h(c['limitations'])+'</p>'+evidence(c)+'</details>'
  meter='字段填充 '+str(percent)+'%'if percent is not None else'暂无登记字段'
  module_html.append('<details class="reader-section reader-module" id="reader-'+key+'" tabindex="-1"><summary><span class="module-icon">'+icon(key)+'</span><div class="module-title"><h2><span>'+str(i).zfill(2)+'</span>'+h(name)+'</h2><p>'+str(len(group))+' 条资料记录 · '+str(n)+' 个有值字段 · '+str(len(ai))+' 条AI解读</p></div><div class="module-meter"><span>'+meter+'</span>'+('<progress value="'+str(n)+'" max="'+str(alln)+'" aria-label="'+h(name)+'当前字段填充率"></progress>'if alln else'')+'</div><span class="module-chevron">'+icon('chevron')+'</span></summary><div class="module-content"><span id="module-'+str(i)+'"></span>'+text+'<div class="module-footer"><a class="reader-link" href="#reader-top">回到档案总览 ↑</a></div></div></details>')
  assessment.append('<li>'+h(name)+'：'+str(n)+' / '+str(alln)+' 个已登记字段有值；'+('待补充记录'if not group else'仍需专业审核')+'</li>')
 source_html=[]
 read_labels={'machine_text_extraction_not_human_read':'机器整理 · 不代表核读','machine_table_boundaries_not_human_read':'表格转换 · 不代表核读','machine_ocr_not_human_read':'机器识别 · 待核对','full_text':'全文范围','abstract_only':'仅摘要','metadata_only':'仅题录','not_read':'尚未核读','full_text_read':'全文已读'}
 for sid,x in sources.items():
  origin=x.get('origin',{});u=origin.get('url')or'';title=image_titles.get(sid)or mapping.get(u)or origin.get('filename')or x['title']
  scope=x.get('read_scope','');label=read_labels.get(scope,'核读范围待确认')
  source_html.append('<details class="paper-reading" id="source-'+h(sid)+'" tabindex="-1"><summary>'+icon('chevron')+'<div class="paper-reading-top"><span>'+h(label)+'</span><span>已保存原件</span></div><h3>'+h(title)+'</h3></summary><div class="paper-body"><p class="reader-note">原件保存、机器转换与实际核读分别管理。来源编号 '+h(sid)+'</p><p class="source-actions"><a href="'+h(url('/asset',source=sid,kind='original'))+'">下载保存的原件</a><a href="'+h(url('/asset',source=sid,kind='document'))+'">查看可读来源</a></p>'+('<p><a href="'+h(u)+'" rel="noopener noreferrer" target="_blank">原始网站 ↗</a></p>'if u.startswith(('https://','http://'))else'')+'</div></details>')
 toc='<aside class="toc" id="toc" aria-label="阅读目录"><div id="toc-reader"><b>阅读目录</b><a href="#reader-top" data-reader-section="top">'+icon('overview')+'档案概览</a>'+''.join('<a href="#reader-'+key+'" data-reader-section="'+key+'">'+icon(key)+h(name)+'</a>'for key,name in zip(KEYS,pp.MODULES))+'<div class="toc-reading-appendix"><a href="#library-view" data-switch="library">'+icon('ip')+'资料与解读</a><a href="#assessment-view" data-switch="assessment">'+icon('governance')+'档案评估</a></div><div class="toc-note"><b>档案研究版</b>空白保留，资料持续补充。<br>质量总分未评 · 待专业审核</div></div></aside>'
 project_record=next((r for r in records if r['entity']=='project'),{})
 summary_cell=project_record.get('cells',{}).get('summary',{})
 overview=summary_cell['value']if summary_cell.get('value_state')=='known'and isinstance(summary_cell.get('value'),str)else'从需求与系统、设计思路到指标与验证，逐步了解这个项目。资料依据和AI解读分别呈现，未知信息保留空白。'
 hero='<div class="hero" id="workspace-content"><p class="workspace-context">研究整理档案 · 8 个阅读模块　<a href="'+h(url('/'))+'">整理与查看研究版本 →</a></p><div class="eyebrow">好设计 / 项目档案</div><h1>'+h(meta['name'])+'</h1><p class="summary">'+h(overview)+'</p><div class="reader-hero-meta"><span class="ui-badge">'+icon('award')+h('题录年份 '+str(meta.get('year')or'待补')+' · '+str(meta.get('award')or'奖项待补'))+'</span><span class="ui-badge pending">'+icon('info')+'待专业审核</span><span>'+h(revision if w['revision']else'尚未发布研究版本')+'</span></div></div>'
 metrics='<div class="reader-metrics">'+''.join('<div><b>'+h(value)+'</b><span>'+label+'</span></div>'for value,label in [(8,'内容模块'),(len(records),'信息记录'),(len(sources),'保存的来源文件'),('未评','档案质量')])+'</div>'
 story='<div class="project-story"><div class="project-story-copy"><span class="ui-kicker">认识这个项目</span><h3>从项目事实，读到设计思路。</h3><p>先看需求与系统，再理解创新机制，最后核对指标与验证。</p><p class="reader-note">另有 '+str(len(interpretations))+' 条AI解读，前提与限制单独保留。</p></div><div class="generic-route">'+''.join('<a href="#reader-'+key+'">'+icon(key)+label+'</a>'for key,label in [('technical','需求与系统'),('innovation','设计思路'),('validation','指标与验证')])+'</div></div>'
 archive='<section data-panel="archive" id="reader-view"><div id="reader-top" tabindex="-1"><div class="reader-overview-heading"><h2>档案概览</h2><span class="ui-badge pending">'+icon('info')+'来源资料整理 · 待专业审核</span></div>'+metrics+story+'<details class="stats-definition"><summary>'+icon('info')+'如何理解这里的统计与评分？</summary><p>'+str(filled)+' / '+str(total)+' 个已登记字段有值，填充率只针对当前记录，不表示研究完整或事实正确。质量分：未评；专家审核未完成。</p></details></div><div class="module-list-heading"><h2>深入了解这个项目</h2><p>8 个板块 · 点开阅读，一次聚焦一个主题</p></div>'+''.join(module_html)+'</section>'
 reading_guide=('<details class="reader-expand"><summary>档案阅读导读 · AI整理</summary><p>'+h(notes['overview'])+'</p><p class="reader-note">绑定 '+h(revision)+'；不是新增事实或专家结论。</p><a href="'+h(url('/api/research-document',document='guide',revision=revision,guide_version=notes['version']))+'">下载阅读导读</a></details>')if notes else''
 library='<section data-panel="library" id="library-view" hidden><div class="reader-view-heading"><h2>资料与解读</h2><p>从原始资料核对档案，实际核读范围单独标注。AI解读在相应档案模块中阅读。</p></div><span id="source-list"></span>'+reading_guide+''.join(source_html)+('</section>')
 assessment_html='<section data-panel="assessment" id="assessment-view" hidden><span id="quality"></span><div class="reader-view-heading"><h2>档案评估与完善</h2><p>把整理情况、研究判断和仍需补充的资料分开查看。</p></div>'+review_html+'<div class="research-box"><h3>字段登记统计</h3><p>8 个阅读模块；'+str(filled)+' / '+str(total)+' 个已登记字段有值。填充率不代表项目研究完整度。</p><p>质量分：未评。专家审核：未完成。</p><ul>'+''.join(assessment)+'</ul>'+('<a href="'+h(url('/api/research-document',document='data',revision=revision))+'">下载本研究版本结构化档案</a>'if w['revision']else'')+'</div></section>'
 return '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:,"><title>'+h(meta['name'])+' · 项目档案</title><style>'+READER_CSS+CSS+shared_css+'</style></head><body>'+header+'<div class="shell reader-shell">'+toc+'<main>'+hero+view_bar()+archive+library+assessment_html+'<footer class="reader-note">好设计 · 项目档案<br>依据已归档资料整理，空白持续补充。项目方与专业审核待完成。</footer></main></div><script>'+JS+'</script></body></html>'
