'use strict';
(() => {
 const tabs=[...document.querySelectorAll('.tabs [role=tab]')],panels=[...document.querySelectorAll('main>section[role=tabpanel]')];
 const stageTabs=[...document.querySelectorAll('.stage-picker [role=tab]')];
 const stagePanels=[...document.querySelectorAll('#process>div[role=tabpanel]')];
 function setTabs(buttons,sections,id){buttons.forEach(t=>{const active=t.getAttribute('aria-controls')===id;t.setAttribute('aria-selected',String(active));t.tabIndex=active?0:-1});sections.forEach(p=>p.hidden=p.id!==id)}
 function stage(i){setTabs(stageTabs,stagePanels,'stage-'+i)}
 function show(id){setTabs(tabs,panels,id)}
 function route(){const raw=location.hash.slice(1);const selected=/^process-([1-3])$/.exec(raw);if(selected){show('process');stage(Number(selected[1])-1);return;}const aliases={methods:'process',questions:'report',tests:'report'};show(aliases[raw]||(['report','process','evidence'].includes(raw)?raw:'report'));if(raw==='methods'){stage(0);document.querySelector('#stage-0>.method').open=true}if(['questions','tests'].includes(raw))document.getElementById(raw).open=true;}
 function keyboard(buttons){buttons.forEach((t,i)=>t.addEventListener('keydown',e=>{const index=e.key==='Home'?0:e.key==='End'?buttons.length-1:e.key==='ArrowRight'?(i+1)%buttons.length:e.key==='ArrowLeft'?(i-1+buttons.length)%buttons.length:-1;if(index>=0){e.preventDefault();buttons[index].focus();buttons[index].click()}}))}
 tabs.forEach(t=>t.onclick=()=>{history.pushState(null,'','#'+t.getAttribute('aria-controls'));route()});
 stageTabs.forEach((t,i)=>t.onclick=()=>{history.pushState(null,'','#process-'+(i+1));show('process');stage(i)});keyboard(tabs);keyboard(stageTabs);
 document.querySelectorAll('[data-stage]').forEach(a=>a.onclick=e=>{e.preventDefault();history.pushState(null,'','#process-'+(Number(a.dataset.stage)+1));route();document.querySelector('.tabs').scrollIntoView({block:'start'})});
 document.querySelectorAll('[data-open]').forEach(b=>b.onclick=()=>{const d=document.getElementById(b.dataset.open);d.open=true;d.scrollIntoView({behavior:'smooth',block:'start'})});
 addEventListener('popstate',route);addEventListener('hashchange',route);route();
 document.querySelectorAll('.direction').forEach(d=>d.addEventListener('toggle',()=>{if(d.open)document.querySelectorAll('.direction').forEach(other=>{if(other!==d)other.open=false})}));
 const dialog=document.getElementById('evidence-dialog'),body=document.getElementById('evidence-body');
 document.querySelectorAll('[data-evidence]').forEach(b=>b.onclick=()=>{const source=document.getElementById('ev-'+b.dataset.evidence);if(!source)return;const copy=source.cloneNode(true);copy.removeAttribute('id');copy.querySelector('.original').open=true;body.replaceChildren(copy);const direction=b.closest('.direction');document.getElementById('evidence-context').textContent=direction?'对应建议：'+direction.querySelector('summary strong').textContent:'当前分析使用的参考依据';dialog.showModal()});
 document.getElementById('close-evidence').onclick=()=>dialog.close();dialog.addEventListener('click',e=>{if(e.target===dialog){const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)dialog.close()}});
 // Keep evidence and methods available on paper, then restore the reading state.
 let printed=[];addEventListener('beforeprint',()=>{printed=[...document.querySelectorAll('details')].map(x=>[x,x.open]);printed.forEach(([x])=>x.open=true)});addEventListener('afterprint',()=>printed.forEach(([x,open])=>x.open=open));
 const replay=document.getElementById('replay'),message=document.getElementById('message');
 if(location.protocol==='file:'){replay.hidden=true;document.querySelector('.workspace-header').hidden=true;document.querySelector('.offline-note').hidden=false;document.querySelectorAll('.source-download').forEach(a=>{a.removeAttribute('href');a.textContent='来源原件请在本地后台查看'})}
 replay.onclick=async()=>{replay.disabled=true;try{const initial=await fetch('/api/projects').then(r=>r.json());const response=await fetch('/api/method-demo?project=2025-00',{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':initial.token},body:JSON.stringify({actor:'本地用户重放固定模拟示例'})});const job=await response.json();if(!response.ok)throw Error(job.error||'提交失败');message.textContent='正在重新读取方法与项目资料。完成后打开新记录，原记录保留。';const poll=async()=>{const r=await fetch('/api/jobs?project=2025-00').then(r=>r.json());const j=r.jobs.find(x=>x.id===job.id);if(!j)throw Error('未找到任务记录');if(j.status==='completed'&&j.result?.run_id){location.href='/methods/?run='+encodeURIComponent(j.result.run_id);return}if(['failed','needs_attention','interrupted'].includes(j.status))throw Error(j.error||'运行未完成，请查看处理记录');setTimeout(()=>poll().catch(e=>{message.textContent=e.message;replay.disabled=false}),1200)};await poll()}catch(e){message.textContent=e.message;replay.disabled=false}};
})();
