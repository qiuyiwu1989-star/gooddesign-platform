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
    check(page.locator('h1').first.inner_text() == '创新设计大模型', '官方模型标题保持')
    check('让真实项目经验，参与下一次创新' in page.locator('.mo-tagline').inner_text(), '首屏价值主张清晰')
    check('不是单一基础模型' in page.locator('.mo-hero-summary').inner_text(), '模型定义不夸大')
    check(page.locator('[data-model-layer]').count() == 3, '三层架构可交互')
    for key, marker in (('engine', '让模型调用知识与方法'), ('applications', '从真实问题出发'), ('database', '一个项目，只有一份主档案')):
        page.locator(f'[data-model-layer="{key}"]').click()
        check(marker in page.locator('.mo-system-detail').inner_text(), f'{key}层详情正确')
        check(page.locator(f'[data-model-layer="{key}"]').get_attribute('aria-pressed') == 'true', f'{key}层选中状态')
    for key, marker in (('connect', '比较相似机制'), ('create', '形成候选方向'), ('validate', '把已知、推断和待验证分开'), ('understand', '从任务约束理解设计选择')):
        page.locator(f'[data-capability="{key}"]').click()
        check(marker in page.locator('.mo-capability-detail').inner_text(), f'{key}能力详情正确')
        check(page.locator(f'[data-capability="{key}"]').get_attribute('aria-pressed') == 'true', f'{key}能力选中状态')
    check(page.locator('.mo-status-facts dd').all_inner_texts() == ['560', '103', '64', '12'], '当前资产与MCP口径正确')
    check('不宣称已经自主训练基础大模型' in page.locator('.mo-boundaries').inner_text(), '模型能力边界明确')
    page.screenshot(path=str(OUT / 'model-hero.png'))
    for element in page.locator('.mo-reveal').all():
        element.scroll_into_view_if_needed()
        page.wait_for_timeout(90)
    page.evaluate('window.scrollTo({top:0,behavior:"instant"})')
    page.screenshot(path=str(OUT / 'model-full.png'), full_page=True)
    page.pdf(path=str(OUT / 'model-a4.pdf'), format='A4', print_background=True, prefer_css_page_size=True)
    pdf = fitz.open(OUT / 'model-a4.pdf')
    check(3 <= pdf.page_count <= 12, f'模型页打印页数合理（{pdf.page_count}页）')
    pdf.close()

    page.goto('http://127.0.0.1:8892/about/', wait_until='networkidle')
    check(page.locator('.about-model').count() == 1, '关于页有独立大模型板块')
    check('让项目、方法与智能研究' in page.locator('.about-model').inner_text(), '大模型板块价值明确')
    check(page.locator('.about-model-flow article').count() == 3, '大模型三层关系完整')
    check(page.locator('.about-model a[href="/model/"]').count() == 1, '关于页提供模型入口')
    check(page.locator('.about-model a[href="/expo/"]').count() == 1, '关于页提供产业研究入口')
    page.locator('.about-model').screenshot(path=str(OUT / 'about-model-section.png'))
    page.locator('.about-model a[href="/model/"]').click()
    page.wait_for_url('**/model/')
    check(page.locator('h1').first.inner_text() == '创新设计大模型', '关于页到模型页路径真实')

    for route in ('/model/', '/about/'):
        for width in (1440, 1280, 1024, 768, 390, 360):
            page.set_viewport_size({'width': width, 'height': 900})
            page.goto('http://127.0.0.1:8892' + route, wait_until='networkidle')
            check(page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'{route}{width}px无横向溢出')
            if route == '/model/' and width == 390:
                page.screenshot(path=str(OUT / 'model-mobile.png'), full_page=True)
            if route == '/about/' and width == 390:
                page.screenshot(path=str(OUT / 'about-mobile-model.png'), full_page=True)
        page.set_viewport_size({'width': 1440, 'height': 1000})
        page.goto('http://127.0.0.1:8892' + route, wait_until='networkidle')
        page.locator('[data-gd-theme-toggle]').click()
        page.wait_for_timeout(700)
        check(page.locator('html').get_attribute('data-theme') == 'dark', f'{route}深色主题生效')
        page.locator('[data-gd-theme-toggle]').click()

    reduced = browser.new_context(viewport={'width': 1440, 'height': 1000}, reduced_motion='reduce')
    rp = reduced.new_page()
    rp.goto('http://127.0.0.1:8892/model/', wait_until='networkidle')
    check(rp.locator('.mo-reveal').count() == 0, '减少动态不隐藏模型内容')
    reduced.close()
    check(not errors, '无浏览器脚本异常：' + repr(errors))
    check(not failed, '无资源加载失败：' + repr(failed))
    browser.close()

report = {'check_count': len(checks), 'checks': checks, 'errors': errors, 'failed_resources': failed}
(OUT / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
