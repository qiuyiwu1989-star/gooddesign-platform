# coding: utf-8
"""098 S6/S7：功能选项、概念族组合与约束剪枝。

选项与组合来自研究推理提议，引擎校验结构与引用完整性。
只有已确认硬约束才能排除组合；未知相容性保持 unknown。
理论笛卡尔组合空间不等于已研究方案数。
"""

MAX_OPTIONS_PER_FUNCTION = 4
BASELINE_SUFFIX = "O0"


def _validate_option(o, function_ids):
    if o.get("function_id") not in function_ids:
        raise ValueError(f"选项 {o.get('id')} 引用未定义功能：{o.get('function_id')}")
    if not o.get("id", "").startswith(o["function_id"]):
        raise ValueError(f"选项 {o.get('id')} 的 ID 必须以功能 ID 开头")
    if not o.get("principle", "").strip():
        raise ValueError(f"选项 {o.get('id')} 的 principle 不能为空")
    if not isinstance(o.get("conditions"), list) or not o["conditions"]:
        raise ValueError(f"选项 {o.get('id')} 必须写明条件与不适用边界")
    return dict(o)


def form_options(functions, proposal_options):
    """校验提议选项：每功能最多 4 个，O0 客户现状占位自动补齐。"""
    function_ids = [f["id"] for f in functions]
    options = [_validate_option(o, function_ids) for o in proposal_options]
    by_fn = {fid: [] for fid in function_ids}
    for o in options:
        by_fn[o["function_id"]].append(o)
    for f in functions:
        fid = f["id"]
        existing = by_fn[fid]
        baseline_id = fid + BASELINE_SUFFIX
        if not any(o["id"] == baseline_id for o in existing):
            existing.insert(0, {
                "id": baseline_id,
                "function_id": fid,
                "principle": "客户现状待现场采集",
                "conditions": ["客户现状占位，不是已测基准；条件待确认"],
                "evidence_refs": [],
            })
        if len(existing) > MAX_OPTIONS_PER_FUNCTION:
            raise ValueError(f"{fid} 选项数 {len(existing)} 超过 {MAX_OPTIONS_PER_FUNCTION}")
        by_fn[fid] = sorted(existing, key=lambda o: o["id"])
    return [o for fid in function_ids for o in by_fn[fid]]


def compose_concepts(functions, options, proposal_combinations):
    """校验概念组合：引用的选项必须存在，每个组合覆盖全部功能，C0 必须全是 O0。"""
    option_ids = {o["id"] for o in options}
    function_ids = {f["id"] for f in functions}
    combos = []
    for c in proposal_combinations:
        ids = c.get("option_ids", [])
        unknown_ref = [i for i in ids if i not in option_ids]
        if unknown_ref:
            raise ValueError(f"组合 {c.get('id')} 引用未定义选项：{unknown_ref}")
        covered = {i.split("O")[0] for i in ids}
        if covered != function_ids:
            raise ValueError(f"组合 {c.get('id')} 未覆盖全部功能：缺 {sorted(function_ids - covered)}")
        if c.get("id") == "C0" and any(not i.endswith(BASELINE_SUFFIX) for i in ids):
            raise ValueError("C0 必须由全部 O0 基线占位组成")
        if c.get("status") not in ("unknown", "option_candidate", "excluded"):
            raise ValueError(f"组合 {c.get('id')} 状态非法：{c.get('status')}")
        combos.append(dict(c))
    return combos


def validate_compatibility(compatibility, options):
    """相容性只能保持 unknown 或由已确认硬约束排除；引擎不自行判定冲突。"""
    option_ids = {o["id"] for o in options}
    pairs = []
    for pair in compatibility or []:
        ids = pair.get("option_ids", [])
        if len(ids) != 2 or any(i not in option_ids for i in ids):
            raise ValueError(f"相容性记录引用非法：{ids}")
        if pair.get("status") not in ("unknown", "compatible", "conflict"):
            raise ValueError(f"相容性状态非法：{pair.get('status')}")
        if pair["status"] == "conflict" and not pair.get("confirmed_hard_constraint"):
            raise ValueError("只有已确认硬约束才能标记 conflict，本任务不得由引擎或模型提议")
        pairs.append(dict(pair))
    return pairs


def theoretical_space_note(functions, options):
    counts = {}
    for o in options:
        counts[o["function_id"]] = counts.get(o["function_id"], 0) + 1
    space = 1
    for f in functions:
        space *= counts.get(f["id"], 0)
    return (
        f"理论组合空间 {space} 只是笛卡尔乘积，不代表已研究 {space} 个方案；"
        "本报告只研究显式列出的概念组合"
    )
