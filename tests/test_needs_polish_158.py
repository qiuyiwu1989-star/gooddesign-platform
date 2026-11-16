# coding: utf-8
"""158 需求研究界面精修契约。"""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class NeedsPolish158Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.js = (ROOT / 'extensions/design-system/needs-workspace.js').read_text()
        cls.css = (ROOT / 'extensions/design-system/needs-workspace.css').read_text()
        cls.live = (ROOT / 'extensions/design-system/needs-live-demo.css').read_text()

    def test_unknowns_are_collapsed_with_complete_list(self):
        self.assertIn('查看全部 ${rows.length} 项待确认', self.js)
        self.assertIn('rows.map(item =>', self.js)
        self.assertNotIn('primaryUnknowns', self.js)
        self.assertIn('gd-needs-unknown-more', self.js)

    def test_lightweight_visual_hierarchy(self):
        for marker in ('.gd-needs-guide.gd-needs-panel{padding:0;border:0', '.gd-needs-prompt{margin-bottom:24px', '.gd-needs-status-card{padding:20px', '.gd-needs-heading-actions #live-demo-start'):
            self.assertIn(marker, self.css)

    def test_live_mobile_grid_does_not_expand_from_stage_scroller(self):
        self.assertIn('.gd-live-layout{grid-template-columns:minmax(0,1fr)}', self.live)
        self.assertIn('overflow-wrap:anywhere;word-break:break-word', self.live)

    def test_existing_workflow_and_model_boundary_unchanged(self):
        for marker in ("const KEY = 'gd-needs-workspace-v1'", "const HANDOFF_KEY = 'gd-reasoning-canvas-handoff-v1'", 'model_calls: 0', 'source_projects_modified: false', 'engineering_validated: false', 'data-action="canvas"', 'data-action="download"', 'data-action="clarify"'):
            self.assertIn(marker, self.js)

    def test_mobile_print_and_focus_rules_remain(self):
        self.assertIn('@media(max-width:640px)', self.css)
        self.assertIn('@media print', self.css)
        self.assertIn('outline: 2px solid var(--focus-color)', self.css)
        self.assertIn('@media (prefers-reduced-motion: reduce)', self.live)


if __name__ == '__main__':
    unittest.main()
