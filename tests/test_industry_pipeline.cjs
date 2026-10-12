const fs=require('fs'),vm=require('vm'),assert=require('assert'),path=require('path');
const root=path.resolve(__dirname,'..'),elements=new Map();
function makeEl(id){return {id,value:'',innerHTML:'',textContent:'',disabled:false,onclick:null,scrollIntoView(){},setAttribute(){},addEventListener(){}}}
const el=id=>{if(!elements.has(id))elements.set(id,makeEl(id));return elements.get(id)};
const data=JSON.parse(fs.readFileSync(root+'/extensions/public/industry-demo/data.json','utf8'));
let buttons=[];
const document={
  getElementById:el,
  querySelectorAll(sel){
    if(sel==='[data-step]')return buttons;
    if(sel==='[name=track]')return [];
    return [];
  },
  createElement(){return makeEl('created')}
};
const ctx=vm.createContext({document,fetch:async()=>({ok:true,json:async()=>data}),URL:{createObjectURL:()=>'',revokeObjectURL(){}},Blob,setTimeout,clearTimeout});
Object.defineProperty(el('steps'),'innerHTML',{set(v){this._html=v;buttons=[];for(const m of v.matchAll(/data-step=\"(\\d)\"/g)){buttons.push({dataset:{step:m[1]},onclick:null,setAttribute(){}})}},get(){return this._html||''}});
vm.runInContext(fs.readFileSync(root+'/extensions/public/industry-demo/app.js','utf8'),ctx);
setTimeout(()=>{try{
  assert(el('panel').innerHTML.includes('企业识别'));
  assert(el('flow').innerHTML.includes('企业主体已识别'));
  el('company').value='浙江双环传动机械股份有限公司';
  el('confirm').checked=true;
  vm.runInContext('next()',ctx);
  assert(el('panel').innerHTML.includes('调研与了解企业'));
  vm.runInContext('step=2;render()',ctx);
  assert(el('panel').innerHTML.includes('企业研究问题'));
  assert(el('panel').innerHTML.includes('问题 01'));
  assert(!el('panel').innerHTML.includes('好设计项目库如何服务企业研发'));
  vm.runInContext("track='process';step=3;render()",ctx);
  assert(el('panel').innerHTML.includes('匹配效果与知识融合'));
  assert(el('panel').innerHTML.includes('2025-04'));
  vm.runInContext('step=4;render()',ctx);
  assert(el('panel').innerHTML.includes('网页研究简报'));
  assert(el('panel').innerHTML.includes('下载网页报告'));
  assert(vm.runInContext('reportHtml',ctx).includes('双环传动精密传动创新机会研究报告'));
  assert(el('signal').innerHTML.includes('下载网页简报'));
  vm.runInContext('playing=true;paused=false;pauseAuto()',ctx);
  assert.equal(el('auto').textContent,'继续演示');
  assert(el('status').textContent.includes('已暂停'));
  vm.runInContext('resumeAuto();pauseAuto();stopAuto()',ctx);
  assert.equal(el('auto').textContent,'自动演示');
  console.log('PASS industry pipeline steps, evidence fusion and report stage');
}catch(e){console.error(e);process.exitCode=1}},30);
