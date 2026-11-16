import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/design-157'
OUT.mkdir(parents=True, exist_ok=True)
checks = []
errors = []
failed = []


def check(value, label):
    if not value:
        raise AssertionError(label)
    checks.append(label)


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1440, 'height': 1000}, color_scheme='light')
    page = context.new_page()
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('requestfailed', lambda request: failed.append(request.url))

    page.goto('http://127.0.0.1:8892/museum/', wait_until='networkidle')
    check(page.locator('.foyer img').evaluate_all('(imgs)=>imgs.every(i=>i.complete&&i.naturalWidth>0)'), '首屏三张项目封面全部恢复')
    check(page.locator('.zbg').evaluate_all('(els)=>els.every(e=>getComputedStyle(e).backgroundImage.includes("/inno/"))'), '三大展区背景使用有效部署资源路径')
    check(page.locator('.museum-exhibit').count() == 6, '六个真实精选展项完整')
    check(page.locator('.museum-cosmos').evaluate('(el)=>getComputedStyle(el).display') == 'none', '星空装饰不再干扰展品')
    check(page.locator('.museum-exhibit-filter').count() == 0, '筛选无重复容器')
    for zone, count in (('industry', 4), ('life', 1), ('society', 1), ('all', 6)):
        page.locator(f'[data-exhibit-filter="{zone}"]').click()
        check(page.locator('.museum-exhibit:visible').count() == count, f'{zone}展项筛选数量正确')
        check(page.locator(f'[data-exhibit-filter="{zone}"]').get_attribute('aria-pressed') == 'true', f'{zone}筛选状态正确')
    check('找项目、读方法、核证据' in page.locator('.guide').inner_text(), '导览能力表述真实')
    check(page.locator('.gd-nav').count() == 1 and page.locator('.gd-footer').count() == 1, '展馆统一顶底栏')
    page.screenshot(path=str(OUT / 'museum-hero.png'))
    page.locator('#zones').screenshot(path=str(OUT / 'museum-zones.png'))
    page.locator('#featured').screenshot(path=str(OUT / 'museum-featured.png'))

    for width in (1440, 1280, 1024, 768, 390, 360):
        page.set_viewport_size({'width': width, 'height': 900})
        page.goto('http://127.0.0.1:8892/museum/', wait_until='networkidle')
        check(page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'展馆{width}px无横向溢出')
        check(page.locator('.foyer img').evaluate_all('(imgs)=>imgs.every(i=>i.complete&&i.naturalWidth>0)'), f'展馆{width}px封面有效')
        if width == 390:
            page.screenshot(path=str(OUT / 'museum-mobile.png'), full_page=True)

    page.set_viewport_size({'width': 1440, 'height': 1000})
    page.goto('http://127.0.0.1:8892/apps/', wait_until='networkidle')
    check(page.locator('.app-card').count() == 8, '七个应用完整')
    check(len(page.locator('.app-store-grid').evaluate('(el)=>getComputedStyle(el).gridTemplateColumns.split(" ")')) == 3, '桌面三列应用货架')
    grid_width = page.locator('.app-store-grid').evaluate('(el)=>el.getBoundingClientRect().width')
    regional_width = page.locator('[data-app-id="regional"]').evaluate('(el)=>el.getBoundingClientRect().width')
    check(abs(grid_width - regional_width) < 2, '产业创新Agent整幅特色卡')
    for kind, count in (('experience', 3), ('innovation', 3), ('access', 2), ('all', 8)):
        page.locator(f'[data-app-kind="{kind}"]').click()
        check(page.locator('.app-card:visible').count() == count, f'{kind}应用筛选数量正确')
        check(f'显示 {count} 项应用' in page.locator('#app-count').inner_text(), f'{kind}计数正确')
    page.locator('[data-app-kind="access"]').click()
    check('kind=access' in page.url, '分类筛选写入URL')
    page.locator('#app-search-input').fill('MCP')
    check(page.locator('.app-card:visible').count() == 1, '搜索与分类组合筛选')
    check('q=mcp' in page.url, '搜索关键词写入URL')
    page.locator('#app-search-input').fill('不存在-157')
    check(page.locator('#app-empty').is_visible(), '无结果空态可见')
    check(page.locator('#app-clear').is_visible(), '清除搜索与筛选入口可见')
    page.locator('#app-clear').click()
    check(page.locator('.app-card:visible').count() == 8, '清除后恢复七个应用')
    check('q=' not in page.url and 'kind=' not in page.url, '清除同步清理URL')

    page.goto('http://127.0.0.1:8892/apps/?kind=access&q=MCP', wait_until='networkidle')
    check(page.locator('.app-card:visible').count() == 1, '分享链接恢复应用筛选')
    check(page.locator('[data-app-kind="access"]').get_attribute('aria-pressed') == 'true', '分享链接恢复分类状态')
    page.locator('#app-clear').click()
    page.locator('[data-app-id="regional"]').click()
    check(page.locator('#app-sheet').evaluate('(el)=>el.open'), '产业应用详情打开')
    check(page.locator('#app-detail-title').inner_text() == '产业创新 Agent', '详情应用标题正确')
    check(page.locator('#app-detail-route').get_attribute('href') == '/expo/', '详情真实入口正确')
    check('玉环产业创新专区' in page.locator('.app-case-strip').inner_text(), '详情案例联动正确')
    page.screenshot(path=str(OUT / 'apps-dialog.png'))
    page.keyboard.press('Escape')
    check(not page.locator('#app-sheet').evaluate('(el)=>el.open'), 'Escape关闭详情')
    check(page.locator('[data-app-id="regional"]').evaluate('(el)=>el===document.activeElement'), '关闭后焦点返回产业卡')
    page.locator('[data-app-id="mcp"]').click()
    check('Agent如何读取项目' in page.locator('.app-case-strip').inner_text(), 'MCP详情案例联动')
    page.locator('#app-sheet-close').click()
    page.locator('[data-app-id="mcp"]').click()
    page.mouse.click(2, 2)
    check(not page.locator('#app-sheet').evaluate('(el)=>el.open'), '背板点击关闭详情')
    page.screenshot(path=str(OUT / 'apps-desktop.png'))

    for width in (1280, 1024, 768, 600, 390, 360):
        page.set_viewport_size({'width': width, 'height': 900})
        page.goto('http://127.0.0.1:8892/apps/', wait_until='networkidle')
        check(page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'应用中心{width}px无横向溢出')
        if width <= 600:
            check(len(page.locator('.app-store-grid').evaluate('(el)=>getComputedStyle(el).gridTemplateColumns.split(" ")')) == 1, f'应用中心{width}px单列阅读')
        if width == 390:
            page.screenshot(path=str(OUT / 'apps-mobile.png'), full_page=True)
            page.locator('[data-app-id="needs"]').click()
            page.wait_for_timeout(350)
            box = page.locator('#app-sheet').bounding_box()
            check(box['width'] <= 390 and box['y'] + box['height'] <= 901, '移动详情位于视口内')
            page.keyboard.press('Escape')

    page.set_viewport_size({'width': 1440, 'height': 1000})
    page.goto('http://127.0.0.1:8892/apps/', wait_until='networkidle')
    page.locator('[data-gd-theme-toggle]').click()
    page.wait_for_timeout(700)
    check(page.locator('html').get_attribute('data-theme') == 'dark', '应用中心深色主题生效')
    check(page.locator('.app-store-head h1').evaluate('(el)=>getComputedStyle(el).color') == 'rgb(236, 238, 255)', '深色标题对比正确')
    page.screenshot(path=str(OUT / 'apps-dark.png'))

    reduced = browser.new_context(viewport={'width': 1440, 'height': 1000}, reduced_motion='reduce')
    rp = reduced.new_page()
    rp.goto('http://127.0.0.1:8892/museum/', wait_until='networkidle')
    check(rp.locator('.museum-cosmos').evaluate('(el)=>getComputedStyle(el).display') == 'none', '减少动态展馆保持安静')
    rp.goto('http://127.0.0.1:8892/apps/', wait_until='networkidle')
    rp.locator('[data-app-id="needs"]').click()
    check(rp.locator('#app-sheet').evaluate('(el)=>getComputedStyle(el).animationName') == 'none', '减少动态详情无入场动画')
    reduced.close()
    check(not errors, '无浏览器脚本异常：' + repr(errors))
    check(not failed, '无资源加载失败：' + repr(failed))
    browser.close()

report = {'check_count': len(checks), 'checks': checks, 'errors': errors, 'failed_resources': failed}
(OUT / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
