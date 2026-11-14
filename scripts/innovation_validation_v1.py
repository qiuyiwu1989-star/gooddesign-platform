# coding: utf-8
"""098 S8/S9：逐项比较、推荐门禁与验证计划。

判断值只能是 pass / conditional / unknown / conflict / not_applicable。
推荐门禁由确定性代码控制：硬约束未确认、存在 unknown、偏好未确认时
recommendations 必须为空，这不是算法失败，是正确的研究状态。
"""

JUDGMENT_VALUES = {"pass", "conditional", "unknown", "conflict", "not_applicable"}

GATE_TEMPLATE = [
    {"id": "G0", "purpose": "需求、现场基线、口径、许可与责任确认"},
    {"id": "G1", "purpose": "非活树或替代件的机构、物流与退出检查"},
    {"id": "G2", "purpose": "经许可的局部机制对照"},
    {"id": "G3", "purpose": "受限现场试点与完整日志"},
    {"id": "G4", "purpose": "跨周期影响、维护、成本与真实采用"},
]

UNKNOWN_BASIS = "未取得同条件客户基线、已冻结验收目标或实测。该格保留未知，不以相同或中分填补。"


def build_criteria(requirements):
    """比较准则由需求生成，保留需求版本和硬软原值。"""
    criteria = []
    for r in requirements:
        criteria.append({
            "id": r["id"].replace("N", "K", 1),
            "text": f"{r['text']}；判据：{r['acceptance']}",
            "hard": r.get("hard"),
            "requirement_ids": [r["id"]],
        })
    return criteria


def build_judgments(candidate_ids, criteria):
    """rule_only 模式下没有任何已确认证据，全部判断为 unknown。"""
    return [
        {"candidate_id": cid, "criterion_id": c["id"], "value": "unknown",
         "basis": UNKNOWN_BASIS, "evidence_refs": []}
        for cid in candidate_ids for c in criteria
    ]


def apply_recommendation_gate(judgments, criteria, brief):
    """推荐必须同时满足：硬约束已确认、无 conflict、关键判断非 unknown、
    偏好与准则已确认、工程验证达到交付层级。任一不满足则为空。"""
    requirements = brief["requirements"]
    hard_unconfirmed = [r["id"] for r in requirements if r.get("hard") is True and r.get("status") != "confirmed"]
    undecided_hard = [r["id"] for r in requirements if r.get("hard") is None]
    unknowns = [j for j in judgments if j["value"] == "unknown"]
    reasons = []
    if hard_unconfirmed:
        reasons.append(f"硬性需求未确认：{'、'.join(hard_unconfirmed)}")
    if undecided_hard:
        reasons.append(f"硬软属性未决：{'、'.join(undecided_hard)}")
    if unknowns:
        reasons.append(f"{len(unknowns)} 格判断为 unknown")
    reasons.append("用户偏好与比较准则未确认")
    reasons.append("目标工程验证未达到任何交付层级")
    return [], reasons


DEFAULT_CONFIG_TEMPLATE = "待冻结的目标设备/对象/环境/工具与传感配置；当前仅规划"


def build_validation_plan(requirements, validation_methods=None, gate_statuses=None,
                          configuration_template=DEFAULT_CONFIG_TEMPLATE):
    methods = validation_methods or {}
    statuses = gate_statuses or {}
    gates = [dict(g, status=statuses.get(g["id"], "planned")) for g in GATE_TEMPLATE]
    matrix = []
    for r in requirements:
        matrix.append({
            "requirement_id": r["id"],
            "purpose": "verification",
            "method": methods.get(r["id"], "analysis"),
            "criterion": r["acceptance"],
            "configuration": configuration_template,
            "evidence_status": "planned",
            "evidence_refs": [],
        })
    return {"gates": gates, "matrix": matrix, "execution_status": "planned"}
