"""RC-01/RC-02 推理画布静态回归：文件存在、引用正确、数据完整、无破折号字符。"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXT = os.path.join(ROOT, "extensions", "reasoning-canvas")


class TestReasoningCanvasFiles(unittest.TestCase):
    def test_files_exist(self):
        for name in ["index.html", "data.js", "state.js", "reasoning-canvas.js", "reasoning-canvas.css", "README.md"]:
            self.assertTrue(os.path.isfile(os.path.join(EXT, name)), name)

    def test_html_uses_gooddesign_layers(self):
        html = open(os.path.join(EXT, "index.html"), encoding="utf-8").read()
        self.assertIn("../method-workbench/vendor/tokens.css", html)
        self.assertIn("../method-workbench/vendor/design-system.css", html)
        self.assertIn("../design-system/gooddesign.css", html)
        self.assertIn('id="main"', html)
        self.assertIn('data-zw-mode="product"', html)

    def test_no_em_dash_in_visible_sources(self):
        for name in ["index.html", "data.js", "state.js", "reasoning-canvas.js", "reasoning-canvas.css"]:
            text = open(os.path.join(EXT, name), encoding="utf-8").read()
            self.assertNotRegex(text, "[—–]", name)

    def test_data_completeness(self):
        data = open(os.path.join(EXT, "data.js"), encoding="utf-8").read()
        self.assertEqual(len(re.findall(r"id:'n\d'", data)), 7, "七节点")
        for cid in ["A", "B", "C", "D", "E", "F"]:
            self.assertIn(f"id:'{cid}'", data)
        for evid in ["K1", "K2", "K3", "S2", "S4", "S5", "S6", "S8"]:
            self.assertIn(f"id:'{evid}'", data)

    def test_state_machine_has_review_ripple(self):
        js = open(os.path.join(EXT, "state.js"), encoding="utf-8").read()
        self.assertIn("review", js)
        self.assertIn("reopen", js)
        self.assertIn("confirmReview", js)

    def test_state_logic_separated_from_view(self):
        view = open(os.path.join(EXT, "reasoning-canvas.js"), encoding="utf-8").read()
        self.assertIn("RC_State", view)
        self.assertNotIn("localStorage.setItem(LS_KEY", view, "视图层不直接写画布研究状态")

    def test_flow_engine_present(self):
        html = open(os.path.join(EXT, "index.html"), encoding="utf-8").read()
        self.assertIn('id="rc-flow-run"', html)
        self.assertIn('id="rc-roster"', html)
        self.assertIn('id="rc-feed"', html)
        js = open(os.path.join(EXT, "reasoning-canvas.js"), encoding="utf-8").read()
        for token in ["AGENTS", "spawnPlan", "runFlow", "buildFlow", "renderRoster"]:
            self.assertIn(token, js)
        state = open(os.path.join(EXT, "state.js"), encoding="utf-8").read()
        self.assertIn("recordFlowRun", state)
        self.assertIn("markFlowDirty", state)
        self.assertIn("推理运行记录", state)


if __name__ == "__main__":
    unittest.main()
