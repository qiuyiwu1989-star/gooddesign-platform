import json
from pathlib import Path
import fitz
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/design-159'
OUT.mkdir(parents=True, exist_ok=True)
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
    page.goto('http://127.0.0.1:8892/model/', wait_until='networkidle')
    check(page.locator('.mo-architecture-map svg').count() == 1, '三层协同原生SVG存在')
    check('三层协同全景图' in page.locator('#mo-map-title').text_content(), '架构图具备可读标题')
    check('项目档案数据库向设计创新引擎提供项目、方法和证据' in page.locator('#mo-map-desc').text_content(), '架构图说明真实关系')
    check(page.locator('.mo-map-node').count() == 7, '输入与应用节点完整')
    check(page.locator('.mo-map-core').count() == 1, '研究中枢唯一')
    check('证据可信环' in page.locator('.mo-architecture-map').inner_text() and '验证生长环' in page.locator('.mo-architecture-map').inner_text(), '双环进入全景图')
    page.locator('#architecture').scroll_into_view_if_needed()
    page.wait_for_timeout(600)
    page.locator('.mo-architecture-map').screenshot(path=str(OUT / 'architecture-map-161.png'))

    check(page.locator('.mo-capability-tabs button').count() == 4, '四能力工作台完整')
    check(len(page.locator('.mo-capability-tabs').evaluate('(el)=>getComputedStyle(el).gridTemplateColumns.split(" ")')) == 2, '四能力为2×2布局')
    check(page.locator('.mo-capability-tabs button').first.evaluate('(el)=>getComputedStyle(el).borderRadius') == '16px', '能力卡不使用胶囊样式')
    for key, marker in (('connect', '比较相似机制'), ('create', '形成候选方向'), ('validate', '把已知、推断和待验证分开'), ('understand', '从任务约束理解设计选择')):
        page.locator(f'[data-capability="{key}"]').click()
        check(marker in page.locator('.mo-capability-detail').inner_text(), f'{key}能力详情正确')
        check(page.locator(f'[data-capability="{key}"]').get_attribute('aria-pressed') == 'true', f'{key}选中状态')
    page.locator('#capabilities').scroll_into_view_if_needed()
    page.wait_for_timeout(500)
    page.locator('#capabilities').screenshot(path=str(OUT / 'capabilities-161.png'))

    check(page.locator('.mo-app-source').count() == 1, '真实项目证据中心唯一')
    check(page.locator('.mo-app-branch').count() == 4, '四条真实应用路径完整')
    for index, route in enumerate(('/museum/', '/museum/#education', '/needs/', '/expo/')):
        check(page.locator('.mo-app-branch').nth(index).get_attribute('href') == route, f'应用路径{route}正确')
    check(page.locator('.mo-app-source').get_attribute('href') == '/cases/chang-e/', '证据中心连接真实应用案例')
    page.locator('#applications').scroll_into_view_if_needed()
    page.wait_for_timeout(500)
    page.locator('#applications').screenshot(path=str(OUT / 'applications-161.png'))
    check(page.locator('.mo-status-facts dd').all_inner_texts() == ['560', '103', '64', '12'], 'MCP12口径不变')

    for width in (1440, 1280, 1024, 768, 390, 360):
        page.set_viewport_size({'width': width, 'height': 900})
        page.goto('http://127.0.0.1:8892/model/', wait_until='networkidle')
        check(page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'{width}px全页无横向溢出')
        if width <= 390:
            page.locator('#architecture').scroll_into_view_if_needed()
            check(page.locator('.mo-architecture-map').evaluate('(el)=>el.scrollWidth>el.clientWidth'), f'{width}px架构图使用局部滚动')
            page.locator('.mo-architecture-map').evaluate('(el)=>el.scrollLeft=0')
            page.locator('#applications').scroll_into_view_if_needed()
            page.wait_for_timeout(450)
            page.locator('#applications').screenshot(path=str(OUT / 'applications-mobile-161.png')
            )
    page.set_viewport_size({'width': 1440, 'height': 1000})
    page.goto('http://127.0.0.1:8892/model/', wait_until='networkidle')
    for element in page.locator('.mo-reveal').all():
        element.scroll_into_view_if_needed()
        page.wait_for_timeout(70)
    page.pdf(path=str(OUT / 'model-visual-a4.pdf'), format='A4', print_background=True, prefer_css_page_size=True)
    pdf = fitz.open(OUT / 'model-visual-a4.pdf')
    check(3 <= pdf.page_count <= 12, f'可视化模型页打印页数合理（{pdf.page_count}页）')
    check('证据可信环' in ''.join(item.get_text() for item in pdf), '打印保留架构图文本')
    pdf.close()
    page.locator('[data-gd-theme-toggle]').click()
    page.wait_for_timeout(700)
    check(page.locator('html').get_attribute('data-theme') == 'dark', '深色主题生效')
    page.locator('[data-gd-theme-toggle]').click()
    reduced = browser.new_context(viewport={'width': 1440, 'height': 1000}, reduced_motion='reduce')
    rp = reduced.new_page()
    rp.goto('http://127.0.0.1:8892/model/', wait_until='networkidle')
    check(rp.locator('.mo-reveal').count() == 0, '减少动态不隐藏架构内容')
    reduced.close()
    check(not errors, '无浏览器脚本异常：' + repr(errors))
    check(not failed, '无资源加载失败：' + repr(failed))
    browser.close()

report = {'check_count': len(checks), 'checks': checks, 'errors': errors, 'failed_resources': failed}
(OUT / 'report-161.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
