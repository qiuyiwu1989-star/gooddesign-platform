import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / 'extensions/design-system'


class HomeRefinement080Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (DESIGN / 'portal.html').read_text(encoding='utf-8')
        cls.css = (DESIGN / 'portal.css').read_text(encoding='utf-8')
        cls.js = (DESIGN / 'portal.js').read_text(encoding='utf-8')

    def test_080_real_content_and_dynamic_statistics(self):
        self.assertIn('id="stats-research"', self.html)
        self.assertIn("rows.filter(project => project.research).length", self.js)
        self.assertIn('fetchpriority="high"', self.html)
        self.assertIn('covers/case-2025-00.jpg', self.html)
        self.assertIn("fetch('/inno/catalog.json'", self.js)

    def test_080_discovery_contract_is_preserved(self):
        for element_id in ('hero-search', 'hero-query', 'filters', 'query', 'year', 'award', 'status', 'clear', 'empty-clear', 'previous', 'next'):
            self.assertIn(f'id="{element_id}"', self.html)
        for hook in ('pageSize = 12', 'restore()', 'render(true)', 'popstate', 'research', 'basic'):
            self.assertIn(hook, self.html + self.js)

    def test_080_clear_and_error_states_are_real(self):
        self.assertIn('id="clear" disabled', self.html)
        self.assertIn("$('clear').disabled = !Object.values(fields)", self.js)
        self.assertIn('项目目录加载失败', self.js)
        self.assertIn("$('empty-clear').addEventListener('click', () => location.reload()", self.js)

    def test_080_layout_refinement_and_legacy_reset(self):
        for selector in ('.gd-portal-hero-grid', '.gd-library-facts', '.gd-filter-panel', '.gd-project-card'):
            self.assertIn(selector, self.css)
        self.assertIn('min-height: 0;', self.css)
        for width in ('1100px', '767px', '480px', '359px'):
            self.assertIn(width, self.css)
        self.assertIn('prefers-reduced-motion', self.css)
        self.assertIn('prefers-reduced-transparency', self.css)
        self.assertIn('@media print', self.css)

    def test_080_links_and_copy_avoid_decoration(self):
        self.assertNotRegex(self.html, r'>[^<]*[→↗↑←↘↙][^<]*<')
        self.assertNotIn('—', self.html)
        self.assertNotIn('–', self.html)
        self.assertNotIn('window.addEventListener(\'scroll\'', self.js)
        self.assertNotIn('window.addEventListener("scroll"', self.js)

    def test_080_javascript_and_local_assets(self):
        result = subprocess.run(['node', '--check', str(DESIGN / 'portal.js')], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn('/Volumes/', self.html + self.css + self.js)
        self.assertNotIn('picsum.photos', self.html + self.js)
        self.assertNotIn('fonts.googleapis.com', self.html + self.css)


if __name__ == '__main__':
    unittest.main()
