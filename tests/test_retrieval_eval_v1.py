# coding: utf-8
"""110 检索质量评估回归：评估器本身可复算，基线发现被锁定。

基线（2026-11-05，库 research 版本 103 项目）：
- 逐字对照召回 100%，人工改写召回 0%，词表差距是完全缺口。
- 机械自召回 95.3%，全部未中窗口含换行符（json.dumps 转义所致）。
- 割胶功能抽象词全库触达为 0：S3 查询词必须来自源语汇，不能只用功能抽象词。
"""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import retrieval_eval_v1 as ev  # noqa: E402

LIBRARY = ROOT / "04-知识库/项目库"
EVAL_SET = ROOT / "tests/fixtures/retrieval_eval_v1/paraphrase_set.json"
RUBBER_PROPOSAL = ROOT / "tests/fixtures/engine_v1/rubber-proposal.json"


class RetrievalEvalFixtureTests(unittest.TestCase):
    def test_fixture_self_consistent(self):
        """评估集自洽：改写不含原文子串，对照为逐字窗口，目标节点存在。"""
        import innovation_knowledge as ik
        items = json.loads(EVAL_SET.read_text(encoding="utf-8"))["items"]
        self.assertEqual(len([i for i in items if i["kind"] == "paraphrase"]), 16)
        self.assertEqual(len([i for i in items if i["kind"] == "verbatim_control"]), 16)
        cache = {}
        for it in items:
            pid = it["project_id"]
            if pid not in cache:
                cache[pid] = {n["id"]: n for n in ik.build_index(LIBRARY, pid)["nodes"]}
            node = cache[pid].get(it["expected_node_id"])
            self.assertIsNotNone(node, it["id"])
            body = (json.dumps(node["value"], ensure_ascii=False) + " "
                    + str(node.get("conditions") or "") + " "
                    + str(node.get("limitations") or "")).casefold()
            if it["kind"] == "paraphrase":
                self.assertNotIn(it["query"].casefold(), body, it["id"])
            else:
                self.assertIn(it["query"].casefold(), body, it["id"])


class RetrievalEvalMetricsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = ev.run_all(LIBRARY, EVAL_SET, task_path=RUBBER_PROPOSAL)

    def test_census_baseline(self):
        c = self.report["census"]
        self.assertGreaterEqual(c["indexable"], 100)
        self.assertGreater(c["not_indexable"], 0)
        self.assertGreaterEqual(c["totals"]["nodes"], 1000)
        self.assertGreaterEqual(len(c["full_dimension_projects"]), 20)
        states = c["totals"]
        self.assertEqual(states.get("unverified", 0), 0)

    def test_control_recall_is_perfect(self):
        """逐字对照必须全中：未中即机械回归，不是词表问题。"""
        g = self.report["paraphrase_gap"]
        self.assertEqual(g["control_recall"], 1.0)
        for item in g["items"]:
            if item["kind"] == "verbatim_control":
                self.assertTrue(item["hit"], item["id"])

    def test_paraphrase_gap_is_recorded(self):
        """改写召回基线为 0；放宽到 0.25 以内容忍库增长，超出须重估。"""
        g = self.report["paraphrase_gap"]
        self.assertLessEqual(g["paraphrase_recall"], 0.25)

    def test_self_recall_misses_are_newline_only(self):
        """自召回未中全部源于换行转义；其他原因的未中即为新回归。"""
        s = self.report["self_recall"]
        self.assertGreaterEqual(s["recall"], 0.9)
        for m in s["missed"]:
            self.assertIn("\n", m["term"], m)

    def test_engine_reach_zero_with_abstract_verbs(self):
        """割胶功能抽象词（无源语汇 hints）全库零触达，未命中如实记录。"""
        r = self.report["engine_reach"]
        self.assertEqual(r["projects_with_candidates"], 0)
        self.assertEqual(r["total_candidates"], 0)
        self.assertIn("识别对象并建立局部轨迹", r["unmatched_terms"])
        self.assertIn("完成受控切削", r["unmatched_terms"])

    def test_report_is_deterministic(self):
        r2 = ev.run_all(LIBRARY, EVAL_SET, task_path=RUBBER_PROPOSAL)
        self.assertEqual(self.report, r2)


if __name__ == "__main__":
    unittest.main()
