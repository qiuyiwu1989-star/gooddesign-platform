import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/inno-preview/gooddesign-site'


class GoodDesignChrome072Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = sorted(path for path in OUT.rglob('*.html') if path.name != 'site-index.html')

    def test_072_one_standard_navigation_and_footer_per_page(self):
        for path in self.pages:
            text = path.read_text()
            self.assertEqual(text.count('data-gd-chrome="navigation"'), 1, str(path))
            self.assertEqual(text.count('data-gd-chrome="footer"'), 1, str(path))
            self.assertIn('GoodDesign', text, str(path))
            self.assertIn('/inno/portal/brand-logo.svg', text, str(path))
            self.assertIn('/inno/portal/ip-xiaohao.svg', text, str(path))
            self.assertEqual(text.count('/inno/portal/chrome.js'), 1, str(path))
            self.assertNotRegex(text, r'class="(?:pp-nav|workspace-header|inno-nav)"')

    def test_072_no_hyperlink_arrow_suffixes(self):
        for path in self.pages:
            text = path.read_text()
            for arrow in ('↗', '↘', '→', '←', '↔', '⇄', '↑', '↓'):
                self.assertNotIn(arrow, text, str(path))

    def test_072_normalized_chrome_is_shared(self):
        def normalized(path):
            text = path.read_text()
            nav = re.search(r'<header class="gd-nav".*?</header>', text, re.S).group(0)
            nav = re.sub(r'\s*aria-current="page"', '', nav)
            return re.sub(r'<span id="feedback".*?</span>|<button id="print".*?</button>', '', nav, flags=re.S)
        gold = normalized(self.pages[0])
        for path in self.pages:
            self.assertEqual(normalized(path), gold, str(path))

    def test_072_review_index_uses_shared_chrome(self):
        text = (OUT / 'site-index.html').read_text()
        self.assertEqual(text.count('data-gd-chrome="navigation"'), 1)
        self.assertEqual(text.count('data-gd-chrome="footer"'), 1)
        self.assertIn('/inno/portal/brand-logo.svg', text)
        for arrow in ('↗', '↘', '→', '←', '↔', '⇄', '↑', '↓'):
            self.assertNotIn(arrow, text)

    def test_072_brand_and_assistant_assets(self):
        for name in ('brand-logo.svg', 'ip-xiaohao.svg', 'chrome.js'):
            self.assertTrue((OUT / 'inno/portal' / name).is_file(), name)
        for name in ('brand-logo.svg', 'ip-xiaohao.svg'):
            text = (OUT / 'inno/portal' / name).read_text()
            self.assertIn('<svg', text)
            self.assertIn('aria-labelledby', text)
        script = (OUT / 'inno/portal/chrome.js').read_text()
        self.assertIn('showModal', script)
        self.assertIn("addEventListener('close'", script)
        self.assertIn('localStorage', script)


if __name__ == '__main__':
    unittest.main()
