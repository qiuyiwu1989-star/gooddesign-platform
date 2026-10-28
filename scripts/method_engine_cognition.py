"""ML-022: stateless, evidence-scoped context for the existing innovation engine.

This adapts Shennao principles, not its personal-memory store. No model calls,
network access, automatic fact promotion, persistence or engineering approval.
"""
import hashlib
import json
from pathlib import Path

from method_engine import Engine, ROOT, digest
from method_engine_contracts import META

CONTENT = ROOT / '02-研究/ML-021-内容质量深化'
STATES = {'observed', 'inferred', 'associated', 'hypothesized'}


def text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError('missing_' + label)
    return value


def read_deep_method(method_id, content_root=CONTENT):
    """Read the exact independently reviewed manuscript; keep partial ratings."""
    root = Path(content_root).resolve()
    raw = (root / '64项最终内容索引.json').read_bytes()
    index = json.loads(raw)
    row = next((r for r in index['methods'] if r['method_id'] == method_id), None)
    if row is None:
        raise ValueError('unknown_method')
    # The index stores repository-relative paths; never expose arbitrary files.
    p = (ROOT / row['candidate_path']).resolve()
    if not p.is_relative_to(root):
        raise ValueError('method_path_outside_content_root')
    body = p.read_bytes()
    if hashlib.sha256(body).hexdigest() != row['sha256']:
        raise ValueError('reviewed_manuscript_changed')
    return {'method_id': method_id, 'name': row['name'],
            'content_sha256': row['sha256'], 'index_sha256': hashlib.sha256(raw).hexdigest(),
            'content': body.decode('utf-8'), 'seven_dimensions': row['seven_dimensions'],
            'partial_dimensions': [k for k, v in row['seven_dimensions'].items()
                                   if v.get('assessment', v.get('rating')) == '局部'],
            'execution_available': method_id in META,
            'scope': 'reviewed_method_teaching_not_original_algorithm_or_engineering_certification'}


