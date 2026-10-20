async page=>{
 const checks=[];const check=(ok,msg)=>{if(!ok)throw Error(msg);checks.push(msg)};
 await page.goto('http://127.0.0.1:8775/inno/projects/2025-00/?v=5.2.1#reader-innovation');await page.reload();await page.setViewportSize({width:1440,height:1000});
 check(await page.locator('#reader-innovation[open]').count()===1,'设计思路深链打开');
 check(await page.locator('.mechanism-unit').count()===6,'六机制单元');check(await page.locator('.mechanism-unit[open]').count()===0,'机制默认收起');
 await page.locator('#mechanism-K01>summary').click();check(await page.locator('#mechanism-K01 .mechanism-grid').isVisible(),'机制解读可展开');
 check((await page.locator('#mechanism-K01').textContent()).includes('匹配前先问'),'包含匹配追问');
 await page.locator('#mechanism-K01 [data-reasoning-source=S07]').click();check(await page.locator('#evidence-view').isVisible(),'机制来源可回查');
 await page.goto('http://127.0.0.1:8775/inno/projects/2025-00/?v=5.2.1#reader-applications');await page.reload();
 check(!await page.locator('#reasoning-cards').isVisible(),'具体应用设想默认折叠');await page.locator('#related-explorations>summary').focus();await page.keyboard.press('Enter');
 check(await page.locator('#reasoning-cards').isVisible(),'键盘可打开独立关联探索');
 await page.locator('#reasoning-toggle').click();check(!await page.locator('#reasoning-cards').isVisible(),'保留隐藏AI能力');
 await page.locator('#view-bar [data-view=assessment]').click();check((await page.locator('#assessment-view').textContent()).includes('已验证迁移：0 项'),'评估区分结构和验证');
 await page.goto('http://127.0.0.1:8775/inno/projects/2025-00/?v=5.2.1#reader-innovation');await page.setViewportSize({width:390,height:844});await page.locator('#mechanism-K06>summary').click();
 check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'手机无溢出');await page.locator('#mechanism-K06').scrollIntoViewIfNeeded();await page.screenshot({path:'output/playwright/mechanisms029-mobile.png'});
 const before=await page.locator('.mechanism-unit').evaluateAll(xs=>xs.map(x=>x.open));await page.evaluate(()=>dispatchEvent(new Event('beforeprint')));check(await page.locator('.mechanism-unit[open]').count()===6,'打印展开六机制');await page.evaluate(()=>dispatchEvent(new Event('afterprint')));check(JSON.stringify(before)===JSON.stringify(await page.locator('.mechanism-unit').evaluateAll(xs=>xs.map(x=>x.open))),'打印恢复机制状态');
 await page.setViewportSize({width:1440,height:1000});await page.goto('http://127.0.0.1:8775/inno/projects/2025-00/?v=5.2.1#reader-innovation');await page.locator('#mechanism-K01>summary').click();await page.locator('#reader-innovation').scrollIntoViewIfNeeded();await page.screenshot({path:'output/playwright/mechanisms029-desktop.png'});
 return checks;
}
