import collections
import json
import sys
import unittest
from pathlib import Path
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import data_report_page


class DataReport075Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / 'extensions/project-portal/data-report.json').read_text())
        cls.catalog = json.loads((ROOT / 'extensions/project-portal/catalog.json').read_text())
        cls.html = data_report_page.page()

    def test_075_hero_metrics_match_snapshot(self):
        summary = self.data['summary']
        for key in ('catalog_entries', 'published_research', 'deepening_reports', 'project_source_entries', 'known_cells', 'fact_records', 'methods'):
            self.assertIn(f'{summary[key]:,}', self.html)

    def test_075_award_and_year_charts_match_catalog(self):
        awards = collections.Counter(row['award'] for row in self.catalog)
        years = collections.Counter(int(row['year']) for row in self.catalog)
        self.assertEqual(self.html.count('class="dr-donut-segment'), len(awards))
        self.assertEqual(self.html.count('class="dr-year-bar"'), len(years))
        self.assertIn(f'<strong>{len(years)}<small>个有数据年度</small>', self.html)
        for award, count in awards.items():
            self.assertIn(f'<span>{award}</span><b>{count}</b>', self.html)
            self.assertIn('/projects/?' + urlencode({'award': award}) + '#collection', self.html)
        for year in years:
            self.assertIn('/projects/?' + urlencode({'year': year}) + '#collection', self.html)

    def test_075_evidence_points_match_gold_projects(self):
        projects = self.data['projects']
        self.assertEqual(self.html.count('class="dr-evidence-link"'), len(projects))
        self.assertEqual(self.html.count('dr-evidence-point--deep'), sum(row['deepening'] for row in projects))
        for row in projects:
            self.assertIn(f'/dossier/?project={row["id"]}', self.html)
            self.assertIn(f'{row["source_entries"]}条来源，{row["known_cells"]}个已知值字段，{row["records"]}条结构化记录', self.html)

    def test_075_quality_and_scores_preserve_unknowns(self):
        projects = self.data['projects']
        self.assertEqual(self.html.count('data-quality="'), len(projects))
        for status, count in self.data['project_quality_counts'].items():
            self.assertIn(f'data-quality-filter="{status}"', self.html)
            self.assertIn(f'<b>{count}案</b>', self.html)
        calibrated = self.data['project_quality_counts']['独立Agent校准，非专家']
        self.assertIn(f'<strong>{len(projects) - calibrated}</strong><span>仍需推进', self.html)
        self.assertIn('未评或待复评', self.html)
        self.assertIn('未评不算0分', self.html)

    def test_075_method_categories_and_baseline(self):
        counts = collections.Counter(row['category'] for row in self.data['methods'])
        self.assertEqual(len(counts), 7)
        self.assertIn('64份独立校准基线', self.html)
        self.assertIn('47.5', self.html)
        self.assertIn('61.25', self.html)
        for row in self.data['method_upgrades']:
            self.assertIn(str(row['score']), self.html)

    def test_075_original_detail_features_and_deep_links_remain(self):
        for anchor in ('id="data"', 'id="work"', 'id="quality"', 'id="details"', 'id="next"'):
            self.assertIn(anchor, self.html)
        for feature in ('id="report-search"', 'data-table="projects"', 'data-table="methods"', 'id="detail-prev"', 'id="detail-next"', 'id="print-report"'):
            self.assertIn(feature, self.html)
        script = (ROOT / 'extensions/project-portal/data-report.js').read_text()
        self.assertIn('data-quality-filter', self.html)
        self.assertIn('row.dataset.quality === quality', script)
        self.assertIn('window.print()', script)

    def test_075_no_inline_style_or_link_arrows(self):
        self.assertNotIn('style=', self.html)
        built = (ROOT / 'output/inno-preview/gooddesign-site/inno/report/index.html').read_text()
        for arrow in ('↗', '↘', '→', '←', '↔', '⇄', '↑', '↓'):
            self.assertNotIn(arrow, built)


if __name__ == '__main__':
    unittest.main()
