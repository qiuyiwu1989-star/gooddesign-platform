import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class HeavyExhibition163Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / 'output/inno-preview/gooddesign-site/hall.html').read_text()
        cls.data = json.loads((ROOT / 'original-app/public/exhibits-heavy.json').read_text())
        cls.catalog = {row['id']: row for row in json.loads((ROOT / 'extensions/project-portal/catalog.json').read_text())}

    def test_single_special_exhibition_without_portal_or_chronicle(self):
        self.assertEqual(self.html.count('class="heavy-chapter"'), 4)
        self.assertEqual(self.html.count('class="heavy-project"'), 8)
        for marker in ('hall-relation', 'hall-interact', 'chronList', 'experience-grid', '十年编年', '互动乐园', '获奖作品是权威源头'):
            self.assertNotIn(marker, self.html)
        for marker in ('国之重器', '在极限中设计', '进入不可达之地', '组织高速与巨力', '设计能源心脏', '抵达深空任务'):
            self.assertIn(marker, self.html)

    def test_eight_real_projects_and_application_links(self):
        for item in self.data['featured']:
            slug = item['slug']
            self.assertIn(f'id="project-{slug}"', self.html)
            self.assertIn(self.catalog[slug]['name'], self.html)
            if slug == '2025-00':
                self.assertIn('2025-00-r1.webp', self.html)
                self.assertIn('data-cover-kind="scene_illustration"', self.html)
            else:
                self.assertIn('/inno/portal/' + self.catalog[slug]['cover'], self.html)
            self.assertIn(f'/dossier/?project={slug}', self.html)
            self.assertIn(item['maturity'], self.html)

    def test_shared_chrome_canonical_and_legacy_deep_links(self):
        self.assertEqual(self.html.count('data-gd-chrome="navigation"'), 1)
        self.assertEqual(self.html.count('data-gd-chrome="footer"'), 1)
        self.assertIn('rel="canonical" href="https://haoshejiguan.com/museum/hall"', self.html)
        self.assertIn('id="hall-heavy"', self.html)
        self.assertIn('id="hall-chron"', self.html)
        self.assertIn('href="/projects/"', self.html)
        self.assertIn('href="/needs/"', self.html)

    def test_accessible_responsive_reduced_motion_and_no_arrow_links(self):
        self.assertIn('aria-label="观展控制"', self.html)
        self.assertIn('aria-label="真实任务"', self.html)
        for arrow in ('↗', '↘', '→', '←', '↔', '⇄'):
            self.assertNotIn(arrow, self.html)
        css = (ROOT / 'extensions/design-system/heavy-exhibition.css').read_text()
        self.assertIn('@media(max-width:800px)', css)
        self.assertIn('@media(prefers-reduced-motion:reduce)', css)
        self.assertIn('@media print', css)
        js = (ROOT / 'extensions/design-system/heavy-exhibition.js').read_text()
        self.assertIn('IntersectionObserver', js)
        self.assertIn("prefers-reduced-motion: reduce", js)


if __name__ == '__main__':
    unittest.main()
