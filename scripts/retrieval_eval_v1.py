# coding: utf-8
"""110 检索质量评估器：098 S3/S4 确定性检索的四个可复算指标。

1. census          库覆盖普查：多少项目可被引擎检索、节点与证据状态分布、三维覆盖。
2. self_recall     机械自召回：节点正文取逐字窗口，检索自身索引必须命中该节点，
                   验证逐字匹配与 limit 截断不丢应命中的节点。
3. paraphrase_gap  词表差距：人工撰写的改写查询（不含原文连续子串）对已知目标
                   节点的命中率；逐字对照组必须全中，证明未命中来自词表而非机械。
4. engine_reach    引擎触达：真实任务检索计划在全库的候选分布与维度覆盖。

评估器只读，不写库，不调用模型。评估集中的人工改写查询是评估数据，不是研究事实。
"""
import argparse
import hashlib
import json
from pathlib import Path

import innovation_knowledge as ik
import project_pipeline as pp
import research_workflow as rw

SCHEMA = "retrieval-eval-110-1"
DIMENSIONS = ["mechanism", "boundary", "verification"]
MAX_PROJECTS = 10000
SELF_WINDOW = 12
SELF_MIN_LEN = 4
SELF_PER_PROJECT = 5


def indexable_projects(library):
    """枚举可建索引的项目；失败项目如实记录原因，不中断。"""
    lib = Path(library)
    ok, errors = [], []
    for d in sorted(lib.iterdir()):
        if not d.is_dir():
            continue
        try:
            p = pp.project(lib, d.name)
            rev = "research-%06d" % rw.current(p)["revision"]
            rw.check_version(p, rev)
            ok.append((d.name, rev))
        except Exception as exc:
            errors.append({"project_id": d.name, "error": str(exc)[:200]})
    if len(ok) > MAX_PROJECTS:
        raise ValueError("项目数超出评估上限")
    return ok, errors


def census(library):
    """库覆盖普查：检索质量的上限是库覆盖，先量底数。"""
    ok, errors = indexable_projects(library)
    rows = []
    totals = {"nodes": 0, "frozen_traceable": 0, "legacy_reference_only": 0, "unverified": 0}
    dim_cover = {k: 0 for k in DIMENSIONS}
    full_cover = []
    for pid, rev in ok:
        idx = ik.build_index(library, pid, revision=rev)
        states = {}
        dims = set()
        for n in idx["nodes"]:
            states[n["evidence_state"]] = states.get(n["evidence_state"], 0) + 1
            dims.update(n["dimensions"])
        for k in DIMENSIONS:
            if k in dims:
                dim_cover[k] += 1
        if all(k in dims for k in DIMENSIONS):
            full_cover.append(pid)
        for k in totals:
            if k == "nodes":
                totals["nodes"] += len(idx["nodes"])
            else:
                totals[k] += states.get(k, 0)
        rows.append({"project_id": pid, "revision": rev, "nodes": len(idx["nodes"]),
                     "evidence_states": states, "dimensions": sorted(dims),
                     "gaps": len(idx["gaps"])})
    return {"indexable": len(ok), "not_indexable": len(errors),
            "errors": errors, "projects": rows, "totals": totals,
            "dimension_projects": dim_cover, "full_dimension_projects": sorted(full_cover)}


def _strings(value):
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [s for v in value for s in _strings(v)]
    if isinstance(value, dict):
        return [s for v in value.values() for s in _strings(v)]
    return []


def extract_window(node, window=SELF_WINDOW):
    """确定性取词：从节点最长字符串字段取一个正文窗口，不含 JSON 结构字符。"""
    texts = [t for t in _strings(node.get("value")) if len(t.strip()) >= SELF_MIN_LEN]
    if not texts:
        return None
    text = max(texts, key=len)
    if len(text) <= window:
        return text.strip()
    start = int(hashlib.sha256(node["id"].encode()).hexdigest(), 16) % (len(text) - window)
    return text[start:start + window]


