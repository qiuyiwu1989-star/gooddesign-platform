import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/reports/项目进展汇报-2026-11-04.html'
DATA = ROOT / 'output/reports/项目进展数据-2026-11-04.json'


class KnowledgeAssets092Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = OUT.read_text(encoding='utf-8')
        cls.data = json.loads(DATA.read_text())
        match = re.search(r'<script type="application/json" id="asset-data">(.*?)</script>', cls.html, re.S)
        cls.assets = json.loads(match.group(1))

    def test_092_eight_cards_match_asset_taxonomy(self):
        self.assertEqual(self.html.count('class="asset-card"'), 8)
        self.assertEqual(len(self.assets), 8)
        for kind, count in (('archive', 2), ('sources', 4), ('application', 2)):
            self.assertEqual(sum(asset['kind'] == kind for asset in self.assets.values()), count)
        self.assertEqual(self.html.count('data-asset-filter='), 4)

    def test_092_values_come_from_structured_report(self):
        research = self.data['research']
        expected = {
            'directory': self.data['product']['index_projects'],
            'native': research['native_projects'],
            'full': research['full_sources'],
            'patents': research['patents_sources'],
            'raw': research['raw_source_files'],
            'images': research['image_files'],
            'methods': self.data['product']['method_count'],
            'case079': '000001',
        }
        self.assertEqual({key: asset['value'] for key, asset in self.assets.items()}, expected)
        self.assertEqual(self.assets['native']['meter'], 18.4)
        self.assertEqual(self.assets['case079']['case_metrics'], [['记录', 45], ['事实字段', 180], ['AI分析', 42]])

    def test_092_each_card_has_action_boundary_and_real_evidence(self):
        allowed = {
            '/research-088/audit-summary.json',
            '/research-088/queues.json',
            '/research-089/material-inventory.csv',
            '/research-079/2019-s19/publish-result.json',
            '/reports/项目进展数据-2026-11-04.json',
        }
        for asset in self.assets.values():
            self.assertTrue(asset['next'])
            self.assertTrue(asset['boundary'])
            self.assertIn(asset['evidence'], allowed)
        self.assertIn('未评分、未专家审核', self.assets['case079']['boundary'])
        self.assertIn('不代表项目已完成深研', self.assets['directory']['boundary'])

    def test_092_dialog_and_filters_are_accessible(self):
        self.assertIn('<dialog class="asset-detail" id="asset-detail"', self.html)
        self.assertIn('aria-labelledby="asset-detail-title"', self.html)
        self.assertIn('aria-describedby="asset-detail-summary"', self.html)
        self.assertEqual(self.html.count('aria-haspopup="dialog"'), 8)
        self.assertIn("dialog.addEventListener('close'", self.html)
        self.assertIn('activeCard.focus()', self.html)
        self.assertIn("button.setAttribute('aria-pressed'", self.html)
        self.assertIn('aria-live="polite"', self.html)

    def test_092_print_restores_filter_and_mobile_is_defined(self):
        self.assertIn("window.addEventListener('beforeprint'", self.html)
        self.assertIn("window.addEventListener('afterprint'", self.html)
        self.assertIn("applyFilter('all')", self.html)
        self.assertIn('applyFilter(printFilter)', self.html)
        self.assertIn('@media(max-width:560px)', self.html)
        self.assertIn('.asset-card[hidden]{display:none}', self.html)


if __name__ == '__main__':
    unittest.main()
