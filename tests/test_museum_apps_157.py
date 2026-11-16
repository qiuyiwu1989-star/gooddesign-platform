# coding: utf-8
"""157 展馆与应用中心联合升级契约。"""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import app_center_096


class MuseumApps157Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.museum = (ROOT / 'output/inno-preview/gooddesign-site/inno/museum/index.html').read_text()
        cls.original = (ROOT / 'original-app/public/index.html').read_text()
        cls.apps = app_center_096.render(json.loads((ROOT / 'extensions/application-center/apps.json').read_text()), json.loads((ROOT / 'extensions/application-center/cases.json').read_text()))

    def test_museum_assets_use_legacy_base_and_real_exhibits(self):
        self.assertIn('<base href="/inno/legacy/">', self.museum)
        self.assertNotIn('<base href="/inno/legacy/">', self.original)
        self.assertEqual(self.museum.count('class="museum-exhibit"'), 6)
        for pid in ('2025-00', '2017-01', '2015-02', '2021-00', '2025-03', '2021-01'):
            self.assertIn(f'/dossier/?project={pid}', self.museum)
        for zone in ('industry', 'life', 'society'):
            self.assertIn(f'data-exhibit-filter="{zone}"', self.museum)
        self.assertIn('museum-exhibits', self.museum)

    def test_museum_visual_and_guide_boundaries(self):
        self.assertIn('.museum-cosmos,.hero-motion-control{display:none!important}', (ROOT / 'extensions/design-system/museum-polish.css').read_text())
        self.assertIn('找项目、读方法、核证据', self.museum)
        self.assertNotIn('点亮深度推理模式', self.museum)
        self.assertNotIn('四种顿悟', self.museum)

    def test_preview_matches_production_legacy_mapping(self):
        preview = (ROOT / 'scripts/preview_gooddesign_site.py').read_text()
        self.assertIn("elif parsed.path.startswith('/inno/legacy/'):", preview)
        self.assertIn("self.path = '/' + parsed.path[len('/inno/legacy/'):]", preview)

    def test_apps_layout_and_regional_feature(self):
        self.assertEqual(self.apps.count('class="app-card"'), 8)
        self.assertIn('grid-template-columns:repeat(3,minmax(0,1fr))', self.apps)
        self.assertIn('data-app-id="regional"', self.apps)
        self.assertIn('grid-column:1/-1', self.apps)
        self.assertIn('选择合适的应用', self.apps)

    def test_apps_empty_clear_url_and_dialog_contract(self):
        for marker in ('id="app-empty"', 'id="app-clear"', 'function applyFilters(updateUrl=true)', 'initialParams.get(\'kind\')', 'initialParams.get(\'q\')'):
            self.assertIn(marker, self.apps)
        for marker in ('aria-label="查看应用详情：', 'aria-haspopup="dialog"', 'id="app-sheet-close"', 'sheet.close()', 'lastCard.focus()'):
            self.assertIn(marker, self.apps)

    def test_no_new_arrow_links(self):
        for arrow in ('↗', '↘', '→', '←', '↔', '⇄', '↑', '↓'):
            self.assertNotIn(arrow, self.apps)


if __name__ == '__main__':
    unittest.main()
