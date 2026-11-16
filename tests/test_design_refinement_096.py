import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DesignRefinement096Tests(unittest.TestCase):
    def test_096_model_uses_real_research_path(self):
        text = (ROOT / 'output/inno-preview/gooddesign-site/inno/index.html').read_text()
        for marker in ('model-explorer', 'data-model-step="evidence"', '45条记录，180个有值事实字段', 'R48、R14、R17', '42条带边界AI分析'):
            self.assertIn(marker, text)
        self.assertIn('真实研究数据，不是模型执行进度', text)

    def test_096_home_uses_model_explorer_not_three_cards(self):
        text = (ROOT / 'output/inno-preview/gooddesign-site/inno/index.html').read_text()
        self.assertIn('把项目证据，变成可执行的创新研究', text)
        self.assertIn('model-chain', text)
        self.assertNotIn('<h3>项目证据</h3>', text)
        self.assertNotIn('<h3>创新方法</h3>', text)
        self.assertNotIn('<h3>真实应用</h3>', text)

    def test_096_apps_use_task_detail_and_case_preview(self):
        text = (ROOT / 'output/inno-preview/gooddesign-site/inno/apps/index.html').read_text()
        self.assertIn('app-store', text)
        self.assertIn('app-detail-title', text)
        self.assertIn('app-case-title', text)
        self.assertIn('app-data', text)
        self.assertIn('selectApp', text)
        self.assertIn('选择合适的应用', text)

    def test_096_responsive_and_print_are_defined(self):
        text = (ROOT / 'scripts/model_explorer_096.py').read_text() + (ROOT / 'scripts/app_center_096.py').read_text()
        for query in ('@media(max-width:640px)', '@media(max-width:760px)', '@media print'):
            self.assertIn(query, text)


if __name__ == '__main__':
    unittest.main()
