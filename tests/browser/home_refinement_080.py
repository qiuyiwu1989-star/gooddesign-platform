import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/design-080/after'
OUT.mkdir(parents=True, exist_ok=True)
URL = 'http://127.0.0.1:8892/inno/'
checks = []
errors = []
failed = []


def check(condition, label):
    if not condition:
        raise AssertionError(label)
    checks.append(label)


def contrast(page, selector, pseudo=None):
    return page.locator(selector).first.evaluate('''(el, pseudo) => {
      const parse = value => {
        const parts = value.match(/[\\d.]+/g)?.map(Number) || [0, 0, 0, 1];
        return [parts[0], parts[1], parts[2], parts.length > 3 ? parts[3] : 1];
      };
      const over = (top, bottom) => {
        if (top[3] === 0) return bottom;
        if (bottom[3] === 0) return top;
        const a = top[3] + bottom[3] * (1 - top[3]);
        return [0, 1, 2].map(i => (top[i] * top[3] + bottom[i] * bottom[3] * (1 - top[3])) / a).concat(a);
      };
      let background = [0, 0, 0, 0];
      const layers = [];
      for (let node = el; node; node = node.parentElement) layers.push(node);
      const body = parse(getComputedStyle(document.body).backgroundColor);
      for (const node of layers.reverse()) background = over(parse(getComputedStyle(node).backgroundColor), background);
      background = over(background, body);
      const foreground = over(parse(getComputedStyle(el, pseudo).color), background);
      const luminance = rgba => rgba.slice(0, 3).map(v => {
        const c = v / 255;
        return c <= .04045 ? c / 12.92 : ((c + .055) / 1.055) ** 2.4;
      }).reduce((sum, v, i) => sum + v * [.2126, .7152, .0722][i], 0);
      const a = luminance(foreground);
      const b = luminance(background);
      return (Math.max(a, b) + .05) / (Math.min(a, b) + .05);
    }''', pseudo)


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1440, 'height': 1000}, color_scheme='light')
    page = context.new_page()
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('requestfailed', lambda request: failed.append(request.url))

    for width in (1440, 1280, 1024, 768, 390, 360):
        page.set_viewport_size({'width': width, 'height': 900})
        page.goto(URL, wait_until='networkidle')
        check(page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'{width}px无全页横向溢出')
        check(page.locator('.gd-project-card').count() == 12, f'{width}px每页12个真实项目')
        columns = page.locator('.gd-project-grid').evaluate('(el) => getComputedStyle(el).gridTemplateColumns.split(" ").length')
        expected = 3 if width > 1100 else 2 if width > 767 else 1
        check(columns == expected, f'{width}px项目网格正确降级')
        cover_height = page.locator('.gd-project-cover').first.evaluate('(el) => el.getBoundingClientRect().height')
        check(cover_height <= 212, f'{width}px封面不被旧min-height撑高')
        controls = page.locator('#hero-search button, #filters input, #filters select, #clear, [data-gd-theme-toggle]')
        heights = controls.evaluate_all('(els) => els.filter(el => el.getBoundingClientRect().height > 0).map(el => el.getBoundingClientRect().height)')
        check(all(height >= 44 for height in heights), f'{width}px主要触控目标至少44px')
        if width >= 1024:
            nav_height = page.locator('.gd-nav-inner').evaluate('(el) => el.getBoundingClientRect().height')
            check(nav_height <= 80, f'{width}px桌面导航单行且不超过80px')
        check(page.locator('#stats-research').inner_text() != '-', f'{width}px研究统计来自真实目录')
        arrows = page.locator('a').evaluate_all('(links) => links.map(a => a.textContent).filter(t => /[→↗↑←↘↙]/.test(t))')
        check(not arrows, f'{width}px链接文字无箭头')
        if width == 1440:
            page.screenshot(path=str(OUT / 'home-light-top.png'))
            page.locator('#collection').scroll_into_view_if_needed()
            page.screenshot(path=str(OUT / 'home-light-collection.png'))
            check(contrast(page, '.gd-lead') >= 4.5, '浅色导语对比度至少4.5:1')
            check(contrast(page, '#hero-search button') >= 4.5, '浅色主按钮对比度至少4.5:1')
            check(contrast(page, '#query', '::placeholder') >= 4.5, '浅色搜索占位文字对比度至少4.5:1')
        if width == 390:
            page.screenshot(path=str(OUT / 'home-mobile-top.png'))
            page.locator('#collection').scroll_into_view_if_needed()
            page.screenshot(path=str(OUT / 'home-mobile-collection.png'))

    page.set_viewport_size({'width': 1440, 'height': 1000})
    page.goto(URL, wait_until='networkidle')
    check(page.locator('#clear').is_disabled(), '初始清除按钮禁用')
    check(page.locator('#previous').is_disabled(), '初始上一页禁用')
    check(page.locator('#next').is_enabled(), '初始下一页可用')
    initial_border = page.locator('#hero-search').evaluate('(el) => getComputedStyle(el).borderColor')
    page.locator('#hero-query').focus()
    page.wait_for_timeout(250)
    focused_border = page.locator('#hero-search').evaluate('(el) => getComputedStyle(el).borderColor')
    check(initial_border != focused_border, '搜索容器具有清晰focus-within状态')
    page.locator('#hero-query').fill('嫦娥')
    page.locator('#hero-search button').click()
    check('q=%E5%AB%A6%E5%A8%A5' in page.url, '首屏搜索写入URL')
    check('560 个项目' not in page.locator('#result-count').inner_text(), '首屏搜索真实过滤目录')
    check(page.locator('.gd-project-card').count() > 0, '搜索结果有真实项目')
    check(page.locator('#clear').is_enabled(), '有筛选时清除按钮启用')
    page.locator('#clear').click()
    check(page.locator('#result-count').inner_text() == '560 个项目', '清除恢复完整目录')
    check(page.locator('#clear').is_disabled(), '恢复后清除按钮再次禁用')
    check(page.locator('#hero-query').input_value() == '', '清除同步首屏搜索框')

    research_count = page.locator('#stats-research').inner_text()
    page.locator('#status').select_option('research')
    check(page.locator('#result-count').inner_text() == f'{research_count} 个项目', '研究状态筛选与统计一致')
    check('status=research' in page.url, '研究状态写入URL')
    page.locator('#clear').click()
    page.locator('#award').select_option('金奖')
    check('award=%E9%87%91%E5%A5%96' in page.url, '奖项筛选写入URL')
    check('560 个项目' not in page.locator('#result-count').inner_text(), '奖项真实过滤目录')
    page.locator('#clear').click()

    page.locator('#query').fill('不存在的项目关键字080')
    check(page.locator('#empty').is_visible(), '无结果状态可见')
    check(page.locator('#pagination').is_hidden(), '无结果时隐藏分页')
    page.locator('#empty-clear').click()
    check(page.locator('#result-count').inner_text() == '560 个项目', '空状态可恢复全部项目')
    page.locator('#next').click()
    check(page.locator('#page-state').inner_text().startswith('2 /'), '下一页真实翻页')
    check('page=2' in page.url, '页码写入URL')
    check(page.locator('#previous').is_enabled(), '第二页上一页可用')
    page.go_back(wait_until='networkidle')
    check(page.locator('#page-state').inner_text().startswith('1 /'), '浏览器回退恢复第一页')
    page.goto(URL + '?q=%E5%AB%A6%E5%A8%A5', wait_until='networkidle')
    check(page.locator('#query').input_value() == '嫦娥', 'URL恢复搜索条件')
    check(page.locator('#hero-query').input_value() == '嫦娥', 'URL同步首屏搜索条件')
    page.goto(URL, wait_until='networkidle')

    search_button = page.locator('#hero-search button')
    search_button.hover()
    page.mouse.down()
    transform = search_button.evaluate('(el) => getComputedStyle(el).transform')
    check(transform != 'none', '主按钮具有按下反馈')
    page.mouse.up()

    page.locator('[data-gd-theme-toggle]').click()
    check(page.locator('html').get_attribute('data-theme') == 'dark', '深色主题生效')
    page.wait_for_timeout(400)
    check(contrast(page, '.gd-lead') >= 4.5, '深色导语对比度至少4.5:1')
    check(contrast(page, '#hero-search button') >= 4.5, '深色主按钮对比度至少4.5:1')
    check(contrast(page, '#query', '::placeholder') >= 4.5, '深色搜索占位文字对比度至少4.5:1')
    page.screenshot(path=str(OUT / 'home-dark-top.png'))
    page.locator('#collection').scroll_into_view_if_needed()
    page.screenshot(path=str(OUT / 'home-dark-collection.png'))

    lcp = page.evaluate('''() => new Promise(resolve => {
      const observer = new PerformanceObserver(list => {
        const entries = list.getEntries();
        resolve(entries.length ? entries.at(-1).startTime : 0);
        observer.disconnect();
      });
      observer.observe({type: 'largest-contentful-paint', buffered: true});
      setTimeout(() => resolve(0), 600);
    })''')
    check(0 < lcp < 2500, '本地首屏LCP小于2.5秒')
    check(not errors, '无浏览器脚本异常')
    check(not failed, '无页面资源加载失败')

    reduced = browser.new_context(viewport={'width': 1280, 'height': 900}, color_scheme='light', reduced_motion='reduce')
    reduced_page = reduced.new_page()
    reduced_page.goto(URL, wait_until='networkidle')
    check(reduced_page.locator('.gd-project-card').first.evaluate('(el) => getComputedStyle(el).transitionDuration') == '0s', '减少动态偏好关闭卡片过渡')
    reduced.close()

    error_page = context.new_page()
    error_page.route('**/catalog.json', lambda route: route.abort())
    error_page.goto(URL, wait_until='networkidle')
    check('项目目录加载失败' in error_page.locator('#empty').inner_text(), '目录失败显示真实错误')
    check(error_page.locator('#empty-clear').inner_text() == '重新加载', '错误状态提供重试动作')
    error_page.unroute('**/catalog.json')
    error_page.locator('#empty-clear').click()
    error_page.wait_for_load_state('networkidle')
    check(error_page.locator('#result-count').inner_text() == '560 个项目', '重试后恢复真实目录')
    error_page.close()

    loading_page = context.new_page()
    loading_page.route('**/catalog.json', lambda route: (time.sleep(.5), route.continue_()))
    loading_page.goto(URL, wait_until='domcontentloaded')
    check(loading_page.locator('.gd-project-skeleton').count() == 3, '载入骨架与最终三列布局同形')
    loading_page.wait_for_load_state('networkidle')
    check(loading_page.locator('.gd-project-card').count() == 12, '载入完成后显示真实项目')
    loading_page.close()
    browser.close()

report = {'check_count': len(checks), 'checks': checks, 'errors': errors, 'failed_resources': failed}
(OUT / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'check_count': len(checks), 'errors': errors, 'failed_resources': failed}, ensure_ascii=False))
