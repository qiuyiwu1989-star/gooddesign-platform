# coding: utf-8
"""160 应用案例、互动学习与项目库统一契约。"""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import activate_museum_apps_release_157
import app_center_096
import build_application_registry


class Architecture160Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.apps = json.loads((ROOT / 'extensions/application-center/apps.json').read_text())
        cls.cases = json.loads((ROOT / 'extensions/application-center/cases.json').read_text())
        cls.page = app_center_096.render(cls.apps, cls.cases)
        cls.museum = (ROOT / 'output/inno-preview/gooddesign-site/inno/museum/index.html').read_text()
        cls.project = (ROOT / 'output/inno-preview/gooddesign-site/project/2015-02.html').read_text()
        cls.atom = (ROOT / 'output/inno-preview/gooddesign-site/atom/2015-02.html').read_text()
        cls.playground = (ROOT / 'output/inno-preview/gooddesign-site/playground.html').read_text()

    def test_xray_is_eighth_real_application_with_schema_and_case(self):
        self.assertEqual(len(self.apps), 12)
        self.assertIn('xray', [app['id'] for app in self.apps])
        xray = next(app for app in self.apps if app['id'] == 'xray')
        self.assertEqual(xray['route']['runtime'], '/museum/x-ray')
        self.assertEqual(xray['evidence']['case_ids'], ['x-ray'])
        registry = build_application_registry.build_registry()
        self.assertEqual(len(registry['apps']), 12)
        self.assertIn('x-ray', registry['cases'])
        self.assertIn('xray', self.page)
        self.assertIn('拆解一件国之重器', self.page)

    def test_project_and_atom_have_project_specific_learning_links(self):
        for text in (self.project, self.atom):
            self.assertIn('/museum/x-ray?slug=2015-02', text)
            self.assertIn('/museum/playground?slug=2015-02&tab=migrate', text)
            self.assertIn('继续探索这个项目', text)
        self.assertIn('museum-learning.css', self.project)
        self.assertIn('museum-learning.css', self.atom)

    def test_playground_is_honest_interactive_learning(self):
        self.assertIn('互动学习', self.playground)
        self.assertNotIn('互动乐园', self.playground)
        for route in ('/lab/', '/quest/', '/studio/', '/transfer/'):
            self.assertIn(f'href="{route}"', self.playground)
        for tab in ('experiment', 'questline', 'create', 'migrate'):
            self.assertIn(tab, self.playground)

    def test_case_page_is_not_second_archive(self):
        case_page = (ROOT / 'output/inno-preview/gooddesign-site/inno/cases/chang-e/index.html').read_text()
        self.assertIn('不是第二份项目档案', case_page)
        self.assertIn('项目事实以项目档案为准', case_page)
        self.assertIn('/dossier/?project=2025-00', case_page)

    def test_laureates_merge_preserves_routes_and_filters(self):
        build = (ROOT / 'scripts/build_gooddesign_site.py').read_text()
        nginx = (ROOT / 'deploy/nginx-inno-root.conf').read_text()
        self.assertIn('laureates.html\': \'href="/projects/', build)
        self.assertIn("'laureates.html': '/projects/'", build)
        self.assertIn('location = /museum/laureates', nginx)
        self.assertIn('return 301 /projects/?$gd_query', nginx)
        self.assertIn('award=$arg_level', nginx)
        self.assertIn('year=$arg_year', nginx)
        self.assertIn('q=$arg_slug', nginx)
        self.assertIn('set $gd_year_sep', nginx)
        self.assertNotIn('if ($gd_query', nginx)
        self.assertNotIn('playground|laureates|assistant', nginx)

    def test_release_replacement_does_not_mutate_hardlinked_previous_release(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / 'source.html'
            previous = root / 'previous.html'
            cloned = root / 'cloned.html'
            source.write_text('new')
            previous.write_text('old')
            os.link(previous, cloned)
            activate_museum_apps_release_157.replace_file(source, cloned)
            self.assertEqual(previous.read_text(), 'old')
            self.assertEqual(cloned.read_text(), 'new')
            nested = root / 'new-case' / 'index.html'
            activate_museum_apps_release_157.replace_file(source, nested)
            self.assertEqual(nested.read_text(), 'new')


if __name__ == '__main__':
    unittest.main()
