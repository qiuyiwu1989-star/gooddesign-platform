# coding: utf-8
"""156 数据价值与研究质量双视图契约。"""
import collections
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import data_report_page


class DataReport156Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / 'extensions/project-portal/data-report.json').read_text())
        cls.catalog = json.loads((ROOT / 'extensions/project-portal/catalog.json').read_text())
        cls.html = data_report_page.page()
        cls.script = (ROOT / 'extensions/project-portal/data-report.js').read_text()

    def test_value_and_quality_views_have_distinct_scopes(self):
        self.assertIn('data-view="value"', self.html)
        self.assertIn('data-view="quality"', self.html)
        self.assertIn('全库构建时统计', self.html)
        self.assertIn('以下字段、来源、补证和评分只统计 98 个金奖专项', self.html)
        self.assertIn('看见设计知识', self.html)
        self.assertNotIn('看见数据如何变成设计知识', self.html)

    def test_current_overall_counts_and_refreshed_gold_snapshot(self):
        summary = self.data['summary']
        for value in (560, 103, 64, 12):
            self.assertIn(f'<strong>{value}</strong>', self.html)
        for key in ('project_source_entries', 'known_cells', 'fact_records', 'deepening_reports'):
            self.assertIn(f'{summary[key]:,}', self.html)
        self.assertGreater(self.data['generated_at'], '2026-10-27')
        self.assertEqual(summary['deepening_reports'], 24)

    def test_research_depth_buckets_reconcile_to_98(self):
        counts = collections.Counter()
        for row in self.data['projects']:
            value = row['known_cells']
            label = '1—9 个已知字段' if value < 10 else '10—19 个已知字段' if value < 20 else '20—49 个已知字段' if value < 50 else '50 个以上已知字段'
            counts[label] += 1
        self.assertEqual(sum(counts.values()), 98)
        for label, count in counts.items():
            self.assertIn(label, self.html)
            self.assertIn(f'<b>{count}<small>案</small></b>', self.html)

    def test_showcase_benchmarks_and_applications_are_real(self):
        self.assertEqual(self.html.count('class="dr-showcase-card"'), 20)
        self.assertEqual(self.html.count('class="dr-benchmark-card"'), 3)
        for pid in ('2025-00', '2015-02', '2017-01'):
            self.assertIn(f'/dossier/?project={pid}', self.html)
        for route in ('/expo/', '/loop/', '/museum/', '/museum/#education'):
            self.assertIn(f'href="{route}"', self.html)

    def test_view_url_asset_filter_and_existing_interactions(self):
        for marker in ('function setView', 'function renderAssetFilters', "searchParams.set('view', 'quality')", "updateAssetFilter('award'", "updateAssetFilter('year'", 'asset-explore'):
            self.assertIn(marker, self.script)
        for marker in ('data-quality-filter', 'row.dataset.quality === quality', "event.key !== 'Enter'", 'window.print()'):
            self.assertIn(marker, self.script)

    def test_professional_data_and_unknowns_remain(self):
        self.assertEqual(self.html.count('class="dr-evidence-link"'), 98)
        self.assertEqual(self.html.count('data-quality="'), 98)
        self.assertIn('未评或待复评', self.html)
        self.assertIn('未评不算0分', self.html)
        self.assertIn('不是项目技术价值', self.html)


if __name__ == '__main__':
    unittest.main()
