import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/inno-preview/gooddesign-site'
sys.path.insert(0, str(ROOT / 'scripts'))
from gooddesign_chrome import navigation


class MuseumAssets083Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = (OUT / 'inno/museum/index.html').read_text(encoding='utf-8')
        cls.original = (ROOT / 'original-app/public/index.html').read_text(encoding='utf-8')

    def test_083_real_museum_page_uses_legacy_asset_base(self):
        self.assertIn('<base href="/inno/legacy/">', self.page)
        self.assertIn('data-gd-family="inno-museum"', self.page)
        self.assertNotIn('<nav>\n  <a class="brand" href="index.html">', self.page)
        self.assertNotIn('<script src="copilot.js" defer></script>', self.page)

    def test_083_original_assets_exist_in_build(self):
        sources = set(re.findall(r'src=["\']((?:cases|assets)/[^"\']+)["\']', self.original))
        sources |= set(re.findall(r'url\(((?:cases|assets)/[^)]+)\)', self.original))
        self.assertGreaterEqual(len(sources), 11)
        for source in sorted(sources):
            self.assertTrue((OUT / source).is_file(), source)
        covers = list((ROOT / 'original-app/public/cases').glob('case-*.jpg'))
        self.assertEqual(len(covers), 98)
        for cover in covers:
            self.assertTrue((OUT / 'cases' / cover.name).is_file(), cover.name)

    def test_083_museum_is_in_main_navigation_and_active(self):
        html = navigation('museum')
        self.assertIn('href="/museum/" data-gd-nav="museum" aria-current="page"', html)
        self.assertNotIn('data-gd-nav="projects" aria-current="page"', html)
        home = navigation('projects')
        self.assertIn('href="/museum/" data-gd-nav="museum"', home)

    def test_083_preview_no_longer_aliases_to_wrong_root(self):
        preview = (ROOT / 'scripts/preview_gooddesign_site.py').read_text(encoding='utf-8')
        self.assertNotIn("'/museum/': '/index.html'", preview)

    def test_083_single_modern_assistant(self):
        self.assertEqual(self.page.count('data-gd-assistant-open'), 1)
        self.assertEqual(self.page.count('data-gd-assistant aria-labelledby'), 1)
        self.assertNotIn('id="gcFab"', self.page)


if __name__ == '__main__':
    unittest.main()
