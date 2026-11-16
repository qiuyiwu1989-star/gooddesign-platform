import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/design-148'
OUT.mkdir(parents=True, exist_ok=True)
checks = []
errors = []


def check(value, label):
    if not value:
        raise AssertionError(label)
    checks.append(label)


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1600, 'height': 1000})
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.route('**/expo/api/places', lambda route: route.fulfill(
        status=200, content_type='application/json', body='{"places":[]}'))
    page.goto('http://127.0.0.1:8897/expo/', wait_until='networkidle')
    page.evaluate("void startStatic('嘉善')")
    page.wait_for_selector('.worker-card')
    check(page.locator('.worker-card').count() == 3, '等待期立即展开三个角色工位')
    check(page.locator('.worker-card .worker-avatar').count() == 3, '每个工位有独立角色形象')
    check(page.locator('.worker-card .agent-pointer').count() == 3, '每个工位有角色鼠标指针')
    check(page.locator('.worker-card .worker-line').count() == 3, '每个工位有持续工作动线')
    names = page.locator('.worker-card small').all_inner_texts()
    check(len(set(names)) == 3, '三个工位分工与角色不同')
    check(page.evaluate("document.querySelectorAll('.worker-avatar')[0].naturalWidth > 0"), '工位图片已内嵌且可显示')
    page.locator('#pause').click()
    count = page.locator('#orch-work').inner_text()
    page.wait_for_timeout(350)
    check(page.locator('#orch-work').inner_text() == count, '工位动画不虚构工作计数')
    check(page.locator('.worker-card .agent-pointer').first.evaluate("el=>getComputedStyle(el).animationPlayState") == 'paused', '暂停时工位指针冻结')
    page.locator('#pause').click()
    page.evaluate("handleEvent({type:'activity',stage:LIVE.currentStage,kind:'sources',n:1,label:'读取公开资料'})")
    check('读取公开资料' in page.locator('.research-stream').inner_text(), '真实事件继续展开成果卡')
    page.wait_for_timeout(300)
    page.screenshot(path=str(OUT / 'agent-workers.png'))
    page.evaluate("void startStatic('玉环')")
    page.wait_for_selector('#report.on', timeout=30000)
    check(page.locator('#rdoc .rsec').count() >= 12, '完整回放与报告交付不回归')
    check(not errors, '浏览器无JavaScript异常：' + repr(errors))
    browser.close()

print(json.dumps({'checks': len(checks), 'passed': checks, 'errors': errors}, ensure_ascii=False, indent=2))
