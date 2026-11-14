# coding: utf-8
"""098 GD-CRE-0.1 引擎契约、负例与割胶固定夹具。

割胶基线：15 需求 / 7 功能 / 28 选项 / 4 组合 / 60 未知判断 / recommendations=[]。
夹具由 GDRP 标准示例生成，引擎输出与标准主数据逐段对齐，不另写事实。
"""
import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import innovation_engine_v1 as engine
import innovation_concepts_v1 as concepts
import innovation_retrieval_v1 as retrieval
import innovation_transfer_v1 as transfer

FIXTURES = ROOT / "tests" / "fixtures" / "engine_v1"
GDRP_PACK = ROOT / "04-知识库/项目档案标准-v1/创新研究输出物标准-v1/examples/rubber-research-pack.json"


def load_fixture():
    task = json.loads((FIXTURES / "rubber-task.json").read_text(encoding="utf-8"))
    proposal = json.loads((FIXTURES / "rubber-proposal.json").read_text(encoding="utf-8"))
    return task, proposal


def fixture_retriever(library, case_library, queries):
    """离线检索器：返回割胶真实检索记录，不访问库。"""
    pack = json.loads(GDRP_PACK.read_text(encoding="utf-8"))
    by_id = {e["project_id"]: e for e in pack["case_retrieval"]}
    results = []
    for case in case_library:
        e = by_id[case["project_id"]]
        results.append(dict(project_id=e["project_id"], revision=e["revision"],
                            record_count=e["record_count"], read_sources=e["read_sources"],
                            errors=[], candidates=[]))
    return results


def run_rubber():
    task, proposal = load_fixture()
    return engine.run(task, proposal, retriever=fixture_retriever), task, proposal


class EngineV1FixtureTests(unittest.TestCase):
    def test_rubber_baseline_counts_and_gate(self):
        result, _, _ = run_rubber()
        pack = result["pack"]
        self.assertEqual(len(pack["problem_brief"]["requirements"]), 15)
        self.assertEqual(len(pack["function_model"]["functions"]), 7)
        self.assertEqual(len(pack["concept_set"]["options"]), 28)
        self.assertEqual([c["id"] for c in pack["concept_set"]["combinations"]], ["C0", "C1", "C2", "C3"])
        judgments = pack["comparison"]["judgments"]
        self.assertEqual(len(judgments), 60)
        self.assertTrue(all(j["value"] == "unknown" for j in judgments))
        self.assertEqual(pack["comparison"]["recommendations"], [])
        self.assertEqual([g["id"] for g in pack["validation_plan"]["gates"]], ["G0", "G1", "G2", "G3", "G4"])
        self.assertEqual(pack["validation_plan"]["execution_status"], "planned")
        self.assertEqual(pack["execution"]["model_calls"]["status"], "failed")
        self.assertEqual(pack["execution"]["model_calls"]["count"], 0)

    def test_rubber_pack_parity_with_gdrp_example(self):
        """引擎产物与 GDRP 割胶标准主数据逐段一致（Host 散文摘要除外）。"""
        result, _, _ = run_rubber()
        pack = result["pack"]
        ref = json.loads(GDRP_PACK.read_text(encoding="utf-8"))
        for section in ("problem_brief", "function_model", "transfer_maps", "case_retrieval",
                        "domain_extension", "evidence"):
            self.assertEqual(pack[section], ref[section], section)
        self.assertEqual(pack["concept_set"]["options"], ref["concept_set"]["options"])
        self.assertEqual(pack["concept_set"]["combinations"], ref["concept_set"]["combinations"])
        # GDRP 示例的判据 hard=true 早于 098 的禁升格规则；引擎从需求派生（N04 等为 null），
        # 由 test_hard_null_and_proposed_preserved 锁定，此处比对其余字段。
        strip = lambda cs: [{k: v for k, v in c.items() if k != "hard"} for c in cs]
        self.assertEqual(strip(pack["comparison"]["criteria"]), strip(ref["comparison"]["criteria"]))
        self.assertEqual(pack["comparison"]["judgments"], ref["comparison"]["judgments"])
        self.assertEqual(pack["validation_plan"], ref["validation_plan"])
        self.assertEqual(pack["execution"]["source_versions"], ref["execution"]["source_versions"])
        self.assertEqual(pack["review"], ref["review"])

    def test_freeze_is_immutable_and_verifiable(self):
        result, task, _ = run_rubber()
        with tempfile.TemporaryDirectory() as tmp:
            out = engine.freeze(result, tmp, task, {"task": FIXTURES / "rubber-task.json"}, run_id="run-test")
            manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
            for name, sha in manifest["files"].items():
                self.assertEqual(hashlib.sha256((out / name).read_bytes()).hexdigest(), sha)
            with self.assertRaises(FileExistsError):
                engine.freeze(result, tmp, task, {}, run_id="run-test")


