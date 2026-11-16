const modelLayers = {
  database: {
    label: '平台知道什么',
    title: '一个项目，只有一份主档案',
    text: '问题、约束、设计机制、验证和来源按统一结构保存。展馆、教育与 Agent 引用同一项目身份和研究版本。',
    route: '/inno/dossier/?project=2025-00',
    action: '阅读嫦娥项目档案'
  },
  engine: {
    label: '平台怎样研究',
    title: '让模型调用知识与方法，而非凭空回答',
    text: '通用模型负责理解与生成，知识检索找到证据，方法系统组织分析，研究 Agent 执行任务，评测检查引用与建议质量。',
    route: '/inno/methods/',
    action: '查看创新方法库'
  },
  applications: {
    label: '用户完成什么',
    title: '从真实问题出发，带走可验证的成果',
    text: '项目阅读、展馆、教育、需求研究、企业创新和 MCP 共享同一份证据，分别形成适合当前任务的应用成果。',
    route: '/inno/apps/',
    action: '进入应用中心'
  }
};

const capabilities = {
  understand: {
    label: '真实项目解读',
    title: '从任务约束理解设计选择',
    text: '沿嫦娥采样任务、钻取机构和层序保持，解释为什么这样设计。每项关键判断都能返回项目证据。',
    image: '/inno/portal/illustrations/2025-pixel-v1/2025-00-r1.webp?v=93a2d741d6',
    alt: '嫦娥月球钻取采样系统项目示意',
    route: '/inno/dossier/?project=2025-00',
    action: '阅读项目证据'
  },
  connect: {
    label: '跨项目发现关联',
    title: '比较相似机制，也说明哪里不能照搬',
    text: '从真实项目的场景、问题和设计机制寻找参照，同时比较工况、约束和验证差异，不只返回相似名称。',
    image: '/inno/portal/covers/case-2021-00.jpg',
    alt: '火星车移动系统项目照片',
    route: '/inno/',
    action: '探索真实项目'
  },
  create: {
    label: '条件化迁移研究',
    title: '形成候选方向，而不是直接复制方案',
    text: '割胶机器人研究从真实项目机制出发，保留树体保护、胶乳质量和现场流程约束，形成有待验证的候选路线。',
    image: '/inno/portal/illustrations/2025-pixel-v1/2025-00-r1.webp?v=93a2d741d6',
    alt: '作为迁移研究参考的嫦娥采样系统',
    route: '/inno/cases/rubber-tapping/',
    action: '查看迁移研究案例'
  },
  validate: {
    label: '证据与验证边界',
    title: '把已知、推断和待验证分开',
    text: '研究档案保留原始试验、公开报道、AI 分析和待补事项。数据、对照、指标与停止条件必须重新确认。',
    image: '/inno/portal/covers/case-2015-02.jpg',
    alt: '蛟龙号载人潜水器项目照片',
    route: '/inno/dossier/?project=2015-02',
    action: '查看研究档案'
  }
};

function selectLayer(key) {
  const item = modelLayers[key];
  if (!item) return;
  document.querySelectorAll('[data-model-layer]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.modelLayer === key)));
  document.getElementById('mo-layer-label').textContent = item.label;
  document.getElementById('mo-system-title').textContent = item.title;
  document.getElementById('mo-layer-text').textContent = item.text;
  const link = document.getElementById('mo-layer-link');
  link.href = item.route;
  link.textContent = item.action;
}

function selectCapability(key) {
  const item = capabilities[key];
  if (!item) return;
  document.querySelectorAll('[data-capability]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.capability === key)));
  document.getElementById('mo-capability-label').textContent = item.label;
  document.getElementById('mo-capability-title').textContent = item.title;
  document.getElementById('mo-capability-text').textContent = item.text;
  const image = document.getElementById('mo-capability-image');
  image.src = item.image;
  image.alt = item.alt;
  const link = document.getElementById('mo-capability-link');
  link.href = item.route;
  link.textContent = item.action;
}

document.querySelectorAll('[data-model-layer]').forEach(button => button.addEventListener('click', () => selectLayer(button.dataset.modelLayer)));
document.querySelectorAll('[data-capability]').forEach(button => button.addEventListener('click', () => selectCapability(button.dataset.capability)));

if (window.matchMedia('(prefers-reduced-motion: no-preference)').matches && 'IntersectionObserver' in window) {
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('mo-visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.08 });
  document.querySelectorAll('.mo-definition, .mo-layer, .mo-loops, .mo-network, .mo-capabilities, .mo-applications, .mo-difference, .mo-status').forEach(element => {
    element.classList.add('mo-reveal');
    observer.observe(element);
  });
}
