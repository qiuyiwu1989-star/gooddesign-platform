import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/inno-preview/gooddesign-site/inno/needs-v2'


class NeedsLiveDemo082Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (OUT / 'index.html').read_text(encoding='utf-8')
        cls.js = (OUT / 'needs-live-demo.js').read_text(encoding='utf-8')
        cls.css = (OUT / 'needs-live-demo.css').read_text(encoding='utf-8')

    def test_082_demo_identity_and_real_evidence(self):
        self.assertIn('模拟演示 · 真实资料 · 0 次模型调用', self.html)
        self.assertIn('高功率工业泵电驱改造研究', self.html)
        for source in ('S7e3f4f2b06f63fe8 / B0003', 'S7e3f4f2b06f63fe8 / B0004', 'S7e3f4f2b06f63fe8 / B0006', 'S8ae50c84687b0709 / B0001'):
            self.assertIn(source, self.js)
        self.assertIn('/inno/dossier/?project=2019-s19', self.js)

    def test_082_research_process_and_report_boundary(self):
        for stage in ('拆解问题', '规划检索', '阅读证据', '交叉核对', '形成结论'):
            self.assertIn(stage, self.html + self.js)
        self.assertIn('研究结论草案 · 模拟整理', self.js)
        self.assertIn('待领域复核 · 非工程结论', self.js)
        self.assertIn('9项专利只有申报总数', self.js)
        self.assertIn('不能合并成统一比例', self.js)

    def test_082_playback_controls_are_real(self):
        for hook in ("$('live-pause').addEventListener", "$('live-replay').addEventListener", "$('live-close').addEventListener", 'clearTimeout(timer)', 'index = 0', "$('live-progress').value = index"):
            self.assertIn(hook, self.js)
        self.assertNotIn('fetch(', self.js)
        self.assertNotIn('setInterval(', self.js)
        self.assertNotIn("addEventListener('scroll'", self.js)

    def test_082_reduced_motion_shows_complete_case(self):
        self.assertIn("matchMedia('(prefers-reduced-motion: reduce)')", self.js)
        self.assertIn('while (index < events.length) renderOne();', self.js)
        self.assertIn('complete();', self.js)

    def test_082_responsive_and_shared_tokens(self):
        for width in ('1100px', '900px', '640px'):
            self.assertIn(width, self.css)
        self.assertIn('prefers-reduced-motion', self.css)
        self.assertIn('@media print', self.css)
        self.assertNotIn('#', self.css.replace('#fff', ''))

    def test_082_existing_workspace_and_builder_remain(self):
        original = (OUT / 'needs-workspace.js').read_text(encoding='utf-8')
        self.assertIn('model_calls: 0', original)
        self.assertIn('prepared_context_not_executed', original)
        builder = (ROOT / 'scripts/build_gooddesign_site.py').read_text(encoding='utf-8')
        self.assertIn("'needs-live-demo.css', 'needs-live-demo.js'", builder)
        self.assertEqual(self.html.count('data-gd-assistant-open'), 1)


if __name__ == '__main__':
    unittest.main()
