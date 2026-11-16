import json
import secrets
import string
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/deploy-093'
SCREEN = OUT / 'screens'
SCREEN.mkdir(parents=True, exist_ok=True)
BASE = 'https://opendesign.cc'
USER = 'qa093'
PASSWORD = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(24))
checks = []
errors = []
failed = []
bad_responses = []


def check(condition, label):
    if not condition:
        raise AssertionError(label)
    checks.append(label)


def remote(command, **kwargs):
    return subprocess.run(['ssh', '-o', 'BatchMode=yes', 'yongle-nanjing', command], check=True, **kwargs)


def watch(page):
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('requestfailed', lambda request: failed.append(request.url))
    page.on('response', lambda response: bad_responses.append(f'{response.status} {response.url}') if response.status >= 400 else None)


remote('sudo -n cp /etc/nginx/inno.htpasswd /var/lib/innovation-design/release-backups/20261104-093e/inno.htpasswd-qa093')
try:
    hashed = remote('openssl passwd -6 -stdin', input=PASSWORD + '\n', text=True, capture_output=True).stdout.strip()
    remote('sudo -n sh -c "cat >> /etc/nginx/inno.htpasswd"', input=f'{USER}:{hashed}\n', text=True, capture_output=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1440, 'height': 1000}, http_credentials={'username': USER, 'password': PASSWORD})
        page = context.new_page()
        watch(page)

        response = page.goto(BASE + '/inno/', wait_until='networkidle')
        check(response.status == 200, '生产首页200')
        check('看见好设计' in page.locator('h1').inner_text(), '新版首页内容')
        check(page.locator('.gd-nav').count() == 1 and page.locator('.gd-footer').count() == 1, '首页统一顶底栏')
        check(page.locator('.gd-footer-note').inner_text() == 'GoodDesign · OpenDesign 创新项目区', '生产页脚口径更新')
        page.locator('#query').fill('嫦娥')
        page.wait_for_timeout(350)
        check('嫦娥' in page.locator('#projects').inner_text(), '首页项目搜索真实可用')
        page.locator('#clear').click()
        page.locator('[data-gd-theme-toggle]').click()
        check(page.locator('html').get_attribute('data-theme') == 'dark', '首页深色主题')
        page.screenshot(path=str(SCREEN / 'home-dark.png'))

        response = page.goto(BASE + '/inno/needs/', wait_until='networkidle')
        check(response.status == 200, '需求研究主入口200')
        check('把真实问题，变成可验证的研究' in page.locator('h1').inner_text(), '需求研究V2成为主入口')
        page.locator('#example').click()
        check('当前浏览器草稿' in page.locator('#status').inner_text(), '草稿使用生产中性口径')
        page.locator('[data-action="next"]').click()
        check(page.locator('#project-options button').count() > 0, '真实项目目录加载')
        check(page.locator('#method-options button').count() > 0, '真实方法目录加载')
        page.locator('#live-demo-start').click()
        check(page.locator('#live-demo').is_visible(), '动态研究案例可打开')
        page.locator('#live-pause').click()
        page.locator('#live-close').click()

        response = page.goto(BASE + '/inno/museum/', wait_until='networkidle')
        check(response.status == 200, '好设计馆200')
        check(page.locator('img').count() > 0, '展馆图片存在')
        check(page.locator('img').evaluate_all('(imgs) => imgs.every(img => img.complete && img.naturalWidth > 0)'), '展馆全部图片成功解码')
        check(page.locator('.gd-nav').count() == 1, '展馆仅一个统一导航')
        page.screenshot(path=str(SCREEN / 'museum-desktop.png'))
        page.locator('a[href="categories.html#industry"]').click()
        page.wait_for_load_state('networkidle')
        check(page.url.startswith(BASE + '/inno/legacy/categories.html'), '展区链接留在主项目区')
        check(page.locator('.gd-nav').count() == 1, '旧展区统一导航')

        response = page.goto(BASE + '/inno/methods/methods/R50.html', wait_until='networkidle')
        check(response.status == 200, 'R50方法页200')
        check(page.locator('.gd-nav').count() == 1 and page.locator('.gd-footer').count() == 1, '方法页统一顶底栏')
        check('GoodDesign · OpenDesign 创新项目区' in page.locator('body').inner_text(), '方法页生产说明更新')

        response = page.goto(BASE + '/inno/report/', wait_until='networkidle')
        check(response.status == 200, '数据总览200')
        check(page.locator('svg').count() > 0, '数据总览以真实图表呈现')

        response = page.goto(BASE + '/inno/mcp/', wait_until='networkidle')
        check(response.status == 200, 'MCP新版页面200')
        check(page.locator('.mcp-tool').count() == 8, 'MCP八项工具完整')
        page.locator('[data-tool-filter="discovery"]').click()
        check(page.locator('.mcp-tool:visible').count() == 3, 'MCP发现工具筛选')
        check(page.locator('#mcp-config').inner_text().find('<YOUR_PRIVATE_MCP_KEY>') >= 0, 'MCP密钥只用占位符')
        page.screenshot(path=str(SCREEN / 'mcp-desktop.png'))

        response = page.goto(BASE + '/inno/about/', wait_until='networkidle')
        check(response.status == 200, '使用说明200')
        about = page.locator('body').inner_text()
        check('当前公开主项目区为opendesign.cc/inno/' in about, '主项目区说明更新')
        check('gooddesign.qiuyiwu.com/industry-demo/' not in about, '旧企业外链移除')
        check('需求研究' in about and 'MCP 接入' in about, '新栏目说明完整')

        response = page.goto(BASE + '/inno/dossier/?project=2019-s19', wait_until='networkidle')
        check(response.status == 200, '079生产档案200')
        check('6000HP' in page.locator('body').inner_text(), '079项目内容正确')
        check(page.locator('.gd-nav').count() == 1 and page.locator('.gd-footer').count() == 1, '动态档案统一顶底栏')

        response = page.goto(BASE + '/inno/learn/', wait_until='networkidle')
        check(response.status == 200, '科技教育200')
        check(page.locator('.gd-nav').count() == 1, '科技教育统一导航')

        response = page.goto(BASE + '/inno/loop/', wait_until='networkidle')
        check(response.status == 200, '授权企业工作台200')
        check(page.locator('h1').inner_text() == '企业创新工作台', '企业工作台产品定义')
        check(page.locator('#task-select option').count() == 3, '三个真实研究任务')
        check('授权内部试运行' in page.locator('body').inner_text(), '企业页生产口径')
        for view in ('requirement', 'routes', 'validation', 'feedback', 'overview'):
            page.locator(f'.ew-nav [data-view="{view}"]').click()
            check(page.locator('#workspace-view').inner_text().strip() != '', f'企业视图{view}可用')
        page.screenshot(path=str(SCREEN / 'loop-desktop.png'))

        for width, route in ((768, '/inno/'), (390, '/inno/'), (390, '/inno/needs/'), (390, '/inno/museum/'), (390, '/inno/mcp/')):
            page.set_viewport_size({'width': width, 'height': 900})
            response = page.goto(BASE + route, wait_until='networkidle')
            check(response.status == 200, f'{width}px {route}可访问')
            check(page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'{width}px {route}无横向溢出')
            if width == 390 and route == '/inno/':
                page.screenshot(path=str(SCREEN / 'home-mobile.png'))

        check(not errors, '线上无浏览器脚本异常：' + repr(errors))
        check(not failed, '线上无资源请求失败：' + repr(failed))
        check(not bad_responses, '线上无HTTP错误资源：' + repr(bad_responses))
        browser.close()
finally:
    remote('sudo -n sh -c "cp /var/lib/innovation-design/release-backups/20261104-093e/inno.htpasswd-qa093 /etc/nginx/inno.htpasswd && rm -f /var/lib/innovation-design/release-backups/20261104-093e/inno.htpasswd-qa093"')

report = {'check_count': len(checks), 'checks': checks, 'errors': errors, 'failed_resources': failed, 'bad_responses': bad_responses, 'temporary_auth_removed': True}
(OUT / 'browser-production.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'check_count': len(checks), 'errors': errors, 'failed_resources': failed, 'bad_responses': bad_responses}, ensure_ascii=False))
