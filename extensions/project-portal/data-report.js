(() => {
  'use strict';
  let active = 'projects';
  let page = 1;
  let quality = '';
  const size = 15;
  const $ = selector => document.querySelector(selector);
  const $$ = selector => [...document.querySelectorAll(selector)];

  function syncTabs() {
    $$('[data-table]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.table === active)));
    $$('[data-quality-filter]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.qualityFilter === quality && button.dataset.qualityFilter !== '')));
  }

  function render() {
    const query = $('#report-search').value.trim().toLowerCase();
    let count = 0;
    $$('[data-panel]').forEach(panel => {
      panel.hidden = panel.dataset.panel !== active;
      if (panel.hidden) return;
      const rows = [...panel.querySelectorAll('tbody tr')];
      const hits = rows.filter(row => {
        const matchesQuery = row.textContent.toLowerCase().includes(query);
        const matchesQuality = active !== 'projects' || !quality || row.dataset.quality === quality;
        return matchesQuery && matchesQuality;
      });
      count = hits.length;
      const pages = Math.max(1, Math.ceil(count / size));
      page = Math.min(page, pages);
      rows.forEach(row => { row.hidden = true; });
      hits.slice((page - 1) * size, page * size).forEach(row => { row.hidden = false; });
      $('#detail-page').textContent = `${page} / ${pages}`;
      $('#detail-prev').disabled = page === 1;
      $('#detail-next').disabled = page === pages;
    });
    const qualityLabel = active === 'projects' && quality ? `，状态：${quality}` : '';
    $('#detail-count').textContent = count ? `匹配 ${count} 项${qualityLabel}` : `没有符合条件的条目${qualityLabel}，试试其他关键词或查看全部状态。`;
  }

  $$('[data-table]').forEach(button => button.addEventListener('click', () => {
    active = button.dataset.table;
    page = 1;
    syncTabs();
    render();
  }));

  $$('[data-quality-filter]').forEach(button => button.addEventListener('click', () => {
    active = 'projects';
    quality = button.dataset.qualityFilter;
    page = 1;
    syncTabs();
    render();
    if (quality) $('#details').scrollIntoView({ block: 'start', behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth' });
  }));

  $$('.dr-evidence-link').forEach(link => link.addEventListener('keydown', event => {
    if (event.key !== 'Enter') return;
    event.preventDefault();
    window.location.href = link.getAttribute('href');
  }));

  $('#report-search').addEventListener('input', () => { page = 1; render(); });
  $('#detail-prev').addEventListener('click', () => { page -= 1; render(); });
  $('#detail-next').addEventListener('click', () => { page += 1; render(); });
  $('#print-report').addEventListener('click', () => window.print());
  function setView(view, update = true) {
    const selected = view === 'quality' ? 'quality' : 'value';
    $$('[data-view]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.view === selected)));
    $$('[data-view-panel]').forEach(panel => { panel.hidden = panel.dataset.viewPanel !== selected; });
    $$('[data-view-nav]').forEach(nav => { nav.hidden = nav.dataset.viewNav !== selected; });
    if (update) {
      const url = new URL(location.href);
      if (selected === 'quality') url.searchParams.set('view', 'quality');
      else url.searchParams.delete('view');
      history.replaceState({}, '', url);
    }
  }

  function assetFilters() {
    const params = new URLSearchParams(location.search);
    return { year: params.get('year') || '', award: params.get('award') || '' };
  }

  function renderAssetFilters() {
    const { year, award } = assetFilters();
    const cards = $$('#asset-projects .dr-showcase-card');
    const matches = cards.filter(card => (!year || card.dataset.year === year) && (!award || card.dataset.award === award));
    cards.forEach(card => { card.hidden = true; });
    matches.slice(0, 6).forEach(card => { card.hidden = false; });
    $('#asset-empty').hidden = matches.length > 0;
    $('#asset-clear').hidden = !year && !award;
    $('#asset-filter-status').textContent = `${year ? year + '年' : '全部年份'} · ${award || '全部奖项'} · ${matches.length} 个代表项目`;
    const explore = new URL('/projects/', location.origin);
    if (year) explore.searchParams.set('year', year);
    if (award) explore.searchParams.set('award', award);
    explore.hash = 'collection';
    $('#asset-explore').href = explore.pathname + explore.search + explore.hash;

    const awardLinks = $$('.dr-legend-item');
    const segments = $$('.dr-donut-segment');
    awardLinks.forEach((link, index) => {
      const selected = award && new URL(link.getAttribute('href'), location.origin).searchParams.get('award') === award;
      link.classList.toggle('dr-selected', Boolean(selected));
      if (segments[index]) segments[index].classList.toggle('dr-muted', Boolean(award && !selected));
    });
    $$('.dr-year-panel a[href*="/projects/"]').forEach(link => {
      const selected = year && new URL(link.getAttribute('href'), location.origin).searchParams.get('year') === year;
      link.classList.toggle('dr-selected', Boolean(selected));
      link.classList.toggle('dr-muted', Boolean(year && !selected));
    });
  }

  function updateAssetFilter(key, value) {
    const url = new URL(location.href);
    if (url.searchParams.get(key) === value) url.searchParams.delete(key);
    else url.searchParams.set(key, value);
    url.searchParams.delete('view');
    history.replaceState({}, '', url);
    setView('value', false);
    renderAssetFilters();
  }

  $$('[data-view]').forEach(button => button.addEventListener('click', () => setView(button.dataset.view)));
  $$('.dr-legend-item').forEach(link => link.addEventListener('click', event => {
    event.preventDefault();
    updateAssetFilter('award', new URL(link.getAttribute('href'), location.origin).searchParams.get('award'));
  }));
  $$('.dr-year-panel a[href*="/projects/"]').forEach(link => link.addEventListener('click', event => {
    event.preventDefault();
    updateAssetFilter('year', new URL(link.getAttribute('href'), location.origin).searchParams.get('year'));
  }));
  $('#asset-clear').addEventListener('click', () => {
    const url = new URL(location.href);
    url.searchParams.delete('year');
    url.searchParams.delete('award');
    history.replaceState({}, '', url);
    renderAssetFilters();
  });

  setView(new URLSearchParams(location.search).get('view'), false);
  renderAssetFilters();
  syncTabs();
  render();
})();
