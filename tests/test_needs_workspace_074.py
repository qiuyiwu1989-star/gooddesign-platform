import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/inno-preview/gooddesign-site'


class NeedsWorkspace074Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = (OUT / 'inno/needs-v2/index.html').read_text()
        cls.script = (OUT / 'inno/needs-v2/needs-workspace.js').read_text()

    def test_074_workspace_route_uses_shared_chrome(self):
        self.assertIn('id="steps"', self.page)
        self.assertIn('id="task"', self.page)
        self.assertIn('id="status"', self.page)
        self.assertEqual(self.page.count('data-gd-chrome="navigation"'), 1)
        self.assertEqual(self.page.count('data-gd-chrome="footer"'), 1)
        self.assertIn('aria-current="page"', self.page)

    def test_074_research_flow_and_reference_binding(self):
        for title in ('真实问题', '参考资料', '研究路线', '核对计划'):
            self.assertIn(title, self.script)
        self.assertIn("fetch('/inno/catalog.json'", self.script)
        self.assertIn("fetch('/inno/portal/method-catalog.json'", self.script)
        self.assertIn('aria-pressed', self.script)
        self.assertIn('localStorage.setItem', self.script)

    def test_074_export_preserves_research_boundaries(self):
        for field in ('prepared_context_not_executed', 'research_proposed_not_customer_confirmed', 'pending_confirmation', 'model_calls: 0', 'source_projects_modified: false', 'engineering_validated: false', 'expert_reviewed: false'):
            self.assertIn(field, self.script)
        self.assertNotIn('工程验证通过', self.script)
        self.assertIn('function notify()', self.script)
        self.assertGreaterEqual(self.script.count('notify();'), 1)
        self.assertIn("$('handoff').showModal()", self.script)
        self.assertIn("$('handoff-text').select()", self.script)
        self.assertNotIn('navigator.clipboard', self.script)
        self.assertIn('Command+C 或 Ctrl+C', self.page)

    def test_074_validation_keeps_clarification_input(self):
        error_branch = self.script.split("if (!value || !actor) {", 1)[1].split('state.clarifications.push', 1)[0]
        self.assertIn('feedback.textContent = message.text', error_branch)
        self.assertIn("$('nw-clarify-actor')).focus()", error_branch)
        self.assertNotIn('render();', error_branch)

    def test_074_responsive_layout_and_no_link_arrows(self):
        css = (OUT / 'inno/needs-v2/needs-workspace.css').read_text()
        self.assertIn('@media(max-width:900px)', css)
        self.assertIn('@media(max-width:640px)', css)
        for arrow in ('↗', '↘', '→', '←', '↔', '⇄', '↑', '↓'):
            self.assertNotIn(arrow, self.page + self.script)


if __name__ == '__main__':
    unittest.main()
