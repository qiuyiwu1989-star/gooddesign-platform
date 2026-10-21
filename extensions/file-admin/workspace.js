'use strict';
(() => {
 const buttons=[...document.querySelectorAll('[data-view]')];
 const names={files:'文件',review:'提炼与审核',jobs:'处理记录'};
 function view(){return location.hash==='#research-panel'?'review':location.hash==='#jobs'?'jobs':'files'}
 function apply(){const current=view();document.querySelectorAll('[data-admin-view]').forEach(x=>x.hidden=x.dataset.adminView!==current);buttons.forEach(b=>{if(b.dataset.view===current)b.setAttribute('aria-current','page');else b.removeAttribute('aria-current')});document.querySelector('#file-actions').hidden=current!=='files';document.querySelector('#file-kinds').hidden=current!=='files';document.querySelector('#admin-location').textContent='资料管理 / '+names[current];document.querySelector('#review-scope-note').hidden=scope==='project';}
 buttons.forEach(b=>b.onclick=()=>{const hash={files:'#files',review:'#research-panel',jobs:'#jobs'}[b.dataset.view];if(location.hash!==hash)history.pushState(null,'',hash);apply();document.querySelector('.admin-tabs').scrollIntoView({block:'start'})});
 addEventListener('popstate',apply);addEventListener('hashchange',apply);document.addEventListener('project-ready',apply);
 document.querySelector('#review-project-scope').onclick=()=>{document.querySelector('#material-scope').value='project';document.querySelector('#material-scope').dispatchEvent(new Event('change'))};
 document.addEventListener('research-ready',e=>{const n=e.detail.counts.pending||0;document.querySelector('#review-count').textContent=n?'· '+n:''});
 apply();
 // Plain HTML remains readable without JS; enhanced controls only hide sibling tasks.
})();
