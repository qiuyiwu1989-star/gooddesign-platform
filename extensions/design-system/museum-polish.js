(()=>{'use strict';
const ticker=document.querySelector('.ticker');
if(ticker&&!ticker.querySelector('.ticker-control')){
 const button=document.createElement('button');button.type='button';button.className='ticker-control';
 const reduce=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
 function set(paused){ticker.dataset.paused=String(paused);button.textContent=paused?'播放':'暂停';button.setAttribute('aria-label',paused?'播放展品名称滚动':'暂停展品名称滚动');button.setAttribute('aria-pressed',String(paused));}
 set(reduce);if(reduce){button.disabled=true;button.textContent='静止';button.setAttribute('aria-label','已按减少动态偏好停止滚动');}
 button.addEventListener('click',()=>set(ticker.dataset.paused!=='true'));ticker.append(button);
 const track=ticker.querySelector('.tk-track');if(track){const items=[...track.children];for(let i=items.length/2;i<items.length;i++)items[i]?.setAttribute('aria-hidden','true');}
}
const ids=['2021-00','2017-01','2021-01'];document.querySelectorAll('.foyer .hc').forEach((card,i)=>{if(card.querySelector('a')||!ids[i])return;const a=document.createElement('a');a.className='hc-link';a.href='/dossier/?project='+ids[i];a.setAttribute('aria-label','查看项目档案：'+(card.querySelector('img')?.alt||ids[i]));card.append(a);});
})();
// Reader-facing overview, calculated from the visible gallery scope.
(()=>{const stats=document.querySelectorAll('.stats .stat');const counts=[...document.querySelectorAll('.zcount')].map(e=>e.textContent.match(/·\s*(\d+)\s*件/)).filter(Boolean);if(stats.length===4&&counts.length===3){stats[2].querySelector('.num').textContent=String(counts.reduce((n,m)=>n+Number(m[1]),0));stats[2].querySelector('.lbl').textContent='当前布展展品';stats[0].querySelector('.lbl').textContent='收录获奖项目';stats[1].querySelector('.lbl').textContent='主题展区 / 展位';const years=document.querySelector('.foyer .kicker')?.textContent.match(/\d{4}\s*[—–-]\s*\d{4}/);if(years){stats[3].querySelector('.num').textContent=years[0];stats[3].querySelector('.lbl').textContent='馆藏收录年份';}}})();
// Progressive atmosphere: no asset download, no blocking overlay, no hidden content dependency.
(()=>{const hero=document.querySelector('.foyer');if(!hero||hero.querySelector('.museum-cosmos'))return;
const cosmos=document.createElement('div');cosmos.className='museum-cosmos';cosmos.setAttribute('aria-hidden','true');
cosmos.innerHTML='<div class="museum-nebula"></div><div class="museum-horizon"></div>';
for(let i=0;i<44;i++){const star=document.createElement('i');star.className='museum-star'+(i%4===0?' is-live':'');const x=(i*37+13)%100,y=(i*23+7)%94;star.style.left=x+'%';star.style.top=y+'%';star.style.setProperty('--star-alpha',String(x<45?.22:.35+(i%4)*.14));star.style.setProperty('--star-time',(5+i%6)+'s');if(i%9===0){star.style.width='3px';star.style.height='3px';}cosmos.append(star);}hero.prepend(cosmos);
const button=document.createElement('button');button.type='button';button.className='hero-motion-control';let paused=false;try{paused=sessionStorage.getItem('gd-hero-motion')==='paused';}catch(e){}
function update(){hero.dataset.motion=paused?'paused':'playing';button.textContent=paused?'播放星空动效':'暂停星空动效';button.setAttribute('aria-pressed',String(paused));}
button.addEventListener('click',()=>{paused=!paused;update();try{sessionStorage.setItem('gd-hero-motion',paused?'paused':'playing');}catch(e){}});update();hero.append(button);
if('IntersectionObserver' in window)new IntersectionObserver(entries=>{hero.dataset.away=String(!entries[0].isIntersecting);},{threshold:0}).observe(hero);
})();

// 157 精选展项筛选：只操作真实展项，不改变项目数据。
(()=>{const buttons=[...document.querySelectorAll('[data-exhibit-filter]')];if(!buttons.length)return;const cards=[...document.querySelectorAll('.museum-exhibit')];buttons.forEach(button=>button.addEventListener('click',()=>{const zone=button.dataset.exhibitFilter;buttons.forEach(item=>item.setAttribute('aria-pressed',String(item===button)));cards.forEach(card=>{card.hidden=zone!=='all'&&card.dataset.zone!==zone;});}));})();
