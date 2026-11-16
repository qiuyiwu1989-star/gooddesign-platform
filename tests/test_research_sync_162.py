import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import activate_research_sync_162


class ResearchSync162Tests(unittest.TestCase):
    def test_public_snapshot_counts_and_boundaries(self):
        manifest = json.loads((ROOT / 'output/research-sync-162/release-manifest.json').read_text())
        self.assertEqual(manifest['catalog_count'], 560)
        self.assertEqual(manifest['research_project_count'], 103)
        self.assertEqual(manifest['research_version_count'], 221)
        self.assertEqual(len(manifest['research_projects']), 103)
        self.assertEqual(len(manifest['files']), 7286)
        self.assertFalse(manifest['private_originals_in_research_snapshot'])
        for relative in manifest['files']:
            self.assertNotIn('private-sources', Path(relative).parts)
            self.assertNotIn('__pycache__', Path(relative).parts)

    def test_replace_file_does_not_mutate_previous_snapshot(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / 'source.json'
            previous = root / 'previous.json'
            cloned = root / 'nested/cloned.json'
            source.write_text('new')
            source.chmod(0o600)
            previous.write_text('old')
            cloned.parent.mkdir()
            os.link(previous, cloned)
            activate_research_sync_162.replace_file(source, cloned)
            self.assertEqual(previous.read_text(), 'old')
            self.assertEqual(cloned.read_text(), 'new')
            self.assertEqual(cloned.stat().st_mode & 0o777, 0o644)

    def test_activation_skips_identical_files_and_checks_all_public_services(self):
        source = (ROOT / 'scripts/activate_research_sync_162.py').read_text()
        self.assertIn('if target.is_file() and target.stat().st_size == record', source)
        self.assertIn("'changed_files': changed_files", source)
        self.assertIn("subprocess.run(['systemctl', 'restart', 'innovation-readonly', 'innovation-mcp']", source)
        self.assertIn("'research-000008' in dossier", source)


if __name__ == '__main__':
    unittest.main()
