# coding: utf-8
"""123 检索质量确定性修复回归：匹配体空白归一化与查询词源语汇化预警。

修复均为确定性改动：归一化单调不减召回（旧命中不丢），预警只是标注。
不做语义召回，不改事实/评分/冻结产物。
"""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import innovation_knowledge as ik  # noqa: E402
import innovation_retrieval_v1 as retrieval  # noqa: E402
import innovation_engine_v1 as engine  # noqa: E402
import project_pipeline as pp  # noqa: E402
import research_workflow as rw  # noqa: E402

LIBRARY = ROOT / "04-知识库" / "项目库"
BASELINE = ROOT / "output" / "retrieval-eval-v1" / "baseline-20261105.json"


class MatchBodyNormalizationTests(unittest.TestCase):
    """ik.search 匹配体归一化：跨行与空白差异不再丢命中。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=pp.ROOT / "output")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.p = self.root / "P"
        self.p.mkdir()
        self.folder = self.p / "v"
        self.folder.mkdir()
        (self.p / "original").write_text("原始资料")
        (self.p / "chunks.json").write_text(json.dumps(
            [dict(id="B1", text="导向锥下部安装\n有缓冲器")], ensure_ascii=False))
        sha = pp.sha((self.p / "original").read_bytes())
        self.src = dict(sha256=sha, original="original", origin={})
        quote = "导向锥下部安装"
        e = dict(source_id="S1", source_sha256=sha, chunks_path="chunks.json",
                 chunks_sha256=pp.sha((self.p / "chunks.json").read_bytes()),
                 chunk_id="B1", quote=quote, quote_sha256=pp.sha(quote.encode()))
        self.data = dict(project_id="P", records=[dict(
            id="R1", entity="innovation", project_id="P", title="导向机构",
            cells=dict(mechanism=dict(
                value="导向锥下部安装\n有缓冲器，\t用于减振",
                value_state="known", content_nature="source_statement", evidence=e)))],
            interpretations=[])
        for name in ["档案.json", "manifest.json"]:
            (self.folder / name).write_text("{}")
        patches = [patch.object(pp, "project", return_value=self.p),
                   patch.object(rw, "current", return_value=dict(revision=1)),
                   patch.object(rw, "check_version", return_value=(self.folder, {})),
                   patch.object(rw, "dataset", side_effect=lambda *a, **kw: copy.deepcopy(self.data)),
                   patch.object(rw, "source", side_effect=lambda p, s: self.src)]
        for x in patches:
            x.start()
            self.addCleanup(x.stop)

    def search(self, terms):
        return ik.search(ik.build_index(self.root, "P"), functions=terms)

    def test_cross_line_query_hits(self):
        """基线未中情形闭合：含换行的查询命中跨行正文。"""
        out = self.search(["导向锥下部安装\n有缓冲器"])
        self.assertEqual(out["total_matches"], 1)
        self.assertEqual(out["matches"][0]["node"]["id"], "R1.mechanism")

    def test_whitespace_difference_both_directions(self):
        """查询无空白而正文跨行、查询带空格而正文无空格，双向都命中。"""
        self.assertEqual(self.search(["导向锥下部安装有缓冲器"])["total_matches"], 1)
        self.assertEqual(self.search(["导向锥 下部 安装 有缓冲器"])["total_matches"], 1)
        self.assertEqual(self.search(["有 缓冲器， 用于减振"])["total_matches"], 1)

    def test_monotonic_old_hits_and_unmatched_kept(self):
        """单调性：无空白旧查询行为不变；未命中仍如实报告。"""
        out = self.search(["导向锥下部安装", "毫无关联词"])
        self.assertEqual(out["total_matches"], 1)
        self.assertEqual(out["unmatched"][0]["term"], "毫无关联词")
        self.assertIn("空白归一化", out["matches"][0]["match_reason"])
        self.assertNotIn("score", out["matches"][0])


class RealLibraryMissedWindowTests(unittest.TestCase):
    """真实库定点复查：110 基线全部换行未中窗口修复后必须命中来源节点。"""

    def test_baseline_newline_misses_now_hit(self):
        baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
        missed = baseline["self_recall"]["missed"]
        self.assertEqual(len(missed), 15)
        self.assertTrue(all("\n" in m["term"] for m in missed))
        cache = {}
        for m in missed:
            pid = m["project_id"]
            if pid not in cache:
                cache[pid] = ik.build_index(LIBRARY, pid)
            hit = ik.search(cache[pid], functions=[m["term"]], limit=8)
            self.assertIn(m["node_id"],
                          [x["node"]["id"] for x in hit["matches"]],
                          (pid, m["node_id"]))


class QuerySourceVocabularyTests(unittest.TestCase):
    """build_queries 源语汇标注与零召回预警。"""

    def test_no_hints_gets_zero_recall_warning(self):
        qs = retrieval.build_queries([{"id": "F1", "verb_object": "识别对象并建立局部轨迹"}])
        self.assertEqual(qs[0]["query_terms"], ["识别对象并建立局部轨迹"])
        self.assertFalse(qs[0]["source_vocabulary"])
        self.assertIn("零召回", qs[0]["zero_recall_warning"])

    def test_hints_marked_source_vocabulary_without_warning(self):
        qs = retrieval.build_queries(
            [{"id": "F2", "verb_object": "约束切入与耗皮"}],
            {"F2": {"query_terms": ["仿形", "力位协同", "限深"]}})
        self.assertTrue(qs[0]["source_vocabulary"])
        self.assertNotIn("zero_recall_warning", qs[0])
        self.assertEqual(qs[0]["query_terms"], ["仿形", "力位协同", "限深"])

    def test_fallback_and_validation_unchanged(self):
        with self.assertRaises(ValueError):
            retrieval.build_queries([{"id": "F1", "verb_object": "  "}],
                                    {"F1": {"query_terms": ["  "]}})


class EngineRegressionTests(unittest.TestCase):
    """割胶引擎夹具：基线计数与禁推荐门禁不因检索标注而改变。"""

    def test_rubber_baseline_unchanged(self):
        fixtures = ROOT / "tests" / "fixtures" / "engine_v1"
        task = json.loads((fixtures / "rubber-task.json").read_text(encoding="utf-8"))
        proposal = json.loads((fixtures / "rubber-proposal.json").read_text(encoding="utf-8"))
        pack_ref = json.loads((ROOT / "04-知识库" / "项目档案标准-v1"
                               / "创新研究输出物标准-v1" / "examples"
                               / "rubber-research-pack.json").read_text(encoding="utf-8"))
        by_id = {e["project_id"]: e for e in pack_ref["case_retrieval"]}

        def retriever(library, case_library, queries):
            return [dict(project_id=e["project_id"], revision=e["revision"],
                         record_count=e["record_count"], read_sources=e["read_sources"],
                         errors=[], candidates=[])
                    for e in (by_id[c["project_id"]] for c in case_library)]

        result = engine.run(task, proposal, retriever=retriever)
        pack = result["pack"]
        self.assertEqual(len(pack["problem_brief"]["requirements"]), 15)
        self.assertEqual(len(pack["function_model"]["functions"]), 7)
        self.assertEqual(len(pack["concept_set"]["options"]), 28)
        self.assertEqual(len(pack["comparison"]["judgments"]), 60)
        self.assertEqual(pack["comparison"]["recommendations"], [])
        queries = result["engine_run"]["queries"]
        self.assertEqual(len(queries), 7)
        self.assertTrue(all(q["source_vocabulary"] is False for q in queries))
        self.assertTrue(all("zero_recall_warning" in q for q in queries))


if __name__ == "__main__":
    unittest.main()
