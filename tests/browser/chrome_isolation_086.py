import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/design-086'
OUT.mkdir(parents=True, exist_ok=True)
checks = []
errors = []
failed = []


def check(condition, label):
    if not condition:
        raise AssertionError(label)
    checks.append(label)


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1440, 'height': 1000}, color_scheme='light')
    page = context.new_page()
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('requestfailed', lambda request: failed.append(request.url))
    page.goto('http://127.0.0.1:8892/categories.html', wait_until='networkidle')
    check(page.locator('body > nav').count() == 0, '旧馆顶部导航已移除')
    check(page.locator('.gd-nav').count() == 1, '只有一个统一顶部栏')
    check(page.locator('footer').count() == 1, '只有一个统一底部栏')
    check(page.locator('[data-gd-nav="museum"]').get_attribute('aria-current') == 'page', '好设计馆正确高亮')
    check(page.locator('[data-gd-nav="projects"]').get_attribute('aria-current') is None, '项目库不错误高亮')
    footer_style = page.locator('.gd-footer-links').evaluate('(el) => ({background: getComputedStyle(el).backgroundColor, position: getComputedStyle(el).position, padding: getComputedStyle(el).padding})')
    check(footer_style['background'] == 'rgba(0, 0, 0, 0)', '底部链接无旧纸色背景')
    check(footer_style['position'] == 'static', '底部链接无旧sticky定位')
    check(footer_style['padding'] == '0px', '底部链接无旧导航内边距')
    nav_style = page.locator('.gd-links').evaluate('(el) => ({background: getComputedStyle(el).backgroundColor, position: getComputedStyle(el).position, padding: getComputedStyle(el).padding})')
    check(nav_style['background'] == 'rgba(0, 0, 0, 0)', '顶部链接无旧纸色背景')
    check(nav_style['position'] == 'static', '顶部链接无旧sticky定位')
    check(page.locator('#gcFab').count() == 0, '旧copilot不重复出现')
    check(page.locator('[data-gd-assistant-open]').count() == 1, '只保留一个小好入口')
    page.locator('.gd-footer').scroll_into_view_if_needed()
    page.wait_for_load_state('networkidle')
    page.wait_for_function("[...document.images].every(i => i.complete && i.naturalWidth > 0)")
    images = page.locator('img').evaluate_all('(imgs) => imgs.map(i => i.complete && i.naturalWidth > 0)')
    check(all(images), '展区现有图片全部正常加载')
    page.screenshot(path=str(OUT / 'chrome-footer-light.png'))

    for name in ('award.html', 'laureates.html'):
        page.goto('http://127.0.0.1:8892/' + name, wait_until='networkidle')
        check(page.locator('[data-gd-nav="museum"]').get_attribute('aria-current') == 'page', name + '高亮好设计馆')
        check(page.locator('footer').count() == 1, name + '只有一个底部栏')

    for width in (1024, 768, 390, 360):
        page.set_viewport_size({'width': width, 'height': 900})
        page.goto('http://127.0.0.1:8892/categories.html', wait_until='networkidle')
        check(page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'{width}px顶底栏无横向溢出')
        labels = page.locator('.gd-links a').evaluate_all('(links) => links.every(a => getComputedStyle(a).whiteSpace === "nowrap" && a.scrollWidth <= a.clientWidth + 1)')
        check(labels, f'{width}px导航标签保持单行')
        if width == 390:
            page.screenshot(path=str(OUT / 'chrome-mobile-light.png'))

    page.set_viewport_size({'width': 1440, 'height': 1000})
    page.goto('http://127.0.0.1:8892/categories.html', wait_until='networkidle')
    page.locator('[data-gd-theme-toggle]').click()
    check(page.locator('html').get_attribute('data-theme') == 'dark', '深色主题生效')
    page.locator('.gd-footer').scroll_into_view_if_needed()
    page.wait_for_timeout(250)
    check(page.locator('.gd-footer-links').evaluate('(el) => getComputedStyle(el).backgroundColor') == 'rgba(0, 0, 0, 0)', '深色底部无旧纸色背景')
    page.screenshot(path=str(OUT / 'chrome-footer-dark.png'))

    page.goto('http://127.0.0.1:8892/inno/museum/', wait_until='networkidle')
    check(page.locator('body > nav').count() == 0, '馆首页旧顶栏仍保持移除')
    check(page.locator('[data-gd-nav="museum"]').get_attribute('aria-current') == 'page', '馆首页高亮保持')
    page.goto('http://127.0.0.1:8892/inno/dossier/?project=2019-s19', wait_until='networkidle')
    check(page.locator('.gd-nav').count() == 1, '动态档案统一顶栏')
    check(page.locator('footer').count() == 1, '动态档案统一底部')
    check(page.locator('.gd-nav .gd-brand strong').inner_text() == '好设计', '中文品牌层级保持')
    check(not errors, '无浏览器脚本异常')
    check(not failed, '无页面资源加载失败')
    browser.close()

report = {'check_count': len(checks), 'checks': checks, 'errors': errors, 'failed_resources': failed}
(OUT / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'check_count': len(checks), 'errors': errors, 'failed_resources': failed}, ensure_ascii=False))
