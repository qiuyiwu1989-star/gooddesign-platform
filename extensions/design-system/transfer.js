(() => {
  const $ = id => document.getElementById(id);
  const data = window.PLAY_DATA.migrate;
  const state = { project: data.exhibits[0].slug, mechanism: data.exhibits[0].tags[0], industry: data.industries[0].key };
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function currentProject() { return data.exhibits.find(item => item.slug === state.project); }
  function currentIndustry() { return data.industries.find(item => item.key === state.industry); }
  function setStep(number) {
    [1, 2, 3].forEach(step => {
      const section = $(`transfer-step-${step}`);
      section.hidden = step > number;
      document.querySelector(`[data-step="${step}"]`).setAttribute('aria-current', step === number ? 'step' : 'false');
    });
  }
  function renderProjects() {
    $('transfer-project').innerHTML = data.exhibits.map(project => `<button type="button" data-value="${project.slug}" aria-pressed="${project.slug === state.project}">${project.name}<small>${project.tags.join(' · ')}</small></button>`).join('');
    $('transfer-project').querySelectorAll('button').forEach(button => button.addEventListener('click', () => {
      state.project = button.dataset.value;
      state.mechanism = currentProject().tags[0];
      renderProjects();
      renderMechanisms();
      setStep(1);
    }));
  }
  function renderMechanisms() {
    $('transfer-mechanism').innerHTML = currentProject().tags.map(tag => `<button type="button" data-value="${tag}" aria-pressed="${tag === state.mechanism}">${tag}</button>`).join('');
    $('transfer-mechanism').querySelectorAll('button').forEach(button => button.addEventListener('click', () => {
      state.mechanism = button.dataset.value;
      renderMechanisms();
      renderIndustries();
      setStep(2);
    }));
  }
  function renderIndustries() {
    $('transfer-industry').innerHTML = data.industries.map(industry => `<button type="button" data-value="${industry.key}" aria-pressed="${industry.key === state.industry}">${industry.name}<small>${industry.hint}</small></button>`).join('');
    $('transfer-industry').querySelectorAll('button').forEach(button => button.addEventListener('click', () => {
      state.industry = button.dataset.value;
      renderIndustries();
    }));
  }
  function researchText() {
    const project = currentProject();
    const industry = currentIndustry();
    const direct = (data.map[state.mechanism] || []).includes(state.industry);
    const problem = $('transfer-problem').value.trim();
    return `好设计馆 · 迁移研究上下文\n\n真实项目：${project.name}\n可借鉴机制：${state.mechanism}\n目标产业：${industry.name}\n真实问题：${problem}\n\n迁移判断：${direct ? '可以形成一个小范围验证假设，但不能把原项目参数直接复制到目标产品。' : '当前只有方法启发，尚不能建立直接迁移结论。'}\n\n必须保留的差异与未知：\n1. 原项目的工况、载荷、环境和安全边界是否与目标场景一致，尚未确认。\n2. 目标产品的结构、成本、用户、制造和维护条件，需要重新定义。\n3. 当前匹配不是工程证明，也不代表客户或专家已经认可。\n\n建议验证：\n1. 明确目标产品的基线、约束、可测量指标与停止条件。\n2. 只做最小验证样机或实验，记录有效、无效和异常。\n3. 由目标领域人员复核结果，再决定是否进入下一轮研究。\n`;
  }
  function review() {
    const problem = $('transfer-problem').value.trim();
    if (!problem) {
      $('transfer-status').textContent = '请先填写一个真实问题，再形成迁移映射。';
      $('transfer-problem').focus();
      return;
    }
    $('transfer-status').textContent = '';
    const project = currentProject();
    const industry = currentIndustry();
    const direct = (data.map[state.mechanism] || []).includes(state.industry);
    $('transfer-map').innerHTML = `<div class="ia-mapping"><div class="ia-mapping-side"><p class="ia-eyebrow">项目证据</p><h3>${project.name}</h3><p>机制：${state.mechanism}</p><a href="/dossier/?project=${project.slug}">查看项目证据</a></div><div class="ia-mapping-connector" aria-hidden="true">⇄</div><div class="ia-mapping-side"><p class="ia-eyebrow">目标问题</p><h3>${industry.name}</h3><p>${problem.replace(/[&<>"']/g, character => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[character]))}</p></div></div><p class="ia-mapping-note"><strong>${direct ? '可形成小范围验证假设' : '目前仅保留方法启发'}</strong><br>${direct ? '可以讨论机制如何回应目标问题，但不能直接复制原项目的参数、结构或工程结论。' : '现有映射不足以支持直接迁移。需要补充目标场景和原项目条件的对应证据。'}</p><div class="ia-mapping"><div class="ia-mapping-side"><h3>差异与未知</h3><ul><li>工况、载荷、环境和安全边界尚未对应</li><li>目标产品的用户、成本、制造和维护条件需要重定义</li><li>没有目标场景的原型或试验证据</li></ul></div><div class="ia-mapping-connector" aria-hidden="true">·</div><div class="ia-mapping-side"><h3>验证计划</h3><ol><li>明确基线、指标与停止条件</li><li>开展最小样机或实验并记录异常</li><li>由目标领域人员复核后决定下一步</li></ol></div></div>`;
    setStep(3);
  }
  function copyContext() {
    const text = researchText();
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(() => {
        $('transfer-status').textContent = '研究上下文已复制，可粘贴到需求研究。';
      }).catch(() => window.prompt('复制研究上下文：', text));
    } else {
      window.prompt('复制研究上下文：', text);
    }
  }
  function exportAndOpen() {
    const url = URL.createObjectURL(new Blob([researchText()], { type: 'text/plain;charset=utf-8' }));
    const link = document.createElement('a');
    link.href = url;
    link.download = '迁移研究-验证计划.txt';
    link.click();
    URL.revokeObjectURL(url);
    window.open('/needs/', '_blank', 'noopener');
  }

  $('transfer-review').addEventListener('click', review);
  $('transfer-copy').addEventListener('click', copyContext);
  $('transfer-export').addEventListener('click', exportAndOpen);
  renderProjects();
  renderMechanisms();
  renderIndustries();
  setStep(1);
})();
