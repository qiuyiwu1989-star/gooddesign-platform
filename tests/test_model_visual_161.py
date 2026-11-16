# coding: utf-8
"""161 大模型架构与真实应用可视化契约。"""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ModelVisual161Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / 'scripts/model_official_097.py').read_text()
        cls.css = (ROOT / 'extensions/design-system/model-official.css').read_text()

    def test_architecture_svg_has_three_layers_and_two_loops(self):
        for marker in ('mo-architecture-map', '项目档案数据库', '设计创新引擎', '公众与展馆', '科技教育', '企业创新研究', '地方产业与 Agent', '证据可信环', '验证生长环', 'mo-map-title', 'mo-map-desc'):
            self.assertIn(marker, self.html)
        self.assertIn('viewBox="0 0 1200 720"', self.html)
        self.assertIn('marker-end="url(#mo-arrowhead)"', self.html)

    def test_capability_workbench_is_not_pills(self):
        self.assertIn('grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;counter-reset:mo-capability', self.css)
        self.assertIn('counter-increment:mo-capability', self.css)
        self.assertNotIn('border-radius:999px;font-size:13px', self.css)

    def test_application_map_has_one_source_and_four_real_paths(self):
        for marker in ('mo-app-source', '一个嫦娥项目', '公众与展馆', '科技教育', '企业与研究', '地方产业与 Agent', '主题展览 · 项目故事', '活动单 · 探究任务', '需求简报 · 验证计划', '产业报告 · 研究上下文'):
            self.assertIn(marker, self.html)
        for route in ('/museum/', '/museum/#education', '/needs/', '/expo/', '/cases/chang-e/'):
            self.assertIn(f'href="{route}"', self.html)

    def test_responsive_accessible_and_print_rules(self):
        self.assertIn('aria-labelledby="mo-map-title mo-map-desc"', self.html)
        self.assertIn('@media(max-width:720px){.mo-architecture-map svg{min-width:860px}', self.css)
        self.assertIn('@media print{.mo-architecture-map{break-inside:avoid}', self.css)


if __name__ == '__main__':
    unittest.main()
