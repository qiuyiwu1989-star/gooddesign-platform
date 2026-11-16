import base64
import json
import re
from pathlib import Path
import cv2
import fitz
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/design-135'
OUT.mkdir(parents=True, exist_ok=True)
URL = 'http://127.0.0.1:8897/expo/'
checks = []
errors = []


def check(value, label):
    if not value:
        raise AssertionError(label)
    checks.append(label)


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1600, 'height': 1000}, accept_downloads=True)
    page = context.new_page()
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.route('**/expo/api/places', lambda route: route.fulfill(
        status=200, content_type='application/json', body='{"places":[]}'))
    page.route('**/expo/api/archive', lambda route: route.fulfill(
        status=200, content_type='application/json',
        body=json.dumps({'ok': True, 'report': {'place': '玉环', 'ts': 1, 'curated': True, 'counts': {}}}, ensure_ascii=False)))
    page.goto(URL, wait_until='networkidle')

    page.evaluate("void startStatic('玉环')")
    page.wait_for_selector('#member-poti.working', state='attached')
    page.locator('#back').click()
    page.wait_for_load_state('domcontentloaded')
    page.wait_for_selector('#home:not(.off)')
    page.wait_for_timeout(700)
    check(page.locator('#run.on').count() == 0, '返回后旧回放不会继续打开报告')

    page.goto(URL + '?report=玉环', wait_until='networkidle')
    page.wait_for_selector('#report.on')
    check('玉环产业' in page.locator('.rcover h1').inner_text(), '旧中文报告链接保持兼容')
    page.locator('#again').click()
    page.goto(URL + '?report=yuhuan', wait_until='networkidle')
    page.wait_for_selector('#report.on')
    check('玉环产业' in page.locator('.rcover h1').inner_text(), '全拼报告链接直接打开对应报告')
    check(page.evaluate("getComputedStyle(document.body).backgroundColor === 'rgb(242, 243, 245)'"), '在线报告使用浅色背景')
    check(page.locator('#rtoc a[href="/expo/"]').count() == 1, '在线报告目录提供返回首页入口')
    page.locator('#again').click()

    page.evaluate("void startStatic('玉环')")
    page.wait_for_selector('#member-poti.working', state='attached')
    page.locator('#pause').click()
    paused_time = page.locator('#elapsed').inner_text()
    page.wait_for_timeout(900)
    check(page.locator('#pause').inner_text() == '继续', '暂停后提供继续动作')
    check(page.locator('#elapsed').inner_text() == paused_time, '暂停时计时冻结')
    check(page.locator('#member-scout.working').count() == 0, '暂停时静态研究不进入下一阶段')
    page.locator('#pause').click()
    page.wait_for_selector('#report.on', timeout=30000)
    check(not page.locator('#btn-archive').is_disabled(), '新报告可确认收录后台')
    page.locator('#btn-archive').click()
    page.wait_for_function("document.querySelector('#btn-archive').textContent === '已收录后台'")
    check(page.locator('#btn-archive').is_disabled(), '收录成功后状态固定')
    check(page.locator('.project-cover').count() > 0, '项目关系卡包含真实封面或明确占位')
    check(page.locator('.project-side img').count() > 0, '每个项目关系卡包含专属二维码')
    check('扫码打开并保存本报告' in page.locator('#report-qr').inner_text(), '通用二维码替换为本报告二维码')
    check(page.locator('.decision-grid section').count() == 4, '摘要包含四个领导决策区')
    check(page.locator('.evidence-note').count() >= 2, '核心判断包含具体依据说明')
    check('供会商' in page.locator('.pilot-framework').inner_text(), '试点组织建议明确供会商而非既定分工')
    check('推广前提' in page.locator('.pilot-framework').inner_text(), '试点建议包含推广前提')
    for selector, name in [('#cover-qr', 'report-qr.png'), ('.project-side img', 'project-qr.png')]:
        data = page.locator(selector).first.get_attribute('src')
        (OUT / name).write_bytes(base64.b64decode(data.split(',', 1)[1]))

    with page.expect_download() as download_info:
        page.locator('#btn-save').click()
    download = download_info.value
    html_path = OUT / download.suggested_filename
    download.save_as(str(html_path))
    html = html_path.read_text(encoding='utf-8')
    check('<script' not in html.lower(), '独立HTML无脚本依赖')
    check('https://haoshejiguan.com/dossier/' in html, '独立HTML项目链接转为绝对地址')
    check('delivery-nav' in html and '管理层摘要' in html, '独立HTML含完整目录与报告')
    check('href="https://haoshejiguan.com/expo/"' in html and '返回产业研究首页' in html, '独立HTML提供返回首页入口')
    images = re.findall(r'<img[^>]+src="([^"]+)"', html)
    check(images and all(src.startswith('data:image/') for src in images), '下载HTML二维码与封面全部内嵌')

    page.pdf(path=str(OUT / 'report-a4.pdf'), format='A4', print_background=True, prefer_css_page_size=True)
    pdf = fitz.open(OUT / 'report-a4.pdf')
    check(10 <= pdf.page_count <= 22, f'A4页数合理（{pdf.page_count}页）')
    req_page = next((i for i, pge in enumerate(pdf) if 'N4' in pge.get_text()), None)
    check(req_page is not None, 'PDF包含完整需求表')
    pdf[0].get_pixmap(matrix=fitz.Matrix(1.4, 1.4)).save(OUT / 'print-cover.png')
    pdf[req_page].get_pixmap(matrix=fitz.Matrix(1.4, 1.4)).save(OUT / 'print-requirements.png')
    map_page = next((i for i, pge in enumerate(pdf) if '可借鉴做法' in pge.get_text()), None)
    check(map_page is not None, 'PDF包含案例借鉴关系')
    pdf[map_page].get_pixmap(matrix=fitz.Matrix(1.4, 1.4)).save(OUT / 'print-projects.png')
    summary_page = next(i for i, pge in enumerate(pdf) if '建议工作路径' in pge.get_text())
    pilot_page = next(i for i, pge in enumerate(pdf) if '试点组织建议' in pge.get_text())
    pdf[summary_page].get_pixmap(matrix=fitz.Matrix(1.4, 1.4)).save(OUT / 'print-decision-summary.png')
    pdf[pilot_page].get_pixmap(matrix=fitz.Matrix(1.4, 1.4)).save(OUT / 'print-pilot-framework.png')
    req_text = pdf[req_page].get_text()
    check('待企业确认' in req_text, 'PDF需求状态使用领导阅读版表述')
    pdf.close()

    offline = context.new_page()
    offline.goto(html_path.as_uri(), wait_until='load')
    check('玉环产业' in offline.locator('.rcover h1').inner_text(), '下载HTML离线打开内容完整')
    check(offline.evaluate('document.documentElement.scrollWidth <= innerWidth'), '独立HTML桌面无横向溢出')
    offline.screenshot(path=str(OUT / 'standalone-html.png'), full_page=False)
    offline.pdf(path=str(OUT / 'standalone-a4.pdf'), format='A4', print_background=True, prefer_css_page_size=True)
    offline_pdf = fitz.open(OUT / 'standalone-a4.pdf')
    check(10 <= offline_pdf.page_count <= 22, f'独立HTML打印页数合理（{offline_pdf.page_count}页）')
    offline_pdf.close()

    offline.set_viewport_size({'width': 390, 'height': 844})
    check(offline.evaluate('document.documentElement.scrollWidth <= innerWidth'), '独立HTML移动无横向溢出')
    check(not errors, '浏览器无 JavaScript 异常：' + repr(errors))
    browser.close()

report_qr = cv2.QRCodeDetector().detectAndDecode(cv2.imread(str(OUT / 'report-qr.png')))[0]
project_qr = cv2.QRCodeDetector().detectAndDecode(cv2.imread(str(OUT / 'project-qr.png')))[0]
check(report_qr == 'https://haoshejiguan.com/expo/?report=yuhuan&id=demo-yuhuan', '报告二维码解码后为全拼独立版本链接')
check(project_qr.startswith('https://haoshejiguan.com/dossier/?project='), '项目二维码解码后为项目档案链接')
print(json.dumps({'checks': len(checks), 'passed': checks, 'errors': errors}, ensure_ascii=False, indent=2))
