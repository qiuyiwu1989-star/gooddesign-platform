import html
import json
from pathlib import Path

import app_center_096
import model_explorer_096
import model_official_097
import method_library_catalog
import project_pipeline as pp
from project_portal import shell, catalog

ROOT = Path(__file__).resolve().parents[1]
APPS = json.loads((ROOT / 'extensions/application-center/apps.json').read_text())
CASES = json.loads((ROOT / 'extensions/application-center/cases.json').read_text())
E = lambda value: html.escape(str(value), quote=True)

CSS = '''
.pp-page{overflow-x:hidden}
.info-hero{max-width:850px;padding:42px 0 32px}.info-hero h1{margin:12px 0 18px;font-size:clamp(34px,4.4vw,54px);line-height:1.2;letter-spacing:-.04em}.info-hero p{max-width:720px;color:var(--fg2);font-size:17px;line-height:1.85}.info-actions{display:flex;flex-wrap:wrap;gap:10px;margin-top:24px}.info-actions a{display:inline-flex;align-items:center;min-height:44px;padding:9px 16px;border:1px solid var(--bdrSoft);border-radius:99px;background:var(--card);font-size:var(--fs-caption)}.info-actions a:first-child{background:var(--accent);color:white;border-color:var(--accent)}.info-facts{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin:12px 0 34px}.info-facts div{padding:20px;border-top:1px solid var(--bdr)}.info-facts strong{display:block;font-size:28px;font-weight:500;font-variant-numeric:tabular-nums}.info-facts span{color:var(--fg2);font-size:var(--fs-xs)}.info-section{margin-top:38px}.info-section h2{margin:0 0 14px;font-size:26px;letter-spacing:-.025em}.info-section>p{max-width:780px;color:var(--fg2);line-height:1.85}.info-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.info-grid.three{grid-template-columns:repeat(3,minmax(0,1fr))}.info-card{padding:24px;border:1px solid var(--bdrSoft);border-radius:18px;background:var(--card)}.info-card h3{margin:0 0 10px;font-size:18px}.info-card p,.info-card li{color:var(--fg2);font-size:var(--fs-caption);line-height:1.8}.info-card a{display:inline-block;margin-top:8px}.info-note{padding:18px 20px;border-left:3px solid var(--accent);border-radius:0 14px 14px 0;background:var(--acBg);color:var(--fg2);line-height:1.8}.info-layers{display:grid;gap:0;border-top:1px solid var(--bdrSoft)}.info-layer{display:grid;grid-template-columns:180px 1fr;gap:24px;padding:20px 0;border-bottom:1px solid var(--bdrSoft)}.info-layer strong{font-size:var(--fs-sm)}.info-layer p{margin:0;color:var(--fg2);line-height:1.8}.info-table{width:100%;border-collapse:collapse}.info-table th,.info-table td{padding:15px 12px;border-bottom:1px solid var(--bdrSoft);text-align:left;vertical-align:top;line-height:1.75}.info-table th{color:var(--fg2);font-size:var(--fs-xs);font-weight:500}.app-toolbar{display:flex;align-items:center;justify-content:space-between;gap:16px;margin:22px 0}.app-filters{display:flex;flex-wrap:wrap;gap:8px}.app-filters button{min-height:40px;padding:8px 14px;border:1px solid var(--bdrSoft);border-radius:99px;background:transparent;color:var(--fg2)}.app-filters button[aria-pressed=true]{background:var(--acBg);color:var(--accentDeep);border-color:var(--accent)}#app-count{margin:0;color:var(--fg2);font-size:var(--fs-xs)}.app-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}.app-card{display:flex;min-height:265px;flex-direction:column;padding:22px;border:1px solid var(--bdrSoft);border-radius:18px;background:var(--card);text-decoration:none;transition:transform .16s,border-color .16s}.app-card:hover{transform:translateY(-2px);border-color:var(--accent)}.app-card[hidden]{display:none}.app-card-top{display:flex;align-items:center;justify-content:space-between;gap:10px}.app-user{color:var(--accentDeep);font-size:var(--fs-xs)}.app-status{padding:3px 8px;border-radius:99px;background:var(--acBg);color:var(--accentDeep);font-size:11px}.app-card h3{margin:18px 0 8px;font-size:20px}.app-card p{color:var(--fg2);font-size:var(--fs-caption);line-height:1.75}.app-card-foot{margin-top:auto;padding-top:16px;color:var(--accentDeep);font-size:var(--fs-caption)}.app-output{margin-top:10px!important;color:var(--fg)!important;font-size:var(--fs-xs)!important}.case-list{display:grid;gap:12px}.case-link{display:grid;grid-template-columns:180px 1fr auto;gap:20px;align-items:center;padding:18px 0;border-bottom:1px solid var(--bdrSoft)}.case-link span{color:var(--fg2);font-size:var(--fs-xs)}.case-link p{margin:0;color:var(--fg2);font-size:var(--fs-caption)}.case-assets{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:20px 0}.case-assets span{padding:16px;border-radius:12px;background:var(--demo);color:var(--fg2);font-size:var(--fs-caption);line-height:1.65}.case-steps{counter-reset:step;list-style:none;padding:0}.case-steps li{counter-increment:step;display:grid;grid-template-columns:36px 1fr;gap:14px;padding:14px 0;border-bottom:1px solid var(--bdrSoft)}.case-steps li:before{content:counter(step);display:grid;place-items:center;width:28px;height:28px;border-radius:50%;background:var(--acBg);color:var(--accentDeep);font-size:var(--fs-xs)}@media(max-width:1000px){.app-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.info-grid.three{grid-template-columns:repeat(2,minmax(0,1fr))}.case-assets{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:640px){.info-facts{grid-template-columns:repeat(2,minmax(0,1fr))}.info-grid,.info-grid.three,.app-grid{grid-template-columns:1fr}.info-layer{grid-template-columns:1fr;gap:8px}.case-link{grid-template-columns:1fr;gap:6px}.app-toolbar{align-items:flex-start;flex-direction:column}.case-assets{grid-template-columns:1fr}.info-hero{padding-top:26px}.info-table{display:block;overflow-x:auto;white-space:nowrap}}@media print{.app-filters,.info-actions,.gd-ip-trigger{display:none!important}.app-card{break-inside:avoid}.app-grid{grid-template-columns:repeat(2,1fr)}.info-hero{padding-top:0}.info-card,.info-layer,.case-steps li{break-inside:avoid}}
'''


