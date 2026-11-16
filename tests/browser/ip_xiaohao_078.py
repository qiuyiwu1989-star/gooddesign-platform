import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/playwright/gooddesign-ip-078'
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
    check('v=078' in page.locator('.gd-ip-trigger img').get_attribute('src'), '角色资产版本防旧缓存')
    check(page.locator('.gd-ip-trigger img').evaluate('(img) => img.complete && img.naturalWidth > 0'), '导航角色资源正常')
    page.locator('[data-gd-assistant-open]').click()
    check(page.locator('.gd-assistant-action').count() == 3, '三个真实导览动作')
    check(page.locator('.gd-assistant-action img').evaluate_all('(imgs) => imgs.every(img => img.complete && img.naturalWidth > 0)'), '三个动作角色资源正常')
    check('GoodDesign AI Agent' in page.locator('[data-gd-assistant]').inner_text(), 'AI Agent角色身份')
    check('研究搭子' in page.locator('[data-gd-assistant]').inner_text(), '研究伙伴角色文案')
    page.screenshot(path=str(OUT / 'assistant-light.png'))
    page.locator('.gd-assistant-action').nth(1).click()
    page.wait_for_url('**/inno/methods/')
    check(page.url.endswith('/inno/methods/'), '读方法进入真实方法库')
    page.go_back(wait_until='networkidle')
    page.locator('[data-gd-assistant-open]').click()
    page.keyboard.press('Escape')
    check(not page.locator('[data-gd-assistant]').is_visible(), 'Escape关闭导览')
    check(page.evaluate('document.activeElement.hasAttribute("data-gd-assistant-open")'), '关闭后焦点返回触发按钮')

    page.goto('http://127.0.0.1:8892/inno/dossier/?project=2015-02', wait_until='networkidle')
    page.locator('[data-gd-assistant-open]').click()
    check('project=2015-02' in page.locator('.gd-assistant-action').nth(2).get_attribute('href'), '核证据保留当前项目')
    page.keyboard.press('Escape')
    page.locator('[data-gd-theme-toggle]').click()
    check(page.locator('html').get_attribute('data-theme') == 'dark', '深色主题角色显示')
    page.locator('[data-gd-assistant-open]').click()
    page.screenshot(path=str(OUT / 'assistant-dark.png'))
    page.keyboard.press('Escape')
    page.locator('[data-gd-theme-toggle]').click()
    check(page.locator('html').get_attribute('data-theme') == 'light', '浅色主题恢复')

    for width in (390, 360):
        page.set_viewport_size({'width': width, 'height': 844})
        page.goto('http://127.0.0.1:8892/inno/', wait_until='networkidle')
        page.locator('[data-gd-assistant-open]').click()
        check(page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'{width}px导览无全页横向溢出')
        if width == 390:
            page.screenshot(path=str(OUT / 'assistant-mobile.png'))
        page.keyboard.press('Escape')
    for name in ('ip-xiaohao.svg?v=078', 'ip-xiaohao-method.svg', 'ip-xiaohao-evidence.svg'):
        response = page.request.get('http://127.0.0.1:8892/inno/portal/' + name)
        check(response.status == 200, name + '资源可访问')
    check(not errors, '无浏览器脚本异常')
    check(not failed, '无角色资源加载失败')
    browser.close()

report = {'checks': checks, 'errors': errors, 'failed_resources': failed}
(OUT / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
print(json.dumps({'check_count': len(checks), 'errors': errors, 'failed_resources': failed}, ensure_ascii=False))
