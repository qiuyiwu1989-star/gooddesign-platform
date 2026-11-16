import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from opendesign_readonly import single_chrome


class ChromeDedupe094Tests(unittest.TestCase):
    def test_duplicate_navigation_and_footer_are_removed(self):
        nav = '<header class="gd-nav" data-gd-chrome="navigation"><nav>项目库</nav></header>'
        footer = '<footer class="gd-shell gd-footer" data-gd-chrome="footer"><p>好设计</p></footer>'
        text = nav + nav + '<main>档案</main>' + footer + footer
        result = single_chrome(text)
        self.assertEqual(result.count('data-gd-chrome="navigation"'), 1)
        self.assertEqual(result.count('data-gd-chrome="footer"'), 1)
        self.assertIn('<main>档案</main>', result)

    def test_existing_single_chrome_is_unchanged(self):
        text = '<header data-gd-chrome="navigation">导航</header><main>正文</main><footer data-gd-chrome="footer">底部</footer>'
        self.assertEqual(single_chrome(text), text)


if __name__ == '__main__':
    unittest.main()
