import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/design-142'
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
    page.wait_for_selector('#log .ln.show')
    check(page.locator('#log').is_visible(), '左侧连续执行流可见')
    check(page.locator('#team').is_hidden(), '左侧不再重复显示角色卡')
    check('研究统筹' in page.locator('#loghead').inner_text(), '左侧只有小好统筹Agent')
    check(page.locator('#graph .agent-ip').count() == 9, '上方分工主视图保留')
    check('项过程' in page.locator('#orch-work').inner_text(), '真实过程数量可见')

    page.evaluate("handleEvent({type:'think',stage:0,tail:'{\"headline\":\"嘉善产业基础\"}',progress:50})")
    page.evaluate("handleEvent({type:'think',stage:0,tail:'{\"headline\":\"嘉善产业基础与结构\"}',progress:100})")
    check(page.locator('#thinking-0').count() == 1, '连续思考原位更新不刷屏')
    check('嘉善产业基础与结构' in page.locator('#thinking-0').inner_text(), '最新思考内容可见')
    page.evaluate("handleEvent({type:'activity',stage:0,kind:'theses',n:3,label:'形成 3 条初步判断'})")
    check(page.locator('#log .activity').count() >= 1, '资料与数据动作进入连续执行流')

    page.locator('#pause').click()
    before = page.locator('#log').inner_text()
    page.evaluate("handleEvent({type:'log',text:'暂停期间排队动作'})")
    check(page.locator('#log').inner_text() == before, '暂停时执行流冻结')
    check('已暂停' in page.locator('#run-state').inner_text(), '统筹Agent显示暂停状态')
    page.locator('#pause').click()
    check('暂停期间排队动作' in page.locator('#log').inner_text(), '继续后排队动作恢复')
    page.wait_for_timeout(400)
    page.screenshot(path=str(OUT / 'single-agent-process.png'))

    page.evaluate("void startStatic('玉环')")
    page.wait_for_selector('#report.on', timeout=30000)
    check(page.locator('#rdoc .rsec').count() >= 12, '完整回放与报告交付不回归')
    check(not errors, '浏览器无JavaScript异常：' + repr(errors))
    browser.close()

print(json.dumps({'checks': len(checks), 'passed': checks, 'errors': errors}, ensure_ascii=False, indent=2))
