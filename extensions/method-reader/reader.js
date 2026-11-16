(()=>{'use strict';
const search=document.querySelector('#method-search');
let category='';
if(search){
 const cards=[...document.querySelectorAll('.method-card')], buttons=[...document.querySelectorAll('[data-category]')];
 const url=new URL(location.href), requested=url.searchParams.get('category')||'';
 category=buttons.some(x=>x.dataset.category===requested)?requested:'';
 search.value=url.searchParams.get('q')||'';
 function filter(syncURL=true){
  const q=search.value.trim().toLowerCase();let count=0;
  cards.forEach(c=>{c.hidden=!!((category&&c.dataset.cat!==category)||(q&&!c.dataset.search.includes(q)));if(!c.hidden)count++});
  buttons.forEach(x=>x.setAttribute('aria-pressed',String(x.dataset.category===category)));
  const active=buttons.find(x=>x.dataset.category===category)?.textContent||'全部';
  document.querySelector('#search-status').textContent=`${active} · ${count} 项方法与专题`;
  document.querySelector('#empty').hidden=count!==0;
  document.querySelector('.mh-clear').hidden=!search.value;
  document.querySelector('.mh-reset').hidden=!category&&!search.value;
  if(syncURL){const u=new URL(location.href);search.value.trim()?u.searchParams.set('q',search.value.trim()):u.searchParams.delete('q');category?u.searchParams.set('category',category):u.searchParams.delete('category');history.replaceState(null,'',u.pathname+u.search+u.hash)}
 }
 function reset(){category='';search.value='';filter();search.focus()}
 search.addEventListener('input',()=>filter());
 search.addEventListener('keydown',e=>{if(e.key==='Escape'&&search.value){e.preventDefault();search.value='';filter()}});
 search.closest('form').addEventListener('submit',e=>e.preventDefault());
 buttons.forEach(b=>b.addEventListener('click',()=>{category=b.dataset.category;filter()}));
 document.querySelector('.mh-clear').addEventListener('click',()=>{search.value='';filter();search.focus()});
 document.querySelectorAll('[data-reset-filters]').forEach(b=>b.addEventListener('click',reset));
 window.addEventListener('popstate',()=>{const u=new URL(location.href);search.value=u.searchParams.get('q')||'';category=buttons.some(b=>b.dataset.category===u.searchParams.get('category'))?u.searchParams.get('category'):'';filter(false)});
 filter(false);
}
document.querySelectorAll('.copy').forEach(b=>b.addEventListener('click',async()=>{const box=b.closest('.code'),text=box.querySelector('code').textContent;try{await navigator.clipboard.writeText(text);box.querySelector('[role=status]').textContent='已复制'}catch{const selection=window.getSelection(),r=document.createRange();r.selectNodeContents(box.querySelector('code'));selection.removeAllRanges();selection.addRange(r);box.querySelector('[role=status]').textContent='浏览器未允许自动复制，已选中文本，请按 Ctrl/Cmd+C'}}));document.querySelectorAll('.method-detail>.contents a[href^="#"],.method-detail .flow a[href^="#"]').forEach(a=>a.addEventListener('click',()=>{const target=document.getElementById(a.getAttribute('href').slice(1));if(target?.matches('details.step'))target.open=true;document.querySelectorAll('.method-detail>.contents a').forEach(x=>x.removeAttribute('aria-current'));a.setAttribute('aria-current','location')}));window.addEventListener('beforeprint',()=>document.querySelectorAll('details').forEach(d=>d.open=true));})();
