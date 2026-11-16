# coding: utf-8
"""135/136 正式交付与运行控制回归。"""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import expo_agent_server as expo  # noqa: E402


class ArchiveTests(unittest.TestCase):
    def test_archive_marks_only_existing_server_report(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'output') as tmp:
            with patch.object(expo, 'REPORT_STORE', Path(tmp)):
                pack = {'sectors': [], 'companies': [], 'requirements': [], 'matches': [], 'opportunities': []}
                expo.store_report('玉环', pack)
                self.assertFalse(expo.load_report('玉环')['curated'])
                archived = expo.archive_report('玉环')
                self.assertTrue(archived['curated'])
                self.assertEqual(expo.archive_report('不存在'), None)

    def test_print_delivery_and_controls_contract(self):
        source = (ROOT / 'extensions/expo/agent-template.html').read_text(encoding='utf-8')
        self.assertIn('#report,#report.on{position:static!important;display:block!important', source)
        self.assertIn('function deliveryDocument()', source)
        self.assertIn("new URL(href, 'https://haoshejiguan.com/expo/')", source)
        self.assertIn("a.download = LIVE.reportNo + '.html'", source)
        self.assertIn("$('#btn-save').addEventListener('click', saveReportHtml)", source)
        self.assertIn("$('#pause').addEventListener('click', togglePause)", source)
        self.assertIn('if (LIVE.paused) { LIVE.queue.push(evt); return; }', source)
        self.assertIn("$('#btn-archive').addEventListener('click', archiveCurrent)", source)
        self.assertIn("if parsed.path != '/api/archive':", (ROOT / 'scripts/expo_agent_server.py').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
