(() => {
  const $ = id => document.getElementById(id);
  const quests = window.PLAY_DATA.quest;
  const storageKey = 'gd-quest-progress-v1';
  let completed = [];
  try { completed = JSON.parse(localStorage.getItem(storageKey) || '[]'); } catch (_) {}
  let currentIndex = 0;
  let questionIndex = 0;
  let answered = false;

  function save() {
    try { localStorage.setItem(storageKey, JSON.stringify(completed)); } catch (_) {}
  }
  function unlockedCount() {
    let count = 1;
    while (count < quests.length && completed.includes(quests[count - 1].slug)) count += 1;
    return count;
  }
  function renderProgress() {
    $('quest-progress').textContent = `已解锁 ${unlockedCount()} / 8 · 已完成 ${completed.length} / 8`;
  }
  function renderMap() {
    const unlocked = unlockedCount();
    $('quest-map').innerHTML = quests.map((quest, index) => {
      const allowed = index < unlocked;
      const done = completed.includes(quest.slug);
      return `<button class="ia-quest-card" type="button" data-index="${index}" ${allowed ? '' : 'disabled'} aria-current="${index === currentIndex}"><img src="/inno/legacy/${quest.image}" alt="" loading="lazy"><strong>${quest.name}</strong><small>${done ? '已完成' : allowed ? `第 ${index + 1} 关` : '待解锁'}</small></button>`;
    }).join('');
    $('quest-map').querySelectorAll('button:not(:disabled)').forEach(button => button.addEventListener('click', () => select(Number(button.dataset.index))));
  }
  function select(index) {
    currentIndex = index;
    questionIndex = 0;
    answered = false;
    renderMap();
    renderClue();
  }
  function renderClue() {
    const quest = quests[currentIndex];
    $('quest-current').innerHTML = `<img src="/inno/legacy/${quest.image}" alt="${quest.name}"><h2>${quest.name}</h2><p class="ia-clue">先观察这个项目的任务与结构，再完成两个设计判断。答错也会看到对应资料解释，不需要反复猜测。</p><div class="ia-quest-actions"><a href="/museum/x-ray?slug=${quest.slug}">先看拆解线索</a><button class="ia-primary" id="quest-begin" type="button">开始第 1 问</button></div>`;
    $('quest-begin').addEventListener('click', renderQuestion);
  }
  function renderQuestion() {
    const quest = quests[currentIndex];
    const question = quest.questions[questionIndex];
    answered = false;
    $('quest-current').innerHTML = `<p class="ia-eyebrow">第 ${currentIndex + 1} 关 · 第 ${questionIndex + 1} / 2 问</p><h3>${question.q}</h3><div class="ia-quest-options">${question.options.map((option, index) => `<button type="button" data-index="${index}" aria-pressed="false">${option}</button>`).join('')}</div><div id="quest-feedback" hidden></div>`;
    $('quest-current').querySelectorAll('.ia-quest-options button').forEach(button => button.addEventListener('click', () => answer(Number(button.dataset.index))));
  }
  function answer(index) {
    if (answered) return;
    answered = true;
    const quest = quests[currentIndex];
    const question = quest.questions[questionIndex];
    $('quest-current').querySelectorAll('.ia-quest-options button').forEach(button => {
      button.disabled = true;
      button.setAttribute('aria-pressed', String(Number(button.dataset.index) === index));
    });
    const feedback = document.createElement('div');
    feedback.className = 'ia-quest-feedback';
    feedback.innerHTML = `<strong>${index === question.answer ? '这个判断抓住了关键。' : '这也是一个值得排除的方向。'}</strong><p>${question.explain}</p><div class="ia-quest-actions"><a href="/dossier/?project=${quest.slug}">查看项目证据</a><button class="ia-primary" id="quest-next" type="button">${questionIndex === 0 ? '进入第 2 问' : '完成本关'}</button></div>`;
    $('quest-current').appendChild(feedback);
    $('quest-next').addEventListener('click', next);
  }
  function next() {
    if (questionIndex === 0) {
      questionIndex = 1;
      answered = false;
      renderQuestion();
      return;
    }
    const quest = quests[currentIndex];
    if (!completed.includes(quest.slug)) completed.push(quest.slug);
    save();
    renderProgress();
    const hasNext = currentIndex + 1 < quests.length;
    $('quest-current').innerHTML = `<p class="ia-eyebrow">本关完成</p><h2>你找到了${quest.name}的设计逻辑。</h2><p class="ia-clue">这关的两项判断已经完成。可以回到拆解和项目档案继续核对，也可以进入下一件作品。</p><div class="ia-quest-actions"><a href="/dossier/?project=${quest.slug}">继续核对证据</a>${hasNext ? '<button class="ia-primary" id="quest-next-level" type="button">进入下一关</button>' : '<button class="ia-primary" id="quest-finish" type="button">查看全部关卡</button>'}</div>`;
    if (hasNext) $('quest-next-level').addEventListener('click', () => select(currentIndex + 1));
    else $('quest-finish').addEventListener('click', renderMap);
    renderMap();
  }
  function exportTasks() {
    const lines = ['好设计馆 · 观展任务单', '', '目标：从真实项目中识别任务、约束、设计措施与验证边界。', `当前进度：已完成 ${completed.length} / 8`, ''];
    quests.forEach((quest, index) => {
      lines.push(`第 ${index + 1} 关：${quest.name}（${completed.includes(quest.slug) ? '已完成' : '待完成'}）`);
      quest.questions.forEach((question, qIndex) => lines.push(`  ${qIndex + 1}. ${question.q}`));
      lines.push(`  我的发现：________________`, '');
    });
    lines.push('说明：题目与解释基于公开项目资料，仍应回到项目证据核对。');
    const url = URL.createObjectURL(new Blob([lines.join('\n')], { type: 'text/plain;charset=utf-8' }));
    const link = document.createElement('a');
    link.href = url;
    link.download = '好设计馆-观展任务单.txt';
    link.click();
    URL.revokeObjectURL(url);
  }

  $('quest-export').addEventListener('click', exportTasks);
  const firstIncomplete = quests.findIndex(quest => !completed.includes(quest.slug));
  currentIndex = firstIncomplete >= 0 ? Math.min(firstIncomplete, unlockedCount() - 1) : quests.length - 1;
  renderProgress();
  select(currentIndex);
})();
