import base64
import json
import secrets
import string
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/design-095'
OUT.mkdir(parents=True, exist_ok=True)
USER = 'qa095' + secrets.token_hex(4)
PASSWORD = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(24))
BASE = 'https://opendesign.cc'
checks = []


def check(condition, label):
    if not condition:
        raise AssertionError(label)
    checks.append(label)


def remote(command, **kwargs):
    return subprocess.run(['ssh', '-o', 'BatchMode=yes', 'yongle-nanjing', command], check=True, **kwargs)


remote('sudo -n cp /etc/nginx/inno.htpasswd /var/lib/innovation-design/release-backups/20261104-095/inno.htpasswd-auth-qa095')
try:
    hashed = remote('openssl passwd -6 -stdin', input=PASSWORD + '\n', text=True, capture_output=True).stdout.strip()
    encoded = base64.b64encode(f'\n{USER}:{hashed}\n'.encode()).decode()
    remote(f'sudo -n python3 -c "import base64;open(\'/etc/nginx/inno.htpasswd\',\'ab\').write(base64.b64decode(\'{encoded}\'))"')
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1440, 'height': 1000})
        response = page.goto(BASE + '/inno/loop/', wait_until='networkidle')
        check(response.status in (200, 302), '未登录进入统一登录页')
        check('/inno/login/' in page.url, '未登录跳转登录地址')
        check('登录后继续研究' in page.locator('h1').inner_text(), '统一登录页内容')
        check(page.locator('#username').count() == 1 and page.locator('#password').count() == 1, '登录表单完整')
        page.screenshot(path=str(OUT / 'login-desktop.png'))

        page.locator('#username').fill(USER)
        page.locator('#password').fill('wrong-password')
        page.locator('button[type="submit"]').click()
        page.wait_for_load_state('networkidle')
        check('账号或密码不正确' in page.locator('body').inner_text(), '错误密码有明确反馈')

        page.locator('#username').fill(USER)
        page.locator('#password').fill(PASSWORD)
        page.locator('button[type="submit"]').click()
        page.wait_for_load_state('networkidle')
        check(page.url.startswith(BASE + '/inno/loop/'), '正确登录返回企业工作台')
        check(page.locator('h1').inner_text() == '企业创新工作台', '授权后企业页面可用')
        check(page.locator('#task-select option').count() == 3, '授权后真实任务可读取')

        response = page.request.get(BASE + '/inno/logout/', max_redirects=0)
        check(response.status == 303, '退出登录返回303')
        browser.close()
finally:
    remote('sudo -n sh -c "cp /var/lib/innovation-design/release-backups/20261104-095/inno.htpasswd-auth-qa095 /etc/nginx/inno.htpasswd && rm -f /var/lib/innovation-design/release-backups/20261104-095/inno.htpasswd-auth-qa095"')

report = {'check_count': len(checks), 'checks': checks, 'temporary_auth_removed': True}
(OUT / 'auth-production.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False))
