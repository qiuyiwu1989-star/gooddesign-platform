import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
BASE = os.environ.get('GOODDESIGN_BASE', 'http://127.0.0.1:8892/inno')
OUT = ROOT / 'output/design-097'
OUT.mkdir(parents=True, exist_ok=True)
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
    page.goto(BASE + '/model/', wait_until='networkidle')
    check(page.locator('h1').first.inner_text() == '创新设计大模型', '官方模型标题')
    check(page.locator('main#main').count() == 1, '正文焦点落点唯一')
    check(page.locator('.gd-nav').count() == 1 and page.locator('.gd-footer').count() == 1, '共享顶底栏唯一')
    check(round(page.locator('.gd-nav').evaluate('(el) => el.getBoundingClientRect().height')) == 65, '桌面导航65px')
    check(page.locator('[data-model-layer]').count() == 3, '三层架构可交互')
    for key, marker in (('engine', '让模型调用知识与方法'), ('applications', '从真实问题出发'), ('database', '一个项目，只有一份主档案')):
        page.locator(f'[data-model-layer="{key}"]').click()
        check(marker in page.locator('.mo-system-detail').inner_text(), f'{key}层详情正确')
        check(page.locator(f'[data-model-layer="{key}"]').get_attribute('aria-pressed') == 'true', f'{key}层选中状态')
    for key, marker in (('connect', '比较相似机制'), ('create', '形成候选方向'), ('validate', '把已知、推断和待验证分开'), ('understand', '从任务约束理解设计选择')):
        page.locator(f'[data-capability="{key}"]').click()
        check(marker in page.locator('.mo-capability-detail').inner_text(), f'{key}能力详情正确')
        check(page.locator(f'[data-capability="{key}"]').get_attribute('aria-pressed') == 'true', f'{key}能力选中状态')
    page.screenshot(path=str(OUT / 'model-hero.png'))

    for element in page.locator('.mo-reveal').all():
        element.scroll_into_view_if_needed()
        page.wait_for_timeout(80)
    check(page.locator('.mo-reveal:not(.mo-visible)').count() == 0, '滚动叙事全部正常显现')
    page.evaluate('window.scrollTo({top:0,behavior:"instant"})')
    page.screenshot(path=str(OUT / 'model-desktop-scrolled.png'), full_page=True)
    page.locator('[data-gd-theme-toggle]').click()
    check(page.locator('html').get_attribute('data-theme') == 'dark', '深色主题生效')
    page.screenshot(path=str(OUT / 'model-dark.png'))
    page.locator('[data-gd-theme-toggle]').click()

    for route in ('/', '/methods/', '/dossier/?project=2019-s19', '/museum/', '/apps/', '/about/'):
        page.goto(BASE + route, wait_until='networkidle')
        check(round(page.locator('.gd-nav').evaluate('(el) => el.getBoundingClientRect().height')) == 65, f'{route}导航尺寸一致')
        check(round(page.locator('.gd-footer').evaluate('(el) => el.getBoundingClientRect().height')) == 139, f'{route}底部尺寸一致')
        check(page.locator('.gd-nav').evaluate('(el) => getComputedStyle(el).fontFamily') == page.locator('.gd-footer').evaluate('(el) => getComputedStyle(el).fontFamily'), f'{route}顶底字体一致')

    for width in (1280, 1024, 768, 390, 360):
        page.set_viewport_size({'width': width, 'height': 900})
        page.goto(BASE + '/model/', wait_until='networkidle')
        check(page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'{width}px无横向溢出')
        check(page.locator('.gd-links a').evaluate_all('(links) => links.every(a => getComputedStyle(a).whiteSpace === "nowrap" && a.scrollWidth <= a.clientWidth + 1)'), f'{width}px导航标签不换行')
        if width == 390:
            page.screenshot(path=str(OUT / 'model-mobile.png'), full_page=True)

    reduced = browser.new_context(viewport={'width': 1440, 'height': 1000}, reduced_motion='reduce')
    reduced_page = reduced.new_page()
    reduced_page.goto(BASE + '/model/', wait_until='networkidle')
    check(reduced_page.locator('.mo-reveal').count() == 0, '减少动态时不隐藏内容')
    reduced.close()
    check(not errors, '无浏览器脚本异常')
    check(not failed, '无资源加载失败')
    browser.close()

report = {'base': BASE, 'check_count': len(checks), 'checks': checks, 'errors': errors, 'failed_resources': failed}
(OUT / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'base': BASE, 'check_count': len(checks), 'errors': errors, 'failed_resources': failed}, ensure_ascii=False))
