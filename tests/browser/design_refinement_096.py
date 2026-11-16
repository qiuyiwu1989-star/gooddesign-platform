import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
BASE = os.environ.get('GOODDESIGN_BASE', 'http://127.0.0.1:8892/inno')
OUT = ROOT / 'output/design-096'
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
    page = browser.new_page(viewport={'width': 1440, 'height': 1000})
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('requestfailed', lambda request: failed.append(request.url))

    page.goto(BASE + '/', wait_until='networkidle')
    check(page.locator('.model-explorer').count() == 1, '模型区为真实关系图')
    check(page.locator('.model-step').count() == 4, '四层研究路径完整')
    check('45条记录，180个有值事实字段' in page.locator('.model-detail').inner_text(), '079证据直接可见')
    for key, marker in (('method', 'R48、R14、R17'), ('research', '42条带边界AI分析'), ('application', '需求研究、企业创新与MCP')):
        page.locator(f'[data-model-step="{key}"]').click()
        check(marker in page.locator('.model-detail').inner_text(), f'{key}详情正确切换')
        check(page.locator(f'[data-model-step="{key}"]').get_attribute('aria-pressed') == 'true', f'{key}选中状态正确')
    page.screenshot(path=str(OUT / 'model-desktop.png'))

    page.goto(BASE + '/apps/', wait_until='networkidle')
    check(page.locator('.app-store').count() == 1, '应用中心为市场式布局')
    check(page.locator('.app-card').count() == 8, '七个应用入口完整')
    page.locator('[data-app-id="needs"]').click()
    check(page.locator('#app-sheet').evaluate('el => el.open') is True, '详情弹层打开')
    check(page.locator('#app-detail-title').inner_text() == '需求研究', '应用详情切换')
    check('6000HP电动压裂泵' in page.locator('.app-case-strip').inner_text(), '案例随应用联动')
    check(page.locator('#app-detail-route').get_attribute('href') == '/needs/', '应用入口正确')
    page.locator('#app-sheet-close').click()
    page.locator('[data-app-id="mcp"]').click()
    check('Agent如何读取项目' in page.locator('.app-case-strip').inner_text(), 'MCP案例联动')
    page.locator('#app-sheet-close').click()
    page.screenshot(path=str(OUT / 'apps-desktop.png'))

    for kind, count in (('experience', 3), ('innovation', 3), ('access', 2), ('all', 8)):
        page.locator(f'[data-app-kind="{kind}"]').click()
        check(page.locator('.app-card:visible').count() == count, f'{kind}筛选数量正确')
        check(f'显示 {count} 项应用' in page.locator('#app-count').inner_text(), f'{kind}计数正确')

    for route in ('/model/', '/apps/'):
        page.set_viewport_size({'width': 390, 'height': 900})
        page.goto(BASE + route, wait_until='networkidle')
        check(page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'{route}移动无横向溢出')
        check(page.locator('.gd-nav').count() == 1 and page.locator('.gd-footer').count() == 1, f'{route}顶底栏唯一')
        page.screenshot(path=str(OUT / (route.strip('/').replace('/', '-') + '-mobile.png')))

    check(not errors, '无浏览器脚本异常')
    check(not failed, '无资源加载失败')
    browser.close()

report = {'check_count': len(checks), 'checks': checks, 'errors': errors, 'failed_resources': failed}
(OUT / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'check_count': len(checks), 'errors': errors, 'failed_resources': failed}, ensure_ascii=False))
