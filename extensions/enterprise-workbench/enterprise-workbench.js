(() => {
  'use strict';
  const $ = selector => document.querySelector(selector);
  const $$ = selector => [...document.querySelectorAll(selector)];
  const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]));
  const words = { proposed: '待确认提案', draft: '草稿', confirmed: '已记录确认', unknown: '未知', conflict: '存在冲突', supported: '有资料支持', pending: '待审核', required: '需要专业批准', approved: '已记录批准', not_required_with_reason: '已说明豁免理由', requires_evidence_and_preference_review: '需结合证据与偏好审查', source_statement: '来源陈述', inferred: '分析推断', hypothesized: '待验证假设', conditional_research_only: '满足条件后可继续研究', blocked_by_constraint_conflict: '约束冲突，暂不可推进', pending_review: '待审核' };
  const keys = { conditions: '成立条件', key_unknowns: '关键未知', next_action: '下一步动作', route_ref: '路线', execution_authorized: '允许工程执行', status: '状态', reason: '理由', actor: '责任人', cost: '成本', budget: '预算', operating_context: '作业条件', acceptance_threshold: '验收条件', resources: '资源', responsible_actor: '责任人', value: '数值或内容', unit: '单位', nature: '内容性质', missing_reason: '待补充', id: '记录', revision: '版本' };
  const fieldLabels = { budget: '预算与资源', operating_context: '作业条件', acceptance_threshold: '验收与停止条件' };
  const kindLabels = { opinion: '意见', reported_observation: '报告观察', reported_trial: '报告试验结果' };
  const views = new Set(['overview', 'requirement', 'routes', 'validation', 'feedback']);
  let currentBundle = JSON.parse($('#initial-bundle').textContent);
  let currentView = views.has(location.hash.slice(1)) ? location.hash.slice(1) : 'overview';
  let selectedRouteId = sessionStorage.getItem('ew-route-' + currentBundle.current_task_id) || currentBundle.routes?.[0]?.id || '';
  let pendingFeedbackIdentity = null;
  let lastEvidenceTrigger = null;

  function friendly(value) {
    if (value === null || value === undefined) return '待确认';
    if (Array.isArray(value)) return value.map(friendly).join('；') || '暂无记录';
    if (typeof value === 'object') {
      if ('value' in value) return friendly(value.value) + (value.nature ? `（${friendly(value.nature)}）` : '') + (value.missing_reason ? `；${friendly(value.missing_reason)}` : '');
      return Object.entries(value).map(([key, item]) => `${keys[key] ?? key}：${friendly(item)}`).join('；');
    }
    if (typeof value === 'boolean') return value ? '是' : '否';
    return words[String(value)] ?? String(value);
  }

  function unknowns() {
    return Object.keys(currentBundle.requirement?.missing_reason ?? {}).map(key => ({ key, label: fieldLabels[key] ?? key, reason: currentBundle.requirement.missing_reason[key] }));
  }

  function selectedRoute() {
    return (currentBundle.routes ?? []).find(route => route.id === selectedRouteId) || currentBundle.routes?.[0];
  }

  function selectedAction() {
    const route = selectedRoute();
    return (currentBundle.research_action ?? []).find(action => action.route_ref?.id === route?.id && action.route_ref?.revision === route?.revision);
  }

  function setMessage(text, kind = '') {
    const node = $('#workspace-status');
    node.textContent = text;
    node.dataset.kind = kind;
  }

  function routeCard(route, detailed = false) {
    const conditions = (route.conditions ?? []).map(condition => `<li>${esc(condition)}</li>`).join('');
    const nextAction = String(route.next_action).replace(/ TASK-[A-Z0-9-]+$/, '');
    return `<article class="ew-route-card"><span class="ew-badge ${route.constraint_status === 'conflict' ? 'ew-badge--warn' : ''}">${esc(friendly(route.constraint_status))}</span><h3>${esc(route.mechanism)}</h3><ul>${conditions}</ul>${detailed ? `<p><strong>成本与代价：</strong>${esc(friendly(route.cost))}</p><p><strong>关键未知：</strong>${esc(friendly(route.missing_reason))}</p>` : ''}<p><strong>下一步：</strong>${esc(nextAction)}</p><div class="ew-route-actions"><button class="gd-button" type="button" data-route-open="${esc(route.id)}">查看验证计划</button><button class="gd-button gd-button--quiet" type="button" data-evidence="${esc(route.id)}">核对候选资料</button></div></article>`;
  }

  function renderNav() {
    $$('[data-view]').forEach(button => {
      if (button.closest('.ew-nav')) button.setAttribute('aria-current', button.dataset.view === currentView ? 'page' : 'false');
    });
  }

  function renderStatus() {
    const requirement = currentBundle.requirement ?? {};
    const missing = unknowns();
    const nextView = missing.length ? 'requirement' : 'routes';
    const nextText = missing.length ? '先补充关键条件，再比较路线' : '比较路线并核对验证计划';
    $('#research-status').innerHTML = `<section class="ew-status-card"><h2>当前研究判断</h2><p><strong>${esc(requirement.goal || '尚未定义研究目标')}</strong></p><p>状态：${esc(friendly(requirement.status))}</p><p>${currentBundle.routes?.length ?? 0} 条候选路线，${currentBundle.research_action?.length ?? 0} 项研究行动</p></section><section class="ew-status-next"><strong>建议下一步</strong><p>${nextText}</p><button class="gd-button" type="button" data-view="${nextView}">${missing.length ? '补充关键条件' : '比较研究路线'}</button></section><section class="ew-status-card"><h2>仍需确认</h2><div class="ew-unknowns">${missing.length ? missing.map(row => `<button class="ew-unknown-button" type="button" data-unknown="${esc(row.key)}"><strong>${esc(row.label)}</strong><br>${esc(row.reason)}</button>`).join('') : '<p>当前未列出额外缺失项，请继续核对输入。</p>'}</div></section>`;
  }

  function renderOverview() {
    const methods = (currentBundle.methods ?? []).map(method => `<span>${esc(method.method_id)} ${esc(method.name)}</span>`).join('');
    return `<section class="ew-panel" id="decision-overview"><header class="ew-section-heading"><h2>先比较研究路线，再决定验证什么。</h2><p>三条路线都来自当前任务包。它们不是自动生成的企业方案，也不存在无依据的最优排名。</p></header><div class="ew-route-grid">${(currentBundle.routes ?? []).map(route => routeCard(route)).join('')}</div></section><section class="ew-panel"><header class="ew-section-heading"><h2>这项任务已有的研究基础</h2><p>经验、方法与行动分别呈现，不将资料存在误解为迁移已经成立。</p></header><div class="ew-fact-grid"><div class="ew-fact"><strong>${currentBundle.routes?.length ?? 0}</strong><span>候选路线</span></div><div class="ew-fact"><strong>${currentBundle.research_action?.length ?? 0}</strong><span>研究行动</span></div><div class="ew-fact"><strong>${currentBundle.experiences?.length ?? 0}</strong><span>可查阅经验</span></div></div><h3>本任务方法</h3><div class="ew-method-row">${methods}</div><p class="ew-callout">${esc(currentBundle.notice || '当前为研究提案，需要继续核对对象与条件。')}</p></section>`;
  }

  function renderRequirement() {
    const requirement = currentBundle.requirement ?? {};
    const source = requirement.source_ref ?? {};
    const constraints = (requirement.constraints_proposed ?? []).map(item => `<li>${esc(item)}</li>`).join('');
    const records = (currentBundle.clarifications ?? []).map(row => `<li><strong>待确认 · ${esc(fieldLabels[row.field] ?? row.field)}</strong><br>${esc(row.value)}<br>提供者：${esc(row.actor)}</li>`).join('');
    return `<section class="ew-panel"><header class="ew-section-heading"><h2>先确认问题与边界，不急着确认方案。</h2><p>原需求保持独立版本。任何补充都先进入待确认记录，不自动成为客户事实。</p></header><h3 class="ew-goal">${esc(requirement.goal)}</h3><div class="ew-requirement-grid"><article class="ew-info-block"><h3>需求来源与确认状态</h3><p><strong>状态：</strong>${esc(friendly(requirement.status))}</p><p><strong>记录：</strong>${esc(requirement.id)} v${esc(requirement.revision)}</p><p><strong>来源：</strong>${esc(source.source_kind || '研究整理稿')}</p><p>${esc(source.original_user_request_status || currentBundle.notice)}</p></article><article class="ew-info-block"><h3>当前硬约束提案</h3><ul>${constraints || '<li>尚未记录约束，需要补充。</li>'}</ul></article></div></section><section class="ew-panel"><header class="ew-section-heading"><h2>补充待确认条件</h2><p>已知多少写多少。保存后仍可复核，不改写原需求，不触发自动方案生成。</p></header><form class="ew-form" id="clarify-form"><div class="ew-field-inline"><div class="ew-field"><label for="clarify-field">补充类型</label><select id="clarify-field"><option value="operating_context">作业条件</option><option value="budget">预算与资源</option><option value="acceptance_threshold">验收与停止条件</option></select></div><div class="ew-field"><label for="clarify-actor">提供者</label><input id="clarify-actor" placeholder="例如：企业工程师、研究人员"></div></div><div class="ew-field"><label for="clarify-value">补充内容</label><textarea id="clarify-value" placeholder="记录工况、预算、资源或验收口径，不确定的仍需注明"></textarea></div><button class="gd-button gd-button--primary" type="submit" id="clarify-save">保存待确认补充</button><p class="ew-form-status" id="clarify-status" role="status" aria-live="polite"></p></form><ul class="ew-clarifications" id="clarify-records">${records}</ul></section>`;
  }

  function renderRoutes() {
    const methods = (currentBundle.methods ?? []).map(method => `<article class="ew-info-block"><h3>${esc(method.method_id)} ${esc(method.name)}</h3><p>${esc(friendly(method.scope))}</p></article>`).join('');
    return `<section class="ew-panel"><header class="ew-section-heading"><h2>比较机制、条件与代价，不选表面最优。</h2><p>${esc(friendly(currentBundle.comparison?.recommendation_status))}。证据充分程度与用户偏好需要分别判断。</p></header><div class="ew-route-grid">${(currentBundle.routes ?? []).map(route => routeCard(route, true)).join('')}</div><p class="ew-callout">${esc(currentBundle.transfer?.notice || '结构迁移仍需双侧核对，不直接复制原项目参数。')}</p></section><section class="ew-panel"><header class="ew-section-heading"><h2>本任务方法</h2><p>方法提供分析路径，不自动执行，也不证明项目团队曾采用这些方法。</p></header><div class="ew-requirement-grid">${methods}</div></section>`;
  }

  function renderValidation() {
    const route = selectedRoute();
    const action = selectedAction();
    const tabs = (currentBundle.routes ?? []).map(item => `<button type="button" data-route-tab="${esc(item.id)}" aria-pressed="${item.id === route?.id}">${esc(item.mechanism)}</button>`).join('');
    if (!route || !action) return `<section class="ew-panel"><div class="ew-empty">当前路线还没有可核对的验证行动。</div></section>`;
    const hypotheses = (action.hypotheses ?? []).map(item => `<li>${esc(item)}</li>`).join('');
    return `<section class="ew-panel"><header class="ew-section-heading"><h2>把路线变成可判别的研究行动。</h2><p>先明确怎样区分竞争解释，以及何时停止或改道。未获批准前不进入实体试验。</p></header><div class="ew-route-tabs" role="group" aria-label="选择验证路线">${tabs}</div><span class="ew-badge ew-badge--warn">${esc(friendly(action.professional_approval?.status))}</span><h3 class="ew-goal">${esc(action.question)}</h3><dl class="ew-validation-list"><div><dt>竞争解释</dt><dd><ul>${hypotheses}</ul></dd></div><div><dt>观测内容</dt><dd>${esc(action.observation)}</dd></div><div><dt>判别方式</dt><dd>${esc(action.decision_rule)}</dd></div><div><dt>停止条件</dt><dd>${esc(action.stop_condition)}</dd></div><div><dt>研究资源</dt><dd>${esc(friendly(action.resources))}${action.missing_reason?.resources ? `<br><small>${esc(action.missing_reason.resources)}</small>` : ''}</dd></div><div><dt>责任主体</dt><dd>${esc(friendly(action.responsible_actor))}${action.missing_reason?.responsible_actor ? `<br><small>${esc(action.missing_reason.responsible_actor)}</small>` : ''}</dd></div><div><dt>工程执行</dt><dd>${esc(friendly(action.execution_authorized))}，结构校验仅用于研究整理，不授权实体试验，也不证明批准真实性。</dd></div></dl><button class="gd-button gd-button--primary" id="export-plan" type="button">导出研究交接</button></section>`;
  }

  function renderFeedback() {
    const route = selectedRoute();
    const options = (currentBundle.routes ?? []).map(item => `<option value="${esc(item.id)}">${esc(item.mechanism)} · v${esc(item.revision)}</option>`).join('');
    const feedback = (currentBundle.feedback ?? []).map(item => `<article class="ew-feedback-item"><strong>${esc(kindLabels[item.kind] ?? item.kind)} · ${esc(friendly(item.processing_status))}</strong><p>${esc(item.basis)}</p><p>角色：${esc(item.actor_role)}，路线：${esc(item.route_ref?.id)} v${esc(item.route_ref?.revision)}</p></article>`).join('');
    return `<section class="ew-panel"><header class="ew-section-heading"><h2>让反馈回到具体判断，而不是散落在对话里。</h2><p>每条反馈精确绑定需求、路线和主张版本。保存后等待审核，事实与评分不自动改变。</p></header><form class="ew-form" id="feedback-form"><div class="ew-field"><label for="route-select">反馈路线</label><select id="route-select">${options}</select><p class="ew-form-status" id="binding-note" role="status"></p></div><div class="ew-field-inline"><div class="ew-field"><label for="feedback-kind">反馈类型</label><select id="feedback-kind"><option value="opinion">意见</option><option value="reported_observation">报告观察</option><option value="reported_trial">报告试验结果</option></select></div><div class="ew-field"><label for="actor-role">你的角色</label><input id="actor-role" placeholder="例如：企业工程师、研究人员"></div></div><div class="ew-field"><label for="feedback-body">反馈内容及判断依据</label><textarea id="feedback-body" placeholder="写清支持、反对或需要修正的内容，以及依据"></textarea></div><label class="ew-check"><input type="checkbox" id="internal-consent">允许本次反馈用于内部研究，不公开、不用于训练</label><details class="ew-advanced"><summary>高级：检查或编辑反馈 JSON</summary><label class="ew-check"><input type="checkbox" id="advanced-mode">使用下方 JSON 提交</label><div class="ew-field"><label for="feedback-input">反馈 JSON</label><textarea id="feedback-input" spellcheck="false"></textarea></div></details><button class="gd-button gd-button--primary" id="save" type="submit" disabled>确认保存反馈</button></form></section><section class="ew-panel"><header class="ew-section-heading"><h2>已保存反馈</h2><p>按当前需求版本显示，待审核内容不会自动进入事实或训练。</p></header><div class="ew-feedback-list">${feedback || '<div class="ew-empty">当前需求版本还没有反馈记录。</div>'}</div></section>`;
  }

  function render() {
    if (!views.has(currentView)) currentView = 'overview';
    if (!(currentBundle.routes ?? []).some(route => route.id === selectedRouteId)) selectedRouteId = currentBundle.routes?.[0]?.id || '';
    renderNav();
    renderStatus();
    const host = $('#workspace-view');
    host.innerHTML = currentView === 'overview' ? renderOverview() : currentView === 'requirement' ? renderRequirement() : currentView === 'routes' ? renderRoutes() : currentView === 'validation' ? renderValidation() : renderFeedback();
    if (currentView === 'feedback') {
      $('#route-select').value = selectedRouteId;
      updateBinding();
    }
  }

  function setView(view) {
    if (!views.has(view)) return;
    currentView = view;
    if (location.hash !== '#' + view) location.hash = view;
    else render();
  }

  function selectRoute(id, targetView = currentView) {
    selectedRouteId = id;
    sessionStorage.setItem('ew-route-' + currentBundle.current_task_id, id);
    setView(targetView);
  }

  function selectedBinding() {
    const route = (currentBundle.routes ?? []).find(item => item.id === $('#route-select')?.value);
    const requirement = currentBundle.requirement;
    const claim = (currentBundle.claims ?? []).find(item => item.route_ref?.id === route?.id && item.route_ref?.revision === route?.revision);
    return { requirement, route, claim };
  }

  function updateBinding() {
    const { requirement, route, claim } = selectedBinding();
    const allowed = Boolean(requirement && route && claim);
    if ($('#save')) $('#save').disabled = !allowed;
    if ($('#binding-note')) $('#binding-note').textContent = allowed ? `绑定需求 ${requirement.id} v${requirement.revision}，路线 ${route.id} v${route.revision}，主张 ${claim.id} v${claim.revision}` : '该路线尚无可绑定的主张记录，暂不能保存反馈。';
  }

  function formFeedback() {
    const { requirement, route, claim } = selectedBinding();
    if (!requirement || !route || !claim) throw Error('缺少精确主张绑定');
    if (!$('#internal-consent').checked) throw Error('请明确内部研究用途授权');
    const basis = $('#feedback-body').value.trim();
    const role = $('#actor-role').value.trim();
    if (!basis || !role) throw Error('请填写角色与反馈依据');
    const signature = JSON.stringify([requirement.id, requirement.revision, route.id, route.revision, claim.id, claim.revision, $('#feedback-kind').value, role, basis]);
    if (pendingFeedbackIdentity?.signature !== signature) pendingFeedbackIdentity = { signature, id: 'FB-' + crypto.randomUUID() };
    return { schema_version: '0.1.0', id: pendingFeedbackIdentity.id, revision: 1, requirement_ref: { id: requirement.id, revision: requirement.revision }, route_ref: { id: route.id, revision: route.revision }, claim_ref: { id: claim.id, revision: claim.revision }, kind: $('#feedback-kind').value, actor_role: role, basis, authorization: { internal_research: true, public: false, training: false } };
  }

  function openEvidence(trigger) {
    lastEvidenceTrigger = trigger;
    const experiences = currentBundle.experiences ?? [];
    $('#evidence-content').innerHTML = experiences.length ? experiences.map(experience => `<article class="ew-evidence-card"><h3>${esc(experience.object_scope)}</h3><p><strong>来源中的机制或过程：</strong>${esc(friendly(experience.mechanism))}</p><p><strong>适用限制：</strong>${esc(friendly(experience.limitations))}</p>${(experience.evidence_refs ?? []).map(ref => `<p>项目 ${esc(ref.project_id)}，${esc(ref.research_revision)}，${esc(ref.chunk_id)}</p><blockquote>${esc(ref.quote)}</blockquote>`).join('')}</article>`).join('') : '<div class="ew-empty">尚无可查阅证据。</div>';
    $('#evidence-panel').showModal();
    $('#evidence-close').focus();
  }

  async function reload() {
    const draft = $('#feedback-body')?.value ?? '';
    setMessage('正在读取当前研究数据。');
    try {
      const response = await fetch('/api/bundle' + location.search, { credentials: 'same-origin', cache: 'no-store' });
      if (!response.ok) throw Error('读取失败 HTTP ' + response.status);
      currentBundle = await response.json();
      render();
      if ($('#feedback-body') && draft) $('#feedback-body').value = draft;
      setMessage('已读取当前数据，请核对版本。', 'success');
    } catch (error) {
      setMessage(String(error) + '。当前内容与未保存草稿已保留，可重试。', 'error');
    }
  }

  function exportPlan() {
    const route = selectedRoute();
    const action = selectedAction();
    const packet = { schema: 'gooddesign-enterprise-workbench-handoff-1.0', status: 'prepared_context_not_executed', task_id: currentBundle.current_task_id, requirement: currentBundle.requirement, route, research_action: action, comparison: currentBundle.comparison, methods: currentBundle.methods, pending_clarifications: currentBundle.clarifications, model_calls: 0, source_projects_modified: false, execution_authorized: false, engineering_validated: false, expert_reviewed: false };
    const blob = new Blob([JSON.stringify(packet, null, 2)], { type: 'application/json' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `${currentBundle.current_task_id}-${route?.id || 'research'}.json`;
    link.click();
    URL.revokeObjectURL(link.href);
    setMessage('研究交接已导出，内容仍是待核实的研究计划。', 'success');
  }

  document.addEventListener('click', event => {
    const view = event.target.closest('[data-view]');
    if (view) return setView(view.dataset.view);
    const unknown = event.target.closest('[data-unknown]');
    if (unknown) {
      setView('requirement');
      $('#clarify-field').value = unknown.dataset.unknown;
      $('#clarify-value').focus();
      return;
    }
    const routeOpen = event.target.closest('[data-route-open]');
    if (routeOpen) return selectRoute(routeOpen.dataset.routeOpen, 'validation');
    const routeTab = event.target.closest('[data-route-tab]');
    if (routeTab) {
      selectedRouteId = routeTab.dataset.routeTab;
      sessionStorage.setItem('ew-route-' + currentBundle.current_task_id, selectedRouteId);
      render();
      return;
    }
    const evidence = event.target.closest('[data-evidence]');
    if (evidence) return openEvidence(evidence);
    if (event.target.closest('#export-plan')) return exportPlan();
  });

  document.addEventListener('change', event => {
    if (event.target.id === 'route-select') {
      selectedRouteId = event.target.value;
      sessionStorage.setItem('ew-route-' + currentBundle.current_task_id, selectedRouteId);
      updateBinding();
    }
  });

  document.addEventListener('submit', async event => {
    if (event.target.id === 'clarify-form') {
      event.preventDefault();
      const button = $('#clarify-save');
      const status = $('#clarify-status');
      const data = { task_id: currentBundle.current_task_id, field: $('#clarify-field').value, value: $('#clarify-value').value.trim(), actor: $('#clarify-actor').value.trim() };
      if (!data.value || !data.actor) {
        status.textContent = '请填写补充内容和提供者，已输入内容会保留。';
        status.dataset.kind = 'error';
        (!data.value ? $('#clarify-value') : $('#clarify-actor')).focus();
        return;
      }
      try {
        button.disabled = true;
        const response = await fetch('/api/clarifications', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
        if (!response.ok) throw Error('保存失败 HTTP ' + response.status);
        $('#clarify-value').value = '';
        $('#clarify-actor').value = '';
        await reload();
        $('#clarify-status').textContent = '已保存为待确认补充，原需求未被改写。';
        $('#clarify-status').dataset.kind = 'success';
      } catch (error) {
        status.textContent = String(error) + '，输入已保留。';
        status.dataset.kind = 'error';
      } finally {
        button.disabled = false;
      }
      return;
    }
    if (event.target.id !== 'feedback-form') return;
    event.preventDefault();
    const button = $('#save');
    try {
      const generated = formFeedback();
      const data = $('#advanced-mode').checked ? JSON.parse($('#feedback-input').value) : generated;
      button.disabled = true;
      setMessage('正在保存反馈。');
      const response = await fetch('/api/feedback', { method: 'POST', credentials: 'same-origin', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
      if (!response.ok) throw Error('保存失败 HTTP ' + response.status + ' ' + await response.text());
      pendingFeedbackIdentity = null;
      await reload();
      if ($('#feedback-body')) $('#feedback-body').value = '';
      setMessage('反馈已保存，等待审核。', 'success');
    } catch (error) {
      setMessage(String(error) + '。输入已保留，请修正后重试。', 'error');
    } finally {
      updateBinding();
    }
  });

  function updateTasks() {
    const select = $('#task-select');
    select.innerHTML = (currentBundle.tasks ?? []).map(task => `<option value="${esc(task.task_id)}">${esc(task.title ?? task.task_id)}</option>`).join('');
    if (currentBundle.current_task_id) select.value = currentBundle.current_task_id;
  }

  $('#task-select').addEventListener('change', () => {
    const url = new URL(location.href);
    url.searchParams.set('task', $('#task-select').value);
    url.hash = 'overview';
    location.assign(url.pathname + url.search + url.hash);
  });
  $('#reload').addEventListener('click', reload);
  $('#evidence-close').addEventListener('click', () => $('#evidence-panel').close());
  $('#evidence-panel').addEventListener('close', () => lastEvidenceTrigger?.focus());
  $('#evidence-panel').addEventListener('click', event => {
    if (event.target !== $('#evidence-panel')) return;
    const rect = $('#evidence-panel').getBoundingClientRect();
    if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) $('#evidence-panel').close();
  });
  addEventListener('hashchange', () => {
    currentView = views.has(location.hash.slice(1)) ? location.hash.slice(1) : 'overview';
    render();
  });
  updateTasks();
  render();
})();
