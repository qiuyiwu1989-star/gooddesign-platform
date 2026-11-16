(() => {
  const root = document.documentElement;
  const saved = localStorage.getItem('gd-preview-theme');
  if (saved === 'dark' || saved === 'light') root.dataset.theme = saved;
  document.querySelectorAll('[data-gd-theme-toggle]').forEach(button => {
    function sync() {
      const dark = root.dataset.theme === 'dark';
      button.textContent = dark ? '浅色' : '深色';
      button.setAttribute('aria-label', dark ? '切换为浅色主题' : '切换为深色主题');
    }
    sync();
    button.addEventListener('click', () => {
      root.dataset.theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
      localStorage.setItem('gd-preview-theme', root.dataset.theme);
      sync();
    });
  });

  const dialog = document.querySelector('[data-gd-assistant]');
  if (!dialog) return;
  const open = document.querySelector('[data-gd-assistant-open]');
  const close = document.querySelector('[data-gd-assistant-close]');
  dialog.id = dialog.id || 'assistant-panel';
  open.setAttribute('aria-haspopup', 'dialog');
  open.setAttribute('aria-controls', dialog.id);
  open.setAttribute('aria-expanded', 'false');
  open.addEventListener('click', () => {
    dialog.showModal();
    open.setAttribute('aria-expanded', 'true');
    close.focus();
  });
  close.addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => {
    if (event.target !== dialog) return;
    const rect = dialog.getBoundingClientRect();
    if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) dialog.close();
  });
  dialog.addEventListener('close', () => {
    open.setAttribute('aria-expanded', 'false');
    open.focus();
  });
})();
