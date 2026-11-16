(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const fields = { q: $('query'), year: $('year'), award: $('award'), status: $('status') };
  const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]));
  const pageSize = 12;
  let rows = [];
  let page = 1;

  function restore() {
    const url = new URL(location.href);
    Object.entries(fields).forEach(([key, element]) => { element.value = url.searchParams.get(key) || ''; });
    page = Math.max(1, parseInt(url.searchParams.get('page'), 10) || 1);
    $('hero-query').value = fields.q.value;
  }

  function awardIcon(award) {
    const slug = { '金奖': 'gold', '银奖': 'silver', '铜奖': 'bronze', '创意奖': 'creative', '提名奖': 'nominee', '菁英奖': 'elite' }[award] || 'nominee';
    return `<img class="gd-award-icon" src="/inno/portal/awards/${slug}.svg?v=medal-20261116" alt="">`;
  }

  function card(project) {
    const cover = project.cover
      ? `<img src="../project-portal/${esc(project.cover)}" alt="${esc(project.name)}${project.cover_kind === 'scene_illustration' ? ' · 场景插画' : '项目示意'}" loading="lazy">${project.cover_kind === 'scene_illustration' ? '<span class="gd-cover-caption">场景插画</span>' : ''}`
      : `<div class="gd-no-cover"><strong>${esc(project.year)}</strong><span>${esc(project.award)}</span><small>好设计 · 项目档案</small></div>`;
    const status = project.research
      ? '<span class="gd-badge gd-badge--accent">研究整理版</span>'
      : '<span class="gd-badge">基础条目</span>';
    return `<a class="gd-project-card" href="/dossier/?project=${encodeURIComponent(project.id)}"><div class="gd-project-cover" data-cover-kind="${esc(project.cover_kind || '')}">${cover}</div><div class="gd-project-body"><div class="gd-project-meta"><span class="gd-award-label">${awardIcon(project.award)}<span>${esc(project.year)} · ${esc(project.award)}</span></span>${status}</div><h3>${esc(project.name)}</h3><p class="gd-project-summary">${esc(project.summary || '从项目条目开始，进一步了解它的任务、设计与技术线索。')}</p><div class="gd-project-unit"><span>${esc(project.unit || '完成单位待补')}</span></div></div></a>`;
  }

  function render(push = false) {
    const query = fields.q.value.trim().toLowerCase();
    const filtered = rows.filter(project =>
      (!query || [project.name, project.unit, project.summary, project.id].join(' ').toLowerCase().includes(query)) &&
      (!fields.year.value || String(project.year) === fields.year.value) &&
      (!fields.award.value || project.award === fields.award.value) &&
      (!fields.status.value || (fields.status.value === 'research' ? project.research : !project.research))
    );
    const pages = Math.max(1, Math.ceil(filtered.length / pageSize));
    page = Math.min(page, pages);
    const url = new URL(location.href);
    Object.entries(fields).forEach(([key, element]) => {
      if (element.value) url.searchParams.set(key, element.value);
      else url.searchParams.delete(key);
    });
    if (page > 1) url.searchParams.set('page', page);
    else url.searchParams.delete('page');
    if (push) history.pushState({}, '', url);
    else history.replaceState({}, '', url);
    $('result-count').textContent = `${filtered.length} 个项目`;
    $('clear').disabled = !Object.values(fields).some(element => Boolean(element.value));
    $('page-state').textContent = `${page} / ${pages}`;
    $('previous').disabled = page === 1;
    $('next').disabled = page === pages;
    $('pagination').hidden = !filtered.length;
    $('empty').hidden = Boolean(filtered.length);
    $('projects').setAttribute('aria-busy', 'false');
    $('projects').innerHTML = filtered.slice((page - 1) * pageSize, page * pageSize).map(card).join('');
  }

  function reset() {
    Object.values(fields).forEach(element => { element.value = ''; });
    $('hero-query').value = '';
    page = 1;
    render(true);
  }

  $('filters').addEventListener('submit', event => event.preventDefault());
  fields.q.addEventListener('input', () => { page = 1; render(); });
  ['year', 'award', 'status'].forEach(key => fields[key].addEventListener('change', () => { page = 1; render(true); }));
  $('clear').addEventListener('click', reset);
  $('empty-clear').addEventListener('click', reset);
  $('hero-search').addEventListener('submit', event => {
    event.preventDefault();
    fields.q.value = $('hero-query').value;
    page = 1;
    render(true);
    $('collection').scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth' });
  });
  $('previous').addEventListener('click', () => { page -= 1; render(true); $('collection').scrollIntoView({ block: 'start' }); });
  $('next').addEventListener('click', () => { page += 1; render(true); $('collection').scrollIntoView({ block: 'start' }); });
  addEventListener('popstate', () => { restore(); render(); });

  fetch('/inno/catalog.json', { cache: 'no-store' })
    .then(response => { if (!response.ok) throw Error('catalog_unavailable'); return response.json(); })
    .then(data => {
      rows = data.map(p => ({...p,...(window.GD_PROJECT_COVERS?.[p.id] || {})}));
      $('stats-projects').textContent = rows.length;
      $('stats-covers').textContent = rows.filter(project => Boolean(project.cover)).length;
      $('stats-research').textContent = rows.filter(project => project.research).length;
      $('stats-awards').textContent = new Set(rows.map(project => project.award)).size;
      const options = [
        ['year', [...new Set(rows.map(project => project.year))].sort((a, b) => b - a)],
        ['award', [...new Set(rows.map(project => project.award))]]
      ];
      options.forEach(([id, values]) => $(id).insertAdjacentHTML('beforeend', values.map(value => `<option value="${esc(value)}">${esc(value)}</option>`).join('')));
      restore();
      render();
    })
    .catch(() => {
      $('projects').setAttribute('aria-busy', 'false');
      $('projects').replaceChildren();
      $('result-count').textContent = '项目目录暂时无法加载';
      $('empty').hidden = false;
      $('empty').querySelector('h3').textContent = '项目目录加载失败';
      $('empty').querySelector('p').textContent = '请检查网络连接后重试，已输入的筛选条件会保留在地址栏。';
      $('empty-clear').textContent = '重新加载';
      $('empty-clear').addEventListener('click', () => location.reload(), { once: true });
      $('pagination').hidden = true;
    });
})();
