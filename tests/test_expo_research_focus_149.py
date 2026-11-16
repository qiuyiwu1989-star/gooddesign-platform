# coding: utf-8
"""149 研究路径聚焦与深度可视化契约。"""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ResearchFocusTests(unittest.TestCase):
    def test_focus_trace_and_depth_contract(self):
        source = (ROOT / 'extensions/expo/agent-template.html').read_text(encoding='utf-8')
        for phrase in ('function focusResearchCard(', 'function clearResearchFocus(',
                       'function makeResearchFocusable(', 'function updateDepth(',
                       'class="depth-panel"', 'class="research-focus"',
                       "event.key === 'Escape'", "event.key === 'Enter'",
                       "card.classList.add('trace')", 'updateDepth();'):
            self.assertIn(phrase, source, phrase)
        self.assertIn("'—'", source)
        self.assertIn('进行中分工', source)
        self.assertIn('真实研究事件', source)


if __name__ == '__main__':
    unittest.main()
