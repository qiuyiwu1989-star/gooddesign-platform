(() => {
  const $ = id => document.getElementById(id);
  const NS = 'http://www.w3.org/2000/svg';
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const layers = [
    { y: 120, h: 34, fill: '#C9A06B', name: '松软表层' },
    { y: 154, h: 30, fill: '#B08D5C', name: '细颗粒层' },
    { y: 184, h: 40, fill: '#96744A', rock: true },
    { y: 224, h: 36, fill: '#7E5F3C', name: '致密层' },
    { y: 260, h: 44, fill: '#6A4F30', name: '基岩层' }
  ];
  const storageKey = 'gd-lab-runs-v1';
  let drill;
  let hit = 1;
  let state = 'ready';
  let elapsed = 0;
  let startedAt = 0;
  let raf = 0;
  let runs = [];
  try { runs = JSON.parse(localStorage.getItem(storageKey) || '[]').slice(0, 2); } catch (_) { runs = []; }

  function element(tag, attrs, parent) {
    const node = document.createElementNS(NS, tag);
    Object.entries(attrs).forEach(([key, value]) => node.setAttribute(key, value));
    if (parent) parent.appendChild(node);
    return node;
  }
  function buildScene() {
    const svg = $('lab-scene');
    svg.innerHTML = '';
    element('rect', { width: 420, height: 340, fill: '#F6F7FA' }, svg);
    const title = element('text', { x: 210, y: 28, 'text-anchor': 'middle', 'font-size': 12.5, fill: '#8A8F98' }, svg);
    title.textContent = '模拟月壤剖面（含未知岩块）';
    layers.forEach(layer => {
      element('rect', { x: 70, y: layer.y, width: 280, height: layer.h, fill: layer.fill, rx: 3 }, svg);
      if (layer.rock) {
        element('circle', { cx: 228, cy: layer.y + layer.h * .62, r: 15, fill: '#57452E' }, svg);
        element('circle', { cx: 160, cy: layer.y + layer.h * .32, r: 9, fill: '#5E4A30' }, svg);
      }
    });
    drill = element('g', { transform: 'translate(210,56)' }, svg);
    drill.innerHTML = '<rect x="-7" y="-74" width="14" height="74" fill="#B9BECB" rx="3"/><path d="M-15 0 L-12 -26 L-7 -26 L-7 -60 L7 -60 L7 -26 L12 -26 L15 0 Z" fill="#B08936"/><path d="M-12 -26 L-7 -26 L-7 -60 L7 -60 L7 -26 L12 -26" stroke="#fff" stroke-width="2" fill="none" opacity="0.6"/><circle cx="0" cy="-42" r="3.5" fill="#4F58C0"/>';
  }
  function evaluate(rpm, feed, impact, ok) {
    let core = 92 - Math.abs(rpm - 180) * .18 - Math.max(0, feed - 8) * 1.8 + (impact === 1 ? 5 : impact === 2 ? -4 : -8);
    let risk = 24 + Math.abs(feed - 8) * 2.8 + Math.abs(rpm - 180) * .12 + (impact === 2 ? 18 : impact === 0 ? 22 : 0);
    let energy = 30 + rpm * .12 + feed * 1.4 + impact * 18;
    if (ok === false) { core -= 26; risk += 24; }
    return {
      core: Math.max(12, Math.min(98, Math.round(core))),
      risk: Math.max(8, Math.min(98, Math.round(risk))),
      energy: Math.max(18, Math.min(98, Math.round(energy)))
    };
  }
  function parameters() {
    return { rpm: Number($('lab-rpm').value), feed: Number($('lab-feed').value), impact: hit };
  }
  function strategy(metrics) {
    if (metrics.risk > 70) return '当前策略风险偏高：下压、冲击或转速过激，可能提高卡钻和机构冲击风险。';
    if (metrics.energy > 76) return '当前策略能耗压力偏高：适合短时破岩，但不适合长时间无人任务。';
    if (metrics.core < 60) return '当前策略样芯完整度不足：取回材料可能破碎或层序信息受损。';
    return '当前策略需要在样芯质量、能耗和设备风险之间继续权衡。';
  }
  function updateControls() {
    const { rpm, feed, impact } = parameters();
    $('lab-rpm-value').textContent = `${rpm} rpm`;
    $('lab-feed-value').textContent = `${feed} mm/s`;
    const metrics = evaluate(rpm, feed, impact, true);
    $('lab-core').textContent = `${metrics.core}%`;
    $('lab-risk').textContent = `${metrics.risk}%`;
    $('lab-energy').textContent = `${metrics.energy}%`;
    $('lab-strategy').textContent = strategy(metrics);
  }
  function setProgress(value) {
    $('lab-progress').style.transform = `scaleX(${value})`;
  }
  function setDrill(progress, jammed) {
    const y = 56 + 258 * progress;
    drill.setAttribute('transform', `translate(210,${y})${jammed ? ' rotate(12)' : ''}`);
  }
  function saveRuns() {
    try { localStorage.setItem(storageKey, JSON.stringify(runs)); } catch (_) {}
  }
  function renderRuns() {
    $('lab-export').disabled = runs.length === 0;
    if (!runs.length) {
      $('lab-runs').innerHTML = '<p class="ia-empty">完成一次钻进后，这里会保留结果。再完成一次，就能比较两种策略。</p>';
      return;
    }
    $('lab-runs').innerHTML = runs.map((run, index) => `<article class="ia-run"><strong>${index === 0 ? '最近实验' : '上一次实验'}<small>${run.ok ? '完成取样' : '卡钻中断'}</small></strong><span><small>样芯完整</small>${run.metrics.core}%</span><span><small>设备风险</small>${run.metrics.risk}%</span><span><small>能耗压力</small>${run.metrics.energy}%</span><em>${run.rpm} rpm · ${run.feed} mm/s · ${['低', '中', '高'][run.impact]}冲击<br>${run.review}</em></article>`).join('');
  }
  function finish(ok) {
    state = 'finished';
    const { rpm, feed, impact } = parameters();
    const metrics = evaluate(rpm, feed, impact, ok);
    const review = ok ? '完成取样，但仍需检查参数与验证条件。' : '岩块导致中断，需要重新调整冲击与进给。';
    runs.unshift({ rpm, feed, impact, ok, metrics, review, at: new Date().toISOString() });
    runs = runs.slice(0, 2);
    saveRuns();
    renderRuns();
    $('lab-status').textContent = ok ? '任务完成：取得模拟样芯' : '任务中断：发生卡钻';
    $('lab-start').textContent = '再做一次';
    $('lab-start').disabled = false;
    $('lab-pause').disabled = true;
    $('lab-review').scrollIntoView({ behavior: reduced ? 'auto' : 'smooth', block: 'nearest' });
  }
  function frame(now) {
    if (state !== 'running') return;
    const current = elapsed + now - startedAt;
    const duration = 2600;
    const progress = Math.min(1, current / duration);
    const canBreak = hit === 2 || (hit === 1 && Number($('lab-feed').value) <= 12) || (hit === 0 && Number($('lab-feed').value) <= 4);
    const jammed = progress >= .55 && progress < .72 && !canBreak;
    setProgress(progress);
    setDrill(jammed ? .55 : progress, jammed);
    if (jammed) {
      finish(false);
      return;
    }
    $('lab-status').textContent = progress >= .72 ? '保层序取芯中：软袋包覆样芯' : progress >= .55 ? '岩块层：正在破岩' : '表层钻进：排屑与进给协同';
    if (progress >= 1) finish(true);
    else raf = requestAnimationFrame(frame);
  }
  function start() {
    if (state === 'running') return;
    if (state === 'paused') {
      state = 'running';
      startedAt = performance.now();
      raf = requestAnimationFrame(frame);
    } else {
      elapsed = 0;
      setProgress(0);
      setDrill(0, false);
      if (reduced) {
        const canBreak = hit === 2 || (hit === 1 && Number($('lab-feed').value) <= 12) || (hit === 0 && Number($('lab-feed').value) <= 4);
        finish(canBreak);
        return;
      }
      state = 'running';
      startedAt = performance.now();
      raf = requestAnimationFrame(frame);
    }
    $('lab-start').textContent = '钻进中';
    $('lab-start').disabled = true;
    $('lab-pause').disabled = false;
    $('lab-pause').textContent = '暂停';
  }
  function pause() {
    if (state !== 'running') return;
    elapsed += performance.now() - startedAt;
    cancelAnimationFrame(raf);
    state = 'paused';
    $('lab-status').textContent = '已暂停，可继续观察当前剖面';
    $('lab-start').disabled = false;
    $('lab-start').textContent = '继续';
    $('lab-pause').textContent = '已暂停';
  }
  function reset() {
    cancelAnimationFrame(raf);
    state = 'ready';
    elapsed = 0;
    setProgress(0);
    setDrill(0, false);
    $('lab-status').textContent = '准备就绪';
    $('lab-start').disabled = false;
    $('lab-start').textContent = '开始钻进';
    $('lab-pause').disabled = true;
    $('lab-pause').textContent = '暂停';
  }
  function exportCard() {
    if (!runs.length) return;
    const lines = ['好设计馆 · 极限实验室观察卡', '', '教学模拟，结果不代表工程精确或实际验证。', ''];
    runs.forEach((run, index) => {
      lines.push(`${index === 0 ? '最近实验' : '上一次实验'}：${run.ok ? '完成取样' : '卡钻中断'}`);
      lines.push(`参数：${run.rpm} rpm，${run.feed} mm/s，${['低', '中', '高'][run.impact]}冲击`);
      lines.push(`结果：样芯完整 ${run.metrics.core}%，设备风险 ${run.metrics.risk}%，能耗压力 ${run.metrics.energy}%`);
      lines.push(`复盘：${run.review}`, '');
    });
    if (runs.length === 2) lines.push('比较提示：观察两组参数如何改变样芯、风险和能耗，不把模拟结果当作工程最优解。');
    const url = URL.createObjectURL(new Blob([lines.join('\n')], { type: 'text/plain;charset=utf-8' }));
    const link = document.createElement('a');
    link.href = url;
    link.download = '极限实验室-设计观察卡.txt';
    link.click();
    URL.revokeObjectURL(url);
  }

  $('lab-rpm').addEventListener('input', updateControls);
  $('lab-feed').addEventListener('input', updateControls);
  $('lab-hit').querySelectorAll('button').forEach(button => button.addEventListener('click', () => {
    hit = Number(button.dataset.value);
    $('lab-hit').querySelectorAll('button').forEach(item => item.setAttribute('aria-pressed', String(item === button)));
    updateControls();
  }));
  $('lab-start').addEventListener('click', start);
  $('lab-pause').addEventListener('click', pause);
  $('lab-reset').addEventListener('click', reset);
  $('lab-export').addEventListener('click', exportCard);
  buildScene();
  updateControls();
  renderRuns();
})();
