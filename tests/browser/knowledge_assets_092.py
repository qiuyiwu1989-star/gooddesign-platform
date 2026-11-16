import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/design-092'
OUT.mkdir(parents=True, exist_ok=True)
checks = []
errors = []
failed = []


def check(condition, label):
    if not condition:
        raise AssertionError(label)
    checks.append(label)


def visible_cards(page):
    return page.locator('.asset-card:visible').count()


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1440, 'height': 1000}, color_scheme='light')
    page = context.new_page()
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('requestfailed', lambda request: failed.append(request.url))
    response = page.goto('http://127.0.0.1:8896/', wait_until='networkidle')
    check(response.status == 200, '资产汇报页真实HTTP可访问')
    check(page.locator('.asset-card').count() == 8, '八张知识资产卡完整')
    check(visible_cards(page) == 8, '默认显示全部资产')
    check(page.locator('.asset-flow>div').count() == 4, '四层资产关系完整')
    check(page.locator('[data-asset-filter]').count() == 4, '四类筛选入口完整')
    check(len(page.locator('.asset-grid').evaluate('(el) => getComputedStyle(el).gridTemplateColumns.split(" ")')) == 4, '桌面四列卡片')
    check('显示 8 / 8 项资产' in page.locator('#asset-count').inner_text(), '初始资产数量正确')

    expectations = (('archive', 2), ('sources', 4), ('application', 2), ('all', 8))
    for kind, count in expectations:
        page.locator(f'[data-asset-filter="{kind}"]').click()
        check(visible_cards(page) == count, f'{kind}筛选显示{count}张卡片')
        check(page.locator(f'[data-asset-filter="{kind}"]').get_attribute('aria-pressed') == 'true', f'{kind}筛选状态同步')
        check(f'显示 {count} / 8 项资产' in page.locator('#asset-count').inner_text(), f'{kind}筛选计数正确')

    page.locator('[data-asset-filter="application"]').click()
    case_card = page.locator('[data-asset="case079"]')
    case_card.click()
    dialog = page.locator('#asset-detail')
    check(dialog.is_visible(), '079卡片打开真实详情')
    check(case_card.get_attribute('aria-expanded') == 'true', '079卡片展开状态同步')
    check(dialog.get_attribute('open') is not None, '详情使用原生dialog')
    check('079 原生单案示范' in dialog.inner_text(), '079详情标题正确')
    check('000001 研究版本' in dialog.inner_text(), '079研究版本正确')
    check('6000HP电动压裂泵' in dialog.inner_text(), '079单案内容正确')
    check('未评分、未专家审核' in dialog.inner_text(), '079审核边界保留')
    evidence = page.locator('#asset-detail-evidence')
    check(evidence.get_attribute('href') == '/research-079/2019-s19/publish-result.json', '079证据深链正确')
    check(page.request.get('http://127.0.0.1:8896' + evidence.get_attribute('href')).status == 200, '079证据真实可访问')
    dialog.screenshot(path=str(OUT / 'asset-detail-079.png'))
    page.locator('#asset-detail-close').click()
    check(not dialog.is_visible(), '关闭按钮关闭详情')
    check(case_card.evaluate('(el) => el === document.activeElement'), '关闭后焦点返回079卡片')
    page.wait_for_function("document.querySelector('[data-asset=case079]').getAttribute('aria-expanded') === 'false'")
    check(case_card.get_attribute('aria-expanded') == 'false', '关闭后展开状态复位')

    case_card.focus()
    page.keyboard.press('Enter')
    check(dialog.is_visible(), '键盘Enter可打开详情')
    page.keyboard.press('Escape')
    check(not dialog.is_visible(), 'Escape关闭详情')
    check(case_card.evaluate('(el) => el === document.activeElement'), 'Escape后焦点返回原卡片')

    page.locator('[data-asset-filter="all"]').click()
    page.locator('[data-asset="images"]').click()
    check('版权待核' in dialog.inner_text(), '图片详情保留版权边界')
    page.mouse.click(4, 4)
    check(not dialog.is_visible(), '点击对话框外部可关闭')
    check(page.locator('[data-asset="images"]').evaluate('(el) => el === document.activeElement'), '外部关闭后焦点返回图片卡片')

    page.locator('[data-assets]').screenshot(path=str(OUT / 'assets-desktop-light.png'))
    page.locator('[data-asset-filter="sources"]').click()
    page.evaluate("window.dispatchEvent(new Event('beforeprint'))")
    check(visible_cards(page) == 8, '打印前自动展开全部资产')
    page.emulate_media(media='print')
    check(not page.locator('.asset-toolbar').is_visible(), '打印隐藏筛选工具栏')
    page.emulate_media(media='screen')
    page.evaluate("window.dispatchEvent(new Event('afterprint'))")
    check(visible_cards(page) == 4, '打印后恢复来源素材筛选')
    check(page.locator('[data-asset-filter="sources"]').get_attribute('aria-pressed') == 'true', '打印后筛选状态正确恢复')
    page.locator('[data-asset-filter="all"]').click()

    page.locator('[data-gd-theme-toggle]').click()
    check(page.locator('html').get_attribute('data-theme') == 'dark', '深色主题生效')
    page.wait_for_timeout(200)
    page.locator('[data-assets]').screenshot(path=str(OUT / 'assets-desktop-dark.png'))
    page.locator('[data-asset="native"]').click()
    check('18.4%' in dialog.inner_text(), '深色详情保留真实原生覆盖率')
    check(dialog.evaluate('(el) => getComputedStyle(el, "::backdrop").backdropFilter') == 'none', '资产详情背景不模糊')
    page.keyboard.press('Escape')

    for width, columns in ((768, 2), (390, 1)):
        page.set_viewport_size({'width': width, 'height': 900})
        page.goto('http://127.0.0.1:8896/', wait_until='networkidle')
        check(page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'{width}px资产页无横向溢出')
        check(len(page.locator('.asset-grid').evaluate('(el) => getComputedStyle(el).gridTemplateColumns.split(" ")')) == columns, f'{width}px卡片为{columns}列')
        check(visible_cards(page) == 8, f'{width}px全部资产可见')
        if width == 390:
            if page.locator('html').get_attribute('data-theme') == 'dark':
                page.locator('[data-gd-theme-toggle]').click()
            check(len(page.locator('.asset-flow').evaluate('(el) => getComputedStyle(el).gridTemplateColumns.split(" ")')) == 2, '手机资产关系为两列网格')
            check(page.locator('.asset-flow').evaluate('(el) => el.scrollWidth <= el.clientWidth'), '手机四层关系无需横向滑动')
            page.locator('.asset-flow').screenshot(path=str(OUT / 'asset-flow-mobile-light.png'))
            page.locator('[data-assets]').screenshot(path=str(OUT / 'assets-mobile-light.png'))
            page.locator('[data-asset="case079"]').click()
            check(dialog.is_visible(), '手机端079详情可打开')
            check(dialog.evaluate('(el) => el.getBoundingClientRect().width <= innerWidth'), '手机端详情不超出视口')
            page.keyboard.press('Escape')

    check(not errors, '无浏览器脚本异常')
    check(not failed, '无页面资源加载失败')
    browser.close()

report = {'check_count': len(checks), 'checks': checks, 'errors': errors, 'failed_resources': failed}
(OUT / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'check_count': len(checks), 'errors': errors, 'failed_resources': failed}, ensure_ascii=False))
