import csv
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/research-100'
BASELINE = json.loads((OUT / 'current-baseline.json').read_text())
INVENTORY = json.loads((OUT / 'material-inventory/material-inventory.json').read_text())
SUMMARY = INVENTORY['summary']
ROWS = INVENTORY['projects']


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ArchiveBaseline100Tests(unittest.TestCase):
    def test_100_current_inventory_covers_the_whole_catalog(self):
        index = json.loads((ROOT / '04-知识库/项目库/项目索引.json').read_text())['projects']
        self.assertEqual(len(index), 560)
        self.assertEqual([row['project_id'] for row in ROWS], [row['id'] for row in index])
        self.assertEqual(SUMMARY['totals']['native_projects'], 103)
        self.assertEqual(SUMMARY['gap_counts']['未生成原生研究版'], 457)
        with (OUT / 'material-inventory/material-inventory.csv').open(encoding='utf-8-sig') as stream:
            self.assertEqual(len(list(csv.DictReader(stream))), 560)

    def test_100_current_inventory_recomputes_totals_and_known_gaps(self):
        for key in ('material_bytes', 'raw_source_files', 'raw_source_bytes', 'image_files', 'image_bytes', 'full_sources', 'patents_sources'):
            self.assertEqual(SUMMARY['totals'][key], sum(row[key] for row in ROWS), key)
        self.assertEqual(SUMMARY['gap_counts']['缺文档:07-专利与论文明细.md'], 199)
        self.assertEqual(SUMMARY['gap_counts']['full校验异常'], 205)
        self.assertEqual(SUMMARY['gap_counts']['patents校验异常'], 127)
        self.assertEqual(SUMMARY['gap_counts']['缺full标准批'], 93)
        self.assertEqual(SUMMARY['gap_counts']['缺patents标准批'], 93)

    def test_100_manifest_pins_current_files_and_duplicate_snapshot(self):
        self.assertEqual(BASELINE['schema'], 'gooddesign-archive-baseline-1.0')
        self.assertEqual(BASELINE['duplicate_index']['mutation_policy'], 'index_only_no_delete')
        for section, path_key, hash_key in (
            ('material_inventory', 'path', 'sha256'),
            ('material_inventory', 'rows_path', 'rows_sha256'),
            ('material_inventory', 'csv_path', 'csv_sha256'),
            ('duplicate_index', 'summary_path', 'summary_sha256'),
            ('duplicate_index', 'groups_path', 'groups_sha256'),
            ('project_measurements', 'path', 'sha256'),
        ):
            item = BASELINE[section]
            self.assertEqual(sha256(ROOT / item[path_key]), item[hash_key], item[path_key])
        duplicate_summary = json.loads((ROOT / BASELINE['duplicate_index']['summary_path']).read_text())
        self.assertEqual(duplicate_summary['duplicate_groups'], BASELINE['duplicate_index']['all_groups'])
        self.assertEqual(BASELINE['duplicate_index']['all_groups'], 2690)
        self.assertEqual(BASELINE['duplicate_index']['content_groups'], 2610)

    def test_100_scope_does_not_turn_asset_counts_into_quality(self):
        meaning = SUMMARY['meaning'] + BASELINE['quality_meaning']
        for phrase in ('不代表独立来源', '全文核读', '研究完整度', '质量分'):
            self.assertIn(phrase, meaning)
        self.assertNotEqual(BASELINE['status'], 'production_realtime')
        self.assertEqual(BASELINE['not_researched_projects'], 457)


if __name__ == '__main__':
    unittest.main()
