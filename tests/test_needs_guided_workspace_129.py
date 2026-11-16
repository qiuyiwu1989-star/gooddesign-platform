import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'extensions/design-system'


class NeedsGuidedWorkspace129Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (SOURCE / 'needs-workspace.html').read_text(encoding='utf-8')
        cls.js = (SOURCE / 'needs-workspace.js').read_text(encoding='utf-8')

    def test_129_preserves_074_and_082_dom_contracts(self):
        for dom_id in ('steps', 'task', 'status', 'example', 'live-demo', 'live-demo-start', 'live-pause', 'live-replay', 'live-close', 'live-log', 'live-evidence', 'live-report', 'live-progress'):
            self.assertIn(f'id="{dom_id}"', self.html)
        self.assertIn('id="nw-problem"', self.js)
        self.assertIn('data-action="next"', self.js)
        self.assertIn("if (name === 'next') return setStep(state.step + 1);", self.js)
        self.assertIn('src="needs-live-demo.js"', self.html)

    def test_129_xiaohao_is_the_single_guide_voice(self):
        for class_name in ('gd-needs-guide', 'gd-needs-conversation', 'gd-needs-prompt', 'gd-needs-reply', 'gd-needs-taskcard', 'gd-needs-draft-note'):
            self.assertIn(class_name, self.js)
        self.assertIn('小好 · 研究引导', self.js)
        self.assertIn('全程 0 次模型调用', self.html)
        self.assertNotIn('AI 推荐', self.js)

    def test_129_task_card_has_all_live_fields(self):
        for field in ('problem', 'outcome', 'constraints', 'references', 'route', 'unknowns', 'next'):
            self.assertIn(f'data-task-field="{field}"', self.js)
        for label in ('问题', '目标', '约束', '参考', '路线', '未知', '下一步'):
            self.assertIn(f'<dt>{label}</dt>', self.js)
        self.assertIn('renderStatus();', self.js.split("querySelectorAll('[data-field]')", 1)[1])

    def test_129_four_stage_flow_allows_optional_fields_and_skips(self):
        for title in ('真实问题', '参考资料', '研究路线', '核对计划'):
            self.assertIn(title, self.js)
        self.assertIn('补充研究名称、目标与约束（可选）', self.js)
        self.assertIn('<details class="gd-needs-optional"', self.js)
        self.assertIn('期待什么改变', self.js)
        self.assertIn('已知条件与不能牺牲的内容', self.js)
        self.assertNotIn('required', self.html + self.js)
        self.assertIn('data-action="skip" data-skip="references"', self.js)
        self.assertIn('data-action="skip" data-skip="route"', self.js)
        self.assertIn('跳过只表示这里不做选择，不代表没有相关资料', self.js)
        self.assertIn('未选择路线不会阻止继续', self.js)

    def test_129_route_starts_null_and_legacy_measure_is_not_confirmation(self):
        initial = self.js.split('const initial = () =>', 1)[1].split('const text =', 1)[0]
        self.assertIn('route: null', initial)
        self.assertIn('route_selected: false', initial)
        self.assertIn("saved.route !== 'measure'", self.js)
        self.assertIn('route: route ? { id: state.route, ...route } : null', self.js)
        self.assertNotIn('|| ROUTES.measure', self.js)
        self.assertIn('state.route_selected = true;', self.js)

    def test_129_state_is_deterministic_and_has_no_model_or_api_intelligence(self):
        self.assertEqual(self.js.count('fetch('), 2)
        self.assertIn("fetch('/inno/catalog.json'", self.js)
        self.assertIn("fetch('/inno/portal/method-catalog.json'", self.js)
        self.assertNotIn('Promise.all(', self.js)
        self.assertIn('不会猜测标题、目标或约束', self.js)
        self.assertEqual(self.js.count('state.title ='), 1)
        self.assertIn('model_calls: 0', self.js)
        for forbidden in ('OpenAI', 'chat/completions', 'semantic_match', 'autoDetect', '自动匹配'):
            self.assertNotIn(forbidden, self.js)

    def test_129_draft_restore_and_storage_failures_are_contained(self):
        self.assertIn('function restore(saved)', self.js)
        self.assertIn('JSON.parse(savedRaw)', self.js)
        self.assertRegex(self.js, r'function save\(\) \{\s*try \{')
        self.assertIn("localStorage.setItem(KEY, JSON.stringify(state));", self.js)
        self.assertIn('旧草稿无法读取，已新建草稿', self.js)
        self.assertIn('浏览器存储不可用，草稿仅保留在当前页面', self.js)
        self.assertIn('请导出研究上下文，避免刷新后丢失', self.js)

    def test_129_catalog_failures_are_independent(self):
        self.assertIn('function loadProjects()', self.js)
        self.assertIn('function loadMethods()', self.js)
        self.assertIn('projectCatalogFailed = true;', self.js)
        self.assertIn('methodCatalogFailed = true;', self.js)
        self.assertIn('项目目录暂时不可用，方法参考仍可选择，也可以跳过', self.js)
        self.assertIn('方法目录暂时不可用，项目参考仍可选择，也可以跳过', self.js)
        self.assertNotIn('目录暂时无法加载</h2>', self.js)

    def test_129_packet_schema_boundaries_and_skipped_are_preserved(self):
        for value in ('gooddesign-research-packet-1.0', 'prepared_context_not_executed', 'research_proposed_not_customer_confirmed', 'pending_confirmation', 'source_projects_modified: false', 'engineering_validated: false', 'expert_reviewed: false'):
            self.assertIn(value, self.js)
        self.assertIn('skipped: [...state.skipped]', self.js)
        self.assertIn('pending_clarifications: state.clarifications', self.js)
        self.assertIn("relation: 'reference_not_adoption_proof'", self.js)

    def test_129_canvas_handoff_is_random_verified_and_then_navigates(self):
        self.assertIn('data-action="canvas"', self.js)
        self.assertIn("const HANDOFF_KEY = 'gd-reasoning-canvas-handoff-v1';", self.js)
        self.assertIn("schema: 'gooddesign-canvas-handoff-1.0'", self.js)
        self.assertIn('task_id: randomTaskId()', self.js)
        self.assertIn('created_at: new Date().toISOString()', self.js)
        self.assertIn('packet: packet()', self.js)
        self.assertIn('return `needs-${window.crypto.randomUUID()}`', self.js)
        canvas = self.js.split("if (name === 'canvas')", 1)[1].split("if (name === 'download')", 1)[0]
        write = canvas.index('localStorage.setItem(HANDOFF_KEY, serialized);')
        verify = canvas.index('localStorage.getItem(HANDOFF_KEY) !== serialized')
        navigate = canvas.index("location.assign('/canvas/?from=needs');")
        self.assertLess(write, verify)
        self.assertLess(verify, navigate)
        self.assertIn('catch {', canvas)
        self.assertIn('仍停留在本页', canvas)
        self.assertIn('notify();', canvas)

    def test_129_export_copy_clarify_and_live_demo_remain_isolated(self):
        self.assertIn("$('handoff').showModal()", self.js)
        self.assertIn("$('handoff-text').select()", self.js)
        self.assertNotIn('navigator.clipboard', self.js)
        self.assertIn('Command+C 或 Ctrl+C', self.html)
        error_branch = self.js.split('if (!value || !actor) {', 1)[1].split('state.clarifications.push', 1)[0]
        self.assertIn('feedback.textContent = message.text', error_branch)
        self.assertNotIn('render();', error_branch)
        self.assertNotIn("$('live-demo')", self.js)
        self.assertNotIn('live-progress', self.js)
        self.assertIn("const KEY = 'gd-needs-workspace-v1';", self.js)

    def test_129_copy_has_no_long_dashes_or_link_arrows(self):
        self.assertNotIn('—', self.html + self.js)
        for arrow in ('↗', '↘', '→', '←', '↔', '⇄', '↑', '↓'):
            self.assertNotIn(arrow, self.html + self.js)


if __name__ == '__main__':
    unittest.main()
