import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/design-085'
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
    page.goto('http://127.0.0.1:8892/inno/', wait_until='networkidle')
    page.locator('[data-gd-assistant-open]').click()
    backdrop = page.locator('[data-gd-assistant]').evaluate('(el) => ({background: getComputedStyle(el, "::backdrop").backgroundColor, filter: getComputedStyle(el, "::backdrop").backdropFilter})')
    check(backdrop['background'] in ('rgba(0, 0, 0, 0)', 'transparent'), '背景遮罩完全透明')
    check(backdrop['filter'] == 'none', '背景不使用模糊滤镜')
    check(page.locator('[data-gd-assistant]').is_visible(), '导览面板正常打开')
    check(page.locator('[data-gd-assistant-open]').get_attribute('aria-expanded') == 'true', 'ARIA打开状态保持')
    page.screenshot(path=str(OUT / 'copilot-clear-desktop.png'))
    page.keyboard.press('Escape')
    check(page.evaluate('document.activeElement.hasAttribute("data-gd-assistant-open")'), '关闭后焦点返回入口')

    page.locator('[data-gd-theme-toggle]').click()
    page.locator('[data-gd-assistant-open]').click()
    page.wait_for_timeout(250)
    check(page.locator('html').get_attribute('data-theme') == 'dark', '深色主题正常')
    check(page.locator('[data-gd-assistant]').evaluate('(el) => getComputedStyle(el, "::backdrop").backdropFilter') == 'none', '深色背景同样不模糊')
    page.screenshot(path=str(OUT / 'copilot-clear-dark.png'))
    page.keyboard.press('Escape')
    page.locator('[data-gd-theme-toggle]').click()

    page.set_viewport_size({'width': 390, 'height': 844})
    page.goto('http://127.0.0.1:8892/inno/', wait_until='networkidle')
    page.locator('[data-gd-assistant-open]').click()
    check(page.locator('[data-gd-assistant]').evaluate('(el) => getComputedStyle(el, "::backdrop").backdropFilter') == 'none', '移动背景同样不模糊')
    check(page.evaluate('document.documentElement.scrollWidth <= innerWidth'), '移动端无全页横向溢出')
    page.screenshot(path=str(OUT / 'copilot-clear-mobile.png'))
    page.keyboard.press('Escape')
    check(page.evaluate('document.activeElement.hasAttribute("data-gd-assistant-open")'), '移动端关闭焦点返回')
    check(not errors, '无浏览器脚本异常')
    check(not failed, '无页面资源加载失败')
    browser.close()

report = {'check_count': len(checks), 'checks': checks, 'errors': errors, 'failed_resources': failed}
(OUT / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'check_count': len(checks), 'errors': errors, 'failed_resources': failed}, ensure_ascii=False))
