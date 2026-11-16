const root = document.documentElement;
const themeToggle = document.getElementById('theme-toggle');
const savedTheme = localStorage.getItem('gd-preview-theme');
if (savedTheme === 'dark' || savedTheme === 'light') root.dataset.theme = savedTheme;

function syncTheme() {
  const dark = root.dataset.theme === 'dark';
  themeToggle.textContent = dark ? '浅色' : '深色';
  themeToggle.setAttribute('aria-label', dark ? '切换为浅色主题' : '切换为深色主题');
}
syncTheme();
themeToggle.addEventListener('click', () => {
  root.dataset.theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
  localStorage.setItem('gd-preview-theme', root.dataset.theme);
  syncTheme();
});

const dialog = document.getElementById('evidence-dialog');
const evidenceOpen = document.getElementById('evidence-open');
const evidenceClose = document.getElementById('evidence-close');
evidenceOpen.addEventListener('click', () => {
  dialog.showModal();
  evidenceClose.focus();
});
evidenceClose.addEventListener('click', () => dialog.close());
dialog.addEventListener('click', event => {
  if (event.target !== dialog) return;
  const rect = dialog.getBoundingClientRect();
  if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) dialog.close();
});
dialog.addEventListener('close', () => evidenceOpen.focus());

const routeDetails = {
  r1: '<strong>下一步：</strong>先确认接触、排屑和清洁的边界，再讨论模块拆分。',
  r2: '<strong>下一步：</strong>先定义作业状态、退出条件和故障退回，再评估分时控制。',
  r3: '<strong>下一步：</strong>先建立独立量测和校准基线，再研究感知与调整。'
};
const routeNames = {
  r1: '接触模块与可拆卸胶路分离',
  r2: '作用、退出与清理按状态分时',
  r3: '独立参考量测后再研究感知调整'
};
let selectedRoute = 'r1';
const routeButtons = [...document.querySelectorAll('[data-route]')];
const routeDetail = document.getElementById('route-detail');
routeButtons.forEach(button => button.addEventListener('click', () => {
  selectedRoute = button.dataset.route;
  routeButtons.forEach(item => {
    const selected = item === button;
    item.setAttribute('aria-pressed', String(selected));
    item.querySelector('.gd-route-action').textContent = selected ? '当前比较路线' : '选择比较';
  });
  routeDetail.innerHTML = routeDetails[selectedRoute];
}));

document.getElementById('search-form').addEventListener('submit', event => {
  event.preventDefault();
  const query = document.getElementById('project-search').value.trim();
  const award = document.getElementById('award-filter').value;
  document.getElementById('search-status').textContent = query
    ? `检索条件已整理：${query}，${award}。样板页不发起网络检索。`
    : '请输入项目、完成单位或关键词后再检索。';
});

const feedbackForm = document.getElementById('feedback-form');
const feedbackStatus = document.getElementById('feedback-status');
function feedbackPayload(kind) {
  return {
    id: `${kind}-${Date.now()}`,
    kind,
    route_id: selectedRoute,
    route_name: routeNames[selectedRoute],
    role: document.getElementById('feedback-role').value.trim(),
    body: document.getElementById('feedback-body').value.trim(),
    status: kind === 'feedback' ? 'pending_review' : 'pending_confirmation',
    saved_at: new Date().toISOString()
  };
}
function saveRecord(kind) {
  const record = feedbackPayload(kind);
  if (!record.role || !record.body) {
    feedbackStatus.textContent = '请填写角色和具体内容，已输入的内容会保留。';
    feedbackStatus.className = 'gd-status gd-error';
    return;
  }
  const key = 'gd-preview-records';
  const records = JSON.parse(localStorage.getItem(key) || '[]');
  records.push(record);
  localStorage.setItem(key, JSON.stringify(records));
  feedbackStatus.textContent = kind === 'feedback'
    ? `已保存“${record.route_name}”的待审核反馈，共 ${records.length} 条本机记录。`
    : `已保存“${record.route_name}”的待确认条件，原需求未被改写。`;
  feedbackStatus.className = 'gd-status';
}
feedbackForm.addEventListener('submit', event => {
  event.preventDefault();
  saveRecord('feedback');
});
document.getElementById('clarification-save').addEventListener('click', () => saveRecord('clarification'));
