import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[2]
BASE = os.environ.get('GOODDESIGN_BASE', 'http://127.0.0.1:8892/inno')
OUT = ROOT / 'output/design-095'
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

    for route, marker in (
        ('/about/', '让真实创新'),
        ('/model/', '创新设计大模型'),
        ('/guide/', '从当前任务，选择正确入口'),
        ('/apps/', '同一个知识底座，长出不同的创新应用'),
        ('/cases/chang-e/', '一个嫦娥项目，支撑多种应用'),
        ('/cases/pump-079/', '6000HP电动压裂泵'),
        ('/cases/rubber-tapping/', '割胶机器人'),
        ('/cases/mcp-research/', 'Agent如何读取项目'),
        ('/cases/yuhuan/', '玉环产业创新专区'),
    ):
        response = page.goto(BASE + route, wait_until='networkidle')
        check(response.status == 200, f'{route}返回200')
        check(marker in page.locator('body').inner_text(), f'{route}核心内容正确')
        check(page.locator('.gd-nav').count() == 1 and page.locator('.gd-footer').count() == 1, f'{route}顶底栏唯一')
        check(page.locator('[data-gd-nav="apps"]').count() == 1, f'{route}应用中心导航存在')
        check(page.locator('[data-gd-nav="about"]').count() == 1, f'{route}关于入口存在')

    page.goto(BASE + '/apps/', wait_until='networkidle')
    for kind, count in (('live', 4), ('pilot', 1), ('planned', 1), ('all', 6)):
        page.locator(f'[data-app-filter="{kind}"]').click()
        check(page.locator('.app-card:visible').count() == count, f'应用筛选{kind}为{count}项')
        check(f'显示 {count} 项应用' in page.locator('#app-count').inner_text(), f'应用筛选计数{kind}')
    page.locator('[data-app-filter="all"]').click()
    page.screenshot(path=str(OUT / 'apps-desktop.png'))

    page.goto(BASE + '/model/', wait_until='networkidle')
    check('四种核心能力' in page.locator('body').inner_text(), '大模型四能力完整')
    check('尚不宣称' in page.locator('body').inner_text(), '大模型边界明确')
    check('项目档案数据库' in page.locator('body').inner_text(), '大模型底座明确')
    page.screenshot(path=str(OUT / 'model-desktop.png'))

    page.goto(BASE + '/dossier/?project=2019-s19', wait_until='networkidle')
    trigger = page.locator('.citation-trigger').first
    trigger.click()
    dialog = page.locator('#citation-dialog')
    check(dialog.is_visible(), '桌面引用预览打开')
    check(dialog.evaluate('(el)=>el.open'), '引用使用独立dialog')
    check(dialog.locator('#citation-title').inner_text() != '', '引用标题存在')
    check(dialog.locator('#citation-quote').inner_text() != '', '引用原文存在')
    check(trigger.get_attribute('aria-expanded') == 'true', '引用展开状态同步')
    page.screenshot(path=str(OUT / 'citation-desktop.png'))
    page.locator('#citation-close').click()
    check(not dialog.is_visible(), '引用关闭按钮有效')
    expect(trigger).to_have_attribute('aria-expanded', 'false')
    check(trigger.evaluate('(el)=>el===document.activeElement'), '引用关闭焦点返回')

    page.set_viewport_size({'width': 390, 'height': 900})
    page.goto(BASE + '/dossier/?project=2019-s19', wait_until='networkidle')
    trigger = page.locator('.citation-trigger').first
    trigger.click()
    check(dialog.is_visible(), '移动引用面板打开')
    rect = dialog.bounding_box()
    check(rect['width'] <= 390, '移动引用不超出视口')
    check(rect['y'] + rect['height'] <= 901, '移动引用位于底部')
    page.screenshot(path=str(OUT / 'citation-mobile.png'))
    page.keyboard.press('Escape')
    check(not dialog.is_visible(), '移动Escape关闭引用')
    check(page.evaluate('document.documentElement.scrollWidth <= innerWidth'), '移动档案无横向溢出')

    for route in ('/about/', '/model/', '/guide/', '/apps/'):
        page.goto(BASE + route, wait_until='networkidle')
        check(page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'{route}移动无横向溢出')

    for route, target in (('/needs-v2/', '/inno/needs/'),('/projects/', '/inno/'),('/learn/', '/inno/museum/#education')):
        response = page.request.get(BASE + route, max_redirects=0)
        check(response.status in (301, 302), f'{route}执行重定向')
        check(response.headers.get('location', '').endswith(target), f'{route}重定向目标正确')

    check(not errors, '无浏览器脚本异常')
    check(not failed, '无资源加载失败')
    browser.close()

report = {'check_count': len(checks), 'checks': checks, 'errors': errors, 'failed_resources': failed}
(OUT / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'check_count': len(checks), 'errors': errors, 'failed_resources': failed}, ensure_ascii=False))
