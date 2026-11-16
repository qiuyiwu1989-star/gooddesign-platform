import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ApplicationCenterConsole109Tests(unittest.TestCase):
    def test_109_generator_defines_three_column_console_and_wide_page(self):
        text = (ROOT / 'scripts/app_center_096.py').read_text()
        for marker in (
            'app-store', 'app-store-tabs', 'app-store-grid', 'app-detail',
            'repeat(3,minmax(0,1fr))',
            'max-width:1200px', 'app-sheet', 'showModal',
        ):
            self.assertIn(marker, text)

    def test_109_built_page_has_console_navigation_and_product_inspector(self):
        text = (ROOT / 'output/inno-preview/gooddesign-site/inno/apps/index.html').read_text()
        for marker in (
            'GoodDesign Applications', '应用中心',
            '全部应用', '内容学习', '创新研究', '接入扩展',
            '当前应用', '开发者', '查看完整案例',
        ):
            self.assertIn(marker, text)
        self.assertIn('data-tone="enterprise"', text)
        self.assertIn('data-tone="regional"', text)

    def test_109_responsive_console_rules_are_explicit(self):
        text = (ROOT / 'scripts/app_center_096.py').read_text()
        for query in ('@media(max-width:760px)', '@media(max-width:390px)'):
            self.assertIn(query, text)
        self.assertIn('max-height:88dvh', text)
        self.assertIn('@media print', text)


if __name__ == '__main__':
    unittest.main()
