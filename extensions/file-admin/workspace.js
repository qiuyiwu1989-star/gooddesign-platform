'use strict';
(() => {
 const buttons=[...document.querySelectorAll('[data-view]')];
 const names={files:'文件',review:'整理入档',jobs:'任务进度'};
 function view(){return location.hash==='#research-panel'?'review':location.hash==='#jobs'?'jobs':'files'}
 function apply(){const current=view();document.querySelectorAll('[data-admin-view]').forEach(x=>x.hidden=x.dataset.adminView!==current);buttons.forEach(b=>{if(b.dataset.view===current)b.setAttribute('aria-current','page');else b.removeAttribute('aria-current')});document.querySelector('#file-actions').hidden=current!=='files';document.querySelector('#file-kinds').hidden=current!=='files';document.querySelector('#admin-location').textContent='资料管理 / '+names[current];document.querySelector('#review-scope-note').hidden=scope==='project';}
 buttons.forEach(b=>b.onclick=()=>{const hash={files:'#files',review:'#research-panel',jobs:'#jobs'}[b.dataset.view];if(location.hash!==hash)history.pushState(null,'',hash);apply();if(b.dataset.view==='jobs')jobs().catch(e=>notice(e.message));document.querySelector('.admin-tabs').scrollIntoView({block:'start'})});
 addEventListener('popstate',apply);addEventListener('hashchange',apply);document.addEventListener('project-ready',apply);
 document.querySelector('#review-project-scope').onclick=()=>{document.querySelector('#material-scope').value='project';document.querySelector('#material-scope').dispatchEvent(new Event('change'))};
 document.addEventListener('research-ready',e=>{const n=e.detail.counts.pending||0;document.querySelector('#review-count').textContent=n?'· '+n:''});
 apply();
 // Plain HTML remains readable without JS; enhanced controls only hide sibling tasks.
})();

// Status only: does not start jobs or adopt research candidates.
(() => {
 let requestNumber=0;
 async function refreshAutomation(){
  const pid=project,request=++requestNumber;
  if(!pid)return;
  try{
   const d=await api('/api/automation?project='+encodeURIComponent(pid));
   if(project!==pid||request!==requestNumber)return;
   const labels={running:'自动接收与提取 · 运行中',starting:'自动接收与提取 · 正在启动',stopped:'自动接收与提取 · 未启动',error:'自动巡检遇到问题，请查看任务进度',delayed:'自动巡检尚未完成，请稍后查看'};
   document.querySelector('#automation-state').textContent=labels[d.state]||'自动处理状态未知';
   document.querySelector('#automation-queue').textContent=`本项目：${d.running} 项处理中 · ${d.queued} 项排队 · ${d.attention_records} 条异常或中断记录`;
  }catch(e){if(project===pid&&request===requestNumber){document.querySelector('#automation-state').textContent='暂时无法读取自动处理状态';document.querySelector('#automation-queue').textContent='请确认本地服务仍在运行';}}
 }
 setInterval(()=>{if(!document.hidden)refreshAutomation();},8000);
 document.addEventListener('project-ready',refreshAutomation);
 document.addEventListener('jobs-updated',refreshAutomation);
 document.addEventListener('project-switching',()=>{requestNumber++;document.querySelector('#automation-state').textContent='正在读取当前项目状态…';document.querySelector('#automation-queue').textContent='';});
})();
