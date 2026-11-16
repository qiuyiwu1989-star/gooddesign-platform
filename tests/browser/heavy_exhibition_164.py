import json
from pathlib import Path
import fitz
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/design-164'
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
    check(page.locator('.heavy-project').count() == 8, '八件项目完整')
    check(page.locator('.heavy-step').count() == 24, '每件项目三个镜头')
    check(page.locator('.heavy-evidence-link').count() == 8, '每件项目仅保留一个证据入口')
    check(page.locator('.heavy-project-actions').count() == 0, '旧三按钮退出')
    check(page.locator('.heavy-hero h1').evaluate('(el)=>parseFloat(getComputedStyle(el).fontSize)') == 96, '桌面首屏标题96px')
    check(page.locator('.heavy-hero h1').evaluate('(el)=>getComputedStyle(el).fontWeight') == '600', '首屏字重回到600')
    page.screenshot(path=str(OUT / 'hero-desktop.png'))
    second = page.locator('#project-2015-02 .heavy-step[data-step="2"]')
    second.scroll_into_view_if_needed()
    page.wait_for_function('document.querySelector(\'#project-2015-02\').dataset.activeStep === \'2\'', timeout=8000)
    check(page.locator('#project-2015-02').get_attribute('data-active-step') == '2', '滚动进入设计局部镜头')
    page.wait_for_function('getComputedStyle(document.querySelector(\'#project-2015-02 .heavy-step[data-step="2"]\')).opacity === \'1\'', timeout=3000)
    check(second.evaluate('(el)=>getComputedStyle(el).opacity') == '1', '当前镜头完整可读')
    page.screenshot(path=str(OUT / 'project-detail.png'))
    third = page.locator('#project-2015-02 .heavy-step[data-step="3"]')
    third.scroll_into_view_if_needed()
    page.wait_for_function('document.querySelector(\'#project-2015-02\').dataset.activeStep === \'3\'', timeout=8000)
    check(page.locator('#project-2015-02').get_attribute('data-active-step') == '3', '滚动进入策展收束镜头')
    for image in page.locator('.heavy-project-media img').all():
        image.scroll_into_view_if_needed()
        page.wait_for_timeout(100)
        check(image.evaluate('(img)=>img.complete&&img.naturalWidth>0'), '镜头图片加载：' + image.get_attribute('alt'))

    page.locator('[data-heavy-browse]').click()
    check(page.locator('#heavy-browser').evaluate('(el)=>el.open'), '快速浏览打开')
    check(page.locator('.heavy-browser-links a').count() == 8, '快速浏览包含八件项目')
    page.locator('.heavy-browser-links a[href="#project-2025-00"]').click()
    page.wait_for_timeout(500)
    check(not page.locator('#heavy-browser').evaluate('(el)=>el.open'), '选择后关闭快速浏览')
    check(page.url.endswith('#project-2025-00'), '快速浏览直达深空项目')
    page.locator('[data-heavy-present]').click()
    check(page.locator('body').evaluate('(el)=>el.classList.contains("heavy-presenting")'), '细看进入纯净展示')
    check(page.locator('header.gd-nav').evaluate('(el)=>getComputedStyle(el).display') == 'none', '细看隐藏导航')
    check(page.locator('[data-heavy-present]').inner_text() == '退出细看', '细看退出状态明确')
    page.locator('[data-heavy-present]').click()
    check(not page.locator('body').evaluate('(el)=>el.classList.contains("heavy-presenting")'), '退出细看恢复页面')
    check(page.locator('header.gd-nav').evaluate('(el)=>getComputedStyle(el).display') != 'none', '退出后恢复导航')
    check(page.locator('#project-2025-00 .heavy-evidence-link').get_attribute('href') == '/dossier/?project=2025-00', '嫦娥证据链接正确')

    for width in (1440, 1280, 1024, 768, 390, 360):
        page.set_viewport_size({'width': width, 'height': 900})
        page.goto('http://127.0.0.1:8892/museum/hall', wait_until='networkidle')
        check(page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'{width}px全页无横向溢出')
        if width <= 800:
            check(page.locator('.heavy-step').first.evaluate('(el)=>getComputedStyle(el).opacity') == '1', f'{width}px镜头内容直接可读')
        if width == 390:
            page.screenshot(path=str(OUT / 'hero-mobile.png'))
            check(page.locator('.heavy-controls').evaluate('(el)=>el.getBoundingClientRect().right < document.querySelector(\'.gd-ip-trigger\').getBoundingClientRect().left'), '手机控制条与小好不重叠')
            page.locator('[data-heavy-present]').click()
            check(page.locator('body').evaluate('(el)=>el.classList.contains("heavy-presenting")'), '手机细看可点击')
            page.locator('[data-heavy-present]').click()
            page.locator('#project-2015-02 .heavy-step[data-step="2"]').scroll_into_view_if_needed()
            page.screenshot(path=str(OUT / 'project-mobile.png'))

    page.set_viewport_size({'width': 1440, 'height': 1000})
    page.goto('http://127.0.0.1:8892/museum/hall', wait_until='networkidle')
    page.pdf(path=str(OUT / 'heavy-exhibition-a4.pdf'), format='A4', print_background=True, prefer_css_page_size=True)
    pdf = fitz.open(OUT / 'heavy-exhibition-a4.pdf')
    text = ''.join(item.get_text() for item in pdf)
    check(6 <= pdf.page_count <= 30, f'沉浸展打印页数合理（{pdf.page_count}页）')
    check('真实任务' in text and '设计局部' in text and '策展收束' in text, '打印保留三镜头内容')
    pdf.close()
    reduced = browser.new_context(viewport={'width': 1440, 'height': 1000}, reduced_motion='reduce')
    rp = reduced.new_page()
    rp.goto('http://127.0.0.1:8892/museum/hall', wait_until='networkidle')
    check(rp.locator('.heavy-step').first.evaluate('(el)=>getComputedStyle(el).opacity') == '1', '减少动态不隐藏镜头')
    check(rp.locator('.heavy-project-media img').first.evaluate('(el)=>getComputedStyle(el).transitionDuration') == '0s', '减少动态关闭镜头过渡')
    reduced.close()
    check(not errors, '无浏览器脚本异常：' + repr(errors))
    check(not failed, '无资源加载失败：' + repr(failed))
    browser.close()

report = {'check_count': len(checks), 'checks': checks, 'errors': errors, 'failed_resources': failed}
(OUT / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
