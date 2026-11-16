import json
from pathlib import Path
import fitz
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/design-163'
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
    page.goto('http://127.0.0.1:8892/museum/hall', wait_until='networkidle')
    check(page.locator('.heavy-chapter').count() == 4, '四章专题路线完整')
    check(page.locator('.heavy-project').count() == 8, '八件真实项目完整')
    check(page.locator('.heavy-project-actions a').count() == 24, '每件项目三个真实入口')
    for image in page.locator('.heavy-project-media img').all():
        image.scroll_into_view_if_needed()
        page.wait_for_timeout(120)
        check(image.evaluate('(img)=>img.complete&&img.naturalWidth>0'), '项目图片真实加载：' + image.get_attribute('alt'))
    check('十年编年' not in page.locator('main').inner_text() and '互动乐园' not in page.locator('main').inner_text(), '旧门户与编年退出专题页')
    check(page.locator('.gd-nav').count() == 1 and page.locator('.gd-footer').count() == 1, '统一导航与页脚')
    page.screenshot(path=str(OUT / 'hero-desktop.png'))
    page.locator('[data-chapter-link="chapter-4"]').click()
    page.wait_for_function('document.querySelector(\'[data-chapter-link="chapter-4"]\').getAttribute(\'aria-current\') === \'true\'', timeout=8000)
    check(page.url.endswith('#chapter-4'), '章节导航深链正确')
    check(page.locator('[data-chapter-link="chapter-4"]').get_attribute('aria-current') == 'true', '当前章节状态同步')
    check(page.locator('#project-2025-00').is_visible(), '深空项目可见')
    page.locator('#project-2025-00').screenshot(path=str(OUT / 'project-chang-e.png'))
    check(page.locator('#project-2025-00 .heavy-action-primary').get_attribute('href') == '/museum/x-ray?slug=2025-00', '嫦娥拆解入口正确')
    page.goto('http://127.0.0.1:8892/museum/hall#hall-chron', wait_until='networkidle')
    check(page.locator('#hall-chron').is_visible(), '旧编年锚点落到专题结束页')
    check(page.locator('#hall-chron a[href="/projects/"]').is_visible(), '结束页提供统一项目库入口')

    for width in (1440, 1280, 1024, 768, 390, 360):
        page.set_viewport_size({'width': width, 'height': 900})
        page.goto('http://127.0.0.1:8892/museum/hall', wait_until='networkidle')
        check(page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'{width}px全页无横向溢出')
        if width <= 768:
            check(len(page.locator('#project-2015-02').evaluate('(el)=>getComputedStyle(el).gridTemplateColumns.split(" ")')) == 1, f'{width}px项目单列阅读')
        if width == 390:
            page.screenshot(path=str(OUT / 'hero-mobile.png'))
            page.locator('#project-2015-02').screenshot(path=str(OUT / 'project-mobile.png'))

    page.set_viewport_size({'width': 1440, 'height': 1000})
    page.goto('http://127.0.0.1:8892/museum/hall', wait_until='networkidle')
    page.pdf(path=str(OUT / 'heavy-exhibition-a4.pdf'), format='A4', print_background=True, prefer_css_page_size=True)
    pdf = fitz.open(OUT / 'heavy-exhibition-a4.pdf')
    text = ''.join(item.get_text() for item in pdf)
    check(4 <= pdf.page_count <= 24, f'专题展打印页数合理（{pdf.page_count}页）')
    check('国之重器' in text and '蛟龙号载人潜水器' in text and '嫦娥五/六号' in text, '打印保留首末项目内容')
    pdf.close()
    reduced = browser.new_context(viewport={'width': 1440, 'height': 1000}, reduced_motion='reduce')
    rp = reduced.new_page()
    rp.goto('http://127.0.0.1:8892/museum/hall', wait_until='networkidle')
    check(rp.locator('.heavy-project-media img').first.evaluate('(el)=>getComputedStyle(el).transitionDuration') == '0s', '减少动态关闭图片过渡')
    check(rp.locator('.heavy-project').count() == 8, '减少动态仍完整呈现八件项目')
    reduced.close()
    check(not errors, '无浏览器脚本异常：' + repr(errors))
    check(not failed, '无资源加载失败：' + repr(failed))
    browser.close()

report = {'check_count': len(checks), 'checks': checks, 'errors': errors, 'failed_resources': failed}
(OUT / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
