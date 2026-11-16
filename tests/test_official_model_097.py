import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/inno-preview/gooddesign-site'
sys.path.insert(0, str(ROOT / 'scripts'))
import info_pages_095
import model_official_097


class OfficialModel097Tests(unittest.TestCase):
    def test_097_official_definition_and_architecture(self):
        page = model_official_097.page()
        for text in ('GoodDesign 官方介绍', '领域智能系统', '项目档案数据库', '设计创新引擎', '应用能力', '证据可信环', '验证生长环', '四种核心能力', '尚不宣称与能力边界'):
            self.assertIn(text, page)
        self.assertEqual(page.count('data-model-layer='), 3)
        self.assertEqual(page.count('data-capability='), 4)
        self.assertIn('45', page)
        self.assertIn('180', page)
        self.assertIn('42', page)
        self.assertNotIn('—', page)
        self.assertNotIn('–', page)

    def test_097_model_uses_shared_chrome_and_main_target(self):
        page = info_pages_095.model()
        self.assertEqual(page.count('data-gd-chrome="navigation"'), 1)
        self.assertEqual(page.count('data-gd-chrome="footer"'), 1)
        self.assertIn('<main class="pp-page" id="main">', page)
        self.assertIn('href="#main"', page)
        self.assertIn('/inno/portal/model-official.css', page)
        self.assertIn('/inno/portal/model-official.js', page)

    def test_097_all_static_pages_have_one_chrome_and_valid_main(self):
        for page in OUT.rglob('*.html'):
            text = page.read_text(encoding='utf-8')
            self.assertEqual(text.count('data-gd-chrome="navigation"'), 1, str(page))
            self.assertEqual(text.count('data-gd-chrome="footer"'), 1, str(page))
            self.assertIn('id="main"', text, str(page))

    def test_097_dynamic_dossier_has_main_target(self):
        import project_pipeline
        import workspace_ui
        page = workspace_ui.dossier('2019-s19', project_pipeline.LIB)
        self.assertIn('<main id="main">', page)
        self.assertEqual(page.count('id="main"'), 1)
        self.assertIn('href="#main"', page)

    def test_097_shared_chrome_reset_and_assets_are_published(self):
        css = (OUT / 'inno/portal/gooddesign.css').read_text(encoding='utf-8')
        self.assertIn('body > header.gd-nav{display:block;width:100%;max-width:none;height:auto', css)
        self.assertIn('body > footer.gd-footer{display:flex;width:min(100%,var(--gd-page))', css)
        for name in ('model-official.css', 'model-official.js'):
            self.assertTrue((OUT / 'inno/portal' / name).is_file(), name)
        script = (OUT / 'inno/portal/model-official.js').read_text(encoding='utf-8')
        self.assertIn('IntersectionObserver', script)
        self.assertIn('prefers-reduced-motion', script)


if __name__ == '__main__':
    unittest.main()
