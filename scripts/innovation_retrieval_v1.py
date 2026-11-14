# coding: utf-8
"""098 S3/S4：检索计划、混合召回、机制多样化与候选分层。

V1 只实现 literal 与 structural 两路召回（复用 innovation_knowledge 的只读
冻结证据索引与逐字检索）；semantic 召回未启用，启用时只能扩展召回，不能新增事实。
检索候选一律以 unknown 状态进入后续流程，命中不代表可迁移。
"""
import innovation_knowledge as ik

REQUIRED_DIMENSIONS = ["mechanism", "boundary", "verification"]
MAX_PER_FUNCTION = 8

TIER_ORDER = {"frozen_traceable": 0, "legacy_reference_only": 1, "unverified": 2}


def build_queries(functions, query_hints=None):
    """按功能生成检索计划。术语只来自功能定义与人工提示，不按行业或企业名称检索。

    123：无人工 query_hints 的功能以功能抽象词回退，并标注 source_vocabulary=false
    与零召回预警（110 基线：抽象词全库零触达）；预警是标注，不改变检索行为。
    """
    hints = query_hints or {}
    queries = []
    for f in functions:
        hint = hints.get(f["id"], {})
        hinted = bool(hint.get("query_terms"))
        terms = [t.strip() for t in (hint.get("query_terms") or [f["verb_object"]]) if t.strip()]
        if not terms:
            raise ValueError(f"{f['id']} 没有可用检索词")
        q = {
            "function_id": f["id"],
            "intent": hint.get("intent") or f"寻找与「{f['verb_object']}」相关的不同处理机制",
            "query_terms": terms,
            "source_vocabulary": hinted,
            "required_dimensions": list(REQUIRED_DIMENSIONS),
            "exclude_as_proof": hint.get("exclude_as_proof") or ["源项目参数、阈值或控制增益直接成为目标规格"],
        }
        if not hinted:
            q["zero_recall_warning"] = (
                "该功能无人工源语汇 query_hints，直接使用功能抽象词检索；110 评估基线显示"
                "功能抽象词全库零触达，预期零召回。请先补充源语汇 query_hints 或词汇映射表，"
                "不要把零结果解读为库中没有相关知识")
        queries.append(q)
    return queries


def retrieve_with_knowledge(library, case_library, queries, limit=MAX_PER_FUNCTION):
    """默认检索器：对指定项目与冻结研究版本做逐字召回。

    只读，不写库，不调用模型。每个项目独立记录错误，单项目失败不中断整体。
    """
    results = []
    for case in case_library:
        pid, rev = case["project_id"], case["revision"]
        entry = {"project_id": pid, "revision": rev, "record_count": 0,
                 "read_sources": [], "errors": [], "candidates": []}
        try:
            index = ik.build_index(library, pid, revision=rev)
            entry["record_count"] = len(index["nodes"])
            sources = set()
            for q in queries:
                hit = ik.search(index, functions=q["query_terms"], limit=limit)
                for m in hit["matches"]:
                    node = m["node"]
                    sources.update(node.get("source_ids", []))
                    entry["candidates"].append({
                        "function_id": q["function_id"],
                        "node_id": node["id"],
                        "title": node.get("title", node["id"]),
                        "dimensions": node["dimensions"],
                        "evidence_state": node["evidence_state"],
                        "hits": m["hits"],
                    })
            entry["read_sources"] = sorted(sources)
        except Exception as exc:  # 单项目失败不中断，如实记录
            entry["errors"].append(str(exc))
        results.append(entry)
    return results


def tier_candidates(retrieval_results):
    """候选分层：版本可定位优先、逐字命中其次、机制多样化（不同项目），
    不使用未校准的单一相似度分数。所有候选初始状态都是 unknown。"""
    tiered = []
    seen = set()
    for entry in retrieval_results:
        for cand in entry["candidates"]:
            key = (entry["project_id"], cand["node_id"], cand["function_id"])
            if key in seen:
                continue
            seen.add(key)
            tiered.append({
                "project_id": entry["project_id"],
                "revision": entry["revision"],
                "function_id": cand["function_id"],
                "node_id": cand["node_id"],
                "title": cand["title"],
                "dimensions": cand["dimensions"],
                "evidence_state": cand["evidence_state"],
                "tier": TIER_ORDER.get(cand["evidence_state"], 3),
                "status": "unknown",
                "note": "逐字命中仅表示可定位类比候选，不证明可迁移；需机制映射与目标验证",
            })
    tiered.sort(key=lambda c: (c["function_id"], c["tier"], c["project_id"], c["node_id"]))
    return tiered
