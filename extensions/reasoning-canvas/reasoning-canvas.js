/* 推理画布视图层：渲染与事件绑定。状态变更一律经 RC_State 动作。 */
(() => {
  const S = RC_State;
  const D = RC_DATA;
  let state = S.load();

  /* RC-08 本机工作区：localStorage 仍是降级层，服务可达时追加不可覆盖修订 */
  const WORKSPACE_ID = 'rubber-tapping-demo';
  const RC_API = location.pathname.startsWith('/inno/canvas/') ? '/inno/canvas/api/rc' : '/api/rc';
  const workspaceStatusEl = document.getElementById('rc-workspace-status');
  let workspaceRevision = 0;
  let remoteAvailable = false;
  let remoteSaving = false;
  let remoteQueued = false;
  let remoteTimer = null;

  function setWorkspaceStatus(text, tone) {
    workspaceStatusEl.textContent = text;
    workspaceStatusEl.classList.toggle('is-ok', tone === 'ok');
    workspaceStatusEl.classList.toggle('is-warn', tone === 'warn');
  }

  function apiPost(path, payload) {
    return fetch(path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    }).then(r => r.json()).then(j => {
      if (!j.ok) throw Object.assign(new Error(j.error || '服务返回失败'), { code: j.code });
      return j;
    });
  }

  function queueRemoteSave() {
    if (!remoteAvailable && workspaceRevision === 0) return;
    setWorkspaceStatus('待保存', 'warn');
    clearTimeout(remoteTimer);
    remoteTimer = setTimeout(persistRemote, 500);
  }

  async function persistRemote() {
    if (remoteSaving) { remoteQueued = true; return; }
    remoteSaving = true;
    const snapshot = JSON.parse(JSON.stringify(state));
    const base = workspaceRevision;
    try {
      const j = await apiPost(`${RC_API}/state`, { workspace_id: WORKSPACE_ID, base_revision: base, state: snapshot });
      workspaceRevision = j.result.revision;
      remoteAvailable = true;
      setWorkspaceStatus(`已保存 · r${workspaceRevision}`, 'ok');
    } catch (e) {
      if (e.code === 'revision_conflict') setWorkspaceStatus('版本冲突，本地保留', 'warn');
      else setWorkspaceStatus('服务未启动，仅本地', 'warn');
      remoteAvailable = false;
    } finally {
      remoteSaving = false;
      if (remoteQueued) { remoteQueued = false; queueRemoteSave(); }
    }
  }

  async function restoreWorkspace() {
    try {
      const j = await apiGet(`${RC_API}/state?workspace_id=${encodeURIComponent(WORKSPACE_ID)}`);
      state = Object.assign(S.defaultState(), j.result.state || {});
      workspaceRevision = j.result.revision;
      remoteAvailable = true;
      setWorkspaceStatus(`工作区 r${workspaceRevision}`, 'ok');
      render(); fitView(); updateFlowUI(); restoreFlow();
    } catch (e) {
      setWorkspaceStatus(e.code === 'workspace_not_found' ? '新工作区 · 本地草稿' : '服务未启动，仅本地', 'warn');
    }
  }

  /* RC-09 本地三角色视图：约束界面操作，不冒充身份认证 */
  const ROLE_KEY = 'gd-reasoning-canvas-role';
  const ROLE_LABEL = { designer: '设计师', advisor: '顾问', expert: '专家' };
  const ROLE_NOTE_WHO = { designer: '我', advisor: '顾问', expert: '专家' };
  const ROLE_PERMS = {
    designer: { status: true, evidence: true, concept: true, priority: true, reason: true, commit: true, intent: true, subproblem: true, note: true, reset: true },
    advisor: { status: false, evidence: false, concept: false, priority: false, reason: false, commit: false, intent: true, subproblem: true, note: true, reset: false },
    expert: { status: false, evidence: false, concept: false, priority: false, reason: false, commit: false, intent: false, subproblem: false, note: true, reset: false }
  };
  const roleEl = document.getElementById('rc-role');
  let currentRole = localStorage.getItem(ROLE_KEY) || 'designer';
  if (!ROLE_PERMS[currentRole]) currentRole = 'designer';
  roleEl.value = currentRole;
  const can = key => ROLE_PERMS[currentRole][key];

  roleEl.addEventListener('change', () => {
    currentRole = roleEl.value;
    localStorage.setItem(ROLE_KEY, currentRole);
    applyRoleChrome();
    render();
  });

  function applyRoleChrome() {
    document.getElementById('rc-reset').disabled = !can('reset');
  }
  applyRoleChrome();

  const viewportEl = document.getElementById('rc-viewport');
  const worldEl = document.getElementById('rc-world');
  const edgesEl = document.getElementById('rc-edges');
  const detailEl = document.getElementById('rc-detail');

  /* ComfyUI 式自由画布：节点卡片、端口圆点、贝塞尔连线、拖动/平移/缩放 */
  const WORLD_W = 2700, WORLD_H = 2050;
  const DEFAULT_POS = {
    n1: { x: 60, y: 760 }, n2: { x: 520, y: 760 }, n3: { x: 980, y: 760 },
    n4: { x: 1440, y: 760 }, n5: { x: 1440, y: 1480 }, n6: { x: 1900, y: 1480 }, n7: { x: 2360, y: 1480 },
    A: { x: 1180, y: 80 }, B: { x: 1440, y: 80 }, C: { x: 1700, y: 80 },
    D: { x: 1180, y: 330 }, E: { x: 1440, y: 330 }, F: { x: 1700, y: 330 }
  };
  /* 数字员工团队：DesignGPT 式多角色协作（arXiv:2311.11591） */
  const AGENTS = [
    { id: 'scribe', name: '书记员', tone: 'warn', stage: 'n1' },
    { id: 'scout', name: '检索员', tone: 'info', stage: 'n2' },
    { id: 'coach', name: '陪练', tone: 'plain', stage: 'n3' },
    { id: 'ideator', name: '点子库', tone: 'accent', stage: 'n4' },
    { id: 'redteam', name: '红队', tone: 'err', stage: 'n5' },
    { id: 'you', name: '你', tone: 'ok', stage: 'n6', human: true },
    { id: 'archivist', name: '档案员', tone: 'plain', stage: 'n7' }
  ];
  const FN_W = 220, FN_H = 58;
  const CHAIN = [['n1', 'n2'], ['n2', 'n3'], ['n3', 'n4'], ['n4', 'n5'], ['n5', 'n6'], ['n6', 'n7']];
  const BRANCHES = D.concepts.map(c => ['n4', c.id]);
  const NODE_TONE = { n1: 'warn', n2: 'info', n3: 'plain', n4: 'accent', n5: 'err', n6: 'ok', n7: 'plain' };
  let view = { x: 28, y: 28, k: 1 };
  let focusConcept = null;
  const isMobileCanvas = () => window.matchMedia('(max-width: 980px)').matches;
  const posOf = id => (state.positions && state.positions[id]) || DEFAULT_POS[id];

  /* ============ 流程引擎：多 Agent 脑暴展开 ============ */
  let flowNodes = [];      // {id,type,x,y,title,sub,cls,agent}
  let flowEdgesDrawn = []; // {from,to,cls}
  let flowEngineData = null;
  let flowRunning = false;
  const feedEl = document.getElementById('rc-feed');
  const rosterEl = document.getElementById('rc-roster');
  const flowBtn = document.getElementById('rc-flow-run');
  const flowHint = document.getElementById('rc-flow-hint');

  function flowAnchor(id, side) {
    if (/^n\d$/.test(id)) {
      const sel = side === 'out' ? `[data-node="${id}"] [data-port-out="main"]` : `[data-node="${id}"] [data-port-in]`;
      const el = worldEl.querySelector(sel);
      return el ? portCenter(el) : null;
    }
    const f = flowNodes.find(n => n.id === id);
    if (!f) return null;
    return side === 'out' ? { x: f.x + FN_W, y: f.y + FN_H / 2 } : { x: f.x, y: f.y + FN_H / 2 };
  }

  /* 按当前条件构建展开图：证据、子问题、功能、选项、红队、档案 */
  function buildFlow() {
    flowNodes = []; flowEdgesDrawn = [];
    const p1 = posOf('n1'), p2 = posOf('n2'), p3 = posOf('n3'), p4 = posOf('n4'), p5 = posOf('n5'), p7 = posOf('n7');
    const counts = Object.fromEntries(state.intent.map(g => [g.key, g.items.length]));
    flowNodes.push({ id: 'sum-intent', type: 'sum', agent: 'scribe', x: p1.x, y: p1.y + 190,
      title: `意图：${counts['事实'] || 0} 事实 · ${counts['假设'] || 0} 假设 · ${counts['待补证'] || 0} 待补证`,
      sub: '', cls: '' });
    flowEdgesDrawn.push({ from: 'n1', to: 'sum-intent' });
    const evs = [...D.evidence, ...state.extraEvidence];
    evs.forEach((e, i) => {
      const id = 'ev-' + e.id;
      flowNodes.push({ id, type: 'ev', agent: 'scout', x: p2.x - 60 + (i % 2) * 250, y: p2.y + 190 + Math.floor(i / 2) * 84,
        title: `[${e.id}] ${e.t || e.title}`, sub: (e.d || e.desc || '').slice(0, 34),
        cls: state.evMarks[e.id] === 'trust' ? 'is-trust' : 'is-doubt' });
      flowEdgesDrawn.push({ from: 'n2', to: id, cls: state.evMarks[e.id] === 'trust' ? '' : 'is-doubt' });
    });
    state.subproblems.forEach((s, i) => {
      const id = 'sp-' + i;
      flowNodes.push({ id, type: 'sp', agent: 'coach', x: p3.x - 60 + (i % 2) * 250, y: p3.y + 190 + Math.floor(i / 2) * 84,
        title: s.split('：')[0], sub: i >= D.subproblems.length ? '人工补充' : '',
        cls: i >= D.subproblems.length ? 'is-manual' : '' });
      flowEdgesDrawn.push({ from: 'n3', to: id });
    });
    if (flowEngineData) {
      (flowEngineData.functions || []).forEach((f, fi) => {
        const fid = 'fn-' + f.id;
        const fy = 120 + fi * 280;
        flowNodes.push({ id: fid, type: 'fn', agent: 'ideator', x: p4.x + 340, y: fy, title: `${f.id} ${f.name}`, sub: '', cls: '' });
        flowEdgesDrawn.push({ from: 'n4', to: fid });
        (flowEngineData.options || []).filter(o => o.function_id === f.id).forEach((o, oi) => {
          const oid = 'opt-' + o.id;
          const dec = state.engineDecisions[o.id];
          flowNodes.push({ id: oid, type: 'opt', agent: 'ideator', x: p4.x + 640, y: fy + 42 + oi * 62,
            title: `[${o.id}] ${o.principle.slice(0, 24)}`, sub: o.evidence_refs.length ? '证据 ' + o.evidence_refs.join(', ') : '',
            cls: dec === 'confirmed' ? 'is-trust' : dec === 'dismissed' ? 'is-doubt' : '' });
          flowEdgesDrawn.push({ from: fid, to: oid });
        });
      });
    }
    D.redteam.forEach((r, i) => {
      const id = 'rt-' + i;
      const v = state.redteam[i];
      flowNodes.push({ id, type: 'rt', agent: 'redteam', x: p5.x - 60 + (i % 2) * 250, y: p5.y + 180 + Math.floor(i / 2) * 84,
        title: r.q.slice(0, 30), sub: r.target,
        cls: v === 'accept' ? 'is-trust' : v === 'reject' ? 'is-doubt' : '' });
      flowEdgesDrawn.push({ from: 'n5', to: id });
    });
    flowNodes.push({ id: 'sum-valid', type: 'sum', agent: 'archivist', x: p7.x, y: p7.y + 190,
      title: `${D.concepts.length} 条路线的验证与停止条件`, sub: state.committed ? '已签署' : '未签署', cls: state.committed ? 'is-trust' : '' });
    flowEdgesDrawn.push({ from: 'n7', to: 'sum-valid' });
  }

  function flowNodeHtml(f) {
    const agent = AGENTS.find(a => a.id === f.agent);
    return `<div class="gd-rc-fnode gd-rc-fnode--${f.type} ${f.cls}" data-fnode="${f.id}" style="left:${f.x}px;top:${f.y}px">
      <div class="gd-rc-fnode-title">${esc(f.title)}</div>
      ${f.sub ? `<div class="gd-rc-fnode-sub">${esc(f.sub)}</div>` : ''}
      <span class="gd-rc-fnode-agent tone-${agent.tone}">${agent.name}</span>
    </div>`;
  }

  function spawnBatch(ids) {
    const html = ids.map(id => flowNodeHtml(flowNodes.find(n => n.id === id))).join('');
    worldEl.insertAdjacentHTML('beforeend', html);
    const fresh = [...worldEl.querySelectorAll('.gd-rc-fnode:not(.is-spawned)')];
    fresh.forEach((el, i) => { el.style.transitionDelay = Math.min(i * 45, 400) + 'ms'; });
    void worldEl.offsetWidth; // 强制 reflow，让弹入过渡生效
    fresh.forEach(el => el.classList.add('is-spawned'));
    drawWires(true);
  }

  function feedLine(agentId, text) {
    const agent = AGENTS.find(a => a.id === agentId);
    const div = document.createElement('div');
    div.className = 'gd-rc-feed-line';
    div.innerHTML = `<span class="gd-rc-fnode-agent tone-${agent.tone}">${agent.name}</span>${esc(text)}`;
    feedEl.appendChild(div);
    feedEl.scrollTop = feedEl.scrollHeight;
  }

  function renderRoster(activeId, doneIds) {
    rosterEl.innerHTML = AGENTS.map(a => {
      const st = a.id === activeId ? '工作中' : (doneIds || []).includes(a.id) ? '已完成' : '待命';
      const cls = a.id === activeId ? 'is-active' : (doneIds || []).includes(a.id) ? 'is-done' : '';
      return `<span class="gd-rc-roster-item tone-${a.tone} ${cls}">${a.human ? '负责人' : 'AI'} · ${a.name}<i>${st}</i></span>`;
    }).join('');
  }

  function updateFlowUI() {
    const runs = state.flow.runs;
    flowBtn.textContent = runs > 0 ? '再次推理' : '开始推理';
    flowHint.textContent = state.flow.dirty
      ? '条件已修改，可再次推理'
      : runs > 0 ? `已完成 ${runs} 轮展开 · 0 次模型调用` : '数字员工按逻辑逐步展开，0 次模型调用';
  }

  function touchFlow() {
    if (state.flow.runs > 0) { S.markFlowDirty(state); save(); updateFlowUI(); }
  }

  /* 生成一轮展开计划：批次 + 当时说话的数字员工 + 会议室日志 */
  function spawnPlan() {
    const doubts = [...D.evidence, ...state.extraEvidence].filter(e => state.evMarks[e.id] !== 'trust').map(e => e.id);
    const manual = state.subproblems.length - D.subproblems.length;
    const accepted = state.redteam.filter(v => v === 'accept').length;
    const plan = [
      { agent: 'scribe', ids: ['sum-intent'], feed: `把意图拆成 ${state.intent.map(g => g.items.length).reduce((a, b) => a + b, 0)} 条事实、需要、假设与待补证` },
      { agent: 'scout', ids: flowNodes.filter(n => n.type === 'ev').map(n => n.id),
        feed: `检索项目库与方法库，沉淀 ${flowNodes.filter(n => n.type === 'ev').length} 条证据${doubts.length ? `；你对 ${doubts.join('、')} 标了存疑` : ''}` },
      { agent: 'coach', ids: flowNodes.filter(n => n.type === 'sp').map(n => n.id),
        feed: `整机拆成 ${state.subproblems.length} 个可独立验证的子问题${manual > 0 ? `，其中 ${manual} 个是你补的` : ''}` }
    ];
    if (flowEngineData) {
      plan.push({ agent: 'ideator', ids: flowNodes.filter(n => n.type === 'fn').map(n => n.id),
        feed: `${flowEngineData.functions.length} 个功能建立功能模型（GD-CRE-0.1 确定性骨架）` });
      plan.push({ agent: 'ideator', ids: flowNodes.filter(n => n.type === 'opt').map(n => n.id),
        feed: `逐功能出选项，共 ${flowEngineData.options.length} 个候选，确认后才会写入痕迹` });
    }
    plan.push({ agent: 'redteam', ids: flowNodes.filter(n => n.type === 'rt').map(n => n.id),
      feed: `提出 ${D.redteam.length} 条质疑，${accepted} 条已被接受写入免责声明` });
    plan.push({ agent: 'you', ids: [], feed: '优先级与取舍由人决定，这一步 AI 不介入' });
    plan.push({ agent: 'archivist', ids: ['sum-valid'], feed: `验证计划与停止条件已登记${state.committed ? '，已签署' : '，等待签署'}` });
    return plan;
  }

  function clearFlowDom() {
    worldEl.querySelectorAll('.gd-rc-fnode').forEach(el => el.remove());
    flowEdgesDrawn = [];
    drawWires();
  }

  async function runFlow() {
    if (flowRunning || isMobileCanvas()) return;
    flowRunning = true;
    flowBtn.disabled = true;
    if (!flowEngineData) {
      try { flowEngineData = (await apiGet(`${RC_API}/engine_candidates`)).result; }
      catch (e) { flowEngineData = null; }
    }
    clearFlowDom();
    buildFlow();
    renderRoster(null, []);
    feedEl.innerHTML = '';
    const round = state.flow.runs + 1;
    feedLine('you', state.flow.dirty || round > 1 ? `条件有改动，第 ${round} 轮脑暴开始` : `第 ${round} 轮脑暴开始`);
    const plan = spawnPlan();
    const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
    const doneIds = [];
    let i = 0;
    const step = () => {
      if (i >= plan.length) {
        const killedList = D.concepts.filter(c => state.killed[c.id]).map(c => c.id);
        const doubts = [...D.evidence].filter(e => state.evMarks[e.id] !== 'trust').map(e => e.id);
        const summary = [
          killedList.length ? `毙掉 ${killedList.join('、')}` : '无毙掉方向',
          doubts.length ? `存疑 ${doubts.join('、')}` : '证据全采信',
          flowEngineData ? '引擎候选已接入' : '引擎候选不可用（降级展开）'
        ].join('；');
        S.recordFlowRun(state, summary);
        save(); updateFlowUI(); renderRoster(null, AGENTS.map(a => a.id));
        flowRunning = false; flowBtn.disabled = false;
        return;
      }
      const p = plan[i];
      renderRoster(p.agent, doneIds);
      feedLine(p.agent, p.feed);
      if (p.ids.length) spawnBatch(p.ids);
      doneIds.push(p.agent);
      i++;
      setTimeout(step, reduced ? 0 : 620);
    };
    step();
  }

  async function restoreFlow() {
    if (!state.flow.runs || isMobileCanvas()) return;
    if (!flowEngineData) {
      try { flowEngineData = (await apiGet(`${RC_API}/engine_candidates`)).result; } catch (e) { flowEngineData = null; }
    }
    buildFlow();
    spawnBatch(flowNodes.map(n => n.id));
    renderRoster(null, AGENTS.map(a => a.id));
    state.flow.log.slice(-3).forEach(r => feedLine('archivist', `第 ${r.run} 轮（${r.time}）：${r.summary}`));
  }

  flowBtn.addEventListener('click', runFlow);

  function esc(s) {
    return String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  }
  function save() { S.save(state); queueRemoteSave(); }
  function render() {
    renderCanvas(); renderDetail();
    detailEl.classList.toggle('is-open', panelOpen || isMobileCanvas());
  }

  /* ============ 画布 ============ */
  function mainNodeHtml(n) {
    const st = state.statuses[n.id];
    const p = posOf(n.id);
    const notes = (state.notes[n.id] || []).length;
    const branchSlots = n.id === 'n4'
      ? '<div class="gd-rc-cnode-outputs">' + D.concepts.map(c =>
          `<div class="gd-rc-out-slot"><span>${c.id} ${esc(c.title.slice(0, 6))}</span><i class="gd-rc-port gd-rc-port--slot" data-out-slot="${c.id}"></i></div>`).join('') + '</div>'
      : '';
    return `<div class="gd-rc-cnode tone-${NODE_TONE[n.id]} is-${st} ${n.id === state.selected ? 'is-selected' : ''}"
        data-node="${n.id}" role="button" tabindex="0" style="left:${p.x}px;top:${p.y}px"
        aria-label="节点${n.num} ${n.title}，状态${S.STATUS_LABEL[st]}">
      <div class="gd-rc-cnode-title"><span>${n.num} · ${n.title}</span><span class="gd-rc-status gd-rc-status--${st}">${S.STATUS_LABEL[st]}</span></div>
      <div class="gd-rc-cnode-body">
        <div class="gd-rc-cnode-row">${esc(n.method)}</div>
        <div class="gd-rc-cnode-row gd-rc-cnode-roles"><span>人：思考</span><span>AI：${n.aiRole}</span></div>
        ${notes ? `<div class="gd-rc-cnode-row gd-rc-cnode-notes">${notes} 条旁注</div>` : ''}
        ${branchSlots}
      </div>
      ${n.id !== 'n1' ? '<i class="gd-rc-port gd-rc-port--in" data-port-in></i>' : ''}
      ${n.id !== 'n7' ? '<i class="gd-rc-port gd-rc-port--out" data-port-out="main"></i>' : ''}
    </div>`;
  }

  function conceptNodeHtml(c) {
    const p = posOf(c.id);
    const k = state.killed[c.id];
    return `<div class="gd-rc-cnode gd-rc-cnode--concept ${k ? 'is-killed' : ''} ${c.id === focusConcept ? 'is-focus' : ''}"
        data-concept="${c.id}" role="button" tabindex="0" style="left:${p.x}px;top:${p.y}px"
        aria-label="概念${c.id} ${esc(c.title)}">
      <div class="gd-rc-cnode-title"><span>${c.id} · ${esc(c.title)}</span></div>
      <div class="gd-rc-cnode-body"><div class="gd-rc-cnode-row">${k ? '已毙，保留备查' : esc(state.priorities[c.id] || c.tag)}</div></div>
      <i class="gd-rc-port gd-rc-port--in" data-port-in></i>
    </div>`;
  }

  function portCenter(el) {
    let x = 0, y = 0, n = el;
    while (n && n !== worldEl) { x += n.offsetLeft; y += n.offsetTop; n = n.offsetParent; }
    return { x: x + el.offsetWidth / 2, y: y + el.offsetHeight / 2 };
  }

  function wirePath(a, b) {
    const dx = Math.max(48, Math.abs(b.x - a.x) / 2);
    return `M ${a.x} ${a.y} C ${a.x + dx} ${a.y}, ${b.x - dx} ${b.y}, ${b.x} ${b.y}`;
  }

  function drawWires(animateFlow) {
    if (isMobileCanvas()) { edgesEl.innerHTML = ''; return; }
    const paths = [];
    const chainWire = (from, to) => {
      const a = worldEl.querySelector(`[data-node="${from}"] [data-port-out="main"]`);
      const b = worldEl.querySelector(`[data-node="${to}"] [data-port-in]`);
      if (!a || !b) return;
      const st = state.statuses[to];
      const cls = `wire wire-${st}` + ((from === state.selected || to === state.selected) ? ' is-hot' : '');
      paths.push(`<path class="${cls}" d="${wirePath(portCenter(a), portCenter(b))}"/>`);
    };
    CHAIN.forEach(([f, t]) => chainWire(f, t));
    BRANCHES.forEach(([f, t]) => {
      const a = worldEl.querySelector(`[data-node="${f}"] [data-out-slot="${t}"]`);
      const b = worldEl.querySelector(`[data-concept="${t}"] [data-port-in]`);
      if (!a || !b) return;
      const cls = 'wire wire-branch' + (state.killed[t] ? ' is-killed' : '') + (f === state.selected || t === focusConcept ? ' is-hot' : '');
      paths.push(`<path class="${cls}" d="${wirePath(portCenter(a), portCenter(b))}"/>`);
    });
    flowEdgesDrawn.forEach(e => {
      const a = flowAnchor(e.from, 'out'), b = flowAnchor(e.to, 'in');
      if (a && b) paths.push(`<path class="wire wire-flow ${e.cls || ''}" d="${wirePath(a, b)}"/>`);
    });
    edgesEl.setAttribute('width', WORLD_W);
    edgesEl.setAttribute('height', WORLD_H);
    edgesEl.innerHTML = paths.join('');
    if (animateFlow) {
      edgesEl.querySelectorAll('.wire-flow:not(.is-doubt)').forEach(p => {
        try {
          const len = p.getTotalLength();
          p.style.strokeDasharray = String(len);
          p.style.strokeDashoffset = String(len);
          requestAnimationFrame(() => { p.classList.add('is-drawing'); p.style.strokeDashoffset = '0'; });
          p.addEventListener('transitionend', () => {
            p.style.strokeDasharray = ''; p.style.strokeDashoffset = ''; p.classList.remove('is-drawing');
          }, { once: true });
        } catch (e) { /* 长度不可算时保持静态 */ }
      });
    }
  }

  function applyView(animate) {
    if (isMobileCanvas()) {
      worldEl.style.transform = '';
      viewportEl.style.backgroundPosition = '';
      return;
    }
    if (animate) {
      worldEl.classList.add('is-animating');
      setTimeout(() => worldEl.classList.remove('is-animating'), 400);
    }
    worldEl.style.transform = `translate(${view.x}px, ${view.y}px) scale(${view.k})`;
    viewportEl.style.backgroundSize = `${24 * view.k}px ${24 * view.k}px`;
    viewportEl.style.backgroundPosition = `${view.x}px ${view.y}px`;
    document.getElementById('rc-zoom-label').textContent = Math.round(view.k * 100) + '%';
  }

  function fitView() {
    if (isMobileCanvas()) return applyView();
    const vw = viewportEl.clientWidth, vh = viewportEl.clientHeight;
    if (!vw || !vh) return;
    view.k = Math.min(vw / WORLD_W, vh / WORLD_H) * 0.9;
    view.x = (vw - WORLD_W * view.k) / 2;
    view.y = (vh - WORLD_H * view.k) / 2;
    applyView(true);
  }

  function renderCanvas() {
    worldEl.querySelectorAll('.gd-rc-cnode').forEach(el => el.remove());
    const html = D.nodes.map(mainNodeHtml).join('') + D.concepts.map(conceptNodeHtml).join('');
    worldEl.insertAdjacentHTML('beforeend', html);
    if (isMobileCanvas()) {
      worldEl.querySelectorAll('.gd-rc-cnode').forEach(el => { el.style.left = ''; el.style.top = ''; });
    }
    drawWires();
  }

  let panelOpen = false;

  function selectNode(id, conceptId) {
    state.selected = id;
    focusConcept = conceptId || null;
    panelOpen = true;
    save(); render();
    const card = worldEl.querySelector(`.gd-rc-cnode[data-node="${id}"]`);
    if (card) { card.classList.remove('is-pulse'); void card.offsetWidth; card.classList.add('is-pulse'); }
    if (focusConcept) {
      const el = detailEl.querySelector(`.gd-rc-concept[data-focus="${CSS.escape(focusConcept)}"]`);
      if (el) el.scrollIntoView({ block: 'nearest' });
    }
  }

  /* 画布交互：拖卡片、拖空白平移、滚轮缩放 */
  (() => {
    let drag = null;
    viewportEl.addEventListener('pointerdown', e => {
      if (isMobileCanvas()) return;
      const card = e.target.closest('.gd-rc-cnode');
      const startX = e.clientX, startY = e.clientY;
      if (card) {
        const id = card.dataset.node || card.dataset.concept;
        const p = posOf(id);
        drag = { kind: 'node', id, card, startX, startY, baseX: p.x, baseY: p.y, moved: false };
      } else {
        drag = { kind: 'pan', startX, startY, baseX: view.x, baseY: view.y, moved: false };
      }
      viewportEl.setPointerCapture(e.pointerId);
      viewportEl.classList.add('is-grabbing');
    });
    viewportEl.addEventListener('pointermove', e => {
      if (!drag) return;
      const dx = (e.clientX - drag.startX) / view.k;
      const dy = (e.clientY - drag.startY) / view.k;
      if (Math.abs(e.clientX - drag.startX) + Math.abs(e.clientY - drag.startY) > 4) drag.moved = true;
      if (!drag.moved) return;
      if (drag.kind === 'node') {
        drag.card.style.left = (drag.baseX + dx) + 'px';
        drag.card.style.top = (drag.baseY + dy) + 'px';
        drawWires();
      } else {
        view.x = drag.baseX + (e.clientX - drag.startX);
        view.y = drag.baseY + (e.clientY - drag.startY);
        applyView();
      }
    });
    viewportEl.addEventListener('pointerup', e => {
      viewportEl.classList.remove('is-grabbing');
      if (!drag) return;
      if (drag.kind === 'node') {
        if (drag.moved) {
          S.setNodePos(state, drag.id, parseFloat(drag.card.style.left), parseFloat(drag.card.style.top));
          save();
        } else {
          const id = drag.id;
          if (drag.card.dataset.node) selectNode(id);
          else selectNode('n4', id);
        }
      } else if (!drag.moved) {
        panelOpen = false; detailEl.classList.remove('is-open');
      }
      drag = null;
    });
    viewportEl.addEventListener('wheel', e => {
      if (isMobileCanvas()) return;
      e.preventDefault();
      const old = view.k;
      const k = Math.min(1.6, Math.max(0.4, old * (e.deltaY < 0 ? 1.08 : 0.92)));
      const rect = viewportEl.getBoundingClientRect();
      const cx = e.clientX - rect.left, cy = e.clientY - rect.top;
      view.x = cx - (cx - view.x) * (k / old);
      view.y = cy - (cy - view.y) * (k / old);
      view.k = k;
      applyView();
    }, { passive: false });
    document.getElementById('rc-zoom-in').addEventListener('click', () => { view.k = Math.min(1.6, view.k * 1.15); applyView(true); });
    document.getElementById('rc-zoom-out').addEventListener('click', () => { view.k = Math.max(0.4, view.k / 1.15); applyView(true); });
    document.getElementById('rc-zoom-reset').addEventListener('click', fitView);
    const feedToggle = document.getElementById('rc-feed-toggle');
    feedToggle.addEventListener('click', () => {
      const wrap = feedToggle.closest('.gd-rc-feedwrap');
      const collapsed = wrap.classList.toggle('is-collapsed');
      feedToggle.setAttribute('aria-expanded', String(!collapsed));
    });
    worldEl.addEventListener('keydown', e => {
      if (e.key !== 'Enter' && e.key !== ' ') return;
      const card = e.target.closest('.gd-rc-cnode');
      if (!card) return;
      e.preventDefault();
      if (card.dataset.node) selectNode(card.dataset.node);
      else selectNode('n4', card.dataset.concept);
    });
    window.addEventListener('resize', () => { applyView(); drawWires(); });
  })();

  /* ============ 详情 ============ */
  function block(kind, title, inner) {
    const label = { human: '人做什么', ai: 'AI 帮什么', trace: '思考痕迹' }[kind];
    return `<section class="gd-rc-block gd-rc-block--${kind}">
      <h3><span class="gd-rc-kind gd-rc-kind--${kind}">${label}</span>${title ? `<span class="gd-rc-kind-note">${esc(title)}</span>` : ''}</h3>
      ${inner}</section>`;
  }

  /* 跨渲染保留的检索与引擎候选 UI 状态（结果不是痕迹，痕迹在 state 里） */
  let searchUI = { domain: 'methods', q: '', results: null, error: '', busy: false };
  let engineUI = { loaded: false, data: null, error: '', busy: false };

  function apiGet(path) {
    return fetch(path).then(r => r.json()).then(j => {
      if (!j.ok) throw Object.assign(new Error(j.error || '服务返回失败'), { code: j.code });
      return j;
    });
  }
  function serviceHint(err) {
    return `检索服务未启动或失败：${err.message}。本机启动：.runtime/pipeline/bin/python3 scripts/reasoning_canvas_server.py`;
  }

  function nodeSpecific(id) {
    if (id === 'n1') {
      return state.intent.map(g => `<div class="gd-rc-igroup">
        <div class="gd-rc-igroup-head"><b>${esc(g.key)}</b></div>
        <ul class="gd-rc-ilist">${g.items.map((it, i) =>
          `<li>${esc(it)}<button class="gd-rc-mini" type="button" data-intent-del="${esc(g.key)}:${i}" aria-label="移除该条目" ${can('intent') ? '' : 'disabled'}>移除</button></li>`).join('')}</ul>
        <div class="gd-rc-iadd"><input data-intent-input="${esc(g.key)}" placeholder="补充一条${esc(g.key)}，未知就写未知" aria-label="补充${esc(g.key)}条目" ${can('intent') ? '' : 'disabled'}><button class="gd-button gd-button--quiet gd-rc-mini-btn" type="button" data-intent-add="${esc(g.key)}" ${can('intent') ? '' : 'disabled'}>添加</button></div>
      </div>`).join('');
    }
    if (id === 'n2') {
      const rows = D.evidence.map(e => {
        const m = state.evMarks[e.id];
        return `<div class="gd-rc-evrow">
          <div><b>[${e.id}] ${esc(e.t)}</b><p>${esc(e.d)}</p></div>
          <div class="gd-rc-evbtns">
            <button class="gd-button gd-rc-mini-btn ${m === 'trust' ? 'gd-button--primary' : ''}" type="button" data-ev="${e.id}" data-m="trust" aria-pressed="${m === 'trust'}" ${can('evidence') ? '' : 'disabled'}>采信</button>
            <button class="gd-button gd-rc-mini-btn ${m === 'doubt' ? 'gd-rc-warn-on' : 'gd-button--quiet'}" type="button" data-ev="${e.id}" data-m="doubt" aria-pressed="${m === 'doubt'}" ${can('evidence') ? '' : 'disabled'}>存疑</button>
          </div></div>`;
      }).join('');
      const extras = state.extraEvidence.map(e => {
        const m = state.evMarks[e.id];
        return `<div class="gd-rc-evrow">
          <div><b>[${esc(e.id)}] ${esc(e.title)}</b> <span class="gd-rc-tag">检索加入</span><p>${esc(e.desc)}</p></div>
          <div class="gd-rc-evbtns">
            <button class="gd-button gd-rc-mini-btn ${m === 'trust' ? 'gd-button--primary' : ''}" type="button" data-ev="${esc(e.id)}" data-m="trust" aria-pressed="${m === 'trust'}" ${can('evidence') ? '' : 'disabled'}>采信</button>
            <button class="gd-button gd-rc-mini-btn ${m === 'doubt' ? 'gd-rc-warn-on' : 'gd-button--quiet'}" type="button" data-ev="${esc(e.id)}" data-m="doubt" aria-pressed="${m === 'doubt'}" ${can('evidence') ? '' : 'disabled'}>存疑</button>
          </div></div>`;
      }).join('');
      const log = state.searchLog.length
        ? '<p class="gd-rc-meta">检索留痕：' + state.searchLog.map(s =>
            `${s.time} ${s.domain === 'methods' ? '方法库' : '项目库'}「${esc(s.query) || '全部'}」命中 ${s.total} 条`).join('；') + '</p>'
        : '';
      return `<div class="gd-rc-search">
          <div class="gd-rc-search-row">
            <select id="rc-search-domain" class="gd-rc-select gd-rc-search-domain" aria-label="检索范围">
              <option value="methods" ${searchUI.domain === 'methods' ? 'selected' : ''}>方法库（64）</option>
              <option value="projects" ${searchUI.domain === 'projects' ? 'selected' : ''}>项目库（560）</option>
            </select>
            <input id="rc-search-q" placeholder="输入检索词，留空为全部" aria-label="检索词" value="${esc(searchUI.q)}">
            <button class="gd-button gd-button--primary gd-rc-mini-btn" id="rc-search-go" type="button">检索</button>
          </div>
          <div id="rc-search-status" class="gd-rc-search-status" role="status">${searchUI.error ? esc(searchUI.error) : ''}</div>
          <div id="rc-search-results"></div>
        </div>
        ${log}${rows}${extras}`;
    }
    if (id === 'n3') {
      return `<div class="gd-rc-sublist">${state.subproblems.map((s, i) =>
        `<div class="gd-rc-subitem"><span>${esc(s)}</span><button class="gd-rc-mini" type="button" data-sub-del="${i}" aria-label="移除该子问题" ${can('subproblem') ? '' : 'disabled'}>移除</button></div>`).join('')}</div>
      <div class="gd-rc-iadd" style="margin-top:14px"><input data-sub-input placeholder="新增一个子问题，写清它可独立验证什么" aria-label="新增子问题" ${can('subproblem') ? '' : 'disabled'}><button class="gd-button gd-button--quiet gd-rc-mini-btn" type="button" data-sub-add ${can('subproblem') ? '' : 'disabled'}>添加</button></div>
      <p class="gd-rc-note-text">${esc(D.subproblemNote)}</p>`;
    }
    if (id === 'n4') {
      const cards = D.concepts.map(c => {
        const k = state.killed[c.id];
        return `<article class="gd-rc-concept ${k ? 'is-killed' : ''} ${c.id === focusConcept ? 'is-focus' : ''}" data-focus="${c.id}">
          <div class="gd-rc-concept-head"><b>${c.id} · ${esc(c.title)}</b><span class="gd-rc-tag ${k ? 'gd-rc-tag--warm' : ''}">${k ? '已毙，保留备查' : esc(state.priorities[c.id] || c.tag)}</span></div>
          <p class="gd-rc-meta">${esc(c.method)}</p>
          <p>${esc(c.design)}</p>
          <button class="gd-button gd-button--quiet gd-rc-mini-btn" type="button" data-kill="${c.id}" ${can('concept') ? '' : 'disabled'}>${k ? '恢复这个方向' : '毙掉（保留痕迹）'}</button>
        </article>`;
      }).join('');
      const confirmed = state.engineConfirmed.length
        ? '<div class="gd-rc-confirmed"><b>已确认写入痕迹的引擎候选</b>' + state.engineConfirmed.map(o =>
            `<div class="gd-rc-confirmed-row">[${esc(o.id)}] ${esc(o.principle)}</div>`).join('') + '</div>'
        : '';
      return cards + `<div class="gd-rc-engine">
        <div class="gd-rc-engine-head"><b>引擎候选 · GD-CRE-0.1 割胶冻结样例</b><span class="gd-rc-tag gd-rc-tag--warm">review_pending，未经确认不写入痕迹</span></div>
        ${confirmed}
        <div class="gd-rc-engine-actions"><button class="gd-button gd-button--quiet gd-rc-mini-btn" id="rc-engine-load" type="button">${engineUI.loaded ? '重新读取候选' : '获取引擎候选'}</button></div>
        <div id="rc-engine-status" class="gd-rc-search-status" role="status">${engineUI.error ? esc(engineUI.error) : ''}</div>
        <div id="rc-engine-list"></div>
      </div>`;
    }
    if (id === 'n5') {
      return D.redteam.map((r, i) => {
        const v = state.redteam[i];
        const label = v === 'accept' ? '已接受，写入免责声明' : v === 'reject' ? '已驳回' : '待你裁决';
        return `<div class="gd-rc-rt">
          <p class="gd-rc-meta">${esc(r.target)}</p>
          <p>${esc(r.q)}</p>
          <div class="gd-rc-rt-row">
            <span class="gd-rc-rt-state gd-rc-rt-state--${v || 'none'}">${label}</span>
            <button class="gd-button gd-rc-mini-btn" type="button" data-rt="${i}" data-v="accept" ${can('evidence') ? '' : 'disabled'}>接受</button>
            <button class="gd-button gd-button--quiet gd-rc-mini-btn" type="button" data-rt="${i}" data-v="reject" ${can('evidence') ? '' : 'disabled'}>驳回</button>
          </div>
          ${v === 'reject' ? `<textarea class="gd-rc-reason" data-rt-reason="${i}" placeholder="驳回须填写理由" ${can('evidence') ? '' : 'disabled'}>${esc(state.redteamReasons[i] || '')}</textarea>` : ''}
        </div>`;
      }).join('');
    }
    if (id === 'n6') {
      return D.concepts.map(c => `<div class="gd-rc-pri">
          <label for="rc-pri-${c.id}"><b>${c.id} · ${esc(c.title)}</b></label>
          <select id="rc-pri-${c.id}" class="gd-rc-select" data-pri="${c.id}" ${can('priority') ? '' : 'disabled'}>
            ${D.priorityOptions.map(o => `<option ${state.priorities[c.id] === o ? 'selected' : ''}>${o}</option>`).join('')}
          </select></div>`).join('') +
        `<label class="gd-rc-label" for="rc-reason">取舍理由（写给未来的自己）</label>
        <textarea class="gd-rc-reason" id="rc-reason" placeholder="例如：D 是门槛，因为测量误差大于农艺余量时，后面所有自动化都不成立。" ${can('reason') ? '' : 'disabled'}>${esc(state.reasons.main || '')}</textarea>`;
    }
    if (id === 'n7') {
      return D.concepts.map(c => `<div class="gd-rc-teststop">
          <b>${c.id} · ${esc(c.title)}</b>
          <p>验证：${esc(c.test)}</p>
          <p class="gd-rc-stopline">放弃条件：${esc(c.stop)}</p>
        </div>`).join('') +
        `<label class="gd-rc-commit"><input type="checkbox" id="rc-commit" ${state.committed ? 'checked' : ''} ${can('commit') ? '' : 'disabled'}>
          <span><b>我承诺按上面的放弃条件执行</b><small>勾选后，这轮推理才算定稿。未来的你看到停止条件触发时，不许找借口。</small></span></label>`;
    }
    return '';
  }

  /* ============ 检索与引擎候选（RC-03/05/06） ============ */
  function renderSearchResults() {
    const box = document.getElementById('rc-search-results');
    if (!box) return;
    if (!searchUI.results) { box.innerHTML = ''; return; }
    const { domain, result } = searchUI.results;
    box.innerHTML = result.data.map((it, i) => {
      const id = domain === 'methods' ? (it.research_id || it.method_id) : it.id;
      const desc = it.summary || it.unit || '';
      return `<div class="gd-rc-hit"><div><b>[${esc(id)}] ${esc(it.name || '')}</b><p>${esc(desc)}</p></div>
        <button class="gd-button gd-button--quiet gd-rc-mini-btn" type="button" data-add-ev="${i}">加入证据池</button></div>`;
    }).join('') || '<p class="gd-rc-empty">没有命中。</p>';
    box.querySelectorAll('[data-add-ev]').forEach(b => b.addEventListener('click', () => {
      const it = searchUI.results.result.data[+b.dataset.addEv];
      const dm = searchUI.results.domain;
      S.addEvidenceFromSearch(state, {
        id: dm === 'methods' ? (it.research_id || it.method_id) : it.id,
        title: it.name || '',
        desc: it.summary || it.unit || '',
        origin: dm === 'methods' ? '方法库检索' : '项目库检索'
      });
      touchFlow(); save(); render();
    }));
  }

  function renderEngineList() {
    const box = document.getElementById('rc-engine-list');
    if (!box || !engineUI.data) return;
    const fns = engineUI.data.functions || [];
    box.innerHTML = `<p class="gd-rc-meta">run ${esc(engineUI.data.run_id)} · 模式 ${esc(engineUI.data.mode)} · 状态 ${esc(engineUI.data.status)} · pack 指纹 ${esc((engineUI.data.pack_sha256 || '').slice(0, 12))}…</p>` +
      fns.map(f => {
        const opts = (engineUI.data.options || []).filter(o => o.function_id === f.id);
        if (!opts.length) return '';
        return `<div class="gd-rc-efunc"><b>${esc(f.id)} ${esc(f.name)}</b>${opts.map(o => {
          const dec = state.engineDecisions[o.id];
          return `<div class="gd-rc-eopt ${dec === 'confirmed' ? 'is-confirmed' : dec === 'dismissed' ? 'is-dismissed' : ''}">
            <span>[${esc(o.id)}] ${esc(o.principle)}${o.evidence_refs.length ? ` <small>证据 ${o.evidence_refs.map(esc).join(', ')}</small>` : ''}</span>
            <span class="gd-rc-eopt-btns">
              ${dec === 'confirmed' ? '<span class="gd-rc-tag">已写入痕迹</span>' : ''}
              ${dec === 'dismissed' ? '<span class="gd-rc-tag gd-rc-tag--warm">暂不采用</span>' : ''}
              <button class="gd-rc-mini" type="button" data-eng="${esc(o.id)}" data-dec="confirmed" ${can('concept') ? '' : 'disabled'}>确认写入</button>
              <button class="gd-rc-mini" type="button" data-eng="${esc(o.id)}" data-dec="dismissed" ${can('concept') ? '' : 'disabled'}>暂不</button>
            </span></div>`;
        }).join('')}</div>`;
      }).join('');
    box.querySelectorAll('[data-eng]').forEach(b => b.addEventListener('click', () => {
      const opt = engineUI.data.options.find(o => o.id === b.dataset.eng);
      S.setEngineDecision(state, opt, b.dataset.dec); touchFlow(); save(); render();
    }));
  }

  function renderDetail() {
    const n = D.nodes.find(x => x.id === state.selected);
    const st = state.statuses[n.id];
    const notes = state.notes[n.id] || [];
    let toolbar = '';
    if (can('status') && st === 'done') toolbar = `<button class="gd-button gd-button--quiet gd-rc-mini-btn" type="button" data-act="reopen">重新打开（后续节点将标为待复核）</button>`;
    if (can('status') && (st === 'doing' || st === 'todo')) toolbar = `<button class="gd-button gd-button--primary gd-rc-mini-btn" type="button" data-act="finalize">这一步想好了，定稿</button>`;
    if (can('status') && st === 'review') toolbar = `<button class="gd-button gd-button--primary gd-rc-mini-btn" type="button" data-act="confirm">复核过，仍然成立</button><button class="gd-button gd-button--quiet gd-rc-mini-btn" type="button" data-act="reopen">重新修改</button>`;

    detailEl.innerHTML = `
      <div class="gd-rc-detail-inner">
        <button class="gd-rc-mini gd-rc-detail-close" id="rc-detail-close" type="button" aria-label="收起详情">收起</button>
        <div class="gd-rc-detail-head">
          <span class="gd-kicker">节点 ${n.num} · ${S.STATUS_LABEL[st]}</span>
          <h2>${n.title}</h2>
          <p class="gd-rc-meta">${esc(n.method)}</p>
          <div class="gd-rc-toolbar">${toolbar}</div>
        </div>
        ${block('human', '', `<p>${esc(n.human)}</p>`)}
        ${block('ai', 'AI 在这一步是' + n.aiRole, `<p>${esc(n.ai)}</p>`)}
        ${block('trace', '', nodeSpecific(n.id))}
        <section class="gd-rc-block">
          <h3><span class="gd-rc-kind gd-rc-kind--note">旁注</span><span class="gd-rc-kind-note">自己、顾问、专家的意见挂在这一步旁边</span></h3>
          <div>${notes.length ? notes.map(m =>
            `<div class="gd-rc-note ${m.who !== '我' ? 'gd-rc-note--other' : ''}"><small>${esc(m.who)} · ${esc(m.time)}</small><p>${esc(m.text)}</p></div>`).join('')
            : '<p class="gd-rc-empty">还没有旁注。</p>'}</div>
          <div class="gd-rc-noteadd">
            <select id="rc-note-who" class="gd-rc-select gd-rc-note-who" aria-label="旁注身份">${D.noteRoles.map(r => `<option ${r === ROLE_NOTE_WHO[currentRole] ? 'selected' : ''}>${r}</option>`).join('')}</select>
            <input id="rc-note-text" placeholder="在这一步写下想法或意见" aria-label="旁注内容">
            <button class="gd-button gd-button--primary gd-rc-mini-btn" id="rc-note-add" type="button">添加</button>
          </div>
        </section>
      </div>`;

    detailEl.querySelectorAll('[data-act]').forEach(b => b.addEventListener('click', () => {
      const act = b.dataset.act;
      if (act === 'reopen') S.reopen(state, n.id);
      if (act === 'finalize') S.finalize(state, n.id);
      if (act === 'confirm') S.confirmReview(state, n.id);
      save(); render();
    }));
    document.getElementById('rc-detail-close').addEventListener('click', () => {
      panelOpen = false; detailEl.classList.remove('is-open');
    });
    detailEl.querySelectorAll('[data-ev]').forEach(b => b.addEventListener('click', () => {
      S.setEvidence(state, b.dataset.ev, b.dataset.m); touchFlow(); save(); render();
    }));
    detailEl.querySelectorAll('[data-kill]').forEach(b => b.addEventListener('click', () => {
      S.toggleKill(state, b.dataset.kill); touchFlow(); save(); render();
    }));
    detailEl.querySelectorAll('[data-rt]').forEach(b => b.addEventListener('click', () => {
      S.setRedteam(state, +b.dataset.rt, b.dataset.v); save(); render();
    }));
    detailEl.querySelectorAll('[data-rt-reason]').forEach(t => t.addEventListener('input', () => {
      S.setRedteam(state, +t.dataset.rtReason, 'reject', t.value); save();
    }));
    detailEl.querySelectorAll('[data-pri]').forEach(s => s.addEventListener('change', () => {
      S.setPriority(state, s.dataset.pri, s.value); save(); renderCanvas();
    }));
    detailEl.querySelectorAll('[data-intent-add]').forEach(b => b.addEventListener('click', () => {
      const input = detailEl.querySelector(`[data-intent-input="${b.dataset.intentAdd}"]`);
      S.intentAdd(state, b.dataset.intentAdd, input.value); touchFlow(); save(); render();
    }));
    detailEl.querySelectorAll('[data-intent-del]').forEach(b => b.addEventListener('click', () => {
      const [k, i] = b.dataset.intentDel.split(':');
      S.intentRemove(state, k, +i); touchFlow(); save(); render();
    }));
    const subAdd = detailEl.querySelector('[data-sub-add]');
    if (subAdd) subAdd.addEventListener('click', () => {
      const input = detailEl.querySelector('[data-sub-input]');
      S.subproblemAdd(state, input.value); touchFlow(); save(); render();
    });
    detailEl.querySelectorAll('[data-sub-del]').forEach(b => b.addEventListener('click', () => {
      S.subproblemRemove(state, +b.dataset.subDel); touchFlow(); save(); render();
    }));
    const searchGo = document.getElementById('rc-search-go');
    if (searchGo) {
      renderSearchResults();
      searchGo.addEventListener('click', () => {
        const domain = document.getElementById('rc-search-domain').value;
        const q = document.getElementById('rc-search-q').value.trim();
        searchUI = { domain, q, results: null, error: '', busy: true };
        const status = document.getElementById('rc-search-status');
        status.textContent = '检索中…';
        apiGet(`${RC_API}/search_${domain === 'methods' ? 'methods' : 'projects'}?q=${encodeURIComponent(q)}`)
          .then(j => {
            searchUI.busy = false; searchUI.results = { domain, result: j.result };
            S.logSearch(state, domain, q, j.result.total); save(); renderCanvas();
            status.textContent = `命中 ${j.result.total} 条（${domain === 'methods' ? '方法库 64 目录' : '项目库 560 目录'}）`;
            renderSearchResults();
          })
          .catch(err => {
            searchUI.busy = false; searchUI.error = serviceHint(err);
            status.textContent = searchUI.error;
          });
      });
    }
    const engLoad = document.getElementById('rc-engine-load');
    if (engLoad) {
      renderEngineList();
      engLoad.addEventListener('click', () => {
        const status = document.getElementById('rc-engine-status');
        status.textContent = '读取冻结样例…';
        apiGet(`${RC_API}/engine_candidates`)
          .then(j => { engineUI = { loaded: true, data: j.result, error: '', busy: false }; status.textContent = ''; renderEngineList(); })
          .catch(err => { engineUI = { loaded: false, data: null, error: serviceHint(err), busy: false }; status.textContent = engineUI.error; });
      });
    }
    const reason = document.getElementById('rc-reason');
    if (reason) reason.addEventListener('input', () => { S.setReason(state, reason.value); save(); });
    const commit = document.getElementById('rc-commit');
    if (commit) commit.addEventListener('change', () => { S.setCommitted(state, commit.checked); save(); });
    const noteAdd = document.getElementById('rc-note-add');
    if (noteAdd) noteAdd.addEventListener('click', () => {
      const t = document.getElementById('rc-note-text').value.trim();
      if (!t) return;
      S.addNote(state, n.id, document.getElementById('rc-note-who').value, t);
      save(); render();
    });
  }

  /* ============ 顶部动作 ============ */
  document.getElementById('rc-save').addEventListener('click', () => {
    setWorkspaceStatus('正在保存…', 'warn');
    clearTimeout(remoteTimer);
    persistRemote();
  });
  document.getElementById('rc-gdrp').addEventListener('click', () => {
    setWorkspaceStatus('正在生成研究包…', 'warn');
    apiGet(`${RC_API}/gdrp?workspace_id=${encodeURIComponent(WORKSPACE_ID)}`)
      .then(j => {
        const name = `${j.result.research_pack.package_id}.research-pack.json`;
        const blob = new Blob([JSON.stringify(j.result.research_pack, null, 2)], { type: 'application/json;charset=utf-8' });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = name;
        a.click();
        URL.revokeObjectURL(a.href);
        setWorkspaceStatus(`研究包已导出 · r${j.result.revision}`, 'ok');
      })
      .catch(err => setWorkspaceStatus(`研究包失败：${err.message}`, 'warn'));
  });
  document.getElementById('rc-report').addEventListener('click', () => {
    setWorkspaceStatus('正在生成报告…', 'warn');
    apiGet(`${RC_API}/gdrp_package?workspace_id=${encodeURIComponent(WORKSPACE_ID)}`)
      .then(j => {
        const name = `${j.result.research_pack.package_id}.report.html`;
        const blob = new Blob([j.result.report_html], { type: 'text/html;charset=utf-8' });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = name;
        a.click();
        URL.revokeObjectURL(a.href);
        setWorkspaceStatus(`报告已导出 · r${j.result.revision}`, 'ok');
      })
      .catch(err => setWorkspaceStatus(`报告失败：${err.message}`, 'warn'));
  });
  document.getElementById('rc-export').addEventListener('click', () => {
    const blob = new Blob([S.exportMarkdown(state)], { type: 'text/markdown;charset=utf-8' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = '割胶机器人-推理档案.md';
    a.click();
    URL.revokeObjectURL(a.href);
  });
  document.getElementById('rc-reset').addEventListener('click', () => {
    if (!confirm('重置会清空所有裁决、毙掉记录、旁注与承诺，回到初始状态。确定吗？')) return;
    state = S.reset(); render();
  });

  render();
  fitView();
  updateFlowUI();
  restoreFlow();
  restoreWorkspace();
})();
