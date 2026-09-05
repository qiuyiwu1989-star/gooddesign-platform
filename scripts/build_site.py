from pathlib import Path
import json, re, shutil, collections, html, csv
R=Path(__file__).resolve().parents[1]; SRC=R/'99-历史项目快照/good-design/public'; OUT=R/'site'
OUT.mkdir(exist_ok=True)
exclude={'backstage','outputs','materials'}
private={'architecture.html','report.html','brand.html','exhibition-summary.html','exhibit-guide.html'}
replaced={'index.html','assistant.html','connect.html','migration-report.html','laureates.html'}
rows=[]
for p in SRC.rglob('*'):
 if not p.is_file():continue
 rel=p.relative_to(SRC); parts=rel.parts
 internal=parts[0] in exclude or str(rel) in private or str(rel)=='atom/index.html' or p.suffix in {'.md','.pdf','.pptx'}
 rows.append({'path':str(rel),'bytes':p.stat().st_size,'category': '内部资料' if internal else ('新版入口替换' if str(rel) in replaced else ('项目档案' if parts[0]=='project' else '知识页' if parts[0]=='atom' else '应用与资源')),'publish':not internal})
 if internal:continue
 target=OUT/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
awards=json.loads((SRC/'awards.json').read_text()); counts=collections.Counter(a['level'] for a in awards)
atoms=list((R/'99-历史项目快照/good-design/.build/atoms').glob('*.json'))
(R/'00-项目管理/公开内容资产清单.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
with (R/'00-项目管理/公开内容资产清单.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
nav='''<header class="gd-header"><a class="gd-brand" href="/index.html"><img src="/assets/brand/good-design-mark.png" alt="" onerror="this.hidden=true"><span>好设计<small>GOOD DESIGN</small></span></a><nav class="gd-nav" aria-label="主导航"><a href="/projects.html">项目库</a><a href="/knowledge.html">知识库</a><a href="/applications.html">应用</a><a href="/about.html">关于平台</a></nav><a class="gd-search" href="/projects.html#search">搜索作品 ↗</a></header>'''
# Reuse the actual existing brand asset.
brand=list((SRC/'assets/brand').glob('*')); print('brand assets',[x.name for x in brand])
if brand:
 pick=SRC/'assets/brand/logo-seal.svg';nav=nav.replace('good-design-mark.png',pick.name)
footer='''<footer class="gd-footer"><a href="/index.html">好设计 · 创新设计知识平台</a><p>基于公开资料整理的项目探索站。奖项信息以<a href="https://cgd.cmes.org/exhibit/home" target="_blank" rel="noopener">好设计官方发布</a>为准。设计解读与知识草稿不代表官方评审意见。</p><a href="/about.html#sources">内容来源与使用说明 ↗</a></footer>'''
css='''
:root{--gd-paper:#fafaf7;--gd-ink:#182528;--gd-muted:#566366;--gd-blue:#2d4faf;--gd-line:#dce1df;--gd-soft:#eff2f4;--gd-radius:10px}
.gd-header,.gd-footer,.gd-note{font-family:"PingFang SC","Microsoft YaHei",Arial,sans-serif!important;box-sizing:border-box}
.gd-header{position:relative;z-index:200;display:flex;align-items:center;gap:32px;padding:20px max(24px,calc((100% - 1240px)/2));background:var(--gd-paper);border-bottom:1px solid var(--gd-line);color:var(--gd-ink);min-height:82px}
.gd-header a{text-decoration:none;color:var(--gd-ink)}.gd-brand{display:flex;gap:10px;align-items:center;min-width:142px;font-size:23px;font-weight:700;line-height:1.1}.gd-brand img{width:34px;height:34px;object-fit:contain}.gd-brand small{display:block;font-size:8px;letter-spacing:2px;margin-top:6px}.gd-nav{all:unset;display:flex;gap:30px;margin:auto;align-items:center;font-size:14px;white-space:nowrap}.gd-nav a:hover,.gd-footer a:hover{color:var(--gd-blue)}.gd-search{font-size:13px;white-space:nowrap}.gd-footer{padding:42px max(24px,calc((100% - 1240px)/2));border-top:1px solid var(--gd-line);font-size:12px;color:var(--gd-muted);background:var(--gd-paper);line-height:1.9}.gd-footer a{color:inherit;text-decoration:none}.gd-footer p{max-width:720px;margin:14px 0}.gd-note{background:#edf1f7;color:#30466b;border-bottom:1px solid #d3ddeb;padding:12px 24px;font-size:12px;line-height:1.7;text-align:center}.gd-note a{color:inherit}.gd-skip{position:absolute;left:-9999px}.gd-skip:focus{left:12px;top:12px;z-index:1000;background:#fff;padding:12px}*:focus-visible{outline:3px solid #2d4faf;outline-offset:4px}
@media(max-width:680px){.gd-header{padding:16px 20px;gap:16px;flex-wrap:wrap;min-height:104px}.gd-brand{font-size:20px;min-width:120px}.gd-brand img{width:28px;height:28px}.gd-search{margin-left:auto}.gd-nav{order:3;flex-basis:100%;gap:0;justify-content:space-between;font-size:13px}.gd-note{text-align:left;padding:12px 20px}}
'''
(OUT/'platform.css').write_text(css)
# Existing app/detail pages retain routes and content; retire private navigation and external fonts.
for p in OUT.rglob('*.html'):
 rel=str(p.relative_to(OUT));s=p.read_text()
 s=re.sub(r'<link\b[^>]*(?:fonts\.googleapis|fonts\.gstatic)[^>]*>','',s)
 s=re.sub(r'<nav\b[^>]*>.*?</nav>',nav,s,count=1,flags=re.S)
 if 'class="gd-header"' not in s:s=re.sub(r'(<body[^>]*>)',r'\1'+nav,s,count=1)
 if rel=='x-ray.html':
  s=s.replace('<div class="tip">校准模式:', '<div class="tip" hidden>校准模式:').replace('id="calBtn" type="button"','id="calBtn" type="button" hidden')
 s=s.replace('</head>','<link rel="stylesheet" href="/platform.css"></head>')
 s=re.sub(r'backstage/[a-zA-Z0-9_-]+\.html','about.html',s)
 s=s.replace('查看规划汇报','了解平台').replace('打开方案中心','了解平台').replace('查看迁移样板','了解应用方向')
 s=s.replace('index.html?ask=', 'assistant.html?ask=')
 if rel=='workshop.html':
  s=s.replace('作品广场','作品预览').replace('发布到这里让更多人看见','制作设计卡与同伴讨论').replace('分享链接的作品会出现在这里','仅显示当前链接中的作品与教学示例；点赞保存在本机').replace('发布到广场','生成分享链接').replace('问 AI 助手','查项目资料').replace('把你的想法讲给好设计助手,让它帮你想方案、找漏洞、迭代三版。','从项目库中寻找相关作品，比较原理和约束，再完善自己的想法。')
  s=s.replace('JSON.parse(decodeURIComponent(w))','JSON.parse(w)')
 if rel=='playground.html':s=s.replace('发布到广场','生成分享链接')

 # No backend/cost-bearing requests are enabled in the first static release.
 s=re.sub(r'<a\b([^>]*?)href=["\']([^"\']*(?:backstage/|materials/|outputs/|architecture.html|report.html|brand.html|exhibition-summary.html|exhibit-guide.html|atom/index.html)[^"\']*)["\']([^>]*)>(.*?)</a>',lambda m:'<span title="该内部资料暂不公开">'+m[4]+'</span>',s,flags=re.S)
 if rel.startswith('atom/'):
  s=s.replace('已核验','历史标注·待复核').replace('已验证','待复核').replace('技术体系已实际拓展应用','历史迁移设想，实际应用状态待核实')
  note='知识整理稿 · 历史字段与AI解读尚需逐条复核；页面数量不代表已完成原子化。'
 elif rel.startswith('project/'):note='项目档案 · 按历史收录资料展示，设计解读不代表官方评价。<a href="/projects.html">返回项目库 ↗</a>'
 else:note='好设计应用体验 · 互动模拟用于理解设计原理，不作为工程参数或专业仿真依据。'
 s=s.replace('</header>','</header><div class="gd-note">'+note+'</div>',1)
 s=s.replace('</body>',footer+'<script src="/platform-bridge.js" defer></script></body>')
 p.write_text(s)
(OUT/'platform-bridge.js').write_text('''document.addEventListener('click',function(e){var a=e.target.closest('[data-copilot],[data-ask]');if(a){e.preventDefault();location.href='/assistant.html';}},true);document.querySelectorAll('a[href]').forEach(a=>{const u=new URL(a.href,location.href);if(u.origin===location.origin&&u.pathname.endsWith('/index.html')&&u.pathname.includes('/atom/'))a.href='/knowledge.html';});''')
(OUT/'copilot.js').write_text('''/* Static launch: use the project search. Generative assistant is not enabled. */window.GoodCopilot={open:function(){location.href='/assistant.html';}};''')
def page(name,title,body,script=''):
 s=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} · 好设计</title><meta name="description" content="从优秀作品理解创新设计。探索好设计项目库、知识结构与场馆、科技教育应用。"><link rel="stylesheet" href="/platform.css"><link rel="stylesheet" href="/portal.css"></head><body class="portal"><a class="gd-skip" href="#main">跳到主要内容</a>{nav}<main id="main">{body}</main>{footer}{script}</body></html>'''
 (OUT/name).write_text(s)
def card(a):
 img='/'+a['cover'] if a.get('cover') else ''
 return f'''<a class="project-card" href="/project/{a['slug']}.html"><div class="picture">{('<img src="'+html.escape(img)+'" alt="'+html.escape(a['name'])+'" loading="lazy">') if img else '<span>好设计项目档案</span>'}</div><p class="meta">{a['year']} · {a['level']}</p><h3>{html.escape(a['name'])}</h3><p class="unit">{html.escape(a['unit'])}</p></a>'''
featured=[next(a for a in awards if a['slug']==slug) for slug in ['2025-00','2021-00','2015-00']]
page('index.html','创新设计知识平台',f'''
<section class="hero shell"><div class="hero-copy"><p class="eyebrow">GOOD DESIGN · KNOWLEDGE & POSSIBILITY</p><h1>读懂好设计，<br>发现新的可能。</h1><p class="lead">从真实作品出发，理解科技与设计的相遇，让创新知识走进展馆、课堂和产业。</p><div class="actions"><a class="button primary" href="/projects.html">探索项目库 ↗</a><a class="text-link" href="/applications.html">发现应用</a></div></div><a class="hero-work" href="/project/2015-00.html"><img src="/{featured[2]['cover']}" alt="CRH380A型高速动车组"><div><span>从高速列车，看见系统设计的力量</span><span>阅读作品 ↗</span></div></a></section>
<section class="stats shell" aria-label="当前收录数据"><div><b>560</b><span>项目档案</span></div><div><b>10</b><span>届奖项资料</span></div><div><b>98</b><span>金奖项目</span></div><p>当前档案收录范围为2015至2025年。<br>计数依据已导入资料，知识内容持续整理。</p></section>
<section class="section shell"><h2>每一件作品，都是一个问题的回答。</h2><p class="intro">看见成果，也走近成果背后的挑战、原理与设计选择。</p><div class="featured">{''.join(card(a) for a in featured)}</div></section>
<section class="section shell journey"><div><h2>从作品档案，<br>走向可复用的知识。</h2><p class="intro">项目是连接点。原始资料、设计过程、知识条目和不同应用，围绕同一个项目持续积累。</p><a class="text-link" href="/knowledge.html">了解知识库 ↗</a></div><ol><li><span>项目档案</span><p>它是什么，解决什么问题，谁完成了它。</p></li><li><span>设计知识</span><p>如何实现，为什么这样选择，有哪些约束。</p></li><li><span>应用实践</span><p>在展馆理解，在课堂探索，在产业中发现启发。</p></li></ol></section>
<section class="section shell"><h2>让好设计，进入不同的现场。</h2><div class="app-list"><a href="/museum.html"><span>好设计馆</span><p>作品策展、主题展区与互动体验</p><b>进入馆 ↗</b></a><a href="/education.html"><span>科技教育</span><p>从真实工程理解科学，走进设计课堂</p><b>开始探索 ↗</b></a><a href="/connect.html"><span>产业创新</span><p>整理问题，寻找相关作品与方法</p><b>查看方向 ↗</b></a></div></section>''')
explorer='''<section class="shell page-head"><p class="eyebrow">PROJECT LIBRARY</p><h1>从一个问题，找到一件好设计。</h1><p class="intro">浏览当前收录的560项作品，按名称、完成单位、年度或奖项探索。</p></section><section class="shell" id="search"><form class="search-form" id="searchForm"><label for="query">搜索项目</label><div><input id="query" type="search" placeholder="项目名称、技术关键词或完成单位" autocomplete="off"><button class="button primary">搜索</button></div></form><div class="filters"><label>奖项 <select id="level"><option value="">全部奖项</option>'''+''.join(f'<option>{k}</option>' for k in counts)+'''</select></label><label>年度 <select id="year"><option value="">全部年度</option>'''+''.join(f'<option>{y}</option>' for y in sorted(set(a['year'] for a in awards),reverse=True))+'''</select></label><button id="reset" class="reset">重置筛选</button></div><p class="result-count" id="resultCount" role="status">正在读取项目档案…</p><div class="catalog" id="results"></div><div class="pagination"><button id="prev" class="button">上一页</button><span id="pageInfo"></span><button id="next" class="button">下一页</button></div><noscript>请开启JavaScript使用筛选；也可从首页进入精选作品。</noscript></section>'''
page('projects.html','项目库',explorer,'<script src="/catalog.js"></script>')
page('knowledge.html','知识库','''<section class="shell page-head"><p class="eyebrow">DESIGN KNOWLEDGE</p><h1>知识，从项目中生长。</h1><p class="intro">把“做出了什么”进一步拆解成“如何做到、为什么这样做、何处可以借鉴”。当前知识库处于整理与校准阶段。</p></section><section class="shell knowledge-overview"><div><b>560</b><h3>项目关联知识页</h3><p>用于组织档案与分析内容。</p></div><div><b>2</b><h3>独立原子化样本</h3><p>已有结构化文件，仍待专家校准。</p></div><div><b>持续整理</b><h3>事实、解读、迁移假设</h3><p>分别标注来源与核验状态。</p></div></section><section class="shell section"><h2>一件作品的知识结构</h2><div class="knowledge-fields"><span>原始问题</span><span>使用场景</span><span>技术原理</span><span>材料与工艺</span><span>设计取舍</span><span>验证证据</span><span>五大构成</span><span>迁移条件</span></div><p class="intro">每个条目将关联原始资料、项目和适用条件。尚无证据的内容留作待补，分析与事实分开呈现。</p></section><section class="shell section"><h2>先看两个整理样本</h2><div class="sample-list"><a href="/atom/2025-00.html"><h3>嫦娥五/六号月球钻取采样</h3><p>从月面采样的约束，理解系统与机构设计。</p><span>知识草稿 · 待复核 ↗</span></a><a href="/atom/2021-00.html"><h3>天问一号火星车移动系统</h3><p>从复杂地形移动，理解结构与控制的配合。</p><span>知识草稿 · 待复核 ↗</span></a></div><a class="button" href="/projects.html">从全部项目继续探索 ↗</a></section>''')
page('applications.html','应用','''<section class="shell page-head"><p class="eyebrow">APPLICATIONS</p><h1>同一份知识，多种打开方式。</h1><p class="intro">场馆、教育和产业服务围绕共享项目库组织。已有内容可以体验，下一阶段能力逐步验证。</p></section><section class="shell app-list large"><a href="/museum.html"><span>好设计馆</span><p>按产业、生活、社会策展，走进优秀作品与互动展项。</p><b>已有内容 · 进入 ↗</b></a><a href="/education.html"><span>科技教育</span><p>把项目中的科学原理变成课程、任务与互动探索。</p><b>已有原型 · 进入 ↗</b></a><a href="/connect.html"><span>产业创新</span><p>从企业问题出发，发现案例与技术迁移的可能。</p><b>方向探索 · 查看 ↗</b></a><a href="/assistant.html"><span>好设计助手</span><p>当前开放作品检索；带证据的智能问答将在后续完善。</p><b>项目检索 · 进入 ↗</b></a></section>''')
page('museum.html','好设计馆','''<section class="shell page-head"><p class="eyebrow">GOOD DESIGN MUSEUM</p><h1>走进作品，也走进创造的过程。</h1><p class="intro">好设计馆是平台的展览与体验应用。围绕不同主题理解作品，借助互动看见设计背后的原理。</p><div class="actions"><a class="button primary" href="/hall.html">进入数字展馆 ↗</a><a class="button" href="/categories.html">浏览三大主题展区</a></div></section><section class="shell section"><div class="sample-list"><a href="/x-ray.html"><h3>拆解实验室</h3><p>从系统到部件，理解国之重器如何协同工作。</p><span>互动拆解 ↗</span></a><a href="/playground.html"><h3>互动乐园</h3><p>用简化模拟与挑战任务，探索设计和科学。</p><span>开始体验 ↗</span></a><a href="/exhibit-sim.html"><h3>月面钻取任务</h3><p>面向展厅的采样任务交互原型。</p><span>打开展项 ↗</span></a><a href="/exhibit-xray.html"><h3>展厅拆解大屏</h3><p>面向现场讲解的作品结构体验。</p><span>打开大屏 ↗</span></a></div></section>''')
page('education.html','科技教育','''<section class="shell page-head"><p class="eyebrow">LEARN THROUGH DESIGN</p><h1>用真实的创造，打开科学课堂。</h1><p class="intro">从工程问题理解科学原理，再把所学用于自己的设计。已有课例、学科单元和互动体验可供探索。</p><a class="button primary" href="/learn.html">进入教育应用 ↗</a></section><section class="shell section"><div class="sample-list"><a href="/lesson/index.html"><h3>项目课例库</h3><p>从优秀作品切入，组织课堂问题与探索任务。</p><span>浏览课例 ↗</span></a><a href="/courseware/index.html"><h3>科学备课素材</h3><p>围绕真实案例，关联科学课程与教学活动。</p><span>打开素材 ↗</span></a><a href="/playground.html"><h3>动手探索</h3><p>通过模拟和闯关观察变量，理解原理。</p><span>进入互动 ↗</span></a><a href="/passport.html"><h3>参观任务护照</h3><p>把观察、提问与设计挑战带进展馆。</p><span>查看任务 ↗</span></a></div></section>''')
page('assistant.html','好设计助手','''<section class="shell page-head"><p class="eyebrow">DESIGN ASSISTANT</p><h1>先找到相关作品。</h1><p class="intro">当前版本开放项目检索。智能问答和专业推理仍待完善，现阶段不会生成或提交分析报告。</p><a class="button primary" href="/projects.html#search">搜索项目库 ↗</a></section><section class="shell section"><h2>试试这些方向</h2><div class="knowledge-fields"><a href="/projects.html?q=机器人">机器人</a><a href="/projects.html?q=采样">采样</a><a href="/projects.html?q=医疗">医疗</a><a href="/projects.html?q=制造">制造</a></div></section>''')
page('connect.html','产业创新','''<section class="shell page-head"><p class="eyebrow">DESIGN FOR INDUSTRY</p><h1>带着具体问题，重新理解好设计。</h1><p class="intro">产业服务正在规划。当前可浏览相关作品，或整理一份问题草稿，为后续案例对标与专家讨论做准备。</p></section><section class="shell draft-section"><h2>梳理你的设计问题</h2><p>内容仅保存在本次页面中，下载为本地文本，不会提交给平台。</p><form id="draft"><label for="industry">产品或行业</label><input id="industry" placeholder="例如：水暖阀门"><label for="problem">目前遇到的问题</label><textarea id="problem" required placeholder="描述现象、约束、已有尝试与期望目标"></textarea><button class="button primary">下载问题草稿</button><p role="status" id="draftStatus"></p></form><a class="text-link" href="/projects.html">去项目库寻找启发 ↗</a></section>''','''<script>document.getElementById('draft').addEventListener('submit',e=>{e.preventDefault();const text='设计问题草稿\n产品/行业：'+document.getElementById('industry').value+'\n问题：'+document.getElementById('problem').value+'\n\n下一步需明确：适用工况、约束、对标案例、验证方法。';const u=URL.createObjectURL(new Blob([text],{type:'text/plain;charset=utf-8'}));const a=document.createElement('a');a.href=u;a.download='设计问题草稿.txt';a.click();setTimeout(()=>URL.revokeObjectURL(u),1000);document.getElementById('draftStatus').textContent='问题草稿已生成下载，未提交到平台。';});</script>''')
page('about.html','关于平台','''<section class="shell page-head"><p class="eyebrow">ABOUT GOOD DESIGN</p><h1>让创新设计知识，被看见、被理解、被使用。</h1><p class="intro">以好设计奖项目为起点，连接科技知识、设计方法与应用实践。项目库是共享核心，好设计馆与教育应用是它的不同入口。</p></section><section class="shell section"><h2>平台正在做什么</h2><div class="sample-list"><div><h3>已经可以探索</h3><p>项目档案、数字展馆、课例、互动拆解与知识整理稿。</p></div><div><h3>接下来逐步完善</h3><p>有证据的知识条目、项目间关系、专家校准及面向不同任务的智能服务。</p></div></div></section><section class="shell section" id="sources"><h2>来源与内容边界</h2><p class="intro">当前560项为历史资料导入计数，覆盖2015至2025年十届档案，包含金奖98、银奖199、创意奖190、提名奖70、菁英奖3。不是本轮重新核验的官方统计。</p><p class="intro">奖项事实请以<a href="https://cgd.cmes.org/exhibit/home">好设计官方展览中心</a>为准。原项目页中已有的资料来源与链接保留。AI分析、五维解读和互动模拟用于学习与探索，不构成官方评分或工程结论。</p><p class="intro">知识页面尚在整理，需逐条补齐来源和校准。本站是项目团队的知识探索站，不提供官方奖项申报或评审服务。</p></section>''')
for name,target in [('laureates.html','projects.html'),('migration-report.html','connect.html')]:
 page(name,'页面入口已整理',f'<section class="shell page-head"><h1>内容已整理到新的入口。</h1><a class="button primary" href="/{target}">继续浏览 ↗</a></section>')
(OUT/'404.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>页面不存在 · 好设计</title><h1>这个页面暂不可访问</h1><a href="/">返回好设计平台</a></html>')
(OUT/'robots.txt').write_text('User-agent: *\nAllow: /\nDisallow: /atom/\nSitemap: https://gooddesign.qiuyiwu.com/sitemap.xml\n')
urls=['index.html','projects.html','knowledge.html','applications.html','museum.html','education.html','about.html']+['project/'+a['slug']+'.html' for a in awards]
(OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>https://gooddesign.qiuyiwu.com/'+p+'</loc></url>' for p in urls)+'</urlset>')
print('Built',len(list(OUT.rglob('*'))),'entries; counts',dict(counts))
for p in (R/'scripts/portal-assets').glob('*'):shutil.copy2(p,OUT/p.name)
