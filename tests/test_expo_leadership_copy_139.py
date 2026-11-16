# coding: utf-8
"""139 政府领导版咨政报告语言回归。"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import expo_agent_server as expo  # noqa: E402


class LeadershipCopyTests(unittest.TestCase):
    def test_no_internal_jargon_in_report_template(self):
        source = (ROOT / 'extensions/expo/agent-template.html').read_text(encoding='utf-8')
        for phrase in ('方向可以谈', 'proposed', 'hard=null', '确定性层', '模型调用',
                       '逐字召回', '机制迁移评估', '最终推荐', '真实调用失败', '研究假设'):
            self.assertNotIn(phrase, source, phrase)
        for phrase in ('先开展验证，再研究推广', '优秀案例的借鉴价值',
                       '创新方向与试点建议', '待企业确认', '依据较充分', '部分印证'):
            self.assertIn(phrase, source, phrase)

    def test_model_prompt_requires_leadership_language(self):
        self.assertIn('地方政府领导', expo.SYS_JSON)
        self.assertIn('咨政语言', expo.SYS_JSON)
        self.assertIn('实地调研', expo.SYS_JSON)
        self.assertIn('不要输出其他文字', expo.SYS_JSON)


if __name__ == '__main__':
    unittest.main()
