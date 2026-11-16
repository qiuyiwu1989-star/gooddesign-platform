# coding: utf-8
"""159 大模型叙事与关于页关联契约。"""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ModelNarrative159Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = (ROOT / 'scripts/model_official_097.py').read_text()
        cls.about = (ROOT / 'scripts/info_pages_095.py').read_text()
        cls.css = (ROOT / 'extensions/design-system/about-page.css').read_text()

    def test_model_is_value_led_and_shorter(self):
        for marker in ('让真实项目经验，参与下一次创新', '为什么需要', '三层协同', '四种核心能力', '当前建设与边界'):
            self.assertIn(marker, self.model)
        self.assertNotIn('让真实创新经验，成为可理解、可迁移、可验证、可再创造的创新能力', self.model)
        self.assertNotIn('早期五层架构', self.model)

    def test_model_keeps_layers_capabilities_and_boundaries(self):
        for marker in ('data-model-layer="database"', 'data-model-layer="engine"', 'data-model-layer="applications"', 'data-capability="understand"', 'data-capability="connect"', 'data-capability="create"', 'data-capability="validate"'):
            self.assertIn(marker, self.model)
        self.assertIn('不宣称已经自主训练基础大模型', self.model)
        self.assertIn('AI 迁移建议不等于工程结论', self.model)

    def test_current_mcp_tool_count_is_12(self):
        self.assertIn('<dt>MCP 只读工具</dt><dd>12</dd>', self.model)
        self.assertNotIn('<dt>MCP 只读工具</dt><dd>8</dd>', self.model)

    def test_about_has_prominent_model_section_and_routes(self):
        for marker in ('class="about-section about-model"', '让项目、方法与智能研究', '01 · 项目档案数据库', '02 · 设计创新引擎', '03 · 应用能力', 'href="/model/"', 'href="/expo/"'):
            self.assertIn(marker, self.about)
        self.assertIn('.about-model{position:relative;padding:42px', self.css)

    def test_no_new_link_arrows(self):
        about_body = self.about.split('def about():', 1)[1].split('def model():', 1)[0]
        for arrow in ('↗', '↘', '→', '←', '↔', '⇄', '↑', '↓'):
            self.assertNotIn(arrow, self.model)
            self.assertNotIn(arrow, about_body)


if __name__ == '__main__':
    unittest.main()
