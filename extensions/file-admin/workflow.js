'use strict';
let wfState=null,wfProject='',wfCandidate=null,wfFiles=[],wfRunning=null,wfAll=false,wfLastJobs=[],wfPreviewIds=[],wfSubmitting=false;
const wfNames={pending:'待你确认',approved:'已确认 · 待入档',needs_more:'需补资料',rejected:'不采用',published:'已入档'};
function wfNotice(t){$('#wf-notice').textContent=t}
function wfActor(){const a=$('#wf-actor').value.trim();if(!a)throw Error('请填写记录人');return a}
async function wfPost(path,body){if(wfProject!==project||!wfState)throw Error('正在切换项目，请稍候');if(scope!=='project')throw Error('请先切回本项目资料');return api(path+'?project='+encodeURIComponent(project),{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)})}
function wfSelected(){return $('#wf-source').value}
function wfLabel(c){return wfState?.schema.entities.find(e=>e.key===c.entity)?.fields.find(f=>f.name===c.field)?.label||'研究内容'}
function wfStep(n,persist=true){n=Math.min(3,Math.max(1,Number(n)||1));document.querySelectorAll('[data-wf-panel]').forEach(p=>p.hidden=Number(p.dataset.wfPanel)!==n);document.querySelectorAll('[data-wf-step]').forEach(b=>{if(Number(b.dataset.wfStep)===n)b.setAttribute('aria-current','step');else b.removeAttribute('aria-current')});if(persist){const u=new URL(location.href);u.searchParams.set('wf_step',String(n));history.replaceState(null,'',u)} }
function wfRemember(){const u=new URL(location.href);if(wfSelected())u.searchParams.set('source',wfSelected());else u.searchParams.delete('source');u.searchParams.set('wf_state',$('#wf-filter').value);if(wfAll)u.searchParams.set('wf_all','1');else u.searchParams.delete('wf_all');history.replaceState(null,'',u)}
async function wfOpenSource(sid){try{wfAll=false;const u=new URL(location.href);u.searchParams.set('source',sid);u.searchParams.set('wf_step','1');u.searchParams.set('wf_state','pending');u.searchParams.delete('wf_all');u.hash='research-panel';history.pushState(null,'',u);dispatchEvent(new Event('hashchange'));await wfLoad();$('#research-panel').scrollIntoView({block:'start'});$('#wf-source').focus()}catch(e){wfNotice(e.message)}}
function wfDescribeSource(){
 const x=wfFiles.find(x=>x.id===wfSelected()),scopeOk=scope==='project';const info=$('#wf-source-info');info.replaceChildren();
 const active=wfSubmitting||!!wfRunning||wfLastJobs.some(j=>['queued','running'].includes(j.status)&&(['fetch','ingest'].includes(j.kind)||j.args.source_id===x?.id));
 $('#wf-pending-count').textContent=(wfState.counts.pending||0)+' 项待确认（全项目）';$('#wf-approved-count').textContent=(wfState.counts.approved||0)+' 项已确认待入档';
 $('#wf-extract').disabled=!x||!scopeOk||active;$('#wf-open-file').disabled=!x;$('#wf-existing').hidden=true;$('#wf-extract').textContent='提取待确认内容';$('#wf-extract').classList.add('primary');$('#wf-existing').classList.remove('primary');
 if(!x){info.append(el('p','请选择一份资料，或从文件列表点击“整理入档”。'));return}
 const records=wfState.candidates.filter(c=>c.source_id===x.id);const pending=records.filter(c=>c.status==='pending').length;
 let hint=x.chunks?'已提取文字，可以开始整理。':'还没有可读文字。扫描 PDF 会先识别文字，其他资料可能需要人工补充。';
 if(active)hint='这份资料或新上传资料正在处理中，请稍候。完成后会更新结果。';
 if(['needs_ocr','partial_text_needs_ocr'].includes(x.status)&&!wfState.capabilities.ocr){hint='这份扫描件需要识别文字，但本机识别工具暂不可用。可以先读原件，或在任务进度中查看问题。';$('#wf-extract').disabled=true}
 info.append(el('p',hint));if(records.length){$('#wf-extract').textContent='重新提取内容';$('#wf-extract').classList.remove('primary');$('#wf-existing').classList.add('primary');info.append(el('p','这份资料已有 '+records.length+' 项整理内容，其中 '+pending+' 项待确认。','muted'));$('#wf-existing').hidden=false;$('#wf-existing').textContent=pending?'核对这份资料的 '+pending+' 项内容 →':'查看这份资料已整理的内容 →'}
 $('#wf-pending-count').textContent=(wfState.counts.pending||0)+' 项待确认（全项目）';$('#wf-approved-count').textContent=(wfState.counts.approved||0)+' 项已确认待入档';
}
function wfFields(){const e=wfState?.schema.entities.find(e=>e.key===$('#wf-entity').value);$('#wf-field').replaceChildren();for(const f of e?.fields||[]){const o=el('option',f.label);o.value=f.name;$('#wf-field').append(o)}}
async function wfLoad(){
 const pid=project;const [state,list]=await Promise.all([api('/api/research?project='+encodeURIComponent(pid)),api('/api/files?project='+encodeURIComponent(pid))]);if(project!==pid)return;
 wfState=state;wfProject=pid;const route=new URLSearchParams(location.search);wfAll=route.get('wf_all')==='1';$('#wf-filter').value=route.has('wf_state')?route.get('wf_state'):'pending';wfFiles=list.files.filter(x=>x.kind!=='source_reference');const requested=new URLSearchParams(location.search).get('source')||$('#wf-source').value;
 $('#wf-source').replaceChildren();const blank=el('option','请选择论文、专利或其他资料');blank.value='';$('#wf-source').append(blank);
 for(const [kind,title]of [['paper','论文'],['patent','专利'],['file','网页与其他文件'],['image','图片与扫描页']]){const group=el('optgroup');group.label=title;for(const x of wfFiles.filter(x=>x.kind===kind)){const o=el('option',x.name);o.value=x.id;group.append(o)}if(group.children.length)$('#wf-source').append(group)}
 $('#wf-source').value=wfFiles.some(x=>x.id===requested)?requested:'';wfRemember();
 const entity=$('#wf-entity').value;$('#wf-entity').replaceChildren();for(const e of state.schema.entities){const o=el('option',e.label);o.value=e.key;$('#wf-entity').append(o)}if(entity)$('#wf-entity').value=entity;wfFields();
 $('#wf-summary').replaceChildren();for(const t of ['研究版本 '+Number(state.revision.split('-').pop()),(state.counts.published||0)+' 项已入档'])$('#wf-summary').append(el('span',t));$('#wf-ocr').disabled=!state.capabilities.ocr;
 $('#wf-documents').replaceChildren();if(state.revision!=='research-000000')for(const [title,key]of [['查看研究档案','archive'],['资料解读','library'],['整理情况','assessment'],['结构化数据','data'],['本版更新','changes']]){const b=el('button',title);b.onclick=async()=>{try{const requestedProject=project;const r=await fetch('/api/research-document?project='+encodeURIComponent(requestedProject)+'&document='+key);if(!r.ok)throw Error('文档暂时读不到，请刷新重试');const text=await r.text();if(requestedProject!==project)return;$('#wf-document').textContent=text;$('#wf-document').hidden=false}catch(e){wfNotice(e.message)}};$('#wf-documents').append(b)}
 $('#wf-events').replaceChildren();for(const e of state.events.slice().reverse())$('#wf-events').append(el('p',new Date(e.at).toLocaleString('zh-CN')+' · '+e.actor+' · '+e.action+' · '+(e.reason||e.candidate_id||e.revision||'')));
 wfDescribeSource();wfRender();wfPublishPreview();wfStep(new URLSearchParams(location.search).get('wf_step')||1,false);document.dispatchEvent(new CustomEvent('research-ready',{detail:state}));
}
function wfValue(parent,value,operation){if(operation==='clear'){parent.append(el('p','撤回现有值，字段保留为空。','wf-value'));return}if(value===null)parent.append(el('p','待补充'));else if(typeof value!=='object')parent.append(el('p',String(value),'wf-value'));else if(Array.isArray(value)&&value.every(v=>typeof v!=='object')){const ul=el('ul');value.forEach(v=>ul.append(el('li',String(v))));parent.append(ul)}else{const d=el('details');d.append(el('summary','查看完整内容'),el('pre',JSON.stringify(value,null,2)));parent.append(d)}}
async function wfReview(c,decision,button){
 const pid=project;
 if(decision==='approved'){
  if(button)button.disabled=true;
  try{await wfPost('/api/review',{candidate_id:c.id,decision,actor:wfActor(),reason:'在核对卡片中选择确认采用，保留所附来源与适用条件。'});if(pid!==project)return;await wfLoad();if(pid!==project)return;wfStep(2);wfNotice('已确认采用，尚未更新档案。你可以继续核对，或去第 3 步预览本次更新。')}
  catch(e){wfNotice(e.message)}finally{if(button)button.disabled=false}return;
 }
 wfCandidate=c;$('#wf-review-target').textContent=wfLabel(c)+' · '+(c.title||c.record_id);$('#wf-decision').value=decision;wfDecision();$('#wf-review-dialog').showModal();
}
function wfDecision(){const approved=$('#wf-decision').value==='approved';$('#wf-review-reason').value=approved?'在核对卡片中选择确认采用，保留所附来源与适用条件。':'';$('#wf-review-reason').placeholder=approved?'可补充本次核对说明':'请说明还缺哪些资料，或为什么不采用'}
function wfRender(){
 if(!wfState)return;const filter=$('#wf-filter').value,sid=wfSelected();const source=wfFiles.find(x=>x.id===sid);const rows=wfState.candidates.filter(c=>(wfAll||!sid||c.source_id===sid)&&(!filter||c.status===filter));
 $('#wf-review-context').textContent=wfAll||!sid?'范围：全项目 · '+rows.length+' 项内容':'当前资料：'+(source?.name||'所选资料')+' · '+rows.length+' 项内容';$('#wf-all-sources').textContent=wfAll&&sid?'只看当前资料':'查看全项目内容';$('#wf-all-sources').disabled=!sid;
 const list=$('#wf-candidates');list.replaceChildren();
 if(!rows.length){const empty=el('div',undefined,'wf-empty');empty.append(el('strong',filter==='pending'?'这里暂时没有待确认的内容':'这个状态下还没有内容'),el('p',filter==='pending'?'先在第 1 步选资料并提取；如果已经确认完，可以去第 3 步查看待入档内容。':'可以切换其他状态，或返回第 1 步选择资料。'));list.append(empty)}
 if(rows.length>50)list.append(el('p','当前显示最近 50 项，请选择具体资料或状态缩小范围。','muted'));
 for(const c of rows.slice(-50).reverse()){
  const card=el('article',undefined,'wf-review-card');const head=el('div',undefined,'section-head');head.append(el('h4',wfLabel(c)),el('span',wfNames[c.status],'wf-state'));card.append(head,el('p',c.title||'未命名记录','muted'));
  const compare=el('div',undefined,'wf-compare'),proposed=el('div'),original=el('div');proposed.append(el('small',(c.status==='published'?'已入档的内容':c.status==='approved'?'已确认，待入档的内容':'本次提取的内容')+' · '+({source_statement:'资料陈述',ai_interpretation:'AI 解读',ai_hypothesis:'AI 假设'}[c.content_nature]||'待标注')));wfValue(proposed,c.value,c.operation);original.append(el('small','原文依据'),el('blockquote',c.quote),el('p',c.locator,'muted'));compare.append(proposed,original);card.append(compare);
  if(c.conditions)card.append(el('p','适用前提：'+c.conditions));if(c.limitations)card.append(el('p','使用限制：'+c.limitations));
  if(c.status!=='published'){const actions=el('div',undefined,'wf-main-actions');for(const [decision,label]of [['approved','确认采用'],['needs_more','还需补资料'],['rejected','不采用']]){const b=el('button',label,decision==='approved'?'primary':'');b.onclick=()=>wfReview(c,decision,b);actions.append(b)}card.append(actions)}
  const metadata=el('details',undefined,'wf-technical');metadata.append(el('summary','核对与来源记录'));if(c.reviewer)metadata.append(el('p','记录人：'+c.reviewer),el('p','处理说明：'+c.review_reason));metadata.append(el('p',c.record_id+'.'+c.field+' · '+c.source_id+' / '+c.chunk_id),el('p','提取方式：'+c.extraction_method));card.append(metadata);list.append(card);
 }
}
function wfApproved(){return wfState?.candidates.filter(c=>c.status==='approved')||[]}
function wfPublishPreview(){const rows=wfApproved();const files=new Set(rows.map(c=>c.source_id));$('#wf-publish').disabled=!rows.length||wfRunning?.kind==='publish';$('#wf-publish').textContent=wfRunning?.kind==='publish'?'正在保存…':rows.length?'预览 '+rows.length+' 项更新':'尚无已确认内容';$('#wf-publish-preview').replaceChildren(el('p',rows.length?'全项目有 '+rows.length+' 项已确认内容，来自 '+files.size+' 份资料。':'先在第 2 步对照原文确认内容，再回到这里保存。'));}
async function wfTask(action){
 const sid=wfSelected(),pid=project;if(!sid){wfNotice('请先选择一份资料。');return}if(wfRunning||wfSubmitting){wfNotice('还有一个整理任务在进行，可在“任务进度”查看。');return;}
 wfSubmitting=true;$('#wf-extract').disabled=true;
 try{const job=await wfPost('/api/'+action,{source_id:sid,actor:wfActor()});if(pid!==project)return;wfRunning={id:job.id,project:pid,source:sid,kind:action};$('#wf-extract').disabled=true;wfNotice('任务已开始：准备可读文字，再提取待确认内容。你可以继续查看资料，完成后这里会显示结果。');await jobs()}catch(e){if(pid===project)wfNotice(e.message)}finally{wfSubmitting=false;if(wfState)wfDescribeSource()}
}
$('#wf-source').onchange=()=>{wfAll=false;$('#wf-filter').value='pending';wfRemember();wfNotice('');wfDescribeSource();wfRender()};
$('#wf-open-file').onclick=()=>{const x=wfFiles.find(x=>x.id===wfSelected());if(x)detail(x)};
$('#wf-existing').onclick=()=>{const pending=wfState.candidates.some(c=>c.source_id===wfSelected()&&c.status==='pending');$('#wf-filter').value=pending?'pending':'';wfAll=false;wfRemember();wfRender();wfStep(2)};
$('#wf-all-sources').onclick=()=>{wfAll=!wfAll;wfRemember();wfRender()};document.querySelectorAll('[data-wf-step]').forEach(b=>b.onclick=()=>wfStep(b.dataset.wfStep));
$('#wf-filter').onchange=()=>{wfRemember();wfRender()};$('#wf-entity').onchange=wfFields;$('#wf-refresh').onclick=()=>Promise.all([wfLoad(),jobs()]).catch(e=>wfNotice(e.message));$('#wf-extract').onclick=()=>wfTask('process');$('#wf-ocr').onclick=()=>wfTask('ocr');
$('#wf-evidence').onclick=async()=>{try{const sid=wfSelected();if(!sid)throw Error('请先选择资料');const pid=project;const d=await api('/api/preview?project='+encodeURIComponent(pid)+'&source='+encodeURIComponent(sid));if(pid!==project)return;$('#wf-blocks').replaceChildren();for(const b of d.blocks){const div=el('div');div.append(el('strong',b.id+' · '+b.locator),el('p',b.text));$('#wf-blocks').append(div)}$('#wf-blocks-panel').open=true}catch(e){wfNotice(e.message)}};
$('#wf-propose').onsubmit=async e=>{e.preventDefault();const button=e.submitter;button.disabled=true;try{if(!wfSelected())throw Error('请先在第 1 步选择关联的资料');const entity=$('#wf-entity').value,field=$('#wf-field').value,definition=wfState.schema.entities.find(x=>x.key===entity).fields.find(x=>x.name===field);let value=$('#wf-value').value;if(['number','integer','boolean','object'].includes(definition.type)||definition.type.endsWith('_list'))value=JSON.parse(value);const candidate={entity,field,value,record_id:$('#wf-record').value.trim(),title:$('#wf-title').value,source_id:$('#wf-source').value,chunk_id:$('#wf-block').value.trim(),quote:$('#wf-quote').value,content_nature:$('#wf-nature').value,object:$('#wf-object').value,unit:$('#wf-unit').value,conditions:$('#wf-conditions').value,limitations:$('#wf-limits').value};await wfPost('/api/candidate',{actor:wfActor(),candidate});wfNotice('已加入待审核候选，尚未改变档案。');$('#wf-filter').value='pending';await wfLoad();wfStep(2)}catch(e){wfNotice(e.message)}finally{button.disabled=false}};
$('#wf-review-close').onclick=()=>$('#wf-review-dialog').close();$('#wf-decision').onchange=wfDecision;
$('#wf-review-form').onsubmit=async e=>{e.preventDefault();const button=e.submitter,pid=project;button.disabled=true;try{await wfPost('/api/review',{candidate_id:wfCandidate.id,decision:$('#wf-decision').value,actor:wfActor(),reason:$('#wf-review-reason').value});if(pid!==project)return;$('#wf-review-dialog').close();await wfLoad();wfNotice('处理决定已保存。确认采用的内容可在第 3 步预览并保存入档。');wfStep(2)}catch(e){$('#wf-review-target').textContent=e.message}finally{button.disabled=false}};
$('#wf-publish').onclick=async()=>{try{await wfLoad();const rows=wfApproved();if(!rows.length){wfNotice('目前没有待入档内容，请先核对。');return}wfPreviewIds=rows.map(c=>c.id).sort();$('#wf-publish-items').replaceChildren();for(const c of rows){const item=el('article',undefined,'wf-publish-item');item.append(el('strong',wfLabel(c)),el('p',c.title,'muted'));wfValue(item,c.value,c.operation);$('#wf-publish-items').append(item)}$('#wf-reason').value='采用已核对的 '+rows.length+' 项内容，更新研究档案。';$('#wf-publish-error').textContent='';$('#wf-publish-dialog').showModal()}catch(e){wfNotice(e.message)}};
$('#wf-publish-close').onclick=()=>$('#wf-publish-dialog').close();
$('#wf-publish-form').onsubmit=async e=>{e.preventDefault();const b=e.submitter,pid=project;b.disabled=true;try{const j=await wfPost('/api/publish',{actor:wfActor(),reason:$('#wf-reason').value.trim(),expected_candidate_ids:wfPreviewIds});if(pid!==project)return;wfRunning={id:j.id,project:pid,source:null,kind:'publish'};$('#wf-publish-dialog').close();wfPublishPreview();wfNotice('正在保存新研究版本，原资料和原版本保留。');await jobs()}catch(e){$('#wf-publish-error').textContent=e.message}finally{b.disabled=false}};
document.addEventListener('jobs-updated',async e=>{
 if(e.detail.project!==project)return;wfLastJobs=e.detail.jobs;if(wfState)wfDescribeSource();if(!wfRunning||wfRunning.project!==project)return;
 const j=e.detail.jobs.find(j=>j.id===wfRunning.id);if(!j||['queued','running'].includes(j.status))return;
 const completed=wfRunning;wfRunning=null;try{await wfLoad();if(e.detail.project!==project)return;if(j.status!=='completed'){wfNotice('这次处理未完成，原件已保留。请在“任务进度”查看原因并重试。');return}
 if(completed.kind==='publish'){wfStep(3);wfNotice('研究档案新版本已保存。可以查看本版更新；项目展示档案仍保留原版。');return}
 if(completed.source!==wfSelected())return;if(completed.kind==='ocr'){wfStep(1);wfNotice('文字识别完成，仍需核对识别结果。接下来可以提取待确认内容。');return}const rows=wfState.candidates.filter(c=>c.source_id===completed.source);const pending=rows.filter(c=>c.status==='pending');$('#wf-filter').value=pending.length?'pending':'';wfRemember();wfRender();wfStep(2);
 wfNotice(pending.length?'提取完成，有 '+pending.length+' 项内容等你对照原文确认。':rows.length?'处理完成，没有新增待确认内容。已有的整理记录保留在下面。':'没有自动提取到可确认的内容。原文已保存，这不代表资料没有价值；可先读原文，再请研究人员补充。');
 }catch(err){wfNotice(err.message)}
});
let wfLast='';setInterval(()=>{const key=project+'|'+$('#revision').textContent;if(wfLast!==key){wfLast=key;wfLoad().catch(e=>wfNotice(e.message))}},1500);
document.addEventListener('jobs-completed',()=>wfLoad().catch(e=>wfNotice(e.message)));
function wfChangeProject(){if(wfProject===project&&wfState)return;wfState=null;wfCandidate=null;wfRunning=null;wfAll=false;wfLastJobs=[];$('#wf-review-dialog').close();$('#wf-publish-dialog').close();$('#wf-document').hidden=true;for(const id of ['#wf-candidates','#wf-summary','#wf-blocks','#wf-events','#wf-documents','#wf-source'])$(id).replaceChildren();wfNotice('正在读取当前项目资料…');wfLast=project+'|'+$('#revision').textContent;wfLoad().then(()=>wfNotice('')).catch(e=>wfNotice(e.message))}
document.addEventListener('project-ready',wfChangeProject);document.addEventListener('project-switching',wfChangeProject);
addEventListener('popstate',()=>wfLoad().catch(e=>wfNotice(e.message)));wfStep(1,false);
