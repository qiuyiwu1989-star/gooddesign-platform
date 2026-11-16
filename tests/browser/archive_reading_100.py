import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
BASE = os.environ.get('ARCHIVE_PREVIEW_BASE', 'http://127.0.0.1:56061')
OUT = ROOT / 'output/research-100/browser'
OUT.mkdir(parents=True, exist_ok=True)
PROJECTS = ('2025-00', '2021-00', '2024-00', '2024-09', '2020-01', '2015-00', '2025-01', '2025-02', '2019-s19', '2017-01')
REVISIONS = {
    '2025-00': 'research-000008', '2021-00': 'research-000002', '2024-00': 'research-000003',
    '2024-09': 'research-000004', '2020-01': 'research-000002', '2015-00': 'research-000001',
    '2025-01': 'research-000006', '2025-02': 'research-000002', '2019-s19': 'research-000001',
    '2017-01': 'research-000008',
}
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
    for project in PROJECTS:
        page.goto(f'{BASE}/{project}.html', wait_until='networkidle')
        check(page.locator('.reader-module').count() == 8, f'{project}八模块完整')
        check(page.locator('.reader-module[open]').count() == 4, f'{project}核心四模块展开')
        check('项目档案' in page.title(), f'{project}标题正确')
        primary_text = page.locator('#reader-view').inner_text()
        check('AI阅读导读' not in page.locator('body').inner_text(), f'{project}无旧导读标签')
        for internal_text in ('空白保留', '此处另有若干项尚未登记', '这不是项目方事实陈述，完整状态见维护数据', '研究整理版', '8 个阅读模块'):
            check(internal_text not in primary_text, f'{project}阅读区无内部文案：{internal_text}')
        check('machine_text_extraction_not_human_read' not in page.locator('body').inner_text(), f'{project}读取范围中文化')
        check('research-' not in page.locator('.hero').inner_text(), f'{project}主阅读流隐藏研究代号')
        check(page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), f'{project}桌面无横向溢出')
        page.locator('[data-reader-tab="assessment"]').click()
        check(REVISIONS[project] in page.locator('#assessment-view').inner_text(), f'{project}维护视图保留当前版本')
        page.locator('[data-reader-tab="archive"]').click()
        if project == '2025-00':
            check('367 / 476 项项目事实的来源证据尚待重绑' in page.locator('body').inner_text(), '2025-00证据缺口明确')
            check('尚未形成有效评估，旧评估不沿用' in page.locator('#assessment-view').inner_text(), '2025-00旧评估不沿用')
            check(page.locator('.reference-item').count() == 37, '2025-00完整去重引用')
            page.locator('#reader-history>summary').click()
            history_ai = page.locator('#reader-history .research-ai').first
            check(history_ai.get_attribute('open') is not None, '2025-00故事正文直接展开')
            check('校方报道呈现团队在正式任务前后的持续设计与试验积累' in history_ai.inner_text(), '2025-00长期准备正文完整')
            page.locator('[data-reader-tab="library"]').click()
            check(page.locator('.reference-index').is_visible(), '2025-00完整引文集中可核对')
            page.locator('[data-reader-tab="archive"]').click()
            page.screenshot(path=str(OUT / '2025-00-desktop.png'))
        if project == '2021-00':
            check(page.locator('.reference-item').count() == 46, '2021-00完整去重引用')
            check(page.locator('.research-guide').count() == 8, '2021-00八章提要完整')
            check('平台解读聚焦' in page.locator('#reader-innovation').inner_text(), '2021-00导读正文人文化')
            check(page.locator('#reader-innovation #record-TECH-HYBRID').count() == 1, '2021-00技术记录归入设计思路')
            page.locator('#reader-innovation .citation-trigger').first.click()
            check('机器整理，未经人工逐条核读' in page.locator('#citation-dialog').inner_text(), '2021-00来源弹窗标明机器整理')
            page.locator('#citation-close').click()
            page.evaluate("window.dispatchEvent(new Event('beforeprint'))")
            check(page.locator('.reader-module[open]').count() == 8, '2021-00打印前展开全部模块')
            page.evaluate("window.dispatchEvent(new Event('afterprint'))")
            check(page.locator('.reader-module[open]').count() == 4, '2021-00打印后恢复核心模块')
            page.screenshot(path=str(OUT / '2021-00-desktop.png'))
        page.set_viewport_size({'width': 390, 'height': 900})
        page.goto(f'{BASE}/{project}.html?mobile=1#reader-top', wait_until='networkidle')
        check(page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), f'{project}手机无横向溢出')
        check(page.locator('.reader-module[open]').count() == 4, f'{project}手机核心模块仍展开')
        if project in ('2025-00', '2021-00'):
            page.screenshot(path=str(OUT / f'{project}-mobile.png'))
        page.set_viewport_size({'width': 1440, 'height': 1000})
    check(not errors, '无浏览器脚本异常')
    check(not failed, '无资源加载失败')
    browser.close()

report = {'check_count': len(checks), 'checks': checks, 'errors': errors, 'failed_resources': failed}
(OUT / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'check_count': len(checks), 'errors': errors, 'failed_resources': failed}, ensure_ascii=False))
