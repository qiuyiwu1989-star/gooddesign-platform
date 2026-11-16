import json
from pathlib import Path
from urllib.parse import parse_qs, unquote
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/design-150'
OUT.mkdir(parents=True, exist_ok=True)
checks = []
errors = []
requests = []


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
    page.route('**/expo/api/run?*', lambda route: route.abort())
    page.on('request', lambda request: requests.append(request.url) if '/expo/api/run' in request.url else None)
    page.goto('http://127.0.0.1:8897/expo/', wait_until='networkidle')

    page.locator('#q').fill('玉环水暖阀门')
    page.locator('#go').click()
    page.wait_for_timeout(150)
    query = parse_qs(unquote(requests[-1]).split('?', 1)[1])
    check(query['region'] == ['玉环'], '地区正确解析为玉环')
    check(query['industry'] == ['水暖阀门'], '产业正确解析为水暖阀门')
    check('需求' in query['question'][0] and '试点' in query['question'][0], '研究问题随地方产业生成')
    check(page.evaluate("LIVE.target.region + ' · ' + LIVE.target.industry") == '玉环 · 水暖阀门', '运行对象用中文地方产业显示')

    page.goto('http://127.0.0.1:8897/expo/', wait_until='networkidle')
    page.locator('#q').fill('杭州市西湖区数字经济')
    page.locator('#go').click()
    page.wait_for_timeout(150)
    query = parse_qs(unquote(requests[-1]).split('?', 1)[1])
    check(query['region'] == ['杭州市西湖区'], '已消歧地名与产业保持关系')
    check(query['industry'] == ['数字经济'], '产业字段不被地名覆盖')

    page.evaluate("startStatic('玉环')")
    page.wait_for_selector('#report.on', timeout=30000)
    page.evaluate("LIVE.pack.target={region:'玉环',industry:'水暖阀门',question:'研究玉环水暖阀门产业的企业需求与试点'};LIVE.pack.label='玉环水暖阀门';LIVE.pack.slug='yuhuan-shui-nuan-fa-men';LIVE.pack.report_id='target-v1';buildReport(LIVE.pack)")
    check('玉环水暖阀门产业' in page.locator('.rcover h1').inner_text(), '报告标题包含中文地方产业')
    check('玉环 · 水暖阀门' in page.locator('.rcover').inner_text(), '封面明确研究对象')
    check(page.locator('.relation-flow > div').count() == 5, '报告呈现五级研究关系链')
    check('外部趋势只作参照' in page.locator('#rs-design').inner_text(), '报告明确跨层证据边界')

    page.evaluate("void startStatic('嘉善')")
    page.wait_for_selector('.worker-card')
    page.locator('#pause').click()
    cursor = page.locator('.research-cursor')
    before = cursor.evaluate('el=>({left:el.style.left,top:el.style.top})')
    page.evaluate("expandResearch(LIVE.currentStage,'sources',1,'读取新增公开资料',false)")
    page.wait_for_timeout(350)
    after = cursor.evaluate('el=>({left:el.style.left,top:el.style.top})')
    check(before != after, '工作指针移动到新的真实工作卡片')
    check(len(cursor.locator('span').inner_text()) > 0, '指针显示当前工作角色')
    page.screenshot(path=str(OUT / 'industry-cursor.png'))
    check(not errors, '浏览器无JavaScript异常：' + repr(errors))
    browser.close()

print(json.dumps({'checks': len(checks), 'passed': checks, 'errors': errors}, ensure_ascii=False, indent=2))
