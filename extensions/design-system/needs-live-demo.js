(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]));
  const stages = ['拆解问题', '规划检索', '阅读证据', '交叉核对', '形成结论'];
  const dossier = '/inno/dossier/?project=2019-s19';
  const events = [
    { stage: 0, title: '读取演示问题', detail: '目标：从高功率工业泵改造出发，识别值得验证的机制，不直接复制设备参数。' },
    { stage: 0, title: '拆成三个研究问题', detail: '动力传动如何改变？低速重载如何承载？排量与压力如何控制？' },
    { stage: 1, title: '制定检索计划', detail: '查找宏华HH6000的结构、基本参数和现场记录，优先论文与可定位原文。' },
    { stage: 1, title: '确定核对口径', detail: '将历史申报、论文实验、媒体引述和后续产业化分开，不合并不同组态的等效台数。' },
    { stage: 2, title: '阅读《新型大功率电动压裂泵组的研制》', detail: '定位额定输入功率4500 kW，保留卧式五缸单作用柱塞泵和论文参数范围。', evidence: { title: '2017论文 · 基本参数', quote: '新型压裂泵组设计为卧式五缸单作用柱塞泵，额定输入功率4 500 kW', locator: 'S7e3f4f2b06f63fe8 / B0003', url: dossier + '#record-MET-001' } },
    { stage: 2, title: '核对直驱与承载结构', detail: '电机直驱取消中间机械变速机构；双端斜齿轮与六支撑曲轴共同处理承载和周期振动。', evidence: { title: '2017论文 · 结构设计', quote: '将动力机 (电机) 与执行机构 (压裂泵) 纳入一体化设计，打破了常规压裂泵车柴油机加传动箱的传动结构形式，取消了中间机械变速传动机构', locator: 'S7e3f4f2b06f63fe8 / B0004', url: dossier + '#record-INNO-001' } },
    { stage: 2, title: '核对长宁H9现场记录', detail: '两台泵组分别累计132.2h与107.2h，施工压力70~85 MPa，保留原文时间与工况。', evidence: { title: '2017论文 · 现场应用', quote: '作业施工压力70~85 MPa。在此期间，1号电动压裂泵组累计运行132.2 h (66段)，2号电动泵组累计运行107.2h (48段)', locator: 'S7e3f4f2b06f63fe8 / B0006', url: dossier + '#record-VAL-002' } },
    { stage: 3, title: '比较三种等效口径', detail: '单台等效3台、6台等效18台来自论文不同组态；8台等效20台以上来自媒体，不能合并成统一比例。', evidence: { title: '环球网 · 媒体引述', quote: '8台6000马力压裂泵至少等同于20台以上传统柴油机压裂设备的性能。', locator: 'S8ae50c84687b0709 / B0001', url: dossier + '#record-MET-020' } },
    { stage: 3, title: '标记证据缺口', detail: '9项专利只有申报总数；成本缺原始测算表；现场缺逐段日志和测量不确定度。' },
    { stage: 3, title: '形成机制组合判断', detail: '直驱不是简单换电机，结构、承载和控制需要共同验证。这只是演示中的研究解释，不是新增工程结论。' },
    { stage: 4, title: '生成研究结论草案', detail: '优先验证电机直驱与变频控制、双端承载结构、网电条件下的控制精度，不预设普遍节能率。' },
    { stage: 4, title: '列出下一步验证', detail: '取得原始施工日志、专利清单和成本测算表，再由领域人员确认适用工况。', report: ['电机直驱、双端斜齿轮、六支撑曲轴和中压变频控制应作为组合机制研究。', '现有资料支持继续研究，不支持直接复制参数、统一等效比例或普遍节能承诺。', '下一步先补原始施工日志、专利清单和成本测算，再由领域人员确认适用边界。'] }
  ];
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  let index = 0;
  let timer = null;
  let running = false;
  let finished = false;

  function renderStages(active) {
    document.querySelectorAll('[data-live-stage]').forEach(item => {
      const stage = Number(item.dataset.liveStage);
      item.classList.toggle('is-done', stage < active || (finished && stage === active));
      item.classList.toggle('is-active', stage === active && !finished);
      if (stage === active && !finished) item.setAttribute('aria-current', 'step');
      else item.removeAttribute('aria-current');
    });
  }

  function addEvidence(evidence) {
    if (!evidence || document.querySelector(`[data-evidence="${esc(evidence.locator)}"]`)) return;
    const empty = $('live-evidence').querySelector('.gd-live-empty');
    if (empty) empty.remove();
    $('live-evidence').insertAdjacentHTML('beforeend', `<article class="gd-live-source" data-evidence="${esc(evidence.locator)}"><span>${esc(evidence.title)}</span><blockquote>${esc(evidence.quote)}</blockquote><small>${esc(evidence.locator)}</small><a href="${esc(evidence.url)}">在项目档案中核对</a></article>`);
  }

  function addReport(items) {
    if (!items) return;
    $('live-report').innerHTML = `<article class="gd-live-report"><span>研究结论草案 · 模拟整理</span><h3>哪些机制值得继续验证？</h3><ul>${items.map(item => `<li>${esc(item)}</li>`).join('')}</ul><p>待领域复核 · 非工程结论</p><a href="${dossier}">查看6000HP项目完整档案</a></article>`;
  }

  function renderOne() {
    const event = events[index];
    finished = false;
    renderStages(event.stage);
    $('live-current-label').textContent = `${stages[event.stage]} · 动作 ${index + 1}/${events.length}`;
    $('live-current-title').textContent = event.title;
    $('live-current-detail').textContent = event.detail;
    $('live-log').insertAdjacentHTML('beforeend', `<li><span>${String(index + 1).padStart(2, '0')}</span><div><strong>${esc(event.title)}</strong><p>${esc(event.detail)}</p></div></li>`);
    $('live-log').scrollTop = $('live-log').scrollHeight;
    addEvidence(event.evidence);
    index += 1;
    $('live-progress').value = index;
    $('live-count').textContent = `${index} / ${events.length} 项动作`;
    $('live-state').textContent = running ? '正在演示' : '已暂停';
    if (index === events.length) addReport(events[index - 1].report);
  }

  function complete() {
    running = false;
    finished = true;
    clearTimeout(timer);
    $('live-demo').setAttribute('aria-busy', 'false');
    $('live-pause').textContent = '已完成';
    $('live-pause').disabled = true;
    $('live-state').textContent = '演示完成';
    $('live-current-label').textContent = '动态案例已播放完毕';
    renderStages(stages.length - 1);
  }

  function schedule(delay = 1200) {
    clearTimeout(timer);
    if (!running) return;
    timer = setTimeout(() => {
      renderOne();
      if (index >= events.length) complete();
      else schedule();
    }, delay);
  }

  function resetContent() {
    clearTimeout(timer);
    index = 0;
    finished = false;
    $('live-log').replaceChildren();
    $('live-evidence').innerHTML = '<p class="gd-live-empty">阅读到的原文会在这里保留，可以跳回项目档案核对。</p>';
    $('live-report').replaceChildren();
    $('live-progress').value = 0;
    $('live-count').textContent = `0 / ${events.length} 项动作`;
    $('live-pause').disabled = false;
    $('live-pause').textContent = '暂停';
    $('live-demo').setAttribute('aria-busy', 'true');
  }

  function play() {
    resetContent();
    running = true;
    if (reduced.matches) {
      while (index < events.length) renderOne();
      complete();
      return;
    }
    $('live-state').textContent = '正在演示';
    schedule(250);
  }

  $('live-demo-start').addEventListener('click', () => {
    $('live-demo').hidden = false;
    $('live-demo-start').disabled = true;
    play();
    $('live-demo').scrollIntoView({ behavior: reduced.matches ? 'instant' : 'smooth', block: 'start' });
  });
  $('live-pause').addEventListener('click', () => {
    if (finished) return;
    if (running) {
      running = false;
      clearTimeout(timer);
      $('live-demo').setAttribute('aria-busy', 'false');
      $('live-pause').textContent = '继续';
      $('live-state').textContent = '已暂停';
      $('live-current-label').textContent = '演示已暂停，当前研究动作已保留';
    } else {
      running = true;
      $('live-demo').setAttribute('aria-busy', 'true');
      $('live-pause').textContent = '暂停';
      $('live-state').textContent = '正在演示';
      schedule(350);
    }
  });
  $('live-replay').addEventListener('click', play);
  $('live-close').addEventListener('click', () => {
    running = false;
    clearTimeout(timer);
    $('live-demo').setAttribute('aria-busy', 'false');
    $('live-demo').hidden = true;
    $('live-demo-start').disabled = false;
    $('live-demo-start').focus();
  });
  addEventListener('pagehide', () => clearTimeout(timer));
})();
