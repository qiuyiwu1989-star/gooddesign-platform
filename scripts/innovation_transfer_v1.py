# coding: utf-8
"""098 S5：机制映射契约校验。

机制映射是研究推理产物（Host 或受限模型提议），引擎只校验契约，
不替它背书。任何映射都必须写清差异、不能迁移的部分和证伪路径，
否则视为不合格输入，直接拒绝。
"""

REQUIRED_FIELDS = [
    "source_case", "target_function", "mechanism", "transfer_kind",
    "differences", "not_transferable", "status", "falsification_path",
]
TRANSFER_KINDS = {"structure", "workflow", "control_strategy", "validation_strategy", "explanation"}
STATUSES = {"option_candidate", "research_only", "excluded", "unknown"}


def validate_transfer_map(m, case_ids, function_ids):
    if not isinstance(m, dict):
        raise ValueError("TransferMap 必须是对象")
    missing = [k for k in REQUIRED_FIELDS if k not in m]
    if missing:
        raise ValueError(f"TransferMap 缺字段：{missing}")
    if m["source_case"] not in case_ids:
        raise ValueError(f"TransferMap 引用了未声明的来源项目：{m['source_case']}")
    if m["target_function"] not in function_ids:
        raise ValueError(f"TransferMap 引用了未定义的功能：{m['target_function']}")
    if m["transfer_kind"] not in TRANSFER_KINDS:
        raise ValueError(f"非法 transfer_kind：{m['transfer_kind']}")
    if m["status"] not in STATUSES:
        raise ValueError(f"非法映射状态：{m['status']}")
    if not m["mechanism"].strip():
        raise ValueError("mechanism 不能为空")
    if not isinstance(m["differences"], list) or not m["differences"]:
        raise ValueError("differences 必须是非空列表：没有差异分析的映射不允许进入")
    if not isinstance(m["not_transferable"], list) or not m["not_transferable"]:
        raise ValueError("not_transferable 必须是非空列表：必须写明什么不能迁移")
    if not m["falsification_path"].strip():
        raise ValueError("falsification_path 不能为空：必须给出证伪路径")
    return dict(m)


def validate_all(transfer_maps, case_ids, function_ids):
    """全量校验并返回规范化列表；任何一条不合格则整批拒绝。"""
    if not isinstance(transfer_maps, list):
        raise ValueError("transfer_maps 必须是列表")
    return [validate_transfer_map(m, case_ids, function_ids) for m in transfer_maps]
