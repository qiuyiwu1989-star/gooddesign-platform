import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/design-143'
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
    page.evaluate("handleEvent({type:'think',stage:0,tail:'{\"headline\":\"嘉善产业基础\"}',progress:60})")
    page.wait_for_selector('#think .research-card')
    check(page.locator('#think.expanded').count() == 1, '右侧从固定结构切入调研展开')
    check(page.locator('.research-thought').count() == 1, '真实思考形成研究卡')
    page.evaluate("handleEvent({type:'think',stage:0,tail:'{\"headline\":\"嘉善产业基础与结构\"}',progress:100})")
    check(page.locator('.research-thought').count() == 1, '思考卡持续更新而不重复')
    check('嘉善产业基础与结构' in page.locator('.research-thought').inner_text(), '最新分析内容进入主视区')

    for i in range(1, 9):
        page.evaluate(f"handleEvent({{type:'activity',stage:0,kind:'theses',n:{i},label:'核查产业判断 {i}'}})")
    check(page.locator('.research-card').count() == 6, '连续事件展开且最多保留六项')
    check('核查产业判断 8' in page.locator('.research-stream').inner_text(), '最新研究事件可见')
    check(page.locator('#log .activity').count() >= 8, '左侧执行流同步增加')

    page.locator('#pause').click()
    before = page.locator('.research-stream').inner_text()
    page.evaluate("handleEvent({type:'activity',stage:LIVE.currentStage,kind:'theses',n:9,label:'暂停后新增资料'})")
    check(page.locator('.research-stream').inner_text() == before, '暂停时右侧不展开')
    page.locator('#pause').click()
    check('暂停后新增资料' in page.locator('.research-stream').inner_text(), '继续后研究事件恢复展开')
    page.evaluate("handleEvent({type:'stage',i:0,s:'doing'});handleEvent({type:'stage',i:1,s:'doing'})")
    check(page.locator('.research-card').count() > 0, '阶段切换保留最近调研卡片')
    page.wait_for_timeout(350)
    page.screenshot(path=str(OUT / 'research-expansion.png'))

    page.set_viewport_size({'width': 390, 'height': 844})
    check(page.evaluate('document.documentElement.scrollWidth <= innerWidth'), '移动端无横向溢出')
    page.set_viewport_size({'width': 1600, 'height': 1000})
    page.evaluate("void startStatic('玉环')")
    page.wait_for_selector('#report.on', timeout=30000)
    check(page.locator('#rdoc .rsec').count() >= 12, '完整回放与报告交付不回归')
    check(not errors, '浏览器无JavaScript异常：' + repr(errors))
    browser.close()

print(json.dumps({'checks': len(checks), 'passed': checks, 'errors': errors}, ensure_ascii=False, indent=2))
