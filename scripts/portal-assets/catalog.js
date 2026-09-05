'use strict';
(async function(){
const $=id=>document.getElementById(id), params=new URLSearchParams(location.search);let items=[],page=1;const size=24;
$('query').value=params.get('q')||'';
function render(){const q=$('query').value.trim().toLowerCase(),level=$('level').value,year=$('year').value;
const found=items.filter(a=>(!level||a.level===level)&&(!year||String(a.year)===year)&&(!q||[a.name,a.unit,a.summary].join(' ').toLowerCase().includes(q)));
const pages=Math.max(1,Math.ceil(found.length/size));page=Math.min(page,pages);$('resultCount').textContent=`找到 ${found.length} 个项目 · 当前共收录 ${items.length} 项`;$('results').replaceChildren();
for(const a of found.slice((page-1)*size,page*size)){const card=document.createElement('a');card.className='project-card';card.href='/project/'+encodeURIComponent(a.slug)+'.html';const pic=document.createElement('div');pic.className='picture';if(a.cover){const im=document.createElement('img');im.src='/'+a.cover;im.alt=a.name;im.loading='lazy';im.addEventListener('error',()=>{im.remove();pic.textContent='好设计项目档案';});pic.append(im);}else pic.textContent='好设计项目档案';card.append(pic);for(const [tag,cls,text]of[['p','meta',a.year+' · '+a.level],['h3','',a.name],['p','unit',a.unit]]){const e=document.createElement(tag);e.className=cls;e.textContent=text;card.append(e);}$('results').append(card);}
if(!found.length){const e=document.createElement('p');e.className='empty';e.textContent='没有找到匹配项目。试试更短的关键词，或重置筛选。';$('results').append(e);}$('pageInfo').textContent=page+' / '+pages;$('prev').disabled=page<=1;$('next').disabled=page>=pages;
}
$('searchForm').addEventListener('submit',e=>{e.preventDefault();page=1;render();});for(const id of ['level','year'])$(id).addEventListener('change',()=>{page=1;render();});$('reset').addEventListener('click',()=>{$('query').value='';$('year').value='';$('level').value='';page=1;render();});for(const [id,d]of[['prev',-1],['next',1]])$(id).addEventListener('click',()=>{page+=d;render();$('search').scrollIntoView({block:'start'});});
try{const res=await fetch('/awards.json');if(!res.ok)throw new Error('读取失败');items=await res.json();render();}catch(e){$('resultCount').textContent='项目档案暂时未能加载，请刷新页面重试。';$('prev').disabled=$('next').disabled=true;}
})();
