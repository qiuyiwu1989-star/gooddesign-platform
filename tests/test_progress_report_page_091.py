import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/reports/项目进展汇报-2026-11-04.html'
DATA = ROOT / 'output/reports/项目进展数据-2026-11-04.json'


class ProgressReportPage091Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = OUT.read_text(encoding='utf-8')
        cls.data = json.loads(DATA.read_text())

    def test_091_page_matches_structured_report(self):
        research = self.data['research']
        for text in (f'<strong>{research["native_projects"]}</strong>', f'{research["full_sources"]} / {research["patents_sources"]}', str(self.data['product']['built_html_pages']), f'{research["evidence_issues"]}项异常'):
            self.assertIn(text, self.html)
        self.assertIn(f'{research["full_batch_status"]["needs_correction"]}批', self.html)
        self.assertIn(f'{research["patents_batch_status"]["needs_correction"]}批', self.html)
        self.assertIn('18.4%', self.html)

    def test_091_report_contains_all_presentation_sections(self):
        for section in ('管理层摘要', '项目当前架构', '产品与设计系统更新', '数据资产进展', '全量深研分层队列', '质量现状与必须正视的问题', '下一阶段计划', '可复核入口'):
            self.assertIn(section, self.html)

    def test_091_shared_chrome_and_report_boundaries(self):
        self.assertEqual(self.html.count('data-gd-chrome="navigation"'), 1)
        self.assertEqual(self.html.count('data-gd-chrome="footer"'), 1)
        self.assertIn('<strong>好设计</strong><small>GoodDesign</small>', self.html)
        self.assertIn('0次模型调用的脚本演示', self.html)
        self.assertIn('没有生产部署', self.html)
        self.assertIn('未公开推荐书或会议内容', self.html)

    def test_091_responsive_and_print_rules(self):
        for query in ('@media(max-width:900px)', '@media(max-width:560px)', '@media print'):
            self.assertIn(query, self.html)
        self.assertIn("addEventListener('click',()=>window.print())", self.html)
        self.assertIn('#report-print{display:none!important}', self.html)

    def test_091_evidence_routes_are_allowlisted(self):
        server = (ROOT / 'scripts/preview_progress_report_091.py').read_text()
        for route in ('/research-088/audit-summary.json', '/research-088/queues.json', '/research-089/material-inventory.csv', '/research-079/2019-s19/publish-result.json', '/reports/项目进展数据-2026-11-04.json'):
            self.assertIn(route, server)
        self.assertIn("127.0.0.1", server)
        self.assertIn("localhost", server)


if __name__ == '__main__':
    unittest.main()
