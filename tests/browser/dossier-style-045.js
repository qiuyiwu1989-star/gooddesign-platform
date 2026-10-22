async (page) => {
 const results=[];const errors=[];page.on('pageerror',e=>errors.push(e.message));
 let baseline;
 for(const pid of ['2025-00','2015-02','2017-01','2019-s10']){
  await page.setViewportSize({width:1440,height:1000});await page.goto('http://127.0.0.1:8776/dossier/?project='+pid);
  const style=await page.evaluate(()=>({font:getComputedStyle(document.body).fontFamily,bg:getComputedStyle(document.body).backgroundColor,grid:getComputedStyle(document.querySelector('.shell')).gridTemplateColumns,radius:getComputedStyle(document.querySelector('.reader-module')).borderRadius,modules:document.querySelectorAll('.reader-module').length,open:document.querySelectorAll('.reader-module[open]').length,toc:document.querySelector('#toc').getBoundingClientRect().width}));
  if(!baseline)baseline=style;for(const k of ['font','bg','grid','radius','modules'])if(style[k]!==baseline[k])throw Error(pid+' style mismatch '+k+JSON.stringify(style));
  if(style.open!==0)throw Error('not initially collapsed');
  await page.locator('#view-bar button').nth(1).click();const toc1=await page.locator('#toc').boundingBox();await page.locator('#view-bar button').nth(2).click();const toc2=await page.locator('#toc').boundingBox();if(toc1.x!==toc2.x||toc1.width!==toc2.width)throw Error('directory shifts');
  await page.locator('#view-bar button').nth(0).click();await page.locator('#reader-technical > summary').click();await page.locator('#reader-innovation > summary').click();if(await page.locator('.reader-module[open]').count()!==1)throw Error('accordion');
  if(pid!=='2025-00'){
   await page.locator('#toc-reader a[data-reader-section="overview"]').click();const record=page.locator('#reader-overview .research-record').first();await record.locator(':scope > summary').click();const source=record.locator('a[href^="#source-"]').first();const hash=await source.getAttribute('href');await source.locator('..').locator('..').evaluate(el=>el.open=true);await source.click();if(!await page.locator('#library-view').isVisible())throw Error('source did not switch view');if(!await page.locator(hash).evaluate(el=>el.open))throw Error('source not expanded');
   await page.reload();if(!await page.locator(hash).isVisible())throw Error('source deep link lost');
   await page.locator('#view-bar button').nth(0).click();await page.locator('#reader-history > summary').focus();await page.keyboard.press('Enter');if(!await page.locator('#reader-history').evaluate(el=>el.open))throw Error('keyboard');
   await page.locator('#view-bar button').nth(1).click();await page.emulateMedia({media:'print'});if(!await page.locator('#library-view').isVisible())throw Error('library print hidden');await page.emulateMedia({media:null});await page.locator('#view-bar button').nth(2).click();await page.emulateMedia({media:'print'});if(!await page.locator('#assessment-view').isVisible())throw Error('assessment print hidden');await page.emulateMedia({media:null});
   const before=await page.locator('details').evaluateAll(els=>els.map(el=>el.open));await page.evaluate(()=>{window.dispatchEvent(new Event('beforeprint'));window.dispatchEvent(new Event('afterprint'));});const after=await page.locator('details').evaluateAll(els=>els.map(el=>el.open));if(JSON.stringify(before)!==JSON.stringify(after))throw Error('print state');
  }
  await page.setViewportSize({width:390,height:844});await page.goto('http://127.0.0.1:8776/dossier/?project='+pid);
  const mobile=await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth}));if(mobile.scroll>mobile.width)throw Error('mobile overflow '+pid);
  await page.locator('#reader-technical > summary').click();const expanded=await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth}));if(expanded.scroll>expanded.width)throw Error('expanded overflow');
  if(pid==='2015-02')await page.screenshot({path:'output/playwright/045-jiaolong-mobile.png',fullPage:false});
  results.push({project:pid,style,views:'same_sidebar',accordion:'passed',mobile,expanded});
 }
 if(errors.length)throw Error(JSON.stringify(errors));return {status:'passed',results,errors};
}
