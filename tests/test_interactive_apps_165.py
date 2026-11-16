import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_application_registry


class InteractiveApps165Tests(unittest.TestCase):
    def test_four_new_manifests_and_twelve_app_registry(self):
        registry = build_application_registry.build_registry()
        apps = registry['apps']
        self.assertEqual(len(apps), 12)
        by_id = {app['id']: app for app in apps}
        for app_id, route in (('lab', '/lab/'), ('quest', '/quest/'), ('studio', '/studio/'), ('transfer', '/transfer/')):
            self.assertEqual(by_id[app_id]['route']['runtime'], route)
            self.assertEqual(by_id[app_id]['capabilities']['writes'], 'client_local')
            self.assertFalse(by_id[app_id]['permissions']['requires_login'])
        self.assertEqual(sum(app['category'] == 'experience' for app in apps), 6)
        self.assertEqual(sum(app['category'] == 'innovation' for app in apps), 4)

    def test_four_routes_and_playground_migration(self):
        for app in ('lab', 'quest', 'studio', 'transfer'):
            page = (ROOT / f'output/inno-preview/gooddesign-site/inno/{app}/index.html')
            self.assertTrue(page.is_file(), app)
            text = page.read_text()
            self.assertIn('data-gd-chrome="navigation"', text)
            self.assertNotIn('AI 裁判', text)
        playground = (ROOT / 'output/inno-preview/gooddesign-site/playground.html').read_text()
        self.assertEqual(playground.count('class="ia-app-choices"'), 1)
        for app in ('lab', 'quest', 'studio', 'transfer'):
            self.assertIn(f'href="/{app}/"', playground)
        for tab in ('experiment', 'questline', 'create', 'migrate'):
            self.assertIn(tab, playground)

    def test_interaction_contracts_use_real_data_and_local_storage(self):
        scripts = {name: (ROOT / f'extensions/design-system/{name}.js').read_text() for name in ('lab', 'quest', 'studio', 'transfer')}
        self.assertIn('gd-lab-runs-v1', scripts['lab'])
        self.assertIn('gd-quest-progress-v1', scripts['quest'])
        self.assertIn('gd-studio-draft-v1', scripts['studio'])
        self.assertIn('requestAnimationFrame', scripts['lab'])
        self.assertIn('toDataURL', scripts['studio'])
        self.assertIn('PLAY_DATA.migrate', scripts['transfer'])
        for name, source in scripts.items():
            self.assertNotIn('AI裁判', source)
            self.assertNotIn('fetch(', source)


if __name__ == '__main__':
    unittest.main()
