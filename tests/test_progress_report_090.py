import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ProgressReport090Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / 'output/reports/项目进展数据-2026-11-04.json').read_text())
        cls.text = (ROOT / 'output/reports/项目进展汇报-2026-11-04.md').read_text()
        cls.audit = json.loads((ROOT / 'output/research-088/audit-summary.json').read_text())
        cls.inventory = json.loads((ROOT / 'output/research-089/summary.json').read_text())

    def test_090_report_uses_current_native_and_queue_data(self):
        self.assertEqual(self.data['research']['native_projects'], self.audit['native_research']['projects'])
        self.assertEqual(self.data['research']['queue_counts'], self.audit['queue_counts'])
        self.assertEqual(sum(self.data['research']['queue_counts'].values()), 560)
        self.assertIn('原生研究版 | 103', self.text)
        self.assertIn('A队列60项', self.text)
        self.assertIn('B队列397项', self.text)

    def test_090_batch_status_is_not_overclaimed(self):
        self.assertEqual(self.data['research']['full_batch_status'], self.audit['standard_batch_validation']['20261103-doubao-full-01'])
        self.assertEqual(self.data['research']['patents_batch_status'], self.audit['standard_batch_validation']['20261103-doubao-patents-01'])
        self.assertIn('越界路径和非标准文件角色', self.text)
        self.assertIn('不能宣称全库深研完成', self.text)

    def test_090_inventory_and_case_metrics_match(self):
        research = self.data['research']
        for key in ('full_sources', 'patents_sources', 'raw_source_files', 'image_files', 'material_bytes', 'image_bytes'):
            self.assertEqual(research[key], self.inventory['totals'][key])
        self.assertEqual(self.data['case_079']['records'], 45)
        self.assertEqual(self.data['case_079']['known_fact_cells'], 180)
        self.assertEqual(self.data['case_079']['ai_items'], 42)

    def test_090_report_keeps_research_and_release_boundaries(self):
        for text in ('0次模型调用的脚本演示', '生产站点尚未部署本轮更新', '专家审核和工程验证未完成', 'lead', '图片版权未知', '不直接全站覆盖'):
            self.assertIn(text, self.text)
        self.assertIn('旧人工底稿缺逐字段冻结证据对象', self.text)
        self.assertFalse(self.data['product']['production_changed'])

    def test_090_report_is_actionable_and_verifiable(self):
        self.assertGreaterEqual(self.data['verification']['full_regression_tests'], 591)
        for path in ('output/research-088/audit-summary.json', 'output/research-088/queues.json', 'output/research-089/material-inventory.csv', 'output/research-079/2019-s19/publish-result.json'):
            self.assertIn(path, self.text)
        for queue in ('A队列60项', 'B队列397项', 'C队列70项', 'D队列33项'):
            self.assertIn(queue, self.text)


if __name__ == '__main__':
    unittest.main()
