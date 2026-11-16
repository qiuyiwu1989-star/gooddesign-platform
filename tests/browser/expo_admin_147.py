import json
from urllib.parse import unquote
from pathlib import Path
from playwright.sync_api import sync_playwright

checks = []
errors = []
run_places = []


def check(value, label):
    if not value:
        raise AssertionError(label)
    checks.append(label)


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1440, 'height': 900})
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.route('**/expo/api/places', lambda route: route.fulfill(
        status=200, content_type='application/json', body='{"places":[]}'))
    page.route('**/expo/api/run?*', lambda route: route.abort())
    page.on('request', lambda request: run_places.append(request.url) if '/expo/api/run' in request.url else None)
    page.goto('http://127.0.0.1:8897/expo/', wait_until='networkidle')
    page.wait_for_function('MSTATE.cty.length === 2875')
    identities = page.evaluate("MSTATE.cty.filter(c=>c.adcode===330106||c.adcode===360103).map(c=>c.identity)")
    check(identities == ['杭州市西湖区', '南昌市西湖区'], '两个西湖区使用不同完整身份')

    page.evaluate("mapClick(MSTATE.cty.find(c=>c.adcode===330106))")
    page.wait_for_function("document.querySelectorAll('#loghead').length === 1")
    page.wait_for_timeout(150)
    check(any('杭州市西湖区' in unquote(url) for url in run_places), '点击杭州西湖区进入杭州研究')

    page.goto('http://127.0.0.1:8897/expo/', wait_until='networkidle')
    page.locator('#q').fill('西湖区')
    page.locator('#go').click()
    page.wait_for_selector('#place-choices button')
    check(page.locator('#place-choices button').count() == 2, '同名输入先显示两个候选')
    check('杭州市西湖区' in page.locator('#place-choices').inner_text(), '候选包含杭州')
    check('南昌市西湖区' in page.locator('#place-choices').inner_text(), '候选包含南昌')
    check(not any('place=' in unquote(url) for url in run_places if '西湖' in url), '未选择前不启动同名研究')
    page.locator('#place-choices button', has_text='南昌市西湖区').click()
    page.wait_for_timeout(150)
    check(any('南昌市西湖区' in unquote(url) for url in run_places), '选择南昌后进入南昌研究')
    check(not errors, '浏览器无JavaScript异常：' + repr(errors))
    browser.close()

print(json.dumps({'checks': len(checks), 'passed': checks, 'errors': errors}, ensure_ascii=False, indent=2))
