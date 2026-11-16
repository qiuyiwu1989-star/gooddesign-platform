# coding: utf-8
"""152 领导决策摘要与专业核查内容构成。"""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ReportContentTests(unittest.TestCase):
    def test_decision_evidence_and_pilot_contract(self):
        source = (ROOT / 'extensions/expo/agent-template.html').read_text(encoding='utf-8')
        for phrase in ('class="decision-grid"', '产业基础', '关键制约', '案例启示', '建议工作路径',
                       'class="evidence-note"', 'class="pilot-framework"',
                       '试点组织建议', '供会商 · 非既定分工', '试点对象', '牵头协同', '评价依据', '推广前提'):
            self.assertIn(phrase, source, phrase)
        self.assertIn('demandExamples.map', source)
        self.assertIn('caseExamples.map', source)
        self.assertIn('firstOp.verify', source)


if __name__ == '__main__':
    unittest.main()
