import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/design-129'
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


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1440, 'height': 1000}, color_scheme='light', accept_downloads=True)
    page = context.new_page()
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('requestfailed', lambda request: failed.append(request.url))
    page.on('request', lambda request: posts.append(request.url) if request.method == 'POST' else None)
    page.goto(URL + '/needs/', wait_until='networkidle')

    check(page.locator('#nw-problem').is_visible(), '首屏真实问题可见')
    check(not page.locator('.gd-needs-optional').evaluate('(el) => el.open'), '可选字段默认收起')
    next_box = page.locator('[data-action="next"]').bounding_box()
    check(next_box['y'] + next_box['height'] <= 1000, '首屏继续按钮在初始视口内')
    page.locator('[data-action="next"]').click()
    check('先描述真实问题' in page.locator('.gd-needs-message').inner_text(), '空问题被阻止')

    page.locator('.gd-needs-optional summary').click()
    page.locator('#nw-title').fill('社区助餐配送研究')
    page.locator('#nw-outcome').fill('减少重复沟通与等待，保留异常订单的人工复核')
    page.locator('#nw-constraints').fill('不得公开老人住址与联系方式')
    problem = '社区助餐在午高峰需要反复电话确认订单，志愿者容易重复登记，希望减少等待并保留服务追溯。'
    page.locator('#nw-problem').fill(problem)
    check(problem in page.locator('[data-task-field="problem"]').inner_text(), '任务卡同步用户问题')
    check('不得公开老人住址' in page.locator('[data-task-field="constraints"]').inner_text(), '任务卡同步约束')
    page.screenshot(path=str(OUT / 'needs-problem-desktop.png'))
    page.locator('[data-action="next"]').click()

    check(page.locator('#project-options .gd-needs-option').count() > 0, '真实项目目录加载')
    check(page.locator('#method-options .gd-needs-option').count() > 0, '真实方法目录加载')
    page.locator('#project-options .gd-needs-option').first.click()
    page.locator('#method-options .gd-needs-option').first.click()
    check(page.locator('#selected-projects .gd-needs-chip').count() == 1, '项目明确加入参考')
    check(page.locator('#selected-methods .gd-needs-chip').count() == 1, '方法明确加入参考')
    page.locator('[data-action="next"]').click()
    page.locator('[data-route="measure"]').click()
    check(page.locator('[data-route="measure"]').get_attribute('aria-pressed') == 'true', '路线由用户明确选择')
    page.locator('[data-action="next"]').click()
    check('社区助餐配送研究' in page.locator('#status').inner_text(), '核对页保留任务名称')
    page.screenshot(path=str(OUT / 'needs-review-desktop.png'))

    page.locator('[data-action="canvas"]').click()
    page.wait_for_url('**/canvas/?workspace=needs-*', wait_until='networkidle')
    workspace_id = page.url.split('workspace=', 1)[1]
    check(workspace_id.startswith('needs-'), '生成独立任务ID')
    check('社区助餐配送研究' in page.title(), '画布标题来自任务包')
    check(page.locator('#rc-story-home').is_visible(), '新任务先进入研究首页')
    check(problem in page.locator('#rc-story-home').inner_text(), '研究首页保留用户原始陈述')
    check(page.locator('#rc-gdrp').is_disabled(), '新任务不套用演示GDRP')
    check(page.locator('#rc-report').is_disabled(), '新任务不套用演示报告')
    check(page.locator('#rc-flow-run').is_disabled(), '新任务不执行演示推理')
    check(page.evaluate("localStorage.getItem('gd-reasoning-canvas-handoff-v1')") is None, '交接键只消费一次')
    body = page.locator('body').inner_text()
    for polluted in ('柔顺限深刀头', '固定仿形割胶装置', '月壤采样', '胶园树径'):
        check(polluted not in body, f'画布不含演示内容：{polluted}')
    page.screenshot(path=str(OUT / 'canvas-imported-desktop.png'))

    page.locator('#rc-start-research').click()
    check(page.locator('#rc-story-nav').is_visible(), '开始查证进入四阶段步骤视图')
    check(len(posts) == 0, '开始查证与普通编辑不写入服务器')
    page.locator('#rc-overview').click()
    check(page.locator('#rc-viewport').is_visible(), '可切换研究总览')
    page.locator('#rc-story-view').click()
    check(page.locator('#rc-story-nav').is_visible(), '可返回当前步骤')
    page.locator('#rc-save').click()
    page.wait_for_function("document.getElementById('rc-workspace-status').textContent.includes('已保存 · r1')")
    check(len(posts) == 1, '显式保存只发送一次POST')
    page.reload(wait_until='networkidle')
    check(page.locator('#rc-story-home').is_visible(), '无研究痕迹时刷新仍回到研究首页')
    page.locator('#rc-start-research').click()
    page.locator('[data-story-node="n1"]').click()
    check(problem in page.locator('#rc-detail').inner_text(), '刷新恢复任务内容')
    check('社区助餐配送研究' in page.title(), '刷新恢复独立工作区')

    page.locator('#rc-more summary').click()
    with page.expect_download() as download_info:
        page.locator('#rc-export').click()
    download = download_info.value
    markdown = Path(download.path()).read_text(encoding='utf-8')
    check('社区助餐配送研究' in markdown and problem in markdown, '推理档案导出当前任务')
    check('柔顺限深刀头' not in markdown and 'GD-CRE' not in markdown, '推理档案不混入演示内容')

    page.set_viewport_size({'width': 390, 'height': 844})
    check(page.evaluate('document.documentElement.scrollWidth <= innerWidth'), '390px画布无页面横向溢出')
    page.screenshot(path=str(OUT / 'canvas-imported-mobile.png'))

    page.goto(URL + '/needs/', wait_until='networkidle')
    check(page.evaluate('document.documentElement.scrollWidth <= innerWidth'), '390px需求页无页面横向溢出')
    page.screenshot(path=str(OUT / 'needs-mobile-light.png'))
    page.locator('[data-gd-theme-toggle]').click()
    check(page.locator('html').get_attribute('data-theme') == 'dark', '深色主题切换')
    page.wait_for_timeout(400)
    check(page.locator('body').evaluate('(el) => getComputedStyle(el).backgroundColor') == 'rgb(20, 19, 31)', '深色正文背景使用语义令牌')
    check(page.locator('.gd-needs-heading h1').evaluate('(el) => getComputedStyle(el).color') == 'rgb(236, 238, 255)', '深色标题对比色正确')
    check(page.locator('.gd-needs-heading-actions .gd-button').last.evaluate('(el) => getComputedStyle(el).color') == 'rgb(236, 238, 255)', '深色次级按钮文字清晰')
    page.screenshot(path=str(OUT / 'needs-mobile-dark.png'))
    page.set_viewport_size({'width': 360, 'height': 844})
    check(page.evaluate('document.documentElement.scrollWidth <= innerWidth'), '360px需求页无页面横向溢出')
    heights = page.locator('.gd-needs-step, [data-action="next"]').evaluate_all('(els) => els.map(el => el.getBoundingClientRect().height)')
    check(all(height >= 44 for height in heights), '移动步骤与主按钮触控高度至少44px')

    check(not errors, f'无浏览器脚本异常：{errors}')
    check(not failed, f'无网络级资源加载失败：{failed}')
    browser.close()

report = {'check_count': len(checks), 'checks': checks, 'errors': errors, 'failed_resources': failed, 'post_count': len(posts)}
(OUT / 'browser-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'check_count': len(checks), 'errors': errors, 'failed_resources': failed, 'post_count': len(posts)}, ensure_ascii=False))
