# coding: utf-8
"""027 public-field-only static preview. No production files or private sources exported."""
import html,json,re,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];PUBLIC=ROOT/'original-app/public';CASE=ROOT/'04-知识库/标杆案例/2025-00-嫦娥钻取采样';OUT=ROOT/'output/inno-preview/inno';ASSETS=ROOT/'extensions/inno'
e=lambda v:html.escape(str(v or ''),quote=True)
NAV=[('','首页'),('awards/','好设计奖'),('projects/','项目库'),('museum/','好设计馆'),('education/','科技教育'),('industry/','企业创新')]
def nav(active):return '<a class="skip-link" href="#content">跳到正文</a><div class="inno-nav"><a class="inno-brand" href="/inno/">创新设计<span>INNO</span></a><nav aria-label="主导航">'+''.join('<a href="/inno/'+p+'"'+(' aria-current="page"'if p==active else '')+'>'+name+'</a>'for p,name in NAV)+'</nav><span class="preview-label">本地预览</span></div>'
def footer():return '<footer class="inno-footer"><b>创新设计 · 从真实项目出发</b><span>公开资料整理 · 研究与审核持续进行</span><a href="/inno/about/">平台与资料说明</a></footer>'
def shell(title,body,active='projects/',script=''):
 return '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+e(title)+' · 创新设计</title><link rel="icon" href="data:,"><link rel="stylesheet" href="/inno/assets/site.css"></head><body>'+nav(active)+'<main id="content" class="page">'+body+'</main>'+footer()+script+'</body></html>'
def write(rel,text):
 p=OUT/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')
def badge(row):return '<span class="badge research">研究档案 · 待复核</span>'if row['research']else '<span class="badge">基础资料</span>'
def cover(row,cls=''):
 return '<img class="'+cls+'" src="/inno/'+e(row['cover'])+'" alt="'+e(row['name'])+' · 原库项目图" loading="lazy">'if row['cover']else '<div class="no-cover '+cls+'"><span>'+e(row['year'])+'</span><b>'+e(row['award'])+'</b><small>暂无项目封面</small></div>'
