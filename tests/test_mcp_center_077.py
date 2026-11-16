import collections
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import innovation_gateway_page


class McpCenter077Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = innovation_gateway_page.page()
        cls.script = (ROOT / 'extensions/project-portal/mcp-guide.js').read_text()
        cls.css = (ROOT / 'extensions/project-portal/mcp-center.css').read_text()

    def test_077_tool_catalog_matches_remote_contract(self):
        expected = {'inno_capabilities', 'inno_search_projects', 'inno_search_methods', 'inno_read_project', 'inno_read_method', 'inno_search_fields', 'inno_read_evidence', 'inno_prepare_research'}
        self.assertEqual({row['name'] for row in innovation_gateway_page.TOOLS}, expected)
        counts = collections.Counter(row['group'] for row in innovation_gateway_page.TOOLS)
        self.assertEqual(counts, {'discovery': 3, 'read': 4, 'prepare': 1})
        self.assertNotIn('inno_start_research', self.html)
        self.assertNotIn('inno_read_research', self.html)

    def test_077_layout_regions_and_original_features(self):
        for anchor in ('id="setup"', 'id="tools"', 'id="workflow"', 'id="start"', 'id="troubleshooting"'):
            self.assertIn(anchor, self.html)
        for feature in ('id="mcp-token"', 'id="mcp-config"', 'data-format="json"', 'data-format="toml"', 'id="copy-config"', 'id="copy-prompt"', 'id="copy-endpoint"'):
            self.assertIn(feature, self.html)
        self.assertIn('远程只读', self.html)
        self.assertNotIn('服务正常', self.html)
        self.assertNotIn('已连接', self.html)

    def test_077_secret_handling_and_copy_fallback(self):
        for token in ('<YOUR_PRIVATE_MCP_KEY>', 'GOODDESIGN_MCP_TOKEN', 'pagehide', 'token.value = \'\'', 'copyDialogText.value = \'\'', 'copyDialog.showModal()', 'copyDialogText.select()'):
            self.assertIn(token, self.script)
        self.assertNotIn('localStorage', self.script)
        self.assertNotIn('sessionStorage', self.script)
        self.assertNotIn('fetch(', self.script)
        self.assertIn('config(\'<YOUR_PRIVATE_MCP_KEY>\')', self.script)

    def test_077_tool_search_filters_and_accessibility(self):
        for token in ('data-tool-filter', 'tool-search', 'tool-count', 'tool-empty', 'aria-live="polite"', 'copy-dialog-title'):
            self.assertIn(token, self.html + self.script)
        for rule in ('@media(max-width:700px)', '@media(prefers-reduced-motion:reduce)', '@media print'):
            self.assertIn(rule, self.css)

    def test_077_build_includes_css_and_no_link_arrows(self):
        builder = (ROOT / 'scripts/build_gooddesign_site.py').read_text()
        self.assertIn("'mcp-center.css'", builder)
        built = ROOT / 'output/inno-preview/gooddesign-site/inno/mcp/index.html'
        if built.exists():
            text = built.read_text()
            self.assertIn('/inno/portal/mcp-center.css', text)
            for arrow in ('↗', '↘', '→', '←', '↔', '⇄', '↑', '↓'):
                self.assertNotIn(arrow, text)


if __name__ == '__main__':
    unittest.main()
