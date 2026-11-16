(() => {
  const $ = id => document.getElementById(id);
  const projects = JSON.parse($('studio-projects').textContent);
  const storageKey = 'gd-studio-draft-v1';
  const defaults = { project: projects[0].id, name: '我的极限设计', problem: '', desc: '', theme: 'ocean', size: 44, x: 10, y: 22 };
  let state = { ...defaults };

  function readHash() {
    if (!location.hash.startsWith('#design=')) return null;
    try { return JSON.parse(decodeURIComponent(escape(atob(location.hash.slice(8))))); } catch (_) { return null; }
  }
  function restore() {
    const shared = readHash();
    if (shared) return { ...defaults, ...shared };
    try { return { ...defaults, ...JSON.parse(localStorage.getItem(storageKey) || '{}') }; } catch (_) { return { ...defaults }; }
  }
  function project() {
    return projects.find(item => item.id === state.project) || projects[0];
  }
  function render() {
    $('studio-project').value = state.project;
    $('studio-name').value = state.name;
    $('studio-problem').value = state.problem;
    $('studio-desc').value = state.desc;
    $('studio-size').value = state.size;
    $('studio-size-value').textContent = `${state.size}px`;
    $('studio-preview').dataset.theme = state.theme;
    $('studio-image').src = project().cover;
    $('studio-image').alt = `${project().name}项目背景`;
    $('studio-project-name').textContent = project().name;
    $('studio-title').textContent = state.name || '我的极限设计';
    $('studio-title').style.left = `${state.x}%`;
    $('studio-title').style.top = `${state.y}%`;
    $('studio-title').style.fontSize = `${state.size}px`;
    $('studio-problem-preview').textContent = state.problem || '写下这个设计要解决的真实问题。';
    $('studio-description').textContent = state.desc || '你的设计说明会出现在这里。';
    $('studio-theme').querySelectorAll('button').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.value === state.theme)));
  }
  function update(key, value) {
    state[key] = value;
    render();
  }
  function save() {
    try {
      localStorage.setItem(storageKey, JSON.stringify(state));
      $('studio-status').textContent = '草稿已保存到本机。';
    } catch (_) {
      $('studio-status').textContent = '当前浏览器无法保存草稿，请先导出作品。';
    }
  }
  function share() {
    const encoded = btoa(unescape(encodeURIComponent(JSON.stringify(state))));
    const url = `${location.origin}${location.pathname}#design=${encoded}`;
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(url).then(() => {
        $('studio-status').textContent = '分享链接已复制，打开后会恢复当前作品。';
      }).catch(() => window.prompt('复制这个作品链接：', url));
    } else {
      window.prompt('复制这个作品链接：', url);
    }
  }
  function wrap(context, text, x, y, maxWidth, lineHeight, maxLines) {
    const characters = [...text];
    let line = '';
    let lines = 0;
    for (const character of characters) {
      const candidate = line + character;
      if (context.measureText(candidate).width > maxWidth && line) {
        context.fillText(line, x, y);
        y += lineHeight;
        line = character;
        lines += 1;
        if (lines >= maxLines) return y;
      } else {
        line = candidate;
      }
    }
    if (line) context.fillText(line, x, y);
    return y + lineHeight;
  }
  function exportImage() {
    const canvas = document.createElement('canvas');
    canvas.width = 1200;
    canvas.height = 1500;
    const context = canvas.getContext('2d');
    const image = new Image();
    image.onload = () => {
      const scale = Math.max(1200 / image.width, 1500 / image.height);
      const width = image.width * scale;
      const height = image.height * scale;
      context.drawImage(image, (1200 - width) / 2, (1500 - height) / 2, width, height);
      const gradient = context.createLinearGradient(0, 0, 0, 1500);
      gradient.addColorStop(0, 'rgba(5,12,20,.15)');
      gradient.addColorStop(1, state.theme === 'coral' ? 'rgba(74,27,20,.94)' : state.theme === 'graphite' ? 'rgba(12,12,16,.94)' : 'rgba(5,17,29,.94)');
      context.fillStyle = gradient;
      context.fillRect(0, 0, 1200, 1500);
      context.fillStyle = 'rgba(255,255,255,.72)';
      context.font = '24px sans-serif';
      wrap(context, project().name, 80, 90, 1000, 34, 2);
      context.fillStyle = '#fff';
      context.font = `600 ${state.size * 2}px sans-serif`;
      wrap(context, state.name || '我的极限设计', state.x * 12, state.y * 15, 900, state.size * 2.5, 4);
      context.fillStyle = 'rgba(255,255,255,.86)';
      context.font = '30px sans-serif';
      wrap(context, state.problem || '写下这个设计要解决的真实问题。', 80, 1160, 1000, 46, 3);
      context.fillStyle = 'rgba(255,255,255,.66)';
      context.font = '24px sans-serif';
      wrap(context, state.desc || '你的设计说明会出现在这里。', 80, 1320, 1000, 38, 4);
      context.font = '20px sans-serif';
      context.fillText('GoodDesign Studio · 概念作品，未经工程验证', 80, 1450);
      const link = document.createElement('a');
      link.download = `${(state.name || '我的极限设计').replace(/[\\/:*?"<>|]/g, '-')}.png`;
      link.href = canvas.toDataURL('image/png');
      link.click();
      $('studio-status').textContent = 'PNG 已生成。';
    };
    image.onerror = () => { $('studio-status').textContent = '项目图片暂时无法导出，请稍后重试。'; };
    image.src = project().cover;
  }
  function newDesign() {
    state = { ...defaults };
    try { localStorage.removeItem(storageKey); } catch (_) {}
    history.replaceState(null, '', location.pathname);
    render();
    $('studio-status').textContent = '已经开始新的创作。';
  }

  $('studio-form').addEventListener('submit', event => event.preventDefault());
  $('studio-project').addEventListener('change', event => update('project', event.target.value));
  $('studio-name').addEventListener('input', event => update('name', event.target.value));
  $('studio-problem').addEventListener('input', event => update('problem', event.target.value));
  $('studio-desc').addEventListener('input', event => update('desc', event.target.value));
  $('studio-size').addEventListener('input', event => update('size', Number(event.target.value)));
  $('studio-theme').querySelectorAll('button').forEach(button => button.addEventListener('click', () => update('theme', button.dataset.value)));
  $('studio-save').addEventListener('click', save);
  $('studio-share').addEventListener('click', share);
  $('studio-export').addEventListener('click', exportImage);
  $('studio-new').addEventListener('click', newDesign);

  let dragging = null;
  $('studio-title').addEventListener('pointerdown', event => {
    dragging = { x: event.clientX, y: event.clientY, startX: state.x, startY: state.y };
    $('studio-title').setPointerCapture(event.pointerId);
    event.preventDefault();
  });
  $('studio-title').addEventListener('pointermove', event => {
    if (!dragging) return;
    const bounds = $('studio-preview').getBoundingClientRect();
    state.x = Math.max(5, Math.min(65, dragging.startX + (event.clientX - dragging.x) / bounds.width * 100));
    state.y = Math.max(12, Math.min(72, dragging.startY + (event.clientY - dragging.y) / bounds.height * 100));
    render();
  });
  $('studio-title').addEventListener('pointerup', () => { dragging = null; });
  $('studio-title').addEventListener('pointercancel', () => { dragging = null; });

  state = restore();
  render();
})();
