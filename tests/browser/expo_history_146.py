import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
checks = []
errors = []


def check(value, label):
    if not value:
        raise AssertionError(label)
    checks.append(label)


def report_for(place, report_id):
    return {'place': place, 'id': report_id, 'slug': 'jiashan', 'curated': False,
            'pack': {'label': place, 'slug': 'jiashan', 'report_id': report_id, 'depth': 'deep' if report_id == 'v2' else 'standard',
                     'headline': '产业研究', 'intro': '内容', 'sectors': [], 'drivers': [], 'summary_points': [],
                     'theses': [], 'boundary': '', 'sources': [], 'facts': [], 'benchmarks': [], 'chain': [],
                     'companies': [], 'note': '', 'personas': [], 'requirements': [], 'matches': [],
                     'opportunities': [], 'risks': [], 'metrics': {}, 'projects': {}}}


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1440, 'height': 900})
    page.on('pageerror', lambda error: errors.append(str(error)))
    reports = [report_for('嘉善', 'v1'), report_for('嘉善', 'v2')]
    page.route('**/expo/api/places', lambda route: route.fulfill(
        status=200, content_type='application/json', body=json.dumps({'places': reports}, ensure_ascii=False)))
    def report_route(route):
        query = route.request.url.split('?', 1)[1]
        from urllib.parse import parse_qs
        params = parse_qs(query)
        report = report_for('嘉善', params.get('id', ['v2'])[0])
        route.fulfill(status=200, content_type='application/json', body=json.dumps(report, ensure_ascii=False))
    page.route('**/expo/api/report?*', report_route)
    page.goto('http://127.0.0.1:8897/expo/', wait_until='networkidle')
    check(page.locator('.history-item').count() == 2, '历史区域保留两份独立报告')
    hrefs = page.locator('.history-item').evaluate_all('(els)=>els.map(e=>e.getAttribute("href"))')
    check('id=v1' in hrefs[0] and 'id=v2' in hrefs[1], '每个历史版本有独立链接')

    page.locator('.history-item').first.click()
    page.wait_for_selector('#report.on')
    check(page.evaluate('LIVE.reportId') == 'v1', '历史项打开指定第一版')
    check('嘉善产业' in page.locator('.rcover h1').inner_text(), '报告标题使用中文地名')
    check('jiashan' not in page.locator('.rcover h1').inner_text(), '报告标题不泄漏拼音')
    check('嘉善' in page.locator('.rcover .quiet').inner_text(), '报告编号使用中文地名')
    check(page.evaluate('LIVE.reportUrl').endswith('report=jiashan&id=v1'), '报告二维码链接含全拼地名和版本ID')
    page.locator('#again').click()
    page.locator('.history-item').nth(1).click()
    page.wait_for_selector('#report.on')
    check(page.evaluate('LIVE.reportId') == 'v2', '可打开另一独立版本')

    page.goto('http://127.0.0.1:8897/expo/?report=jiashan&id=v1', wait_until='networkidle')
    page.wait_for_selector('#report.on')
    check(page.evaluate('LIVE.reportId') == 'v1', '独立链接可直接恢复指定版本')
    check(not errors, '浏览器无JavaScript异常：' + repr(errors))
    browser.close()

print(json.dumps({'checks': len(checks), 'passed': checks, 'errors': errors}, ensure_ascii=False, indent=2))
