import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
BASE = os.environ.get('DOSSIER_BASE', 'http://127.0.0.1:8892/inno')
OUT = ROOT / 'output/design-094'
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

    for project in ('2025-00', '2019-s19'):
        page.goto(f'{BASE}/dossier/?project={project}', wait_until='networkidle')
        modules = page.locator('.reader-module')
        check(modules.count() == 8, f'{project}八模块完整')
        check(page.locator('.reader-module[open]').count() == 4, f'{project}核心四模块默认展开')
        for key in ('overview', 'technical', 'innovation', 'validation'):
            check(page.locator(f'#reader-{key}').get_attribute('open') is not None, f'{project}{key}默认展开')
        check(page.locator('#reader-ip').get_attribute('open') is None, f'{project}专利默认收起')
        check(page.locator('.gd-nav').count() == 1 and page.locator('.gd-footer').count() == 1, f'{project}统一顶底栏')
        page.locator('#reader-ip>summary').click()
        check(page.locator('.reader-module[open]').count() == 5, f'{project}第五模块可展开')
        check(page.locator('#reader-overview').get_attribute('open') is not None, f'{project}展开第五模块不关闭概况')
        page.locator('#reader-ip>summary').click()
        check(page.locator('.reader-module[open]').count() == 4, f'{project}可收起第五模块')
        page.locator('[data-gd-theme-toggle]').click()
        check(page.locator('html').get_attribute('data-theme') == 'dark', f'{project}深色主题')
        page.locator('[data-gd-theme-toggle]').click()
        page.evaluate('window.scrollTo(0,0)')
        page.screenshot(path=str(OUT / f'{project}-desktop.png'))
        if project == '2019-s19':
            record = page.locator('#record-MET-020')
            check(record.get_attribute('open') is not None, '079已知记录直接展开')
            check(record.locator('.research-row').count() > 0, '079已知字段直接可见')
            check(record.locator('.citation-trigger').count() > 0, '079原文证据以紧凑注号提供')
            check(page.locator('.research-ai[open]').count() == 0, '079 AI解读默认收起')
        page.evaluate("window.dispatchEvent(new Event('beforeprint'))")
        check(page.locator('.reader-module[open]').count() == 8, f'{project}打印前展开全部模块')
        page.evaluate("window.dispatchEvent(new Event('afterprint'))")
        check(page.locator('.reader-module[open]').count() == 4, f'{project}打印后恢复核心模块')

    page.goto(f'{BASE}/dossier/?project=2025-00#reader-governance', wait_until='networkidle')
    check(page.locator('#reader-governance').get_attribute('open') is not None, '质量维护深链自动展开')
    check(page.locator('#reader-governance').is_visible(), '质量维护深链内容可见')
    check(page.locator('#reader-overview').get_attribute('open') is not None, '深链不关闭核心概况')

    for project in ('2025-00', '2019-s19'):
        page.set_viewport_size({'width': 390, 'height': 900})
        page.goto(f'{BASE}/dossier/?project={project}', wait_until='networkidle')
        check(page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'{project}手机无横向溢出')
        check(page.locator('.reader-module[open]').count() == 4, f'{project}手机核心模块仍展开')
        page.screenshot(path=str(OUT / f'{project}-mobile.png'))

    check(not errors, '无浏览器脚本异常')
    check(not failed, '无资源加载失败')
    browser.close()

report = {'check_count': len(checks), 'checks': checks, 'errors': errors, 'failed_resources': failed}
(OUT / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'check_count': len(checks), 'errors': errors, 'failed_resources': failed}, ensure_ascii=False))