def about():
    projects = {p['id']: p for p in catalog(pp.LIB)}
    project_count = len(projects)
    research_count = sum(1 for p in projects.values() if p.get('research'))
    method_count = len(method_library_catalog.catalog()['methods'])
    app_count = len(APPS)
    about_css = (ROOT / 'extensions/design-system/about-page.css').read_text(encoding='utf-8')
    hero = projects['2025-00']
    primary = projects['2025-08']
    secondary = [projects['2023-04'], projects['2023-02']]
    secondary_copy = {
        '2023-04': '围绕高耐压与低摩擦，看密封技术如何回应严苛工况。',
        '2023-02': '从效率与寿命的协同，理解重型装备中的设计取舍。',
    }
    small_cases = ''.join(f'''<article class="about-case-small">
      <img src="/inno/portal/{E(p['cover'])}" alt="{E(p['name'])}项目封面" loading="lazy">
      <div><div class="about-case-meta"><b>{E(p['award'])}</b><span>真实项目档案</span></div><h3>{E(p['name'])}</h3><p>{E(secondary_copy[p['id']])}</p><a class="about-text-link" href="/dossier/?project={E(p['id'])}">阅读项目档案</a></div>
    </article>''' for p in secondary)
    body = f'''<style>{about_css}</style><div class="about-page">
    <section class="about-hero" aria-labelledby="about-title">
      <div class="about-hero-copy"><span class="about-kicker">GoodDesign · 关于好设计</span><h1 id="about-title">让真实创新，<br>成为下一次创新的<span>起点。</span></h1><p class="about-lead">好设计以真实获奖项目为起点，连接项目档案、设计方法、证据与创新应用。让一件作品不止被看见，更能被理解、学习和用于新的研究。</p><div class="about-actions"><a href="/projects/">探索真实项目</a><a href="#applications">查看应用场景</a></div></div>
      <a class="about-hero-art" href="/dossier/?project={E(hero['id'])}" aria-label="阅读{E(hero['name'])}项目档案"><img src="/inno/portal/{E(hero['cover'])}" alt="{E(hero['name'])}项目封面" fetchpriority="high"><span class="about-art-badge">{E(hero['award'])} · 真实项目档案</span><span class="about-art-copy"><small>从一份真实档案开始</small><strong>{E(hero['name'])}</strong><span>沿任务约束、系统设计与验证线索，读懂复杂工程如何成立。</span></span></a>
    </section>
    <section class="about-facts" aria-label="好设计已形成的知识资产"><div class="about-fact"><strong>{project_count}</strong><span>真实项目目录</span></div><div class="about-fact"><strong>{research_count}</strong><span>原生研究版</span></div><div class="about-fact"><strong>{method_count}</strong><span>创新方法档案</span></div><div class="about-fact"><strong>{app_count}</strong><span>应用与试点入口</span></div></section>
    <section class="about-section" aria-labelledby="about-path-title"><div class="about-section-head"><div><span class="about-kicker">从作品到知识，再到应用</span><h2 id="about-path-title">作品值得被看见，<br>经验更应该被理解。</h2></div><p>优秀项目常常停留在题录、新闻和展示页。好设计继续追问：它解决了什么问题，为什么这样设计，哪些经验可以启发新的真实问题。</p></div><div class="about-path"><div class="about-path-step"><span>01</span><strong>真实作品</strong><p>从可追溯的项目身份、背景与完成单位开始。</p></div><div class="about-path-step"><span>02</span><strong>项目档案</strong><p>组织需求、约束、机制、指标、历程与来源。</p></div><div class="about-path-step"><span>03</span><strong>设计方法</strong><p>把经验连接到可阅读、可讨论的研究路径。</p></div><div class="about-path-step"><span>04</span><strong>创新研究</strong><p>围绕新问题形成假设、证据与待验证方向。</p></div><div class="about-path-step"><span>05</span><strong>场景应用</strong><p>进入产业、企业、展馆、教育与智能研究。</p></div></div></section>
    <section class="about-section" aria-labelledby="about-cases-title"><div class="about-section-head"><div><span class="about-kicker">真实项目，真实设计取舍</span><h2 id="about-cases-title">从一个个具体问题，<br>看见创新如何发生。</h2></div><p>不只展示结果，也保留问题背景、设计机制与资料来源。每一份研究档案，都可以成为理解其他问题的参照。</p></div><div class="about-case-layout"><article class="about-case-primary"><a href="/dossier/?project={E(primary['id'])}"><img src="/inno/portal/{E(primary['cover'])}" alt="{E(primary['name'])}项目封面" loading="lazy"><div class="about-case-copy"><div class="about-case-meta"><b>{E(primary['award'])}</b><span>材料 · 工艺 · 装备</span></div><h3>{E(primary['name'])}</h3><p>从材料制备到核心装备，理解高功率芯片散热背后的系统设计。</p><span class="about-text-link">阅读项目档案</span></div></a></article><div class="about-case-side">{small_cases}</div></div></section>
    <section class="about-section" id="applications" aria-labelledby="about-apps-title"><div class="about-section-head"><div><span class="about-kicker">一套知识底座，不同的创新现场</span><h2 id="about-apps-title">让项目经验，<br>进入真实工作与学习。</h2></div><p>同一批项目和方法，可以服务产业研究、企业验证、公众策展与科技教育。每个入口保留自己的任务和边界，不复制成彼此孤立的数据。</p></div><div class="about-applications"><a class="about-application" href="/expo/"><span class="about-app-no">01</span><span class="about-app-title"><strong>地方与产业</strong><span>产业创新 Agent</span></span><p>围绕地方产业开展公开资料研究、获奖案例对照与创新路径研判，形成可供会商的研究报告。</p><span class="about-app-status">在线体验</span><span class="about-app-link">进入产业看台</span></a><a class="about-application" href="/loop/"><span class="about-app-no">02</span><span class="about-app-title"><strong>企业与园区</strong><span>企业创新工作台</span></span><p>在授权空间组织需求、研究任务、参考资料与验证计划，让研发讨论保有版本和证据。</p><span class="about-app-status">授权试点</span><span class="about-app-link">了解企业创新</span></a><a class="about-application" href="/museum/"><span class="about-app-no">03</span><span class="about-app-title"><strong>场馆与公众</strong><span>好设计馆</span></span><p>通过主题展览、项目故事与互动内容，理解真实作品背后的科技、设计与社会价值。</p><span class="about-app-status">公开展示</span><span class="about-app-link">进入好设计馆</span></a><a class="about-application" href="/museum/#education"><span class="about-app-no">04</span><span class="about-app-title"><strong>学校与教师</strong><span>科技教育</span></span><p>用真实项目、原理阅读和活动单组织探究学习，让学生接触真实世界中的设计问题。</p><span class="about-app-status">学习内容</span><span class="about-app-link">查看教育内容</span></a></div><p class="about-mcp">需要在自己的 Agent 中检索项目与方法？<a href="/mcp/">查看 MCP 接入方式</a>，或前往<a href="/apps/">应用中心</a>了解全部应用。</p></section>
    <section class="about-section about-model" id="model" aria-labelledby="about-model-title"><div class="about-model-head"><div><span class="about-kicker">创新设计大模型</span><h2 id="about-model-title">让项目、方法与智能研究，<br>形成同一个创新闭环。</h2></div><p>它不是单一基础模型，也不是聊天界面的包装，而是好设计连接真实项目、设计方法、研究 Agent 与验证反馈的领域智能系统。</p></div><div class="about-model-flow"><article><span>01 · 项目档案数据库</span><strong>知道真实项目为什么这样设计</strong><p>项目背景、约束、机制、试验、来源和版本按统一结构保存，让每个判断都有回查的起点。</p></article><article><span>02 · 设计创新引擎</span><strong>用证据与方法组织研究</strong><p>围绕真实问题检索项目、调用方法，形成设计解释、案例参照、候选方向和验证计划。</p></article><article><span>03 · 应用能力</span><strong>把研究带回真实工作与学习</strong><p>进入产业研判、企业验证、公众策展、科技教育和 Agent 研究任务，而不是停留在一次回答。</p></article></div><div class="about-model-foot"><p>从真实项目到研究，再回到真实应用。只有经过确认的成果，才会沉淀为公共知识；生成内容不会自动成为工程结论。</p><div class="about-actions"><a href="/model/">了解创新设计大模型</a><a href="/expo/">体验产业研究</a></div></div></section>
    <section class="about-section about-trust" aria-labelledby="about-trust-title"><span class="about-kicker">我们的内容原则</span><h2 id="about-trust-title">不仅给出答案，<br>更保留答案从哪里来。</h2><p class="about-trust-intro">可信不是一句口号，而是每一条事实、每一次解读和每一个研究版本都能被继续核对。</p><div class="about-trust-grid"><div><strong>事实有出处</strong><p>项目事实与公开资料保留来源，未知信息不补造。</p></div><div><strong>解读有边界</strong><p>平台整理、AI分析与原始事实分层呈现。</p></div><div><strong>研究有版本</strong><p>新增证据形成新版本，历史研究不被悄悄覆盖。</p></div><div><strong>应用先验证</strong><p>案例启发不等于直接适用，候选方向仍需试验与确认。</p></div></div></section>
    <p class="about-source">好设计是项目团队建设的创新设计知识平台，不提供官方奖项申报或评审服务。项目身份与奖项信息以<a href="https://cgd.cmes.org/exhibit/home" target="_blank" rel="noopener">好设计奖官方发布</a>为准；研究整理版不代表专家审核，AI分析不代表工程结论。</p>
    <section class="about-closing" aria-labelledby="about-closing-title"><div><span class="about-kicker">从真实问题开始</span><h2 id="about-closing-title">下一次创新，<br>可以从这里开始。</h2><p>可以从一个项目、一门课程、一个产业或一项企业需求开始。先在公开区域探索；涉及企业资料与验证任务时，再进入授权空间。</p></div><div class="about-actions"><a href="/needs/">开始需求研究</a><a href="/apps/">查看全部应用</a></div></section>
    </div>'''
    return shell('关于好设计', body, active='about', description='好设计连接真实获奖项目、项目档案、设计方法、证据与创新应用，服务地方产业、企业创新、场馆展示与科技教育。')


