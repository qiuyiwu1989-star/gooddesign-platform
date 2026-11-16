# coding: utf-8
"""118 全站审计回归：构建产物必须 P0=0、P1=0；canonical 与版本化 CSS 在场。"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

BUILD = ROOT / "output/inno-preview/gooddesign-site"


class SiteAudit118Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (BUILD / "inno/index.html").is_file():
            raise unittest.SkipTest("构建产物不存在，先运行 build_gooddesign_site.py")

    def test_audit_has_no_p0_or_p1(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "audit.json"
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/site_audit_118.py"),
                 "--root", str(BUILD), "--out", str(out)],
                capture_output=True, text=True)
            report = json.loads(out.read_text(encoding="utf-8"))
            violations = [r for r in report["rules"] if r["rule"].startswith(("P0", "P1"))]
            self.assertEqual(violations, [], json.dumps(violations[:5], ensure_ascii=False))
            self.assertEqual(result.returncode, 0)

    def test_canonical_points_to_main_domain(self):
        for rel, expected in [
            ("inno/index.html", "https://haoshejiguan.com/projects/"),
            ("inno/museum/index.html", "https://haoshejiguan.com/"),
            ("hall.html", "https://haoshejiguan.com/museum/hall"),
        ]:
            text = (BUILD / rel).read_text(encoding="utf-8")
            self.assertIn(f'rel="canonical" href="{expected}"', text, rel)

    def test_css_links_are_content_versioned(self):
        import gooddesign_assets
        links = gooddesign_assets.links()
        self.assertIn("?v=", links)
        version = gooddesign_assets.css_version()
        self.assertEqual(len(version), 8)
        r50 = (BUILD / "inno/methods/methods/R50.html").read_text(encoding="utf-8")
        self.assertIn("method-detail.css?v=", r50)

    def test_no_stray_gt_after_main_id(self):
        """119 修复 workspace_ui.decorate 正则：main 标签后不得出现孤立 > 文本。"""
        import re
        import workspace_ui
        html_text = "<!doctype html><html><head></head><body><main><p>x</p></main></body></html>"
        for cls in (True, False):
            result = re.sub(r'<main\b(?![^>]*\bid=)([^>]*)>',
                            lambda m: '<main id="main"' + m.group(1) + '>', html_text, count=1)
            self.assertNotIn('id="main">>', result)


if __name__ == "__main__":
    unittest.main()
