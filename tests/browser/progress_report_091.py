import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/design-091'
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
    response = page.goto('http://127.0.0.1:8896/', wait_until='networkidle')
    check(response.status == 200, 'HTML汇报页真实HTTP可访问')
    check('项目进展汇报' in page.title(), '页面标题正确')
    check(page.locator('.report-kpi').count() == 4, '首屏四个核心指标')
    check('560' in page.locator('.report-kpi').nth(0).inner_text(), '560项目总数')
    check('103' in page.locator('.report-kpi').nth(1).inner_text(), '103原生研究版')
    check('979 / 496' in page.locator('.report-kpi').nth(2).inner_text(), '来源条目与JSON一致')
    check('1239' in page.locator('.report-kpi').nth(3).inner_text(), '构建页面数正确')
    check('18.4%' in page.locator('.report-summary').inner_text(), '原生覆盖按103/560计算')
    check(page.locator('.report-queue').count() == 4, '四个深研分层队列')
    check('205批' in page.locator('.report-issues').inner_text(), 'full结构问题可见')
    check('127批' in page.locator('.report-issues').inner_text(), 'patents结构问题可见')
    check('791项异常' in page.locator('.report-issues').inner_text(), '2025-00证据异常可见')
    check('0次模型调用的脚本演示' in page.locator('body').inner_text(), '动态案例边界保留')
    check(page.locator('.gd-nav').count() == 1, '统一顶部栏')
    check(page.locator('.gd-footer').count() == 1, '统一底部栏')
    check(page.locator('.gd-nav .gd-brand strong').inner_text() == '好设计', '中文主品牌')
    check(page.locator('.report-step').count() == 4, 'P0-P3计划完整')
    page.screenshot(path=str(OUT / 'report-desktop-light.png'))

    for width in (1440, 768, 390):
        page.set_viewport_size({'width': width, 'height': 900})
        page.goto('http://127.0.0.1:8896/', wait_until='networkidle')
        check(page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'{width}px汇报页无横向溢出')
        if width == 390:
            page.screenshot(path=str(OUT / 'report-mobile-light.png'))

    page.set_viewport_size({'width': 1440, 'height': 1000})
    page.goto('http://127.0.0.1:8896/', wait_until='networkidle')
    page.locator('[data-gd-theme-toggle]').click()
    check(page.locator('html').get_attribute('data-theme') == 'dark', '深色主题生效')
    page.wait_for_timeout(250)
    page.screenshot(path=str(OUT / 'report-desktop-dark.png'))
    page.evaluate('window.__printed = false; window.print = () => { window.__printed = true; }')
    page.locator('#report-print').click()
    check(page.evaluate('window.__printed') is True, '打印按钮调用真实打印')
    check(page.locator('[data-gd-assistant-open]').count() == 1, '小好入口保留')
    page.locator('[data-gd-assistant-open]').click()
    check(page.locator('[data-gd-assistant]').is_visible(), '小好导览可打开')
    check(page.locator('[data-gd-assistant]').evaluate('(el) => getComputedStyle(el, "::backdrop").backdropFilter') == 'none', '小好打开时背景清晰')
    page.keyboard.press('Escape')

    for route in ('/research-088/audit-summary.json', '/research-088/queues.json', '/research-089/material-inventory.csv', '/research-079/2019-s19/publish-result.json', '/reports/项目进展数据-2026-11-04.json'):
        response = page.request.get('http://127.0.0.1:8896' + route)
        check(response.status == 200, route + '证据可访问')
    check(not errors, '无浏览器脚本异常')
    check(not failed, '无页面资源加载失败')
    browser.close()

report = {'check_count': len(checks), 'checks': checks, 'errors': errors, 'failed_resources': failed}
(OUT / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'check_count': len(checks), 'errors': errors, 'failed_resources': failed}, ensure_ascii=False))
