import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/design-082'
OUT.mkdir(parents=True, exist_ok=True)
URL = 'http://127.0.0.1:8892/needs/'
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
    page.goto(URL, wait_until='networkidle')
    check(page.locator('#live-demo').is_hidden(), '初始不自动播放')
    check(page.locator('#live-demo-start').is_enabled(), '动态案例入口可用')
    page.locator('#live-demo-start').click()
    check(page.locator('#live-demo').is_visible(), '点击后显示研究过程')
    check('0 次模型调用' in page.locator('.gd-live-identity').inner_text(), '明确标注零模型调用')
    page.wait_for_function("document.getElementById('live-progress').value >= 1")
    page.locator('#live-pause').click()
    paused = page.locator('#live-progress').evaluate('(el) => el.value')
    page.wait_for_timeout(1450)
    check(page.locator('#live-progress').evaluate('(el) => el.value') == paused, '暂停不推进研究动作')
    check(page.locator('#live-log li').count() == paused, '暂停不重复写入日志')
    check(page.locator('#live-pause').inner_text() == '继续', '暂停后提供继续动作')
    page.locator('#live-pause').click()
    page.wait_for_function(f"document.getElementById('live-progress').value > {paused}")
    check(page.locator('#live-log li').count() == page.locator('#live-progress').evaluate('(el) => el.value'), '继续后日志与完成动作同步')

    page.locator('#live-replay').click()
    page.wait_for_function("document.getElementById('live-progress').value === 1")
    check(page.locator('#live-log li').count() == 1, '重播从第一个动作重新开始')
    check(page.locator('.gd-live-source').count() == 0, '重播清空旧证据')
    page.wait_for_function("document.getElementById('live-progress').value >= 5")
    check(page.locator('.gd-live-source').count() >= 1, '阅读阶段出现真实证据')
    check('4 500 kW' in page.locator('.gd-live-source').first.inner_text(), '证据保留原始功率写法')
    page.screenshot(path=str(OUT / 'research-working-light.png'))
    page.wait_for_function("document.getElementById('live-progress').value === 12", timeout=30000)
    check(page.locator('#live-log li').count() == 12, '十二项研究动作全部完成')
    check(page.locator('.gd-live-source').count() == 4, '四份真实来源卡完整呈现')
    check(page.locator('.gd-live-report').is_visible(), '完成后出现研究结论草案')
    check('非工程结论' in page.locator('.gd-live-report').inner_text(), '报告保留工程边界')
    check('不能合并成统一比例' in page.locator('#live-log').inner_text(), '等效口径不合并')
    check('9项专利只有申报总数' in page.locator('#live-log').inner_text(), '专利缺口明确')
    check(page.locator('#live-pause').is_disabled(), '完成后暂停按钮禁用')
    check(page.locator('#live-state').inner_text() == '演示完成', '完成状态明确')
    check(page.locator('.gd-live-plan li.is-done').count() == 5, '五个研究阶段全部完成')
    page.screenshot(path=str(OUT / 'research-complete-light.png'))

    evidence_href = page.locator('.gd-live-source a').first.get_attribute('href')
    evidence = context.new_page()
    evidence.goto('http://127.0.0.1:8892' + evidence_href, wait_until='networkidle')
    check('project=2019-s19' in evidence.url, '证据进入真实项目档案')
    check('#record-MET-001' in evidence.url, '证据定位到具体指标')
    check(evidence.locator('#record-MET-001').evaluate('(el) => el.open'), '档案深链展开对应记录')
    evidence.close()

    page.locator('[data-gd-theme-toggle]').click()
    check(page.locator('html').get_attribute('data-theme') == 'dark', '深色主题生效')
    page.wait_for_timeout(300)
    page.screenshot(path=str(OUT / 'research-complete-dark.png'))
    page.locator('[data-gd-theme-toggle]').click()

    page.locator('#live-close').click()
    check(page.locator('#live-demo').is_hidden(), '关闭隐藏动态案例')
    check(page.evaluate('document.activeElement.id') == 'live-demo-start', '关闭后焦点返回入口')
    page.locator('#nw-problem').fill('验证原有需求流程在演示后仍可使用')
    page.locator('[data-action="next"]').click()
    check('选择参考资料' in page.locator('#task').inner_text(), '原需求工作流不受演示影响')

    for width in (390, 360):
        page.set_viewport_size({'width': width, 'height': 844})
        page.goto(URL, wait_until='networkidle')
        page.locator('#live-demo-start').click()
        page.wait_for_function("document.getElementById('live-progress').value >= 1")
        check(page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'{width}px动态案例无横向溢出')
        heights = page.locator('.gd-live-controls button').evaluate_all('(els) => els.map(el => el.getBoundingClientRect().height)')
        check(all(height >= 44 for height in heights), f'{width}px播放控制至少44px')
        if width == 390:
            page.screenshot(path=str(OUT / 'research-working-mobile.png'))
        page.locator('#live-close').click()
        check(page.evaluate('document.activeElement.id') == 'live-demo-start', f'{width}px关闭后焦点返回')

    reduced = browser.new_context(viewport={'width': 1280, 'height': 900}, color_scheme='light', reduced_motion='reduce')
    reduced_page = reduced.new_page()
    reduced_page.goto(URL, wait_until='networkidle')
    reduced_page.locator('#live-demo-start').click()
    check(reduced_page.locator('#live-progress').evaluate('(el) => el.value') == 12, '减少动态模式直接呈现完整案例')
    check(reduced_page.locator('#live-log li').count() == 12, '减少动态模式不逐项自动播放')
    check(reduced_page.locator('#live-state').inner_text() == '演示完成', '减少动态模式完成状态一致')
    reduced.close()

    check(not errors, '无浏览器脚本异常')
    check(not failed, '无页面资源加载失败')
    browser.close()

report = {'check_count': len(checks), 'checks': checks, 'errors': errors, 'failed_resources': failed}
(OUT / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'check_count': len(checks), 'errors': errors, 'failed_resources': failed}, ensure_ascii=False))
