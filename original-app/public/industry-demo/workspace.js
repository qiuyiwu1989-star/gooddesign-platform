'use strict';

const KEY='gooddesign.enterprise.v1';
const $=id=>document.getElementById(id);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let records=[],current,section=0,activeNode=0,index,demo,research,dirty=false,viewReady=false;
let zoom=.78,pan={x:62,y:92},playTimer=null,playStep=0;

const sections=[
  {name:'识别企业',hint:'主体、场景、公开事实',keys:['title','company','scope','baseline']},
  {name:'提出问题',hint:'把现场语言变成可研究问题',keys:['question','target','constraints','attempts']},
  {name:'选择方法',hint:'按问题触发方法，不把方法一次性堆满',kind:'options'},
  {name:'匹配证据',hint:'好设计项目和迁移依据',kind:'evidence'},
  {name:'生成方案',hint:'候选方向、验证路径、负责人',keys:['validation','metrics','owner']},
  {name:'沉淀报告',hint:'结果、边界、下一步',keys:['result','next_action']}
];
const canvasNodes=[
  {id:'company-context',type:'human',section:0,story:'01',lane:'主线',title:'双环企业画像',subtitle:'传动件 / 机器人关节 / 产业约束',role:'先让平台知道“谁来了、在什么业务边界里创新”。',run:'汇总公开资料、现场补充、产品线和不可变条件，形成可信的企业语境。',why:'没有企业语境，后面的案例匹配会变成泛泛推荐。',x:58,y:340},
  {id:'problem-framing',type:'human',section:1,story:'02',lane:'主线',title:'关键问题定义',subtitle:'机器人关节平台化如何落地',role:'把一句现场需求改写成可推理、可验证、可讨论的问题。',run:'锁定目标、基线、约束、已尝试方案和本轮只回答的一个问题。',why:'问题收窄后，方法才有选择依据。',x:318,y:340},
  {id:'method-router',type:'method',section:2,story:'03',lane:'选择器',title:'方法选择器',subtitle:'问题类型 → 方法链',role:'不是把所有方法铺开，而是判断当前问题应该调用哪几类方法。',run:'识别问题属于平台化、精密制造、可靠性、人机体验或商业转化，再给出方法调用顺序。',why:'双环当前演示聚焦“平台化 + 精密传动”，所以只点亮相关方法。',x:578,y:340},
  {id:'function-decompose',type:'method selected',section:2,story:'3A',lane:'已选择',title:'功能拆解',subtitle:'关节模块 / 接口 / 传动链',role:'当前第一优先方法：先拆系统结构，再谈方案。',run:'拆出动力输入、减速传动、轴承支撑、润滑密封、传感反馈、装配维护等模块。',why:'平台化问题本质上先是模块边界问题。',x:832,y:178},
  {id:'triz-conflict',type:'method selected',section:2,story:'3B',lane:'已选择',title:'TRIZ 矛盾',subtitle:'精度、寿命、成本、体积的取舍',role:'当前第二优先方法：把工程取舍抽象成矛盾。',run:'记录改善参数、恶化参数、冲突来源，并输出可讨论的解决方向。',why:'机器人关节常见难点是性能提升会带来制造、装配或成本代价。',x:832,y:340},
  {id:'cross-analogy',type:'method selected',section:2,story:'3C',lane:'已选择',title:'案例类比',subtitle:'从好设计项目借机制',role:'当前第三优先方法：从项目库找可迁移机制，不照搬产品。',run:'匹配高端装备、机器人、精密制造相关案例，提取结构机制、验证方式和价值表达。',why:'好设计项目库的价值在于“迁移机制”，不是简单找同类产品。',x:832,y:502},
  {id:'opportunity-scan',type:'method dormant',section:2,story:'备选',lane:'暂不展开',title:'机会分析',subtitle:'市场机会 / 价值缺口',role:'暂不作为主线展开，只在商业策略讨论时触发。',run:'当企业要做产品线规划或客户场景扩展时，再输出机会地图。',why:'明天演示先讲研发价值，避免把主线拉散。',x:1088,y:110},
  {id:'five-constructs',type:'method dormant',section:2,story:'备选',lane:'暂不展开',title:'五大构成评估',subtitle:'科技 / 人本 / 商业 / 文化 / 艺术',role:'作为方案成熟度检查器，放在报告前使用。',run:'检查方案是否只解决技术问题，还是能形成完整好设计表达。',why:'它适合收束，不适合一开始就放大。',x:1088,y:604},
  {id:'good-design-evidence',type:'evidence',section:3,story:'04',lane:'证据',title:'好设计证据',subtitle:'项目库 / 原文摘录 / 适用边界',role:'所有创新建议必须回到证据，说明来源和迁移边界。',run:'调用项目库、证据看台、摘录、迁移判断和待核实项。',why:'让企业看到平台不是凭空生成，而是在已有知识底座上推理。',x:1088,y:340},
  {id:'live-agent',type:'agent',section:3,story:'Agent',lane:'现场',title:'现场 Agent',subtitle:'把现场补充转成新判断',role:'现场 Agent 不是聊天机器人，而是研究转译器。',run:'把企业现场补充的约束、指标和反驳写回节点，标明哪些判断发生改变。',why:'演示时可以让对方感到“我的一句补充会改变推理路径”。',x:1348,y:178},
  {id:'solution-agent',type:'agent',section:4,story:'05',lane:'生成',title:'方案生成 Agent',subtitle:'候选方向 / 收益假设 / 未知项',role:'把已选方法和证据融合成少量候选方向。',run:'输出 2-3 张方向卡，每张都包含机制、收益、代价、未知项。',why:'候选方案必须少而清楚，方便现场讨论取舍。',x:1348,y:340},
  {id:'validation-plan',type:'validation',section:4,story:'验证',lane:'生成',title:'验证计划',subtitle:'小试、指标、负责人',role:'把创意约束到可试验、可评审、可复盘的行动。',run:'定义最小实验、对照组、KPI、负责人和通过门槛。',why:'企业创新必须落到验证，不然只是概念展示。',x:1348,y:502},
  {id:'report',type:'output',section:5,story:'06',lane:'产出',title:'研究报告',subtitle:'结论、证据、路线',role:'面向企业沟通，标明事实、假设和待核实边界。',run:'生成网页版研究报告和可下载材料。',why:'报告承接演示，方便会后继续推进。',x:1608,y:258},
  {id:'knowledge-base',type:'output',section:5,story:'沉淀',lane:'资产',title:'知识沉淀',subtitle:'项目库 / 方法库 / 经验库',role:'把一次项目沉淀成后续可复用的知识结构。',run:'回写企业问题、方法链路、证据关系和验证结果。',why:'平台越用越强，靠的是沉淀结构化过程，不只是保存结果。',x:1608,y:452}
];
const edges=[
  [0,1,'企业语境'],
  [1,2,'触发选择'],
  [2,3,'平台化优先'],
  [2,4,'矛盾识别'],
  [2,5,'案例迁移'],
  [2,6,'商业场景时触发'],
  [2,7,'报告收束时检查'],
  [3,8,'结构证据'],
  [4,8,'矛盾证据'],
  [5,8,'迁移证据'],
  [8,9,'现场补充'],
  [8,10,'融合生成'],
  [9,10,'修正判断'],
  [10,11,'转为验证'],
  [11,12,'形成报告'],
  [12,13,'回写资产'],
  [8,13,'证据关系沉淀']
];
const libraryGroups=[
  ['human','人输入节点','企业背景、目标、约束、判断'],
  ['method selected','已选择方法','功能拆解、TRIZ、案例类比'],
  ['method dormant','备选方法','机会分析、五大构成等按需触发'],
  ['evidence','证据节点','好设计项目、原文摘录、边界'],
  ['agent','AI Agent 节点','现场转译、匹配、生成'],
  ['validation','验证节点','实验、指标、责任人'],
  ['output','产出节点','报告、方案、知识沉淀']
];
const storySteps=[
  {title:'故事 01｜双环来了',text:'先识别企业背景和产业边界，不急着给方案。'},
  {title:'故事 02｜问题被收窄',text:'把“想做机器人关节”改写成“哪些接口和模块能平台化”。'},
  {title:'故事 03｜选择方法',text:'平台只点亮功能拆解、TRIZ 矛盾、案例类比三条方法链。'},
  {title:'故事 04｜证据进入推理',text:'从好设计项目库提取可迁移机制，并标出边界。'},
  {title:'故事 05｜生成候选方向',text:'现场 Agent 吸收补充条件，生成少量方向和验证计划。'},
  {title:'故事 06｜沉淀为报告',text:'形成研究报告，同时把路径沉淀回知识底座。'}
];
const demoStages=[
  {focus:'company-context',visible:['company-context'],msg:'01 先识别双环：画布只出现企业输入节点，避免一开始就堆方法。'},
  {focus:'problem-framing',visible:['company-context','problem-framing'],msg:'02 把现场表达收窄成一个可研究的问题：机器人关节平台化。'},
  {focus:'method-router',visible:['company-context','problem-framing','method-router'],msg:'03 进入方法选择器：系统先判断问题类型，再决定调用哪些方法。'},
  {focus:'function-decompose',visible:['company-context','problem-framing','method-router','function-decompose','triz-conflict','cross-analogy'],msg:'03A 只点亮本轮需要的三条方法：功能拆解、TRIZ 矛盾、案例类比。'},
  {focus:'good-design-evidence',visible:['company-context','problem-framing','method-router','function-decompose','triz-conflict','cross-analogy','good-design-evidence'],msg:'04 好设计证据进入推理：建议必须能回到项目库、摘录和边界。'},
  {focus:'live-agent',visible:['company-context','problem-framing','method-router','function-decompose','triz-conflict','cross-analogy','good-design-evidence','live-agent'],msg:'04A 现场 Agent 接收企业补充，把新约束写回节点关系。'},
  {focus:'solution-agent',visible:['company-context','problem-framing','method-router','function-decompose','triz-conflict','cross-analogy','good-design-evidence','live-agent','solution-agent','validation-plan'],msg:'05 生成少量候选方向，并同步给出验证计划，而不是生成一堆无法判断的想法。'},
  {focus:'report',visible:['company-context','problem-framing','method-router','function-decompose','triz-conflict','cross-analogy','good-design-evidence','live-agent','solution-agent','validation-plan','report','knowledge-base'],msg:'06 形成报告，同时把问题、方法链、证据关系沉淀回知识底座。'}
];
const fields={title:'课题名称',company:'企业主体',scope:'产品与任务',question:'本轮要解决的问题',baseline:'当前表现 / 基线',target:'希望改善什么',constraints:'不能改变的条件',attempts:'已经尝试的办法',improve:'希望改善的性能',worsen:'可能随之变差的性能',causality:'为什么存在这个取舍？有哪些证据？',method_notes:'方法选择理由 / 参数映射记录',validation:'验证步骤与对照方案',metrics:'评价指标与通过门槛',owner:'负责人',result:'实际结果与适用边界',next_action:'下一步行动'};

