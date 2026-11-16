(() => {
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const projects = [...document.querySelectorAll('.heavy-project')];
  const steps = [...document.querySelectorAll('.heavy-step')];
  const current = document.querySelector('.heavy-current');
  const progress = document.querySelector('.heavy-progress > span');
  const browserDialog = document.getElementById('heavy-browser');
  const browseButton = document.querySelector('[data-heavy-browse]');
  const presentButton = document.querySelector('[data-heavy-present]');
  let presenting = false;
  let nativeFullscreen = false;
  if (!reduced) document.documentElement.style.scrollBehavior = 'smooth';

  function activate(step) {
    const project = step.closest('.heavy-project');
    if (!project) return;
    project.dataset.activeStep = step.dataset.step;
    project.querySelectorAll('.heavy-step').forEach(item => item.classList.toggle('is-active', item === step));
    if (current) current.textContent = `${String(projects.indexOf(project) + 1).padStart(2, '0')} / 08`;
  }

  projects.forEach(project => {
    const first = project.querySelector('.heavy-step[data-step="1"]');
    if (first) first.classList.add('is-active');
  });
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) activate(entry.target);
      });
    }, { rootMargin: '-42% 0px -42% 0px', threshold: 0 });
    steps.forEach(step => observer.observe(step));
  }

  let scheduled = false;
  function updateProgress() {
    scheduled = false;
    if (!progress) return;
    const total = document.documentElement.scrollHeight - window.innerHeight;
    const ratio = total > 0 ? Math.min(1, Math.max(0, window.scrollY / total)) : 1;
    progress.style.transform = `scaleX(${ratio})`;
  }
  function schedule() {
    if (scheduled) return;
    scheduled = true;
    requestAnimationFrame(updateProgress);
  }
  window.addEventListener('scroll', schedule, { passive: true });
  window.addEventListener('resize', schedule);
  updateProgress();

  if (browseButton && browserDialog) {
    browseButton.addEventListener('click', () => browserDialog.showModal());
    browserDialog.querySelector('[data-heavy-close]').addEventListener('click', () => browserDialog.close());
    browserDialog.addEventListener('click', event => {
      if (event.target === browserDialog) browserDialog.close();
    });
    browserDialog.querySelectorAll('a').forEach(link => link.addEventListener('click', () => browserDialog.close()));
  }

  function syncPresenting() {
    document.body.classList.toggle('heavy-presenting', presenting);
    if (presentButton) {
      presentButton.textContent = presenting ? '退出细看' : '细看';
      presentButton.setAttribute('aria-pressed', String(presenting));
    }
  }
  async function enterPresenting() {
    presenting = true;
    syncPresenting();
    if (document.documentElement.requestFullscreen) {
      try {
        await document.documentElement.requestFullscreen();
        nativeFullscreen = true;
      } catch (_) {
        nativeFullscreen = false;
      }
    }
  }
  async function exitPresenting() {
    presenting = false;
    syncPresenting();
    if (nativeFullscreen && document.fullscreenElement && document.exitFullscreen) {
      try { await document.exitFullscreen(); } catch (_) {}
    }
    nativeFullscreen = false;
  }
  if (presentButton) presentButton.addEventListener('click', () => presenting ? exitPresenting() : enterPresenting());
  document.addEventListener('fullscreenchange', () => {
    if (!document.fullscreenElement && presenting && nativeFullscreen) {
      presenting = false;
      nativeFullscreen = false;
      syncPresenting();
    }
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && presenting && !document.fullscreenElement && !browserDialog.open) exitPresenting();
  });
})();
