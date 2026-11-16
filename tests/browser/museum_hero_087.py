import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/design-087'
checks = []
errors = []
failed = []


def check(condition, label):
    if not condition:
        raise AssertionError(label)
    checks.append(label)


def contrast(page, selector):
    return page.locator(selector).evaluate('''(el) => {
      const color = getComputedStyle(el).color.match(/[\\d.]+/g).map(Number);
      const alpha = color.length > 3 ? color[3] : 1;
      const bg = [29, 29, 39];
      const fg = color.slice(0, 3).map((v, i) => v * alpha + bg[i] * (1 - alpha));
      const lum = rgb => rgb.map(v => { const c = v / 255; return c <= .04045 ? c / 12.92 : ((c + .055) / 1.055) ** 2.4; }).reduce((s, v, i) => s + v * [.2126, .7152, .0722][i], 0);
      const a = lum(fg), b = lum(bg);
      return (Math.max(a, b) + .05) / (Math.min(a, b) + .05);
    }''')


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1440, 'height': 1000}, color_scheme='light')
    page = context.new_page()
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('requestfailed', lambda request: failed.append(request.url))
    page.goto('http://127.0.0.1:8892/categories.html', wait_until='networkidle')
    background = page.locator('.page-hero').evaluate('(el) => getComputedStyle(el).backgroundImage')
    check('rgb(21, 21, 28)' in background and 'rgb(39, 35, 47)' in background, '石墨色渐变实际生效')
    check('45, 79, 175' not in background and '89, 132, 214' not in background, '旧高饱和蓝色不再生效')
    check(page.locator('.page-hero h1').evaluate('(el) => getComputedStyle(el).fontFamily').startswith('-apple-system'), '标题使用系统无衬线')
    check(page.locator('.ph-kicker').evaluate('(el) => getComputedStyle(el).color') == 'rgb(245, 154, 130)', '珊瑚色提示与品牌一致')
    check(contrast(page, '.page-hero h1') >= 4.5, '主标题对比度至少4.5:1')
    check(contrast(page, '.ph-en') >= 4.5, '英文副标题对比度至少4.5:1')
    check(contrast(page, '.ph-sub') >= 4.5, '首屏正文对比度至少4.5:1')
    page.screenshot(path=str(OUT / 'categories-light.png'))

    for width in (1440, 1280, 1024, 768, 390, 360):
        page.set_viewport_size({'width': width, 'height': 900})
        page.goto('http://127.0.0.1:8892/categories.html', wait_until='networkidle')
        check(page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'{width}px首屏无横向溢出')
        check(page.locator('.page-hero h1').is_visible(), f'{width}px主标题完整可见')
        check(page.locator('.ph-sub').is_visible(), f'{width}px首屏正文可读')
        if width == 390:
            page.screenshot(path=str(OUT / 'categories-mobile.png'))

    page.set_viewport_size({'width': 1440, 'height': 1000})
    page.goto('http://127.0.0.1:8892/inno/museum/', wait_until='networkidle')
    home_background = page.locator('.foyer').evaluate('(el) => getComputedStyle(el).backgroundImage')
    check(home_background == background, '馆首页与展区使用同一石墨色首屏')
    check(contrast(page, '.foyer h1') >= 4.5, '馆首页标题对比度至少4.5:1')
    check(contrast(page, '.foyer .lead') >= 4.5, '馆首页导语对比度至少4.5:1')
    page.screenshot(path=str(OUT / 'museum-light.png'))

    page.locator('[data-gd-theme-toggle]').click()
    check(page.locator('html').get_attribute('data-theme') == 'dark', '深色主题切换正常')
    check(page.locator('.foyer').evaluate('(el) => getComputedStyle(el).backgroundImage') == background, '深色仍保持同一石墨色首屏')
    page.screenshot(path=str(OUT / 'museum-dark.png'))
    check(page.locator('[data-gd-nav="museum"]').get_attribute('aria-current') == 'page', '好设计馆高亮保持')
    check(page.locator('footer').count() == 1, '统一底部保持')
    check(not errors, '无浏览器脚本异常')
    check(not failed, '无页面资源加载失败')
    browser.close()

report = {'check_count': len(checks), 'checks': checks, 'errors': errors, 'failed_resources': failed}
(OUT / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'check_count': len(checks), 'errors': errors, 'failed_resources': failed}, ensure_ascii=False))
