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

// Explicit controls pause/resume the shared worker; retries never approve conflicts.
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
   const st=d.steward,counts=st.counts;
   document.querySelector('#automation-queue').textContent=`本项目：${counts.running||0} 项整理中 · ${(counts.queued||0)+(counts.retry||0)} 项排队 · ${counts.needs_attention||0} 项需判断 · ${counts.awaiting_agent||0} 项待深度阅读`;
   if(st.paused)document.querySelector('#automation-state').textContent='资料管家已暂停 · 原件接收继续';
   const toggle=document.querySelector('#steward-toggle');toggle.disabled=false;toggle.textContent=st.paused?'恢复全库自动整理':'暂停全库自动整理';
   toggle.onclick=async()=>{toggle.disabled=true;try{await api('/api/steward-control?project='+encodeURIComponent(pid),{method:'POST',body:JSON.stringify({action:st.paused?'resume':'pause'})});await refreshAutomation()}catch(e){notice(e.message);toggle.disabled=false}};
   const controls=document.querySelector('#steward-controls');controls.replaceChildren();
   if(!st.controls?.length)controls.append(el('p','暂无操作记录。'));
   for(const c of st.controls||[])controls.append(el('p',`${date(c.at)} · ${{pause:'暂停全库整理',resume:'恢复全库整理',retry:'重试任务'}[c.action]||c.action}${c.task_id?' #'+c.task_id:''} · ${c.actor}`));
   const results=document.querySelector('#steward-results');results.replaceChildren();
   const jobLabels={completed:'已整理',awaiting_agent:'等待 Agent 深度阅读',needs_attention:'有内容需判断',queued:'排队中',running:'整理中',retry:'等待重试',failed:'处理失败'};
   if(!st.recent.length)results.append(el('p','暂无新的整理任务。已有资料不会在启动时自动重跑。'));
   for(const t of st.recent.slice(0,5)){
    const row=el('div');row.append(el('strong',t.kind==='fetch'&&t.status==='completed'?'原件已保存':jobLabels[t.status]||t.status));row.append(el('p',t.subject||'研究增量'));
    if(t.result?.publication?.revision)row.append(el('span',' · '+t.result.publication.revision));
    if(t.result&&t.kind!=='fetch')row.append(el('p',`采用 ${t.result.accepted?.length||0} 项；需判断 ${t.result.exceptions?.length||0} 项`));
    for(const issue of t.result?.exceptions||[])row.append(el('p',issue.record_id+' · '+issue.field+'：'+issue.reason));
    if(t.error)row.append(el('p',t.error));
    if(t.status==='failed'){
     const retry=el('button','重试这项任务');retry.onclick=async()=>{retry.disabled=true;try{await api('/api/steward-control?project='+encodeURIComponent(pid),{method:'POST',body:JSON.stringify({action:'retry',task_id:t.id})});await refreshAutomation()}catch(e){notice(e.message);retry.disabled=false}};row.append(retry);
    }
    results.append(row);
   }
  }catch(e){if(project===pid&&request===requestNumber){document.querySelector('#automation-state').textContent='暂时无法读取自动处理状态';document.querySelector('#automation-queue').textContent='请确认本地服务仍在运行';}}
 }
 setInterval(()=>{if(!document.hidden)refreshAutomation();},8000);
 document.addEventListener('project-ready',refreshAutomation);
 document.addEventListener('jobs-updated',refreshAutomation);
 document.addEventListener('project-switching',()=>{requestNumber++;document.querySelector('#automation-state').textContent='正在读取当前项目状态…';document.querySelector('#automation-queue').textContent='';document.querySelector('#steward-toggle').disabled=true;document.querySelector('#steward-results').replaceChildren();document.querySelector('#steward-controls').replaceChildren();});
})();
