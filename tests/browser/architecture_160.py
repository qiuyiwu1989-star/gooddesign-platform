import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/design-160'
OUT.mkdir(parents=True, exist_ok=True)
checks = []
errors = []


def check(value, label):
    if not value:
        raise AssertionError(label)
    checks.append(label)


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1440, 'height': 1000}, color_scheme='light')
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto('http://127.0.0.1:8892/apps/', wait_until='networkidle')
    check(page.locator('.app-card').count() == 8, '应用中心八个应用')
    page.locator('[data-app-kind="experience"]').click()
    check(page.locator('.app-card:visible').count() == 3, '内容学习含拆解实验室共三项')
    page.locator('[data-app-id="xray"]').click()
    check(page.locator('#app-detail-title').inner_text() == '拆解实验室', '拆解应用详情打开')
    check('拆解一件国之重器' in page.locator('.app-case-strip').inner_text(), '拆解真实案例联动')
    check(page.locator('#app-detail-route').get_attribute('href') == '/museum/x-ray', '拆解应用入口正确')
    check('不替代工程手册或实际验证' in page.locator('.app-case-strip').inner_text(), '拆解边界明确')
    page.keyboard.press('Escape')
    page.screenshot(path=str(OUT / 'apps-xray.png'))

    page.goto('http://127.0.0.1:8892/museum/x-ray?slug=2015-02', wait_until='domcontentloaded')
    page.wait_for_selector('#exhChips .chip', timeout=30000)
    check(page.locator('#exhChips .chip').count() >= 8, '拆解实验室保留项目切换')
    page.wait_for_selector('#partList li', timeout=30000)
    check(page.locator('#partList li').count() > 0, '拆解部件列表正常')
    page.screenshot(path=str(OUT / 'xray-jiaolong.png'))

    page.goto('http://127.0.0.1:8892/museum/playground', wait_until='domcontentloaded')
    check('互动学习' in page.locator('body').inner_text(), '互动页更名互动学习')
    check('结果不代表工程精确或实际验证' in page.locator('.lead').inner_text(), '互动模拟边界清楚')
    check(page.locator('[data-group="experiment"]').count() > 0, '动手实验入口保留')
    page.screenshot(path=str(OUT / 'playground-learning.png'))

    page.goto('http://127.0.0.1:8892/project/2015-02.html', wait_until='networkidle')
    check(page.locator('.gd-project-apps a[href="/museum/x-ray?slug=2015-02"]').count() == 1, '项目页拆解入口带项目ID')
    check(page.locator('.gd-project-apps a[href="/museum/playground?slug=2015-02&tab=migrate"]').count() == 1, '项目页互动入口带项目ID')
    page.goto('http://127.0.0.1:8892/atom/2015-02.html', wait_until='networkidle')
    check(page.locator('.gd-project-apps a[href="/museum/x-ray?slug=2015-02"]').count() == 1, '原子页拆解入口带项目ID')
    check(page.locator('.gd-project-apps a[href="/museum/playground?slug=2015-02&tab=migrate"]').count() == 1, '原子页互动入口带项目ID')

    page.goto('http://127.0.0.1:8892/cases/chang-e/', wait_until='networkidle')
    check('不是第二份项目档案' in page.locator('main').inner_text(), '应用案例定位明确')
    check(page.locator('a[href="/inno/dossier/?project=2025-00"]').count() == 1, '案例提供真实档案入口')
    check(page.locator('a[href="/inno/museum/"]').count() == 1, '案例提供展馆入口')
    page.screenshot(path=str(OUT / 'case-positioning.png'))

    page.goto('http://127.0.0.1:8892/about/', wait_until='networkidle')
    check(page.locator('.about-fact strong').all_inner_texts() == ['560', '103', '64', '8'], '关于页应用数同步为8')
    page.goto('http://127.0.0.1:8892/report/', wait_until='networkidle')
    check(page.locator('.dr-core-facts strong').all_inner_texts() == ['560', '103', '64', '8'], '数据总览应用数同步为8')

    for route in ('/apps/', '/museum/playground', '/project/2015-02.html', '/atom/2015-02.html'):
        for width in (1280, 768, 390, 360):
            page.set_viewport_size({'width': width, 'height': 900})
            page.goto('http://127.0.0.1:8892' + route, wait_until='domcontentloaded')
            check(page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'{route}{width}px无横向溢出')
    check(not errors, '无浏览器脚本异常：' + repr(errors))
    browser.close()

report = {'check_count': len(checks), 'checks': checks, 'errors': errors}
(OUT / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
