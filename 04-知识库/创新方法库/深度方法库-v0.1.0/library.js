(() => {
  const query = document.querySelector('#query');
  const category = document.querySelector('#category');
  const kind = document.querySelector('#record-kind');
  const cards = [...document.querySelectorAll('.method-card')];
  function filter() {
    const tokens = query.value.toLocaleLowerCase().trim().split(/\s+/).filter(Boolean);
    let count = 0;
    for (const card of cards) {
      const match = (!category.value || card.dataset.category === category.value) &&
        (!kind.value || card.dataset.kind === kind.value) &&
        tokens.every(word => card.dataset.search.includes(word));
      card.hidden = !match;
      if (match) count++;
    }
    document.querySelector('#result-count').textContent = `${count} / ${cards.length} 项内容`;
    document.querySelector('#empty').hidden = count !== 0;
  }
  if (query) {
    query.addEventListener('input', filter);
    category.addEventListener('change', filter);
    kind.addEventListener('change', filter);
  }
  const modules = [...document.querySelectorAll('details.module')];
  function locate() {
    const hash = decodeURIComponent(location.hash.slice(1));
    const target = document.getElementById(hash);
    const ancestor = target?.closest('details.module');
    if (ancestor) ancestor.open = true;
    if (target) requestAnimationFrame(() => target.scrollIntoView({block: 'start'}));
  }
  window.addEventListener('hashchange', locate);
  window.addEventListener('pageshow', locate);
  if (location.hash) locate();
  let printState = null;
  window.addEventListener('beforeprint', () => {
    printState = modules.map(m => m.open);
    document.body.dataset.printing = 'true';
    modules.forEach(m => { m.open = true; });
  });
  window.addEventListener('afterprint', () => {
    if (printState) modules.forEach((m, i) => { m.open = printState[i]; });
    delete document.body.dataset.printing;
  });
  document.querySelector('#print')?.addEventListener('click', () => window.print());
})();
