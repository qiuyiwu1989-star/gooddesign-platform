import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/research-089'


class MaterialInventory089Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((OUT / 'material-inventory.json').read_text())
        cls.summary = json.loads((OUT / 'summary.json').read_text())
        cls.rows = cls.data['projects']
        cls.index = json.loads((ROOT / '04-知识库/项目库/项目索引.json').read_text())['projects']

    def test_089_inventory_has_every_project_in_index_order(self):
        self.assertEqual(len(self.rows), 560)
        self.assertEqual([row['project_id'] for row in self.rows], [row['id'] for row in self.index])
        self.assertEqual(len({row['project_id'] for row in self.rows}), 560)
        with (OUT / 'material-inventory.csv').open(encoding='utf-8-sig') as stream:
            self.assertEqual(len(list(csv.DictReader(stream))), 560)

    def test_089_totals_are_recomputed_from_real_rows(self):
        for key in ('material_bytes', 'raw_source_files', 'raw_source_bytes', 'image_files', 'image_bytes', 'full_sources', 'patents_sources'):
            self.assertEqual(self.summary['totals'][key], sum(row[key] for row in self.rows), key)
        self.assertEqual(self.summary['totals']['native_projects'], 103)
        self.assertGreater(self.summary['totals']['material_bytes'], 0)

    def test_089_gaps_cover_batches_native_images_and_documents(self):
        expected = {'缺full标准批': 93, '缺patents标准批': 93, '未生成原生研究版': 457}
        for gap, count in expected.items():
            self.assertEqual(self.summary['gap_counts'][gap], count, gap)
        self.assertIn('缺文档:07-专利与论文明细.md', self.summary['gap_counts'])
        self.assertIn('full校验异常', self.summary['gap_counts'])
        self.assertIn('patents校验异常', self.summary['gap_counts'])
        self.assertIn('无图片素材', self.summary['gap_counts'])
        self.assertTrue(self.summary['generated_at'])

    def test_089_c30_is_repaired_but_remains_lead(self):
        row = next(row for row in self.rows if row['project_id'] == '2021-c30')
        self.assertEqual(row['patents_status'], 'mechanical_pass_pending_content_review')
        self.assertNotIn('patents校验异常', row['gaps'])
        self.assertIn('专利仅lead待核', row['gaps'])

    def test_089_current_path_errors_are_visible_not_hidden(self):
        row = next(row for row in self.rows if row['project_id'] == '2021-01')
        self.assertEqual(row['full_status'], 'needs_correction')
        self.assertGreater(row['full_sources'], 0)
        self.assertIn('full校验异常', row['gaps'])
        self.assertEqual(self.summary['gap_counts']['旧底稿证据绑定异常'], 1)


if __name__ == '__main__':
    unittest.main()
