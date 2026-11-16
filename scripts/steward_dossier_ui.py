# coding: utf-8
"""045 project-scoped research data in the shared benchmark archive reader."""
import html,json,re,urllib.parse
import project_pipeline as pp
import research_workflow as rw
import project_ownership as own
from archive_presentation import known_cells as known, fact_cells, complete_evidence
from dossier_layout import CSS as READER_CSS,KEYS,icon,view_bar
from dossier_reader_ui import CORE_MODULES
MODULE_ENTITIES=[['project','award','organization','person'],['problem','technology'],['innovation'],['metric','validation'],['patent','paper','achievement'],['event','story'],['application'],['source','task']]
DISPLAY_MODULE_ENTITIES=[['project','award','organization','person'],['problem'],['innovation','technology'],['metric','validation'],['patent','paper','achievement'],['event','story'],['application'],['source','task']]
READ_SCOPE_LABELS={'machine_text_extraction_not_human_read':'机器整理，未经人工逐条核读','machine_table_boundaries_not_human_read':'表格转换，未经人工核读','machine_ocr_not_human_read':'机器识别，待人工核对','full_text':'全文范围','abstract_only':'仅读到摘要','metadata_only':'仅有题录','not_read':'尚未核读','full_text_read':'全文已读'}
UNIT_LABELS={'%':'％','s':'秒','g':'克','kg':'千克','mm':'毫米','N':'牛','N·m':'牛·米','km/h':'千米/小时','MPa':'兆帕','m3·min-1':'立方米/分钟','m3/min':'立方米/分钟','h':'小时','r/min':'转/分钟','min-1':'转/分钟','A':'安','µm':'微米','μm':'微米','kW':'千瓦','t':'吨'}
CSS='''
.research-record{margin:16px 0}.research-record>summary{font-weight:600}.research-record .reader-properties{display:block}.research-record .reader-properties>div{grid-template-columns:130px minmax(0,1fr)}.research-row dd details{margin-top:8px;font-size:12px}.research-row blockquote{margin:8px 0;padding:12px;background:var(--ui-soft);white-space:pre-wrap}.research-note{color:var(--muted);font-size:12px}.research-guide{padding:16px;background:var(--ui-soft);border-radius:12px;margin-bottom:24px}.research-guide p{margin:8px 0}.research-ai{padding:18px;border-left:3px solid var(--accent);background:var(--ui-soft);margin:20px 0}.research-tag{display:inline-flex;font-size:12px;padding:3px 10px;border-radius:999px;color:var(--accent);background:var(--pale)}.research-box{background:var(--ui-surface);border:1px solid var(--line);border-radius:var(--ui-radius);padding:24px;margin:16px 0;overflow-wrap:anywhere}.research-box>summary{cursor:pointer;font-weight:600}.research-box small{display:block;font-weight:400;color:var(--muted);font-size:12px}.source-actions{display:flex;gap:20px;flex-wrap:wrap}.research-box p,.research-record p{overflow-wrap:anywhere}.generic-route{display:flex;gap:16px;flex-wrap:wrap;margin:20px 0}.generic-route a{display:inline-flex;gap:8px;align-items:center;text-decoration:none;padding:10px 14px;border:1px solid var(--line);border-radius:12px}.generic-route .ui-icon{width:18px}.module-title .module-summary{font-size:12px;margin-top:6px}.missing-fields dd{min-height:20px}@media(max-width:850px){.research-record .reader-properties>div{grid-template-columns:90px minmax(0,1fr)}.research-box{padding:20px}}@media print{.reader-shell [data-panel][hidden]{display:none!important}#reader-view:not([hidden]),#library-view:not([hidden]),#assessment-view:not([hidden]){display:block!important}.research-record{break-inside:auto}.research-box{box-shadow:none}.research-row blockquote{white-space:pre-wrap}}
.citation-trigger{display:inline-flex;align-items:center;min-height:32px;margin-left:8px;padding:2px 8px;border:1px solid var(--line);border-radius:999px;background:var(--pale);color:var(--accent);font-size:11px;vertical-align:middle}.citation-trigger[aria-expanded=true]{border-color:var(--accent)}.citation-dialog{position:fixed;z-index:70;width:min(420px,calc(100vw - 32px));max-height:70dvh;margin:0;padding:22px;overflow:auto;border:1px solid var(--line);border-radius:20px;background:var(--ui-surface);color:var(--ink);box-shadow:0 18px 60px rgb(22 24 31 / 18%)}.citation-dialog::backdrop{background:transparent;backdrop-filter:none;-webkit-backdrop-filter:none}.citation-dialog-head{display:flex;align-items:flex-start;justify-content:space-between;gap:16px}.citation-dialog-head h2{margin:0;font-size:19px;line-height:1.5}.citation-dialog-meta{margin:14px 0;color:var(--muted);font-size:12px}.citation-dialog blockquote{margin:16px 0;padding:14px;border-radius:12px;background:var(--ui-soft);font-size:13px;line-height:1.8;white-space:pre-wrap}.citation-dialog a{display:inline-flex;min-height:40px}.citation-print{display:none}@media(max-width:720px){.citation-dialog{left:0!important;right:0;bottom:0;top:auto!important;width:100%;max-width:100%;max-height:75dvh;border-radius:22px 22px 0 0}.citation-dialog-head h2{font-size:18px}}@media print{.citation-trigger,.citation-dialog{display:none!important}.citation-print{display:block}}
.evidence-warning{padding:14px 16px;border-left:3px solid var(--accent);background:var(--ui-soft);font-size:14px}.citation-trigger{min-height:28px;margin-left:6px;padding:0 3px;border:0;background:transparent;font-size:11px;line-height:1.4}.reference-list{padding-left:22px}.reference-item{margin:0 0 22px}.reference-item>p{color:var(--muted);font-size:12px}.reference-item blockquote{white-space:pre-wrap}.reference-item>a{font-size:12px}
.assessment-visual{display:grid;grid-template-columns:190px minmax(0,1fr);gap:22px;margin:26px 0}.assessment-donut{text-align:center}.assessment-donut svg{width:150px;max-width:100%}.assessment-donut-track{fill:none;stroke:var(--line);stroke-width:10}.assessment-donut-value{fill:none;stroke:var(--accent);stroke-width:10;stroke-linecap:round}.assessment-donut text{font-size:16px;font-weight:600;fill:var(--ink)}.assessment-donut text+text{font-size:10px;fill:var(--muted)}.assessment-summary,.assessment-review,.assessment-module-card{border:1px solid var(--line);border-radius:14px;background:var(--ui-surface);padding:18px}.assessment-summary h3,.assessment-review h3{margin:0 0 14px}.assessment-composition-row{display:grid;grid-template-columns:86px minmax(0,1fr) 42px;gap:10px;align-items:center;margin:10px 0}.assessment-composition-row>span{color:var(--muted);font-size:12px}.assessment-composition-row>b{text-align:right}.assessment-bar{height:7px;border-radius:999px;background:var(--line);overflow:hidden}.assessment-bar>span{display:block;height:100%;background:var(--accent);border-radius:999px}.assessment-review{grid-column:1/-1}.assessment-review ol{margin:0;padding-left:20px}.assessment-review li{margin:6px 0}.assessment-modules{grid-column:1/-1;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.assessment-module-card h3{margin:0 0 8px;font-size:15px}.assessment-module-card>b{display:block;margin:8px 0;font-size:18px}.assessment-module-card p{margin:8px 0 0;color:var(--muted);font-size:11px}.graph-link{display:inline-flex;margin-top:12px;padding:10px 14px;border:1px solid var(--accent);border-radius:999px;text-decoration:none}@media(max-width:700px){.assessment-visual{grid-template-columns:1fr}.assessment-modules{grid-template-columns:1fr}.assessment-donut{text-align:left}.assessment-donut svg{width:120px}}
'''
JS='''
const panels=[...document.querySelectorAll('[data-panel]')];
function show(name){panels.forEach(x=>x.hidden=x.dataset.panel!==name);document.querySelectorAll('[data-reader-tab]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.readerTab===name)));document.querySelectorAll('#toc-reader a').forEach(a=>a.removeAttribute('aria-current'));const a=document.querySelector(name==='archive'?'#toc-reader [data-reader-section="top"]':'#toc-reader [data-switch="'+name+'"]');if(a)a.setAttribute('aria-current','location');}
function markModule(el){document.querySelectorAll('#toc-reader a').forEach(a=>a.removeAttribute('aria-current'));const a=document.querySelector('#toc-reader [data-reader-section="'+(el?el.id.slice(7):'top')+'"]');if(a)a.setAttribute('aria-current','location');}
function openModule(el){if(el)el.open=true;markModule(el);}
function locate(hash){const id=decodeURIComponent(hash.replace(/^#/,''));let el=document.getElementById(id);if(!el)return;const panel=el.closest('[data-panel]');if(panel)show(panel.dataset.panel);else show('archive');const module=el.closest('.reader-module');if(module)openModule(module);for(let p=el.parentElement;p;p=p.parentElement)if(p.tagName==='DETAILS')p.open=true;if(el.matches('details:not(.reader-module)'))el.open=true;requestAnimationFrame(()=>el.scrollIntoView({block:'start'}));}
document.querySelectorAll('[data-reader-tab]').forEach(b=>b.addEventListener('click',()=>{show(b.dataset.readerTab);const hash={archive:'#reader-top',library:'#library-view',assessment:'#assessment-view'}[b.dataset.readerTab];history.replaceState(null,'',hash);document.getElementById(hash.slice(1)).scrollIntoView({block:'start'});}));
document.querySelectorAll('.reader-module>summary').forEach(s=>s.addEventListener('click',e=>{e.preventDefault();const m=s.parentElement;m.open=!m.open;markModule(m.open?m:null);history.replaceState(null,'','#'+(m.open?m.id:'reader-top'));}));
document.querySelectorAll('a[href^="#"]').forEach(a=>a.addEventListener('click',e=>{e.preventDefault();const hash=a.getAttribute('href');history.replaceState(null,'',hash);locate(hash);}));
window.addEventListener('hashchange',()=>locate(location.hash));
document.querySelector('[data-print]').addEventListener('click',()=>window.print());
let printState=[];window.addEventListener('beforeprint',()=>{printState=[...document.querySelectorAll('details')].map(el=>[el,el.open]);printState.forEach(([el])=>{if(!el.closest('[hidden]'))el.open=true;});});window.addEventListener('afterprint',()=>printState.forEach(([el,open])=>el.open=open));
const citationDialog=document.getElementById('citation-dialog');let activeCitation=null;
function closeCitation(){if(citationDialog.open)citationDialog.close();}
function openCitation(button){
 activeCitation=button;document.querySelectorAll('.citation-trigger').forEach(item=>item.setAttribute('aria-expanded',String(item===button)));
 citationDialog.querySelector('#citation-title').textContent=button.dataset.citationTitle;
 citationDialog.querySelector('#citation-locator').textContent=button.dataset.citationLocator||'来源位置见对应资料';
 citationDialog.querySelector('#citation-scope').textContent=button.dataset.citationScope;
 citationDialog.querySelector('#citation-quote').textContent=button.dataset.citationQuote;
 citationDialog.querySelector('#citation-link').href=button.dataset.citationLink;
 if(!citationDialog.open)citationDialog.show();
 if(matchMedia('(min-width:721px) and (hover:hover)').matches){
  const rect=button.getBoundingClientRect();const width=citationDialog.getBoundingClientRect().width;const height=citationDialog.getBoundingClientRect().height;
  citationDialog.style.left=Math.max(16,Math.min(rect.left,innerWidth-width-16))+'px';
  citationDialog.style.top=Math.max(16,Math.min(rect.bottom+10,innerHeight-height-16))+'px';
 }else{citationDialog.style.left='';citationDialog.style.top='';}
}
document.querySelectorAll('.citation-trigger').forEach(button=>{
 button.addEventListener('click',()=>openCitation(button));
 if(matchMedia('(hover:hover) and (pointer:fine)').matches)button.addEventListener('mouseenter',()=>openCitation(button));
});
document.getElementById('citation-close').addEventListener('click',closeCitation);
citationDialog.addEventListener('close',()=>{document.querySelectorAll('.citation-trigger').forEach(item=>item.setAttribute('aria-expanded','false'));if(activeCitation)activeCitation.focus();});
document.addEventListener('click',event=>{if(citationDialog.open&&!citationDialog.contains(event.target)&&!event.target.closest('.citation-trigger'))closeCitation();});
document.addEventListener('keydown',event=>{if(event.key==='Escape')closeCitation();});
window.addEventListener('resize',closeCitation);
show('archive');markModule(null);if(location.hash)locate(location.hash);
'''

