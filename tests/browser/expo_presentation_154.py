import json
from pathlib import Path
import fitz
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/design-154'
OUT.mkdir(parents=True, exist_ok=True)
URL = 'http://127.0.0.1:8897/expo/'
checks = []
errors = []


def check(value, label):
    if not value:
        raise AssertionError(label)
    checks.append(label)


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1600, 'height': 1000})
    page = context.new_page()
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.route('**/expo/api/places', lambda route: route.fulfill(
        status=200, content_type='application/json', body='{"places":[]}'))
    page.add_init_script("""
      const nativeSetTimeout = window.setTimeout;
      window.setTimeout = (fn, delay, ...args) => {
        if (delay === 180000) window.__idleCallback = () => fn(...args);
        return nativeSetTimeout(fn, delay, ...args);
      };
    """)
    page.goto(URL, wait_until='networkidle')
    check(page.locator('body>header.gd-nav').is_visible(), '普通模式显示统一全站导航')
    check(page.locator('#home>footer.gd-footer').is_visible(), '首页显示统一全站页脚')
    check(page.locator('[data-gd-theme-toggle]').inner_text() == '浅色', '深色状态提供浅色入口')

    page.locator('[data-gd-theme-toggle]').click()
    check(page.evaluate("document.documentElement.dataset.theme === 'light'"), '全站主题按钮切换应用为浅色')
    check(page.evaluate("getComputedStyle(document.body).getPropertyValue('--bg').trim() === '#f4f5f3'"), '浅色变量作用于应用而非仅全站导航')
    page.wait_for_selector('#layer-cty.ready')
    page.wait_for_function("getComputedStyle(document.querySelector('.cty:not(.lit)')).fill === 'rgb(226, 229, 225)'")
    check(page.evaluate("getComputedStyle(document.querySelector('.cty:not(.lit)')).fill === 'rgb(226, 229, 225)'"), '县级地图使用浅色的独立填色与边界')
    page.screenshot(path=str(OUT / 'home-light.png'))
    page.reload(wait_until='networkidle')
    check(page.evaluate("document.documentElement.dataset.theme === 'light'"), '刷新后保留浅色偏好')

    page.locator('.gd-nav-actions [data-expo-fullscreen]').click()
    page.wait_for_selector('body.expo-presenting')
    check(not page.locator('body>header.gd-nav').is_visible(), '全屏隐藏全站导航')
    check(not page.locator('#home>footer.gd-footer').is_visible(), '全屏隐藏全站页脚')
    check(page.locator('#fullscreen-exit').is_visible(), '全屏仅保留最小退出控制')
    check(page.evaluate('document.documentElement.scrollWidth <= innerWidth'), '浅色全屏首页无横向溢出')
    page.screenshot(path=str(OUT / 'home-pure.png'))
    page.locator('#fullscreen-exit').click()
    check(page.locator('body.expo-presenting').count() == 0, '退出按钮恢复普通页面')
    page.wait_for_function('document.fullscreenElement === null')
    check(page.evaluate('document.fullscreenElement === null'), '退出按钮同步退出浏览器全屏')

    page.evaluate("() => { document.documentElement.requestFullscreen = () => Promise.reject(new Error('denied')); }")
    page.locator('.gd-nav-actions [data-expo-fullscreen]').click()
    page.wait_for_selector('body.expo-presenting')
    check(page.locator('#fullscreen-exit').is_visible(), 'Fullscreen API 被拒绝时仍可使用纯净展示')
    page.keyboard.press('Escape')
    page.wait_for_selector('body:not(.expo-presenting)')
    check(not page.locator('#fullscreen-exit').is_visible(), 'Escape 同步退出 CSS 纯净展示')

    page.evaluate("void startStatic('嘉善')")
    page.wait_for_selector('.worker-card')
    page.locator('#run-controls [data-expo-fullscreen]').click()
    page.wait_for_selector('body.expo-presenting')
    check(not page.locator('#run-controls').is_visible(), '研究全屏隐藏返回暂停等操作区')
    check(page.locator('#think.on').is_visible(), '研究全屏保留实时研究内容')
    check(page.locator('.worker-card').count() == 3, '研究全屏保留多角色工位')
    page.wait_for_timeout(450)
    page.screenshot(path=str(OUT / 'research-pure-light.png'))
    page.keyboard.press('Escape')
    page.wait_for_selector('body:not(.expo-presenting)')
    check(page.locator('#run-controls').is_visible(), '研究退出全屏恢复原操作')
    page.locator('#pause').click()
    check(page.evaluate("getComputedStyle(document.querySelector('#logpane')).backgroundColor === 'rgb(255, 255, 255)'"), '研究日志浅色面板完整生效')
    check(page.evaluate("getComputedStyle(document.querySelector('.research-focus')).backgroundColor === 'rgb(255, 255, 255)'"), '研究聚焦详情使用浅色面板')
    page.screenshot(path=str(OUT / 'research-light.png'))
    page.locator('#pause').click()
    page.wait_for_selector('#report.on', timeout=30000)

    page.locator('#rbar [data-expo-fullscreen]').click()
    page.wait_for_selector('body.expo-presenting')
    check(not page.locator('#rbar').is_visible(), '报告全屏隐藏保存打印等工具栏')
    check(page.locator('#rdoc').is_visible() and page.locator('#rtoc').is_visible(), '报告全屏保留正文和目录')
    page.evaluate('window.__idleCallback()')
    check(page.locator('#report.on').is_visible(), '全屏展示不会被三分钟空闲计时打断')
    page.wait_for_timeout(600)
    page.screenshot(path=str(OUT / 'report-pure.png'))
    page.pdf(path=str(OUT / 'report-light-a4.pdf'), format='A4', print_background=True, prefer_css_page_size=True)
    pdf = fitz.open(OUT / 'report-light-a4.pdf')
    check(10 <= pdf.page_count <= 22, f'浅色全屏状态打印仍为完整 A4（{pdf.page_count}页）')
    pdf[0].get_pixmap(matrix=fitz.Matrix(1.2, 1.2)).save(OUT / 'print-cover.png')
    pdf.close()
    page.keyboard.press('Escape')
    page.wait_for_selector('body:not(.expo-presenting)')

    page.goto(URL + '?report=yuhuan&id=demo-yuhuan', wait_until='networkidle')
    page.wait_for_selector('#report.on')
    check('玉环产业' in page.locator('.rcover h1').inner_text(), '独立版本报告直链保持可用')
    check(page.evaluate("getComputedStyle(document.body).backgroundColor === 'rgb(242, 243, 245)'"), '浅色主题下报告保持纸张阅读版式')
    check(not errors, '浏览器无 JavaScript 异常：' + repr(errors))

    mobile = browser.new_context(viewport={'width': 390, 'height': 844})
    mp = mobile.new_page()
    mp.route('**/expo/api/places', lambda route: route.fulfill(status=200, content_type='application/json', body='{"places":[]}'))
    mp.add_init_script("localStorage.setItem('gd-preview-theme','light')")
    mp.goto(URL, wait_until='networkidle')
    mp.locator('.gd-nav-actions [data-expo-fullscreen]').click()
    mp.wait_for_selector('body.expo-presenting')
    check(mp.locator('#fullscreen-exit').is_visible(), '移动端保留可见退出按钮')
    check(mp.evaluate('document.documentElement.scrollWidth <= innerWidth'), '移动端纯净展示无横向溢出')
    mp.screenshot(path=str(OUT / 'mobile-pure-light.png'))
    mp.locator('#fullscreen-exit').click()
    check(mp.locator('body.expo-presenting').count() == 0, '移动端可正常退出')
    mobile.close()
    browser.close()

print(json.dumps({'checks': len(checks), 'passed': checks, 'errors': errors}, ensure_ascii=False, indent=2))
