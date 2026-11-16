import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class XiaohaoCopilot081Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.css = (ROOT / 'extensions/design-system/gooddesign.css').read_text(encoding='utf-8')
        cls.js = (ROOT / 'extensions/design-system/chrome.js').read_text(encoding='utf-8')

    def test_081_trigger_is_fixed_to_bottom_right(self):
        self.assertIn('.gd-ip-trigger{position:fixed;right:24px;bottom:max(24px,env(safe-area-inset-bottom))', self.css)
        self.assertIn('width:48px;min-height:48px', self.css)
        self.assertIn('right:16px;bottom:max(16px,env(safe-area-inset-bottom))', self.css)

    def test_081_panel_is_anchored_and_responsive(self):
        self.assertIn('dialog.gd-assistant{inset:auto 24px 96px auto', self.css)
        self.assertIn('width:min(420px,calc(100vw - 48px))', self.css)
        self.assertIn('dialog.gd-assistant { inset:auto 12px 84px', self.css)
        self.assertIn('max-height:calc(100dvh - 104px)', self.css)

    def test_081_accessibility_state_tracks_dialog(self):
        for hook in ("open.setAttribute('aria-haspopup', 'dialog')", "open.setAttribute('aria-controls', dialog.id)", "open.setAttribute('aria-expanded', 'false')", "open.setAttribute('aria-expanded', 'true')"):
            self.assertIn(hook, self.js)
        self.assertIn("dialog.addEventListener('close'", self.js)
        self.assertIn('open.focus()', self.js)
        self.assertIn('dialog.showModal()', self.js)

    def test_081_real_actions_and_no_fake_capability(self):
        self.assertNotIn('fetch(', self.js)
        self.assertNotIn('addEventListener(\'scroll\'', self.js)
        self.assertNotIn('addEventListener("scroll"', self.js)
        chrome = (ROOT / 'scripts/gooddesign_chrome.py').read_text(encoding='utf-8')
        self.assertIn('ip-xiaohao.svg?v=078', chrome)
        self.assertIn('</header>\n<button class="gd-ip-trigger"', chrome)

    def test_081_built_pages_have_one_trigger_and_one_panel(self):
        pages = list((ROOT / 'output/inno-preview/gooddesign-site').rglob('*.html'))
        self.assertGreater(len(pages), 1200)
        for page in pages:
            text = page.read_text(encoding='utf-8')
            self.assertEqual(text.count('data-gd-assistant-open'), 1, str(page))
            self.assertEqual(text.count('data-gd-assistant aria-labelledby'), 1, str(page))

    def test_081_print_and_reduced_transparency(self):
        self.assertIn('.gd-panel, .gd-nav, .gd-ip-trigger { background: var(--surface-content); backdrop-filter: none;', self.css)
        self.assertIn('.gd-skip, .gd-ip-trigger { display: none !important; }', self.css)


if __name__ == '__main__':
    unittest.main()
