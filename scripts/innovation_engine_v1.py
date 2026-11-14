# coding: utf-8
"""098 GD-CRE-0.1：好设计创新研究引擎 V1 确定性骨架（S0-S10）。

确定性轨道：输入契约、检索计划、映射/选项/组合校验、比较门禁、验证计划、
不可覆盖保存与指纹。研究推理由 Host 提议文件提供，只作为待审核输入；
模型后端 V1 未实现（model_assisted 拒绝执行）。

用法：
  python3 scripts/innovation_engine_v1.py run \
      --task rubber-task.json --proposal rubber-proposal.json \
      --out-root output/engine-runs [--library 04-知识库/项目库]
"""
import argparse
import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import Draft202012Validator

import innovation_concepts_v1 as concepts
import innovation_retrieval_v1 as retrieval
import innovation_transfer_v1 as transfer
import innovation_validation_v1 as validation

ENGINE_VERSION = "GD-CRE-0.1"
GDRP_SCHEMA_VERSION = "gdrp-0.1"
STD_SCHEMA = Path(__file__).resolve().parent.parent / "04-知识库/项目档案标准-v1" / "创新研究输出物标准-v1" / "research-pack.schema.json"
DEFAULT_LIBRARY = Path(__file__).resolve().parent.parent / "04-知识库" / "项目库"

MODES = {"rule_only", "host_agent"}
TASK_REQUIRED = ["task_id", "revision", "title", "object", "domains", "delivery_level",
                 "boundary", "problem_brief", "case_library", "method_versions", "execution_policy"]
PROPOSAL_ALLOWED = {"function_model", "query_hints", "transfer_maps", "options", "combinations",
                    "compatibility", "concept_unknowns", "sensitivity", "validation_methods",
                    "domain_extension", "boundary_notes", "case_evidence", "configuration_template"}
# 098 第6节：Host/模型不得写入的字段
FORBIDDEN_KEYS = {"approved", "confirmed", "engineering_validated", "expert_reviewed",
                  "target_value", "hard", "pass", "recommendations", "public", "training_authorized"}
REQ_STATUSES = {"proposed", "confirmed", "unknown"}


