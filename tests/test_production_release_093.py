import hashlib
import json
import tarfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/deploy-093'


class ProductionRelease093Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((OUT / 'release-manifest.json').read_text())
        cls.nginx = (ROOT / 'deploy/nginx-inno-readonly.conf').read_text()

    def test_093_manifest_and_package_fingerprints(self):
        self.assertEqual(self.manifest['research_project_count'], 103)
        self.assertIn('2019-s19', self.manifest['research_projects'])
        self.assertEqual(self.manifest['public_html_pages'], 1248)
        self.assertEqual(self.manifest['method_files'], 605)
        for name, record in self.manifest['packages'].items():
            path = OUT / name
            self.assertEqual(path.stat().st_size, record['bytes'])
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), record['sha256'])

    def test_093_research_snapshot_has_no_private_originals(self):
        with tarfile.open(OUT / 'research-snapshot.tar.gz') as archive:
            names = archive.getnames()
        self.assertTrue(names)
        self.assertFalse(any(name.lower().endswith(('.pdf', '.docx', '.zip', '.png', '.jpg', '.jpeg')) for name in names))
        with tarfile.open(OUT / 'runtime-overlay.tar.gz') as archive:
            members = archive.getmembers()
        self.assertFalse(any(member.issym() or member.islnk() or 'private-sources' in member.name for member in members))
        for name in names:
            self.assertTrue('/研究工作区/' in name or '/数据/' in name or name.endswith('/chunks.json') or name.endswith('/metadata.json') or name.endswith('/资料归属.json') or name in self.manifest['experience_source_originals'] or name in {'项目索引.json', '2025-04/01-项目档案.md'}, name)

    def test_093_public_copy_uses_production_language(self):
        public = OUT / 'public-site'
        about = (public / 'inno/about/index.html').read_text()
        self.assertIn('把真实创新经验，建设成可复用的公共能力', about)
        self.assertIn('/inno/model/', about)
        self.assertNotIn('gooddesign.qiuyiwu.com/industry-demo/', about)
        self.assertIn('GoodDesign · OpenDesign 创新项目区', (public / 'inno/index.html').read_text())
        needs = (public / 'inno/needs-v2/needs-workspace.js').read_text()
        self.assertIn('当前浏览器草稿', needs)
        self.assertIn('网络连接或目录服务', needs)
        self.assertNotIn('本地设计迁移预览', (public / 'inno/methods/index.html').read_text())

    def test_093_legacy_assets_resolve_inside_inno(self):
        public = OUT / 'public-site'
        self.assertIn('<base href="/inno/legacy/">', (public / 'inno/museum/index.html').read_text())
        self.assertIn('<base href="/inno/legacy/">', (public / 'learn.html').read_text())
        self.assertIn('href="categories.html#industry"', (public / 'inno/museum/index.html').read_text())

    def test_093_nginx_preserves_public_and_private_boundaries(self):
        for route in ('/inno/needs-v2/', '/inno/museum/', '/inno/legacy/', '/inno/portal/'):
            self.assertIn(f'location ^~ {route}', self.nginx)
        needs = (ROOT / 'deploy/nginx-needs-research.conf').read_text()
        self.assertIn('try_files /inno/needs-v2/index.html =404;', needs)
        loop = self.nginx.split('location ^~ /inno/loop/', 1)[1].split('location ^~ /inno/ {', 1)[0]
        self.assertIn('auth_request /inno/auth/check;', loop)
        self.assertIn('proxy_pass http://127.0.0.1:18784/;', loop)
        self.assertIn('location = /inno/mcp/api', self.nginx)
        self.assertIn('proxy_pass http://127.0.0.1:18779/mcp;', self.nginx)

    def test_093_loop_has_independent_storage_and_allowed_origin(self):
        store = (ROOT / 'scripts/innovation_loop_store.py').read_text()
        server = (ROOT / 'scripts/innovation_loop_server.py').read_text()
        service = (ROOT / 'deploy/innovation-loop.service').read_text()
        self.assertIn("os.environ.get('GOODDESIGN_LOOP_DB'", store)
        self.assertIn("'https://opendesign.cc'", server)
        self.assertIn('/inno/loop/workspace/enterprise-workbench.css', server)
        self.assertIn('Environment=GOODDESIGN_LOOP_DB=/var/lib/innovation-loop/loop.sqlite3', service)
        self.assertIn('ReadWritePaths=/var/lib/innovation-loop', service)


if __name__ == '__main__':
    unittest.main()
