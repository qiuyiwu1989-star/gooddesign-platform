# coding: utf-8
"""143 实时调研展开与节奏增强契约。"""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ResearchExpansionTests(unittest.TestCase):
    def test_stream_cards_and_pace_contract(self):
        source = (ROOT / 'extensions/expo/agent-template.html').read_text(encoding='utf-8')
        server = (ROOT / 'scripts/expo_agent_server.py').read_text(encoding='utf-8')
        self.assertIn('function expandResearch(', source)
        self.assertIn('class="research-stream"', source)
        self.assertIn('while (stream.children.length > 6)', source)
        self.assertIn("expandResearch(evt.stage, evt.kind, LIVE.lastActivity, evt.n)", source)
        self.assertIn("expandResearch(stage, 'thinking', draft, 0, true)", source)
        self.assertIn('await sleep(45)', source)
        self.assertIn('await sleep(35)', source)
        self.assertIn("className = 'agent-pointer'", source)
        self.assertIn("scanned: '逐档案检索'", source)
        self.assertIn('last_push > 0.12', server)


if __name__ == '__main__':
    unittest.main()
