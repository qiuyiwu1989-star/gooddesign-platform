import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/playwright/gooddesign-mcp-077'
OUT.mkdir(parents=True, exist_ok=True)
BASE = 'http://127.0.0.1:8892/inno/mcp/'
checks = []
errors = []
failed = []


def check(condition, label):
    if not condition:
        raise AssertionError(label)
    checks.append(label)


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1440, 'height': 1000}, color_scheme='light', permissions=['clipboard-read', 'clipboard-write'])
    page = context.new_page()
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('requestfailed', lambda request: failed.append(request.url))
    page.goto(BASE, wait_until='networkidle')
    check(page.locator('h1').inner_text() == 'MCP 接入中心', '接入中心产品定位')
    check(page.locator('.mcp-tool').count() == 8, '八项远程只读工具')
    check(page.locator('.mcp-facts').inner_text().find('120KB') >= 0, '首屏显示返回边界')
    page.screenshot(path=str(OUT / 'mcp-desktop-light.png'))

    page.locator('[data-tool-filter="discovery"]').click()
    check(page.locator('.mcp-tool:visible').count() == 3, '发现分组三项')
    page.locator('[data-tool-filter="read"]').click()
    check(page.locator('.mcp-tool:visible').count() == 4, '深读分组四项')
    page.locator('[data-tool-filter="prepare"]').click()
    check(page.locator('.mcp-tool:visible').count() == 1, '组包分组一项')
    page.locator('[data-tool-filter="all"]').click()
    page.locator('#tool-search').fill('evidence')
    check(page.locator('.mcp-tool:visible').count() == 1, '证据工具搜索')
    page.locator('#tool-search').fill('不存在-077')
    check(page.locator('#tool-empty').is_visible(), '工具搜索空态')
    page.locator('#tool-search').fill('')
    page.locator('.mcp-tool summary').nth(3).click()
    check('project_id' in page.locator('.mcp-tool').nth(3).inner_text(), '工具参数可展开')
    page.locator('#tools').scroll_into_view_if_needed()
    page.screenshot(path=str(OUT / 'mcp-tools-light.png'))

    page.locator('#copy-config').click()
    check('请先填写私有访问密钥' in page.locator('#copy-status').inner_text(), '空密钥提示')
    check(page.evaluate('document.activeElement.id') == 'mcp-token', '空密钥聚焦输入')
    fake_key = 'qa-not-a-real-mcp-key-077'
    page.locator('#mcp-token').fill(fake_key)
    check(fake_key not in page.locator('#mcp-config').inner_text(), '真实密钥不进入配置预览')
    page.locator('#copy-config').click()
    page.wait_for_function("document.querySelector('#copy-status').textContent.includes('已复制 JSON 配置')")
    check('已复制 JSON 配置' in page.locator('#copy-status').inner_text(), 'JSON复制反馈')
    clipboard = page.evaluate('navigator.clipboard.readText()')
    check(fake_key in clipboard and 'gooddesign-innovation' in clipboard, 'JSON复制只进入用户剪贴板')
    page.locator('[data-format="toml"]').click()
    check(page.locator('#codex-env-note').is_visible(), 'TOML环境变量说明')
    check('GOODDESIGN_MCP_TOKEN' in page.locator('#mcp-config').inner_text(), 'TOML使用环境变量')
    page.locator('#copy-config').click()
    page.wait_for_function("document.querySelector('#copy-status').textContent.includes('已复制 Codex TOML')")
    clipboard = page.evaluate('navigator.clipboard.readText()')
    check('GOODDESIGN_MCP_TOKEN' in clipboard and fake_key not in clipboard, 'TOML不包含明文密钥')
    page.evaluate("dispatchEvent(new Event('pagehide'))")
    check(page.locator('#mcp-token').input_value() == '', 'pagehide清空密钥')
    page.locator('#copy-prompt').click()
    page.wait_for_function("navigator.clipboard.readText().then(text => text.includes('gooddesign-innovation'))")
    check('gooddesign-innovation' in page.evaluate('navigator.clipboard.readText()'), '任务描述可复制')
    page.locator('#copy-endpoint').click()
    page.wait_for_function("navigator.clipboard.readText().then(text => text.includes('/inno/mcp/api'))")
    check(page.evaluate('navigator.clipboard.readText()') == 'https://opendesign.cc/inno/mcp/api', '服务地址可复制')

    page.locator('[data-gd-theme-toggle]').click()
    check(page.locator('html').get_attribute('data-theme') == 'dark', '深色主题切换')
    page.evaluate('scrollTo(0, 0)')
    page.wait_for_timeout(300)
    page.screenshot(path=str(OUT / 'mcp-desktop-dark.png'))
    page.locator('[data-gd-theme-toggle]').click()
    check(page.locator('html').get_attribute('data-theme') == 'light', '浅色主题恢复')

    for width in (1440, 1280, 1024, 768, 390, 360):
        page.set_viewport_size({'width': width, 'height': 844})
        page.goto(BASE, wait_until='networkidle')
        check(page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'{width}px无全页横向溢出')
        if width == 390:
            page.screenshot(path=str(OUT / 'mcp-mobile-light.png'))
            page.locator('#tools').scroll_into_view_if_needed()
            check(page.locator('#tool-search').is_visible(), '手机工具搜索可用')

    fallback = browser.new_context(viewport={'width': 1280, 'height': 800})
    fallback.add_init_script("navigator.clipboard.writeText = () => Promise.reject(new Error('denied'))")
    other = fallback.new_page()
    other.goto(BASE, wait_until='networkidle')
    other.locator('#copy-endpoint').click()
    check(other.locator('#copy-dialog').is_visible(), '复制拒绝时打开降级对话框')
    check(other.locator('#copy-dialog-text').input_value() == 'https://opendesign.cc/inno/mcp/api', '降级内容已准备')
    other.keyboard.press('Escape')
    check(not other.locator('#copy-dialog').is_visible(), '降级对话框Escape关闭')
    fallback.close()
    check(not errors, '无浏览器脚本异常')
    check(not failed, '无本地资源失败')
    context.close()
    browser.close()

report = {'checks': checks, 'errors': errors, 'failed_resources': failed}
(OUT / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
print(json.dumps({'check_count': len(checks), 'errors': errors, 'failed_resources': failed}, ensure_ascii=False))
