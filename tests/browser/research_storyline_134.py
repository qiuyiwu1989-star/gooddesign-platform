import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/design-134'
OUT.mkdir(parents=True, exist_ok=True)
URL = 'http://127.0.0.1:8899'
checks = []
errors = []
failed = []
posts = []


def check(condition, label):
    if not condition:
        raise AssertionError(label)
    checks.append(label)


packet = {
    'schema': 'gooddesign-research-packet-1.0',
    'status': 'prepared_context_not_executed',
    'requirement': {
        'title': '实验室样品流转研究',
        'problem': '实验室在交接样品时需要反复口头确认，希望减少漏记，同时保留每次人工复核。',
        'outcome': '减少漏记与重复确认',
        'constraints': '样品记录必须可追溯',
        'status': 'research_proposed_not_customer_confirmed',
        'revision': 1,
    },
    'route': {'id': 'measure', 'name': '先验证问题与量测'},
    'project_references': [{'id': '2019-s19', 'name': '电动压裂泵', 'research': True, 'relation': 'reference_not_adoption_proof'}],
    'method_references': ['R48', 'R42'],
    'unknowns': ['峰值交接量', '现有登记方式', '异常复核责任人', '停止条件', '客户确认'],
    'pending_clarifications': [],
    'model_calls': 0,
    'source_projects_modified': False,
    'engineering_validated': False,
    'expert_reviewed': False,
}
handoff = {'schema': 'gooddesign-canvas-handoff-1.0', 'task_id': 'needs-story-134', 'created_at': '2026-11-15T08:00:00Z', 'packet': packet}

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1440, 'height': 1000}, color_scheme='light')
    page = context.new_page()
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('requestfailed', lambda request: failed.append(request.url))
    page.on('request', lambda request: posts.append(request.url) if request.method == 'POST' else None)

    page.goto(URL + '/needs/', wait_until='networkidle')
    first = page.locator('.gd-needs-step').first.bounding_box()
    second = page.locator('.gd-needs-step').nth(1).bounding_box()
    task_top = page.locator('#task').bounding_box()['y']
    check(abs(first['y'] - second['y']) < 2, '桌面四步导航横向排列')
    check(task_top > first['y'] + first['height'], '步骤位于主回复上方')
    check(page.locator('[data-task-field="unknowns"] > dd > ul > li').count() == 3, '摘要默认只展示三项未知')
    check(page.locator('.gd-needs-unknown-more').count() == 1, '其余未知折叠')
    check('共 8 项待确认' in page.locator('#status').inner_text(), '未知总数保持完整')
    check(page.locator('.gd-needs-prompt').inner_text().count('0 次模型调用') == 0, '对话不重复模型边界')
    page.screenshot(path=str(OUT / 'needs-story-desktop.png'))

    page.evaluate("value => localStorage.setItem('gd-reasoning-canvas-handoff-v1', value)", json.dumps(handoff, ensure_ascii=False))
    page.goto(URL + '/canvas/?from=needs', wait_until='networkidle')
    check(page.locator('#rc-story-home').is_visible(), '新任务显示研究首页')
    check(not page.locator('#rc-viewport').is_visible(), '研究首页不显示空节点图')
    check('实验室样品流转研究' in page.locator('#rc-story-home').inner_text(), '首页显示任务名称')
    check('反复口头确认' in page.locator('#rc-story-home').inner_text(), '首页显示原始问题')
    check('1\n参考项目' in page.locator('.gd-rc-story-counts').inner_text() or '参考项目' in page.locator('.gd-rc-story-counts').inner_text(), '首页显示参考数量')
    check(page.locator('.gd-rc-story-pending li').count() == 3, '首页只展开前三项待确认')
    start_box = page.locator('#rc-start-research').bounding_box()
    check(start_box['y'] + start_box['height'] <= 1000, '开始查证在首屏可见')
    page.screenshot(path=str(OUT / 'canvas-story-home.png'))

    page.locator('#rc-start-research').click()
    check(page.locator('.gd-rc-story-stage').count() == 4, '研究过程归为四阶段')
    check(page.locator('[data-story-node="n2"]').count() >= 1, '开始查证进入n2')
    check('查证' in page.locator('#rc-detail').inner_text(), '当前步骤显示查证详情')
    check(len(posts) == 0, '开始查证没有服务器POST')
    page.locator('[data-story-node="n4"]').first.click()
    check('发散' in page.locator('#rc-detail').inner_text(), '形成方向可进入内部节点')
    page.locator('#rc-overview').click()
    check(page.locator('#rc-viewport').is_visible(), '研究总览显示节点图')
    page.locator('#rc-story-view').click()
    check(page.locator('#rc-story-nav').is_visible(), '返回当前步骤')
    check(not page.locator('#rc-export').is_visible(), '导出默认收进更多菜单')
    page.locator('#rc-more summary').click()
    check(page.locator('#rc-export').is_visible(), '更多菜单保留导出动作')
    page.screenshot(path=str(OUT / 'canvas-story-step.png'))

    page.reload(wait_until='networkidle')
    check(page.locator('#rc-story-home').is_visible(), '无研究痕迹刷新仍显示首页')
    page.set_viewport_size({'width': 390, 'height': 844})
    check(page.evaluate('document.documentElement.scrollWidth <= innerWidth'), '390px研究首页无横向溢出')
    page.screenshot(path=str(OUT / 'canvas-story-mobile.png'))
    page.set_viewport_size({'width': 360, 'height': 844})
    check(page.evaluate('document.documentElement.scrollWidth <= innerWidth'), '360px研究首页无横向溢出')

    demo = browser.new_context(viewport={'width': 1440, 'height': 1000})
    demo_page = demo.new_page()
    demo_page.goto(URL + '/canvas/', wait_until='networkidle')
    check(demo_page.locator('#rc-viewport').is_visible(), '演示工作区仍默认节点图')
    check(not demo_page.locator('#rc-story-home').is_visible(), '演示不显示研究首页')
    demo.close()

    check(not errors, f'无浏览器脚本异常：{errors}')
    check(not failed, f'无网络级资源失败：{failed}')
    browser.close()

report = {'check_count': len(checks), 'checks': checks, 'errors': errors, 'failed_resources': failed, 'post_count': len(posts)}
(OUT / 'browser-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'check_count': len(checks), 'errors': errors, 'failed_resources': failed, 'post_count': len(posts)}, ensure_ascii=False))
