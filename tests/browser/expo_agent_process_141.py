import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/design-141'
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
    page.evaluate("void startStatic('玉环')")
    page.wait_for_selector('#member-poti.working', state='attached')
    check(page.locator('#graph .agent-ip').count() == 9, '顶部角色棋子使用小好形象')
    check(page.locator('#team .agent-ip').count() == 7, '左侧七角色均有独立形象')
    check(page.locator('#think .thought-orb .agent-ip').count() == 1, '中央当前角色使用小好形象')
    page.wait_for_function("document.querySelectorAll('#mp-poti span').length > 0")
    check('可研究的问题' in page.locator('#mp-poti').inner_text(), '破题角色显示自己的研究思路')

    page.evaluate("handleEvent({type:'think',stage:0,tail:'{\"headline\":\"玉环产业基础\",\"sectors\":[\"阀门\"]}',progress:100})")
    thought = page.locator('#mp-poti').inner_text()
    check('正在形成' in thought and '玉环产业基础' in thought, '实时思考进入对应角色')
    check('headline' not in thought and '{' not in thought and '}' not in thought, '思考摘要不暴露JSON结构')

    page.evaluate("handleEvent({type:'stage',i:1,s:'doing'});handleEvent({type:'activity',stage:1,kind:'sources',n:1,label:'登记来源 · 玉环统计资料'})")
    check('玉环统计资料' in page.locator('#mp-scout').inner_text(), '资料处理过程进入侦察角色')
    check('1 来源' in page.locator('#mc-scout').inner_text(), '侦察角色工作量同步更新')

    page.locator('#pause').click()
    page.evaluate("handleEvent({type:'activity',stage:1,kind:'sources',n:2,label:'登记来源 · 企业年报'})")
    check('企业年报' not in page.locator('#mp-scout').inner_text(), '暂停时角色过程不推进')
    check(page.evaluate('LIVE.queue.length') >= 1, '暂停期间真实事件排队')
    page.locator('#pause').click()
    check('企业年报' in page.locator('#mp-scout').inner_text(), '继续后事件按序进入角色')
    page.wait_for_timeout(450)
    page.screenshot(path=str(OUT / 'agent-process-working.png'))

    page.evaluate("void startStatic('嘉善')")
    page.wait_for_selector('#report.on', timeout=30000)
    check(page.locator('#rdoc .rsec').count() >= 12, '完整回放与报告交付不回归')
    check(not errors, '浏览器无JavaScript异常：' + repr(errors))
    browser.close()

print(json.dumps({'checks': len(checks), 'passed': checks, 'errors': errors}, ensure_ascii=False, indent=2))
