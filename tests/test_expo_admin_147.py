# coding: utf-8
"""147 同名区县行政区身份与消歧。"""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import expo_agent_server as expo  # noqa: E402


class AdminIdentityTests(unittest.TestCase):
    def test_xihu_identities_and_slugs(self):
        admin = json.loads((ROOT / 'extensions/expo/geo/admin.json').read_text(encoding='utf-8'))
        self.assertEqual(len(admin), 2875)
        self.assertEqual(admin['330106']['label'], '杭州市西湖区')
        self.assertEqual(admin['360103']['label'], '南昌市西湖区')
        self.assertNotEqual(admin['330106']['label'], admin['360103']['label'])
        self.assertEqual(expo.report_slug('杭州市西湖区'), 'hangzhou-xihu')
        self.assertEqual(expo.report_slug('南昌市西湖区'), 'nanchang-xihu')

    def test_map_and_input_use_identity(self):
        source = (ROOT / 'extensions/expo/agent-template.html').read_text(encoding='utf-8')
        for phrase in ('function adminIdentity(', 'function ambiguousPlaces(', 'function showPlaceChoices(',
                       'rec.identity || shortName(rec.name)', 'identity: adminIdentity(',
                       'if (choices.length > 1) { showPlaceChoices(choices); return; }'):
            self.assertIn(phrase, source, phrase)


if __name__ == '__main__':
    unittest.main()
