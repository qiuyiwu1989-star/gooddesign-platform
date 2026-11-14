import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import info_pages_095
import innovation_auth
import project_pipeline as pp
import workspace_ui


class UnifiedRelease095Tests(unittest.TestCase):
    def test_095_about_model_and_guide_use_real_boundaries(self):
        for page in (info_pages_095.about(), info_pages_095.model(), info_pages_095.guide()):
            self.assertIn('/apps/', page)
            self.assertIn('data-gd-chrome="navigation"', page)
        model = info_pages_095.model()
        self.assertIn('四种核心能力', model)
        self.assertIn('尚不宣称', model)
        self.assertIn('自主训练基础大模型', model)
        self.assertIn('项目档案数据库', model)

    def test_095_application_manifest_and_cases_are_real(self):
        self.assertEqual(len(info_pages_095.APPS), 7)
        self.assertEqual(len(info_pages_095.CASES), 5)
        page = info_pages_095.apps()
        self.assertIn('data-app-kind="innovation"', page)
        self.assertIn('/cases/chang-e/', page)
        self.assertIn('规划建设', page)
        pump = info_pages_095.case('pump-079')
        self.assertIn('45条记录', pump)
        self.assertIn('180个有值事实字段', pump)
        self.assertIn('质量未评、未专家审核', pump)
        with self.assertRaises(StopIteration):
            info_pages_095.case('not-found')

    def test_095_navigation_has_application_center_and_about(self):
        home = (ROOT / 'output/inno-preview/gooddesign-site/inno/index.html').read_text()
        self.assertIn('data-gd-nav="apps"', home)
        self.assertIn('data-gd-nav="about"', home)
        self.assertIn('/model/', home)
        self.assertIn('/museum/#education', home)

    def test_095_canonical_routes_and_permissions(self):
        config = (ROOT / 'deploy/nginx-haoshejiguan.com.conf').read_text()
        for route in ('^/inno/needs-v2/(.*)$ /needs/ permanent', '^/inno/projects/(.*)$ /projects/ permanent', '^/inno/learn/(.*)$ /museum/ permanent'):
            self.assertIn(route, config)
        root_conf = (ROOT / 'deploy/nginx-inno-root.conf').read_text()
        self.assertIn('auth_request /auth/check;', root_conf)
        self.assertIn('auth_request /inno/auth/check;', (ROOT / 'deploy/nginx-inno-readonly.conf').read_text())
        self.assertIn('error_page 401 = @root_login;', root_conf)
        readonly = (ROOT / 'deploy/nginx-inno-readonly.conf').read_text()
        self.assertIn('location = /inno/mcp/api', readonly)
        self.assertIn('location ^~ /cases/', root_conf)

    def test_095_citation_preview_has_no_inline_details(self):
        html = workspace_ui.dossier('2019-s19', pp.LIB)
        self.assertIn('class="citation-trigger"', html)
        self.assertIn('id="citation-dialog"', html)
        self.assertIn('class="citation-print"', html)
        self.assertNotIn('<summary>查看出处与原文</summary>', html)
        self.assertIn('openCitation(button)', html)
        self.assertIn('activeCitation.focus()', html)

    def test_095_auth_token_and_next_are_safe(self):
        self.assertEqual(innovation_auth.safe_next('https://evil.example'), '/loop/')
        self.assertEqual(innovation_auth.safe_next('/inno/loop/?task=gear-v1'), '/inno/loop/?task=gear-v1')
        with tempfile.TemporaryDirectory() as temp:
            innovation_auth.KEY_FILE = Path(temp) / 'session.key'
            token = innovation_auth.issue('qa095')
            self.assertEqual(innovation_auth.verify(token), 'qa095')
            self.assertIsNone(innovation_auth.verify(token + 'bad'))

    def test_095_password_verification_uses_existing_hash_format(self):
        with tempfile.TemporaryDirectory() as temp:
            users = Path(temp) / 'users.htpasswd'
            users.write_text('qa095:$apr1$test$I.rgpcfsqhhkbiBqn4mzl0\n')
            innovation_auth.USERS_FILE = users
            self.assertTrue(innovation_auth.check_password('qa095', 'test-only'))
            self.assertFalse(innovation_auth.check_password('qa095', 'wrong'))
            self.assertFalse(innovation_auth.check_password('unknown', 'test-only'))

    def test_095_real_login_and_session_http(self):
        with tempfile.TemporaryDirectory() as temp:
            users = Path(temp) / 'users.htpasswd'
            users.write_text('qa095:$apr1$test$I.rgpcfsqhhkbiBqn4mzl0\n')
            env = dict(os.environ, GOODDESIGN_AUTH_USERS_FILE=str(users), GOODDESIGN_AUTH_KEY_FILE=str(Path(temp) / 'session.key'))
            process = subprocess.Popen([sys.executable, str(ROOT / 'scripts/innovation_auth.py'), '--port', '18786'], cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            try:
                time.sleep(.4)
                request = urllib.request.Request('http://127.0.0.1:18786/login/', data=b'username=qa095&password=wrong&next=%2Finno%2Floop%2F', headers={'Host': '127.0.0.1:18786', 'Origin': 'http://127.0.0.1:18786', 'Content-Type': 'application/x-www-form-urlencoded'})
                with urllib.request.urlopen(request, timeout=5) as wrong:
                    self.assertEqual(wrong.status, 200)
                    self.assertIn('账号或密码不正确', wrong.read().decode())
                class NoRedirect(urllib.request.HTTPRedirectHandler):
                    def redirect_request(self, req, fp, code, msg, headers, newurl):
                        return None
                request = urllib.request.Request('http://127.0.0.1:18786/login/', data=b'username=qa095&password=test-only&next=%2Finno%2Floop%2F', headers={'Host': '127.0.0.1:18786', 'Origin': 'http://127.0.0.1:18786', 'Content-Type': 'application/x-www-form-urlencoded'})
                with self.assertRaises(urllib.error.HTTPError) as success:
                    urllib.request.build_opener(NoRedirect).open(request, timeout=5)
                self.assertEqual(success.exception.code, 303)
                cookie = success.exception.headers['Set-Cookie'].split(';')[0]
                self.assertIn('gd_inno_session=', cookie)
                self.assertIn('Secure', success.exception.headers['Set-Cookie'])
                self.assertIn('HttpOnly', success.exception.headers['Set-Cookie'])
                request = urllib.request.Request('http://127.0.0.1:18786/auth/check', headers={'Host': '127.0.0.1:18786', 'Cookie': cookie})
                with urllib.request.urlopen(request, timeout=5) as response:
                    self.assertEqual(response.status, 200)
            finally:
                process.terminate()
                process.wait(timeout=5)


if __name__ == '__main__':
    unittest.main()
