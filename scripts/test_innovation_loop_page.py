import json
import re
import unittest
from pathlib import Path
from innovation_loop_page import page, friendly

ASSETS = Path(__file__).resolve().parents[1] / 'extensions/enterprise-workbench'


class PageTests(unittest.TestCase):
    def test_escape(self):
        s = page({'requirement': {'goal': '</pre><script>alert(1)</script>'}})
        self.assertIn('\\u003c/pre>\\u003cscript>', s)
        self.assertNotIn('</pre><script>alert', s)

    def test_interfaces(self):
        s = page({})
        script = (ASSETS / 'enterprise-workbench.js').read_text()
        self.assertIn('/workspace/enterprise-workbench.css', s)
        self.assertIn('/workspace/enterprise-workbench.js', s)
        self.assertIn("fetch('/api/bundle' + location.search", script)
        self.assertIn("fetch('/api/feedback'", script)
        self.assertIn('aria-live="polite"', s)
        self.assertIn('type="button"', s)

    def test_feedback_form_and_action(self):
        s = page({'claims': [], 'research_action': {'question': '构造研究'}})
        script = (ASSETS / 'enterprise-workbench.js').read_text()
        for token in ('route-select', 'internal-consent', 'feedback-kind', '竞争解释', '停止条件', '该路线尚无可绑定的主张记录'):
            self.assertIn(token, s + script)
        self.assertIn('claim_ref: { id: claim.id, revision: claim.revision }', script)

    def test_inert_json_escape(self):
        value = {'notice': '</script><script>bad</script>'}
        s = page(value)
        encoded = re.search(r'id="initial-bundle">(.*?)</script>', s).group(1)
        self.assertNotIn('<', encoded)
        self.assertEqual(json.loads(encoded), value)

    def test_friendly(self):
        self.assertEqual(friendly({'value': '原文', 'nature': 'source_statement'}), '原文（来源陈述）')
        self.assertEqual(friendly({'status': 'required'}), '状态：需要专业批准')
        s = page({'experiences': [{'object_scope': '特定设备', 'mechanism': {'value': '过程', 'nature': 'source_statement'}}], 'requirement': {'status': 'proposed'}})
        self.assertIn('特定设备', s)
        self.assertIn('待确认提案', (ASSETS / 'enterprise-workbench.js').read_text())

    def test_task_selector(self):
        s = page({'tasks': [{'task_id': 'rubber-v1', 'title': '割胶'}], 'current_task_id': 'rubber-v1'})
        script = (ASSETS / 'enterprise-workbench.js').read_text()
        self.assertIn('task-select', s)
        self.assertIn("url.searchParams.set('task'", script)
        self.assertIn('研究行动', s + script)
        self.assertIn('本任务方法', script)

    def test_bad_bundle(self):
        with self.assertRaises(ValueError):
            page([])

    def test_decision_overview_and_side_panel(self):
        s = page({'routes': [{'id': 'R', 'mechanism': 'unsafe </script>'}], 'clarifications': []})
        script = (ASSETS / 'enterprise-workbench.js').read_text()
        for token in ['decision-overview', 'ew-route-grid', 'evidence-panel', 'showModal()', 'data-route-open', '/api/clarifications', '待确认补充', 'clarify-records']:
            self.assertIn(token, s + script)
        self.assertIn('不改写原需求', script)
        self.assertNotIn('unsafe </script>', s)


if __name__ == '__main__':
    unittest.main()