def model():
    return shell('创新设计大模型', model_official_097.page(), active='about')


def guide():
    rows = ''.join(f'<tr><td>{title}</td><td>{task}</td><td>{route}</td></tr>' for title, task, route in [
        ('项目库', '搜索项目、阅读档案和核对证据', '/projects/'),
        ('好设计馆', '看展、学习、查看科技教育内容', '/museum/'),
        ('方法库', '阅读64个方法及适用条件', '/methods/'),
        ('应用中心', '按用户任务查看解决方案和真实案例', '/apps/'),
        ('需求研究', '定义问题、选择参考、核对研究简报', '/needs/'),
        ('企业创新', '在授权空间推进任务、证据与验证', '/loop/'),
        ('数据总览', '查看覆盖、分布和研究缺口', '/report/'),
        ('MCP 接入', '配置客户端、检索读取和组装上下文', '/inno/mcp/'),
    ])
    body = f'''<style>{CSS}</style><section class="info-hero"><span class="gd-kicker">使用指南</span><h1>从当前任务，选择正确入口。</h1><p>不必先理解整个平台。找项目从项目库开始，定义自己的问题从需求研究开始，推进企业验证进入企业创新，开发Agent则使用MCP。</p></section><section class="info-section"><h2>各区域怎样使用</h2><table class="info-table"><thead><tr><th>区域</th><th>你用来做什么</th><th>入口</th></tr></thead><tbody>{rows}</tbody></table></section><section class="info-section"><h2>三条推荐路径</h2><div class="info-grid three"><article class="info-card"><h3>读懂一个项目</h3><p>项目库搜索 → 项目档案 → 核心章节 → 来源预览 → 方法参考。</p></article><article class="info-card"><h3>研究一个问题</h3><p>需求研究 → 问题与约束 → 项目与方法 → 核对简报 → 企业创新任务。</p></article><article class="info-card"><h3>接入一个Agent</h3><p>MCP配置 → 搜索项目和方法 → 读取版本与证据 → 当前客户端保存。</p></article></div></section><section class="info-section"><h2>公开与授权</h2><div class="info-layers"><div class="info-layer"><strong>公开阅读</strong><p>项目库、展馆、方法、需求研究、应用案例、数据总览、项目与模型介绍、MCP说明均可直接阅读。</p></div><div class="info-layer"><strong>授权空间</strong><p>企业创新和资料管理使用统一登录。私有原件、内部研究记录与公开项目事实分别管理。</p></div><div class="info-layer"><strong>独立MCP密钥</strong><p>MCP使用Bearer密钥，不使用网页登录密码。密钥不得写入URL、公开配置或报告。</p></div></div></section><section class="info-section"><h2>阅读时需要注意</h2><div class="info-note">研究整理版不等于专家审核，AI解读不等于事实，专利线索不等于实际采用，模拟过程不等于实时Agent，候选方向不等于工程验证。遇到缺失信息，以档案中的待补事项和来源范围为准。</div></section>'''
    return shell('使用指南', body, active='about')


