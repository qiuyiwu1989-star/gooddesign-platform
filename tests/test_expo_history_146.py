# coding: utf-8
"""144/146 中文地名、版本历史与指定收录。"""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import expo_agent_server as expo  # noqa: E402


def pack():
    return {'depth': 'standard', 'sectors': [], 'companies': [], 'requirements': [], 'matches': [], 'opportunities': []}


class HistoryTests(unittest.TestCase):
    def test_versions_latest_specific_and_archive_without_copy(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'output') as tmp:
            with patch.object(expo, 'REPORT_STORE', Path(tmp)):
                expo.store_report('jiashan', pack())
                first = expo.list_reports()[0]
                expo.store_report('jiashan', pack())
                second = expo.list_reports()[0]
                self.assertNotEqual(first['id'], second['id'])
                self.assertEqual(len(expo.list_reports()), 2)
                self.assertEqual(expo.load_report('jiashan')['id'], second['id'])
                self.assertEqual(expo.load_report('jiashan', first['id'])['id'], first['id'])
                self.assertEqual(expo.load_report('嘉善')['id'], second['id'])
                self.assertIsNone(expo.load_report('jiashan', 'wrong-id'))
                archived = expo.archive_report('jiashan', first['id'])
                self.assertTrue(archived['curated'])
                self.assertEqual(len(list(Path(tmp).glob('*.json'))), 2)
                self.assertFalse(expo.load_report('jiashan', second['id'])['curated'])

    def test_existing_pinyin_content_becomes_chinese(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'output') as tmp:
            with patch.object(expo, 'REPORT_STORE', Path(tmp)):
                expo.store_report('jiashan', pack())
                loaded = expo.load_report('jiashan')
                self.assertEqual(loaded['place'], '嘉善')
                self.assertEqual(loaded['pack']['label'], '嘉善')
                self.assertEqual(loaded['slug'], 'jiashan')
                self.assertEqual(expo.list_reports()[0]['place'], '嘉善')


if __name__ == '__main__':
    unittest.main()
