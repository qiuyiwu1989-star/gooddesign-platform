import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/design-084'
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
    page.goto('http://127.0.0.1:8892/inno/', wait_until='networkidle')
    brand = page.locator('.gd-nav .gd-brand')
    check(brand.locator('strong').inner_text() == '好设计', '中文好设计为主标题')
    check(brand.locator('small').inner_text() == 'GoodDesign', '英文GoodDesign为辅助标识')
    chinese_size = brand.locator('strong').evaluate('(el) => parseFloat(getComputedStyle(el).fontSize)')
    english_size = brand.locator('small').evaluate('(el) => parseFloat(getComputedStyle(el).fontSize)')
    check(chinese_size == 20 and english_size == 10, '中文20px大于英文10px')
    check('v=084' in brand.locator('img').get_attribute('src'), 'Logo资源使用084版本防旧缓存')
    check(brand.locator('img').evaluate('(img) => img.complete && img.naturalWidth > 0'), '新Logo实际加载成功')
    check(brand.get_attribute('aria-label') == '好设计 GoodDesign 首页', '品牌首页无障碍名称一致')
    page.screenshot(path=str(OUT / 'brand-desktop-light.png'))
    footer = page.locator('.gd-footer .gd-brand')
    check(footer.locator('strong').inner_text() == '好设计', '页脚中文主标题一致')
    check(footer.locator('small').inner_text() == 'GoodDesign', '页脚英文辅助标识一致')
    check('v=084' in footer.locator('img').get_attribute('src'), '页脚Logo同样使用新版本')

    for width in (1440, 1280, 1024, 768, 390, 360):
        page.set_viewport_size({'width': width, 'height': 900})
        page.goto('http://127.0.0.1:8892/inno/', wait_until='networkidle')
        check(page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'{width}px品牌导航无横向溢出')
        check(page.locator('.gd-nav .gd-brand strong').is_visible(), f'{width}px中文主标题可见')
        check(page.locator('.gd-nav .gd-brand small').is_visible(), f'{width}px英文辅助标识可见')
        check(page.locator('.gd-nav .gd-brand img').evaluate('(img) => img.complete && img.naturalWidth > 0'), f'{width}pxLogo清晰加载')
        if width == 390:
            page.screenshot(path=str(OUT / 'brand-mobile-light.png'))

    page.set_viewport_size({'width': 1440, 'height': 1000})
    page.goto('http://127.0.0.1:8892/inno/dossier/?project=2019-s19', wait_until='networkidle')
    check(page.locator('.gd-nav .gd-brand strong').inner_text() == '好设计', '动态档案中文品牌一致')
    check('v=084' in page.locator('.gd-nav .gd-brand img').get_attribute('src'), '动态档案使用新Logo')
    page.locator('[data-gd-theme-toggle]').click()
    check(page.locator('html').get_attribute('data-theme') == 'dark', '深色主题生效')
    page.wait_for_timeout(300)
    page.screenshot(path=str(OUT / 'brand-dossier-dark.png'))
    check(page.locator('[data-gd-assistant-open]').count() == 1, '品牌更新不影响小好入口')
    page.locator('[data-gd-assistant-open]').click()
    check(page.locator('[data-gd-assistant]').is_visible(), '小好导览正常打开')
    page.keyboard.press('Escape')
    check(not errors, '无浏览器脚本异常')
    check(not failed, '无品牌或页面资源加载失败')
    browser.close()

report = {'check_count': len(checks), 'checks': checks, 'errors': errors, 'failed_resources': failed}
(OUT / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'check_count': len(checks), 'errors': errors, 'failed_resources': failed}, ensure_ascii=False))
