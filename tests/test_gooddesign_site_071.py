import json
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/inno-preview/gooddesign-site'


class GoodDesignSite071Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = sorted(path for path in OUT.rglob('*.html') if path.name != 'site-index.html')
        cls.report = json.loads((ROOT / 'output/inno-preview/gooddesign-site-report.json').read_text())

    def test_071_full_inventory_and_assets(self):
        self.assertEqual(len(self.pages), 1247)
        self.assertEqual(self.report['html_pages'], 1247)
        for name in ('tokens.css', 'design-system.css', 'gooddesign.css', 'site-bridge.css'):
            self.assertTrue((OUT / 'inno/portal' / name).is_file(), name)
        for path in self.pages:
            text = path.read_text()
            self.assertEqual(text.count('gooddesign.css'), 1, str(path))
            self.assertIn('data-theme=', text, str(path))
            self.assertIn('data-gd-family=', text, str(path))
            self.assertNotIn('/Volumes/', text, str(path))

    def test_071_page_families_cover_legacy_and_inno(self):
        groups = self.report['groups']
        self.assertEqual(groups['project'], 560)
        self.assertEqual(groups['atom'], 561)
        self.assertEqual(groups['inno-methods'], 67)
        self.assertEqual(groups['lesson'], 12)
        self.assertEqual(groups['industry-demo'], 5)
        self.assertEqual(groups['interactive-exhibit'], 4)
        for route in ('index.html', 'project/2025-00.html', 'atom/2025-00.html', 'learn.html', 'playground.html', 'teacher-workbench/index.html', 'industry-demo/workspace.html', 'inno/index.html', 'inno/methods/index.html', 'inno/methods/methods/R48.html', 'inno/needs/index.html', 'inno/needs-v2/index.html', 'inno/report/index.html', 'inno/mcp/index.html'):
            self.assertTrue((OUT / route).is_file(), route)
        self.assertIn('Bread<wbr>Trucks<wbr>For<wbr>Plateau<wbr>And<wbr>Cold<wbr>Regions', (OUT / 'project/2020-c33.html').read_text())

    def test_071_build_is_deterministic_and_private_safe(self):
        self.assertEqual(self.report['status'], 'built_not_deployed')
        self.assertTrue(self.report['production_changed'] is False)
        self.assertTrue(self.report['private_sources_exported'] is False)
        self.assertFalse((OUT / '01-原始资料').exists())
        self.assertFalse((OUT / '99-历史项目快照').exists())


if __name__ == '__main__':
    unittest.main()