class EngineV1NegativeTests(unittest.TestCase):
    def test_hard_null_and_proposed_preserved(self):
        result, _, _ = run_rubber()
        reqs = {r["id"]: r for r in result["pack"]["problem_brief"]["requirements"]}
        self.assertIsNone(reqs["N04"]["hard"])
        self.assertIsNone(reqs["N15"]["hard"])
        self.assertTrue(all(r["status"] == "proposed" for r in reqs.values()))
        criteria = {c["id"]: c for c in result["pack"]["comparison"]["criteria"]}
        self.assertIsNone(criteria["K04"]["hard"])
        self.assertTrue(criteria["K01"]["hard"])

    def test_proposal_cannot_override_requirements(self):
        task, proposal = load_fixture()
        proposal["requirements"] = [{"id": "N01", "hard": True}]
        with self.assertRaises(ValueError):
            engine.run(task, proposal, retriever=fixture_retriever)

    def test_forbidden_keys_rejected(self):
        task, proposal = load_fixture()
        bad = copy.deepcopy(proposal)
        bad["transfer_maps"][0]["pass"] = "attempt"
        with self.assertRaises(ValueError):
            engine.run(task, bad, retriever=fixture_retriever)
        bad2 = copy.deepcopy(proposal)
        bad2["recommendations"] = ["C1"]
        with self.assertRaises(ValueError):
            engine.run(task, bad2, retriever=fixture_retriever)

    def test_transfer_map_must_state_not_transferable(self):
        task, proposal = load_fixture()
        bad = copy.deepcopy(proposal)
        del bad["transfer_maps"][0]["not_transferable"]
        with self.assertRaises(ValueError):
            engine.run(task, bad, retriever=fixture_retriever)
        bad2 = copy.deepcopy(proposal)
        bad2["transfer_maps"][0]["not_transferable"] = []
        with self.assertRaises(ValueError):
            engine.run(task, bad2, retriever=fixture_retriever)

    def test_research_only_and_excluded_statuses_accepted(self):
        task, proposal = load_fixture()
        statuses = {m["source_case"]: m["status"] for m in proposal["transfer_maps"]}
        self.assertEqual(statuses["2025-03"], "research_only")
        excluded = dict(proposal["transfer_maps"][0], status="excluded")
        validated = transfer.validate_transfer_map(excluded, ["2025-00"], ["F5"])
        self.assertEqual(validated["status"], "excluded")

    def test_model_assisted_rejected_and_failure_recorded(self):
        task, proposal = load_fixture()
        bad = copy.deepcopy(task)
        bad["execution_policy"] = {"mode": "model_assisted"}
        with self.assertRaises(ValueError):
            engine.run(bad, proposal, retriever=fixture_retriever)
        bad2 = copy.deepcopy(task)
        bad2["execution_policy"]["model_calls"] = {"status": "success", "count": 3}
        with self.assertRaises(ValueError):
            engine.run(bad2, proposal, retriever=fixture_retriever)

    def test_theoretical_space_not_claimed_as_researched(self):
        result, _, _ = run_rubber()
        note = result["pack"]["concept_set"]["unknowns"][-1]
        self.assertIn("16384", note)
        self.assertIn("不代表已研究", note)

    def test_c0_must_be_all_baseline(self):
        with self.assertRaises(ValueError):
            concepts.compose_concepts(
                [{"id": "F1", "verb_object": "x"}],
                [{"id": "F1O1", "function_id": "F1", "principle": "p", "conditions": ["c"]}],
                [{"id": "C0", "option_ids": ["F1O1"], "status": "unknown"}])

    def test_version_change_produces_new_run_not_overwrite(self):
        result, task, _ = run_rubber()
        with tempfile.TemporaryDirectory() as tmp:
            first = engine.freeze(result, tmp, task, {}, run_id="run-a")
            task2 = dict(task, revision="r2")
            result2 = engine.run(task2, json.loads((FIXTURES / "rubber-proposal.json").read_text(encoding="utf-8")),
                                 retriever=fixture_retriever)
            second = engine.freeze(result2, tmp, task2, {}, run_id="run-b")
            self.assertNotEqual(first, second)
            m1 = json.loads((first / "manifest.json").read_text(encoding="utf-8"))
            m2 = json.loads((second / "manifest.json").read_text(encoding="utf-8"))
            self.assertNotEqual(m1["files"]["research-pack.json"], m2["files"]["research-pack.json"])


class EngineV1RealRetrievalTests(unittest.TestCase):
    def test_real_retrieval_2025_00(self):
        """真实库集成：嫦娥研究版逐字召回，未命中如实报告，候选一律 unknown。"""
        library = ROOT / "04-知识库" / "项目库"
        queries = retrieval.build_queries(
            [{"id": "F2", "verb_object": "约束切入与耗皮"}],
            {"F2": {"query_terms": ["仿形", "力位协同", "限深"]}})
        results = retrieval.retrieve_with_knowledge(
            library, [{"project_id": "2025-00", "revision": "research-000001"}], queries)
        entry = results[0]
        self.assertEqual(entry["errors"], [])
        self.assertGreater(entry["record_count"], 0)
        tiered = retrieval.tier_candidates(results)
        self.assertTrue(all(c["status"] == "unknown" for c in tiered))


if __name__ == "__main__":
    unittest.main()