def prepare_context(task, claims, method_ids, conflicts=None, associations=None):
    """Validate supplied provenance, not semantic truth; preserve every claim state.

    Claim evidence consists of caller-supplied source_id/locator/scope anchors.
    Observed means a reported source observation, never verified target truth.
    Explicit conflict/association proposals remain unresolved for Host review.
    """
    text(task.get('task_id'), 'task_id')
    text(task.get('revision'), 'revision')
    target = text(task.get('object'), 'object')
    if not isinstance(claims, list) or len(claims) > 100:
        raise ValueError('claims_must_be_list_at_most_100')
    if (not isinstance(method_ids, list) or not 1 <= len(method_ids) <= 5
            or len(set(method_ids)) != len(method_ids)):
        raise ValueError('select_1_to_5_unique_methods')
    # Reject NaN and excessive untrusted context before it can reach a model.
    if len(json.dumps([task, claims, conflicts, associations], allow_nan=False)) > 120000:
        raise ValueError('context_too_large')
    by_id = {}
    for c in claims:
        ident = text(c.get('id'), 'claim_id')
        if ident in by_id:
            raise ValueError('duplicate_claim_id')
        text(c.get('text'), 'claim_text')
        text(c.get('scope'), 'claim_scope')
        if c.get('epistemic') not in STATES:
            raise ValueError('invalid_epistemic_state')
        anchors = c.get('evidence', [])
        if not isinstance(anchors, list):
            raise ValueError('evidence_must_be_list')
        if c['epistemic'] == 'observed' and not anchors:
            raise ValueError('observed_claim_requires_anchor')
        for anchor in anchors:
            for field in ('source_id', 'locator', 'scope'):
                text(anchor.get(field), 'anchor_' + field)
            if anchor['scope'] != c['scope']:
                raise ValueError('anchor_scope_mismatch')
        by_id[ident] = c
    # A supplied supersession is a proposal, not deletion or automatic new-wins-old.
    supersessions = []
    for c in claims:
        if c.get('supersedes'):
            if c['supersedes'] not in by_id or c['supersedes'] == c['id']:
                raise ValueError('invalid_supersession_reference')
            supersessions.append({'new': c['id'], 'old': c['supersedes'],
                                  'status': 'proposed_requires_reason_and_review'})
    for c in claims:
        seen = set()
        node = c
        while node.get('supersedes'):
            if node['id'] in seen:
                raise ValueError('supersession_cycle')
            seen.add(node['id'])
            node = by_id[node['supersedes']]

    def pair(proposal):
        ids = proposal.get('claim_ids')
        if not isinstance(ids, list) or len(ids) != 2 or len(set(ids)) != 2:
            raise ValueError('two_distinct_claims_required')
        if any(i not in by_id for i in ids):
            raise ValueError('unknown_claim_reference')
        return [by_id[i] for i in ids]

    research = []
    for proposal in conflicts or []:
        a, b = pair(proposal)
        research.append({'claim_ids': [a['id'], b['id']],
                         'question': text(proposal.get('question'), 'conflict_question'),
                         'status': 'boundary_conditions_require_research',
                         'auto_resolved': False})
    links = []
    if len(associations or []) > 3:
        raise ValueError('at_most_3_associations')
    for proposal in associations or []:
        a, b = pair(proposal)
        if not a.get('evidence') or not b.get('evidence'):
            raise ValueError('association_requires_two_anchored_sides')
        if proposal.get('transfer_kind') != 'structural_principle':
            raise ValueError('cross_scope_fact_transfer_forbidden')
        links.append({'claim_ids': [a['id'], b['id']], 'epistemic': 'associated',
                      'principle': text(proposal.get('principle'), 'principle'),
                      'target_scope': target,
                      'conditions_to_check': text(proposal.get('conditions_to_check'), 'conditions_to_check'),
                      'status': 'host_must_review_structure_and_test_target_conditions',
                      'source_facts_transferred': False})
    methods = [read_deep_method(i) for i in method_ids]
    # Keep contents separate from compact model context to avoid silent truncation.
    plan = Engine().plan(task)
    # Full plans repeat six JSON schemas; retrieve them through method_plan.
    # Bind the full-plan digest explicitly, without claiming this projection has
    # that digest or silently truncating method/contract material.
    compact_plan = {k: plan[k] for k in ('task_id', 'task_revision', 'task_sha256',
                    'target', 'implementation_hashes', 'status', 'quality') if k in plan}
    compact_plan['nodes'] = [{k: n[k] for k in ('node_id', 'method_id', 'method_version',
                             'method_content_sha256', 'contract_version', 'contract_sha256',
                             'depends_on', 'output_type', 'executor', 'stop_condition')}
                             for n in plan['nodes']]
    if 'issues' in plan:
        compact_plan['issues'] = plan['issues']
    compact_plan['full_plan_sha256'] = plan.get('plan_sha256')
    compact_plan['full_plan_returned'] = False
    compact_plan['full_plan_tool'] = 'method_plan'
    compact_plan['projection_sha256'] = digest(compact_plan)
    packet = {'version': 'ML022-0.1.2', 'task': task, 'claims': claims,
              'supersession_proposals': supersessions, 'boundary_research': research,
              'association_candidates': links,
              'method_refs': [{k: m[k] for k in ('method_id', 'name', 'content_sha256',
                                'index_sha256', 'partial_dimensions', 'execution_available')} for m in methods],
              'existing_contract_plan': compact_plan,
              'research_readiness': {
                  'status': 'not_assessed_by_engine', 'physical_test_permission_granted': False,
                  'required_before_physical_tests': [
                      '明确台架/装夹/防护与故障注入隔离，确认人员能力、责任及资源缺失的暂停位置',
                      '独立参考、校准、重复装夹与测量不确定性足以分辨要比较的机制；不能只用被测设备自证',
                      '区分几何代理件与真实材料/组织，写清代理覆盖和不得外推的范围',
                      '断电/失联后的能量、保持或退让路径，以及手动检查与复位许可须实际审查',
                      '清洗/换件/复装校准、各出口物料账及恢复基线可追溯',
                      '列出人工、维护、停机、折旧、利用率及长期影响的补证主体；缺数不能批准扩大试点'],
                  'decision_branch_rules': [
                      '测不清：结论不可解释，先修量测；不能判路线或模型失败',
                      '测得清且配置违反给定研究条件：停该配置并返设计；不能悄改判据',
                      '代理件满足但目标真实边界未知：仅保留代理范围结论，不作目标许可'],
                  'dependency_rule': '按风险与数据依赖分支；危险配置停止后，独立且已审查的非危险研究可另行继续，不强制全部串行',
                  'scope': '供Host补齐就绪材料与专业审查，不是已执行检查或试验授权'},
              'host_workflow': [
                  '核对需求版本、主张作用域、证据原件及核读范围；锚点存在不证明主张为真',
                  '逐项读取method_refs对应深化正文，核对前提；补证专题不可当完整算法',
                  '先研究冲突边界，再审跨案例结构同构；不得直接复制参数或现场事实',
                  '构造2到3条有不同机制的候选路径，给条件、二阶后果和证伪方法；缺依据不凑数',
                  '只按已有六契约形成研究产物，模型草稿另过语义与领域审查',
                  '记录实际采用、修订原因、试验配置及结果；反馈不自动升格为事实或专家认证'],
              'capability_boundary': {'model_called': False, 'case_mcp_called': False,
                                      'persistent_memory_written': False, 'semantic_truth_verified': False,
                                      'engineering_validated': False, 'expert_certified': False}}
    # Return a fresh JSON tree, so a caller cannot mutate an already hashed packet.
    packet = json.loads(json.dumps(packet, ensure_ascii=False, allow_nan=False))
    chars = len(json.dumps(packet, ensure_ascii=False))
    return {'status': 'host_reasoning_context_ready' if plan['status'] != 'blocked' else 'blocked',
            'context_sha256': digest(packet), 'context': packet,
            'model_context_chars': chars, 'fits_existing_semantic_match_limit': chars <= 20000,
            'model_context_note': '模型入口上限为20000字符；超限须显式选择证据，禁止静默截断或假装已调用模型'}


def feedback_summary(records):
    """Summarize caller-labelled outcomes; never infer accuracy or confidence."""
    if not isinstance(records, list) or len(records) > 1000:
        raise ValueError('feedback_list_required_at_most_1000')
    groups, seen = {}, set()
    for record in records:
        ident = text(record.get('prediction_id'), 'prediction_id')
        if ident in seen:
            raise ValueError('duplicate_prediction_id')
        seen.add(ident)
        group = text(record.get('judgment_type'), 'judgment_type')
        status = record.get('outcome')
        if status not in {'supported', 'refuted', 'pending', 'inconclusive'}:
            raise ValueError('invalid_outcome')
        if status in {'supported', 'refuted'}:
            text(record.get('outcome_anchor'), 'outcome_anchor')
            text(record.get('test_definition'), 'test_definition')
        bucket = groups.setdefault(group, dict(supported=0, refuted=0, pending=0, inconclusive=0))
        bucket[status] += 1
    return {'groups': groups, 'records': records,
            'scope': 'caller_labelled_counts_only_not_calibrated_model_accuracy_or_new_case_probability',
            'automatic_method_promotion': False, 'persistent_memory_written': False}
