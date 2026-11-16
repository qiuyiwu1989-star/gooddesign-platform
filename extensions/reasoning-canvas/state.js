/* 推理画布状态模块：状态结构、持久化与全部状态变更动作。
   视图层（reasoning-canvas.js）不直接改状态，只调用这里的动作。 */
window.RC_State = (() => {
  const LS_KEY = 'gd-reasoning-canvas-v1';
  const HANDOFF_KEY = 'gd-reasoning-canvas-handoff-v1';
  const WORKSPACE_PREFIX = 'gd-reasoning-canvas-workspace-v1:';
  const DEMO_WORKSPACE_ID = 'rubber-tapping-demo';
  const HANDOFF_SCHEMA = 'gooddesign-canvas-handoff-1.0';
  const PACKET_SCHEMA = 'gooddesign-research-packet-1.0';
  const ROUTE_LABELS = { measure: '先验证问题与量测', functions: '拆解功能与接口', concepts: '组合机制与候选概念' };
  const RESEARCH_GROUPS = ['用户陈述', '需要', '约束', '待补证'];
  const ORDER = () => RC_DATA.nodes.map(n => n.id);
  const STATUS_LABEL = { todo: '待开始', doing: '进行中', done: '已定稿', review: '待复核' };

  function HandoffError(message) {
    this.name = 'HandoffError';
    this.message = '交接导入失败：' + message;
    if (Error.captureStackTrace) Error.captureStackTrace(this, HandoffError);
  }
  HandoffError.prototype = Object.create(Error.prototype);
  HandoffError.prototype.constructor = HandoffError;

  function isObject(value) { return !!value && typeof value === 'object' && !Array.isArray(value); }
  function isResearch(state) { return !!state && isObject(state.workspace) && state.workspace.kind === 'needs-research'; }
  function workspaceKey(id) { return WORKSPACE_PREFIX + id; }
  function routeLabel(route) { return route ? ROUTE_LABELS[route] : '暂未确定'; }
  function packetRoute(packet) {
    if (packet.route === null) return null;
    if (typeof packet.route === 'string') return packet.route;
    return isObject(packet.route) ? packet.route.id : undefined;
  }

  function defaultState() {
    return {
      selected: 'n1',
      statuses: { n1: 'done', n2: 'done', n3: 'done', n4: 'doing', n5: 'todo', n6: 'todo', n7: 'todo' },
      evMarks: Object.fromEntries(RC_DATA.evidence.map(e => [e.id, e.mark])),
      killed: {},
      redteam: RC_DATA.redteam.map(r => r.def),
      redteamReasons: RC_DATA.redteam.map(() => ''),
      priorities: Object.fromEntries(RC_DATA.concepts.map(c => [c.id, c.tag])),
      reasons: {},
      notes: {},
      committed: false,
      intent: RC_DATA.intentGroups.map(g => ({ key: g.key, items: g.items.slice() })),
      subproblems: RC_DATA.subproblems.slice(),
      searchLog: [],
      extraEvidence: [],
      engineDecisions: {},
      engineConfirmed: [],
      positions: {},
      flow: { runs: 0, log: [], dirty: false }
    };
  }

  function validatePacket(packet) {
    if (!isObject(packet)) throw new HandoffError('研究任务包必须是对象');
    if (packet.schema !== PACKET_SCHEMA) throw new HandoffError('研究任务包 schema 必须为 ' + PACKET_SCHEMA);
    if (packet.status !== 'prepared_context_not_executed') throw new HandoffError('研究任务包必须处于未执行状态');
    if (!isObject(packet.requirement)) throw new HandoffError('研究任务包缺少 requirement 对象');
    const requirement = packet.requirement;
    if (typeof requirement.problem !== 'string' || !requirement.problem.trim()) throw new HandoffError('problem 必填且不能为空');
    if (requirement.title !== undefined && typeof requirement.title !== 'string') throw new HandoffError('研究标题必须是字符串');
    for (const key of ['outcome', 'constraints']) {
      if (requirement[key] !== undefined && requirement[key] !== null && typeof requirement[key] !== 'string') {
        throw new HandoffError('requirement.' + key + ' 必须是字符串或 null');
      }
    }
    if (requirement.status !== 'research_proposed_not_customer_confirmed') throw new HandoffError('需求不得标记为客户已确认');
    if (!Number.isInteger(requirement.revision) || requirement.revision < 1) throw new HandoffError('需求 revision 必须是正整数');
    const route = packetRoute(packet);
    if (packet.route !== null && !(typeof route === 'string' && Object.hasOwn(ROUTE_LABELS, route))) {
      throw new HandoffError('route 只能为 null、measure、functions 或 concepts');
    }
    if (!Array.isArray(packet.project_references) || !packet.project_references.every(isObject)) throw new HandoffError('project_references 必须是对象数组');
    packet.project_references.forEach(ref => {
      if (typeof ref.id !== 'string' || !ref.id || typeof ref.name !== 'string' || !ref.name) throw new HandoffError('参考项目必须包含 id 和 name');
      if (ref.relation !== 'reference_not_adoption_proof') throw new HandoffError('参考项目只能作为线索，不能作为采用证明');
    });
    if (!Array.isArray(packet.method_references) || !packet.method_references.every(x => typeof x === 'string' && !!x)) throw new HandoffError('method_references 必须是字符串数组');
    if (!Array.isArray(packet.unknowns) || !packet.unknowns.every(x => typeof x === 'string' && !!x.trim())) throw new HandoffError('unknowns 必须是非空字符串数组');
    if (!Array.isArray(packet.pending_clarifications) || !packet.pending_clarifications.every(isObject)) throw new HandoffError('pending_clarifications 必须是对象数组');
    packet.pending_clarifications.forEach(item => {
      if (!['field', 'value', 'actor'].every(key => typeof item[key] === 'string' && !!item[key].trim())) throw new HandoffError('待确认补充必须包含 field、value 和 actor');
      if (item.status !== 'pending_confirmation') throw new HandoffError('补充记录必须保持待确认状态');
    });
    if (packet.model_calls !== 0) throw new HandoffError('model_calls 必须为 0');
    for (const key of ['source_projects_modified', 'engineering_validated', 'expert_reviewed']) {
      if (packet[key] !== false) throw new HandoffError(key + ' 必须为 false');
    }
    return packet;
  }

  function validateHandoff(envelope) {
    if (!isObject(envelope)) throw new HandoffError('envelope 必须是对象');
    if (envelope.schema !== HANDOFF_SCHEMA) throw new HandoffError('envelope schema 必须为 ' + HANDOFF_SCHEMA);
    if (typeof envelope.task_id !== 'string' || !/^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$/.test(envelope.task_id)) throw new HandoffError('task_id 必填且格式非法');
    if (typeof envelope.created_at !== 'string' || !/^\d{4}-\d{2}-\d{2}T/.test(envelope.created_at) || !Number.isFinite(Date.parse(envelope.created_at))) {
      throw new HandoffError('created_at 必须是有效日期时间');
    }
    validatePacket(envelope.packet);
    return envelope;
  }

  function parseHandoff(raw) {
    let envelope;
    try { envelope = JSON.parse(raw); } catch (e) { throw new HandoffError('JSON 格式非法'); }
    return validateHandoff(envelope);
  }

  function researchState(envelope) {
    validateHandoff(envelope);
    const packet = envelope.packet;
    const requirement = packet.requirement;
    const problem = requirement.problem.trim();
    const title = (requirement.title || '').trim() || problem.slice(0, 60);
    const unknowns = packet.unknowns.slice();
    packet.pending_clarifications.forEach(item => unknowns.push(`${item.field}：${item.value}（提供者：${item.actor}，待确认）`));
    return {
      workspace: {
        id: envelope.task_id,
        kind: 'needs-research',
        title,
        problem,
        route: packetRoute(packet),
        createdAt: envelope.created_at,
        sourcePacket: JSON.parse(JSON.stringify(packet))
      },
      selected: 'n1',
      statuses: { n1: 'doing', n2: 'todo', n3: 'todo', n4: 'todo', n5: 'todo', n6: 'todo', n7: 'todo' },
      evMarks: {},
      killed: {},
      redteam: [],
      redteamReasons: [],
      priorities: {},
      reasons: {},
      notes: {},
      committed: false,
      intent: [
        { key: '用户陈述', items: [problem] },
        { key: '需要', items: requirement.outcome && requirement.outcome.trim() ? [requirement.outcome.trim()] : [] },
        { key: '约束', items: requirement.constraints && requirement.constraints.trim() ? [requirement.constraints.trim()] : [] },
        { key: '待补证', items: unknowns }
      ],
      subproblems: [],
      searchLog: [],
      extraEvidence: [],
      engineDecisions: {},
      engineConfirmed: [],
      positions: {},
      flow: { runs: 0, log: [], dirty: false }
    };
  }

  function normalizeResearchState(saved, id) {
    if (!isObject(saved) || !isObject(saved.workspace) || saved.workspace.kind !== 'needs-research' || saved.workspace.id !== id) {
      throw new Error('工作区加载失败：本地数据身份不匹配');
    }
    let base;
    try {
      base = researchState({ schema: HANDOFF_SCHEMA, task_id: id, created_at: saved.workspace.createdAt, packet: saved.workspace.sourcePacket });
    } catch (e) {
      throw new Error('工作区加载失败：' + e.message);
    }
    const merged = Object.assign(base, saved, { workspace: base.workspace });
    merged.statuses = Object.assign(base.statuses, isObject(saved.statuses) ? saved.statuses : {});
    ORDER().forEach(nodeId => {
      if (!Object.hasOwn(STATUS_LABEL, merged.statuses[nodeId])) merged.statuses[nodeId] = nodeId === 'n1' ? 'doing' : 'todo';
    });
    merged.intent = RESEARCH_GROUPS.map(key => {
      const group = Array.isArray(saved.intent) ? saved.intent.find(g => isObject(g) && g.key === key) : null;
      return { key, items: group && Array.isArray(group.items) ? group.items.filter(x => typeof x === 'string') : [] };
    });
    for (const key of ['subproblems', 'searchLog', 'extraEvidence']) {
      merged[key] = Array.isArray(saved[key]) ? saved[key] : [];
    }
    for (const key of ['evMarks', 'reasons', 'notes', 'positions']) {
      merged[key] = isObject(saved[key]) ? saved[key] : {};
    }
    merged.killed = {};
    merged.redteam = [];
    merged.redteamReasons = [];
    merged.priorities = {};
    merged.engineDecisions = {};
    merged.engineConfirmed = [];
    merged.flow = { runs: 0, log: [], dirty: false };
    merged.committed = !!saved.committed;
    return merged;
  }

  function load() {
    try {
      const raw = localStorage.getItem(LS_KEY);
      if (!raw) return defaultState();
      const s = JSON.parse(raw);
      if (!isObject(s)) return defaultState();
      const d = defaultState();
      return Object.assign(d, s, {
        statuses: Object.assign(d.statuses, s.statuses || {}),
        evMarks: Object.assign(d.evMarks, s.evMarks || {}),
        priorities: Object.assign(d.priorities, s.priorities || {})
      });
    } catch (e) { return defaultState(); }
  }

  function loadResearch(id) {
    if (!/^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$/.test(id || '')) throw new Error('工作区加载失败：workspace 参数非法');
    let raw;
    try { raw = localStorage.getItem(workspaceKey(id)); } catch (e) { throw new Error('工作区加载失败：无法读取本地存储'); }
    if (!raw) throw new Error('工作区加载失败：本地任务不存在，请从需求研究重新交接');
    let saved;
    try { saved = JSON.parse(raw); } catch (e) { throw new Error('工作区加载失败：本地 JSON 格式非法'); }
    return normalizeResearchState(saved, id);
  }

  function save(state) {
    const key = isResearch(state) ? workspaceKey(state.workspace.id) : LS_KEY;
    try { localStorage.setItem(key, JSON.stringify(state)); return true; } catch (e) { return false; }
  }

  function boot() {
    const params = new URLSearchParams(location.search);
    if (params.has('workspace')) {
      const id = params.get('workspace') || '';
      try { return { state: loadResearch(id), workspaceId: id, hasLocal: true, fromUrl: true }; }
      catch (e) { return { error: e.message }; }
    }
    let raw;
    try { raw = localStorage.getItem(HANDOFF_KEY); } catch (e) { return { error: '交接导入失败：无法读取同源 localStorage' }; }
    if (raw !== null) {
      try {
        const state = researchState(parseHandoff(raw));
        const persisted = save(state);
        let consumed = false;
        if (persisted) {
          try { localStorage.removeItem(HANDOFF_KEY); consumed = true; } catch (e) {}
        }
        return {
          state,
          workspaceId: state.workspace.id,
          imported: true,
          hasLocal: persisted,
          warning: persisted ? (consumed ? '' : '任务已保存，但交接键无法移除；当前 URL 会避免重复导入。') : '任务已在内存中打开，但本地保存失败，请先导出档案并检查浏览器存储权限。'
        };
      } catch (e) { return { error: e.message }; }
    }
    let hasLocal = false;
    try { hasLocal = localStorage.getItem(LS_KEY) !== null; } catch (e) {}
    return { state: load(), workspaceId: DEMO_WORKSPACE_ID, hasLocal };
  }

  function reset(state) {
    const key = isResearch(state) ? workspaceKey(state.workspace.id) : LS_KEY;
    try { localStorage.removeItem(key); } catch (e) {}
    return defaultState();
  }

  function reopen(state, id) {
    state.statuses[id] = 'doing';
    const idx = ORDER().indexOf(id);
    ORDER().slice(idx + 1).forEach(k => { if (state.statuses[k] === 'done') state.statuses[k] = 'review'; });
  }
  function finalize(state, id) { state.statuses[id] = 'done'; }
  function confirmReview(state, id) { if (state.statuses[id] === 'review') state.statuses[id] = 'done'; }
  function setEvidence(state, id, mark) { state.evMarks[id] = mark; }
  function toggleKill(state, id) { state.killed[id] = !state.killed[id]; }
  function setRedteam(state, idx, verdict, reason) {
    state.redteam[idx] = verdict;
    if (reason !== undefined) state.redteamReasons[idx] = reason;
  }
  function setPriority(state, id, value) { state.priorities[id] = value; }
  function setReason(state, text) { state.reasons.main = text; }
  function setCommitted(state, value) { state.committed = !!value; }
  function addNote(state, nodeId, who, text) {
    const time = new Date().toLocaleString('zh-CN', { month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    (state.notes[nodeId] = state.notes[nodeId] || []).push({ who, text, time });
  }
  function intentAdd(state, groupKey, text) {
    const g = state.intent.find(x => x.key === groupKey);
    if (g && text.trim()) g.items.push(text.trim());
  }
  function intentRemove(state, groupKey, index) {
    const g = state.intent.find(x => x.key === groupKey);
    if (g) g.items.splice(index, 1);
  }
  function subproblemAdd(state, text) { if (text.trim()) state.subproblems.push(text.trim()); }
  function subproblemRemove(state, index) { state.subproblems.splice(index, 1); }
  function logSearch(state, domain, query, total) {
    const time = new Date().toLocaleString('zh-CN', { month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    state.searchLog.push({ domain, query, total, time });
  }
  function addEvidenceFromSearch(state, item) {
    if (state.extraEvidence.some(e => e.id === item.id)) return;
    state.extraEvidence.push(item);
    state.evMarks[item.id] = 'doubt';
  }
  function setEngineDecision(state, option, decision) {
    state.engineDecisions[option.id] = decision;
    state.engineConfirmed = state.engineConfirmed.filter(o => o.id !== option.id);
    if (decision === 'confirmed') state.engineConfirmed.push(option);
  }
  function setNodePos(state, id, x, y) { state.positions[id] = { x: Math.round(x), y: Math.round(y) }; }
  function markFlowDirty(state) { if (state.flow.runs > 0) state.flow.dirty = true; }
  function recordFlowRun(state, summary) {
    state.flow.runs += 1;
    state.flow.dirty = false;
    const time = new Date().toLocaleString('zh-CN', { month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    state.flow.log.push({ run: state.flow.runs, time, summary });
  }

  function exportResearchMarkdown(state) {
    const workspace = state.workspace;
    const packet = workspace.sourcePacket;
    const L = [
      '# 推理档案 · ' + workspace.title,
      '',
      '导出时间：' + new Date().toLocaleString('zh-CN'),
      '任务 ID：' + workspace.id,
      '研究路线：' + routeLabel(workspace.route),
      '边界：用户陈述与参考线索尚未成为事实、客户确认需求、专家结论或工程验证；0 次模型调用。',
      ''
    ];
    RC_DATA.researchNodes.forEach(n => {
      L.push(`## ${n.num}. ${n.title}（${STATUS_LABEL[state.statuses[n.id]]}）`);
      L.push(`- 人做什么：${n.human}`);
      L.push(`- 辅助说明：${n.ai}`);
      if (n.id === 'n1') state.intent.forEach(g => {
        if (g.items.length) g.items.forEach(i => L.push(`- [${g.key}] ${i}`));
        else L.push(`- [${g.key}] 暂无`);
      });
      if (n.id === 'n2') {
        if (packet.project_references.length) packet.project_references.forEach(ref => L.push(`- 参考项目线索[${ref.id}] ${ref.name}：未作为证据或采用证明`));
        else L.push('- 参考项目线索：暂无');
        if (packet.method_references.length) L.push('- 参考方法线索：' + packet.method_references.join('、') + '（未执行）');
        else L.push('- 参考方法线索：暂无');
        state.extraEvidence.forEach(e => L.push(`- 检索加入[${e.id}] ${e.title}：${state.evMarks[e.id] === 'trust' ? '采信' : '存疑'}`));
        state.searchLog.forEach(s => L.push(`- 检索留痕：${s.time} 在${s.domain === 'methods' ? '方法库' : '项目库'}检索「${s.query || '(全部)'}」，命中 ${s.total} 条`));
      }
      if (n.id === 'n3') {
        if (state.subproblems.length) state.subproblems.forEach(s => L.push(`- 子问题：${s}`));
        else L.push('- 子问题：暂无，等待人工拆解');
      }
      if (n.id === 'n4') L.push('- 概念：暂无；通用概念生成与冻结引擎候选未接入');
      if (n.id === 'n5') L.push('- 质疑记录：暂无；未执行自动红队');
      if (n.id === 'n6') L.push('- 取舍理由：' + (state.reasons.main || '暂无'));
      if (n.id === 'n7') L.push('- 承诺：' + (state.committed ? '已签署先核对验证条件再行动' : '未签署'));
      (state.notes[n.id] || []).forEach(m => L.push(`- 旁注[${m.who} ${m.time}]：${m.text}`));
      L.push('');
    });
    return L.join('\n');
  }

  function exportMarkdown(state) {
    if (isResearch(state)) return exportResearchMarkdown(state);
    const L = ['# 推理档案 · 割胶机器人创新推理', '', '导出时间：' + new Date().toLocaleString('zh-CN'), ''];
    RC_DATA.nodes.forEach(n => {
      L.push(`## ${n.num}. ${n.title}（${STATUS_LABEL[state.statuses[n.id]]}）`);
      L.push(`- 人做什么：${n.human}`);
      L.push(`- AI 角色：${n.aiRole}，${n.ai}`);
      if (n.id === 'n1') state.intent.forEach(g => g.items.forEach(i => L.push(`- [${g.key}] ${i}`)));
      if (n.id === 'n2') {
        L.push('- 证据裁决：' + RC_DATA.evidence.map(e => `[${e.id}]${state.evMarks[e.id] === 'trust' ? '采信' : '存疑'}`).join('，'));
        state.extraEvidence.forEach(e => L.push(`- 检索加入[${e.id}] ${e.title}：${state.evMarks[e.id] === 'trust' ? '采信' : '存疑'}`));
        state.searchLog.forEach(s => L.push(`- 检索留痕：${s.time} 在${s.domain === 'methods' ? '方法库' : '项目库'}检索「${s.query || '(全部)'}」，命中 ${s.total} 条`));
      }
      if (n.id === 'n3') state.subproblems.forEach(s => L.push(`- 子问题：${s}`));
      if (n.id === 'n4') {
        RC_DATA.concepts.forEach(c => L.push(`- ${c.id} ${c.title}：${state.killed[c.id] ? '已毙（保留备查）' : (state.priorities[c.id] || c.tag)}`));
        state.engineConfirmed.forEach(o => L.push(`- 引擎候选已确认[${o.id}] ${o.principle}`));
      }
      if (n.id === 'n5') RC_DATA.redteam.forEach((r, i) => {
        const v = state.redteam[i];
        L.push(`- 红队（${r.target}）：${v === 'accept' ? '接受' : v === 'reject' ? '驳回：' + (state.redteamReasons[i] || '未填理由') : '未裁决'}`);
      });
      if (n.id === 'n6' && state.reasons.main) L.push('- 取舍理由：' + state.reasons.main);
      if (n.id === 'n7') L.push('- 承诺：' + (state.committed ? '已签署按放弃条件执行' : '未签署'));
      (state.notes[n.id] || []).forEach(m => L.push(`- 旁注[${m.who} ${m.time}]：${m.text}`));
      L.push('');
    });
    if (state.flow && state.flow.log.length) {
      L.push('## 推理运行记录');
      state.flow.log.forEach(r => L.push(`- 第 ${r.run} 轮（${r.time}）：${r.summary}`));
      L.push('');
    }
    return L.join('\n');
  }

  return {
    LS_KEY, HANDOFF_KEY, WORKSPACE_PREFIX, DEMO_WORKSPACE_ID,
    HANDOFF_SCHEMA, PACKET_SCHEMA, STATUS_LABEL, ORDER,
    HandoffError, isResearch, workspaceKey, routeLabel,
    defaultState, validatePacket, validateHandoff, parseHandoff, researchState,
    normalizeResearchState, load, loadResearch, save, boot, reset,
    reopen, finalize, confirmReview,
    setEvidence, toggleKill, setRedteam, setPriority, setReason, setCommitted,
    addNote, intentAdd, intentRemove, subproblemAdd, subproblemRemove,
    logSearch, addEvidenceFromSearch, setEngineDecision, setNodePos,
    markFlowDirty, recordFlowRun, exportMarkdown
  };
})();