def feature(row):return '<section class="featured"><div class="featured-media">'+cover(row)+'<span>原库项目示意</span></div><div class="featured-copy"><span class="eyebrow">从一份研究档案开始</span><h2>嫦娥月球钻取采样系统</h2><p>从月球采样任务，读懂系统设计、关键取舍与验证过程。再沿着资料与解读，找到每一项判断的依据。</p><div class="feature-tags"><span>8 个档案模块</span><span>23 份参考资料</span><span>待专业复核</span></div><a class="button primary" href="/inno/projects/2025-00/" data-project-link>阅读项目档案 <span aria-hidden="true">↗</span></a><span class="featured-note">档案自评 55/100 · 不代表项目技术评分</span></div></section>'
def basic_detail(row,detail):
 modules=['项目概况','需求与系统','设计思路','指标与验证','专利与论文','历程与故事','应用与价值','质量与维护'];sid='legacy-'+row['id']
 props='<dl class="properties">'+''.join('<div><dt>'+key+'</dt><dd>'+e(value or '暂无资料')+'</dd></div>'for key,value in [('获奖年份',row['year']),('奖项',row['award']),('完成单位',row['unit']),('原库登记完成人',detail.get('participants')),('项目编号',row['id'])])+'</dl>'
 sections=[]
 for i,name in enumerate(modules,1):
  value=detail.get({1:'desc',3:'features'}.get(i,''))
  text='<p class="note">原库字段摘录 · 尚待核验与研究整合</p><div class="source-excerpt">'+''.join('<p>'+e(x)+'</p>'for x in value.splitlines()if x.strip())+'</div>'if isinstance(value,str)and value.strip()not in ['', '无','暂无','暂无资料','待补充']else '<div class="gap-state"><b>这一部分还有待补充</b><p>保留研究维度，后续从原始资料中补证、整理并审核。</p></div>'
  sections.append('<details class="case-module" id="module-'+str(i)+'"><summary><span class="number">%02d</span><h2>'%i+name+'</h2><span class="module-open">展开</span></summary><div class="module-body">'+(props if i==1 else '')+text+'</div></details>')
 side='<aside class="case-toc" aria-label="项目阅读目录"><b>阅读目录</b><a href="#case-top" data-module="top" aria-current="location">档案概览</a>'+''.join('<a href="#module-'+str(i)+'" data-module="'+str(i)+'">%02d　'%i+name+'</a>'for i,name in enumerate(modules,1))+'<div class="toc-more"><button data-case-tab="library">资料与解读</button><button data-case-tab="assessment">档案评估</button></div><p>原始条目已接入<br>研究与审核尚待开展</p></aside>'
 head='<div class="case-heading"><a class="back-link" href="/inno/projects/" data-back>← 返回项目库</a><div class="breadcrumb">项目库 / '+e(row['year'])+' / '+e(row['award'])+'</div><h1>'+e(row['name'])+'</h1><div class="case-meta">'+badge(row)+'<span>'+e(row['year'])+' · '+e(row['award'])+'</span><span>'+e(row['id'])+'</span></div><p class="case-intro">本页先保留公开条目与来源；设计机制、参数验证和成果归属将在研究后补充。</p></div>'
 tab='<div class="case-tabs" role="group" aria-label="项目阅读方式"><button data-case-tab="archive" aria-pressed="true">项目档案</button><button data-case-tab="library" aria-pressed="false">资料与解读</button><button data-case-tab="assessment" aria-pressed="false">档案评估</button><button class="case-print" onclick="window.print()">打印</button></div>'
 archive='<div id="archive-panel"><section id="case-top" class="case-overview"><div>'+cover(row)+'<span class="note">原库项目图；暂无封面时保留空缺</span></div><article><span class="eyebrow">项目概览</span><h2>项目介绍</h2><p>'+e(row['summary']or '项目介绍尚待补充。')+'</p><p class="note">来自原库公开资料，后续继续补充与核验。</p></article></section><h2 class="section-title">项目档案</h2>'+''.join(sections)+'</div>'
 source_url='https://gooddesign.qiuyiwu.com/cases/detail/'+row['id']+'.json'
 library='<div id="library-panel" hidden><div class="section-heading"><h2>资料与解读</h2><p>原始条目先归档，资料解读将在核读后补充。</p></div><article class="source-card"><span class="eyebrow">原库公开资料</span><h3>'+e(row['name'])+'</h3><p>来源：既有好设计网站项目条目。该记录含项目介绍及其他公开登记字段；原库陈述仍需进一步核验。</p><a class="text-link" href="'+source_url+'" target="_blank" rel="noopener">查看旧站公开原始条目 JSON ↗</a></article><div class="gap-state"><b>论文、专利与其他资料解读</b><p>尚未开展本页的逐项研究，不以原库“已收录”代替全文核读。</p></div></div>'
 assessment='<div id="assessment-panel" hidden><div class="section-heading"><h2>档案评估</h2><p>评价档案研究质量；目前不生成未经依据支持的分数。</p></div><div class="assessment-empty"><div><span>—<small>/100</small></span><b>尚未评价</b></div><p>基础资料已接入。事实补证、设计解读、成果关联与专业审核尚待开展。</p></div><h3>下一步补充</h3><ul class="next-list"><li>核对项目身份、完成单位与获奖记录。</li><li>整理需求、约束、系统方案和关键设计机制。</li><li>补充专利、论文、指标、试验与应用证据。</li><li>形成质量依据，记录内容修订并安排审核。</li></ul></div>'
 return shell(row['name'],'<div class="case-layout">'+side+'<div class="case-main">'+head+tab+archive+library+assessment+'</div></div>',script='<script src="/inno/assets/case.js"></script>')
def curated():
 text=(CASE/'档案.html').read_text(encoding='utf-8')
 text=re.sub(r'<header>.*?</header>',nav('projects/'),text,count=1,flags=re.S)
 text=text.replace('</head>','<link rel="stylesheet" href="/inno/assets/site.css"><style>.inno-nav{font:14px/1.7 var(--ui-font);position:sticky;top:0;z-index:30}.inno-nav nav a{font-size:13px}.inno-nav .inno-brand{font-size:20px}.reader-shell .hero{padding-top:24px}.reader-shell .toc{top:96px;max-height:calc(100vh - 112px)}#view-bar{top:72px}.reader-tools{display:none}.reader-shell [id],#reader-top,#reader-view,#library-view,#assessment-view{scroll-margin-top:160px}.back-library{display:block;margin:8px 0 18px;font-size:12px;color:var(--accent)}@media(max-width:850px){.reader-shell .hero{padding-top:20px}}@media(max-width:700px){#view-bar{top:112px}.reader-shell [id],#reader-top,#reader-view,#library-view,#assessment-view{scroll-margin-top:192px}}@media print{.inno-nav,.back-library{display:none!important}}</style></head>')
 text=text.replace('<div class="hero">','<div class="hero" id="content"><a class="back-library" href="/inno/projects/" data-back>← 返回项目库</a>',1)
 # HTML contains all reading data already. Do not export local research JSON/snapshots or raw attachments.
 def quiet(match):
  href=match.group(1)
  if not href.startswith(('http:','https:','#','mailto:'))and href!='项目图谱.html':return 'aria-disabled="true" title="此预览仅开放阅读，研究文件未导出"'
  return match.group()
 text=re.sub(r'href="([^\"]+\.(?:json|csv|md|pdf)(?:[^\"]*)?)"',quiet,text)
 text=text.replace('</body>','<script src="/inno/assets/return.js"></script></body>')
 return text

