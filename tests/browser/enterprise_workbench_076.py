import json
import shutil
import sys
import tempfile
import threading
import uuid
from pathlib import Path
from unittest.mock import patch
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from innovation_loop_server import Handler, ThreadingHTTPServer
from innovation_loop_store import DEFAULT, LoopStore

OUT = ROOT / 'output/playwright/gooddesign-enterprise-076'
OUT.mkdir(parents=True, exist_ok=True)
checks = []
errors = []
failed = []


def check(condition, label):
    if not condition:
        raise AssertionError(label)
    checks.append(label)


with tempfile.TemporaryDirectory(dir=ROOT / 'output') as temporary:
    database = Path(temporary) / 'loop.sqlite3'
    shutil.copy2(DEFAULT, database)
    with patch('innovation_loop_server.LoopStore', return_value=LoopStore(database)):
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f'http://127.0.0.1:{server.server_port}'
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(viewport={'width': 1440, 'height': 1000}, color_scheme='light', accept_downloads=True)
                page = context.new_page()
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.on('requestfailed', lambda request: failed.append(request.url))
                page.goto(base + '/?task=rubber-v1#overview', wait_until='networkidle')
                check(page.locator('h1').inner_text() == '企业创新工作台', '产品定义为企业创新工作台')
                check(page.locator('#decision-overview .ew-route-card').count() == 3, '首屏显示三条真实路线')
                check(page.locator('.ew-unknown-button').count() == 3, '首屏显示三类关键未知')
                check(page.locator('#auto').count() == 0, '不再以自动演示为入口')
                check(page.locator('#task-select option').count() == 3, '三个真实研究任务')
                page.screenshot(path=str(OUT / 'overview-desktop.png'))

                page.locator('#task-select').select_option('gear-v1')
                page.wait_for_url('**task=gear-v1*')
                check(page.locator('#task-select').input_value() == 'gear-v1', '切换双环齿轮任务')
                page.locator('#task-select').select_option('polish-v1')
                page.wait_for_url('**task=polish-v1*')
                check(page.locator('#task-select').input_value() == 'polish-v1', '切换内腔抛光任务')
                page.locator('#task-select').select_option('rubber-v1')
                page.wait_for_url('**task=rubber-v1*')

                page.locator('[data-view="requirement"]').first.click()
                value = '076QA-' + uuid.uuid4().hex[:10]
                page.locator('#clarify-value').fill(value)
                page.locator('#clarify-save').click()
                check('请填写补充内容和提供者' in page.locator('#clarify-status').inner_text(), '补充缺项提示')
                check(page.locator('#clarify-value').input_value() == value, '错误时保留补充输入')
                page.locator('#clarify-actor').fill('076内部QA')
                page.locator('#clarify-save').click()
                page.wait_for_function("document.querySelector('#clarify-status').textContent.includes('已保存为待确认补充')")
                check(page.locator('#clarify-records li', has_text=value).count() == 1, '补充真实保存')
                page.locator('#clarify-value').fill(value)
                page.locator('#clarify-actor').fill('076内部QA')
                page.locator('#clarify-save').click()
                page.wait_for_function("document.querySelector('#clarify-status').textContent.includes('已保存为待确认补充')")
                check(page.locator('#clarify-records li', has_text=value).count() == 1, '重复补充不在界面重复计数')
                page.reload(wait_until='networkidle')
                check(page.locator('#clarify-records li', has_text=value).count() == 1, '刷新后补充仍在')
                check('待确认提案' in page.locator('#research-status').inner_text(), '补充不自动确认需求')

                page.locator('[data-view="routes"]').first.click()
                page.locator('[data-evidence]').first.click()
                check(page.locator('#evidence-panel').is_visible(), '证据抽屉打开')
                check(page.locator('.ew-evidence-card').count() == 6, '六条候选经验可核对')
                check('尚未证明与当前路线匹配' in page.locator('#evidence-panel').inner_text(), '证据不冒充已匹配')
                page.keyboard.press('Escape')
                check(not page.locator('#evidence-panel').is_visible(), 'Escape关闭证据')
                page.locator('[data-route-open]').nth(1).click()
                page.wait_for_selector('.ew-route-tabs [aria-pressed="true"]')
                check(page.locator('.ew-route-tabs [aria-pressed="true"]').get_attribute('data-route-tab') == 'TASK-RUBBER-V1-R2', '第二路线进入验证计划')
                page.screenshot(path=str(OUT / 'validation-desktop.png'))
                with page.expect_download() as download_info:
                    page.locator('#export-plan').click()
                download = download_info.value
                packet = json.loads(Path(download.path()).read_text())
                check(packet['route']['id'] == 'TASK-RUBBER-V1-R2', '导出绑定第二路线')
                check(packet['model_calls'] == 0 and packet['execution_authorized'] is False, '导出不伪称模型执行或工程授权')
                check(packet['research_action']['stop_condition'], '导出保留停止条件')

                page.locator('[data-view="feedback"]').first.click()
                check('TASK-RUBBER-V1-R2' in page.locator('#binding-note').inner_text(), '反馈绑定当前第二路线')
                first_basis = '076QA反馈-' + uuid.uuid4().hex[:10]
                page.locator('#actor-role').fill('076内部QA')
                page.locator('#feedback-body').fill(first_basis)
                page.locator('#internal-consent').check()
                page.locator('#save').click()
                page.wait_for_function("document.querySelector('#workspace-status').textContent.includes('反馈已保存')")
                check(page.locator('.ew-feedback-item', has_text=first_basis).count() == 1, '反馈真实保存')
                page.reload(wait_until='networkidle')
                check(page.locator('.ew-feedback-item', has_text=first_basis).count() == 1, '刷新后反馈仍在')

                retry_basis = '076QA重试-' + uuid.uuid4().hex[:10]
                page.locator('#feedback-body').fill(retry_basis)
                page.locator('#actor-role').fill('076内部QA')
                page.locator('#internal-consent').check()
                page.route('**/api/feedback', lambda route: route.abort())
                page.locator('#save').click()
                page.wait_for_function("document.querySelector('#workspace-status').dataset.kind === 'error'")
                check(page.locator('#feedback-body').input_value() == retry_basis, '保存失败保留反馈草稿')
                page.unroute('**/api/feedback')
                page.locator('#save').click()
                page.wait_for_function("document.querySelector('#workspace-status').textContent.includes('反馈已保存')")
                store = LoopStore(database)
                records = [row for row in store.list_records('feedback') if row.get('basis') in (first_basis, retry_basis)]
                check(len(records) == 2, '首次反馈与失败重试各只有一条记录')
                check(len([row for row in records if row.get('basis') == retry_basis]) == 1, '重试复用提交身份不重复')
                check(all(row['processing_status'] == 'pending_review' for row in records), '反馈保持待审核')

                page.locator('#feedback-body').fill('076尚未完成的网络草稿')
                page.route('**/api/bundle*', lambda route: route.abort())
                page.locator('#reload').click()
                page.wait_for_function("document.querySelector('#workspace-status').dataset.kind === 'error'")
                check('尚未完成的网络草稿' in page.locator('#feedback-body').input_value(), '读取失败保留当前内容和草稿')
                page.unroute('**/api/bundle*')
                page.locator('#reload').click()
                page.wait_for_function("document.querySelector('#workspace-status').textContent.includes('已读取当前数据')")
                check('尚未完成的网络草稿' in page.locator('#feedback-body').input_value(), '恢复重试不清空草稿')

                page.locator('#task-select').select_option('gear-v1')
                page.wait_for_url('**task=gear-v1*')
                page.locator('[data-view="feedback"]').first.click()
                check(page.locator('.ew-feedback-item', has_text=first_basis).count() == 0, '反馈不跨任务泄漏')
                page.locator('[data-gd-theme-toggle]').click()
                check(page.locator('html').get_attribute('data-theme') == 'dark', '深色主题切换')
                page.wait_for_timeout(400)
                page.screenshot(path=str(OUT / 'feedback-dark.png'))
                page.locator('[data-gd-theme-toggle]').click()
                check(page.locator('html').get_attribute('data-theme') == 'light', '浅色主题恢复')

                for width in (1440, 1280, 1024, 768, 390, 360):
                    page.set_viewport_size({'width': width, 'height': 844})
                    page.goto(base + '/?task=rubber-v1#overview', wait_until='networkidle')
                    check(page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'{width}px无全页横向溢出')
                    if width == 390:
                        page.screenshot(path=str(OUT / 'overview-mobile.png'))
                        page.locator('[data-view="validation"]').first.click()
                        page.wait_for_selector('#export-plan')
                        check(page.locator('#export-plan').is_visible(), '手机可进入验证计划')
                response = page.request.get(base + '/workspace/enterprise-workbench.css')
                check(response.status == 200, '工作台CSS白名单可访问')
                response = page.request.get(base + '/workspace/enterprise-workbench.js')
                check(response.status == 200, '工作台JS白名单可访问')
                response = page.request.get(base + '/workspace/not-registered')
                check(response.status == 404, '未登记静态资源拒绝访问')
                check(not errors, '无浏览器脚本异常')
                unexpected_failures = [url for url in failed if '/api/' not in url]
                check(not unexpected_failures, '无本地静态资源失败')
                browser.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

unexpected_failures = [url for url in failed if '/api/' not in url]
intentional_failures = [url for url in failed if '/api/' in url]
report = {'checks': checks, 'errors': errors, 'failed_resources': unexpected_failures, 'intentional_failure_tests': intentional_failures}
(OUT / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
print(json.dumps({'check_count': len(checks), 'errors': errors, 'failed_resources': unexpected_failures}, ensure_ascii=False))