def apps():
    return shell('应用中心', app_center_096.render(APPS, CASES), active='projects')


def case(case_id):
    item = next(case for case in CASES if case['id'] == case_id)
    assets = ''.join(f'<span>{E(asset)}</span>' for asset in item['assets'])
    steps = ''.join(f'<li>{E(step)}</li>' for step in item['steps'])
    links = ''.join(f'<a href="{E(url)}">{E(label)}</a>' for label, url in item['links'])
    body = f'''<style>{CSS}</style><section class="info-hero"><span class="gd-kicker">{E(item['app'])}</span><h1>{E(item['title'])}</h1><p>{E(item['summary'])}</p><span class="app-status">{E(item['status_label'])}</span></section><p class="info-note">这是一页应用案例，不是第二份项目档案。它说明同一份项目证据如何支持档案阅读、公众讲解与科技教育；项目事实以项目档案为准。</p><section class="info-section"><h2>真实问题</h2><p>{E(item['problem'])}</p></section><section class="info-section"><h2>使用了哪些资产</h2><div class="case-assets">{assets}</div></section><section class="info-section"><h2>实际工作路径</h2><ol class="case-steps">{steps}</ol></section><section class="info-section"><h2>形成的产物</h2><p>{E(item['output'])}</p></section><section class="info-section"><h2>证据与边界</h2><p class="info-note">{E(item['boundary'])}</p></section><section class="info-section"><h2>继续查看</h2><div class="info-actions">{links}</div></section>'''
    return shell(item['title'], body, active='projects')