def render(lib,pid,header,shared_css,graph_href=None):
 p=pp.project(lib,pid);state=pp.state(p);meta=state['project'];w=rw.current(p)
 revision='research-%06d'%w['revision'];data=rw.dataset(p,w)if w['revision']else dict(records=[],interpretations=[])
 fields=rw.schema();records=data['records'];interpretations=data.get('interpretations',[])
 from research_reader_notes import safe_read
 guide=safe_read(p,revision)if w['revision']else dict(notes=None);notes=guide['notes'];module_notes={m['module_id']:m for m in notes['modules']}if notes else{}
 from research_assessment import safe_read as read_assessment,render as render_assessment
 review_result=read_assessment(p,revision)if w['revision']else dict(status='not_available')
 review_html=render_assessment(review_result,data,lambda path,**q:path+'?'+urllib.parse.urlencode(dict(project=pid,**q)))if w['revision']else''
 sources=own.select(p,state['sources']);mapping=pp.load(p/'资料关联.json').get('source_titles',{})if(p/'资料关联.json').exists()else{}
 def complete(c):return complete_evidence(c,sources)
 image_titles={x['library_source_id']:x['title']for x in pp.load(p/'图片素材/图片清单.json')['items']}if(p/'图片素材/图片清单.json').exists()else{}
 h=lambda value:html.escape(str(value),quote=True)
 def url(path,**values):return path+'?'+urllib.parse.urlencode(dict(project=pid,**values))
 record_titles={r['id']:r.get('title') or r['id'] for r in records}
 def source_title(value):
  return re.sub(r'\.(pdf|html?|md|txt)$','',str(value),flags=re.I)
 def unit_text(value):
  if value in UNIT_LABELS:return UNIT_LABELS[value]
  pattern=r'(?<=\d)\s*(m3·min-1|m3/min|N·m|km/h|r/min|min-1|MPa|kW|mm|kg|µm|μm|N|g|s|h|A|t)(?![A-Za-z])'
  return re.sub(pattern,lambda m:' '+UNIT_LABELS[m.group(1)],value).replace('%','％')
 def val(value):
  def one(item):
   if not isinstance(item,str):return str(item)
   if item in record_titles:return record_titles[item]
   if item in sources:return source_title(sources[item]['title'])
   return unit_text(item)
  if isinstance(value,list):return '、'.join(one(x)for x in value)
  if isinstance(value,dict):return json.dumps(value,ensure_ascii=False)
  return one(value)
 def guide_text(value):return str(value).replace('AI解读','平台解读').replace('AI阅读','平台阅读')
 def platform_cells(r,nature=None):return [(k,c)for k,c in known(r)if c.get('content_nature')in ('platform_metadata','platform_analysis')and(nature is None or c.get('content_nature')==nature)]
 citations=[];citation_ids={}
 def evidence(c):
  e=c.get('evidence',c);sid=e.get('source_id');quote=e.get('quote');locator=c.get('locator',e.get('locator',''))
  if not sid:return ''
  if sid not in sources:return '<span class="reader-note">来源待重新绑定</span>'
  title=source_title(image_titles.get(sid)or mapping.get(sources[sid].get('origin',{}).get('url',''))or sources[sid].get('origin',{}).get('filename')or sources[sid]['title'])
  scope=READ_SCOPE_LABELS.get(sources[sid].get('read_scope',''),'核读范围待确认')
  key=(sid,quote)
  if key not in citation_ids:
   number=len(citations)+1;citation_ids[key]=number
   citations.append(dict(number=number,sid=sid,title=title,locator=locator.replace('清洗文本字符','原文位置'),scope=scope,quote=quote or'原文见对应资料'))
  number=citation_ids[key]
  return '<button type="button" class="citation-trigger" data-citation-title="'+h(title)+'" data-citation-locator="'+h(locator.replace('清洗文本字符','原文位置'))+'" data-citation-quote="'+h(quote or'原文见对应资料')+'" data-citation-scope="'+h(scope)+'" data-citation-link="'+h(url('/asset',source=sid,kind='original'))+'" aria-controls="citation-dialog" aria-expanded="false" aria-label="查看来源：'+h(title)+'">注'+str(number)+'</button>'
 def record_title(r):
  return {'EVENT-CE6-AIRCAS-DRILL-TIMELINE':'嫦娥六号钻取任务时间线'}.get(r['id'],r['title'])
 def record(r):
  dictionary=fields.get(r['entity'],{});known_fields=[(k,c)for k,c in fact_cells(r)if k!='date_precision'and not(r['entity'] in {'event','story'} and k in {'subject','entity_scope'})]
  if not known_fields and platform_cells(r,'platform_analysis'):return ''
  rows=''.join('<div class="research-row"><dt>'+h(dictionary.get(k,{}).get('label',k))+'</dt><dd>'+h(val(c['value']))+evidence(c)+'</dd></div>'for k,c in known_fields)
  withdrawn=[c for c in r.get('cells',{}).values()if c.get('value_state')=='not_obtained'and c.get('evidence')]
  retired=not known_fields and bool(withdrawn)
  status=' · 已撤回旧记录'if retired else''
  explanation=('<p class="reader-note">这条旧记录已撤回，保留位置用于版本追溯。'+h(withdrawn[0].get('limitations')or'更正依据见档案评估中的更新记录。')+'</p>')if retired else''
  return '<details class="research-record reader-expand" id="record-'+h(r['id'])+'"'+('' if retired else ' open')+'><summary>'+h(record_title(r))+status+'</summary>'+explanation+'<dl class="reader-properties">'+rows+'</dl></details>'
 total=sum(len(r.get('cells',{}))for r in records);filled=sum(len(known(r))for r in records)
 fact_count=sum(len(fact_cells(r))for r in records)
 incomplete_facts=sum(1 for r in records for _,c in fact_cells(r) if not complete(c))
 evidence_notice=('<p class="reader-note evidence-warning"><b>证据缺口：</b>'+str(incomplete_facts)+' / '+str(fact_count)+' 项项目事实的来源证据尚待重绑，不应作为已核实结论引用。详见档案评估。</p>'if incomplete_facts else'')
 module_html=[];assessment=[];module_visuals=[]
 for i,(name,entities,key)in enumerate(zip(pp.MODULES,DISPLAY_MODULE_ENTITIES,KEYS),1):
  group=[r for r in records if r['entity']in entities];ai=[x for x in interpretations if x['entity']in entities]
  n=sum(len(fact_cells(r))for r in group);registered=sum(len(known(r))for r in group);alln=sum(len(r.get('cells',{}))for r in group)
  traced=sum(1 for r in group for _,c in fact_cells(r) if complete_evidence(c,sources))
  platform_total=sum(len(platform_cells(r))for r in group)
  module_visuals.append(dict(name=name,facts=n,traceable=traced,platform=platform_total,registered=registered,total=alln))
  text=''.join(record(r)for r in group);note=module_notes.get(i)
  if note:
   text='<div class="research-guide"><span class="research-tag">本章提要</span><p>'+h(guide_text(note['summary']))+'</p><details class="reader-expand"><summary>继续完善的方向</summary><ul>'+''.join('<li>'+h(g)+'</li>'for g in note['gaps'])+'</ul></details></div>'+text
  if key=='governance':text=guide_text(review_html)+text
  if not group:text+='<p class="reader-note">本项目的内容仍在整理，当前没有已入档事实。</p>'
  for r in group:
   items=platform_cells(r,'platform_analysis')
   if not items:continue
   dictionary=fields.get(r['entity'],{})
   rows=''.join('<div class="research-row"><dt>'+h(dictionary.get(k,{}).get('label',k))+'</dt><dd>'+h(val(c['value']))+evidence(c)+'</dd></div>'for k,c in items)
   text+='<details class="research-ai reader-expand" id="'+(('record-'+h(r['id'])) if not fact_cells(r) else '')+'"'+(' open' if r['entity']=='story' else '')+'><summary>平台解读 · '+h(record_title(r))+'</summary><p class="reader-note">以下为平台整理，不是项目方事实陈述。</p><dl class="reader-properties">'+rows+'</dl></details>'
  for c in ai:text+='<details class="research-ai reader-expand"><summary>平台解读 · '+h(c['title'])+'</summary><p class="reader-note">以下为平台事后解释，未经过工程验证。</p><p>'+h(val(c['value']))+'</p><p>适用前提：'+h(c['conditions'])+'</p><p>限制：'+h(c['limitations'])+'</p>'+evidence(c)+'</details>'
  module_html.append('<details class="reader-section reader-module" id="reader-'+key+'" tabindex="-1"'+(' open' if key in CORE_MODULES else '')+'><summary><span class="module-icon">'+icon(key)+'</span><div class="module-title"><h2><span>'+str(i).zfill(2)+'</span>'+h(name)+'</h2></div><span class="module-chevron">'+icon('chevron')+'</span></summary><div class="module-content"><span id="module-'+str(i)+'"></span>'+text+'<div class="module-footer"><a class="reader-link" href="#reader-top">回到档案总览</a></div></div></details>')
  assessment.append('<li>'+h(name)+'：'+str(n)+' 项项目事实；'+str(platform_total)+' 项平台条目；共 '+str(registered)+' / '+str(alln)+' 个已登记字段有值；'+('待补充记录'if not group else'仍需专业审核')+'</li>')
 source_html=[]
 for sid,x in sources.items():
  origin=x.get('origin',{});u=origin.get('url')or'';title=source_title(image_titles.get(sid)or mapping.get(u)or origin.get('filename')or x['title'])
  scope=x.get('read_scope','');label=READ_SCOPE_LABELS.get(scope,'核读范围待确认')
  source_html.append('<details class="paper-reading" id="source-'+h(sid)+'" tabindex="-1"><summary>'+icon('chevron')+'<div class="paper-reading-top"><span>'+h(label)+'</span><span>已保存来源文件</span></div><h3>'+h(title)+'</h3></summary><div class="paper-body"><p class="reader-note">登记原文件、机器转换与实际核读分别管理。来源编号 '+h(sid)+'</p><p class="source-actions"><a href="'+h(url('/asset',source=sid,kind='original'))+'">下载登记原文件</a><a href="'+h(url('/asset',source=sid,kind='document'))+'">查看可读来源</a></p>'+('<p><a href="'+h(u)+'" rel="noopener noreferrer" target="_blank">原始网站</a></p>'if u.startswith(('https://','http://'))else'')+'</div></details>')
 reference_items=''.join('<li class="reference-item" id="note-'+str(c['number'])+'"><b>注'+str(c['number'])+'</b> '+h(c['title'])+'<p>'+h(c['locator'])+' · '+h(c['scope'])+'</p><blockquote>'+h(c['quote'])+'</blockquote><a href="'+h(url('/asset',source=c['sid'],kind='original'))+'">查看登记原文件</a></li>'for c in citations)
 reference_html='<details class="paper-reading reference-index"><summary>逐字引文与出处</summary><p class="reader-note">正文使用注号定位；完整引文集中在这里，可按需展开核对。</p><ol class="reference-list">'+reference_items+'</ol></details>'if citations else''
 toc='<aside class="toc" id="toc" aria-label="阅读目录"><div id="toc-reader"><b>阅读目录</b><a href="#reader-top" data-reader-section="top">'+icon('overview')+'档案概览</a>'+''.join('<a href="#reader-'+key+'" data-reader-section="'+key+'">'+icon(key)+h(name)+'</a>'for key,name in zip(KEYS,pp.MODULES))+'<div class="toc-reading-appendix"><a href="#library-view" data-switch="library">'+icon('ip')+'资料与解读</a><a href="#assessment-view" data-switch="assessment">'+icon('governance')+'档案评估</a></div><div class="toc-note"><b>阅读说明</b>事实与平台解读分开，资料出处可逐条核对。</div></div></aside>'
 project_record=next((r for r in records if r['entity']=='project'),{})
 summary_cell=project_record.get('cells',{}).get('summary',{})
 overview=summary_cell['value']if summary_cell.get('value_state')=='known'and isinstance(summary_cell.get('value'),str)else'从需求与系统、设计思路到指标与验证，逐步了解这个项目。资料依据与平台解读分别呈现，引用可逐条核对。'
 hero='<div class="hero" id="workspace-content"><p class="workspace-context">项目档案　<a href="'+h(url('/'))+'">档案维护</a></p><div class="eyebrow">好设计 / 项目档案</div><h1>'+h(meta['name'])+'</h1><p class="summary">'+h(overview)+'</p><div class="reader-hero-meta"><span class="ui-badge">'+icon('award')+h('题录年份 '+str(meta.get('year')or'待补')+' · '+str(meta.get('award')or'奖项待补'))+'</span><span class="ui-badge pending">'+icon('info')+'待专业审核</span></div></div>'
 story='<div class="project-story"><div class="project-story-copy"><span class="ui-kicker">认识这个项目</span><h3>从项目事实，读到设计思路。</h3><p>先看需求与系统，再理解创新机制，最后核对指标与验证。事实与平台解读分开呈现，引用可逐条核对。</p></div><div class="generic-route">'+''.join('<a href="#reader-'+key+'">'+icon(key)+label+'</a>'for key,label in [('technical','需求与系统'),('innovation','设计思路'),('validation','指标与验证')])+'</div></div>'
 archive='<section data-panel="archive" id="reader-view"><div id="reader-top" tabindex="-1"><div class="reader-overview-heading"><h2>档案概览</h2><span class="ui-badge pending">'+icon('info')+'待专业审核</span></div>'+story+'<p class="reader-note">本档案含机器整理内容，尚未经人工逐条核读；引用时请核对资料出处。</p>'+evidence_notice+'</div><div class="module-list-heading"><h2>深入了解这个项目</h2><p>按主题阅读，资料出处可逐条核对</p></div>'+''.join(module_html)+'</section>'
 reading_guide=('<details class="reader-expand"><summary>档案阅读导读 · 平台整理</summary><p>'+h(guide_text(notes['overview']))+'</p><p class="reader-note">绑定 '+h(revision)+'；不是新增事实或专家结论。</p><a href="'+h(url('/api/research-document',document='guide',revision=revision,guide_version=notes['version']))+'">下载阅读导读</a></details>')if notes else''
 library='<section data-panel="library" id="library-view" hidden><div class="reader-view-heading"><h2>资料与解读</h2><p>从原始资料核对档案，实际核读范围单独标注。平台解读在相应档案模块中阅读。</p></div><span id="source-list"></span>'+reading_guide+reference_html+''.join(source_html)+('</section>')
 traceable=fact_count-incomplete_facts
 coverage=round(100*traceable/fact_count,1) if fact_count else 0
 platform_meta=sum(len(platform_cells(r,'platform_metadata')) for r in records)
 platform_analysis=sum(len(platform_cells(r,'platform_analysis')) for r in records)
 graph_url=graph_href or url('/dossier/graph/')
 composition_max=max(fact_count,platform_meta,platform_analysis,1)
 composition=''.join('<div class="assessment-composition-row"><span>'+label+'</span><div class="assessment-bar"><span style="width:'+f'{value/composition_max*100:.1f}'+'%"></span></div><b>'+str(value)+'</b></div>' for label,value in [('项目事实',fact_count),('平台元数据',platform_meta),('平台分析',platform_analysis)])
 module_cards=''.join('<article class="assessment-module-card"><h3>'+h(m['name'])+'</h3><b>'+str(m['traceable'])+' / '+str(m['facts'])+'</b><div class="assessment-bar"><span style="width:'+f'{m["traceable"]/m["facts"]*100 if m["facts"] else 0:.1f}'+'%"></span></div><p>'+('可追溯 / 项目事实' if m['facts'] else '暂无项目事实')+'</p></article>' for m in module_visuals)
 assessment_visual='<div class="assessment-visual"><div class="assessment-donut"><svg viewBox="0 0 120 120" role="img" aria-label="可追溯事实比例 '+str(coverage)+'%"><circle class="assessment-donut-track" cx="60" cy="60" r="48" pathLength="100"/><circle class="assessment-donut-value" cx="60" cy="60" r="48" pathLength="100" stroke-dasharray="'+str(coverage)+' '+str(100-coverage)+'" transform="rotate(-90 60 60)"/><text x="60" y="58" text-anchor="middle">'+str(coverage)+'%</text><text x="60" y="76" text-anchor="middle">可追溯</text></svg><p>'+str(traceable)+' / '+str(fact_count)+' 项事实具备完整证据</p></div><div class="assessment-summary"><h3>档案内容构成</h3>'+composition+'<p class="reader-note">可追溯比例只说明证据绑定状态，不代表研究完整、内容真实或专家认可。</p><a class="graph-link" href="'+h(graph_url)+'">查看项目知识图谱</a></div><div class="assessment-review"><h3>质量状态</h3><ol><li>机器整理：已完成</li><li>证据重绑：'+str(traceable)+' / '+str(fact_count)+' 项</li><li>当前评估：'+('已有绑定评估' if review_result['status']=='available' else '尚未形成有效评估')+'</li><li>人工核读与专家审核：未完成</li></ol></div><div class="assessment-modules">'+module_cards+'</div></div>'
 assessment_html='<section data-panel="assessment" id="assessment-view" hidden><span id="quality"></span><div class="reader-view-heading"><h2>档案评估与完善</h2><p>把整理情况、研究判断和仍需补充的资料分开查看。</p></div>'+assessment_visual+review_html+'<div class="research-box"><h3>字段登记统计</h3><p>当前研究版本：'+h(revision)+'。评估与导读必须绑定这个版本，内容变化后旧评估失效。</p><p>当前版本评估状态：'+('已有绑定评估' if review_result['status']=='available' else '尚未形成有效评估，旧评估不沿用')+'。</p><p>8 个阅读模块；'+str(filled)+' / '+str(total)+' 个已登记字段有值。填充率不代表项目研究完整度。</p><p>质量分：未评。专家审核：未完成。</p><ul>'+''.join(assessment)+'</ul>'+('<a href="'+h(url('/api/research-document',document='data',revision=revision))+'">下载本研究版本结构化档案</a>'if w['revision']else'')+'</div></section>'
 citation_print='<div class="citation-print"><h2>引用来源</h2><ol>'+''.join('<li>'+h(sid)+' · '+h(x['title'])+'</li>' for sid,x in sources.items())+'</ol></div>'
 citation_dialog='<dialog class="citation-dialog" id="citation-dialog" aria-labelledby="citation-title"><div class="citation-dialog-head"><h2 id="citation-title"></h2><button class="gd-button gd-button--quiet" id="citation-close" type="button">关闭</button></div><p class="citation-dialog-meta"><span id="citation-locator"></span><br><span id="citation-scope"></span></p><blockquote id="citation-quote"></blockquote><a id="citation-link" href="/inno/about/">查看完整来源</a></dialog>'
 return '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:,"><title>'+h(meta['name'])+' · 项目档案</title><style>'+READER_CSS+CSS+shared_css+'</style></head><body>'+header+'<div class="shell reader-shell">'+toc+'<main>'+hero+view_bar()+archive+library+assessment_html+citation_print+'<footer class="reader-note">好设计 · 项目档案</footer></main></div>'+citation_dialog+'<script>'+JS+'</script></body></html>'
