import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/design-081'
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
    trigger = page.locator('[data-gd-assistant-open]')
    rect = trigger.bounding_box()
    check(trigger.evaluate('(el) => getComputedStyle(el).position') == 'fixed', '入口使用固定定位')
    check(abs(rect['x'] + rect['width'] - 1416) < 2, '桌面入口距右24px')
    check(abs(rect['y'] + rect['height'] - 976) < 2, '桌面入口距底24px')
    check(trigger.locator('span').is_visible(), '桌面显示小好名称')
    check(trigger.get_attribute('aria-haspopup') == 'dialog', '声明dialog弹出关系')
    check(trigger.get_attribute('aria-controls') == page.locator('[data-gd-assistant]').get_attribute('id'), 'aria-controls指向真实面板')
    check(trigger.get_attribute('aria-expanded') == 'false', '初始展开状态为false')

    trigger.click()
    dialog = page.locator('[data-gd-assistant]')
    check(dialog.is_visible(), '点击打开导览面板')
    check(trigger.get_attribute('aria-expanded') == 'true', '打开后aria-expanded为true')
    check(page.evaluate('document.activeElement.hasAttribute("data-gd-assistant-close")'), '打开后焦点进入关闭按钮')
    panel = dialog.bounding_box()
    check(abs(panel['x'] + panel['width'] - 1416) < 2, '面板与右下入口对齐')
    check(panel['y'] + panel['height'] < rect['y'], '面板位于入口上方')
    check(panel['height'] < 900, '面板不再占满右侧高度')
    check(page.locator('.gd-assistant-action').count() == 3, '保留三个真实导览动作')
    page.screenshot(path=str(OUT / 'copilot-desktop-light.png'))
    page.keyboard.press('Escape')
    check(not dialog.is_visible(), 'Escape关闭面板')
    page.wait_for_function("document.querySelector('[data-gd-assistant-open]').getAttribute('aria-expanded') === 'false'")
    check(trigger.get_attribute('aria-expanded') == 'false', '关闭后aria-expanded恢复false')
    check(page.evaluate('document.activeElement.hasAttribute("data-gd-assistant-open")'), '关闭后焦点返回入口')
    trigger.click()
    page.locator('[data-gd-assistant-close]').click()
    check(not dialog.is_visible(), '关闭按钮可用')

    page.locator('[data-gd-theme-toggle]').click()
    check(page.locator('html').get_attribute('data-theme') == 'dark', '深色主题生效')
    trigger.click()
    page.wait_for_timeout(300)
    page.screenshot(path=str(OUT / 'copilot-desktop-dark.png'))
    check(dialog.evaluate('(el) => getComputedStyle(el).backgroundColor') != 'rgba(0, 0, 0, 0)', '深色面板具有实色表面')
    page.keyboard.press('Escape')
    page.locator('[data-gd-theme-toggle]').click()

    page.goto('http://127.0.0.1:8892/inno/methods/', wait_until='networkidle')
    check(page.locator('[data-gd-assistant-open]').count() == 1, '方法库只有一个浮动入口')
    page.locator('[data-gd-assistant-open]').click()
    page.locator('.gd-assistant-action').nth(1).click()
    page.wait_for_url('**/inno/methods/')
    check(page.url.endswith('/inno/methods/'), '读方法链接保持真实路由')

    page.goto('http://127.0.0.1:8892/inno/dossier/?project=2019-s19', wait_until='networkidle')
    page.locator('[data-gd-assistant-open]').click()
    check('project=2019-s19' in page.locator('.gd-assistant-action').nth(2).get_attribute('href'), '动态档案核证据保留当前项目')
    page.keyboard.press('Escape')

    for width in (390, 360):
        page.set_viewport_size({'width': width, 'height': 844})
        page.goto('http://127.0.0.1:8892/inno/', wait_until='networkidle')
        mobile_trigger = page.locator('[data-gd-assistant-open]')
        mobile = mobile_trigger.bounding_box()
        check(abs(mobile['x'] + mobile['width'] - (width - 16)) < 2, f'{width}px入口距右16px')
        check(abs(mobile['y'] + mobile['height'] - 828) < 2, f'{width}px入口距底16px')
        check(round(mobile['width']) == 48 and round(mobile['height']) == 48, f'{width}px入口为48px圆形触控目标')
        check(mobile_trigger.locator('span').is_hidden(), f'{width}px仅显示头像')
        mobile_trigger.click()
        panel = page.locator('[data-gd-assistant]').bounding_box()
        check(panel['x'] >= 11 and panel['x'] + panel['width'] <= width - 11, f'{width}px面板水平不溢出')
        check(panel['y'] + panel['height'] < mobile['y'], f'{width}px面板位于入口上方')
        check(page.locator('#assistant-title').evaluate('(el) => el.scrollWidth <= el.clientWidth + 1'), f'{width}px助手标题完整单行显示')
        check(page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'{width}px无全页横向溢出')
        if width == 390:
            page.screenshot(path=str(OUT / 'copilot-mobile-light.png'))
        page.keyboard.press('Escape')
        check(page.evaluate('document.activeElement.hasAttribute("data-gd-assistant-open")'), f'{width}px关闭后焦点返回')

    check(not errors, '无浏览器脚本异常')
    check(not failed, '无角色或页面资源加载失败')
    browser.close()

report = {'check_count': len(checks), 'checks': checks, 'errors': errors, 'failed_resources': failed}
(OUT / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'check_count': len(checks), 'errors': errors, 'failed_resources': failed}, ensure_ascii=False))
