/* 推理画布状态模块：状态结构、持久化与全部状态变更动作。
   视图层（reasoning-canvas.js）不直接改状态，只调用这里的动作。 */
window.RC_State = (() => {
  const LS_KEY = 'gd-reasoning-canvas-v1';
  const ORDER = () => RC_DATA.nodes.map(n => n.id);
  const STATUS_LABEL = { todo: '待开始', doing: '进行中', done: '已定稿', review: '待复核' };

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

  function load() {
    try {
      const raw = localStorage.getItem(LS_KEY);
      if (!raw) return defaultState();
      const s = JSON.parse(raw);
      const d = defaultState();
      // 合并缺省字段，容忍旧版本状态
      return Object.assign(d, s, {
        statuses: Object.assign(d.statuses, s.statuses || {}),
        evMarks: Object.assign(d.evMarks, s.evMarks || {}),
        priorities: Object.assign(d.priorities, s.priorities || {})
      });
    } catch (e) { return defaultState(); }
  }

  function save(state) {
    try { localStorage.setItem(LS_KEY, JSON.stringify(state)); } catch (e) { /* 隐私模式下静默降级 */ }
  }

  function reset() { try { localStorage.removeItem(LS_KEY); } catch (e) {} return defaultState(); }

  /* 状态机：重开节点时，下游已定稿节点转为待复核 */
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
    state.extraEvidence.push(item); // {id, title, desc, origin}，默认以存疑身份进入
    state.evMarks[item.id] = 'doubt';
  }
  function setEngineDecision(state, option, decision) {
    state.engineDecisions[option.id] = decision; // confirmed | dismissed
    state.engineConfirmed = state.engineConfirmed.filter(o => o.id !== option.id);
    if (decision === 'confirmed') state.engineConfirmed.push(option);
  }
  function setNodePos(state, id, x, y) {
    state.positions[id] = { x: Math.round(x), y: Math.round(y) };
  }

  /* 流程引擎：记录每一轮推理的条件快照；条件修改置脏 */
  function markFlowDirty(state) {
    if (state.flow.runs > 0) state.flow.dirty = true;
  }
  function recordFlowRun(state, summary) {
    state.flow.runs += 1;
    state.flow.dirty = false;
    const time = new Date().toLocaleString('zh-CN', { month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    state.flow.log.push({ run: state.flow.runs, time, summary });
  }

  function exportMarkdown(state) {
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
    STATUS_LABEL, ORDER, defaultState, load, save, reset,
    reopen, finalize, confirmReview,
    setEvidence, toggleKill, setRedteam, setPriority, setReason, setCommitted,
    addNote, intentAdd, intentRemove, subproblemAdd, subproblemRemove,
    logSearch, addEvidenceFromSearch, setEngineDecision, setNodePos,
    markFlowDirty, recordFlowRun,
    exportMarkdown
  };
})();
