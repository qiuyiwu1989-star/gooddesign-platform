# coding: utf-8
"""148 多角色工位与持续工作动效契约。"""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class WorkerTests(unittest.TestCase):
    def test_workers_have_roles_motion_but_no_fake_counts(self):
        source = (ROOT / 'extensions/expo/agent-template.html').read_text(encoding='utf-8')
        self.assertIn('function renderWorkers(', source)
        self.assertIn('function rolePointer(', source)
        self.assertIn('className = \'research-card worker-card\'', source)
        self.assertIn('worker-line', source)
        self.assertIn('renderWorkers(stage);', source)
        block = source.split('function renderWorkers(', 1)[1].split('function buildGraph(', 1)[0]
        self.assertNotIn('processCount +=', block)
        self.assertNotIn('LIVE.c[', block)


if __name__ == '__main__':
    unittest.main()