const defaultVisibleIds=new Set(['company-context','problem-framing','method-router','function-decompose','triz-conflict','cross-analogy','good-design-evidence','live-agent','solution-agent','validation-plan','report','knowledge-base']);
const lockedNodeIds=new Set(['company-context','problem-framing','method-router','report']);
canvasNodes.forEach(n=>{n.visible=defaultVisibleIds.has(n.id);n.locked=lockedNodeIds.has(n.id)});
const initialCanvasState=canvasNodes.map(n=>({id:n.id,x:n.x,y:n.y,visible:n.visible}));
const initialNodeCount=canvasNodes.length;
const initialEdgeCount=edges.length;
let coNodeSeq=0;
function visibleNodes(){return canvasNodes.filter(n=>n.visible!==false)}
function visibleNodeIds(){return new Set(visibleNodes().map(n=>n.id))}
function firstVisibleIndex(){const idx=canvasNodes.findIndex(n=>n.visible!==false);return idx<0?0:idx}
function ensureVisibleActive(){if(!canvasNodes[activeNode]||canvasNodes[activeNode].visible===false)activeNode=firstVisibleIndex()}

function nodeIndexById(id){return canvasNodes.findIndex(n=>n.id===id)}
function setVisibleByIds(ids){const allowed=new Set(ids);canvasNodes.forEach(n=>{n.visible=allowed.has(n.id)})}
function focusNodeSoft(id){const i=typeof id==='number'?id:nodeIndexById(id);const n=canvasNodes[i];if(!n)return;activeNode=i;section=n.section;zoom=.96;pan={x:Math.max(-1180,390-n.x*zoom),y:Math.max(-520,250-n.y*zoom)};viewReady=true;}
function applyDemoStage(i){const stage=demoStages[Math.min(i,demoStages.length-1)];if(!stage)return;setVisibleByIds(stage.visible);focusNodeSoft(stage.focus);render();message(stage.msg)}

