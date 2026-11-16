# coding: utf-8
"""150/151 地方产业对象、关系链与工作指针契约。"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import expo_agent_server as expo  # noqa: E402


class TargetTests(unittest.TestCase):
    def test_region_industry_question_are_structured(self):
        target = expo.normalize_target('玉环水暖阀门', {'region': '玉环', 'industry': '水暖阀门', 'question': '研究本地企业需求与试点'})
        self.assertEqual(target['label'], '玉环水暖阀门')
        self.assertEqual(target['region'], '玉环')
        self.assertEqual(target['industry'], '水暖阀门')
        self.assertIn('本地企业需求', target['question'])
        self.assertEqual(expo.normalize_target('jiashan')['region'], '嘉善')

    def test_front_and_report_contract(self):
        source = (ROOT / 'extensions/expo/agent-template.html').read_text(encoding='utf-8')
        server = (ROOT / 'scripts/expo_agent_server.py').read_text(encoding='utf-8')
        for phrase in ('function parseResearchTarget(', 'target.region', 'target.industry',
                       "'&region='", "'&industry='", "'&question='", 'class="relation-flow"',
                       'function moveResearchCursor(', 'cursor.dataset.role = role.id'):
            self.assertIn(phrase, source, phrase)
        self.assertIn('外部产业趋势只能作外部参照', server)
        self.assertIn('案例检索由需求驱动', server)
        self.assertIn("'target': target", server)


if __name__ == '__main__':
    unittest.main()