def build():
 OUT.mkdir(parents=True,exist_ok=True)
 (OUT/'assets').mkdir(exist_ok=True)
 for name in ['site.css','library.js','case.js','return.js']:
  shutil.copy2(ASSETS/name,OUT/'assets'/name)
 awards=json.loads((PUBLIC/'awards.json').read_text());rows=[];details={}
 for a in awards:
  pid=a['slug'];assert re.fullmatch(r'[A-Za-z0-9_-]+',pid)
  p=PUBLIC/'cases/detail'/(pid+'.json');d=json.loads(p.read_text())if p.exists()else {};details[pid]=d
  cover_path=a.get('cover')or '';cover_file=PUBLIC/cover_path
  if cover_path and cover_file.is_file()and cover_file.resolve().is_relative_to((PUBLIC/'cases').resolve()):
   target=OUT/cover_path;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(cover_file,target)
  else:cover_path=''
  desc=d.get('desc')or a.get('summary')or '';desc=''if desc.strip()in ['暂无','无','待补充','暂无资料']else desc
  rows.append(dict(id=pid,name=a['name'],year=a['year'],award=a['level'],unit=a.get('unit',''),summary=desc[:230].strip(),cover=cover_path,research=pid=='2025-00'))
 assert len(rows)==len({r['id']for r in rows})==560
 write('catalog.json',json.dumps(rows,ensure_ascii=False,separators=(',',':')))
 years=sorted({x['year']for x in rows},reverse=True);levels=list(dict.fromkeys(x['award']for x in rows));special=next(x for x in rows if x['research'])
 controls='<section class="library-controls" aria-label="检索项目"><div class="collection-heading"><div><h2>全部项目</h2><span id="result-count" role="status" aria-live="polite">560 项</span></div><p>先按年份和奖项浏览，也可以搜索项目名称或完成单位。</p></div><form id="filters" role="search"><label class="search-field"><span>搜索项目</span><div><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10" cy="10" r="6"/><path d="m15 15 5 5"/></svg><input type="search" id="search" placeholder="搜索项目、完成单位或关键词" autocomplete="off"></div></label><label>获奖年份<select id="year"><option value="">全部年份</option>'+''.join('<option>'+str(y)+'</option>'for y in years)+'</select></label><label>奖种<select id="award"><option value="">全部奖种</option>'+''.join('<option>'+e(l)+'</option>'for l in levels)+'</select></label><label>资料状态<select id="status"><option value="">全部项目</option><option value="research">研究档案</option><option value="basic">基础资料</option></select></label><button class="clear-filter" type="button" id="clear">重置</button></form><div class="results-tools"><p id="filter-hint">研究档案仍待专业复核；基础资料将按统一规范持续补充。</p><button class="text-link" id="only-research" type="button">只看研究档案 ↗</button></div></section>'
 library='<div class="library-intro"><div><div class="breadcrumb">创新设计 / 项目库</div><h1>从项目中，读懂创新。</h1><p>汇集好设计获奖项目，逐步建立有结构、可追溯的创新档案。</p></div><div class="collection-total"><b>560</b><span>获奖项目条目</span><small>原库收录，不等于深研完成</small></div></div>'+feature(special)+controls+'<div class="project-grid" id="project-grid"></div><div id="empty-state" class="empty-state" hidden><h3>暂时没有符合条件的项目</h3><p>试试更短的关键词，或清除筛选。</p><button class="button" id="empty-clear">清除筛选</button></div><div class="pagination" id="pagination"><button id="previous">← 上一页</button><span id="page-state"></span><button id="next">下一页 →</button></div><noscript>项目筛选需要JavaScript。可先<a href="/inno/projects/2025-00/">阅读嫦娥研究档案</a>。</noscript>'
 write('projects/index.html',shell('项目库',library,script='<script src="/inno/assets/library.js"></script>'))
 for row in rows:write('projects/'+row['id']+'/index.html',curated()if row['research']else basic_detail(row,details[row['id']]))
 graph=(CASE/'项目图谱.html').read_text();graph=graph.replace('档案.html','./');graph=re.sub(r'href="(?:项目图谱|图谱调用样例)\.json"','aria-disabled="true" title="本预览仅供阅读"',graph);write('projects/2025-00/项目图谱.html',graph)
 home='<section class="home-hero"><span class="eyebrow">创新设计 · 从真实项目出发</span><h1>让创新经验，<br>成为下一次设计的起点。</h1><p>以好设计项目为起点，理解问题、设计机制与验证过程，连接展览、教育和企业创新。</p><a class="button primary" href="/inno/projects/">探索项目库 ↗</a></section>'+feature(special)+'<section class="home-apps"><h2>让项目知识进入更多场景</h2><div>'+''.join('<a href="/inno/'+slug+'/"><span>0'+str(i)+'</span><h3>'+title+'</h3><p>'+desc+'</p><b>了解更多 ↗</b></a>'for i,(slug,title,desc)in enumerate([('museum','好设计馆','通过主题展览与项目故事，理解设计的价值。'),('education','科技教育','从真实工程问题出发，探索科学原理与学习活动。'),('industry','企业创新','带着企业问题，研究可借鉴的机制与验证路径。')],1))+'</div></section>'
 write('index.html',shell('首页',home,active=''))
 pages={
 'awards':('好设计奖','从获奖记录，回到真实项目。','了解好设计奖与历届成果，以年份和奖种进入项目库。','历届项目名录','/inno/projects/','现有奖项介绍','https://gooddesign.qiuyiwu.com/award.html'),
 'museum':('好设计馆','在展览中，看见创新的来路。','围绕主题组织项目、故事与设计原理；展项与项目档案共享来源。','探索相关项目','/inno/projects/','打开现有好设计馆','https://gooddesign.qiuyiwu.com/'),
 'education':('科技教育','让真实项目成为学习的起点。','学生探索原理，教师组织活动；课程与项目资料互相连接。','从项目库选一个主题','/inno/projects/','查看现有教育内容','https://gooddesign.qiuyiwu.com/learn.html'),
 'industry':('企业创新','从企业问题，寻找可借鉴的设计。','研究需求、约束与项目机制的关联，将候选方案落实为可检验的假设。','看割胶机器人迁移试读','/inno/projects/2025-00/项目图谱.html','打开现有企业创新演示','https://gooddesign.qiuyiwu.com/industry-demo/'),
 'about':('平台说明','围绕真实项目，持续积累知识。','底座由项目档案数据库、设计创新引擎和应用能力组成。当前先完善项目档案、资料来源与研究标准。','浏览项目库','/inno/projects/','查看现有网站','https://gooddesign.qiuyiwu.com/')}
 for slug,(title,line,intro,cta,target,old,oldurl)in pages.items():
  body='<div class="section-hero"><span class="eyebrow">创新设计 / '+title+'</span><h1>'+line+'</h1><p>'+intro+'</p><a class="button primary" href="'+target+'">'+cta+' ↗</a></div><section class="bridge-panel"><h2>'+title+' · 已有内容</h2><p>本页先建立统一入口。现有内容可在原网站继续浏览，后续逐步接入同一份项目档案。</p><a class="text-link" href="'+oldurl+'" target="_blank" rel="noopener">'+old+' ↗（原站）</a></section>'
  if slug=='about':body+='<section class="bridge-panel"><h2>资料与研究状态</h2><p>原库共有560条获奖项目。本预览中，嫦娥提供已整理的研究档案，仍待专业复核；其余项目以公开基础资料呈现。原库陈述、平台解读和应用假设分别标注。</p><p>原始素材与私有研究目录不在预览发布清单中。格式转换不是事实核验，档案质量自评不评价项目技术水平。</p></section>'
  write(slug+'/index.html',shell(title,body,active=slug+'/'))
 write('laureates.html','<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=/inno/projects/"><title>历届项目</title><a href="/inno/projects/">进入项目库</a></html>')
 report=dict(projects=len(rows),research_dossiers=sum(r['research']for r in rows),basic_entries=sum(not r['research']for r in rows),covers=sum(bool(r['cover'])for r in rows),export_scope='published_legacy_fields_and_reader_html_only',private_sources_exported=False,base='/inno/')
 write('build-report.json',json.dumps(report,ensure_ascii=False,indent=2));return report
if __name__=='__main__':print(json.dumps(build(),ensure_ascii=False))
