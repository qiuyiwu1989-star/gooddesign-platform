'use strict';
let wfState=null,wfProject='',wfCandidate=null,wfBusy=false;const wfNames={pending:'待审核',approved:'已通过',needs_more:'待补证',rejected:'已驳回',published:'已发布'};
function wfNotice(t){$('#wf-notice').textContent=t}function wfActor(){const a=$('#wf-actor').value.trim();if(!a)throw Error('请填写操作者');return a}
async function wfPost(path,body){if(wfProject!==project||!wfState)throw Error('项目资料仍在切换，请稍候再操作');return api(path+'?project='+encodeURIComponent(project),{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)})}
function wfFields(){const e=wfState?.schema.entities.find(e=>e.key===$('#wf-entity').value);$('#wf-field').replaceChildren();for(const f of e?.fields||[]){const o=el('option',f.label);o.value=f.name;$('#wf-field').append(o)}}
async function wfLoad(){const pid=project;const [state,list]=await Promise.all([api('/api/research?project='+encodeURIComponent(pid)),api('/api/files?project='+encodeURIComponent(pid))]);if(project!==pid)return;wfState=state;wfProject=pid;const selected=$('#wf-source').value;$('#wf-source').replaceChildren();for(const x of list.files.filter(x=>x.kind!=='source_reference')){const o=el('option',x.name);o.value=x.id;$('#wf-source').append(o)}if([...$('#wf-source').options].some(x=>x.value===selected))$('#wf-source').value=selected;const entity=$('#wf-entity').value;$('#wf-entity').replaceChildren();for(const e of state.schema.entities){const o=el('option',e.label);o.value=e.key;$('#wf-entity').append(o)}if(entity)$('#wf-entity').value=entity;wfFields();$('#wf-summary').replaceChildren();for(const t of ['档案版本 '+Number(state.revision.split('-').pop()),state.source_count+' 份项目资料',state.needs_ocr.length+' 份待识别文字',state.ocr_completed+' 份已识别',(state.counts.pending||0)+' 项待审核',(state.counts.approved||0)+' 项待发布'])$('#wf-summary').append(el('span',t));$('#wf-ocr').disabled=!state.capabilities.ocr;$('#wf-documents').replaceChildren();if(state.revision!=='research-000000')for(const [title,key]of [['项目档案','archive'],['资料与解读','library'],['档案评估','assessment'],['结构化 JSON','data'],['本版差异','changes']]){const b=el('button',title);b.onclick=async()=>{try{const requestedProject=project;const r=await fetch('/api/research-document?project='+encodeURIComponent(requestedProject)+'&document='+key);if(!r.ok)throw Error('文档读取失败');const text=await r.text();if(requestedProject!==project)return;$('#wf-document').textContent=text;$('#wf-document').hidden=false}catch(e){wfNotice(e.message)}};$('#wf-documents').append(b)}$('#wf-events').replaceChildren();for(const e of state.events.slice().reverse())$('#wf-events').append(el('p',new Date(e.at).toLocaleString('zh-CN')+' · '+e.actor+' · '+e.action+' · '+(e.reason||e.candidate_id||e.revision||'')));wfRender();document.dispatchEvent(new CustomEvent('research-ready',{detail:state}))}
function wfRender(){
 if(!wfState)return;
 const state=$('#wf-filter').value,rows=wfState.candidates.filter(c=>!state||c.status===state);
 $('#wf-candidates').replaceChildren();
 if(!rows.length)$('#wf-candidates').append(el('p','这里暂无内容。可选择一份资料开始提炼，或补充带依据的字段。','muted'));
 for(const c of rows.slice(-50).reverse()){
  const definition=wfState.schema.entities.find(e=>e.key===c.entity)?.fields.find(f=>f.name===c.field);
  const label=definition?.label||'研究字段';const card=el('details',undefined,'wf-candidate');
  const summary=el('summary');summary.append(el('span',label,'wf-field-name'),el('span',wfNames[c.status],'wf-state'),el('small',c.title||'未命名记录','wf-record-title'));card.append(summary);
  const content=el('div',undefined,'wf-candidate-body');content.append(el('p',({'source_statement':'原文事实',ai_interpretation:'AI 解读',ai_hypothesis:'AI 假设'}[c.content_nature]),'wf-nature'));
  if(c.value===null)content.append(el('p','待补充'));
  else if(typeof c.value!=='object')content.append(el('p',String(c.value),'wf-value'));
  else if(Array.isArray(c.value)&&c.value.every(v=>typeof v!=='object')){const list=el('ul');c.value.forEach(v=>list.append(el('li',String(v))));content.append(list)}
  else{const data=el('details');data.append(el('summary','查看完整字段内容'),el('pre',JSON.stringify(c.value,null,2)));content.append(data)}
  const source=el('details',undefined,'wf-source-evidence');source.append(el('summary','查看原文依据'),el('blockquote',c.quote),el('p',c.locator,'muted'));content.append(source);
  if(c.conditions)content.append(el('p','适用前提：'+c.conditions));if(c.limitations)content.append(el('p','使用限制：'+c.limitations));
  if(c.reviewer)content.append(el('p','审核：'+c.reviewer+' · '+c.review_reason));
  if(c.status!=='published'){const b=el('button','审核这一项');b.onclick=()=>{wfCandidate=c;$('#wf-review-target').textContent=label+' · '+(c.title||c.record_id);$('#wf-review-reason').value='';$('#wf-review-dialog').showModal()};content.append(b)}
  const metadata=el('details',undefined,'wf-technical');metadata.append(el('summary','编号与整理记录'),el('p',c.record_id+'.'+c.field+' · '+c.source_id+' / '+c.chunk_id),el('p','提取方式：'+c.extraction_method));content.append(metadata);
  card.append(content);$('#wf-candidates').append(card);
 }
}

