import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ResearchStoryline134Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.needs_js = (ROOT / 'extensions/design-system/needs-workspace.js').read_text(encoding='utf-8')
        cls.needs_css = (ROOT / 'extensions/design-system/needs-workspace.css').read_text(encoding='utf-8')
        cls.canvas_html = (ROOT / 'extensions/reasoning-canvas/index.html').read_text(encoding='utf-8')
        cls.canvas_js = (ROOT / 'extensions/reasoning-canvas/reasoning-canvas.js').read_text(encoding='utf-8')

    def test_needs_steps_are_above_workspace_and_summary(self):
        self.assertIn('grid-column: 1 / -1', self.needs_css)
        self.assertIn('grid-template-columns: minmax(0, 1fr) 320px', self.needs_css)
        self.assertIn('grid-template-columns: repeat(4, minmax(0, 1fr))', self.needs_css)

    def test_needs_summary_is_progressive_but_export_is_complete(self):
        self.assertIn('rows.slice(0, 3)', self.needs_js)
        self.assertIn('rows.slice(3)', self.needs_js)
        self.assertIn('gd-needs-unknown-more', self.needs_js)
        self.assertIn('${state.projects.length} 个项目 · ${state.methods.length} 个方法', self.needs_js)
        self.assertIn('unknowns: unknowns()', self.needs_js)

    def test_canvas_has_home_four_stages_and_overview_controls(self):
        for dom_id in ('rc-story-home', 'rc-story-nav', 'rc-story-view', 'rc-overview', 'rc-more'):
            self.assertIn(f'id="{dom_id}"', self.canvas_html)
        for label in ('定义问题', '查证研究', '形成方向', '验证行动'):
            self.assertIn(label, self.canvas_js)
        self.assertIn("hasResearchActivity() ? 'step' : 'home'", self.canvas_js)

    def test_story_navigation_preserves_internal_nodes_and_local_only_handoff(self):
        for group in ("nodes: ['n1']", "nodes: ['n2', 'n3']", "nodes: ['n4', 'n5', 'n6']", "nodes: ['n7']"):
            self.assertIn(group, self.canvas_js)
        start = self.canvas_js.split('function selectStoryNode(id)', 1)[1].split('function render()', 1)[0]
        self.assertIn('researchView = \'step\'', start)
        self.assertIn('save();', start)
        self.assertNotIn('apiPost', start)
        self.assertNotIn('persistRemote', start)

    def test_more_menu_preserves_existing_action_ids(self):
        menu = self.canvas_html.split('id="rc-more"', 1)[1].split('</details>', 1)[0]
        for dom_id in ('rc-gdrp', 'rc-report', 'rc-flow-run', 'rc-export', 'rc-reset'):
            self.assertIn(f'id="{dom_id}"', menu)
        self.assertIn('id="rc-save"', self.canvas_html.split('id="rc-more"', 1)[0])

    def test_demo_still_defaults_to_overview(self):
        self.assertIn("isResearch() ? (hasResearchActivity() ? 'step' : 'home') : 'overview'", self.canvas_js)
        self.assertIn('story134', self.canvas_html)


if __name__ == '__main__':
    unittest.main()
