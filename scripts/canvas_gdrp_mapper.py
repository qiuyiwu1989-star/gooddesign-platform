#!/usr/bin/env python3
"""RC-11 第一层：推理画布状态 -> GDRP 研究包。

以 GD-CRE-0.1 冻结割胶包为领域骨架，只把画布中的人类裁决、取舍、签署与检索留痕映射进去。
未知、待复核和 recommendations=[] 保持原样；不生成新的领域事实。
"""
import hashlib
import json
import re
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
FROZEN_PACK = ROOT / "output" / "engine-runs" / "RUBBER-20261026" / "run-20261105T140200Z" / "research-pack.json"
SCHEMA = ROOT / "04-知识库" / "项目档案标准-v1" / "创新研究输出物标准-v1" / "research-pack.schema.json"


def canonical_sha(value):
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def safe_package_part(value):
    text = re.sub(r"[^A-Za-z0-9_.:-]+", "-", value).strip("-") or "canvas"
    return text[:72]


def _canvas_trace(state):
    killed = sorted([key for key, value in state.get("killed", {}).items() if value])
    trust = sorted([key for key, value in state.get("evMarks", {}).items() if value == "trust"])
    doubt = sorted([key for key, value in state.get("evMarks", {}).items() if value == "doubt"])
    confirmed = state.get("engineConfirmed", [])
    flow = state.get("flow", {})
    return {
        "workspace_kind": "reasoning_canvas",
        "canvas_state_sha256": canonical_sha(state),
        "node_statuses": state.get("statuses", {}),
        "evidence_verdicts": {"trusted": trust, "doubted": doubt},
        "killed_directions": killed,
        "priorities": state.get("priorities", {}),
        "decision_reason": state.get("reasons", {}).get("main", ""),
        "committed": bool(state.get("committed")),
        "search_log": state.get("searchLog", []),
        "engine_confirmed_options": confirmed,
        "flow_runs": flow.get("runs", 0),
        "flow_log": flow.get("log", []),
        "notes": state.get("notes", {}),
    }


def map_canvas_to_gdrp(state, workspace_id, revision):
    if not FROZEN_PACK.is_file():
        raise FileNotFoundError("GD-CRE 冻结研究包不存在，无法生成画布 GDRP")
    pack = deepcopy(json.loads(FROZEN_PACK.read_text(encoding="utf-8")))
    trace = _canvas_trace(state)
    state_hash = trace["canvas_state_sha256"]
    package_revision = f"canvas-r{revision}"
    pack["package_id"] = f"RC-{safe_package_part(workspace_id).upper()}-{package_revision}"
    pack["execution"] = dict(pack["execution"])
    pack["execution"]["mode"] = "host_agent"
    pack["execution"]["status"] = "review_pending" if state.get("committed") else "draft"
    pack["execution"]["model_calls"] = {
        "status": "not_used",
        "count": 0,
        "note": "推理画布导出；本轮未调用在线模型，引擎内容来自冻结样例投影。",
    }
    pack["review"] = {
        "customer_confirmed": False,
        "semantic_review": "pending",
        "domain_expert": False,
        "engineering_validated": False,
        "public_authorized": False,
        "training_authorized": False,
        "overall": "pending_review",
    }
    killed_count = len(trace["killed_directions"])
    flow_runs = trace["flow_runs"]
    pack["summary"] = {
        "problem": pack["summary"]["problem"],
        "outcome": f"画布形成 {len(trace['priorities'])} 条路线取舍，毙掉 {killed_count} 条方向，完成 {flow_runs} 轮推理展开；当前不推荐。",
        "next_action": "已签署验证承诺，进入独立评审与真实验证准备。" if state.get("committed") else "先完成画布签署，再进入独立评审。",
        "recommendation_status": "no_recommendation",
    }
    pack["evidence"] = list(pack.get("evidence", [])) + [
        {
            "id": "canvas-state",
            "kind": "canvas_trace",
            "workspace_id": workspace_id,
            "revision": revision,
            "sha256": state_hash,
            "note": "画布人类裁决与过程留痕，不改变源项目事实。",
        }
    ]
    pack.setdefault("concept_set", {})["canvas_trace"] = {
        "killed_directions": trace["killed_directions"],
        "priorities": trace["priorities"],
        "engine_confirmed_options": trace["engine_confirmed_options"],
    }
    pack.setdefault("validation_plan", {})["canvas_commitment"] = {
        "committed": trace["committed"],
        "decision_reason": trace["decision_reason"],
        "flow_runs": trace["flow_runs"],
    }
    product = pack.setdefault("domain_extension", {}).setdefault("product") or {}
    product["reasoning_canvas"] = trace
    pack["domain_extension"]["product"] = product
    pack.setdefault("boundary", {}).setdefault("notes", []).append("画布导出是研究过程快照；画布签署不等于客户确认、专家评审或工程验证。")
    validator = Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8")))
    errors = sorted(validator.iter_errors(pack), key=lambda e: list(e.path))
    if errors:
        raise ValueError("GDRP schema failed: " + "; ".join(e.message for e in errors[:5]))
    return pack


def package_manifest(pack, generated_at=None):
    generated_at = generated_at or datetime.now(timezone.utc).isoformat()
    body = json.dumps(pack, ensure_ascii=False, sort_keys=True, indent=2).encode("utf-8")
    return {
        "schema_version": "gdrp-manifest-0.1",
        "package_id": pack["package_id"],
        "generated_at": generated_at,
        "files": {"research-pack.json": hashlib.sha256(body).hexdigest()},
        "notes": ["由推理画布当前状态生成；不覆盖冻结引擎包。"],
    }


def package_full_manifest(pack, report_html, report_md, generated_at=None):
    generated_at = generated_at or datetime.now(timezone.utc).isoformat()
    pack_body = json.dumps(pack, ensure_ascii=False, sort_keys=True, indent=2).encode("utf-8")
    return {
        "schema_version": "gdrp-manifest-0.1",
        "package_id": pack["package_id"],
        "generated_at": generated_at,
        "files": {
            "research-pack.json": hashlib.sha256(pack_body).hexdigest(),
            "report.html": hashlib.sha256(report_html.encode("utf-8")).hexdigest(),
            "report.md": hashlib.sha256(report_md.encode("utf-8")).hexdigest(),
        },
        "source_facts_modified": pack.get("boundary", {}).get("source_facts_modified", False),
        "notes": ["由推理画布当前状态生成；指纹用于完整性检查，不是数字签名或专家认证。"],
    }
