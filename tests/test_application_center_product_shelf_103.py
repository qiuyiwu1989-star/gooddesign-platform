import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ApplicationCenterProductShelf103Tests(unittest.TestCase):
    def test_103_generator_defines_product_shelf_groups_search_and_tones(self):
        text = (ROOT / 'scripts/app_center_096.py').read_text()
        for marker in (
            'KINDS', "'museum': 'experience'", 'app-search-input',
            'data-tone=museum', 'data-tone=education', 'data-tone=needs',
            'data-tone=enterprise', 'data-tone=canvas', 'data-tone=mcp', 'data-tone=regional',
            'app-card-value', 'app-card-foot', 'app-detail-hero',
            'activeKind', 'applyFilters',
        ):
            self.assertIn(marker, text)

    def test_103_built_cards_are_product_like_and_keep_real_contracts(self):
        text = (ROOT / 'output/inno-preview/gooddesign-site/inno/apps/index.html').read_text()
        for marker in (
            '全部应用', '内容学习', '创新研究', '接入扩展',
            '搜索应用', '点卡片看价值、开发者与案例',
            'app-card-value', 'app-card-foot', 'app-detail-hero',
            'app-store', 'app-detail-title', 'app-case-title',
            'app-data', 'selectApp',
        ):
            self.assertIn(marker, text)
        data_text = text.split('id="app-data">', 1)[1].split('</script>', 1)[0]
        data = json.loads(data_text)
        self.assertEqual(len(data['apps']), 7)
        self.assertEqual(len(data['cases']), 5)
        self.assertEqual(data['case_map']['education'], 'chang-e')
        self.assertEqual(data['case_map']['regional'], 'yuhuan')

    def test_103_combined_filtering_and_mobile_detail_focus_are_defined(self):
        text = (ROOT / 'scripts/app_center_096.py').read_text()
        self.assertIn("activeKind==='all'||card.dataset.kind===activeKind", text)
        self.assertIn('haystack.includes(query)', text)
        self.assertIn('sheet.showModal', text)
        self.assertIn('repeat(auto-fill,minmax(246px,1fr))', text)


if __name__ == '__main__':
    unittest.main()