async function wfTask(action){if(wfBusy)return;wfBusy=true;try{const sid=$('#wf-source').value;if(!sid)throw Error('请先选择资料');await wfPost('/api/'+action,{source_id:sid,actor:wfActor()});wfNotice('任务已进入队列，可在“处理记录”查看进度。完成后会更新研究状态。');await jobs();setTimeout(()=>wfLoad().catch(e=>wfNotice(e.message)),2000)}catch(e){wfNotice(e.message)}finally{wfBusy=false}}
$('#wf-entity').onchange=wfFields;$('#wf-filter').onchange=wfRender;$('#wf-refresh').onclick=()=>wfLoad().catch(e=>wfNotice(e.message));$('#wf-ocr').onclick=()=>wfTask('ocr');$('#wf-extract').onclick=()=>wfTask('extract');$('#wf-evidence').onclick=async()=>{try{const sid=$('#wf-source').value;if(!sid)throw Error('请先选择资料');const requestedProject=project;const d=await api('/api/preview?project='+encodeURIComponent(requestedProject)+'&source='+encodeURIComponent(sid));if(requestedProject!==project)return;$('#wf-blocks').replaceChildren();for(const b of d.blocks){const div=el('div');div.append(el('strong',b.id+' · '+b.locator),el('p',b.text));$('#wf-blocks').append(div)}$('#wf-blocks-panel').open=true}catch(e){wfNotice(e.message)}};
$('#wf-propose').onsubmit=async e=>{e.preventDefault();const button=e.submitter;button.disabled=true;try{const entity=$('#wf-entity').value,field=$('#wf-field').value,definition=wfState.schema.entities.find(x=>x.key===entity).fields.find(x=>x.name===field);let value=$('#wf-value').value;if(['number','integer','boolean','object'].includes(definition.type)||definition.type.endsWith('_list'))value=JSON.parse(value);const candidate={entity,field,value,record_id:$('#wf-record').value.trim(),title:$('#wf-title').value,source_id:$('#wf-source').value,chunk_id:$('#wf-block').value.trim(),quote:$('#wf-quote').value,content_nature:$('#wf-nature').value,object:$('#wf-object').value,unit:$('#wf-unit').value,conditions:$('#wf-conditions').value,limitations:$('#wf-limits').value};await wfPost('/api/candidate',{actor:wfActor(),candidate});wfNotice('已加入待审核候选，尚未改变档案。');$('#wf-filter').value='pending';await wfLoad()}catch(e){wfNotice(e.message)}finally{button.disabled=false}};
$('#wf-review-close').onclick=()=>$('#wf-review-dialog').close();$('#wf-review-form').onsubmit=async e=>{e.preventDefault();e.submitter.disabled=true;try{await wfPost('/api/review',{candidate_id:wfCandidate.id,decision:$('#wf-decision').value,actor:wfActor(),reason:$('#wf-review-reason').value});$('#wf-review-dialog').close();wfNotice('审核结果已保存；通过的内容需再发布才进入档案版本。');await wfLoad()}catch(e){wfNotice(e.message);$('#wf-review-target').textContent=e.message}finally{e.submitter.disabled=false}};
$('#wf-publish').onclick=async()=>{try{const reason=$('#wf-reason').value.trim();if(!reason)throw Error('请填写版本说明');await wfPost('/api/publish',{actor:wfActor(),reason});wfNotice('发布任务已提交，完成后可在这里查看三份文档、结构化数据与版本差异。');await jobs();setTimeout(()=>wfLoad().catch(e=>wfNotice(e.message)),1500)}catch(e){wfNotice(e.message)}};
let wfLast='';setInterval(()=>{const key=project+'|'+$('#revision').textContent;if(wfLast!==key){wfLast=key;wfLoad().catch(e=>wfNotice(e.message))}},1500);

document.addEventListener('jobs-completed',()=>wfLoad().catch(e=>wfNotice(e.message)));

function wfChangeProject(){
 if(wfProject===project&&wfState)return;
 wfState=null;wfCandidate=null;$('#wf-review-dialog').close();$('#wf-document').hidden=true;
 for(const id of ['#wf-candidates','#wf-summary','#wf-blocks','#wf-events','#wf-documents','#wf-source'])$(id).replaceChildren();
 wfNotice('正在读取当前项目的研究资料…');wfLast=project+'|'+$('#revision').textContent;
 wfLoad().then(()=>wfNotice('')).catch(e=>wfNotice(e.message));
}
document.addEventListener('project-ready',wfChangeProject);
document.addEventListener('project-switching',wfChangeProject);
