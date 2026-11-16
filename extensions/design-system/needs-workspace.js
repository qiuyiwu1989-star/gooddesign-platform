(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]));
  const KEY = 'gd-needs-workspace-v1';
  const HANDOFF_KEY = 'gd-reasoning-canvas-handoff-v1';
  const STEPS = [
    { title: '真实问题', next: '选择参考资料' },
    { title: '参考资料', next: '比较研究路线' },
    { title: '研究路线', next: '核对并导出计划' },
    { title: '核对计划', next: '导出研究上下文' }
  ];
  const ROUTES = {
    measure: { name: '先验证问题与量测', mechanism: '先明确对象、工况和独立量测基线，再决定技术路线。', action: '建立参考真值、观察指标与停止条件。', methods: ['R48', 'R42'] },
    functions: { name: '拆解功能与接口', mechanism: '先找必要功能、作用接口和异常退出，再讨论实现方式。', action: '形成功能模型，保留未证实的作用关系。', methods: ['R48', 'R14'] },
    concepts: { name: '组合机制与候选概念', mechanism: '从不同子功能组合候选机制，同时保留排除路径。', action: '比较相容、冲突与未知，不直接复制参数。', methods: ['R48', 'R14', 'R17'] }
  };
  const initial = () => ({ step: 0, title: '', problem: '', outcome: '', constraints: '', projects: [], methods: [], route: null, route_selected: false, skipped: [], clarifications: [], revision: 1 });
  const text = value => typeof value === 'string' ? value : '';
  const ids = value => Array.isArray(value) ? [...new Set(value.filter(item => typeof item === 'string'))] : [];
  let state = initial();
  let projects = [];
  let methods = [];
  let projectCatalogFailed = false;
  let methodCatalogFailed = false;
  let storageAvailable = true;
  let message = { text: '', kind: '' };

  function restore(saved) {
    if (!saved || typeof saved !== 'object' || Array.isArray(saved)) return initial();
    const validRoute = typeof saved.route === 'string' && Object.prototype.hasOwnProperty.call(ROUTES, saved.route);
    const route = validRoute && (saved.route_selected === true || saved.route !== 'measure') ? saved.route : null;
    return {
      step: Number.isInteger(saved.step) ? Math.max(0, Math.min(3, saved.step)) : 0,
      title: text(saved.title),
      problem: text(saved.problem),
      outcome: text(saved.outcome),
      constraints: text(saved.constraints),
      projects: ids(saved.projects),
      methods: ids(saved.methods),
      route,
      route_selected: Boolean(route),
      skipped: ids(saved.skipped).filter(item => item === 'references' || item === 'route'),
      clarifications: Array.isArray(saved.clarifications) ? saved.clarifications.filter(item => item && typeof item === 'object' && text(item.value) && text(item.actor)).map(item => ({
        field: text(item.field), value: text(item.value), actor: text(item.actor), status: 'pending_confirmation', saved_at: text(item.saved_at)
      })) : [],
      revision: Number.isInteger(saved.revision) && saved.revision > 0 ? saved.revision : 1
    };
  }

  let savedRaw = null;
  try {
    savedRaw = localStorage.getItem(KEY);
  } catch {
    storageAvailable = false;
    message = { text: '浏览器存储不可用，草稿仅保留在当前页面，请及时导出。', kind: 'error' };
  }
  if (savedRaw) {
    try {
      state = restore(JSON.parse(savedRaw));
    } catch {
      state = initial();
      message = { text: '旧草稿无法读取，已新建草稿。你仍可继续填写并导出。', kind: 'error' };
    }
  }

  function save() {
    try {
      localStorage.setItem(KEY, JSON.stringify(state));
      storageAvailable = true;
      return true;
    } catch {
      storageAvailable = false;
      return false;
    }
  }
  function selectedRoute() { return state.route ? ROUTES[state.route] || null : null; }
  function selectedProjects() { return state.projects.map(id => projects.find(project => project.id === id)).filter(Boolean); }
  function selectedMethods() { return state.methods.map(id => methods.find(method => method.id === id)).filter(Boolean); }
  function referenceNames() {
    return [
      ...state.projects.map(id => projects.find(project => project.id === id)?.name || id),
      ...state.methods.map(id => methods.find(method => method.id === id)?.name || id)
    ];
  }
  function unknowns() {
    const rows = [];
    if (!state.outcome.trim()) rows.push('期待改变与目标口径');
    if (!state.constraints.trim()) rows.push('作业条件与现场约束');
    rows.push('预算与可用资源', '验收口径与停止条件');
    if (!state.projects.length) rows.push('相关项目证据与适用差异');
    if (!state.methods.length) rows.push('方法选择的确认依据');
    if (!state.route) rows.push('研究路线与顺序');
    rows.push('客户或领域责任人的确认');
    return rows;
  }
  function nextAction() {
    if (!state.problem.trim()) return '先描述真实问题';
    if (state.step === 0) return '选择项目或方法作为研究参考，也可以跳过';
    if (state.step === 1) return '比较研究路线，不直接选最优方案';
    if (state.step === 2) return state.route ? '核对未知和研究动作，再导出交接' : '可暂不选择路线，直接核对未知和下一步';
    return '导出研究上下文，或带入独立推理画布';
  }

  function renderSteps() {
    $('steps').innerHTML = STEPS.map((step, index) => `<button class="gd-needs-step" type="button" data-step="${index}" aria-current="${index === state.step ? 'step' : 'false'}"><span>${index + 1}</span>${step.title}</button>`).join('');
    $('steps').querySelectorAll('[data-step]').forEach(button => button.addEventListener('click', () => setStep(Number(button.dataset.step))));
  }

  function notify() {
    const feedback = $('task').querySelector('.gd-needs-message');
    if (!feedback) return;
    feedback.textContent = message.text;
    feedback.dataset.kind = message.kind;
  }

  function renderStatus() {
    const route = selectedRoute();
    const referenceText = state.projects.length || state.methods.length ? `${state.projects.length} 个项目 · ${state.methods.length} 个方法` : state.skipped.includes('references') ? '已跳过选择，不代表没有相关资料' : '暂未选择';
    const routeText = route ? route.name : state.skipped.includes('route') ? '已跳过选择，后续仍可补充' : '暂未选择，可继续';
    const rows = unknowns();
    const unknownSummary = `<details class="gd-needs-unknown-more"><summary>查看全部 ${rows.length} 项待确认</summary><ul class="gd-needs-unknowns">${rows.map(item => `<li>${esc(item)}</li>`).join('')}</ul></details>`;
    $('status').innerHTML = `<section class="gd-needs-status-card gd-needs-taskcard" aria-labelledby="nw-taskcard-title"><h2 id="nw-taskcard-title">研究任务卡</h2><p class="gd-needs-taskcard-name"><strong>${esc(state.title || '未命名研究')}</strong></p><p>本地草稿 · 需求尚未确认</p><dl class="gd-needs-taskcard-list"><div data-task-field="problem"><dt>问题</dt><dd>${esc(state.problem || '尚未填写')}</dd></div><div data-task-field="outcome"><dt>目标</dt><dd>${esc(state.outcome || '待确认，可留空')}</dd></div><div data-task-field="constraints"><dt>约束</dt><dd>${esc(state.constraints || '待确认，可留空')}</dd></div><div data-task-field="references"><dt>参考</dt><dd>${esc(referenceText)}</dd></div><div data-task-field="route"><dt>路线</dt><dd>${esc(routeText)}</dd></div><div data-task-field="unknowns"><dt>未知</dt><dd>${unknownSummary}</dd></div><div data-task-field="next"><dt>下一步</dt><dd>${esc(nextAction())}</dd></div></dl></section>${storageAvailable ? '<p class="gd-needs-draft-note">草稿仅保存在当前浏览器，普通编辑不会写入服务器。</p>' : '<p class="gd-needs-draft-note" data-kind="error">浏览器存储不可用，草稿仅保留在当前页面。请导出研究上下文，避免刷新后丢失。</p>'}`;
    notify();
  }

  function actions(back = true, next = true) {
    return `<div class="gd-needs-actions"><div>${back ? '<button class="gd-button" type="button" data-action="back">返回上一步</button>' : ''}</div><div>${next ? '<button class="gd-button gd-button--primary" type="button" data-action="next">继续</button>' : ''}</div></div><p class="gd-needs-message" data-kind="${message.kind}" role="status">${esc(message.text)}</p>`;
  }

  function guide(title, prompt, content) {
    return `<section class="gd-needs-panel gd-needs-guide"><div class="gd-needs-conversation"><div class="gd-needs-prompt"><img src="/inno/portal/ip-xiaohao.svg?v=078" alt=""><div><span class="gd-kicker">小好 · 研究引导</span><h2>${esc(title)}</h2><p>${esc(prompt)}</p></div></div><div class="gd-needs-reply">${content}</div></div></section>`;
  }

  function renderProblem() {
    return guide('先说真实问题，不急着选方案。', '我会把你填写的内容整理到右侧任务卡，不会猜测标题、目标或约束。目标与约束可以稍后补充。', `<div class="gd-needs-field"><label for="nw-problem">你遇到的问题</label><textarea class="gd-needs-textarea" id="nw-problem" data-field="problem" placeholder="例如：设备在不规则表面作业时效果不稳定，还需要频繁人工处理">${esc(state.problem)}</textarea><small>这是你的陈述，不会自动变成客户确认需求。</small></div><details class="gd-needs-optional"${state.title || state.outcome || state.constraints ? ' open' : ''}><summary>补充研究名称、目标与约束（可选）</summary><div class="gd-needs-optional-body"><div class="gd-needs-field"><label for="nw-title">研究名称</label><input class="gd-needs-input" id="nw-title" data-field="title" value="${esc(state.title)}" placeholder="给这次研究一个容易识别的名字"></div><div class="gd-needs-field"><label for="nw-outcome">期待什么改变</label><textarea class="gd-needs-textarea" id="nw-outcome" data-field="outcome" placeholder="希望减少什么成本、损伤、等待或不确定性">${esc(state.outcome)}</textarea></div><div class="gd-needs-field"><label for="nw-constraints">已知条件与不能牺牲的内容</label><textarea class="gd-needs-textarea" id="nw-constraints" data-field="constraints" placeholder="对象保护、现场环境、现有做法、可用资源、硬约束">${esc(state.constraints)}</textarea><small>不确定的内容可以留空，后续作为待确认补充。</small></div></div></details>${actions(false, true)}`);
  }

  function optionButtons(rows, kind) {
    if (!rows.length) return '<div class="gd-needs-empty">没有匹配结果，可以换个关键词。</div>';
    return rows.map(row => {
      const id = row.id;
      const name = row.name;
      const detail = kind === 'project' ? (row.unit || '完成单位待补') : (row.summary || row.category || '');
      return `<button class="gd-needs-option" type="button" data-select="${kind}" data-id="${esc(id)}"><strong>${esc(name)}</strong><small>${esc(detail)}</small></button>`;
    }).join('');
  }

  function renderReferences() {
    const projectNotice = projectCatalogFailed ? '<p class="gd-needs-empty" id="project-catalog-error">项目目录暂时不可用，方法参考仍可选择，也可以跳过。</p>' : '';
    const methodNotice = methodCatalogFailed ? '<p class="gd-needs-empty" id="method-catalog-error">方法目录暂时不可用，项目参考仍可选择，也可以跳过。</p>' : '';
    return guide('要选择参考资料吗？', '项目和方法都由你明确选择，只作为研究线索。没有匹配结果或暂时不想选择，都可以跳过。', `<div class="gd-needs-reference-grid"><section><h3>参考项目</h3>${projectNotice}<div class="gd-needs-field"><label for="nw-project-query">搜索项目或完成单位</label><input class="gd-needs-input" id="nw-project-query" placeholder="例如：嫦娥、机器人、装备"></div><div class="gd-needs-options" id="project-options">${optionButtons(projects.slice(0, 6), 'project')}</div><div class="gd-needs-selected" id="selected-projects">${selectedProjects().map(project => `<span class="gd-needs-chip">${esc(project.name)}<button type="button" data-remove="project" data-id="${esc(project.id)}" aria-label="移除${esc(project.name)}">移除</button></span>`).join('')}</div></section><section><h3>分析方法</h3>${methodNotice}<div class="gd-needs-field"><label for="nw-method-query">搜索方法或原理</label><input class="gd-needs-input" id="nw-method-query" placeholder="例如：问题定义、功能、验证"></div><div class="gd-needs-options" id="method-options">${optionButtons(methods.slice(0, 6), 'method')}</div><div class="gd-needs-selected" id="selected-methods">${selectedMethods().map(method => `<span class="gd-needs-chip">${esc(method.name)}<button type="button" data-remove="method" data-id="${esc(method.id)}" aria-label="移除${esc(method.name)}">移除</button></span>`).join('')}</div></section></div><p class="gd-needs-description">跳过只表示这里不做选择，不代表没有相关资料，后续仍可返回补充。</p><button class="gd-button gd-button--quiet" type="button" data-action="skip" data-skip="references">跳过参考资料</button>${actions(true, true)}`);
  }

  function renderRoutes() {
    return guide('由你决定研究路线。', '下面是固定的方法模板，不是智能推荐。可以比较后选择，也可以暂不确定并继续核对。', `<div class="gd-needs-routes">${Object.entries(ROUTES).map(([id, route]) => `<button class="gd-needs-route" type="button" data-route="${id}" aria-pressed="${state.route === id}"><h3>${esc(route.name)}</h3><p>${esc(route.mechanism)}</p><p><strong>研究动作：</strong>${esc(route.action)}</p><small>参考方法：${route.methods.join(' · ')}</small></button>`).join('')}</div><p class="gd-needs-description">未选择路线不会阻止继续，也不会被记录成已确认路线。</p><button class="gd-button gd-button--quiet" type="button" data-action="skip" data-skip="route">暂不选择路线</button>${actions(true, true)}`);
  }

  function renderReview() {
    const route = selectedRoute();
    const refs = referenceNames();
    const methodNames = [...new Set([...selectedMethods().map(method => method.name), ...(route ? route.methods : [])])];
    return guide('请核对研究任务卡。', '导出和画布交接都只包含当前任务上下文，不是自动方案、工程结论或客户确认。', `<dl class="gd-needs-summary"><div><dt>研究问题</dt><dd>${esc(state.problem || '尚未填写')}</dd></div><div><dt>期待改变</dt><dd>${esc(state.outcome || '待确认')}</dd></div><div><dt>已知条件</dt><dd>${esc(state.constraints || '待确认')}</dd></div><div><dt>参考资料</dt><dd>${refs.length ? esc(refs.join('、')) : '暂未选择，这不代表没有相关资料'}</dd></div><div><dt>研究方法</dt><dd>${esc(methodNames.length ? methodNames.join('、') : '暂未选择')}</dd></div><div><dt>研究路线</dt><dd>${route ? `${esc(route.name)}：${esc(route.action)}` : '暂未选择，可进入画布后再确认'}</dd></div><div><dt>已跳过</dt><dd>${esc(state.skipped.length ? state.skipped.map(item => item === 'references' ? '参考资料' : '研究路线').join('、') : '无')}</dd></div></dl><div class="gd-needs-clarify"><div><h3>补充待确认条件</h3><p class="gd-needs-description">保存为独立待确认记录，不改写原需求。</p></div><div><div class="gd-needs-field"><label for="nw-clarify-field">补充类型</label><select class="gd-needs-select" id="nw-clarify-field"><option value="operating_context">作业条件</option><option value="budget">预算与资源</option><option value="acceptance_threshold">验收与停止条件</option></select></div><div class="gd-needs-field"><label for="nw-clarify-value">补充内容</label><textarea class="gd-needs-textarea" id="nw-clarify-value" placeholder="已知多少写多少，保存后仍可复核"></textarea></div><div class="gd-needs-field"><label for="nw-clarify-actor">提供者</label><input class="gd-needs-input" id="nw-clarify-actor" placeholder="例如：研究人员、企业工程师"></div><button class="gd-button" type="button" data-action="clarify">保存待确认补充</button></div><ul class="gd-needs-clarify-list" id="clarify-list">${state.clarifications.map(item => `<li><strong>待确认 · ${esc(item.field)}</strong><br>${esc(item.value)}<br>提供者：${esc(item.actor)}</li>`).join('')}</ul></div><div class="gd-needs-export"><button class="gd-button gd-button--primary" type="button" data-action="canvas">进入推理画布</button><button class="gd-button" type="button" data-action="download">导出研究上下文</button><button class="gd-button" type="button" data-action="copy">复制给研究Agent</button><button class="gd-button gd-button--ghost" type="button" data-action="reset">开始另一份草稿</button></div>${actions(true, false)}`);
  }

  function render() {
    renderSteps();
    $('task').innerHTML = state.step === 0 ? renderProblem() : state.step === 1 ? renderReferences() : state.step === 2 ? renderRoutes() : renderReview();
    renderStatus();
    bindInputs();
  }

  function bindOptions(container) {
    container.querySelectorAll('[data-select]').forEach(button => button.addEventListener('click', () => {
      const kind = button.dataset.select;
      const id = button.dataset.id;
      if (!state[kind + 's'].includes(id)) {
        state[kind + 's'].push(id);
        state.skipped = state.skipped.filter(item => item !== 'references');
        save();
        render();
      }
    }));
  }

  function bindInputs() {
    $('task').querySelectorAll('[data-field]').forEach(input => input.addEventListener('input', () => {
      state[input.dataset.field] = input.value;
      save();
      renderStatus();
    }));
    bindOptions($('task'));
    $('task').querySelectorAll('[data-remove]').forEach(button => button.addEventListener('click', () => {
      const kind = button.dataset.remove;
      state[kind + 's'] = state[kind + 's'].filter(id => id !== button.dataset.id);
      save();
      render();
    }));
    $('task').querySelectorAll('[data-route]').forEach(button => button.addEventListener('click', () => {
      state.route = button.dataset.route;
      state.route_selected = true;
      state.skipped = state.skipped.filter(item => item !== 'route');
      save();
      render();
    }));
    $('task').querySelectorAll('[data-action]').forEach(button => button.addEventListener('click', () => action(button.dataset.action, button)));
    const projectQuery = $('nw-project-query');
    if (projectQuery) projectQuery.addEventListener('input', () => {
      const query = projectQuery.value.trim().toLowerCase();
      const rows = projects.filter(project => !query || [project.name, project.unit, project.summary, project.id].join(' ').toLowerCase().includes(query)).slice(0, 6);
      $('project-options').innerHTML = optionButtons(rows, 'project');
      bindOptions($('project-options'));
    });
    const methodQuery = $('nw-method-query');
    if (methodQuery) methodQuery.addEventListener('input', () => {
      const query = methodQuery.value.trim().toLowerCase();
      const rows = methods.filter(method => !query || [method.name, method.summary, method.category, method.id].join(' ').toLowerCase().includes(query)).slice(0, 6);
      $('method-options').innerHTML = optionButtons(rows, 'method');
      bindOptions($('method-options'));
    });
  }

  function setStep(step) {
    if (step > 0 && !state.problem.trim()) {
      message = { text: '先描述真实问题，已输入的其他内容会保留。', kind: 'error' };
      state.step = 0;
    } else {
      state.step = Math.max(0, Math.min(3, step));
      message = { text: '', kind: '' };
    }
    save();
    render();
    const heading = $('task').querySelector('h2');
    if (heading) {
      heading.tabIndex = -1;
      heading.focus({ preventScroll: true });
    }
  }

  function packet() {
    const route = selectedRoute();
    return {
      schema: 'gooddesign-research-packet-1.0',
      status: 'prepared_context_not_executed',
      requirement: {
        title: state.title || '未命名研究',
        problem: state.problem,
        outcome: state.outcome || null,
        constraints: state.constraints || null,
        status: 'research_proposed_not_customer_confirmed',
        revision: state.revision
      },
      route: route ? { id: state.route, ...route } : null,
      project_references: selectedProjects().map(project => ({ id: project.id, name: project.name, research: Boolean(project.research), relation: 'reference_not_adoption_proof' })),
      method_references: [...new Set([...selectedMethods().map(method => method.id), ...(route ? route.methods : [])])],
      skipped: [...state.skipped],
      unknowns: unknowns(),
      pending_clarifications: state.clarifications,
      model_calls: 0,
      source_projects_modified: false,
      engineering_validated: false,
      expert_reviewed: false
    };
  }

  function randomTaskId() {
    if (!window.crypto) throw new Error('secure_random_unavailable');
    if (typeof window.crypto.randomUUID === 'function') return `needs-${window.crypto.randomUUID()}`;
    if (typeof window.crypto.getRandomValues !== 'function') throw new Error('secure_random_unavailable');
    const bytes = new Uint8Array(16);
    window.crypto.getRandomValues(bytes);
    return `needs-${Array.from(bytes, byte => byte.toString(16).padStart(2, '0')).join('')}`;
  }

  function action(name, button) {
    if (name === 'next') return setStep(state.step + 1);
    if (name === 'back') return setStep(state.step - 1);
    if (name === 'skip') {
      const target = button?.dataset.skip;
      if (target !== 'references' && target !== 'route') return;
      if (!state.skipped.includes(target)) state.skipped.push(target);
      if (target === 'route') {
        state.route = null;
        state.route_selected = false;
      }
      return setStep(state.step + 1);
    }
    if (name === 'clarify') {
      const field = $('nw-clarify-field').value;
      const value = $('nw-clarify-value').value.trim();
      const actor = $('nw-clarify-actor').value.trim();
      if (!value || !actor) {
        message = { text: '请填写补充内容和提供者，已输入内容会保留。', kind: 'error' };
        const feedback = $('task').querySelector('.gd-needs-message');
        feedback.textContent = message.text;
        feedback.dataset.kind = message.kind;
        (!value ? $('nw-clarify-value') : $('nw-clarify-actor')).focus();
        return;
      }
      state.clarifications.push({ field, value, actor, status: 'pending_confirmation', saved_at: new Date().toISOString() });
      message = { text: '已保存为待确认补充，原需求未被改写。', kind: 'success' };
      save();
      render();
      return;
    }
    if (name === 'canvas') {
      if (!state.problem.trim()) return setStep(0);
      try {
        const handoff = {
          schema: 'gooddesign-canvas-handoff-1.0',
          task_id: randomTaskId(),
          created_at: new Date().toISOString(),
          packet: packet()
        };
        const serialized = JSON.stringify(handoff);
        localStorage.setItem(HANDOFF_KEY, serialized);
        if (localStorage.getItem(HANDOFF_KEY) !== serialized) throw new Error('handoff_write_not_verified');
        location.assign('/canvas/?from=needs');
      } catch {
        message = { text: '画布交接未能保存，仍停留在本页。请检查浏览器存储，或先导出研究上下文。', kind: 'error' };
        notify();
      }
      return;
    }
    if (name === 'download') {
      const blob = new Blob([JSON.stringify(packet(), null, 2)], { type: 'application/json' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = `${state.title || 'research-packet'}.json`;
      link.click();
      URL.revokeObjectURL(link.href);
      message = { text: '研究上下文已导出，内容仍为待确认研究提案。', kind: 'success' };
      renderStatus();
      return;
    }
    if (name === 'copy') {
      $('handoff-text').value = JSON.stringify(packet(), null, 2);
      $('handoff').showModal();
      $('handoff-text').focus();
      $('handoff-text').select();
      $('handoff-text').scrollTop = 0;
      return;
    }
    if (name === 'reset') {
      if (!confirm('确定开始另一份草稿？当前输入会被清空。')) return;
      state = initial();
      save();
      render();
    }
  }

  $('example').addEventListener('click', () => {
    state.title = '割胶末端与作业流程研究';
    state.problem = '割胶作业需要保护树体和胶乳品质，研究切割、清理与转场如何影响全流程有效产出。';
    state.outcome = '减少树体损伤、胶液混屑和人工清理负担，同时保留现场安全与可验证性。';
    state.constraints = '树皮保护、清洁要求、树况差异和量测资源待确认。';
    state.route = null;
    state.route_selected = false;
    state.skipped = [];
    state.step = 0;
    message = { text: '示例已填入，仍为研究提案，不是客户确认需求。', kind: 'success' };
    save();
    render();
  });

  $('handoff').querySelector('[value="close"]').addEventListener('click', () => $('handoff').close());

  function loadProjects() {
    return fetch('/inno/catalog.json', { cache: 'no-store' }).then(response => {
      if (!response.ok) throw new Error('catalog');
      return response.json();
    }).then(rows => {
      projects = Array.isArray(rows) ? rows : [];
    }).catch(error => {
      projectCatalogFailed = true;
      console.error('needs_project_catalog_load_failed', error);
    }).finally(() => {
      if (state.step === 1) render(); else renderStatus();
    });
  }

  function loadMethods() {
    return fetch('/inno/portal/method-catalog.json', { cache: 'no-store' }).then(response => {
      if (!response.ok) throw new Error('methods');
      return response.json();
    }).then(rows => {
      methods = Array.isArray(rows) ? rows : [];
    }).catch(error => {
      methodCatalogFailed = true;
      console.error('needs_method_catalog_load_failed', error);
    }).finally(() => {
      if (state.step === 1) render(); else renderStatus();
    });
  }

  render();
  loadProjects();
  loadMethods();
})();
