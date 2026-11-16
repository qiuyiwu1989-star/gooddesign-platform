# coding: utf-8
"""155 关于好设计对外展示页内容与真源契约。"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class AboutPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / 'scripts/info_pages_095.py').read_text(encoding='utf-8')
        cls.css = (ROOT / 'extensions/design-system/about-page.css').read_text(encoding='utf-8')

    def test_page_is_public_value_led_not_internal_architecture(self):
        for text in ('让真实创新', '成为下一次创新的', '从作品到知识，再到应用', '真实项目，真实设计取舍', '一套知识底座，不同的创新现场', '我们的内容原则', '下一次创新'):
            self.assertIn(text, self.source)
        self.assertNotIn('把真实创新经验，建设成可复用的公共能力', self.source)
        self.assertNotIn('<strong>8</strong><span>MCP只读工具</span>', self.source)

    def test_counts_and_projects_come_from_existing_sources(self):
        self.assertIn("projects = {p['id']: p for p in catalog(pp.LIB)}", self.source)
        self.assertIn('research_count = sum(1 for p in projects.values()', self.source)
        self.assertIn("method_library_catalog.catalog()['methods']", self.source)
        self.assertIn('app_count = len(APPS)', self.source)
        for project_id in ('2025-00', '2025-08', '2023-04', '2023-02'):
            self.assertIn(f"projects['{project_id}']", self.source)

    def test_real_application_routes_and_trust_boundaries(self):
        for route in ('href="/expo/"', 'href="/loop/"', 'href="/museum/"', 'href="/museum/#education"', 'href="/needs/"', 'href="/mcp/"'):
            self.assertIn(route, self.source)
        for text in ('授权试点', '不提供官方奖项申报或评审服务', '研究整理版不代表专家审核', 'AI分析不代表工程结论'):
            self.assertIn(text, self.source)

    def test_links_have_no_arrow_decoration(self):
        match = re.search(r"body = f'''(.*?)'''\n    return shell\('关于好设计'", self.source, re.S)
        self.assertIsNotNone(match)
        for text in re.findall(r'<a\b[^>]*>(.*?)</a>', match.group(1), re.S):
            self.assertFalse(re.search(r'[↗↘→←↔⇄↑↓]', text), text)

    def test_responsive_dark_motion_and_print_rules_exist(self):
        for width in (1100, 860, 600):
            self.assertIn(f'@media(max-width:{width}px)', self.css)
        self.assertIn('[data-theme="dark"]', self.css)
        self.assertIn('@media(prefers-reduced-motion:reduce)', self.css)
        self.assertIn('@media print', self.css)
        self.assertIn('description=', self.source)


if __name__ == '__main__':
    unittest.main()
