import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/design-158'
OUT.mkdir(parents=True, exist_ok=True)
checks = []
errors = []
failed = []


def check(value, label):
    if not value:
        raise AssertionError(label)
    checks.append(label)


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1440, 'height': 1000}, color_scheme='light', accept_downloads=True)
    page = context.new_page()
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('requestfailed', lambda request: failed.append(request.url))
    page.goto('http://127.0.0.1:8892/needs/', wait_until='networkidle')
    unknown = page.locator('.gd-needs-unknown-more')
    check(not unknown.evaluate('(el)=>el.open'), '全部待确认默认收合')
    check('查看全部 8 项待确认' in unknown.locator('summary').inner_text(), '待确认数量正确')
    check(not page.locator('.gd-needs-unknowns').is_visible(), '收合时不渲染多个待确认卡片')
    unknown.locator('summary').click()
    check(unknown.evaluate('(el)=>el.open'), '待确认可展开')
    check(unknown.locator('.gd-needs-unknowns li').count() == 8, '展开保留全部八项')
    unknown.locator('summary').click()
    check(page.locator('#nw-problem').is_visible(), '真实问题输入保留')
    check(not page.locator('.gd-needs-optional').evaluate('(el)=>el.open'), '可选字段保持收合')
    page.screenshot(path=str(OUT / 'needs-desktop.png'))

    page.locator('#nw-problem').fill('高功率工业泵改造需要核对不同来源的功率口径，同时保留现有工况边界。')
    page.reload(wait_until='networkidle')
    check('高功率工业泵改造' in page.locator('#nw-problem').input_value(), '浏览器草稿刷新恢复')
    page.locator('[data-action="next"]').click()
    check(page.locator('#project-options .gd-needs-option').count() > 0, '真实项目参考加载')
    check(page.locator('#method-options .gd-needs-option').count() > 0, '真实方法参考加载')
    page.locator('#project-options .gd-needs-option').first.click()
    page.locator('#method-options .gd-needs-option').first.click()
    check(page.locator('#selected-projects .gd-needs-chip').count() == 1, '项目明确加入参考')
    check(page.locator('#selected-methods .gd-needs-chip').count() == 1, '方法明确加入参考')
    page.locator('[data-action="next"]').click()
    page.locator('[data-route="measure"]').click()
    check(page.locator('[data-route="measure"]').get_attribute('aria-pressed') == 'true', '路线明确选择')
    page.locator('[data-action="next"]').click()
    check('请核对研究任务卡' in page.locator('#task').inner_text(), '进入核对计划')
    page.locator('[data-action="copy"]').click()
    check(page.locator('#handoff').evaluate('(el)=>el.open'), '研究交接弹层打开')
    check('model_calls' in page.locator('#handoff-text').input_value(), '交接包含模型调用边界')
    page.locator('#handoff .gd-needs-handoff-head button').click()
    with page.expect_download() as download_info:
        page.locator('[data-action="download"]').click()
    exported = json.loads(Path(download_info.value.path()).read_text())
    check(exported['model_calls'] == 0, '导出保持0次模型调用')
    check(exported['source_projects_modified'] is False and exported['engineering_validated'] is False, '导出不改源事实或工程状态')
    page.screenshot(path=str(OUT / 'needs-review.png'))

    page.locator('#live-demo-start').click()
    page.wait_for_function("document.getElementById('live-progress').value >= 1")
    page.locator('#live-pause').click()
    paused = page.locator('#live-progress').evaluate('(el)=>el.value')
    page.wait_for_timeout(1400)
    check(page.locator('#live-progress').evaluate('(el)=>el.value') == paused, '动态案例暂停不推进')
    page.screenshot(path=str(OUT / 'live-desktop.png'))
    page.locator('#live-close').click()
    check(page.evaluate('document.activeElement.id') == 'live-demo-start', '关闭案例焦点返回入口')

    for width in (1440, 1280, 1024, 768, 390, 360):
        page.set_viewport_size({'width': width, 'height': 900})
        page.goto('http://127.0.0.1:8892/needs/', wait_until='networkidle')
        check(page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'需求页{width}px无横向溢出')
        if width == 390:
            page.screenshot(path=str(OUT / 'needs-mobile.png'), full_page=True)
        if width <= 390:
            page.locator('#live-demo-start').click()
            page.wait_for_timeout(400)
            widths = page.locator('.gd-live,.gd-live-activity,.gd-live-current').evaluate_all('(els)=>els.map(e=>({client:e.clientWidth,scroll:e.scrollWidth}))')
            check(all(item['scroll'] <= item['client'] for item in widths), f'{width}px动态案例内容不被网格裁切')
            page.locator('#live-close').click()

    page.set_viewport_size({'width': 390, 'height': 844})
    page.goto('http://127.0.0.1:8892/needs/', wait_until='networkidle')
    check(not page.locator('.gd-needs-unknowns').is_visible(), '移动端待确认默认收合')
    page.locator('[data-gd-theme-toggle]').click()
    page.wait_for_timeout(700)
    check(page.locator('html').get_attribute('data-theme') == 'dark', '深色主题生效')
    check(page.locator('.gd-needs-heading h1').evaluate('(el)=>getComputedStyle(el).color') == 'rgb(236, 238, 255)', '深色标题对比正确')
    page.screenshot(path=str(OUT / 'needs-mobile-dark.png'))

    page.emulate_media(media='print')
    check(page.locator('.gd-needs-actions').first.evaluate('(el)=>getComputedStyle(el).display') == 'none', '打印隐藏操作按钮')
    check(page.locator('#task').is_visible(), '打印保留任务内容')
    page.emulate_media(media='screen')
    reduced = browser.new_context(viewport={'width': 1280, 'height': 900}, reduced_motion='reduce')
    rp = reduced.new_page()
    rp.goto('http://127.0.0.1:8892/needs/', wait_until='networkidle')
    rp.locator('#live-demo-start').click()
    check(rp.locator('#live-progress').evaluate('(el)=>el.value') == 12, '减少动态直接完整呈现案例')
    check(rp.locator('#live-log li').count() == 12, '减少动态十二动作完整')
    reduced.close()
    check(not errors, '无浏览器脚本异常：' + repr(errors))
    check(not failed, '无资源加载失败：' + repr(failed))
    browser.close()

report = {'check_count': len(checks), 'checks': checks, 'errors': errors, 'failed_resources': failed}
(OUT / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
