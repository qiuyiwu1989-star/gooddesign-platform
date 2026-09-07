from pathlib import Path
from html import escape as e
from html.parser import HTMLParser
import re,json,collections
ROOT=Path(__file__).resolve().parents[1]
NAV=[('projects.html','项目库'),('museum.html','好设计馆'),('education.html','科技教育'),('assist.html','智能助手'),('industry.html','企业创新')]
def page(title,kicker,body):return f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} · 好设计</title></head><body><main class="gd-main"><div class="gd-kicker">{kicker}</div>{body}</main></body></html>'
def card(title,desc,url):return f'<article class="gd-card"><h3><a href="/{url}">{title} ↗</a></h3><p>{desc}</p></article>'
def apply(pub):
 awards=json.loads((pub/'awards.json').read_text());rows=[]
 for x in awards:
  d=json.loads((pub/f"cases/detail/{x['slug']}.json").read_text())
  valid=lambda v:bool(str(v or '').strip()) and str(v).strip() not in ['无','待补充','暂无','暂无资料','-']
  links=[]
  for label,rel in [('课堂教案',f"lesson/{x['slug']}.html"),('拆解数据',f"dismantle/{x['slug']}.json")]:
   if (pub/rel).exists():links.append({'label':label,'path':rel})
  rows.append({**x,'hasDescription':valid(d.get('desc')),'hasFeatures':valid(d.get('features')),'hasParticipants':valid(d.get('participants')),'resources':links})
 (pub/'design/projects.json').write_text(json.dumps(rows,ensure_ascii=False))
 # Preserve the original museum experience while creating the overall platform home.
 (pub/'museum.html').write_text((pub/'index.html').read_text())
 featured=''.join(card(x['name'],f"{x['year']} · {x['level']} · {x['unit']}",f"project/{x['slug']}.html") for x in [awards[0],next(x for x in awards if x['slug']=='2021-s03'),next(x for x in awards if x['slug']=='2021-00')])
 (pub/'index.html').write_text(page('创新设计知识与应用平台','GOOD DESIGN / 知识 · 体验 · 创造',f'''<section class="gd-hero gd-feature"><div><h1>从一项好设计，<br>打开新的可能。</h1><p class="gd-lead">连接真实创新项目、设计知识与应用。理解它如何诞生，再探索它能带来什么。</p><div class="gd-actions"><a class="gd-btn primary" href="/projects.html">探索 {len(awards)} 项档案</a><a class="gd-btn" href="/industry-demo/">体验双环产业研究</a></div></div><figure><img src="/cases/case-2021-00.jpg" alt="星球车复合式移动系统项目"><figcaption>从真实问题出发 · 星球车复合式移动系统项目</figcaption></figure></section><section class="gd-section"><div class="gd-section-head"><h2>五种入口，一套知识</h2><a href="/design-system.html">我们的设计语言 ↗</a></div><div class="gd-grid">{card('项目库','查阅获奖背景、设计特点与资料；选择项目进行并列比较。','projects.html')}{card('好设计馆','走进主题展区，体验拆解、原理与再创作。','museum.html')}{card('科技教育','从项目课例到学科单元，让真实创新走进课堂。','education.html')}{card('智能助手','带着项目与任务提问，探索原理和设计取舍。','assist.html')}{card('企业创新','连接企业问题和案例方法，形成可验证的研究方向。','industry.html')}</div></section><section class="gd-section"><h2>从这些项目开始</h2><div class="gd-grid">{featured}</div></section><p class="gd-note">档案事实、设计解读和应用草案分层呈现。资料持续补充，来源与核验状态随内容展示。</p>'''))
 (pub/'projects.html').write_text(page('好设计奖项目库','01 / PROJECT LIBRARY','''<section class="gd-hero"><h1>看见成果，读懂创新。</h1><p class="gd-lead">以真实项目为中心，连接获奖记录、设计知识与可用资源。</p><div class="gd-actions"><a class="gd-btn" href="/award.html">奖项背景</a><a class="gd-btn" href="/laureates.html">原获奖名录</a></div></section><div class="gd-filters"><label class="gd-field">搜索项目或完成单位<input id="search" type="search" placeholder="例如：机器人、采样、天津大学"></label><label class="gd-field">年度<select id="year"><option value="">全部年度</option></select></label><label class="gd-field">奖项<select id="level"><option value="">全部奖项</option></select></label><label class="gd-field">资料条件<select id="quality"><option value="">全部项目</option><option value="description">有实质描述</option><option value="lesson">有课堂教案</option><option value="missing">描述待补充</option></select></label></div><p class="gd-status" id="count" role="status">正在载入项目…</p><div id="gd-compare" hidden></div><div class="gd-grid" id="results"></div><div class="gd-actions"><button id="more">查看更多</button></div><p class="gd-note">“有实质描述”仅表示排除了空值和占位词，不代表完成事实核验。比较基于档案字段，不生成优劣评分。</p><script src="/design/projects.js" defer></script>'''))
 lessons=[]
 for f in sorted((pub/'lesson').rglob('*.html')):
  if f.name=='index.html':continue
  s=f.read_text();title=re.search(r'<title>(.*?)</title>',s,re.S).group(1).split('—')[0].strip();lessons.append({'title':title,'path':str(f.relative_to(pub)),'kind':'unit' if 'units' in f.parts else 'lesson'})
 edu=''.join(f'<article class="gd-card" data-resource="{x["kind"]}"><span class="gd-tag">{"学科单元" if x["kind"]=="unit" else "项目单课"}</span><h3><a href="/{x["path"]}">{e(x["title"])} ↗</a></h3><p>历史课例 · 教师使用前需按课堂情况校准。</p></article>' for x in lessons)
 (pub/'education.html').write_text(page('科技教育','03 / LEARN THROUGH DESIGN',f'''<section class="gd-hero"><h1>让创新成为一堂课。</h1><p class="gd-lead">从真实工程问题到课堂探究，用证据表达设计想法。</p><div class="gd-actions"><a class="gd-btn primary" href="/teacher-workbench/">进入教师工作台</a><a class="gd-btn" href="/playground.html">学生互动探索</a><a class="gd-btn" href="/learn.html">原教育导览</a></div></section><section><h2>课程资源</h2><label class="gd-field">资源类型<select id="resource-type"><option value="all">全部课例与单元</option><option value="lesson">项目单课</option><option value="unit">学科单元</option></select></label><p id="resource-count" class="gd-status" role="status">{len(lessons)} 份资源</p><div class="gd-grid">{edu}</div></section><section class="gd-section"><h2>从准备到学习产出</h2><div class="gd-grid">{card('课堂课件','馆内课件与独立教师工具课件分别保留。','courseware/')}{card('学习任务护照','组织参观与探究任务，保留原体验。','passport.html')}{card('创作与反馈','用作品卡表达自己的设计；历史原型不等于联网班级系统。','workshop.html')}</div><div class="gd-actions"><a href="/education-tools/courseware/">教师工具配套课件 ↗</a><a href="/teacher-dash.html">本机教师看板 ↗</a></div></section><script src="/design/education.js" defer></script>'''))
 tasks=[('找项目','请帮我寻找与机器人模块化设计相关的好设计项目，区分有资料支持的内容与待核实信息。'),('懂项目','请解释嫦娥五/六号月球钻取采样项目解决的问题、设计取舍和已有资料的边界。'),('做比较','请比较两个机器人项目的设计问题与方法，缺少资料的地方请明确说明，不做无依据的性能排名。'),('做应用','请以一个有资料支持的项目，提出课堂探究任务，并区分档案事实与教学建议。')]
 (pub/'assist.html').write_text(page('智能助手','04 / DESIGN COMPANION','''<section class="gd-hero"><h1>带着一个好问题开始。</h1><p class="gd-lead">找案例、懂原理、看取舍。选择任务，在当前页面继续探索。</p><p class="gd-note">当前助手使用已有知识文本。回答需结合项目资料核对，尚未完成逐句证据检索。</p></section><div class="gd-grid">'''+''.join(f'<article class="gd-card"><h2>{t}</h2><p>{q}</p><button data-prompt="{e(q,quote=True)}">开始{t}</button></article>' for t,q in tasks)+'''</div><p id="gd-task-status" role="status"></p><div class="gd-actions"><a class="gd-btn" href="/assistant.html">打开原版助手</a><a class="gd-btn" href="/projects.html">先选择一个项目</a></div><script src="/copilot.js" defer></script>'''))
 (pub/'industry.html').write_text(page('企业创新','05 / INDUSTRY INNOVATION','''<section class="gd-hero"><h1>从企业的问题，<br>走向可验证的机会。</h1><p class="gd-lead">把企业能力与真实案例中的方法连接起来，形成研究假设和下一步验证。</p><div class="gd-actions"><a class="gd-btn primary" href="/industry-demo/">体验好设计 × 双环</a><a class="gd-btn" href="/connect.html">提交企业合作需求</a></div></section><section><h2>一项研究如何发生</h2><div class="gd-grid">'''+card('01 认识企业','确认主体、业务范围和公开资料；避免同名企业与不同业务混用。','industry-demo/')+card('02 连接案例','按问题与方法寻找证据，识别迁移条件与资料缺口。','projects.html')+card('03 形成验证','让机会卡包含假设、所需资料、验证动作及观察指标。','industry-demo/')+'''</div></section><section class="gd-section"><h2>先把问题写清楚</h2><p>制作一张可带入讨论的需求卡。内容保留在当前页面，下载前不会提交到服务器。</p><form id="need-form"><div class="gd-grid"><label class="gd-field">企业名称<input name="company" required maxlength="100"></label><label class="gd-field">业务 / 场景<input name="scene" required maxlength="150"></label><label class="gd-field">希望改善的结果<input name="goal" required maxlength="300"></label></div><label class="gd-field">当前问题与已有尝试<textarea name="problem" required maxlength="2000"></textarea></label><label class="gd-field">约束与可提供的资料<textarea name="constraints" maxlength="2000"></textarea></label><div class="gd-actions"><button class="primary" type="submit">生成并下载需求卡</button></div></form><p id="need-status" role="status"></p><pre id="need-preview" hidden style="white-space:pre-wrap;font:inherit"></pre></section><script src="/design/industry.js" defer></script>'''))
 tokens=[('纸色','--gd-paper','#f6f3eb'),('深蓝','--gd-blue','#244875'),('印章红','--gd-red','#a83b2e'),('正文墨色','--gd-ink','#172c3c'),('证据绿','--gd-green','#31634d'),('待核实琥珀','--gd-amber','#805b24')]
 (pub/'design-system.html').write_text(page('设计系统','GOOD DESIGN / DESIGN SYSTEM 1.0','''<section class="gd-hero"><h1>有依据，也有温度。</h1><p class="gd-lead">以真实创新为内容中心，以清晰的层级、可追溯的证据和一致的交互建立信任。</p></section><h2>品牌色与语义</h2><div class="gd-grid">'''+''.join(f'<div class="gd-card"><div class="gd-swatch" style="background:var({v})"></div><h3>{n}</h3><p>{v} · {c}</p></div>' for n,v,c in tokens)+'''</div><section class="gd-section"><h2>文字与布局</h2><p>标题使用宋体气质，正文使用系统无衬线。内容宽度1200px；间距以4 / 8 / 12 / 16 / 24 / 32 / 48为基础；卡片圆角8px，控件4px。800px进入折叠菜单，480px单列。</p></section><section class="gd-section"><h2>组件与状态</h2><div class="gd-actions"><button class="primary">主要操作</button><button>次要操作</button><button disabled>不可用</button><a class="gd-btn" href="/projects.html">文本入口 ↗</a></div><span class="gd-tag">来源资料</span><span class="gd-tag draft">分析草案 · 待核实</span><p class="gd-note">标签表达资料性质，不用颜色代替文字，不将展示状态当成审核结论。</p><label class="gd-field">输入与焦点示例<input placeholder="使用 Tab 检查键盘焦点"></label></section><section class="gd-section"><h2>页面模式</h2><p>平台首页：定位与分流。板块首页：任务与资源。项目详情：事实、解读与应用关联。工作台：步骤、输入、依据与产物。专用课件与展项保留画布，在公共外框内运行。</p><h2>内容约定</h2><p>每个项目保持唯一身份；同一来源可以支撑多个知识条目；课程、展项引用项目。空值、无、待补充均作为资料缺口。事实、解读、草案分层呈现。</p></section>'''))
 # Shared static shell on every published HTML; retain local controls and body scripts.
 manifest=[]
 for f in list(pub.rglob('*.html')):
  rel=str(f.relative_to(pub));s=f.read_text()
  # remove old brand navigation only, leaving lesson controls and step navigation intact
  s=re.sub(r'<nav\b[^>]*>.*?</nav>',lambda m:'' if 'class="brand"' in m.group(0) else m.group(0),s,flags=re.S|re.I)
  s=re.sub(r'<a\b([^>]*?)href="backstage/biomimetic-blender-report.html"[^>]*>(.*?)</a>',r'<span>\2（内部资料）</span>',s,flags=re.S)
  section='projects.html' if rel.startswith(('project/','atom/')) or rel in ['projects.html','laureates.html','award.html'] else 'education.html' if rel.startswith(('lesson/','courseware/','education-tools/','teacher-workbench/')) or rel in ['education.html','learn.html','workshop.html','teacher-dash.html','passport.html'] else 'assist.html' if rel in ['assist.html','assistant.html'] else 'industry.html' if rel.startswith('industry-demo/') or rel in ['industry.html','connect.html','migration-report.html'] else 'museum.html'
  if rel in ['index.html','design-system.html']:section=''
  label=dict(NAV).get(section,'平台')
  header='<a class="gd-skip" href="#gd-content">跳到内容</a><div id="gd-shell" class="gd-header"><a class="gd-brand" href="/"><img src="/assets/brand/logo-seal.svg" alt="">好设计</a><button id="gd-menu" class="gd-menu" aria-expanded="false" aria-controls="gd-nav">菜单</button><div class="gd-nav" id="gd-nav" role="navigation" aria-label="全站导航">'+''.join(f'<a href="/{url}"'+(' aria-current="page"' if url==section else '')+f'>{name}</a>' for url,name in NAV)+'</div></div>'
  header+=f'<div class="gd-crumb" id="gd-content" tabindex="-1"><a href="/">好设计平台</a> / <a href="/{section or "index.html"}">{label}</a></div>'
  footer='<div class="gd-footer"><span>好设计 · 创新设计知识与应用平台<br>档案、解读与应用内容分层呈现。</span><span><a href="/design-system.html">设计系统</a> · <a href="/award.html">奖项背景</a> · <a href="https://cgd.cmes.org" target="_blank" rel="noopener">官方信息</a></span></div>'
  if re.search(r'<head\b',s,re.I):s=re.sub(r'</head>', '<link rel="stylesheet" href="/design/system.css"></head>',s,count=1,flags=re.I)
  else:s='<link rel="stylesheet" href="/design/system.css">'+s
  match=re.search(r'<body\b[^>]*>',s,re.I)
  if match:
   tag=match.group(0)
   if re.search('class=',tag):tag=re.sub(r'class="([^"]*)"',r'class="\1 gd-site"',tag)
   else:tag=tag[:-1]+' class="gd-site">'
   s=s[:match.start()]+tag+header+s[match.end():]
  else:
   # Original industry fragment has no explicit body; insert after styles, ahead of its header.
   pos=s.find('<header>');s=s[:pos]+'<body class="gd-site">'+header+s[pos:]
  related=''
  if rel=='museum.html':
   related='<section class="gd-related"><h2>把参观延伸成一次探索</h2><p>建议路线：先看项目，再理解原理，最后带入课堂或产业问题。</p><a href="/project/2021-00.html">星球车：从地形约束理解设计</a><a href="/x-ray.html">进入拆解实验室</a><a href="/education.html">继续课堂探究</a><a href="/industry-demo/">探索机器人产业方法</a></section>' 
  if rel.startswith(('project/','atom/')) and f.stem!='index':
   x=next((x for x in rows if x['slug']==f.stem),None)
   if x:
    related='<aside class="gd-related"><h2>项目知识与应用</h2><p>资料状态：'+('有实质描述' if x['hasDescription'] else '描述待补充')+' · 本轮未逐条重新官方核验。历史页面中的核验与评分为原稿记录。</p>'+f'<a href="/project/{x["slug"]}.html">项目档案</a><a href="/atom/{x["slug"]}.html">知识详情</a>'+''.join(f'<a href="/{r["path"]}">{r["label"]}</a>' for r in x['resources'])+'<a href="/projects.html">搜索与比较项目</a></aside>'
  inject=related+footer+'<script src="/design/shell.js" defer></script>'
  if '</body>' in s.lower():s=re.sub('</body>',inject+'</body>',s,count=1,flags=re.I)
  else:s+=inject+'</body>'
  f.write_text(s);manifest.append({'path':rel,'section':section or 'platform'})
 (ROOT/'00-项目管理/设计系统页面清单.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
 return len(manifest)
