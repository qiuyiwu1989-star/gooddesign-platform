import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/inno-preview/gooddesign-site'
sys.path.insert(0, str(ROOT / 'scripts'))
from build_gooddesign_site import navigation_target
from gooddesign_chrome import replace_chrome


class ChromeIsolation086Tests(unittest.TestCase):
    def test_086_legacy_nav_and_footer_are_replaced(self):
        source = '<html><body><nav><a class="brand">旧馆导航</a></nav><header class="page-hero"><h1>三大展区</h1></header><nav id="steps">功能步骤</nav><main>正文<footer class="gd-live-progress">研究进度</footer></main><footer>旧页脚</footer><script src="copilot.js" defer></script></body></html>'
        result = replace_chrome(source, 'museum')
        self.assertNotIn('旧馆导航', result)
        self.assertNotIn('旧页脚', result)
        self.assertNotIn('copilot.js', result)
        self.assertEqual(result.count('data-gd-chrome="navigation"'), 1)
        self.assertEqual(result.count('data-gd-chrome="footer"'), 1)
        self.assertIn('<header class="page-hero">', result)
        self.assertIn('<nav id="steps">功能步骤</nav>', result)
        self.assertIn('<footer class="gd-live-progress">研究进度</footer>', result)

    def test_086_museum_pages_have_correct_active_target(self):
        for name in ('categories.html', 'award.html', 'laureates.html', 'hall.html', 'index.html'):
            self.assertEqual(navigation_target(Path(name)), 'museum', name)
        self.assertEqual(navigation_target(Path('inno/museum/index.html')), 'museum')

    def test_086_categories_has_one_chrome_and_correct_active(self):
        text = (OUT / 'categories.html').read_text(encoding='utf-8')
        self.assertEqual(text.count('data-gd-chrome="navigation"'), 1)
        self.assertEqual(text.count('data-gd-chrome="footer"'), 1)
        self.assertIn('data-gd-nav="museum" aria-current="page"', text)
        self.assertNotIn('data-gd-nav="projects" aria-current="page"', text)
        self.assertNotIn('<nav>\n  <a class="brand"', text)
        self.assertNotIn('src="copilot.js"', text)

    def test_086_all_pages_have_one_shared_footer(self):
        for page in OUT.rglob('*.html'):
            text = page.read_text(encoding='utf-8')
            self.assertEqual(text.count('data-gd-chrome="footer"'), 1, str(page))

    def test_086_legacy_nav_style_is_reset_with_specificity(self):
        css = (OUT / 'inno/portal/gooddesign.css').read_text(encoding='utf-8')
        self.assertIn('.gd-links,.gd-footer-links{position:static;z-index:auto;height:auto;padding:0;border:0;background:transparent;backdrop-filter:none;-webkit-backdrop-filter:none}', css)
        self.assertNotIn(':where(.gd-links,.gd-footer-links){position:static', css)


if __name__ == '__main__':
    unittest.main()
