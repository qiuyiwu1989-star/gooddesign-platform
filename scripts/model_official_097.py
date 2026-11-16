def page():
    return '''<link rel="stylesheet" href="/inno/portal/model-official.css">
<div class="mo-page">
  <section class="mo-hero" aria-labelledby="mo-title">
    <div class="mo-hero-copy">
      <span class="mo-eyebrow">GoodDesign 官方介绍</span>
      <h1 id="mo-title">创新设计大模型</h1>
      <p class="mo-tagline">让真实项目经验，参与下一次创新。</p>
      <p class="mo-hero-summary">它不是单一基础模型，也不是聊天界面的包装，而是好设计连接真实项目、设计方法、研究 Agent 与验证反馈的领域智能系统。</p>
      <div class="mo-actions"><a class="mo-primary" href="#architecture">了解怎样工作</a><a class="mo-secondary" href="/apps/">查看真实应用</a></div>
    </div>
    <figure class="mo-system" aria-labelledby="mo-system-title">
      <img src="/inno/portal/covers/case-2025-00.jpg" alt="嫦娥月球钻取采样系统的结构与任务流程示意" fetchpriority="high">
      <figcaption>真实项目档案：嫦娥五/六号月球钻取采样系统</figcaption>
      <div class="mo-system-body">
        <div class="mo-layer-switch" role="group" aria-label="查看模型三层架构">
          <button type="button" data-model-layer="database" aria-pressed="true"><span>01</span><strong>项目档案数据库</strong><small>真实证据</small></button>
          <button type="button" data-model-layer="engine" aria-pressed="false"><span>02</span><strong>设计创新引擎</strong><small>方法与研究</small></button>
          <button type="button" data-model-layer="applications" aria-pressed="false"><span>03</span><strong>应用能力</strong><small>任务与成果</small></button>
        </div>
        <div class="mo-system-detail" aria-live="polite">
          <span id="mo-layer-label">平台知道什么</span>
          <h2 id="mo-system-title">一个项目，只有一份主档案</h2>
          <p id="mo-layer-text">问题、约束、设计机制、验证和来源按统一结构保存。展馆、教育与 Agent 引用同一项目身份和研究版本。</p>
          <a id="mo-layer-link" href="/dossier/?project=2025-00">阅读嫦娥项目档案</a>
        </div>
      </div>
    </figure>
  </section>

  <section class="mo-definition" id="definition" aria-labelledby="mo-definition-title">
    <div class="mo-section-index"><span>为什么需要</span><p>从看过作品，到解决新的真实问题。</p></div>
    <div class="mo-definition-main">
      <h2 id="mo-definition-title">把分散的作品、方法和证据，变成可以继续研究的工作基础。</h2>
      <p>优秀项目往往停留在题录、新闻和展示页。创新设计大模型继续追问：它解决了什么问题，为什么这样设计，哪些经验可以启发新的任务，哪些结论必须重新验证。</p>
      <div class="mo-concepts" aria-label="从问题到成果的研究路径">
        <div><strong>读懂真实项目</strong><span>知道为什么这样设计</span><p>从背景、约束、机制和验证理解选择。</p></div>
        <div><strong>找到可借鉴经验</strong><span>比较相似，也识别差异</span><p>让案例成为研究参照，而不是直接答案。</p></div>
        <div><strong>形成研究任务</strong><span>保留未知与验证条件</span><p>把启发整理为可核对的方向和计划。</p></div>
        <div><strong>回到真实应用</strong><span>用反馈决定沉淀</span><p>只有经过确认的成果，才进入公共知识。</p></div>
      </div>
    </div>
  </section>

  <section class="mo-architecture" id="architecture" aria-labelledby="mo-architecture-title">
    <header class="mo-section-heading"><span class="mo-eyebrow">三层协同</span><h2 id="mo-architecture-title">真实项目，如何参与创新研究</h2><p>从项目证据到研究方法，再到场景应用。每一层都保留来源、版本和验证边界。</p></header>
    <figure class="mo-architecture-map" aria-labelledby="mo-map-title mo-map-desc">
      <svg viewBox="0 0 1200 720" role="img" aria-labelledby="mo-map-title mo-map-desc">
        <title id="mo-map-title">创新设计大模型三层协同全景图</title>
        <desc id="mo-map-desc">项目档案数据库向设计创新引擎提供项目、方法和证据，引擎组织研究后连接公众展馆、科技教育、创新研究、地方产业与Agent。证据可信环和验证生长环贯穿全过程。</desc>
        <defs><marker id="mo-arrowhead" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="mo-map-arrowhead"/></marker></defs>
        <text x="44" y="54" class="mo-map-loop-title">证据可信环</text>
        <text x="44" y="84" class="mo-map-loop">原始资料 · 项目事实 · 平台分析 · 应用内容 · 来源与版本</text>
        <path d="M1050 66 H160 Q120 66 120 104" class="mo-map-loop-line" marker-end="url(#mo-arrowhead)"/>
        <text x="44" y="148" class="mo-map-kicker">真实输入</text>
        <g class="mo-map-node"><rect x="40" y="174" width="250" height="100" rx="18"/><text x="62" y="210" class="mo-map-label">项目档案数据库</text><text x="62" y="240" class="mo-map-sub">560 个真实项目 · 统一身份</text></g>
        <g class="mo-map-node"><rect x="40" y="310" width="250" height="100" rx="18"/><text x="62" y="346" class="mo-map-label">设计方法</text><text x="62" y="376" class="mo-map-sub">64 份方法档案 · 研究路径</text></g>
        <g class="mo-map-node"><rect x="40" y="446" width="250" height="100" rx="18"/><text x="62" y="482" class="mo-map-label">证据与版本</text><text x="62" y="512" class="mo-map-sub">原始资料 · 研究修订 · 边界</text></g>
        <path d="M290 224 H410" class="mo-map-arrow" marker-end="url(#mo-arrowhead)"/>
        <path d="M290 360 H410" class="mo-map-arrow" marker-end="url(#mo-arrowhead)"/>
        <path d="M290 496 H410" class="mo-map-arrow" marker-end="url(#mo-arrowhead)"/>
        <g class="mo-map-core"><rect x="420" y="174" width="360" height="372" rx="24"/><text x="450" y="214" class="mo-map-kicker">研究中枢</text><text x="450" y="252" class="mo-map-core-title">设计创新引擎</text><text x="450" y="282" class="mo-map-sub">创新设计大模型的能力内核</text><path d="M450 306 H750" class="mo-map-core-line"/><text x="450" y="338" class="mo-map-step">01 需求澄清</text><text x="450" y="376" class="mo-map-step">02 案例检索</text><text x="450" y="414" class="mo-map-step">03 方法分析</text><text x="450" y="452" class="mo-map-step">04 候选方向</text><text x="450" y="490" class="mo-map-step">05 验证计划</text></g>
        <text x="925" y="108" class="mo-map-kicker">真实应用</text>
        <path d="M780 282 C850 282 850 176 910 176" class="mo-map-arrow" marker-end="url(#mo-arrowhead)"/>
        <path d="M780 330 H910" class="mo-map-arrow" marker-end="url(#mo-arrowhead)"/>
        <path d="M780 402 C850 402 850 420 910 420" class="mo-map-arrow" marker-end="url(#mo-arrowhead)"/>
        <path d="M780 468 C850 468 850 540 910 540" class="mo-map-arrow" marker-end="url(#mo-arrowhead)"/>
        <g class="mo-map-node"><rect x="920" y="132" width="240" height="88" rx="16"/><text x="940" y="166" class="mo-map-label">公众与展馆</text><text x="940" y="194" class="mo-map-sub">主题展览 · 项目讲解</text></g>
        <g class="mo-map-node"><rect x="920" y="264" width="240" height="88" rx="16"/><text x="940" y="298" class="mo-map-label">科技教育</text><text x="940" y="326" class="mo-map-sub">活动单 · 探究任务</text></g>
        <g class="mo-map-node"><rect x="920" y="396" width="240" height="88" rx="16"/><text x="940" y="430" class="mo-map-label">企业创新研究</text><text x="940" y="458" class="mo-map-sub">研究简报 · 验证计划</text></g>
        <g class="mo-map-node"><rect x="920" y="528" width="240" height="88" rx="16"/><text x="940" y="562" class="mo-map-label">地方产业与 Agent</text><text x="940" y="590" class="mo-map-sub">产业报告 · 研究上下文</text></g>
        <path d="M420 590 H250 Q180 590 180 548" class="mo-map-loop-line" marker-end="url(#mo-arrowhead)"/>
        <text x="44" y="642" class="mo-map-loop-title">验证生长环</text>
        <text x="44" y="674" class="mo-map-loop">用户问题 · 研究任务 · 候选方向 · 人工审核 · 验证与回流</text>
        <text x="760" y="674" class="mo-map-sub">专家、设计师、工程师与实践者共同校准</text>
      </svg>
      <figcaption>三层协同：真实项目提供证据，设计创新引擎组织研究，应用能力交付不同成果；可信证据与真实验证贯穿全过程。</figcaption>
    </figure>
    <div class="mo-layers">
      <article class="mo-layer">
        <span class="mo-layer-number">01</span>
        <div class="mo-layer-copy"><h3>项目档案数据库</h3><p>保存项目背景、设计机制、试验、来源与版本，让每个判断都能回到项目本身。</p><div class="mo-tags"><span>场景与问题</span><span>约束与取舍</span><span>机制与原理</span><span>试验与应用</span><span>来源与版本</span></div></div>
        <aside class="mo-ledger" aria-label="079真实项目研究数据"><span>079 / 6000HP电动压裂泵</span><strong>45</strong><small>结构化记录</small><strong>180</strong><small>有值事实字段</small><strong>42</strong><small>带边界 AI 分析</small><a href="/dossier/?project=2019-s19">查看真实研究版本</a></aside>
      </article>
      <article class="mo-layer">
        <span class="mo-layer-number">02</span>
        <div class="mo-layer-copy"><h3>设计创新引擎</h3><p>围绕用户问题，检索项目证据、组织设计方法，形成设计解释、案例参照、候选方向与验证计划。</p><div class="mo-engine-roles"><span><b>通用模型</b>理解与生成</span><span><b>知识检索</b>查找证据</span><span><b>方法系统</b>组织分析</span><span><b>研究 Agent</b>执行任务</span><span><b>任务评测</b>检查质量</span></div></div>
        <ol class="mo-research-path" aria-label="创新研究路径"><li>需求澄清</li><li>案例检索</li><li>方法分析</li><li>候选方向</li><li>验证计划</li></ol>
      </article>
      <article class="mo-layer">
        <span class="mo-layer-number">03</span>
        <div class="mo-layer-copy"><h3>应用能力</h3><p>按任务交付不同成果：公众讲解、学习活动、研究简报、验证计划和 Agent 研究上下文。不同应用共享同一份证据，而不是复制出互相矛盾的数据。</p><div class="mo-application-links"><a href="/projects/">项目阅读<span>理解真实设计</span></a><a href="/museum/">好设计馆<span>讲解与互动</span></a><a href="/museum/#education">科技教育<span>课程与再设计</span></a><a href="/needs/">需求研究<span>定义真实问题</span></a><a href="/expo/">产业看台<span>产业研判与报告</span></a><a href="/mcp/">Agent / MCP<span>读取与组包</span></a></div></div>
      </article>
    </div>
    <div class="mo-loops">
      <article><h3>证据可信环</h3><p>每项应用内容都能回到原始资料和研究版本。</p><ol><li>原始资料</li><li>项目事实</li><li>平台分析</li><li>应用内容</li><li>来源与版本</li></ol></article>
      <article><h3>验证生长环</h3><p>只有经过确认的成果，才会沉淀为公共知识。</p><ol><li>用户问题</li><li>研究任务</li><li>候选方向</li><li>人工审核</li><li>验证与回流</li></ol></article>
    </div>
    <div class="mo-network"><h3>人机协同，完成 AI 做不了的部分</h3><div><span><strong>评审与方法专家</strong>校准方法与设计判断</span><span><strong>获奖设计师与团队</strong>补充过程、手稿与口述</span><span><strong>工程师与研究人员</strong>核对工况并开展验证</span><span><strong>企业与教育实践者</strong>提供真实任务和使用反馈</span></div><p>真正的护城河是专家方法论、设计师智慧、工程验证能力与真实需求反馈。</p></div>
  </section>

  <section class="mo-capabilities" id="capabilities" aria-labelledby="mo-capabilities-title">
    <header class="mo-section-heading"><span class="mo-eyebrow">四种核心能力</span><h2 id="mo-capabilities-title">四种核心能力，回答四个真实问题</h2><p>不止生成一段回答，而是交付可以继续研究和验证的工作成果。</p></header>
    <div class="mo-capability-workbench">
      <div class="mo-capability-tabs" role="group" aria-label="选择核心能力">
        <button type="button" data-capability="understand" aria-pressed="true"><span>理解设计</span><strong>这件作品为什么好？</strong><small>有来源的创新解释</small></button>
        <button type="button" data-capability="connect" aria-pressed="false"><span>发现关联</span><strong>谁解决过类似的问题？</strong><small>相似点、差异与条件</small></button>
        <button type="button" data-capability="create" aria-pressed="false"><span>辅助创新</span><strong>我的问题可以怎样研究？</strong><small>候选方向、取舍与未知</small></button>
        <button type="button" data-capability="validate" aria-pressed="false"><span>支持验证</span><strong>怎样判断思路是否成立？</strong><small>数据、指标与停止条件</small></button>
      </div>
      <article class="mo-capability-detail" aria-live="polite">
        <img id="mo-capability-image" src="/inno/portal/covers/case-2025-00.jpg" alt="嫦娥月球钻取采样系统项目示意" loading="lazy">
        <div><span id="mo-capability-label">真实项目解读</span><h3 id="mo-capability-title">从任务约束理解设计选择</h3><p id="mo-capability-text">沿嫦娥采样任务、钻取机构和层序保持，解释为什么这样设计。每项关键判断都能返回项目证据。</p><a id="mo-capability-link" href="/dossier/?project=2025-00">阅读项目证据</a></div>
      </article>
    </div>
  </section>

  <section class="mo-applications" id="applications" aria-labelledby="mo-applications-title">
    <header class="mo-section-heading"><span class="mo-eyebrow">真实应用</span><h2 id="mo-applications-title">同一份证据，支撑不同的创造任务</h2><p>公众听故事，学生理解原理，设计师研究方法，企业分析迁移。表达不同，事实与版本一致。</p></header>
    <div class="mo-app-map" aria-label="一份项目证据连接四种真实应用">
      <a class="mo-app-source" href="/cases/chang-e/"><img src="/inno/portal/covers/case-2025-00.jpg" alt="嫦娥采样系统结构示意" loading="lazy"><span>真实项目证据中心</span><strong>一个嫦娥项目</strong><p>项目事实、资料来源、研究版本与待补边界都从这里出发。</p><small>查看应用案例</small></a>
      <div class="mo-app-branches">
        <a class="mo-app-branch" href="/museum/"><span>01 · 公众与展馆</span><strong>看见与讲解</strong><p>主题展览 · 项目故事</p><small>进入好设计馆</small></a>
        <a class="mo-app-branch" href="/museum/#education"><span>02 · 科技教育</span><strong>学习与再设计</strong><p>活动单 · 探究任务</p><small>查看科技教育</small></a>
        <a class="mo-app-branch" href="/needs/"><span>03 · 企业与研究</span><strong>定义问题与验证</strong><p>需求简报 · 验证计划</p><small>开始需求研究</small></a>
        <a class="mo-app-branch" href="/expo/"><span>04 · 地方产业与 Agent</span><strong>产业研判与工具调用</strong><p>产业报告 · 研究上下文</p><small>进入产业看台</small></a>
      </div>
    </div>
    <p class="mo-app-caption">不同应用共享同一份项目身份与证据，但分别形成适合当前任务的成果；真实项目不会变成四套相互矛盾的数据。</p>
  </section>


  <section class="mo-status" id="boundaries" aria-labelledby="mo-status-title">
    <div class="mo-status-main"><span class="mo-eyebrow">当前建设与边界</span><h2 id="mo-status-title">能力建设，始终以真实验证为准</h2><p>先连接知识与方法，再用真实任务校准，最后根据评测证据决定检索增强、专用模型或微调。当前定义不代表所有目标能力已经完成。</p><div class="mo-status-actions"><a class="mo-primary" href="/projects/">从真实项目开始</a><a class="mo-secondary" href="/about/">了解好设计平台</a></div></div>
    <dl class="mo-status-facts"><div><dt>项目目录</dt><dd>560</dd></div><div><dt>原生研究版</dt><dd>103</dd></div><div><dt>方法档案</dt><dd>64</dd></div><div><dt>MCP 只读工具</dt><dd>12</dd></div></dl>
    <div class="mo-boundaries"><strong>尚不宣称与能力边界</strong><p>不宣称已经自主训练基础大模型。不宣称 560 个项目都已完成同等深度研究。AI 迁移建议不等于工程结论。平台分析不等于官方评审。生成内容不会因看起来完整而自动进入公共知识底座。</p></div>
  </section>
</div>
<script src="/inno/portal/model-official.js" defer></script>'''
