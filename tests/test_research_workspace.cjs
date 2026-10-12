const fs=require('fs'),vm=require('vm'),assert=require('assert'),path=require('path');
const root=path.resolve(__dirname,'..'),elements=new Map(),storage=new Map();
const el=id=>{if(!elements.has(id))elements.set(id,{value:'',innerHTML:'',textContent:'',hidden:false});return elements.get(id)};
const payloads={'../knowledge-data/project-index.json':JSON.parse(fs.readFileSync(root+'/original-app/public/knowledge-data/project-index.json')),'data.json':JSON.parse(fs.readFileSync(root+'/extensions/public/industry-demo/data.json')),'shuanghuan-research.json':JSON.parse(fs.readFileSync(root+'/extensions/public/industry-demo/shuanghuan-research.json'))};
const ctx=vm.createContext({document:{getElementById:el,querySelectorAll:()=>[]},window:{addEventListener:()=>{}},location:{search:'?research=2025-04'},URLSearchParams,crypto:require('crypto').webcrypto,localStorage:{getItem:k=>storage.get(k)||null,setItem:(k,v)=>storage.set(k,v)},fetch:async u=>({ok:true,json:async()=>structuredClone(payloads[u])}),setTimeout});
vm.runInContext(fs.readFileSync(root+'/extensions/public/industry-demo/workspace.js','utf8'),ctx);
setTimeout(()=>{try{
assert.equal(el('research-choice').value,'2025-04');
vm.runInContext("save();createResearch();save()",ctx);
let saved=JSON.parse(storage.get('gooddesign.enterprise.v1'));assert.equal(saved.length,2);assert.equal(saved[1].research_source,'2025-04');assert.equal(saved[1].result,'');assert(saved[1].options.length===2);assert(saved[1].selected_cases.includes('2025-04'));
for(const c of payloads['shuanghuan-research.json'].cards){el('research-choice').value=c.id;vm.runInContext('createResearch();save()',ctx);assert(vm.runInContext('index.mechanisms.some(m=>m.project_id===current.selected_cases[0])',ctx));}
assert.equal(JSON.parse(storage.get('gooddesign.enterprise.v1')).length,8);
console.log('PASS: 6 direction imports, source availability, baseline alternatives, empty results, existing record preservation and persistence');
}catch(e){console.error(e);process.exitCode=1}},50);