def self_recall(library, projects, limit=8, per_project=SELF_PER_PROJECT):
    """机械自召回：逐字窗口必须召回来源节点自身。"""
    checked, missed, skipped = 0, [], 0
    for pid, rev in projects:
        idx = ik.build_index(library, pid, revision=rev)
        nodes = [n for n in idx["nodes"] if "mechanism" in n["dimensions"]]
        nodes.sort(key=lambda n: n["id"])
        step = max(1, len(nodes) // per_project) if nodes else 1
        for n in nodes[::step][:per_project]:
            term = extract_window(n)
            if not term:
                skipped += 1
                continue
            hit = ik.search(idx, functions=[term], limit=limit)
            checked += 1
            if n["id"] not in [m["node"]["id"] for m in hit["matches"]]:
                missed.append({"project_id": pid, "node_id": n["id"], "term": term,
                               "total_matches": hit["total_matches"]})
    return {"checked": checked, "skipped": skipped, "limit": limit,
            "recall": (checked - len(missed)) / checked if checked else None,
            "missed": missed}


def paraphrase_gap(library, eval_items, limit=8):
    """改写与逐字对照：同一目标节点，对照组必须全中，改写组如实记录命中与否。"""
    results = []
    for item in eval_items:
        idx = ik.build_index(library, item["project_id"])
        hit = ik.search(idx, functions=[item["query"]], limit=limit)
        found = [m for m in hit["matches"] if m["node"]["id"] == item["expected_node_id"]]
        results.append({"id": item["id"], "kind": item["kind"],
                        "project_id": item["project_id"], "query": item["query"],
                        "expected_node_id": item["expected_node_id"],
                        "hit": bool(found),
                        "rank": [m["node"]["id"] for m in hit["matches"]].index(item["expected_node_id"]) + 1 if found else None,
                        "total_matches": hit["total_matches"]})
    def rate(kind):
        rows = [r for r in results if r["kind"] == kind]
        return sum(1 for r in rows if r["hit"]) / len(rows) if rows else None
    return {"limit": limit, "items": results,
            "control_recall": rate("verbatim_control"),
            "paraphrase_recall": rate("paraphrase")}


def engine_reach(library, queries, limit=8):
    """引擎触达：真实检索计划在全库的候选分布与维度覆盖。"""
    ok, _ = indexable_projects(library)
    per_project = []
    total_candidates = 0
    unmatched = {}
    for pid, rev in ok:
        idx = ik.build_index(library, pid, revision=rev)
        dims = set()
        count = 0
        for q in queries:
            hit = ik.search(idx, functions=q["query_terms"], limit=limit)
            count += len(hit["matches"])
            for m in hit["matches"]:
                dims.update(m["node"]["dimensions"])
            for u in hit["unmatched"]:
                unmatched.setdefault(u["term"], set()).add(pid)
        if count:
            per_project.append({"project_id": pid, "candidates": count,
                                "dimensions": sorted(dims)})
            total_candidates += count
    full_dim = [p["project_id"] for p in per_project
                if all(k in p["dimensions"] for k in DIMENSIONS)]
    return {"projects_with_candidates": len(per_project),
            "total_candidates": total_candidates,
            "per_project": sorted(per_project, key=lambda r: (-r["candidates"], r["project_id"])),
            "full_dimension_projects": sorted(full_dim),
            "unmatched_terms": {t: sorted(ps) for t, ps in sorted(unmatched.items())}}


def run_all(library, eval_path, task_path=None, limit=8):
    library = str(library)
    report = {"schema": SCHEMA, "library": library, "limit": limit}
    report["census"] = census(library)
    ok, _ = indexable_projects(library)
    report["self_recall"] = self_recall(library, ok, limit=limit)
    eval_items = json.loads(Path(eval_path).read_text(encoding="utf-8"))["items"]
    report["paraphrase_gap"] = paraphrase_gap(library, eval_items, limit=limit)
    if task_path:
        import innovation_retrieval_v1 as ir
        task = json.loads(Path(task_path).read_text(encoding="utf-8"))
        queries = ir.build_queries(task["function_model"]["functions"])
        report["engine_reach"] = engine_reach(library, queries, limit=limit)
    return report


def main():
    ap = argparse.ArgumentParser(description="109 检索质量评估：普查/自召回/词表差距/引擎触达")
    ap.add_argument("--library", default="04-知识库/项目库")
    ap.add_argument("--eval", default="tests/fixtures/retrieval_eval_v1/paraphrase_set.json")
    ap.add_argument("--task", default=None, help="可选：含 function_model 的任务或提议 JSON，跑引擎触达")
    ap.add_argument("--limit", type=int, default=8)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    report = run_all(args.library, args.eval, task_path=args.task, limit=args.limit)
    text = json.dumps(report, ensure_ascii=False, indent=1)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        if out.exists():
            raise FileExistsError(f"评估报告不可覆盖: {out}")
        out.write_text(text + "\n", encoding="utf-8")
    c = report["census"]
    s = report["self_recall"]
    g = report["paraphrase_gap"]
    print(f"库覆盖: 可检索 {c['indexable']} / 不可检索 {c['not_indexable']}; "
          f"节点 {c['totals']['nodes']} (冻结 {c['totals']['frozen_traceable']}, "
          f"旧引用 {c['totals']['legacy_reference_only']}); "
          f"三维齐全项目 {len(c['full_dimension_projects'])}")
    print(f"机械自召回: {s['recall']:.4f} (检查 {s['checked']}, 未中 {len(s['missed'])})")
    print(f"词表差距: 逐字对照 {g['control_recall']:.4f}, 人工改写 {g['paraphrase_recall']:.4f}")
    if "engine_reach" in report:
        r = report["engine_reach"]
        print(f"引擎触达: 有候选项目 {r['projects_with_candidates']}, "
              f"候选总数 {r['total_candidates']}, 三维齐全 {len(r['full_dimension_projects'])}")


if __name__ == "__main__":
    main()