function message(s){$('feedback').textContent=s}
function blank(){return {id:crypto.randomUUID(),schema_version:'0.1',title:'未命名课题',company:'',scope:'',question:'',baseline:'',target:'',constraints:'',attempts:'',improve:'',worsen:'',causality:'',method:'function',method_notes:'',selected_cases:[],options:[],validation:'',metrics:'',owner:'',result:'',next_action:'',revision:1,reviewed_revision:null,status:'草稿',updated_at:null}}
function mark(){current.revision++;dirty=true;refreshRevision();message('有未保存的修改。')}
function persist(){try{localStorage.setItem(KEY,JSON.stringify(records));dirty=false;message('已保存到此浏览器。建议导出备份。');return true}catch(e){message('本机保存失败，请立即导出备份。');return false}}
function save(){current.updated_at=new Date().toISOString();if(persist()){list();refreshRevision()}}
function refreshRevision(){$('revision').textContent=current.reviewed_revision===current.revision?'已记录本轮人工复核；仍需企业确认。':'当前节点待人工复核；修改条件不会自动生成新方案。'}
function list(){const sel=$('projects');sel.innerHTML=records.map(r=>`<option value="${esc(r.id)}">${esc(r.title||'未命名课题')}</option>`).join('');if(current)sel.value=current.id}
function edit(keys){return '<div class="inspector-fields">'+keys.map(k=>`<label><span>${fields[k]}</span><textarea data-field="${k}" maxlength="12000">${esc(current[k])}</textarea></label>`).join('')+'</div>'}
function statusOf(i){const s=sections[i];if(s.kind==='evidence')return current.selected_cases.length?'has':'empty';if(s.kind==='options')return current.options.length?'has':'empty';return s.keys.some(k=>String(current[k]||'').trim())?'has':'empty'}
function applyView(){
  const canvas=$('canvas');
  if(canvas&&canvas.style)canvas.style.transform=`translate(${pan.x}px,${pan.y}px) scale(${zoom})`;
}
function fitFlow(force){
  const viewport=$('canvas-viewport');
  if(!viewport||!viewport.clientWidth||(!force&&viewReady))return;
  const nodes=visibleNodes();
  if(!nodes.length)return;
  const minX=Math.min(...nodes.map(n=>n.x)),maxX=Math.max(...nodes.map(n=>n.x+230));
  const minY=Math.min(...nodes.map(n=>n.y)),maxY=Math.max(...nodes.map(n=>n.y+190));
  const vw=viewport.clientWidth,vh=viewport.clientHeight||640;
  const nextZoom=Math.max(.38,Math.min(.9,(vw-112)/(maxX-minX+112),(vh-176)/(maxY-minY+112)));
  zoom=Number(nextZoom.toFixed(2));
  pan={x:Math.round((vw-(maxX-minX)*zoom)/2-minX*zoom),y:Math.round((vh-(maxY-minY)*zoom)/2-minY*zoom+34)};
  viewReady=true;
  applyView();
}
function edgeHtml(edge,i){
  const [a,b,label]=edge;
  const from=canvasNodes[a],to=canvasNodes[b];
  if(!from||!to||from.visible===false||to.visible===false)return '';
  const x1=from.x+230,y1=from.y+78,x2=to.x,y2=to.y+78;
  const dx=x2-x1,dy=y2-y1,len=Math.sqrt(dx*dx+dy*dy),angle=Math.atan2(dy,dx)*180/Math.PI;
  const active=from.section===section||to.section===section;
  return `<i class="edge-line ${active?'edge-active':''} ${i>9?'edge-secondary':''}" style="left:${x1}px;top:${y1}px;width:${len}px;transform:rotate(${angle}deg)"><span>${esc(label)}</span></i>`;
}
function wireViewControls(){
  const zin=$('zoom-in'),zout=$('zoom-out'),reset=$('reset-view'),focus=$('focus-flow'),play=$('play-flow'),theme=$('theme-toggle'),remove=$('remove-node'),restore=$('restore-nodes');
  if(zin)zin.onclick=()=>{zoom=Math.min(1.8,Number((zoom+.1).toFixed(2)));applyView();message('画布已放大。')};
  if(zout)zout.onclick=()=>{zoom=Math.max(.38,Number((zoom-.1).toFixed(2)));applyView();message('画布已缩小。')};
  if(reset)reset.onclick=()=>{stopPlay();viewReady=false;fitFlow(true);message('画布视图已复位，当前节点都在首屏可见区域内。')};
  if(focus)focus.onclick=()=>{stopPlay();fitFlow(true);message('已聚焦完整创新流程。')};
  if(play)play.onclick=()=>togglePlay(play);
  if(theme)theme.onclick=()=>toggleTheme();
  if(remove)remove.onclick=()=>removeActiveNode();
  if(restore)restore.onclick=()=>restoreDefaultNodes();
}
function coCreate(kind){
  const input=$('co-create-input');
  const text=String(input?.value||'').trim();
  if(!text){message('先输入一条现场约束、想法或反驳，再生成共创节点。');input?.focus();return;}
  ensureVisibleActive();
  const active=canvasNodes[activeNode]||visibleNodes()[0]||canvasNodes[0];
  const meta={
    constraint:{title:'人的约束',lane:'共创约束',role:'现场参与者补充边界条件，AI 后续推理必须受它约束。',run:'把人的补充转成约束节点，并影响后续方法选择、方案生成和验证计划。',why:'来自现场人的判断，代表本轮推理必须纳入的真实边界。',label:'人的约束'},
    idea:{title:'人的想法',lane:'共创想法',role:'现场参与者提出一个可能方向，AI 帮它连接证据、方法和验证路径。',run:'把想法接入当前节点，后续可继续生成方案、证据匹配或验证节点。',why:'来自现场人的经验和直觉，是人机共创中需要被显性化的创新输入。',label:'人的想法'},
    challenge:{title:'人的反驳',lane:'共创反驳',role:'现场参与者质疑当前判断，AI 必须回到证据和约束重新说明。',run:'把反驳转成复核节点，标记当前链路需要重新判断或补证据。',why:'来自现场对 AI 输出的质疑，用于防止单向生成和过度推断。',label:'人的反驳'}
  }[kind]||{};
  const offset={constraint:{x:270,y:74},idea:{x:270,y:-74},challenge:{x:270,y:170}}[kind]||{x:270,y:74};
  const node={id:'co-'+(kind||'idea')+'-'+Date.now()+'-'+(++coNodeSeq),type:'human co-created',section:active.section,story:'共创',lane:meta.lane||'共创输入',title:meta.title||'人的输入',subtitle:text.slice(0,42)+(text.length>42?'…':''),role:meta.role||'现场参与者把新的判断加入画布。',run:meta.run||'把人的输入接到当前推理链路。',why:meta.why||'来自现场共创输入。',x:active.x+offset.x,y:Math.max(70,active.y+offset.y),visible:true,dynamic:true};
  const newIndex=canvasNodes.push(node)-1;
  edges.push([activeNode,newIndex,meta.label||'人的输入']);
  activeNode=newIndex;section=node.section;viewReady=false;
  current.next_action=(current.next_action?current.next_action+'\n':'')+'共创节点：'+node.title+'｜'+text;
  input.value='';mark();render();message('已生成共创节点：'+node.title+'，并连接到 '+active.title+'。');
}
function bindCoCreate(){
  document.querySelectorAll('[data-co-create]').forEach(b=>b.onclick=()=>coCreate(b.dataset.coCreate));
  const input=$('co-create-input');
  if(input)input.onkeydown=e=>{if((e.metaKey||e.ctrlKey)&&e.key==='Enter')coCreate('idea')};
}
function bindCanvas(){
  wireViewControls();
  bindCoCreate();
  document.querySelectorAll('[data-section]').forEach(b=>b.onclick=()=>{section=Number(b.dataset.section);render()});
  document.querySelectorAll('[data-node]').forEach(card=>{
    const i=Number(card.dataset.node);
    if(!card.addEventListener)return;
    card.onclick=()=>{activeNode=i;section=canvasNodes[i].section;render()};
    card.addEventListener('pointerdown',e=>{
      e.preventDefault();
      e.stopPropagation();
      const start={x:e.clientX,y:e.clientY,pos:{x:canvasNodes[i].x,y:canvasNodes[i].y}};
      if(card.setPointerCapture)card.setPointerCapture(e.pointerId);
      const move=ev=>{
        canvasNodes[i].x=start.pos.x+(ev.clientX-start.x)/zoom;
        canvasNodes[i].y=start.pos.y+(ev.clientY-start.y)/zoom;
        renderNodes();
      };
      const up=()=>{
        if(document.removeEventListener){
          document.removeEventListener('pointermove',move);
          document.removeEventListener('pointerup',up);
        }
      };
      if(document.addEventListener){
        document.addEventListener('pointermove',move);
        document.addEventListener('pointerup',up,{once:true});
      }
    });
  });
  const viewport=$('canvas-viewport');
  if(viewport&&viewport.addEventListener){
    viewport.onpointerdown=e=>{
      if(e.target&&e.target.closest&&e.target.closest('.node-card'))return;
      const start={x:e.clientX,y:e.clientY,pan:{...pan}};
      if(viewport.setPointerCapture)viewport.setPointerCapture(e.pointerId);
      const move=ev=>{pan={x:start.pan.x+ev.clientX-start.x,y:start.pan.y+ev.clientY-start.y};applyView()};
      const up=()=>{
        if(document.removeEventListener){
          document.removeEventListener('pointermove',move);
          document.removeEventListener('pointerup',up);
        }
      };
      if(document.addEventListener){
        document.addEventListener('pointermove',move);
        document.addEventListener('pointerup',up,{once:true});
      }
    };
    viewport.onwheel=e=>{
      if(!e.ctrlKey&&!e.metaKey)return;
      e.preventDefault();
      zoom=Math.max(.38,Math.min(1.8,Number((zoom+(e.deltaY<0?.08:-.08)).toFixed(2))));
      applyView();
    };
  }
  applyView();
}
function stopPlay(resetLabel=true){
  if(playTimer){clearInterval(playTimer);playTimer=null}
  const play=$('play-flow');
  if(play&&resetLabel)play.textContent='演示模式';
}
function focusNode(i){
  const n=canvasNodes[i];
  if(!n)return;
  if(n.visible===false){addNode(i,false)}
  focusNodeSoft(i);
  render();
  message('当前节点：'+n.title+'。'+n.role);
}
function togglePlay(button){
  if(playTimer){stopPlay(false);button.textContent='继续演示';message('演示已暂停，当前画布状态保留。');return}
  if(button.textContent==='继续演示'){
    button.textContent='暂停演示';
    message('演示继续，下一步会添加新的推理节点。');
  }else{
    playStep=0;
    button.textContent='暂停演示';
    applyDemoStage(playStep);
  }
  playTimer=setInterval(()=>{
    playStep++;
    if(playStep>=demoStages.length){stopPlay();fitFlow(true);message('演示完成：一次项目被沉淀为项目库、方法库和经验库。');return}
    applyDemoStage(playStep);
  },3600);
}
function addNode(i,rerender=true){
  const n=canvasNodes[i];
  if(!n)return;
  const active=canvasNodes[activeNode];
  if(n.visible===false){
    n.visible=true;
    if(active&&active.visible!==false){n.x=active.x+260;n.y=Math.max(104,active.y+34)}
    activeNode=i;section=n.section;viewReady=false;mark();
    message('已添加节点：'+n.title+'。');
  }else{activeNode=i;section=n.section;message('已选中节点：'+n.title+'。')}
  if(rerender)render();
}
function removeActiveNode(){
  const n=canvasNodes[activeNode];
  if(!n)return;
  if(n.locked){message('主线关键节点暂不移除，可通过拖动或缩放调整视图。');return}
  n.visible=false;
  activeNode=firstVisibleIndex();
  viewReady=false;
  mark();
  render();
  message('已从画布移除：'+n.title+'。可在节点库中添加回来。');
}
function restoreDefaultNodes(){
  canvasNodes.splice(initialNodeCount);
  edges.splice(initialEdgeCount);
  initialCanvasState.forEach(saved=>{const n=canvasNodes.find(x=>x.id===saved.id);if(n){n.x=saved.x;n.y=saved.y;n.visible=saved.visible}});
  activeNode=0;section=0;viewReady=false;mark();render();fitFlow(true);message('已复原为双环演示默认节点组合，共创节点已清空。');
}
function toggleTheme(){
  const body=document.body;
  if(!body||!body.classList)return;
  const light=body.classList.toggle('theme-light');
  body.classList.toggle('theme-dark',!light);
  const button=$('theme-toggle');
  if(button)button.textContent=light?'深色模式':'浅色模式';
  message(light?'已切换为浅色工作台。':'已切换为深色工作台。');
}
function renderLibrary(){
  const target=$('node-library');
  if(!target)return;
  const count=visibleNodes().length;
  const templates=canvasNodes.map((n,i)=>`<button class="template-card ${n.type} ${n.dynamic?'co-created':''} ${n.visible===false?'off':'on'}" data-template="${i}">
    <b>${esc(n.title)}</b><span>${esc(n.visible===false?'点击添加到画布':'已在画布 · 点击聚焦')}</span><small>${esc(n.subtitle)}</small>
  </button>`).join('');
  target.innerHTML='<div class="node-count"><b>'+count+'</b><span>个节点在画布上</span></div><div class="story-rail">'+storySteps.map((step,i)=>`<button data-story="${i}"><b>${esc(step.title)}</b><span>${esc(step.text)}</span></button>`).join('')+'</div><div class="template-bank"><p>NODE TEMPLATES</p>'+templates+'</div>'+libraryGroups.map(([type,title,desc])=>`<button class="library-card ${type}" data-library="${type}">
    <b>${esc(title)}</b><span>${esc(desc)}</span>
  </button>`).join('');
  document.querySelectorAll('[data-story]').forEach(b=>b.onclick=()=>{const i=Number(b.dataset.story);const map=[0,1,2,8,10,12];focusNode(map[i]??0)});
  document.querySelectorAll('[data-template]').forEach(b=>b.onclick=()=>addNode(Number(b.dataset.template)));
  document.querySelectorAll('[data-library]').forEach(b=>b.onclick=()=>{
    const n=canvasNodes.find(n=>n.visible!==false&&(n.type===b.dataset.library || n.type.split(' ').includes(b.dataset.library)))||canvasNodes.find(n=>n.type===b.dataset.library || n.type.split(' ').includes(b.dataset.library));
    if(n)addNode(canvasNodes.indexOf(n));
  });
}
function renderNodes(){
  ensureVisibleActive();
  const links=edges.map(edgeHtml).join('');
  const ids=visibleNodeIds();
  const nodes=canvasNodes.map((n,i)=>{
    if(!ids.has(n.id))return '';
    return `<button class="node-card ${n.type} ${n.dynamic?'co-created':''} ${i===activeNode?'active':''} ${statusOf(n.section)}" data-node="${i}" data-section="${n.section}" style="left:${n.x}px;top:${n.y}px">
    <span>${esc(n.story||n.type.toUpperCase())} · ${esc(n.lane||n.type.toUpperCase())}</span><b>${esc(n.title)}</b><small>${esc(n.subtitle)}</small><em>${esc(n.role)}</em>
  </button>`;
  }).join('');
  $('canvas').innerHTML=links+nodes;
  $('sections').innerHTML=sections.map((s,i)=>`<button data-section="${i}" aria-current="${i===section}"><span>0${i+1}</span>${esc(s.name)}</button>`).join('');
  renderLibrary();
  bindCanvas();
  setTimeout(()=>fitFlow(false),0);
}
function nodeContext(){
  ensureVisibleActive();
  const n=canvasNodes[activeNode]||visibleNodes().find(n=>n.section===section)||visibleNodes()[0]||canvasNodes[0];
  return `<div class="node-context ${esc(n.type)}"><p class="label">ACTIVE NODE · ${esc(n.story||n.type.toUpperCase())} · ${esc(n.lane||'')}</p><h2>${esc(n.title)}</h2><p>${esc(n.role)}</p>${n.dynamic?'<div class="co-created-note">现场共创节点 · 可继续编辑、移除或生成下游节点</div>':''}<dl><div><dt>为什么到这里</dt><dd>${esc(n.why||'根据当前项目上下文进入该节点。')}</dd></div><div><dt>输入</dt><dd>${esc(n.subtitle)}</dd></div><div><dt>节点运行</dt><dd>${esc(n.run||'根据当前项目上下文运行该节点。')}</dd></div><div><dt>人的工作</dt><dd>判断目标、约束、取舍和可信度。</dd></div><div><dt>AI 的工作</dt><dd>整理证据、调用方法、生成可复核的下一步。</dd></div></dl><div class="node-mini-actions"><button id="inspect-run">模拟运行</button><button id="accept-node">接受输出</button><button id="reject-node">标记待复核</button><button id="branch-node">生成下游节点</button></div></div>`;
}
function evidenceHtml(){
  return `<h2>证据匹配节点</h2><p>这里不是让用户填表，而是选择哪些证据对象进入当前课题。证据来自证据看台，同步保留来源、摘录、平台解读和适用边界。</p>`+
  index.mechanisms.map(m=>{
    const p=index.projects.find(p=>p.id===m.project_id)||{name:m.project_id,year:'',award:'',project_url:'/project/'+m.project_id+'.html'};
    return `<article class="node-evidence"><label><input type="checkbox" data-case="${esc(m.project_id)}" ${current.selected_cases.includes(m.project_id)?'checked':''}> 纳入当前课题</label><h3><a href="${esc(p.project_url)}" target="_blank" rel="noopener">${esc(p.name)}</a></h3><p class="metadata">${esc(p.year)} · ${esc(p.award)} · 库内档案 / 平台假设</p><details><summary>来源与边界</summary><blockquote>${esc(m.excerpt)}</blockquote><p>${esc(m.analysis)}</p></details></article>`;
  }).join('');
}
function optionsHtml(){
  const selected=canvasNodes.filter(n=>n.type.includes('selected')&&n.visible!==false).map(n=>`<article class="method-card selected"><strong>${esc(n.title)}</strong><span>${esc(n.subtitle)}</span><p>${esc(n.why)}</p></article>`).join('');
  const dormant=canvasNodes.filter(n=>n.type.includes('dormant')).map(n=>`<article class="method-card dormant"><strong>${esc(n.title)}</strong><span>${esc(n.visible===false?'节点库中 · 可添加':'已在画布')} · ${esc(n.subtitle)}</span><p>${esc(n.why)}</p></article>`).join('');
  return `<h2>方法选择节点</h2><p>当前不是展示全部方法库，而是演示平台如何根据双环问题选择一条方法链：先拆结构，再识别矛盾，再找案例迁移。其他方法保留在备选区，等问题变化时再触发。</p><div class="method-router"><div><b>问题信号</b><span>机器人关节平台化、精密传动、接口复用、可靠性验证</span></div><div><b>选择逻辑</b><span>平台化问题优先功能拆解；性能取舍进入 TRIZ；好设计库负责跨案例迁移。</span></div></div><div class="method-grid"><section><h3>本轮点亮的方法</h3>${selected}</section><section><h3>暂不展开的方法</h3>${dormant}</section></div><label>当前主方法 <select id="method"><option value="function">功能 / 模块化分析</option><option value="triz">TRIZ 技术矛盾</option><option value="case">案例类比</option></select></label>`+
  edit(['improve','worsen','causality','method_notes'])+
  current.options.map((o,i)=>`<article class="node-option"><h3>候选方向 ${i+1}</h3><div class="inspector-fields">${[['title','方向名称'],['mechanism','迁移方式 / 依据'],['benefit','预期收益（假设）'],['cost','代价与约束'],['unknown','关键未知项']].map(([k,l])=>`<label><span>${l}</span><textarea data-option="${i}" data-key="${k}" maxlength="12000">${esc(o[k])}</textarea></label>`).join('')}</div></article>`).join('')+
  '<div class="node-actions"><button id="add-option">增加候选方向</button><button id="review">记录人工复核</button></div>';
}
function render(){
  list();
  $('workspace').hidden=false;
  refreshRevision();
  renderNodes();
  const s=sections[section];
  let html=nodeContext()+`<p class="label">WORK PANEL 0${section+1}</p><h2>${esc(s.name)}</h2><p>${esc(s.hint)}</p>`;
  if(s.kind==='evidence')html=evidenceHtml();
  else if(s.kind==='options')html=optionsHtml();
  else html+=edit(s.keys);
  if(current.analysis_raw)html+=`<details class="analysis-raw"><summary>现场研究原始分析 · ${esc(current.analysis_mode||'待复核')}</summary><p>这是模型或预置分析，不是试验结果；请审核后整理到对应节点。</p><pre>${esc(current.analysis_raw)}</pre></details>`;
  html+='<div class="node-actions"><button id="resume-live">保存并继续在线研究</button></div>';
  $('content').innerHTML=html;
  $('resume-live').onclick=()=>{current.updated_at=new Date().toISOString();if(persist())location.href='live.html?resume='+encodeURIComponent(current.id)};
  document.querySelectorAll('[data-field]').forEach(e=>e.oninput=()=>{current[e.dataset.field]=e.value;mark();renderNodes()});
  document.querySelectorAll('[data-option]').forEach(e=>e.oninput=()=>{current.options[Number(e.dataset.option)][e.dataset.key]=e.value;mark();renderNodes()});
  document.querySelectorAll('[data-case]').forEach(e=>e.onchange=()=>{current.selected_cases=e.checked?[...new Set([...current.selected_cases,e.dataset.case])]:current.selected_cases.filter(x=>x!==e.dataset.case);mark();renderNodes()});
  if($('method')){$('method').value=current.method;$('method').onchange=e=>{current.method=e.target.value;mark()}}
  if($('add-option'))$('add-option').onclick=()=>{current.options.push({title:'',mechanism:'',benefit:'',cost:'',unknown:''});mark();render()};
  if($('review'))$('review').onclick=()=>{current.reviewed_revision=current.revision;dirty=true;refreshRevision();message('复核记录待保存；工程验证仍需另行开展。')};
  if($('inspect-run'))$('inspect-run').onclick=()=>{const n=canvasNodes[activeNode];message('正在模拟运行节点：'+(n?n.title:'当前节点')+'。输入、处理、输出会在右侧记录。')};
  if($('accept-node'))$('accept-node').onclick=()=>{current.reviewed_revision=current.revision;dirty=true;refreshRevision();message('已接受当前节点输出，仍需企业真实数据验证。')};
  if($('reject-node'))$('reject-node').onclick=()=>{current.reviewed_revision=null;dirty=true;refreshRevision();message('已标记为待复核：该节点输出不会直接进入最终结论。')};
  if($('branch-node'))$('branch-node').onclick=()=>{const pool=canvasNodes.findIndex(n=>n.visible===false&&!n.locked);if(pool>=0)addNode(pool);else message('当前没有可自动添加的模板节点。')};
}
function create(sample){
  if(dirty&&!persist())return;
  current=blank();
  if(sample){
    const t=demo.tracks.find(t=>t.id==='module');
    Object.assign(current,{title:'双环 · 机器人关节平台化（演示假设）',company:'浙江双环传动机械股份有限公司（演示）',scope:t.title,question:t.question,target:'探索可复用的关节配置与接口',constraints:'待企业补充：'+t.missing,selected_cases:[...t.cases],validation:t.experiment,metrics:t.metrics,next_action:'请企业工程师确认具体任务、基线和不可变条件。',options:[{title:'统一核心接口与配置规则',mechanism:t.bridge,benefit:'探索降低重复集成工作的可能性；未验证',cost:'需检查不同工况的性能约束和适配成本',unknown:t.missing},{title:'按任务工况划分模块族',mechanism:'平台研究假设：结合系统工况与模块化视角划分配置边界',benefit:'探索适配性与通用性之间的取舍；未验证',cost:'可能增加模块种类与维护工作',unknown:'任务分类、需求差异和允许的模块种类'}]});
  }
  records.push(current);section=0;dirty=true;render();message('新课题已创建，尚未保存。');
}
function createResearch(){
  if(dirty&&!persist())return;
  const c=research.cards.find(c=>c.id===$('research-choice').value);if(!c)return;
  current=blank();
  Object.assign(current,{title:'双环 · '+c.title+'（待确认）',company:'浙江双环传动机械股份有限公司（研究样例）',scope:c.title,question:c.question,baseline:'待企业填写，未提供实测数据',target:c.mechanism,constraints:'待企业确认：'+c.missing,method:'function',method_notes:'方法选择逻辑：平台化问题优先功能拆解；性能取舍进入 TRIZ；项目库负责机制迁移。'+c.limit,selected_cases:[c.id],validation:c.experiment,metrics:c.metrics,next_action:'补齐企业条件，确认对象与指标；未确认前不作工艺实施。',research_source:c.id,options:[{title:'保留现有方案作为对照',mechanism:'以企业当前方案及实测记录为基线，待补充。',benefit:'建立可比较基准',cost:'需整理现工艺与测量记录',unknown:c.missing},{title:c.title,mechanism:c.mechanism,benefit:'平台提出的潜在价值：'+c.fit,cost:'尚需核算工装、检测、集成及试验成本',unknown:c.limit}]});
  records.push(current);section=2;dirty=true;render();message('已从证据对象生成课题节点，原有课题保留；请编辑并保存。');
}
$('start-research').onclick=createResearch;
$('save').onclick=save;$('create').onclick=()=>create(false);$('sample').onclick=()=>create(true);
$('projects').onchange=e=>{const id=e.target.value;if(dirty&&!persist()){list();return}current=records.find(r=>r.id===id);section=0;render()};
$('export').onclick=()=>{const payload={...current,exported_at:new Date().toISOString(),evidence:index.mechanisms.filter(m=>current.selected_cases.includes(m.project_id))};const url=URL.createObjectURL(new Blob([JSON.stringify(payload,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='好设计-企业课题-'+current.id+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);message('已导出当前课题，包含选中案例的来源。')};
window.addEventListener('beforeunload',e=>{if(dirty){e.preventDefault();e.returnValue=''}});
function valid(r){return r&&typeof r.id==='string'&&r.schema_version==='0.1'&&typeof r.title==='string'&&Array.isArray(r.selected_cases)&&r.selected_cases.every(x=>typeof x==='string')&&Array.isArray(r.options)&&r.options.every(x=>x&&typeof x==='object')&&Number.isInteger(r.revision)}
async function init(){
  document.querySelectorAll('.workspace-toolbar button').forEach(b=>b.disabled=true);
  try{
    [index,demo,research]=await Promise.all(['../knowledge-data/project-index.json','data.json','shuanghuan-research.json'].map(async url=>{const r=await fetch(url);if(!r.ok)throw Error('资料加载失败');return r.json()}));
    const mapped=research.cards.map(c=>({id:'mechanism-'+c.id,project_id:c.id,source:c.source,excerpt:c.excerpt,analysis:c.mechanism+' 适用边界：'+c.limit,analysis_status:'platform_hypothesis',review_status:'pending_expert_review',triz_mapping:null,validation_result:null}));
    index.mechanisms=[...index.mechanisms.filter(m=>!mapped.some(n=>n.project_id===m.project_id)),...mapped];
    $('research-choice').innerHTML=research.cards.map(c=>`<option value="${esc(c.id)}">${esc(c.title)}</option>`).join('');
    const requested=new URLSearchParams(location.search).get('research');if(research.cards.some(c=>c.id===requested))$('research-choice').value=requested;
    try{const stored=JSON.parse(localStorage.getItem(KEY)||'[]');if(!Array.isArray(stored)||!stored.every(valid))throw Error('invalid');records=stored}catch(e){message('本机存储不可读或格式不兼容；原数据未覆盖，请先导出或检查浏览器存储。');return}
    const requestedTask=new URLSearchParams(location.search).get('task');
    if(records.length){
      current=records.find(r=>r.id===requestedTask)||null;
      if(!current&&requestedTask){create(true);message('这是共享课题链接，但本机没有对应课题记录；已载入双环演示样例。')}
      else{current=current||records[0];render()}
    }else create(true);
    document.querySelectorAll('.workspace-toolbar button').forEach(b=>b.disabled=false);
  }catch(e){message('资料加载失败，请刷新重试。课题数据未改动。')}
}
init();
