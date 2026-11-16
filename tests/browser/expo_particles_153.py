import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/design-153'
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
    page.locator('#pause').click()
    check(page.locator('.info-particle').count() == 0, '工位动画不生成虚假粒子')
    role_id = page.evaluate('STAGE_AGENT[LIVE.currentStage]')
    role_before = page.evaluate('roleFrequency("' + role_id + '").total')
    page.evaluate("expandResearch(LIVE.currentStage,'sources',1,'读取第一份真实资料',false)")
    check(page.locator('.info-particle').count() == 1, '真实资料事件生成吸收粒子')
    check(page.evaluate('roleFrequency("' + role_id + '").total') == role_before + 1, '角色频次由真实事件时间戳复算')
    page.evaluate("expandResearch(LIVE.currentStage,'sources',2,'读取第二份真实资料',false)")
    check(page.locator('.info-particle').count() == 2, '第二个真实事件生成新粒子')
    check(str(role_before + 2) + ' 次' in page.locator('.research-cursor').inner_text(), '指针显示角色真实事件次数')
    page.locator('.research-card:not(.worker-card)').last.click()
    check('近 10 秒' in page.locator('.role-frequency').inner_text(), '聚焦详情显示近10秒真实频次')
    page.keyboard.press('Escape')
    before = page.evaluate('Object.values(LIVE.roleEvents).reduce((n,e)=>n+e.length,0)')
    page.evaluate("handleEvent({type:'activity',stage:LIVE.currentStage,kind:'sources',n:3,label:'暂停期间不吸收'})")
    after = page.evaluate('Object.values(LIVE.roleEvents).reduce((n,e)=>n+e.length,0)')
    check(after == before, '暂停时不新增角色事件或粒子')
    page.screenshot(path=str(OUT / 'information-absorption.png'))

    for i in range(40):
        page.evaluate("expandResearch(LIVE.currentStage,'sources'," + str(i + 3) + ",'真实检索事件',false)")
    check(page.locator('.info-particle').count() <= 36, '粒子数量有上限且性能受控')
    page.evaluate("void startStatic('玉环')")
    page.wait_for_selector('#report.on', timeout=30000)
    check(page.locator('#rdoc .rsec').count() >= 12, '完整回放与报告交付不回归')
    check(not errors, '浏览器无JavaScript异常：' + repr(errors))

    reduced = browser.new_context(viewport={'width': 1280, 'height': 900}, reduced_motion='reduce')
    rp = reduced.new_page()
    rp.route('**/expo/api/places', lambda route: route.fulfill(status=200, content_type='application/json', body='{"places":[]}'))
    rp.goto('http://127.0.0.1:8897/expo/', wait_until='networkidle')
    rp.evaluate("void startStatic('嘉善')")
    rp.wait_for_selector('.worker-card')
    rp.locator('#pause').click()
    rp.evaluate("expandResearch(LIVE.currentStage,'sources',1,'减少动态模式资料',false)")
    check(rp.locator('.info-particle').count() == 0, '减少动态时跳过粒子')
    reduced.close()
    browser.close()

print(json.dumps({'checks': len(checks), 'passed': checks, 'errors': errors}, ensure_ascii=False, indent=2))
