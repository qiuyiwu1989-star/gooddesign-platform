import re
import subprocess
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / 'extensions/design-system'


class Assets(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.refs = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if 'id' in values:
            self.ids.append(values['id'])
        for key in ('src', 'href'):
            if key in values:
                self.refs.append(values[key])


class DesignSystem069Tests(unittest.TestCase):
    def setUp(self):
        self.html = (DESIGN / 'index.html').read_text()
        self.css = (DESIGN / 'gooddesign.css').read_text()
        self.js = (DESIGN / 'preview.js').read_text()

    def test_069_local_assets_and_unique_ids(self):
        parser = Assets()
        parser.feed(self.html)
        self.assertEqual(len(parser.ids), len(set(parser.ids)))
        for ref in parser.refs:
            if ref.startswith(('../', 'gooddesign.css', 'preview.js')):
                self.assertTrue((DESIGN / ref).resolve().is_file(), ref)
        self.assertIn('../project-portal/covers/case-2025-00.jpg', self.html)
        for method in ('R48', 'R14', 'R17'):
            self.assertIn(f'../method-reader/icons/{method}.svg', self.html)

    def test_069_no_external_or_private_runtime_dependency(self):
        self.assertNotRegex(self.html, r'(?:src|href)="https?://')
        self.assertNotIn('/Volumes/', self.html + self.css + self.js)
        self.assertNotIn('fetch(', self.js)
        self.assertNotIn('XMLHttpRequest', self.js)

    def test_069_zaowuyun_foundation_and_component_contract(self):
        self.assertIn('../method-workbench/vendor/tokens.css', self.html)
        self.assertIn('../method-workbench/vendor/design-system.css', self.html)
        for token in ('--gd-page', '--gd-reading', '--gd-ok-text', '--gd-warn-text', '--gd-err-text'):
            self.assertIn(token, self.css)
        for selector in ('.gd-button--primary', '.gd-project', '.gd-method', '.gd-route', '.gd-drawer', '.gd-badge--ai'):
            self.assertIn(selector, self.css)
        self.assertEqual(self.css.count('{'), self.css.count('}'))

    def test_069_interaction_and_accessibility_hooks(self):
        for hook in ('showModal', "addEventListener('close'", 'aria-pressed', 'localStorage', 'pending_review', 'pending_confirmation'):
            self.assertIn(hook, self.js + self.html)
        for rule in ('prefers-reduced-motion', 'prefers-reduced-transparency', '@media print', '@media (max-width: 767px)'):
            self.assertIn(rule, self.css)
        self.assertIn('min-height: 44px', self.css)
        self.assertIn(':focus-visible', self.css)

    def test_069_javascript_syntax(self):
        result = subprocess.run(['node', '--check', str(DESIGN / 'preview.js')], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()
