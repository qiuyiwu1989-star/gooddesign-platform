import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/playwright/gooddesign-case-079'
OUT.mkdir(parents=True, exist_ok=True)
URL = 'http://127.0.0.1:8892/inno/dossier/?project=2019-s19'
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
    response = page.goto(URL, wait_until='networkidle')
    check(response.status == 200, '档案真实HTTP可访问')
    check(page.locator('h1').inner_text() == '6000HP电动压裂泵', '项目身份正确')
    check(page.locator('.gd-nav').count() == 1, '一个统一导航栏')
    check(page.locator('.gd-footer').count() == 1, '一个统一底部栏')
    check(page.locator('.research-guide').count() == 8, '八模块均有版本化导读')
    check('research-000001' in page.locator('body').inner_text(), '显示当前研究版本')
    check('45' in page.locator('.reader-metrics').inner_text(), '显示45条信息记录')
    check('未评' in page.locator('.reader-metrics').inner_text(), '不伪造质量评分')
    arrows = page.locator('a').evaluate_all('(links) => links.map(a => a.textContent).filter(t => /[→↗↑←↘↙]/.test(t))')
    check(not arrows, '超链接文字不使用箭头')

    page.locator('#reader-validation > summary').click()
    check(page.locator('#reader-validation').evaluate('(el) => el.open'), '指标与验证模块展开')
    check(page.locator('.reader-module[open]').count() == 1, '一次只展开一个模块')
    page.locator('#record-MET-020 > summary').click()
    page.locator('#record-MET-020').get_by_text('查看出处与原文', exact=True).first.click()
    quote = page.locator('#record-MET-020 blockquote').first.inner_text()
    check('8台6000马力压裂泵至少等同于20台以上传统柴油机压裂设备的性能' in quote, '媒体等效口径保留原文')
    page.locator('#record-MET-020').get_by_text('资料索引', exact=True).first.click()
    check(page.locator('#library-view').is_visible(), '证据链接进入资料视图')
    check(page.locator('#source-S8ae50c84687b0709').evaluate('(el) => el.open'), '定位并展开媒体来源')
    check('机器整理 · 不代表核读' in page.locator('#source-S8ae50c84687b0709').inner_text(), '来源核读状态独立显示')
    page.screenshot(path=str(OUT / 'sources-light.png'), full_page=False)

    page.goto(URL + '#record-MET-009', wait_until='networkidle')
    check(page.locator('#reader-validation').evaluate('(el) => el.open'), '深链自动展开指标模块')
    check(page.locator('#record-MET-009').evaluate('(el) => el.open'), '深链自动展开运行记录')
    check('132.2' in page.locator('#record-MET-009').inner_text(), '长宁H9一号泵组时间可见')
    page.locator('#record-MET-009').get_by_text('查看出处与原文', exact=True).first.click()
    check('132.2 h (66段)' in page.locator('#record-MET-009 blockquote').first.inner_text(), '运行时间和段数保持原口径')
    page.locator('#record-VAL-002 > summary').click()
    page.locator('#reader-validation .research-ai').filter(has_text='四川长宁H9平台压裂施工').nth(1).locator(':scope > summary').click()
    check('未取得原始施工日志' in page.locator('#reader-validation').inner_text(), '验证局限明确显示')
    page.screenshot(path=str(OUT / 'validation-light.png'), full_page=False)

    page.locator('[data-reader-tab="assessment"]').click()
    check(page.locator('#assessment-view').is_visible(), '档案评估视图可切换')
    assessment_text = page.locator('#assessment-view').inner_text()
    check('180 / 180' in assessment_text, '180项事实全部可追溯')
    check('42 / 42' in assessment_text, '42项AI分析依据和边界完整')
    check('专家审核：未完成' in assessment_text, '评估不冒称专家完成')
    check('取得9项国家专利逐项清单' in assessment_text, '补证优先级可见')
    page.locator('[data-gd-theme-toggle]').click()
    check(page.locator('html').get_attribute('data-theme') == 'dark', '深色主题生效')
    page.wait_for_timeout(500)
    contrast = page.locator('.research-box').first.evaluate('''(box) => {
      const rgb = (el, property) => getComputedStyle(el)[property].match(/[\\d.]+/g).slice(0, 3).map(Number);
      const luminance = values => values.map(v => { const c = v / 255; return c <= .04045 ? c / 12.92 : ((c + .055) / 1.055) ** 2.4; }).reduce((sum, v, i) => sum + v * [.2126, .7152, .0722][i], 0);
      const text = luminance(rgb(box.querySelector('p'), 'color'));
      const background = luminance(rgb(box, 'backgroundColor'));
      return (Math.max(text, background) + .05) / (Math.min(text, background) + .05);
    }''')
    check(contrast >= 4.5, '深色评估卡正文对比度至少4.5:1')
    page.screenshot(path=str(OUT / 'assessment-dark.png'), full_page=False)

    page.set_viewport_size({'width': 390, 'height': 844})
    page.goto(URL, wait_until='networkidle')
    page.locator('[data-gd-theme-toggle]').click()
    check(page.locator('html').get_attribute('data-theme') == 'light', '浅色主题恢复')
    page.wait_for_timeout(500)
    page.locator('#reader-validation > summary').focus()
    page.keyboard.press('Enter')
    check(page.locator('#reader-validation').evaluate('(el) => el.open'), '键盘可展开模块')
    check(page.evaluate('document.documentElement.scrollWidth <= innerWidth'), '390px无全页横向溢出')
    page.locator('#record-MET-020 > summary').click()
    check('至少等同于20台以上' in page.locator('#record-MET-020').inner_text(), '移动端媒体口径可读')
    page.screenshot(path=str(OUT / 'validation-mobile.png'), full_page=False)
    check(not errors, '无浏览器脚本异常')
    check(not failed, '无页面资源加载失败')
    browser.close()

report = {'checks': checks, 'errors': errors, 'failed_resources': failed}
(OUT / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
print(json.dumps({'check_count': len(checks), 'errors': errors, 'failed_resources': failed}, ensure_ascii=False))
