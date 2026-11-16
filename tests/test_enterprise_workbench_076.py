import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from innovation_loop_page import page
from innovation_loop_server import bundle
from innovation_loop_tasks import IDS


class EnterpriseWorkbench076Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script = (ROOT / 'extensions/enterprise-workbench/enterprise-workbench.js').read_text()
        cls.css = (ROOT / 'extensions/enterprise-workbench/enterprise-workbench.css').read_text()

    def test_076_product_views_and_navigation(self):
        html = page({})
        for view in ('overview', 'requirement', 'routes', 'validation', 'feedback'):
            self.assertIn(f'data-view="{view}"', html)
        self.assertIn('企业创新工作台', html)
        self.assertIn('当前研究判断', self.script)
        self.assertNotIn('id="auto"', html + self.script)
        self.assertNotIn('自动演示', html + self.script)

    def test_076_three_real_task_bundles(self):
        self.assertEqual(len(IDS), 3)
        for task_id in IDS:
            data = bundle(task_id)
            self.assertEqual(data['current_task_id'], task_id)
            self.assertEqual(data['requirement']['status'], 'proposed')
            self.assertEqual(len(data['routes']), 3)
            self.assertEqual(len(data['research_action']), 3)
            self.assertEqual(len(data['experiences']), 6)
            self.assertEqual(len(data['methods']), 3)

    def test_076_real_write_and_export_contracts(self):
        for token in ("fetch('/api/clarifications'", "fetch('/api/feedback'", 'pending_review', 'pendingFeedbackIdentity', 'claim_ref', 'internal_research: true, public: false, training: false'):
            self.assertIn(token, self.script)
        for token in ('gooddesign-enterprise-workbench-handoff-1.0', 'model_calls: 0', 'source_projects_modified: false', 'execution_authorized: false', 'engineering_validated: false', 'expert_reviewed: false'):
            self.assertIn(token, self.script)

    def test_076_accessibility_and_responsive_rules(self):
        html = page({})
        self.assertIn('id="main"', html)
        self.assertIn('aria-labelledby="evidence-title"', html)
        self.assertIn('aria-live="polite"', html)
        self.assertIn("$('#evidence-close').focus()", self.script)
        self.assertIn("addEventListener('close'", self.script)
        for rule in ('@media(max-width:720px)', '@media(prefers-reduced-motion:reduce)', '@media print'):
            self.assertIn(rule, self.css)

    def test_076_server_asset_whitelist(self):
        source = (ROOT / 'scripts/innovation_loop_server.py').read_text()
        self.assertIn("'/workspace/enterprise-workbench.css'", source)
        self.assertIn("'/workspace/enterprise-workbench.js'", source)
        self.assertIn("ROOT/'extensions/enterprise-workbench'", source)


if __name__ == '__main__':
    unittest.main()
