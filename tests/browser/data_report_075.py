import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/playwright/gooddesign-report-075'
OUT.mkdir(parents=True, exist_ok=True)
DATA = json.loads((ROOT / 'extensions/project-portal/data-report.json').read_text())
checks = []
errors = []
failed = []


def check(condition, label):
    if not condition:
        raise AssertionError(label)
    checks.append(label)


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1440, 'height': 1000}, color_scheme='light')
    page = context.new_page()
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('requestfailed', lambda request: failed.append(request.url))
    page.goto('http://127.0.0.1:8892/inno/report/', wait_until='networkidle')
    check(page.locator('.dr-evidence-link').count() == 98, '98个真实证据点')
    check(page.locator('.dr-donut-segment').count() == 5, '五类奖项分布')
    check(page.locator('.dr-year-bar').count() == 10, '10个有数据年度')
    check(page.locator('.dr-quality-segment').count() == 4, '四类质量状态')
    check(page.locator('.dr-method-grid .dr-hbar').count() == 7, '七类方法分布')
    check(page.locator('html').get_attribute('data-theme') == 'light', '浅色主题默认可见')
    page.screenshot(path=str(OUT / 'report-desktop-light.png'))
    page.locator('#work').scroll_into_view_if_needed()
    page.screenshot(path=str(OUT / 'report-charts-light.png'))

    page.locator('[data-view="quality"]').click()
    status = 'Agent初评，待校准'
    count = DATA['project_quality_counts'][status]
    page.locator(f'[data-quality-filter="{status}"]').click()
    check(f'匹配 {count} 项' in page.locator('#detail-count').inner_text(), '质量筛选与当前快照一致')
    pages = max(1, (count + 14) // 15)
    for current_page in range(1, pages + 1):
        expected = min(15, count - (current_page - 1) * 15)
        check(page.locator('[data-panel="projects"] tbody tr:visible').count() == expected, f'质量筛选第{current_page}页数量正确')
        check(page.locator('#detail-page').inner_text() == f'{current_page} / {pages}', f'质量筛选页码{current_page}/{pages}')
        if current_page < pages:
            page.locator('#detail-next').click()
    page.locator('[data-quality-filter=""]').click()
    check('匹配 98 项' in page.locator('#detail-count').inner_text(), '查看全部恢复98项')
    page.locator(f'[data-quality-filter="{status}"]').focus()
    page.keyboard.press('Space')
    check(f'匹配 {count} 项' in page.locator('#detail-count').inner_text(), '质量按钮键盘Space筛选')
    page.locator('[data-quality-filter=""]').click()
    page.locator('#report-search').fill('2025-01')
    check('匹配 1 项' in page.locator('#detail-count').inner_text(), '项目搜索精确到1项')
    page.locator('#report-search').fill('不存在-075')
    check('没有符合条件的条目' in page.locator('#detail-count').inner_text(), '搜索空态')
    page.locator('#report-search').fill('')
    page.locator('[data-table="methods"]').click()
    check('匹配 64 项' in page.locator('#detail-count').inner_text(), '方法清单64项')
    page.locator('#report-search').fill('R48')
    check('匹配 1 项' in page.locator('#detail-count').inner_text(), '方法搜索R48')
    page.locator('[data-table="projects"]').click()
    page.locator('#report-search').fill('')

    page.locator('[data-view="value"]').click()
    page.locator('.dr-legend-item').first.click()
    check('award=' in page.url, '奖项图更新当前筛选')
    page.locator('#asset-explore').click()
    page.wait_for_load_state('networkidle')
    check(page.locator('#award').input_value() == '金奖', '项目库继承金奖筛选')
    check('98' in page.locator('#result-count').inner_text(), '金奖筛选98项')
    page.go_back(wait_until='networkidle')
    page.locator('#asset-clear').click()
    page.locator('[aria-label="2020年 100个项目"]').click()
    page.locator('#asset-explore').click()
    page.wait_for_load_state('networkidle')
    check(page.locator('#year').input_value() == '2020', '项目库继承2020筛选')
    check('100' in page.locator('#result-count').inner_text(), '2020年筛选100项')
    page.go_back(wait_until='networkidle')
    page.locator('[data-view="quality"]').click()
    page.locator('.dr-evidence-link').first.click()
    page.wait_for_load_state('domcontentloaded')
    check('project=2025-00' in page.url, '证据点进入对应项目档案')
    page.go_back(wait_until='networkidle')
    page.locator('.dr-evidence-link').first.focus()
    page.keyboard.press('Enter')
    page.wait_for_url('**/dossier/?project=2025-00')
    check('project=2025-00' in page.url, '证据点键盘Enter进入项目')
    page.go_back(wait_until='networkidle')

    page.locator('[data-gd-theme-toggle]').click()
    check(page.locator('html').get_attribute('data-theme') == 'dark', '深色主题切换')
    page.locator('[data-gd-theme-toggle]').click()
    check(page.locator('html').get_attribute('data-theme') == 'light', '浅色主题恢复')
    page.emulate_media(media='print')
    check(page.locator('#details').evaluate('(el) => getComputedStyle(el).display') == 'none', '打印隐藏交互清单')
    check(page.locator('.dr-professional-head').is_visible(), '打印保留专业视图')
    page.emulate_media(media='screen')

    for width in (1440, 1280, 1024, 768, 390, 360):
        page.set_viewport_size({'width': width, 'height': 844})
        page.goto('http://127.0.0.1:8892/inno/report/', wait_until='networkidle')
        check(page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'{width}px无全页横向溢出')
        if width == 390:
            page.screenshot(path=str(OUT / 'report-mobile-light.png'))
            page.locator('#work').scroll_into_view_if_needed()
            page.locator('.dr-chart-scroll').evaluate_all('(els) => els.forEach(el => { el.scrollLeft = 0; })')
            page.screenshot(path=str(OUT / 'report-mobile-charts.png'))
            page.locator('#research').scroll_into_view_if_needed()
            check(page.locator('.dr-chart-scroll').first.evaluate('(el) => el.scrollWidth >= el.clientWidth'), '手机图表使用局部滚动')
    page.emulate_media(reduced_motion='reduce')
    check(page.locator('.dr-evidence-point').first.evaluate('(el) => getComputedStyle(el).transitionDuration') == '0s', '减少动态偏好生效')
    check(not errors, '无浏览器脚本异常')
    check(not failed, '无本地资源失败')
    browser.close()

report = {'checks': checks, 'errors': errors, 'failed_resources': failed}
(OUT / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
print(json.dumps({'check_count': len(checks), 'errors': errors, 'failed_resources': failed}, ensure_ascii=False))