def _scan_forbidden(obj, path="proposal"):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in FORBIDDEN_KEYS:
                raise ValueError(f"提议含禁止写字段 {path}.{k}（098 第6节）")
            _scan_forbidden(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            _scan_forbidden(v, f"{path}[{i}]")


def precheck(task, proposal):
    """S0：任务、版本、权限、方法版本与预算预检；冻结执行模式。"""
    missing = [k for k in TASK_REQUIRED if k not in task]
    if missing:
        raise ValueError(f"任务缺字段：{missing}")
    policy = task["execution_policy"]
    mode = policy.get("mode")
    if mode == "model_assisted":
        raise ValueError("V1 未实现模型后端，model_assisted 不可用；模型失败不得写成成功")
    if mode not in MODES:
        raise ValueError(f"非法执行模式：{mode}")
    for case in task["case_library"]:
        if not case.get("revision") or case["revision"] in ("latest", "current"):
            raise ValueError("CaseLibrary 必须指定研究版本，不默认读取全库最新版本")
    extra = set(proposal) - PROPOSAL_ALLOWED
    if extra:
        raise ValueError(f"提议含未声明段落：{sorted(extra)}")
    _scan_forbidden(proposal)
    brief = task["problem_brief"]
    for r in brief.get("requirements", []):
        for k in ("id", "text", "acceptance", "status"):
            if k not in r:
                raise ValueError(f"需求 {r.get('id')} 缺字段 {k}")
        if r.get("hard") not in (True, False, None):
            raise ValueError(f"需求 {r['id']} 的 hard 只能是 true/false/null")
        if r["status"] not in REQ_STATUSES:
            raise ValueError(f"需求 {r['id']} 状态非法：{r['status']}")
    mc = policy.get("model_calls")
    if mc and mc.get("status") == "success":
        raise ValueError("V1 无模型后端，不得声明模型调用成功")
    return mode


def validate_function_model(fm):
    """S2：功能图与接口结构校验。功能不是零件清单。"""
    if not isinstance(fm, dict) or not fm.get("functions"):
        raise ValueError("function_model.functions 不能为空")
    ids = [f["id"] for f in fm["functions"]]
    if len(ids) != len(set(ids)):
        raise ValueError("功能 ID 重复")
    for f in fm["functions"]:
        if not f.get("verb_object", "").strip():
            raise ValueError(f"功能 {f['id']} 必须是动词加对象")
        f.setdefault("necessity", "necessary")
        f.setdefault("evidence_refs", [])
    for fl in fm.get("flows", []):
        if fl["from_function"] not in ids or fl["to_function"] not in ids:
            raise ValueError(f"流 {fl.get('id')} 引用未定义功能")
    for itf in fm.get("interfaces", []):
        if itf.get("kind") not in ("known", "assumption", "unknown"):
            raise ValueError(f"接口 {itf.get('id')} 类型非法")
    return fm


def _model_calls(policy, mode):
    if mode == "rule_only":
        return {"status": "not_used", "count": 0, "note": "rule_only 模式不调用模型"}
    mc = policy.get("model_calls") or {"status": "not_used", "count": 0}
    return {"status": mc["status"], "count": mc.get("count", 0), "note": mc.get("note", "")}


def run(task, proposal, retriever=None, library=None):
    """S0-S9：返回未落盘的运行结果（pack + engine_run）。"""
    mode = precheck(task, proposal)
    brief = copy.deepcopy(task["problem_brief"])
    fm = validate_function_model(copy.deepcopy(proposal["function_model"]))
    function_ids = [f["id"] for f in fm["functions"]]
    case_ids = [c["project_id"] for c in task["case_library"]]

    queries = retrieval.build_queries(fm["functions"], proposal.get("query_hints"))
    if retriever is not None:
        case_retrieval = retriever(library, task["case_library"], queries)
    else:
        case_retrieval = [dict(project_id=c["project_id"], revision=c["revision"],
                               record_count=0, read_sources=[], errors=["未配置检索器"],
                               candidates=[]) for c in task["case_library"]]
    tiered = retrieval.tier_candidates(case_retrieval)

    maps = transfer.validate_all(proposal.get("transfer_maps", []), case_ids, function_ids)
    options = concepts.form_options(fm["functions"], proposal.get("options", []))
    combos = concepts.compose_concepts(fm["functions"], options, proposal.get("combinations", []))
    compat = concepts.validate_compatibility(proposal.get("compatibility", []), options)

    criteria = validation.build_criteria(brief["requirements"])
    judgments = validation.build_judgments([c["id"] for c in combos], criteria)
    recommendations, gate_reasons = validation.apply_recommendation_gate(judgments, criteria, brief)
    plan = validation.build_validation_plan(
        brief["requirements"], proposal.get("validation_methods"),
        configuration_template=proposal.get("configuration_template", validation.DEFAULT_CONFIG_TEMPLATE))

    concept_unknowns = list(proposal.get("concept_unknowns", []))
    concept_unknowns.append(concepts.theoretical_space_note(fm["functions"], options))
    unknown_count = sum(1 for j in judgments if j["value"] == "unknown")

    gates = plan["gates"]
    pack = {
        "schema_version": GDRP_SCHEMA_VERSION,
        "package_id": f"{task['task_id']}-{task['revision']}",
        "task": {k: task[k] for k in ("task_id", "revision", "title", "domains", "object", "delivery_level")},
        "execution": {
            "engine_version": ENGINE_VERSION,
            "mode": mode,
            "status": "review_pending",
            "source_versions": [dict(project_id=c["project_id"], revision=c["revision"],
                                     record_count=next((e["record_count"] for e in case_retrieval
                                                        if e["project_id"] == c["project_id"]), 0))
                                for c in task["case_library"]],
            "method_versions": task["method_versions"],
            "model_calls": _model_calls(task["execution_policy"], mode),
        },
        "review": {"customer_confirmed": False, "semantic_review": "pending", "domain_expert": False,
                   "engineering_validated": False, "public_authorized": False,
                   "training_authorized": False, "overall": "pending_review"},
        "summary": {
            "problem": brief.get("desired_outcome", task["title"]),
            "outcome": f"形成 {len(combos)} 个概念组合；{unknown_count} 格判断均保留 unknown，本次不给出唯一工程推荐。",
            "next_action": f"进入 {gates[0]['id']}：{gates[0]['purpose']}。",
            "recommendation_status": "no_recommendation",
        },
        "problem_brief": brief,
        "function_model": fm,
        "case_retrieval": [{k: e[k] for k in ("project_id", "revision", "read_sources", "record_count", "errors")}
                           for e in case_retrieval],
        "transfer_maps": maps,
        "concept_set": {
            "function_ids": function_ids,
            "options": options,
            "combinations": combos,
            "compatibility": compat,
            "unknowns": concept_unknowns,
        },
        "comparison": {
            "requirements_revision": task["revision"],
            "baseline_id": combos[0]["id"] if combos else None,
            "candidate_ids": [c["id"] for c in combos],
            "criteria": criteria,
            "judgments": judgments,
            "recommendations": recommendations,
            "sensitivity": proposal.get("sensitivity", []),
            "unknowns": gate_reasons,
        },
        "validation_plan": plan,
        "evidence": proposal.get("case_evidence", []),
        "domain_extension": proposal["domain_extension"],
        "boundary": {
            "source_facts_modified": False,
            "physical_test_authorized": False,
            "notes": ([f"研究边界：{task['boundary']}"] +
                      list(proposal.get("boundary_notes", [])) +
                      ["研究、概念与试验计划，不是工程定案",
                       "公开专利线索不构成新颖性、侵权或实施自由判断",
                       "私有原件不进入公开研究包"]),
        },
    }
    schema = json.loads(STD_SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(pack)

    engine_run = {
        "engine_version": ENGINE_VERSION,
        "task_id": task["task_id"],
        "revision": task["revision"],
        "execution_mode": mode,
        "model_calls": pack["execution"]["model_calls"],
        "queries": queries,
        "retrieval": case_retrieval,
        "tiered_candidates": tiered,
        "recommendation_gate": {"recommendations": recommendations, "reasons": gate_reasons},
        "counts": {
            "requirements": len(brief["requirements"]),
            "functions": len(function_ids),
            "options": len(options),
            "combinations": len(combos),
            "judgments": len(judgments),
            "unknown_judgments": unknown_count,
        },
        "host_proposal_status": "pending_review_not_machine_verified",
    }
    return {"pack": pack, "engine_run": engine_run}


def freeze(result, out_root, task, proposal_paths, run_id=None):
    """S10：不可覆盖保存。run_id 取 UTC 秒；目录已存在即拒绝。"""
    run_id = run_id or "run-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = Path(out_root) / task["task_id"] / run_id
    if out_dir.exists():
        raise FileExistsError(f"运行目录已存在，不可覆盖：{out_dir}")
    out_dir.mkdir(parents=True)
    files = {}
    for name, obj in [("research-pack.json", result["pack"]), ("engine-run.json", result["engine_run"])]:
        (out_dir / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        files[name] = hashlib.sha256((out_dir / name).read_bytes()).hexdigest()
    inputs = {}
    for label, p in proposal_paths.items():
        inputs[label] = hashlib.sha256(Path(p).read_bytes()).hexdigest()
    manifest = {
        "schema_version": "engine-run-manifest-0.1",
        "engine_version": ENGINE_VERSION,
        "task_id": task["task_id"],
        "revision": task["revision"],
        "run_id": run_id,
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "input_fingerprints": inputs,
        "files": files,
        "note": "指纹用于完整性检查，不是签名、专家认证或工程结论；反馈只能形成新版本，不得覆盖本目录。",
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return out_dir


def main():
    ap = argparse.ArgumentParser(description="GD-CRE-0.1 创新研究引擎 V1 确定性骨架")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--task", type=Path, required=True)
    r.add_argument("--proposal", type=Path, required=True)
    r.add_argument("--out-root", type=Path, required=True)
    r.add_argument("--library", type=Path, default=DEFAULT_LIBRARY)
    r.add_argument("--no-retrieval", action="store_true", help="跳过真实检索（离线校验）")
    args = ap.parse_args()

    task = json.loads(args.task.read_text(encoding="utf-8"))
    proposal = json.loads(args.proposal.read_text(encoding="utf-8"))
    retriever = None if args.no_retrieval else retrieval.retrieve_with_knowledge
    result = run(task, proposal, retriever=retriever, library=args.library)
    out_dir = freeze(result, args.out_root, task, {"task": args.task, "proposal": args.proposal})
    counts = result["engine_run"]["counts"]
    print(f"engine run frozen: {out_dir}")
    print(f"counts: {counts}, recommendations={result['pack']['comparison']['recommendations']}")


if __name__ == "__main__":
    main()
