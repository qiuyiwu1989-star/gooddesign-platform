import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
BASE = os.environ.get('ARCHIVE_PREVIEW_BASE', 'http://127.0.0.1:56061')
OUT = ROOT / 'output/research-100/browser-graph'
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

    page.goto(f'{BASE}/graphs/2025-00.html', wait_until='networkidle')
    check(page.locator('.graph-node.record').count() == 105, '2025-00全部记录节点')
    check(page.locator('.graph-node.module').count() == 8, '2025-00八主题节点')
    check('105' in page.locator('.summary').inner_text(), '2025-00记录总数')
    check('367' in page.locator('.summary').inner_text(), '2025-00证据缺口')
    check(page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), '2025-00图谱桌面无横向溢出')

    page.locator('#node-record-H01').click()
    check('任务之前的长期准备' in page.locator('#record-detail').inner_text(), 'H01详情标题')
    check('持续设计与试验积累' in page.locator('#record-detail').inner_text(), 'H01详情正文')
    check('canonical_name' not in page.locator('#record-detail').inner_text(), '详情无英文字段名')
    check('module-1' not in page.locator('#record-detail').inner_text(), '详情无内部主题编号')
    check('历程与故事' in page.locator('#record-detail').inner_text(), '详情使用中文主题')

    page.locator('#graph-search').fill('长期准备')
    check('显示 1 条记录' in page.locator('#visible-count').inner_text(), '搜索定位单一故事')
    page.locator('#graph-reset').click()
    check('显示 105 条记录' in page.locator('#visible-count').inner_text(), '重置恢复全部记录')

    page.locator('#status-filter').select_option('missing')
    visible = int(page.locator('#visible-count').inner_text().split()[1])
    check(0 < visible < 105, '待补证据筛选有效')
    page.locator('#graph-reset').click()
    page.locator('#module-filter').select_option('module-5')
    check(int(page.locator('#visible-count').inner_text().split()[1]) > 0, '按主题筛选有效')
    page.locator('#graph-reset').click()
    page.screenshot(path=str(OUT / '2025-00-graph.png'))

    page.goto(f'{BASE}/graphs/2021-00.html', wait_until='networkidle')
    check(page.locator('.graph-node.record').count() == 24, '2021-00全部记录节点')
    page.locator('#node-record-TECH-HYBRID').click()
    check('主被动复合悬架的模式切换' in page.locator('#record-detail').inner_text(), '2021-00技术详情')
    check('承担功能' in page.locator('#record-detail').inner_text(), '2021-00中文字段标签')

    page.goto(f'{BASE}/2025-00.html#assessment-view', wait_until='networkidle')
    check(page.locator('.assessment-donut').count() >= 1, '评估环形图存在')
    check(page.locator('.assessment-module-card').count() == 8, '八主题评估卡片')
    check('22.9%' in page.locator('#assessment-view').inner_text(), '可追溯比例正确')
    check('109 / 476' in page.locator('#assessment-view').inner_text(), '证据计数正确')
    page.screenshot(path=str(OUT / '2025-00-assessment.png'))
    page.locator('.graph-link').click()
    check(page.url.endswith('/graphs/2025-00.html'), '评估链接进入知识图谱')

    page.set_viewport_size({'width': 390, 'height': 900})
    page.goto(f'{BASE}/graphs/2025-00.html', wait_until='networkidle')
    check(page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), '2025-00图谱手机无横向溢出')
    page.locator('#node-record-H01').click()
    check('任务之前的长期准备' in page.locator('#record-detail').inner_text(), '手机记录详情可读')
    page.screenshot(path=str(OUT / '2025-00-graph-mobile.png'))

    check(not errors, '无浏览器脚本异常')
    check(not failed, '无资源加载失败')
    browser.close()

report = {'check_count': len(checks), 'checks': checks, 'errors': errors, 'failed_resources': failed}
(OUT / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'check_count': len(checks), 'errors': errors, 'failed_resources': failed}, ensure_ascii=False))
