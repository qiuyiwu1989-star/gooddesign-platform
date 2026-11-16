import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/design-165'
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
    context = browser.new_context(viewport={'width': 1440, 'height': 1000}, accept_downloads=True, permissions=['clipboard-read', 'clipboard-write'])
    page = context.new_page()
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('requestfailed', lambda request: failed.append(request.url))

    page.goto('http://127.0.0.1:8892/apps/', wait_until='networkidle')
    check(page.locator('.app-card').count() == 12, '应用中心十二项应用')
    page.locator('[data-app-id="lab"]').click()
    check(page.locator('#app-detail-title').inner_text() == '极限实验室', '实验室详情可打开')
    check(page.locator('#app-detail-route').get_attribute('href') == '/lab/', '实验室路由正确')
    page.keyboard.press('Escape')

    page.goto('http://127.0.0.1:8892/lab/', wait_until='networkidle')
    page.locator('#lab-start').click()
    page.wait_for_timeout(450)
    page.locator('#lab-pause').click()
    check('暂停' in page.locator('#lab-status').inner_text(), '实验可暂停')
    page.locator('#lab-start').click()
    page.wait_for_timeout(3200)
    check(page.locator('.ia-run').count() == 1, '首次实验形成复盘')
    page.locator('#lab-start').click()
    page.wait_for_timeout(3200)
    check(page.locator('.ia-run').count() == 2, '第二次实验形成A/B比较')
    page.reload(wait_until='networkidle')
    check(page.locator('.ia-run').count() == 2, '实验记录刷新恢复')
    with page.expect_download() as download_info:
        page.locator('#lab-export').click()
    download = download_info.value
    download.save_as(str(OUT / 'lab-observation.txt'))
    check('教学模拟' in (OUT / 'lab-observation.txt').read_text(), '观察卡保留模拟边界')
    page.screenshot(path=str(OUT / 'lab-desktop.png'))

    page.goto('http://127.0.0.1:8892/quest/', wait_until='networkidle')
    check(page.locator('.ia-quest-card:not(:disabled)').count() == 1, '初始仅首关开放')
    page.locator('#quest-begin').click()
    page.locator('.ia-quest-options button').first.click()
    page.locator('#quest-next').click()
    page.locator('.ia-quest-options button').first.click()
    page.locator('#quest-next').click()
    page.locator('#quest-next-level').click()
    check(page.locator('.ia-quest-card:not(:disabled)').count() == 2, '首关完成后解锁第二关')
    page.locator('#quest-begin').click()
    page.locator('.ia-quest-options button').first.click()
    page.locator('#quest-next').click()
    page.locator('.ia-quest-options button').first.click()
    page.locator('#quest-next').click()
    check('已完成 2 / 8' in page.locator('#quest-progress').inner_text(), '两关进度正确')
    page.reload(wait_until='networkidle')
    check('已完成 2 / 8' in page.locator('#quest-progress').inner_text(), '闯关进度刷新恢复')
    with page.expect_download() as download_info:
        page.locator('#quest-export').click()
    download = download_info.value
    download.save_as(str(OUT / 'quest-tasks.txt'))
    check('第 1 关' in (OUT / 'quest-tasks.txt').read_text(), '任务单导出完整')

    page.goto('http://127.0.0.1:8892/studio/', wait_until='networkidle')
    page.locator('#studio-name').fill('深海返回舱')
    page.locator('#studio-problem').fill('怎样让极端环境中的作业更安全？')
    page.locator('#studio-desc').fill('从真实项目的结构和安全设计获得启发，保留需要验证的条件。')
    page.locator('[data-value="coral"]').click()
    check(page.locator('#studio-preview').get_attribute('data-theme') == 'coral', '作品主题实时更新')
    before = page.locator('#studio-title').evaluate('(el)=>el.style.left')
    box = page.locator('#studio-title').bounding_box()
    page.mouse.move(box['x'] + 40, box['y'] + 20)
    page.mouse.down()
    page.mouse.move(box['x'] + 160, box['y'] + 100, steps=8)
    page.mouse.up()
    after = page.locator('#studio-title').evaluate('(el)=>el.style.left')
    check(before != after, '标题可拖动定位')
    page.locator('#studio-save').click()
    page.reload(wait_until='networkidle')
    check(page.locator('#studio-name').input_value() == '深海返回舱', '创作草稿刷新恢复')
    page.locator('#studio-share').click()
    page.wait_for_timeout(150)
    shared_url = page.evaluate('navigator.clipboard.readText()')
    page.goto(shared_url, wait_until='networkidle')
    check(page.locator('#studio-name').input_value() == '深海返回舱', '分享链接恢复作品')
    with page.expect_download() as download_info:
        page.locator('#studio-export').click()
    download = download_info.value
    download.save_as(str(OUT / 'studio-work.png'))
    check((OUT / 'studio-work.png').read_bytes()[:8] == b'\x89PNG\r\n\x1a\n', '导出真实PNG作品')
    page.screenshot(path=str(OUT / 'studio-desktop.png'))

    page.goto('http://127.0.0.1:8892/transfer/', wait_until='networkidle')
    page.locator('#transfer-mechanism button').first.click()
    page.locator('#transfer-industry button[data-value="robot"]').click()
    page.locator('#transfer-problem').fill('我们的移动机器人需要在复杂环境中稳定工作，但现有系统能耗高且维护困难。')
    page.locator('#transfer-review').click()
    check(page.locator('#transfer-step-3').is_visible(), '迁移双侧映射形成')
    check('差异与未知' in page.locator('#transfer-map').inner_text(), '迁移保留差异未知')
    check('验证计划' in page.locator('#transfer-map').inner_text(), '迁移形成验证计划')
    page.locator('#transfer-copy').click()
    page.wait_for_timeout(150)
    check('研究上下文' in page.evaluate('navigator.clipboard.readText()'), '研究上下文可复制')
    with context.expect_page() as new_page_info, page.expect_download() as download_info:
        page.locator('#transfer-export').click()
    download = download_info.value
    download.save_as(str(OUT / 'transfer-plan.txt'))
    check('建议验证' in (OUT / 'transfer-plan.txt').read_text(), '迁移验证计划可导出')
    new_page = new_page_info.value
    new_page.wait_for_load_state('domcontentloaded')
    check('/needs/' in new_page.url, '导出后进入需求研究')
    new_page.close()
    page.screenshot(path=str(OUT / 'transfer-desktop.png'))

    for app in ('lab', 'quest', 'studio', 'transfer'):
        for width in (1280, 768, 390, 360):
            page.set_viewport_size({'width': width, 'height': 900})
            page.goto(f'http://127.0.0.1:8892/{app}/', wait_until='networkidle')
            check(page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'{app}在{width}px无横向溢出')
    page.goto('http://127.0.0.1:8892/museum/playground?tab=migrate', wait_until='networkidle')
    check('/transfer/' in page.url and 'tab=migrate' in page.url, '旧技术迁移参数正确映射')
    check(not errors, '无浏览器脚本异常：' + repr(errors))
    check(not failed, '无资源加载失败：' + repr(failed))
    browser.close()

report = {'check_count': len(checks), 'checks': checks, 'errors': errors, 'failed_resources': failed}
(OUT / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
