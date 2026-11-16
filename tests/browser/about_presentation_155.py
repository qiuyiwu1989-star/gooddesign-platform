import json
from pathlib import Path
import fitz
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/design-155'
OUT.mkdir(parents=True, exist_ok=True)
BASE = 'http://127.0.0.1:8892'
checks = []
errors = []
failed = []


def check(value, label):
    if not value:
        raise AssertionError(label)
    checks.append(label)


def ready(page):
    page.goto(BASE + '/about/', wait_until='networkidle')
    page.wait_for_timeout(850)


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1440, 'height': 1000}, color_scheme='light')
    page = context.new_page()
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('requestfailed', lambda request: failed.append(request.url))
    response = page.goto(BASE + '/about/', wait_until='networkidle')
    check(response.status == 200, '关于页返回200')
    page.wait_for_timeout(850)
    check(page.locator('h1').inner_text().replace('\n', '') == '让真实创新，成为下一次创新的起点。', '品牌主张清晰完整')
    check('好设计连接真实获奖项目' in page.locator('meta[name="description"]').get_attribute('content'), '对外搜索摘要完整')
    check(page.locator('main#main').count() == 1, '正文主焦点唯一')
    check(page.locator('.gd-nav').count() == 1 and page.locator('.gd-footer').count() == 1, '统一导航与页脚唯一')
    check(page.locator('.about-hero-art img').evaluate('(img)=>img.complete && img.naturalWidth > 0'), '首屏真实项目封面加载')
    check(page.locator('.about-fact').count() == 4, '四项真实资产数据可见')
    check(page.locator('.about-fact strong').all_inner_texts() == ['560', '103', '64', '8'], '项目研究方法与应用计数正确')
    check(page.locator('.about-path-step').count() == 5, '作品到应用五步路径完整')
    check(page.locator('.about-case-layout img').count() == 3, '三个代表项目视觉完整')
    check(page.locator('.about-case-layout img').evaluate_all('(imgs)=>imgs.every(i=>i.complete && i.naturalWidth>0)'), '代表项目封面全部有效')
    check(page.locator('.about-application').count() == 4, '四类应用场景完整')
    check(page.locator('.about-trust-grid>div').count() == 4, '可信原则四项完整')
    for href in ('/expo/', '/loop/', '/museum/', '/museum/#education', '/needs/', '/apps/', '/mcp/'):
        check(page.locator(f'.about-page a[href="{href}"]').count() >= 1, f'真实入口{href}存在')
    check(page.locator('.about-page a').evaluate_all('(links)=>links.every(a=>!/[↗↘→←↔⇄↑↓]/.test(a.innerText))'), '所有页面链接无箭头字符')
    check(not page.locator('.about-page').evaluate('(el)=>/客户评价|战略合作企业|工程认证通过/.test(el.innerText)'), '不虚构客户合作或工程认证')
    page.keyboard.press('Tab')
    check(page.evaluate('document.activeElement.classList.contains("gd-skip")'), '键盘第一焦点为跳转正文')
    page.locator('.about-actions a[href="#applications"]').click()
    check(page.evaluate('location.hash') == '#applications', '场景锚点可直达')
    page.evaluate('window.scrollTo({top:0,behavior:"instant"})')
    page.screenshot(path=str(OUT / 'desktop-hero.png'))
    page.screenshot(path=str(OUT / 'desktop-full.png'), full_page=True)
    page.locator('.about-case-layout').screenshot(path=str(OUT / 'desktop-cases.png'))
    page.locator('#applications').screenshot(path=str(OUT / 'desktop-applications.png'))
    page.evaluate('window.scrollTo({top:0,behavior:"instant"})')

    page.locator('[data-gd-theme-toggle]').click()
    page.wait_for_timeout(250)
    check(page.locator('html').get_attribute('data-theme') == 'dark', '深色主题生效')
    check(page.locator('.about-hero h1').evaluate('(el)=>getComputedStyle(el).color') == 'rgb(236, 238, 255)', '深色标题对比色正确')
    page.screenshot(path=str(OUT / 'dark-hero.png'))
    page.locator('.about-trust').screenshot(path=str(OUT / 'dark-trust.png'))
    page.evaluate('window.scrollTo({top:0,behavior:"instant"})')
    page.locator('[data-gd-theme-toggle]').click()

    for width in (1440, 1280, 1024, 768, 390, 360):
        page.set_viewport_size({'width': width, 'height': 900})
        ready(page)
        check(page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'{width}px无横向溢出')
        check(page.locator('.about-hero-art').is_visible(), f'{width}px真实项目视觉保留')
        check(page.locator('.about-application').count() == 4, f'{width}px应用场景完整')
        if width == 390:
            page.screenshot(path=str(OUT / 'mobile-full.png'), full_page=True)
            page.locator('.about-case-layout').screenshot(path=str(OUT / 'mobile-cases.png'))
            page.evaluate('window.scrollTo({top:0,behavior:"instant"})')

    reduced = browser.new_context(viewport={'width': 1440, 'height': 1000}, reduced_motion='reduce')
    rp = reduced.new_page()
    ready(rp)
    check(rp.locator('.about-hero-copy').evaluate('(el)=>getComputedStyle(el).animationName') == 'none', '减少动态时无入场动画')
    check(rp.locator('.about-hero-copy').evaluate('(el)=>getComputedStyle(el).opacity') == '1', '减少动态时内容立即可见')
    reduced.close()

    page.set_viewport_size({'width': 1440, 'height': 1000})
    ready(page)
    page.emulate_media(media='print')
    check(page.locator('.about-art-copy strong').evaluate('(el)=>getComputedStyle(el).color') == 'rgb(255, 255, 255)', '打印深色项目封面保留白色标题')
    page.pdf(path=str(OUT / 'about-a4.pdf'), format='A4', print_background=True, prefer_css_page_size=True)
    pdf = fitz.open(OUT / 'about-a4.pdf')
    check(3 <= pdf.page_count <= 12, f'关于页A4打印页数合理（{pdf.page_count}页）')
    check('让真实创新' in pdf[0].get_text(), '打印首页保留品牌主张')
    check(not any('全屏展示' in item.get_text() for item in pdf), '打印不混入其他应用控件')
    pdf[0].get_pixmap(matrix=fitz.Matrix(1.25, 1.25)).save(OUT / 'print-cover.png')
    trust_page = next((i for i, item in enumerate(pdf) if '答案从哪里来' in item.get_text()), None)
    check(trust_page is not None, '打印保留可信原则')
    if trust_page is not None:
        pdf[trust_page].get_pixmap(matrix=fitz.Matrix(1.25, 1.25)).save(OUT / 'print-trust.png')
    pdf.close()
    check(not errors, '无浏览器脚本异常：' + repr(errors))
    check(not failed, '无资源加载失败：' + repr(failed))
    browser.close()

report = {'check_count': len(checks), 'checks': checks, 'errors': errors, 'failed_resources': failed}
(OUT / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
