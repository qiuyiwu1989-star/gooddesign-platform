(() => {
  const links = [...document.querySelectorAll('[data-chapter-link]')];
  const chapters = links.map(link => document.getElementById(link.dataset.chapterLink)).filter(Boolean);
  const progress = document.querySelector('.heavy-progress span');
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!reduced) document.documentElement.style.scrollBehavior = 'smooth';

  function setCurrent(id) {
    links.forEach(link => {
      if (link.dataset.chapterLink === id) link.setAttribute('aria-current', 'true');
      else link.removeAttribute('aria-current');
    });
  }

  if (chapters.length) setCurrent(chapters[0].id);
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      const visible = entries.filter(entry => entry.isIntersecting).sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
      if (visible) setCurrent(visible.target.id);
    }, { rootMargin: '-18% 0px -62% 0px', threshold: [0, 0.1, 0.3] });
    chapters.forEach(chapter => observer.observe(chapter));
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
  if (!reduced) {
    window.addEventListener('scroll', schedule, { passive: true });
    window.addEventListener('resize', schedule);
  }
  updateProgress();
})();
