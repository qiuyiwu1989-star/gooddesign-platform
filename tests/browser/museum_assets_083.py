import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/design-083'
OUT.mkdir(parents=True, exist_ok=True)
URL = 'http://127.0.0.1:8892/inno/museum/'
checks = []
errors = []
failed = []
bad_responses = []


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
    page.on('response', lambda response: bad_responses.append((response.status, response.url)) if response.status >= 400 else None)
    page.goto(URL, wait_until='networkidle')
    images = page.locator('img').evaluate_all('(imgs) => imgs.map(i => ({src: i.currentSrc, loaded: i.complete && i.naturalWidth > 0}))')
    check(len(images) >= 20, '展馆图片元素完整呈现')
    check(all(image['loaded'] for image in images), '现存图片元素全部实际加载成功')
    check(not bad_responses, '图片/CSS背景/脚本无404响应')
    check(page.locator('[data-gd-nav="museum"]').get_attribute('aria-current') == 'page', '好设计馆在主导航正确高亮')
    check(page.locator('[data-gd-nav="projects"]').get_attribute('aria-current') is None, '项目库不抢占当前状态')
    check(page.locator('body > nav').count() == 0, '旧馆顶栏已移除')
    check(page.locator('.gd-nav').count() == 1, '只有一个统一主导航')
    check(page.locator('[data-gd-assistant-open]').count() == 1, '只有一个小好入口')
    check(page.locator('#gcFab').count() == 0, '旧copilot不重复出现')
    check(page.locator('.zbg').count() == 3, '三大展区CSS背景保留')
    check(page.locator('a[href="categories.html#industry"]').count() == 1, '展区链接保留旧站正确路径')
    page.screenshot(path=str(OUT / 'museum-desktop-light.png'))

    for width in (1440, 1280, 1024, 768, 390, 360):
        page.set_viewport_size({'width': width, 'height': 900})
        page.goto(URL, wait_until='networkidle')
        check(page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'{width}px展馆无全页横向溢出')
        check(page.locator('[data-gd-nav="museum"]').is_visible(), f'{width}px主导航可见好设计馆')
        labels_single_line = page.locator('.gd-links a').evaluate_all('(links) => links.every(a => getComputedStyle(a).whiteSpace === "nowrap" && a.scrollWidth <= a.clientWidth + 1)')
        check(labels_single_line, f'{width}px导航标签保持单行')
        if width >= 1024:
            height = page.locator('.gd-nav-inner').evaluate('(el) => el.getBoundingClientRect().height')
            check(height <= 80, f'{width}px新增导航后仍单行且不超过80px')
        if width == 390:
            page.screenshot(path=str(OUT / 'museum-mobile-light.png'))

    page.set_viewport_size({'width': 1440, 'height': 1000})
    page.goto(URL, wait_until='networkidle')
    page.locator('[data-gd-theme-toggle]').click()
    check(page.locator('html').get_attribute('data-theme') == 'dark', '深色主题生效')
    page.wait_for_timeout(300)
    page.screenshot(path=str(OUT / 'museum-desktop-dark.png'))
    page.locator('[data-gd-assistant-open]').click()
    check(page.locator('[data-gd-assistant]').is_visible(), '小好导览在展馆可打开')
    check(page.locator('.gd-assistant-action').count() == 3, '小好三个真实动作保留')
    page.keyboard.press('Escape')

    page.locator('a[href="categories.html#industry"]').click()
    page.wait_for_load_state('networkidle')
    check(page.url.startswith('http://127.0.0.1:8892/categories.html'), '展区链接进入真实旧站页面')
    check('#industry' in page.url, '展区锚点保留')
    check(not bad_responses, '进入展区后仍无404资源')
    check(not errors, '无浏览器脚本异常')
    check(not failed, '无页面资源加载失败')
    browser.close()

report = {'check_count': len(checks), 'checks': checks, 'errors': errors, 'failed_resources': failed, 'bad_responses': bad_responses}
(OUT / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'check_count': len(checks), 'errors': errors, 'failed_resources': failed, 'bad_responses': bad_responses}, ensure_ascii=False))
