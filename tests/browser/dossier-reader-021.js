async page => {
 const report={version:'5.0.0',checks:[],errors:[]};
 page.on('pageerror',err=>report.errors.push(err.message));
 const check=(ok,name)=>{if(!ok)throw new Error(name);report.checks.push(name)};
 const open=()=>page.locator('.reader-module[open]').count();
 check(await open()===0,'默认八模块全部收起');
 check(await page.locator('.reader-module').count()===8,'八个板块保留');
 await page.locator('#toc-reader [data-reader-section="technical"]').click();
 check(await open()===1&&await page.locator('#reader-technical').getAttribute('open')!==null,'目录打开系统板块');
 check(await page.locator('#toc-reader [aria-current="location"]').getAttribute('data-reader-section')==='technical','当前目录标记');
 await page.screenshot({path:'output/playwright/ui021-module-desktop.png'});
 const summary=page.locator('#reader-overview>summary');await summary.focus();await page.keyboard.press('Enter');
 check(await open()===1&&await page.locator('#reader-overview').getAttribute('open')!==null,'Enter切换板块并关闭前板块');
 check(await page.locator('#reader-overview .missing-fields[open]').count()===0,'待补字段默认收起');
 await page.locator('#reader-overview .missing-fields>summary').click();
 check(await page.locator('#reader-overview .blank-value').isVisible(),'待补字段展开后留白');
 await summary.focus();await page.keyboard.press('Space');check(await open()===0,'Space可关闭板块');
 await page.locator('[data-view="library"]').first().click();
 check(await page.locator('.paper-reading[open]').count()===0,'论文解读默认收起');
 check(await page.locator('#reader-sources[open]').count()===0,'来源目录后置并收起');
 await page.goto('http://127.0.0.1:8773/档案.html?v=5.0.0#paper-A04');
 check(await page.locator('#library-view').isVisible()&&await page.locator('#paper-A04').getAttribute('open')!==null,'论文深链自动展开');
 await page.goto('http://127.0.0.1:8773/档案.html?v=5.0.0#reader-trials');
 check(await open()===1&&await page.locator('#reader-validation').getAttribute('open')!==null&&await page.locator('#reader-trials').getAttribute('open')!==null,'子资料深链展开父板块');
 const pre=await page.locator('#reader-view details').evaluateAll(els=>els.map(el=>el.open));
 await page.evaluate(()=>window.dispatchEvent(new Event('beforeprint')));
 check(await open()===8,'打印展开全部八模块');
 await page.emulateMedia({media:'print'});
 check(await page.locator('#reader-applications .module-content').isVisible(),'打印可见末尾模块正文');
 await page.emulateMedia({media:'screen'});await page.evaluate(()=>window.dispatchEvent(new Event('afterprint')));
 check(JSON.stringify(pre)===JSON.stringify(await page.locator('#reader-view details').evaluateAll(els=>els.map(el=>el.open))),'打印后恢复每个开合状态');
 await page.goto('http://127.0.0.1:8773/档案.html?v=5.0.0#block-ip');
 check(await page.locator('#reader-ip').getAttribute('open')!==null,'旧block链接仍可打开');
 await page.locator('#reader-ip [data-paper="A01"]').click();check(await page.locator('#paper-A01').getAttribute('open')!==null,'论文入口能打开解读');
 await page.goto('http://127.0.0.1:8773/档案.html?v=5.0.0#field-F001');
 check(await page.locator('#document-view').isVisible(),'旧字段深链保留');
 await page.goto('http://127.0.0.1:8773/档案.html?v=5.0.0#source-S01');
 check(await page.locator('#evidence-view').isVisible(),'旧来源深链保留');
 for(const width of [1440,768,390]){
  await page.setViewportSize({width,height:1000});
  for(const view of ['reader','library','assessment']){
   await page.locator('[data-view="'+view+'"]').first().click();
   check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),width+'px '+view+'无页面横向溢出');
  }
 }
 await page.locator('[data-view="reader"]').first().click();
 await page.locator('#reader-technical>summary').click();
 await page.screenshot({path:'output/playwright/ui021-mobile-module.png',fullPage:true});
 await page.locator('#reader-technical>summary').click();
 await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:'output/playwright/ui021-mobile.png',fullPage:true});
 await page.emulateMedia({reducedMotion:'reduce'});
 check(await page.locator('.module-chevron').first().evaluate(el=>getComputedStyle(el).transitionDuration)==='0s','减少动态偏好');
 await page.emulateMedia({reducedMotion:'no-preference'});
 check(report.errors.length===0,'无JavaScript运行错误');
 await page.setViewportSize({width:1440,height:1100});
 await page.goto('http://127.0.0.1:8773/档案.html?v=5.0.0');
 await page.screenshot({path:'output/playwright/ui021-desktop.png',fullPage:true});
 await page.evaluate(r=>window.ui021Report=r,report);
 return report;
}
