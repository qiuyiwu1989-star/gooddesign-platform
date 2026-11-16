# coding: utf-8
"""141 多 Agent 角色形象与分工思考流契约。"""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class AgentProcessTests(unittest.TestCase):
    def test_roles_process_and_readable_thoughts(self):
        source = (ROOT / 'extensions/expo/agent-template.html').read_text(encoding='utf-8')
        self.assertIn('class="member-process" id="mp-', source)
        self.assertIn('function readableThought(', source)
        self.assertIn('function addAgentNote(', source)
        self.assertIn('function setAgentDraft(', source)
        self.assertIn('addAgentNote(id, LIVE.lastActivity)', source)
        self.assertIn("setAgentDraft(agent.id, draft)", source)
        self.assertIn("upsertThinking(draft, stage)", source)
        self.assertIn('class="agent-ip"', source)
        self.assertIn('class="role-badge"', source)
        self.assertIn('LIVE.paused) { LIVE.queue.push(evt); return; }', source)


if __name__ == '__main__':
    unittest.main()
