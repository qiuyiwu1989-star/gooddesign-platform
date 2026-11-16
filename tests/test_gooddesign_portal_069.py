import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / 'extensions/design-system'


class GoodDesignPortal069Tests(unittest.TestCase):
    def setUp(self):
        self.html = (DESIGN / 'portal.html').read_text()
        self.css = (DESIGN / 'portal.css').read_text()
        self.js = (DESIGN / 'portal.js').read_text()

    def test_069_real_catalog_and_cover(self):
        rows = json.loads((ROOT / 'extensions/project-portal/catalog.json').read_text())
        self.assertEqual(len(rows), 560)
        self.assertEqual(len({row['id'] for row in rows}), 560)
        self.assertEqual(sum(bool(row.get('cover')) for row in rows), 98)
        self.assertIn('../project-portal/covers/case-2025-00.jpg', self.html)
        self.assertIn("fetch('/inno/catalog.json'", self.js)
        self.assertIn('project_portal.catalog(pipeline.LIB)', (ROOT / 'scripts/preview_gooddesign_portal.py').read_text())

    def test_069_preserves_discovery_interactions(self):
        for hook in ('restore()', 'render(true)', 'popstate', 'previous', 'next', 'research', 'basic', 'pageSize = 12'):
            self.assertIn(hook, self.js + self.html)
        self.assertIn('aria-live="polite"', self.html)
        self.assertIn('研究整理版表示已形成版本化档案，不代表专家审核或工程验证', self.html)

    def test_069_responsive_and_javascript(self):
        for width in ('1100px', '767px', '480px'):
            self.assertIn(width, self.css)
        self.assertIn('prefers-reduced-motion', self.css)
        self.assertIn('@media print', self.css)
        result = subprocess.run(['node', '--check', str(DESIGN / 'portal.js')], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn('/Volumes/', self.html + self.css + self.js)


if __name__ == '__main__':
    unittest.main()
