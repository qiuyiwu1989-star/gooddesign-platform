import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/design-149'
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
    page.evaluate("handleEvent({type:'activity',stage:LIVE.currentStage,kind:'sources',n:5,label:'查阅公开统计资料与企业公开信息'})")
    page.locator('#pause').click()
    page.wait_for_selector('.research-card:not(.worker-card)')
    card = page.locator('.research-card:not(.worker-card)').last
    check('trace' in card.get_attribute('class'), '新研究事件带关联追踪动线')
    check('5 项' in page.locator('#depth-sources').inner_text(), '公开资料深度随真实事件更新')
    card.click()
    check('selected' in card.get_attribute('class'), '点击后聚焦当前研究卡')
    check('has-focus' in page.locator('.research-stream').get_attribute('class'), '其他卡片进入降噪状态')
    check('查阅公开统计资料与企业公开信息' in page.locator('.research-focus').inner_text(), '聚焦完整保留原事件内容')
    page.keyboard.press('Escape')
    check(page.locator('.research-focus.on').count() == 0, 'Escape退出聚焦')

    card.focus()
    page.keyboard.press('Enter')
    check(page.locator('.research-focus.on').count() == 1, 'Enter键可打开聚焦详情')
    page.keyboard.press('Escape')
    page.locator('.worker-card').first.click()
    check('进行中分工' in page.locator('.research-focus').inner_text(), '工位明确标为进行中而非完成成果')
    page.keyboard.press('Escape')

    page.locator('#pause').click()
    page.evaluate("handleEvent({type:'activity',stage:LIVE.currentStage,kind:'checked',n:3,label:'完成三项判断核查'})")
    page.evaluate("handleEvent({type:'activity',stage:LIVE.currentStage,kind:'matches',n:18,label:'形成案例对照'})")
    page.evaluate("handleEvent({type:'activity',stage:LIVE.currentStage,kind:'sources',n:6,label:'形成最终资料索引'})")
    page.locator('#pause').click()
    check('3 /' in page.locator('#depth-checked').inner_text(), '判断核查显示实际核证数量')
    check('18 项' in page.locator('#depth-matches').inner_text(), '案例对照显示真实关联数量')
    card = page.locator('.research-card:not(.worker-card)').last
    card.click()
    page.wait_for_timeout(300)
    check(page.locator('#think').evaluate("el=>getComputedStyle(el).opacity === '1'"), '暂停不冻结页面入场与内容可见性')
    check(page.locator('.research-focus').evaluate("el=>getComputedStyle(el).opacity === '1'"), '暂停状态下聚焦详情仍可见')
    check(page.evaluate("(()=>{const f=document.querySelector('.research-focus').getBoundingClientRect();const p=document.querySelector('#think').getBoundingClientRect();return f.top>=p.top&&f.bottom<=p.bottom})()"), '聚焦详情完整显示在主视区内')
    page.screenshot(path=str(OUT / 'research-focus-depth.png'))

    page.evaluate("void startStatic('玉环')")
    page.wait_for_selector('#report.on', timeout=30000)
    check(page.locator('#rdoc .rsec').count() >= 12, '完整回放与报告交付不回归')
    check(not errors, '浏览器无JavaScript异常：' + repr(errors))
    browser.close()

print(json.dumps({'checks': len(checks), 'passed': checks, 'errors': errors}, ensure_ascii=False, indent=2))
