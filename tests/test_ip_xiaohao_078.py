import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from gooddesign_chrome import navigation


class XiaohaoIp078Tests(unittest.TestCase):
    def test_078_character_family_is_original_and_accessible(self):
        for name in ('ip-xiaohao.svg', 'ip-xiaohao-method.svg', 'ip-xiaohao-evidence.svg'):
            text = (ROOT / 'extensions/design-system' / name).read_text()
            self.assertIn('aria-labelledby="title desc"', text)
            self.assertIn('#86C5A5', text)
            self.assertIn('#F59A82', text)
            self.assertIn('小好', text)
            self.assertNotIn('M40 5v8', text)

    def test_078_actions_match_assets_and_real_links(self):
        html = navigation(project='2015-02')
        self.assertIn('GoodDesign AI Agent', html)
        self.assertIn('src="/inno/portal/ip-xiaohao.svg?v=078"', html)
        self.assertIn('src="/inno/portal/ip-xiaohao-method.svg"', html)
        self.assertIn('src="/inno/portal/ip-xiaohao-evidence.svg"', html)
        self.assertIn('href="/methods/"', html)
        self.assertIn('href="/dossier/?project=2015-02"', html)
        self.assertIn('研究搭子', html)
        self.assertIn('这里不调用模型，也不会修改你的资料。', html)

    def test_078_assets_in_static_and_dynamic_builders(self):
        assets = (ROOT / 'scripts/gooddesign_assets.py').read_text()
        builder = (ROOT / 'scripts/build_gooddesign_site.py').read_text()
        for name in ('ip-xiaohao-method.svg', 'ip-xiaohao-evidence.svg'):
            self.assertIn(name, assets)
            self.assertIn(name, builder)
            self.assertTrue((ROOT / 'output/inno-preview/gooddesign-site/inno/portal' / name).is_file(), name)

    def test_078_dynamic_dossier_loads_shared_component_styles(self):
        source = (ROOT / 'scripts/workspace_ui.py').read_text()
        self.assertIn('from gooddesign_assets import links as gooddesign_links', source)
        self.assertIn("if 'gooddesign.css' not in text", source)
        self.assertIn("gooddesign_links()+'<style>'+CSS", source)

    def test_078_existing_dialog_interactions_remain(self):
        script = (ROOT / 'extensions/design-system/chrome.js').read_text()
        self.assertIn('showModal', script)
        self.assertIn("addEventListener('close'", script)
        self.assertIn('open.focus()', script)
        css = (ROOT / 'extensions/design-system/gooddesign.css').read_text()
        self.assertIn('.gd-assistant-action', css)
        self.assertIn('@media (max-width: 767px)', css)
        self.assertIn('prefers-reduced-motion:no-preference', css)


if __name__ == '__main__':
    unittest.main()
