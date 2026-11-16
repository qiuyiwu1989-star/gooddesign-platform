import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class HeavyExhibition164Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / 'output/inno-preview/gooddesign-site/hall.html').read_text()
        cls.css = (ROOT / 'extensions/design-system/heavy-exhibition.css').read_text()
        cls.js = (ROOT / 'extensions/design-system/heavy-exhibition.js').read_text()
        cls.data = json.loads((ROOT / 'original-app/public/exhibits-heavy.json').read_text())

    def test_three_cinematic_steps_per_project_and_one_evidence_link(self):
        self.assertEqual(self.html.count('class="heavy-step"'), 24)
        self.assertEqual(self.html.count('class="heavy-evidence-link"'), 8)
        self.assertNotIn('heavy-project-actions', self.html)
        self.assertNotIn('互动学习</a>', self.html)
        self.assertNotIn('拆解实验室</a>', self.html)
        for marker in ('真实任务', '设计局部', '策展收束'):
            self.assertIn(marker, self.html)
        for item in self.data['featured']:
            self.assertIn(f'/dossier/?project={item["slug"]}', self.html)

    def test_typography_returns_to_gooddesign_scale(self):
        self.assertIn('font-size:clamp(58px,7.2vw,96px)', self.css)
        self.assertIn('font-weight:600;line-height:1.04;letter-spacing:-.025em', self.css)
        self.assertIn('font-size:clamp(28px,2.6vw,36px)', self.css)
        self.assertNotIn('142px', self.css)
        self.assertNotIn('-.065em', self.css)
        self.assertNotIn('font-weight:520', self.css)
        self.assertNotIn('font-weight:450', self.css)

    def test_quick_browser_and_pure_presentation_controls(self):
        self.assertIn('id="heavy-browser"', self.html)
        self.assertEqual(self.html.count('class="heavy-browser-links"'), 1)
        self.assertEqual(self.html.count('data-heavy-browse'), 1)
        self.assertEqual(self.html.count('data-heavy-present'), 1)
        self.assertIn('aria-label="观展控制"', self.html)
        for marker in ('requestFullscreen', 'exitFullscreen', 'heavy-presenting', 'fullscreenchange', 'showModal'):
            self.assertIn(marker, self.js if marker != 'heavy-presenting' else self.css)

    def test_native_scroll_accessibility_and_print(self):
        self.assertIn('position:sticky', self.css)
        self.assertIn('IntersectionObserver', self.js)
        self.assertNotIn('scroll-snap', self.css)
        self.assertNotIn('preventDefault', self.js)
        self.assertIn('@media(prefers-reduced-motion:reduce)', self.css)
        self.assertIn('@media print', self.css)
        for arrow in ('↗', '↘', '→', '←', '↔', '⇄'):
            self.assertNotIn(arrow, self.html)


if __name__ == '__main__':
    unittest.main()
