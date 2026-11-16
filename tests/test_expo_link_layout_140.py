# coding: utf-8
"""140 全拼报告链接、旧链接兼容与浅色双版式。"""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import expo_agent_server as expo  # noqa: E402


class SlugTests(unittest.TestCase):
    def test_known_pinyin_and_ascii_fallback(self):
        self.assertEqual(expo.report_slug('玉环'), 'yuhuan')
        self.assertEqual(expo.report_slug('嘉善'), 'jiashan')
        fallback = expo.report_slug('新地方')
        self.assertTrue(fallback.isascii())
        self.assertEqual(fallback, expo.report_slug('新地方'))
        self.assertEqual(expo.report_slug('新地方', 'xin-difang'), 'xin-difang')
        self.assertNotEqual(expo.report_slug('新地方', '中文'), '中文')

    def test_load_by_place_and_slug_with_legacy_report(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'output') as tmp:
            with patch.object(expo, 'REPORT_STORE', Path(tmp)):
                pack = {'sectors': [], 'companies': [], 'requirements': [], 'matches': [], 'opportunities': []}
                expo.store_report('玉环', pack)
                by_slug = expo.load_report('yuhuan')
                by_place = expo.load_report('玉环')
                self.assertEqual(by_slug['place'], '玉环')
                self.assertEqual(by_slug['slug'], 'yuhuan')
                self.assertEqual(by_place['place'], '玉环')
                self.assertEqual(expo.list_reports()[0]['slug'], 'yuhuan')


class LayoutContractTests(unittest.TestCase):
    def test_light_mode_home_and_print_overrides(self):
        source = (ROOT / 'extensions/expo/agent-template.html').read_text(encoding='utf-8')
        self.assertIn("body.report-mode{--ink:#1b1e24", source)
        self.assertIn("body.report-mode #rbody .rdoc", source)
        self.assertIn('body.report-mode .rcover{min-height:238mm!important', source)
        self.assertIn('aria-label="返回产业研究首页"', source)
        self.assertIn('href="https://haoshejiguan.com/expo/"', source)
        self.assertIn("P.slug || reportSlug(P.label)", source)


if __name__ == '__main__':
    unittest.main()
