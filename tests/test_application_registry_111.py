import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ApplicationRegistry111Tests(unittest.TestCase):
    def test_111_apps_manifest_matches_schema_and_keeps_manifest_apps(self):
        import sys
        sys.path.insert(0, str(ROOT / 'scripts'))
        import build_application_registry

        registry = build_application_registry.build_registry()
        self.assertEqual(registry['app_schema_version'], 'gd-app-0.1')
        self.assertEqual(len(registry['apps']), 8)
        self.assertEqual({app['schema_version'] for app in registry['apps']}, {'gd-app-0.1'})
        self.assertEqual({app['category'] for app in registry['apps']}, {'experience', 'innovation', 'access'})
        self.assertEqual(registry['boundaries']['mcp'], 'remote_read_only')

    def test_111_registry_maps_real_cases_and_agent_onboarding(self):
        import sys
        sys.path.insert(0, str(ROOT / 'scripts'))
        import build_application_registry

        registry = build_application_registry.build_registry()
        case_ids = set(registry['cases'])
        self.assertEqual(case_ids, {'chang-e', 'pump-079', 'rubber-tapping', 'mcp-research', 'yuhuan', 'x-ray'})
        for app in registry['apps']:
            self.assertTrue(app['evidence']['case_ids'])
            self.assertTrue(app['evidence']['must_show_boundary'])
            self.assertTrue(app['release']['requires'])
        self.assertIn('call_inno_capabilities', registry['agent_onboarding'])
        self.assertIn('validate_gdrp_package', registry['agent_onboarding'])

    def test_111_build_outputs_machine_readable_registry_and_schema(self):
        registry_path = ROOT / 'output/inno-preview/gooddesign-site/inno/apps/registry.json'
        schema_path = ROOT / 'output/inno-preview/gooddesign-site/inno/apps/application.schema.json'
        self.assertTrue(registry_path.exists())
        self.assertTrue(schema_path.exists())
        registry = json.loads(registry_path.read_text())
        self.assertEqual(registry['registry_schema_version'], 'gd-app-registry-0.1')
        self.assertEqual(len(registry['apps']), 8)

    def test_111_app_page_uses_manifest_runtime_route(self):
        text = (ROOT / 'output/inno-preview/gooddesign-site/inno/apps/index.html').read_text()
        self.assertIn('app.route.runtime', text)
        self.assertIn('"schema_version": "gd-app-0.1"', text)
        self.assertIn('"catalog": "/apps/"', text)


if __name__ == '__main__':
    unittest.main()
