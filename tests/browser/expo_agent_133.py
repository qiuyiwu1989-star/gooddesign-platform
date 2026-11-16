import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/design-133'
OUT.mkdir(parents=True, exist_ok=True)
URL = 'http://127.0.0.1:8897/expo/'
checks = []
errors = []
run_requests = []


def check(value, label):
    if not value:
        raise AssertionError(label)
    checks.append(label)


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1600, 'height': 1000})
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('request', lambda request: run_requests.append(request.url) if '/expo/api/run' in request.url else None)
    page.route('**/expo/api/places', lambda route: route.fulfill(
        status=200, content_type='application/json',
        body=json.dumps({'places': [{'place': '天台', 'ts': 1, 'counts': {}}]}, ensure_ascii=False)))
    pack = {
        'label': '天台', 'depth': 'standard', 'headline': '产业界定', 'intro': '已有研究概况',
        'sectors': ['装备制造'], 'drivers': [], 'summary_points': [], 'theses': [],
        'boundary': '仅讨论装备制造', 'sources': [], 'chain': [], 'companies': [],
        'personas': [], 'requirements': [], 'matches': [], 'opportunities': [],
        'risks': [], 'metrics': {},
    }
    page.route('**/expo/api/report?*', lambda route: route.fulfill(
        status=200, content_type='application/json',
        body=json.dumps({'pack': pack}, ensure_ascii=False)))
    page.goto(URL, wait_until='networkidle')
    page.wait_for_function("Object.keys(LIT).length >= 3")

    page.locator('[data-p="yuhuan"]').click()
    page.wait_for_selector('#report.on')
    check('玉环产业' in page.locator('.rcover h1').inner_text(), '快捷入口直达玉环已有报告')
    check(not run_requests, '已有报告不发起新研究')
    check(page.locator('#refresh').is_visible(), '保留显式重新研究入口')

    page.locator('#again').click()
    page.locator('#q').fill('天台')
    page.locator('#go').click()
    page.wait_for_selector('#report.on')
    check('天台产业' in page.locator('.rcover h1').inner_text(), '输入已有地名直达缓存报告')
    check(not run_requests, '缓存报告仍未调用研究接口')

    page.locator('#again').click()
    page.evaluate("void startStatic('玉环')")
    page.wait_for_selector('#member-poti.working', state='attached')
    check(page.locator('.member').count() == 7, '七个专业角色分工状态保留')
    check(page.locator('#think.on').is_visible(), '模型等待期显示思维构成')
    check(page.locator('#think .tx').count() == 0, '不显示模型原始文本流')
    page.wait_for_function("document.querySelector('#mc-poti').textContent.includes('假设')")
    check('假设' in page.locator('#mc-poti').inner_text(), '破题角色随事件更新假设数')
    page.wait_for_selector('#member-scout.working', state='attached')
    page.wait_for_timeout(450)
    page.screenshot(path=str(OUT / 'research-team-working.png'))
    page.wait_for_selector('#report.on', timeout=30000)
    check(page.locator('#rdoc .rsec').count() >= 12, '静态回放完整进入正式报告')
    check(page.locator('#member-writer').count() == 1, '成稿角色保持统一状态源')

    page.locator('#again').click()
    page.set_viewport_size({'width': 390, 'height': 844})
    page.evaluate("void startStatic('嘉善')")
    page.wait_for_selector('#member-poti.working', state='attached')
    check(page.evaluate('document.documentElement.scrollWidth <= innerWidth'), '移动窄屏无页面横向溢出')
    page.wait_for_timeout(450)
    page.screenshot(path=str(OUT / 'research-team-mobile.png'))

    check(not errors, '浏览器无 JavaScript 异常：' + repr(errors))
    browser.close()

print(json.dumps({'checks': len(checks), 'passed': checks, 'errors': errors}, ensure_ascii=False, indent=2))
