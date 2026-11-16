import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/inno-preview/gooddesign-site'
sys.path.insert(0, str(ROOT / 'scripts'))
from gooddesign_chrome import navigation, footer


class BrandChinese084Tests(unittest.TestCase):
    def test_084_logo_is_original_chinese_mark(self):
        svg = (ROOT / 'extensions/design-system/brand-logo.svg').read_text(encoding='utf-8')
        self.assertIn('以中文“好”为主体', svg)
        self.assertIn('>好</text>', svg)
        self.assertIn('#5A4FE6', svg)
        self.assertIn('#F59A82', svg)
        self.assertIn('aria-labelledby="title desc"', svg)
        self.assertNotIn('a13 13', svg)
        self.assertNotIn('http', svg.replace('http://www.w3.org/2000/svg', ''))

    def test_084_shared_wordmark_is_chinese_first(self):
        for html in (navigation(), footer()):
            self.assertIn('<strong>好设计</strong><small>GoodDesign</small>', html)
            self.assertIn('brand-logo.svg?v=084', html)
        self.assertIn('aria-label="好设计 GoodDesign 首页"', navigation())

    def test_084_built_pages_use_new_brand(self):
        pages = list(OUT.rglob('*.html'))
        self.assertGreater(len(pages), 1200)
        for page in pages:
            text = page.read_text(encoding='utf-8')
            nav = re.search(r'<header class="gd-nav".*?</header>', text, re.S).group(0)
            foot = re.search(r'<footer class="gd-shell gd-footer".*?</footer>', text, re.S).group(0)
            for chrome in (nav, foot):
                self.assertIn('<strong>好设计</strong><small>GoodDesign</small>', chrome, str(page))
                self.assertIn('brand-logo.svg?v=084', chrome, str(page))
                self.assertNotIn('<strong>GoodDesign</strong><small>好设计</small>', chrome, str(page))

    def test_084_wordmark_type_scale(self):
        css = (ROOT / 'extensions/design-system/gooddesign.css').read_text(encoding='utf-8')
        self.assertIn('.gd-brand-text strong { font-size: 20px;', css)
        self.assertIn('font: 500 10px/1 var(--font-latin)', css)

    def test_084_standalone_portal_uses_versioned_logo(self):
        html = (ROOT / 'extensions/design-system/portal.html').read_text(encoding='utf-8')
        self.assertIn('src="brand-logo.svg?v=084"', html)
        self.assertIn('aria-label="好设计 GoodDesign 首页"', html)


if __name__ == '__main__':
    unittest.main()
