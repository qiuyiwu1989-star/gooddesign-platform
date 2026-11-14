import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ApplicationCenterInteractionContractsTests(unittest.TestCase):
    def test_application_center_keeps_core_detail_case_and_data_contracts(self):
        text = (ROOT / 'scripts/app_center_096.py').read_text()
        for marker in (
            'app-workbench', 'app-dock', 'app-detail-title', 'app-case-title',
            'app-output-chips', 'app-flow', 'app-roadmap', 'app-data', 'selectApp',
        ):
            self.assertIn(marker, text)

    def test_built_page_contains_real_apps_cases_and_status_planning(self):
        text = (ROOT / 'output/inno-preview/gooddesign-site/inno/apps/index.html').read_text()
        for marker in (
            '全部应用', '内容学习', '创新研究', '接入扩展', '适用人群',
            '当前任务', '应用状态', '交付物', '真实案例路径',
            '应用规划', '现在可用', '试点推进', '规划建设',
        ):
            self.assertIn(marker, text)
        data_text = text.split('id="app-data">', 1)[1].split('</script>', 1)[0]
        data = json.loads(data_text)
        self.assertEqual(len(data['apps']), 7)
        self.assertEqual(len(data['cases']), 5)

    def test_mobile_detail_focus_and_print_rules_are_defined(self):
        text = (ROOT / 'scripts/app_center_096.py').read_text()
        self.assertIn("window.matchMedia('(max-width: 1020px)')", text)
        self.assertIn('html:has(.app-workbench),body:has(.app-workbench){overflow-x:hidden}', text)
        self.assertIn('prefers-reduced-motion: reduce', text)
        self.assertIn('scroll-snap-type:x mandatory', text)
        self.assertIn('@media print', text)


if __name__ == '__main__':
    unittest.main()
