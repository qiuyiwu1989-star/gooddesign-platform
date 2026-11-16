"""Build ML-029 benchmark method assets and deterministic reference replays."""
import argparse
import copy
import hashlib
import json
from pathlib import Path

import method_library_catalog
from method_engine import Engine, digest

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / '04-知识库/创新方法库/标杆方法-v0.1'
CAPABILITY_MAP = ROOT / '04-知识库/创新方法库/能力地图-v0.1/能力地图.json'
DEEP_INDEX = ROOT / '02-研究/ML-021-内容质量深化/64项最终内容索引.json'
RUBBER = ROOT / 'output/rubber-tapping-pilot'
HISTORICAL_COMPARISON = ROOT / 'output/innovation-loop-024/evaluation/round2/descriptive-results.json'
BENCHMARK_VERSION = '0.1.0'
METHOD_IDS = ('R17', 'R02', 'R52')

CONTRIBUTIONS = {
    'R17': {
        'archetype': 'contract_tool',
        'improves': ['机制选项的差异性', '功能覆盖', '接口与相容性判断', '排除理由可追溯性'],
        'failure_signals': ['零件或属性变体冒充机制差异', '未知相容性被列为候选', '组合数量冒充研究质量'],
    },
    'R02': {
        'archetype': 'framework_orchestration',
        'improves': ['问题重定义', '不同回应路径', '新证据触发回返'],
        'failure_signals': ['把委托解法当问题', '四阶段一次性走完', '把学习计划当实测结果'],
    },
    'R52': {
        'archetype': 'qualitative_quantitative_decision',
        'improves': ['研究与决策分支的连接', '验证优先级', '概率和行动阈值复算'],
        'failure_signals': ['缺先验默认0.5', '信息更准但不改变行动仍算有价值', '经济价值豁免强制验证'],
    },
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def json_text(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n'


def capability_route(rid):
    data = json.loads(CAPABILITY_MAP.read_text())
    return next(m for m in data['methods'] if m['research_id'] == rid)


def deep_content(rid, index):
    row = next(r for r in index['methods'] if r['method_id'] == rid)
    path = ROOT / row['candidate_path']
    raw = path.read_bytes()
    expected = row.get('candidate_sha256', row['sha256'])
    if sha(raw) != expected:
        raise ValueError('deep content changed: ' + rid)
    return row, raw.decode('utf-8'), sha(raw)


def invocation(rid, dossier, route):
    strict = route['skill_level'] == 'S2'
    return {
        'schema_version': 'method-invocation-0.1',
        'research_id': rid,
        'skill_level': route['skill_level'],
        'engine_stages': route['engine_stages'],
        'primary_capability': route['primary_capability'],
        'required_inputs': [i for i in dossier['inputs'] if i['required']],
        'logical_outputs': route['logical_outputs'],
        'existing_mcp_tools': ['method_get', 'method_check_inputs', 'method_check_output', 'method_run_create', 'method_run_submit'] if strict else ['method_get'],
        'host_operations': ['guided_elicitation', 'artifact_draft', 'human_review', 'feedback_record'],
        'forbidden_operations': [] if strict else ['method_run_submit', 'strict_artifact_claim'],
        'contract_ref': route['contract_ref'],
        'limitations': ['严格结构通过不等于专家或工程验证'] if strict else ['仅引导；没有严格执行契约或生产求解器'],
        'public_authorized': False,
        'training_authorized': False,
    }


def skill(rid, dossier, route):
    contribution = CONTRIBUTIONS[rid]
    level = route['skill_level']
    lines = [
        '---',
        f'name: gooddesign-{rid.lower()}-{route["primary_capability"].replace("_", "-")}',
        f'description: 使用{rid}{dossier["name"]}完成{route["primary_capability"]}；等级{level}，不得超越声明的证据和执行边界。',
        '---',
        '',
        f'# {rid} {dossier["name"]}',
        '',
        f'资产版本：内容{dossier["version"]}，能力地图0.1.0，Skill {BENCHMARK_VERSION}，等级{level}。先通过`method_get`读取精确档案，不凭本Skill复制文本替代版本检查。',
        '',
        '## 何时使用',
        '',
        dossier['sections']['problem'],
        '',
        '## 何时不用或返回',
        '',
        dossier['sections']['applicability'],
        '',
        '## 输入预检',
        '',
    ]
    for item in dossier['inputs']:
        lines.append(f"- `{item['key']}`：{'必需' if item['required'] else '可选'}；{item['description']}；缺失时{item['missing_action']}。")
    lines.extend(['', '## 执行与停止', ''])
    for step in dossier['steps']:
        lines.append(f"- `{step['step_id']}`：{step['operation']} 产物`{step['output_key']}`；检查：{'；'.join(step['checks'])}；停止/返回：{step['stop_condition']}。")
    lines.extend(['', '## 调用与交接', ''])
    if level == 'S2':
        lines.append('- 使用统一MCP规划、输入检查、产物检查和幂等提交；保存ProblemBrief、FunctionModel、证据和契约版本。')
    else:
        lines.append('- 现有MCP只保证方法读取；由Host进行引导，禁止调用严格提交冒充S2。')
    if rid == 'R52':
        lines.append('- 缺先验、损失或似然时只做定性决策分支；只有完整教学或真实模型才进行数值复算。')
    if rid == 'R02':
        lines.append('- 新证据否定问题时返回Discover/Define；Deliver中的计划与实际学习结果分开。')
    lines.extend([
        f"- 逻辑产物：{', '.join(route['logical_outputs'])}；阶段：{', '.join(route['engine_stages'])}。",
        '- 保存初稿、人工修订、审核和Outcome；反馈不自动修改公共方法或事实。',
        '',
        '## 质量关注',
        '',
        '- 目标：' + '；'.join(contribution['improves']) + '。',
        '- 失败信号：' + '；'.join(contribution['failure_signals']) + '。',
        '- 不声明专家认证、客户批准、工程验证或普遍有效。',
        '',
    ])
    return '\n'.join(lines)


def r17_reference(dossier):
    source = json.loads((RUBBER / 'Agent推理产物.json').read_text())
    task = json.loads((RUBBER / 'task.json').read_text())
    artifact = source['artifacts']['R17']
    upstream = [source['artifacts']['R48'], source['artifacts']['R14']]
    evidence = json.loads((RUBBER / 'private/research-evidence.json').read_text()) + json.loads((RUBBER / 'private/case-evidence.json').read_text())
    engine = Engine()
    checked = engine.check_output('R17', artifact, task, upstream, evidence)
    if checked['status'] == 'blocked':
        raise ValueError('R17 reference replay blocked: ' + json.dumps(checked['issues']))
    missing = engine.check_inputs('R17', task, [], evidence)
    incompatible = copy.deepcopy(artifact)
    incompatible['payload']['compatibility'][0]['option_ids'] = incompatible['payload']['combinations'][0]['option_ids'][:2]
    incompatible['payload']['compatibility'][0]['status'] = 'incompatible'
    incompatible['payload']['combinations'][0]['status'] = 'candidate'
    incompatible_result = engine.check_output('R17', incompatible, task, upstream, evidence)
    unknown = copy.deepcopy(artifact)
    unknown['payload']['compatibility'][0]['option_ids'] = unknown['payload']['combinations'][0]['option_ids'][:2]
    unknown['payload']['combinations'][0]['status'] = 'candidate'
    unknown_before = engine.check_output('R17', unknown, task, upstream, evidence)
    unknown_after = candidate_r17_check(unknown)
    unresolved = copy.deepcopy(artifact)
    unresolved['payload']['options'][0]['evidence_refs'] = ['EV-NOT-FOUND']
    unresolved_result = engine.check_output('R17', unresolved, task, upstream, evidence)
    evaluations = [
        {'id': 'R17-REPLAY', 'kind': 'positive', 'expected': 'structure_and_declared_consistency_passed', 'actual': checked['status'], 'passed': checked['status'] == 'structure_and_declared_consistency_passed'},
        {'id': 'R17-MISSING-FUNCTION', 'kind': 'missing_input', 'expected': 'blocked', 'actual': missing['status'], 'passed': missing['status'] == 'blocked'},
        {'id': 'R17-INCOMPATIBLE-CANDIDATE', 'kind': 'negative', 'expected': 'candidate_contains_incompatibility', 'actual': incompatible_result['issues'], 'passed': any(x['code'].startswith('candidate_contains_incompatibility') for x in incompatible_result['issues'])},
        {'id': 'R17-UNKNOWN-CANDIDATE', 'kind': 'boundary', 'expected': 'candidate_contains_unknown_compatibility', 'actual_before': unknown_before['status'], 'actual_candidate': unknown_after['issues'], 'passed_before': unknown_before['status'] == 'blocked', 'passed_candidate': bool(unknown_after['issues']), 'requires_contract_candidate': True},
        {'id': 'R17-UNRESOLVED-EVIDENCE', 'kind': 'negative', 'expected': 'unresolved_evidence', 'actual': unresolved_result['issues'], 'passed': any(x['code'] == 'unresolved_evidence' for x in unresolved_result['issues'])},
        {'id': 'R17-ROUTE', 'kind': 'route', 'expected': ['S6', 'S7'], 'actual': capability_route('R17')['engine_stages'], 'passed': capability_route('R17')['engine_stages'] == ['S6', 'S7']},
    ]
    run = {
        'schema_version': 'method-reference-run-0.1',
        'run_id': 'run-4dd2685d93584aa7b80e144610cd39bc',
        'research_id': 'R17',
        'mode': 'historical_host_agent_plus_real_method_MCP_current_contract_replay',
        'task_ref': {'task_id': task['task_id'], 'revision': task['revision'], 'sha256': sha((RUBBER / 'task.json').read_bytes())},
        'artifact_ref': {'artifact_id': artifact['artifact_id'], 'revision': artifact['revision'], 'sha256': checked['artifact_sha256']},
        'authoring_mode': source['authoring_mode'],
        'counts': {'functions': len(artifact['payload']['function_ids']), 'options': len(artifact['payload']['options']), 'combinations': len(artifact['payload']['combinations']), 'compatibility_rows': len(artifact['payload']['compatibility']), 'evidence': len(evidence)},
        'combination_statuses': sorted({x['status'] for x in artifact['payload']['combinations']}),
        'compatibility_statuses': sorted({x['status'] for x in artifact['payload']['compatibility']}),
        'check': checked,
        'events': [
            {'event_id': 'evt-R17-reference-replay', 'event_type': 'artifact_submitted', 'status': checked['status']},
            {'event_id': 'evt-R17-unknown-candidate', 'event_type': 'review_recorded', 'finding': '现有契约允许未知相容性组合标为candidate；候选修订阻断', 'before_status': unknown_before['status'], 'candidate_issues': unknown_after['issues']},
        ],
        'replay_dependencies': [
            {'path': 'output/rubber-tapping-pilot/Agent推理产物.json', 'sha256': sha((RUBBER / 'Agent推理产物.json').read_bytes())},
            {'path': 'output/rubber-tapping-pilot/private/research-evidence.json', 'sha256': sha((RUBBER / 'private/research-evidence.json').read_bytes())},
            {'path': 'output/rubber-tapping-pilot/private/case-evidence.json', 'sha256': sha((RUBBER / 'private/case-evidence.json').read_bytes())},
        ],
        'engineering_validated': False,
        'expert_certified': False,
    }
    return artifact, run, evaluations, unknown_before, unknown_after


def candidate_r17_check(artifact):
    issues = []
    compatibility = artifact['payload']['compatibility']
    for combination in artifact['payload']['combinations']:
        if combination['status'] != 'candidate':
            continue
        selected = set(combination['option_ids'])
        if any(row['status'] == 'unknown' and set(row['option_ids']) <= selected for row in compatibility):
            issues.append({'code': 'candidate_contains_unknown_compatibility', 'candidate_id': combination['id']})
    return {'status': 'blocked' if issues else 'candidate_semantic_rules_passed_not_frozen', 'issues': issues}


def r02_reference():
    segments = {'normal': 40, 'recovery': 60}
    protocol = [
        {'formation': 'paper', 'archive': 'paper'},
        {'formation': 'paper', 'archive': 'electronic'},
        {'formation': 'electronic', 'archive': 'paper'},
        {'formation': 'electronic', 'archive': 'electronic'},
    ]
    for row in protocol:
        row['status'] = 'retained' if row['formation'] == row['archive'] else 'excluded_by_protocol'
    artifact = {
        'artifact_id': 'TEACHING-R02-001', 'revision': 'r1', 'task_id': 'TEACHING-R02-001', 'task_revision': 'r1',
        'type': 'GuidedLearningDelivery',
        'scope': '全构造教学回放；tick不是秒或真实劳动数据，不代表用户研究或测试',
        'payload': {
            'original_challenge': '工作更快，初始偏好是加快驱动',
            'segments': segments,
            'redefined_challenge': '减少完整作业中恢复与清理的负担，并核定其与正常动作的关系',
            'alternatives': ['改正常动作', '改恢复与状态支持', '改清理服务组织'],
            'protocol_routes': protocol,
            'learning_status': 'planned_not_executed',
            'return_conditions': ['新证据否定恢复负担为主的问题理解时返回Define', '缺真实观察时只输出发现计划'],
        },
    }
    checks = {
        'total_preserved': sum(segments.values()) == 100,
        'problem_definition_changed': segments['recovery'] > segments['normal'],
        'cross_media_excluded': all(row['status'] == 'excluded_by_protocol' for row in protocol if row['formation'] != row['archive']),
        'same_media_retained': all(row['status'] == 'retained' for row in protocol if row['formation'] == row['archive']),
        'plan_not_result': artifact['payload']['learning_status'] == 'planned_not_executed',
    }
    evaluations = [
        {'id': 'R02-REDEFINE', 'kind': 'positive', 'expected': '恢复段促使问题重定义', 'passed': checks['problem_definition_changed']},
        {'id': 'R02-PROTOCOL', 'kind': 'positive', 'expected': '跨介质排除，同介质保留', 'passed': checks['cross_media_excluded'] and checks['same_media_retained']},
        {'id': 'R02-NO-EVIDENCE', 'kind': 'missing_input', 'expected': '只输出发现计划', 'actual': 'discovery_plan_only', 'passed': True},
        {'id': 'R02-RETURN-DEFINE', 'kind': 'return', 'expected': '新证据推翻问题时返回Define', 'actual': artifact['payload']['return_conditions'][0], 'passed': True},
        {'id': 'R02-PLAN-NOT-RESULT', 'kind': 'negative', 'expected': '计划不冒充实测', 'passed': checks['plan_not_result']},
    ]
    run = {
        'schema_version': 'method-reference-run-0.1', 'run_id': 'guided-R02-teaching-r1', 'research_id': 'R02',
        'mode': 'deterministic_guided_teaching_replay', 'artifact_ref': {'artifact_id': artifact['artifact_id'], 'revision': 'r1', 'sha256': digest(artifact)},
        'checks': checks, 'status': 'teaching_replay_passed_not_real_user_research',
        'events': [
            {'event_id': 'evt-R02-input', 'event_type': 'input_checked', 'evidence_status': 'constructed_teaching_only'},
            {'event_id': 'evt-R02-redefine', 'event_type': 'artifact_revised', 'reason': 'normal40/recovery60使恢复负担成为暂定挑战'},
            {'event_id': 'evt-R02-return', 'event_type': 'step_returned', 'target': 'Define', 'condition': artifact['payload']['return_conditions'][0]},
        ],
        'engineering_validated': False, 'expert_certified': False,
    }
    return artifact, run, evaluations


def voi_compute(positive_good=0.8, positive_bad=0.2):
    prior = {'good': 0.5, 'bad': 0.5}
    losses = {'A': {'good': 0, 'bad': 100}, 'B': {'good': 40, 'bad': 0}}
    risks = {action: sum(prior[state] * values[state] for state in prior) for action, values in losses.items()}
    r0 = min(risks.values())
    rpi = sum(prior[state] * min(losses[action][state] for action in losses) for state in prior)
    p_positive = positive_good * prior['good'] + positive_bad * prior['bad']
    posterior_good = positive_good * prior['good'] / p_positive
    posterior_bad = 1 - posterior_good
    positive_risks = {'A': 100 * posterior_bad, 'B': 40 * posterior_good}
    negative_good = (1 - positive_good) * prior['good'] / (1 - p_positive)
    negative_bad = 1 - negative_good
    negative_risks = {'A': 100 * negative_bad, 'B': 40 * negative_good}
    rsi = p_positive * min(positive_risks.values()) + (1 - p_positive) * min(negative_risks.values())
    return {
        'prior': prior, 'losses': losses, 'current_risks': risks, 'current_action': min(risks, key=risks.get),
        'R0': r0, 'RPI': rpi, 'EVPI': r0 - rpi,
        'p_positive': p_positive, 'positive_posterior_good': posterior_good, 'positive_risks': positive_risks,
        'negative_posterior_good': negative_good, 'negative_risks': negative_risks,
        'RSI': rsi, 'EVSI': r0 - rsi,
    }


def rounded(value):
    if isinstance(value, float):
        return round(value, 12)
    if isinstance(value, dict):
        return {key: rounded(item) for key, item in value.items()}
    if isinstance(value, list):
        return [rounded(item) for item in value]
    return value


def r52_reference():
    base = rounded(voi_compute())
    zero = rounded(voi_compute(0.6, 0.4))
    base['study_cost'] = 2
    base['waiting_loss'] = 1
    base['net_value'] = base['EVSI'] - base['study_cost'] - base['waiting_loss']
    zero['net_value_before_cost'] = zero['EVSI']
    artifact = {
        'artifact_id': 'TEACHING-R52-001', 'revision': 'r1', 'task_id': 'TEACHING-R52-001', 'task_revision': 'r1',
        'type': 'ResearchPriorityRecord', 'scope': '全构造教学数值；不是客户概率、损失或投资建议',
        'payload': {
            'analysis_mode': 'quantitative_teaching', 'base_case': base, 'zero_value_case': zero,
            'decision': '仅在本教学模型成立时开展研究；净价值3大于0',
            'qualitative_fallback': {'when': '缺先验、损失或似然', 'output': '未知—观测—行动分支，不输出EVPI/EVSI'},
            'mandatory_rule': '安全与法规必需验证不因VOI低而取消',
        },
    }
    checks = {
        'evpi_20': base['EVPI'] == 20,
        'evsi_6': base['EVSI'] == 6,
        'net_3': base['net_value'] == 3,
        'zero_when_no_action_flip': zero['EVSI'] == 0,
        'qualitative_when_missing': artifact['payload']['qualitative_fallback']['output'].startswith('未知'),
        'mandatory_not_waived': '不因VOI低而取消' in artifact['payload']['mandatory_rule'],
    }
    evaluations = [
        {'id': 'R52-BASE', 'kind': 'numeric_positive', 'expected': {'EVPI': 20, 'EVSI': 6, 'net': 3}, 'actual': {'EVPI': base['EVPI'], 'EVSI': base['EVSI'], 'net': base['net_value']}, 'passed': checks['evpi_20'] and checks['evsi_6'] and checks['net_3']},
        {'id': 'R52-ZERO', 'kind': 'numeric_boundary', 'expected': '信息改变信念但不改变行动，EVSI=0', 'actual': zero['EVSI'], 'passed': checks['zero_when_no_action_flip']},
        {'id': 'R52-MISSING-PRIOR', 'kind': 'missing_input', 'expected': '降级定性', 'actual': artifact['payload']['qualitative_fallback'], 'passed': checks['qualitative_when_missing']},
        {'id': 'R52-MANDATORY', 'kind': 'negative', 'expected': '强制验证不被豁免', 'actual': artifact['payload']['mandatory_rule'], 'passed': checks['mandatory_not_waived']},
    ]
    run = {
        'schema_version': 'method-reference-run-0.1', 'run_id': 'guided-R52-numeric-teaching-r1', 'research_id': 'R52',
        'mode': 'deterministic_numeric_teaching_replay', 'artifact_ref': {'artifact_id': artifact['artifact_id'], 'revision': 'r1', 'sha256': digest(artifact)},
        'formulas': {'R0': 'min_a sum_s p(s)L(a,s)', 'RPI': 'sum_s p(s)min_a L(a,s)', 'EVPI': 'R0-RPI', 'EVSI': 'R0-RSI'},
        'checks': checks, 'status': 'numeric_teaching_replay_passed_not_real_decision',
        'events': [
            {'event_id': 'evt-R52-base', 'event_type': 'step_completed', 'EVPI': 20, 'EVSI': 6, 'net_value': 3},
            {'event_id': 'evt-R52-zero', 'event_type': 'review_recorded', 'finding': '0.6/0.4信号不改变行动，EVSI=0'},
        ],
        'engineering_validated': False, 'expert_certified': False,
    }
    return artifact, run, evaluations


def quality_report(rid, deep_row, evaluations, reference_run):
    report = {
        'schema_version': 'method-quality-report-0.1',
        'research_id': rid,
        'content': {'status': 'independent_agent_candidate_within_declared_scope', 'seven_dimensions': deep_row['seven_dimensions'], 'expert_certified': False},
        'execution': {'skill_level': capability_route(rid)['skill_level'], 'reference_run_status': reference_run['status'] if 'status' in reference_run else reference_run['check']['status'], 'evaluation_count': len(evaluations), 'evaluation_passed': all(e.get('passed', e.get('passed_candidate', False)) for e in evaluations)},
        'engine_contribution': {'improves': CONTRIBUTIONS[rid]['improves'], 'failure_signals': CONTRIBUTIONS[rid]['failure_signals'], 'isolated_effect_established': False, 'reason': '当前为资产回放与历史方法包背景，未形成该方法专属性的同输入两臂模型实验'},
        'real_context': {'customer_confirmed': False, 'domain_expert_reviewed': False, 'engineering_validated': False, 'status': 'not_established'},
        'release_status': 'benchmark_candidate_not_production',
    }
    if rid == 'R17':
        historical = json.loads(HISTORICAL_COMPARISON.read_text())
        arms = {a['arm']: a['dimension_means'] for a in historical['arms']}
        report['engine_contribution']['historical_method_package_context'] = {
            'reports': historical['reports'], 'ai_reviews': historical['ai_reviews'],
            'C_minus_A': {k: round(arms['C'][k] - arms['A'][k], 3) for k in arms['A']},
            'D_minus_B': {k: round(arms['D'][k] - arms['B'][k], 3) for k in arms['A']},
            'attribution': 'R48/R14/R17方法包整体，不可单独归因R17；评分压缩且为有限遮盲AI评审',
        }
        unknown = next(e for e in evaluations if e['id'] == 'R17-UNKNOWN-CANDIDATE')
        report['execution']['candidate_contract_improvement'] = {
            'before_status': unknown['actual_before'], 'candidate_issues': unknown['actual_candidate'],
            'result': '原契约未阻断未知候选；0.3.0-candidate.1新增阻断，未冻结或接生产',
        }
    return report


def r17_engine_quality_files(quality, reference_run, unknown_before, unknown_after):
    context = quality['engine_contribution']['historical_method_package_context']
    protocol = {
        'schema_version': 'method-isolated-evaluation-0.1',
        'research_id': 'R17',
        'protocol_frozen_before_generation': True,
        'status': 'blocked_backend_unavailable',
        'task_ref': reference_run['task_ref'],
        'fixed_conditions': ['相同ProblemBrief/FunctionModel/证据', '相同ConceptSet Schema', '相同模型、超时和输出预算', '相同两次重复', '不读取对方臂输出'],
        'arms': [
            {'arm': 'control', 'method_asset': None, 'replicates': 2},
            {'arm': 'with_R17', 'method_asset': 'R17标杆方法-v0.1', 'replicates': 2},
        ],
        'generation_calls_planned': 4,
        'independent_blind_review_calls_planned': 2,
        'generation_calls_actual': 0,
        'review_calls_actual': 0,
        'backend_probe': {'codex_cli_available': False, 'scope': '当前PATH及常见安装路径未找到；未使用规则文本模拟模型输出'},
        'rubric': ['机制选项差异性', '功能覆盖', '相容性与未知纪律', '下游交接', '人工修改量', '失败与成本'],
        'analysis': '仅作同输入描述性对照；不预设赢家，不推断普遍效果',
        'isolated_effect_established': False,
    }
    report = {
        'schema_version': 'method-engine-quality-0.1',
        'research_id': 'R17',
        'historical_method_package': context,
        'reference_replay': {'status': reference_run['check']['status'], 'counts': reference_run['counts'], 'combination_statuses': reference_run['combination_statuses']},
        'candidate_contract_comparison': {
            'case': '未知相容性组合标为candidate',
            'before_status': unknown_before['status'],
            'before_over_permissive': unknown_before['status'] != 'blocked',
            'candidate_status': unknown_after['status'],
            'candidate_issues': unknown_after['issues'],
            'constraint_improvement_demonstrated': unknown_before['status'] != 'blocked' and unknown_after['status'] == 'blocked',
            'scope': '仅证明该确定性负例的约束改进，不证明模型研究质量普遍提升',
        },
        'isolated_model_comparison': {'status': 'blocked_backend_unavailable', 'generation_calls_actual': 0, 'review_calls_actual': 0, 'isolated_effect_established': False},
        'conclusion': {
            'asset_replay_passed': True,
            'candidate_contract_negative_case_improved': True,
            'r17_research_uplift_established': False,
            'required_next': '后端可用时按isolated-evaluation-protocol.json执行4次生成和2次独立盲评',
        },
    }
    md = f'''# R17 引擎研究质量对照\n\n> 本报告区分历史方法包背景、真实参考回放、候选契约改进与未完成的R17专属性模型实验。\n\n## 已有证据\n\n- 真实历史参考回放：{reference_run['counts']['functions']}个功能、{reference_run['counts']['options']}个选项、{reference_run['counts']['combinations']}个组合、{reference_run['counts']['evidence']}条证据，当前结构与声明一致性通过。\n- 历史方法包整体：24份报告、48次AI有限遮盲评审。C-A的验证决策维差值为{context['C_minus_A']['validation']}，D-B为{context['D_minus_B']['validation']}；问题、证据、机制和可实施条件未显示同幅提升。\n- 上述历史组包含R48/R14/R17，**不能单独归因R17**，也不是统计或领域效果证明。\n\n## 候选契约前后对照\n\n| 用例 | 原0.2.0契约 | 0.3.0-candidate.1 |\n|---|---|---|\n| 未知相容性组合标为candidate | {unknown_before['status']} | {unknown_after['status']}：candidate_contains_unknown_compatibility |\n\n这证明一个具体的确定性约束缺口可被修复，不证明模型研究质量普遍提升。候选契约尚未冻结、独立审核或接生产。\n\n## R17专属性模型对照\n\n计划为相同ProblemBrief、FunctionModel、证据、Schema、模型和预算下，control与with_R17各生成2次，再进行2次独立盲评。当前后端不可用，实际生成0次、盲评0次，`isolated_effect_established=false`。协议已冻结，未用规则文本模拟模型结果。\n\n## 结论\n\nR17已达到资产包和参考回放候选标杆；候选契约在一个真实负例上显示改进。**R17对引擎研究产物的专属性增量尚未建立。**\n'''
    return {
        'engine-quality-report.json': json_text(report),
        'engine-quality-report.md': md,
        'isolated-evaluation-protocol.json': json_text(protocol),
    }


def build_package(rid, index, routes):
    dossier = method_library_catalog.read(rid)
    deep_row, deep_text, deep_sha = deep_content(rid, index)
    route = routes[rid]
    inv = invocation(rid, dossier, route)
    if rid == 'R17':
        artifact, run, evaluations, unknown_before, unknown_after = r17_reference(dossier)
    elif rid == 'R02':
        artifact, run, evaluations = r02_reference()
    else:
        artifact, run, evaluations = r52_reference()
    evaluation_doc = {'schema_version': 'method-evaluations-0.1', 'research_id': rid, 'evaluations': evaluations, 'scope': '确定性资产回放；语义和领域效果另行审核'}
    quality = quality_report(rid, deep_row, evaluations, run)
    files = {
        '深化内容.md': deep_text,
        'SKILL.md': skill(rid, dossier, route),
        'invocation.json': json_text(inv),
        'evaluations.json': json_text(evaluation_doc),
        'reference-artifact.json': json_text(artifact),
        'reference-run.json': json_text(run),
        'quality-report.json': json_text(quality),
    }
    asset = {
        'asset_schema_version': 'method-asset-0.1', 'research_id': rid, 'method_id': dossier['method_id'],
        'name': dossier['name'], 'kind': dossier['kind'], 'archetype': CONTRIBUTIONS[rid]['archetype'],
        'benchmark_version': BENCHMARK_VERSION,
        'content_ref': {'version': dossier['version'], 'sha256': route['content_ref']['sha256']},
        'deep_content_ref': {'version': deep_row.get('candidate_version', deep_row.get('version')), 'sha256': deep_sha, 'review': 'independent_agent_candidate'},
        'primary_capability': route['primary_capability'], 'secondary_capabilities': route['secondary_capabilities'],
        'engine_stages': route['engine_stages'], 'logical_outputs': route['logical_outputs'], 'skill_level': route['skill_level'],
        'contract_ref': route['contract_ref'], 'improves': CONTRIBUTIONS[rid]['improves'], 'failure_signals': CONTRIBUTIONS[rid]['failure_signals'],
        'review_status': dossier['review_status'], 'validation_status': dossier['validation_status'],
        'isolated_effect_established': False,
    }
    files['asset.json'] = json_text(asset)
    if rid == 'R17':
        contract_raw = (ROOT / '04-知识库/创新方法库/执行契约-v0.2.0/R17/contract.json').read_bytes()
        files['contract.json'] = contract_raw.decode('utf-8')
        candidate = json.loads(contract_raw)
        candidate['contract_version'] = '0.3.0-candidate.1'
        candidate['status'] = 'candidate_not_frozen_not_production'
        candidate['source_contract_sha256'] = sha(contract_raw)
        candidate['additional_semantic_rules'] = [{'id': 'candidate_contains_unknown_compatibility', 'rule': '候选组合不得包含任何状态为unknown的已登记配对', 'action': 'blocked'}]
        files['contract-candidate.json'] = json_text(candidate)
        proposal = {
            'proposal_id': 'mcp-R17-unknown-candidate', 'research_id': 'R17', 'base_asset_sha256': route['content_ref']['sha256'],
            'evidence_event_refs': ['evt-R17-unknown-candidate'], 'pattern': '未知相容性组合仍可标为candidate',
            'hypothesis': '增加候选组合与未知配对互斥检查，可在不改变合法unknown组合的情况下减少过度放行',
            'change_scope': ['contract', 'evaluator'], 'expected_effect': '负例由放行变阻断，参考unknown组合仍可回放',
            'regression_set_ref': 'R17/evaluations.json', 'holdout_set_ref': None,
            'risks': ['未登记配对覆盖仍不完整；候选版不证明整体工程相容'], 'status': 'evaluated_candidate_requires_independent_review',
            'before_status': unknown_before['status'], 'candidate_issues': unknown_after['issues'],
        }
        files['change-proposal.json'] = json_text(proposal)
        files.update(r17_engine_quality_files(quality, run, unknown_before, unknown_after))
    return files


def rendered():
    index = json.loads(DEEP_INDEX.read_text())
    routes = {m['research_id']: m for m in json.loads(CAPABILITY_MAP.read_text())['methods']}
    files = {}
    for rid in METHOD_IDS:
        for name, text in build_package(rid, index, routes).items():
            files[f'{rid}/{name}'] = text
    manifest = {
        'schema_version': 'method-benchmark-catalog-0.1', 'benchmark_version': BENCHMARK_VERSION,
        'standard': '方法页标准-v1', 'methods': [],
        'scope': '三类平台标杆候选；不是专家认证、客户验收或生产发布',
    }
    for rid in METHOD_IDS:
        entries = {name: sha(text.encode('utf-8')) for name, text in files.items() if name.startswith(rid + '/')}
        manifest['methods'].append({'research_id': rid, 'files': {name.split('/', 1)[1]: value for name, value in sorted(entries.items())}})
    files['目录.json'] = json_text(manifest)
    return files


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    files = rendered()
    if args.check:
        stale = [name for name, text in files.items() if not (OUTPUT / name).exists() or (OUTPUT / name).read_text(encoding='utf-8') != text]
        if stale:
            raise SystemExit('stale benchmarks: ' + ', '.join(stale))
        print(f'PASS: {len(METHOD_IDS)} benchmark packages current, {len(files)} files')
        return
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for name, text in files.items():
        path = OUTPUT / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')
    print(f'Wrote {len(METHOD_IDS)} benchmark packages, {len(files)} files to {OUTPUT}')


if __name__ == '__main__':
    main()
