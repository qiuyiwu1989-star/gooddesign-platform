# coding: utf-8
"""142 上方分工主视图与左侧单 Agent 执行流契约。"""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class OrchestratorTests(unittest.TestCase):
    def test_single_agent_process_contract(self):
        source = (ROOT / 'extensions/expo/agent-template.html').read_text(encoding='utf-8')
        self.assertIn('id="orchestrator"', source)
        self.assertIn('研究统筹', source)
        self.assertIn('function updateOrchestrator()', source)
        self.assertIn('function upsertThinking(', source)
        self.assertIn("typeLog(LIVE.lastActivity, 'activity')", source)
        self.assertIn("typeLog('阶段结果 · ' + count, 'ok')", source)
        self.assertIn('#team,#stages{display:none!important}', source)
        self.assertIn('logEl.scrollTop = logEl.scrollHeight', source)


if __name__ == '__main__':
    unittest.main()
