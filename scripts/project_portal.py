"""060 public presentation only; no raw files, tokens, or processing state exported."""
from pathlib import Path
import html,json
ROOT=Path(__file__).resolve().parents[1];ASSETS=ROOT/'extensions/project-portal'
E=lambda v:html.escape(str(v),quote=True)
from inno_site_chrome import navigation,footer
from gooddesign_assets import links as gooddesign_links
def shell(title,body,script='',active='projects',description=''):
 from project_cover_display import rewrite_html
 body=rewrite_html('<head></head>'+body).replace('<head>','').replace('</head>','')
 return '<!doctype html><html lang="zh-CN" data-theme="light" data-zw-mode="product"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+E(title)+' · 好设计</title>'+('<meta name="description" content="'+E(description)+'">' if description else '')+'<link rel="icon" href="data:,"><link rel="stylesheet" href="/inno/portal/portal.css"><link rel="stylesheet" href="/inno/portal/system.css">'+gooddesign_links()+'</head><body class="pp-site">'+navigation(active)+'<main class="pp-page" id="main">'+body+'</main>'+footer()+script+'</body></html>'
def catalog(lib):
 rows=json.loads((ASSETS/'catalog.json').read_text())
 for x in rows:
  p=lib/x['id']/'研究工作区/工作状态.json'
  try:x['research']=json.loads(p.read_text()).get('revision',0)>0
  except (OSError,ValueError,TypeError):x['research']=False
 return rows
def home():
 body='''<section class="pp-hero"><div class="pp-kicker">好设计 / 项目知识库</div><h1>看见好设计，<br>读懂创新如何发生。</h1><p class="pp-lead">从一个真实项目出发，理解它面对的问题、设计取舍与技术原理，找到下一次创新的启发。</p><form class="pp-search" id="hero-search" role="search"><label class="pp-sr-only" for="hero-query">搜索项目或完成单位</label><input id="hero-query" type="search" placeholder="搜索项目、完成单位或关键词"><button type="submit">探索项目 <span aria-hidden="true">→</span></button></form><div class="pp-paths"><a href="#collection">01 <b>了解项目</b><span>阅读背景、原理与设计取舍</span></a><a href="/methods/">02 <b>学习方法</b><span>找到适合问题的分析路径</span></a><a href="/needs/">03 <b>带入自己的问题</b><span>从案例启发走向创新研究</span></a></div></section>
<section class="pp-feature" aria-labelledby="feature-title"><a class="pp-feature-image" href="/dossier/?project=2025-00"><img src="/inno/portal/covers/case-2025-00.jpg" alt="嫦娥月球钻取采样系统项目示意"></a><div class="pp-feature-copy"><span class="pp-kicker">从这份档案开始</span><h2 id="feature-title">把月壤带回来，<br>设计要跨过哪些难题？</h2><p>走进嫦娥五号、六号月球钻取采样系统，沿任务、系统设计与验证线索，理解一项复杂工程的关键取舍。</p><a class="pp-button" href="/dossier/?project=2025-00">阅读项目档案 <span aria-hidden="true">↗</span></a><small>内容持续补证，来源与研究边界在档案内呈现。</small></div></section>
<section id="collection" aria-labelledby="collection-title"><div class="pp-results"><div><span class="pp-kicker">探索项目</span><h2 id="collection-title">从这里找到你的研究起点</h2></div><p id="result-count" role="status" aria-live="polite">正在加载项目…</p></div><form id="filters" class="pp-controls" role="search"><label>搜索项目<input id="query" type="search" placeholder="项目名称、单位或关键词"></label><label>获奖年份<select id="year"><option value="">全部年份</option></select></label><label>奖项<select id="award"><option value="">全部奖项</option></select></label><label>阅读内容<select id="status"><option value="">全部项目</option><option value="research">研究整理版</option><option value="basic">基础条目</option></select></label><button type="button" id="clear">清除筛选</button></form><p class="pp-caption">“研究整理版”表示已形成版本化档案，不代表专家审核或工程验证。</p><div class="pp-grid" id="projects"></div><div class="pp-empty" id="empty" hidden><h3>暂时没有匹配的项目</h3><p>试试其他关键词，或清除筛选重新浏览。</p><button id="empty-clear">清除筛选</button></div><div class="pp-pagination" id="pagination"><button id="previous">← 上一页</button><span id="page-state"></span><button id="next">下一页 →</button></div><noscript>请启用JavaScript进行筛选，或先<a href="/dossier/?project=2025-00">阅读嫦娥档案</a>。</noscript></section>'''
 return shell('项目库',body,'<script src="/inno/portal/portal.js"></script>')
def about():
 return shell('使用指南','<section class="pp-hero"><div class="pp-kicker">GoodDesign 使用指南</div><h1>同一份项目知识，<br>连接不同的探索方式。</h1><p class="pp-lead">项目库回答“发生了什么、为什么这样设计”；方法库提供分析路径；需求研究把模糊想法校准为可研究、可验证、可交接的创新问题。</p></section><section class="pp-paths"><a href="/projects/"><b>项目库与档案</b><span>按年份和奖项检索，阅读项目背景、设计取舍、资料与研究版本。</span></a><a href="/methods/"><b>创新方法库</b><span>了解方法的输入、步骤、产物、适用条件与教学示例。</span></a><a href="/needs/"><b>需求研究</b><span>明确真实场景、问题、约束、证据和未知，形成可核对的研究简报。</span></a><a href="/museum/"><b>好设计馆</b><span>通过真实项目封面、展区与互动内容理解设计价值。</span></a><a href="/loop/"><b>企业创新工作台</b><span>在授权内部空间中推进研究任务、证据核对和验证反馈。</span></a><a href="/mcp/"><b>MCP 接入</b><span>使用8项远程只读工具检索项目与方法、核对证据并组装研究上下文。</span></a></section><section class="pp-feature-copy"><h2>阅读资料时，保留证据与边界</h2><p>获奖题录、原文事实、研究解读和应用假设分别呈现。资料整理状态不等于完整性，技术参考不代表项目采用，教学运行不代表实际工程有效。</p><p>项目介绍、方法、展馆和需求研究无需登录。原件下载、可读来源预览、<a href="/admin/">资料管理</a>和<a href="/loop/">企业创新工作台</a>仍需授权。MCP使用独立Bearer密钥，不使用网页登录密码。</p><p>当前公开主域名为 haoshejiguan.com（好设计馆），opendesign.cc/inno/ 已永久跳转至新域名。旧站仅保留历史资产和回滚用途，不作为持续更新的平行频道。</p></section>')
