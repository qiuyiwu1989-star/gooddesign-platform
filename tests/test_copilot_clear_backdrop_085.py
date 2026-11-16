import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CopilotClearBackdrop085Tests(unittest.TestCase):
    def test_085_backdrop_is_transparent_and_unblurred(self):
        css = (ROOT / 'extensions/design-system/gooddesign.css').read_text(encoding='utf-8')
        self.assertIn('dialog.gd-assistant::backdrop{background:transparent;backdrop-filter:none;-webkit-backdrop-filter:none}', css)
        self.assertNotIn('dialog.gd-assistant::backdrop{background:rgba(7,7,15,.18);backdrop-filter:blur(2px)}', css)

    def test_085_built_asset_keeps_clear_backdrop(self):
        css = (ROOT / 'output/inno-preview/gooddesign-site/inno/portal/gooddesign.css').read_text(encoding='utf-8')
        self.assertIn('dialog.gd-assistant::backdrop{background:transparent;backdrop-filter:none;-webkit-backdrop-filter:none}', css)
        self.assertIn('dialog.showModal()', (ROOT / 'extensions/design-system/chrome.js').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
