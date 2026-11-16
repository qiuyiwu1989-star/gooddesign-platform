import json
from pathlib import Path
import fitz
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/design-156'
OUT.mkdir(parents=True, exist_ok=True)
BASE = 'http://127.0.0.1:8892/report/'
DATA = json.loads((ROOT / 'extensions/project-portal/data-report.json').read_text())
checks = []
errors = []
failed = []


def check(value, label):
    if not value:
        raise AssertionError(label)
    checks.append(label)


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1440, 'height': 1000}, color_scheme='light')
    page = context.new_page()
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('requestfailed', lambda request: failed.append(request.url))
    response = page.goto(BASE, wait_until='networkidle')
    check(response.status == 200, '数据总览返回200')
    check(page.locator('[data-view-panel="value"]:visible').count() == 2, '默认显示完整价值视图')
    check(page.locator('[data-view-panel="quality"]:visible').count() == 0, '默认隐藏专业质量视图')
    check(page.locator('.dr-core-facts strong').all_inner_texts() == ['560', '103', '64', '12'], '全库核心资产口径正确')
    check(page.locator('.dr-value-chain>div').count() == 5, '知识价值链五层完整')
    check(page.locator('.dr-showcase-card:visible').count() == 6, '默认展示六个代表项目')
    check(page.locator('.dr-depth-bars .dr-hbar b').evaluate_all('(els)=>els.reduce((n,e)=>n+parseInt(e.textContent),0)') == 98, '研究深度分档合计98案')
    check(page.locator('.dr-benchmark-card').count() == 3, '三个代表研究档案完整')
    page.screenshot(path=str(OUT / 'value-hero.png'))
    page.locator('#work').screenshot(path=str(OUT / 'value-assets.png'))
    page.locator('#research').screenshot(path=str(OUT / 'value-research.png'))
    page.locator('#benchmarks').screenshot(path=str(OUT / 'value-benchmarks.png'))

    page.locator('.dr-legend-item').first.click()
    check('award=' in page.url and '%E9%87%91' in page.url, '奖项筛选写入可分享URL')
    check(page.locator('.dr-legend-item.dr-selected').count() == 1, '奖项图选中状态唯一')
    check(page.locator('.dr-donut-segment.dr-muted').count() == 4, '奖项环图非选中项降噪')
    gold_cards = page.locator('.dr-showcase-card[data-award="金奖"]').count()
    check(f'{gold_cards} 个代表项目' in page.locator('#asset-filter-status').inner_text(), '金奖代表项目联动计数正确')
    page.locator('[aria-label="2025年 33个项目"]').click()
    check('year=2025' in page.url, '年度筛选同步写入URL')
    combined_cards = page.locator('.dr-showcase-card[data-year="2025"][data-award="金奖"]').count()
    check(page.locator('.dr-showcase-card:visible').count() == combined_cards, '奖项与年度组合筛选代表项目')
    check(f'2025年 · 金奖 · {combined_cards} 个代表项目' in page.locator('#asset-filter-status').inner_text(), '组合筛选状态清楚')
    check('year=2025' in page.locator('#asset-explore').get_attribute('href') and 'award=' in page.locator('#asset-explore').get_attribute('href'), '项目库入口继承组合筛选')
    page.locator('#asset-clear').click()
    check('year=' not in page.url and 'award=' not in page.url, '清除筛选同步清理URL')
    check(page.locator('.dr-showcase-card:visible').count() == 6, '清除后恢复代表项目')

    page.goto(BASE + '?year=2024&award=%E9%87%91%E5%A5%96', wait_until='networkidle')
    shared_cards = page.locator('.dr-showcase-card[data-year="2024"][data-award="金奖"]').count()
    check(page.locator('.dr-showcase-card:visible').count() == shared_cards, '分享链接恢复组合筛选')
    page.locator('#asset-explore').click()
    page.wait_for_load_state('networkidle')
    check(page.locator('#year').input_value() == '2024' and page.locator('#award').input_value() == '金奖', '项目库真实继承年度和奖项')
    page.go_back(wait_until='networkidle')

    page.locator('[data-view="quality"]').click()
    check(page.locator('[data-view-panel="quality"]:visible').count() == 1, '专业视图可切换')
    check('view=quality' in page.url, '专业视图写入URL')
    page.reload(wait_until='networkidle')
    check(page.locator('[data-view-panel="quality"]:visible').count() == 1, '刷新后保持专业视图')
    check(page.locator('.dr-evidence-link').count() == 98, '专业视图保留98个证据点')
    check('726' in page.locator('.dr-asset-strip').inner_text() and '2,579' in page.locator('.dr-asset-strip').inner_text(), '专业视图为更新后金奖数据')
    calibrated = DATA['project_quality_counts']['独立Agent校准，非专家']
    page.locator('[data-quality-filter="独立Agent校准，非专家"]').click()
    check(f'匹配 {calibrated} 项' in page.locator('#detail-count').inner_text(), '质量筛选与当前快照一致')
    page.locator('[data-quality-filter=""]').click()
    check('匹配 98 项' in page.locator('#detail-count').inner_text(), '查看全部恢复98项')
    page.locator('#report-search').fill('2025-01')
    check('匹配 1 项' in page.locator('#detail-count').inner_text(), '项目搜索保持可用')
    page.locator('#report-search').fill('')
    page.locator('[data-table="methods"]').click()
    check('匹配 64 项' in page.locator('#detail-count').inner_text(), '方法清单64项保持可用')
    page.locator('#report-search').fill('R48')
    check('匹配 1 项' in page.locator('#detail-count').inner_text(), '方法搜索保持可用')
    page.locator('#report-search').fill('')
    page.locator('[data-table="projects"]').click()
    page.locator('.dr-evidence-link').first.focus()
    page.keyboard.press('Enter')
    page.wait_for_url('**/dossier/?project=2025-00')
    check('project=2025-00' in page.url, '证据点键盘Enter进入档案')
    page.go_back(wait_until='networkidle')
    page.screenshot(path=str(OUT / 'quality-hero.png'))

    page.locator('[data-view="value"]').click()
    page.locator('[data-gd-theme-toggle]').click()
    page.wait_for_timeout(700)
    check(page.locator('html').get_attribute('data-theme') == 'dark', '深色主题生效')
    check(page.locator('.dr-heading h1').evaluate('(el)=>getComputedStyle(el).color') == 'rgb(236, 238, 255)', '深色标题对比色正确')
    check(page.evaluate("getComputedStyle(document.body).backgroundColor === 'rgb(7, 7, 15)'"), '深色页面背景完整生效')
    page.screenshot(path=str(OUT / 'value-dark.png'))
    page.locator('[data-gd-theme-toggle]').click()

    for width in (1440, 1280, 1024, 768, 390, 360):
        page.set_viewport_size({'width': width, 'height': 900})
        page.goto(BASE, wait_until='networkidle')
        check(page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'价值视图{width}px无横向溢出')
        if width == 390:
            page.screenshot(path=str(OUT / 'value-mobile.png'), full_page=True)
        page.locator('[data-view="quality"]').click()
        check(page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'专业视图{width}px无横向溢出')
        if width == 390:
            page.locator('#evidence').scroll_into_view_if_needed()
            check(page.locator('#evidence .dr-chart-scroll').evaluate('(el)=>el.scrollWidth>=el.clientWidth'), '手机证据图局部滚动')

    page.set_viewport_size({'width': 1440, 'height': 1000})
    page.goto(BASE, wait_until='networkidle')
    page.pdf(path=str(OUT / 'value-a4.pdf'), format='A4', print_background=True, prefer_css_page_size=True)
    pdf = fitz.open(OUT / 'value-a4.pdf')
    check(3 <= pdf.page_count <= 12, f'价值视图A4打印页数合理（{pdf.page_count}页）')
    check('看见设计知识' in pdf[0].get_text(), '打印首页保留数据价值主张')
    pdf[0].get_pixmap(matrix=fitz.Matrix(1.2, 1.2)).save(OUT / 'print-value.png')
    pdf.close()
    reduced = browser.new_context(viewport={'width': 1440, 'height': 1000}, reduced_motion='reduce')
    rp = reduced.new_page()
    rp.goto(BASE, wait_until='networkidle')
    check(rp.locator('.dr-evidence-point').first.evaluate('(el)=>getComputedStyle(el).transitionDuration') == '0s', '减少动态偏好生效')
    reduced.close()
    check(not errors, '无浏览器脚本异常：' + repr(errors))
    check(not failed, '无资源加载失败：' + repr(failed))
    browser.close()

report = {'check_count': len(checks), 'checks': checks, 'errors': errors, 'failed_resources': failed}
(OUT / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
