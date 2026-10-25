"""ML-003: authored six-method contracts; structural/declared semantics, not expert truth."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

CONTRACT_VERSION = '0.2.1'
OVERLAY = Path(__file__).resolve().parents[1]/('04-知识库/创新方法库/执行契约-v'+CONTRACT_VERSION)


def obj(properties, required=None):
    return {'type': 'object', 'properties': properties, 'required': list(properties) if required is None else required,
            'additionalProperties': False}


TEXT = {'type': 'string', 'minLength': 1, 'maxLength': 6000, 'pattern': r'\S'}
ID = {'type': 'string', 'pattern': r'^[A-Za-z0-9][A-Za-z0-9_.:-]{0,99}$'}
def arr(item, minimum=0):
    return {'type': 'array', 'items': item, 'minItems': minimum, 'maxItems': 200}
def enum(*values):
    return {'type': 'string', 'enum': list(values)}

REFS = arr(ID)
CONDITION = obj({'id': ID, 'text': TEXT, 'kind': enum('fact', 'assumption', 'unknown'), 'evidence_refs': REFS})
REQUIREMENT = obj({'id': ID, 'text': TEXT, 'hard': {'type': ['boolean', 'null']}, 'acceptance': TEXT,
                   'status': enum('confirmed', 'proposed', 'unknown'), 'evidence_refs': REFS})
QUANTITY = obj({'value': {'type': 'number'}, 'unit': TEXT, 'condition': TEXT, 'evidence_refs': REFS})

PAYLOADS = {
 'R48': ('ProblemBrief', obj({'actor': TEXT, 'object': TEXT, 'boundary': TEXT, 'desired_outcome': TEXT,
     'requirements': arr(REQUIREMENT, 1), 'conditions': arr(CONDITION), 'unknowns': arr(TEXT)})),
 'R14': ('FunctionModel', obj({'boundary': TEXT,
     'functions': arr(obj({'id': ID, 'verb_object': TEXT, 'necessity': enum('necessary', 'supporting', 'unknown'), 'evidence_refs': REFS}), 1),
     'flows': arr(obj({'id': ID, 'from_function': ID, 'to_function': ID, 'flow_type': enum('material', 'energy', 'signal'), 'description': TEXT, 'evidence_refs': REFS})),
     'interfaces': arr(CONDITION), 'unknowns': arr(TEXT)})),
 'R17': ('ConceptSet', obj({'function_ids': arr(ID, 1),
     'options': arr(obj({'id': ID, 'function_id': ID, 'principle': TEXT, 'conditions': arr(TEXT), 'evidence_refs': REFS}), 1),
     'combinations': arr(obj({'id': ID, 'option_ids': arr(ID, 1), 'status': enum('candidate', 'excluded', 'unknown'), 'reason': TEXT}), 1),
     'compatibility': arr(obj({'option_ids': arr(ID, 2), 'status': enum('compatible', 'incompatible', 'unknown'), 'reason': TEXT, 'evidence_refs': REFS})),
     'unknowns': arr(TEXT)})),
 'R36': ('ComparisonRecord', obj({'requirements_revision': ID, 'baseline_id': ID, 'candidate_ids': arr(ID, 1),
     'criteria': arr(obj({'id': ID, 'text': TEXT, 'hard': {'type': 'boolean'}, 'requirement_ids': arr(ID)}), 1),
     'judgments': arr(obj({'candidate_id': ID, 'criterion_id': ID, 'value': enum('better', 'same', 'worse', 'unknown', 'pass', 'fail'), 'basis': TEXT, 'evidence_refs': REFS}), 1),
     'recommendations': arr(ID), 'sensitivity': arr(TEXT), 'unknowns': arr(TEXT)})),
 'R44': ('PrototypePlan', obj({'hypothesis': TEXT, 'learning_goal': TEXT, 'scope': TEXT,
     'procedure': arr(TEXT, 1), 'measurements': arr(obj({'id': ID, 'observable': TEXT, 'unit_or_scale': TEXT, 'criterion': TEXT}), 1),
     'uncovered_questions': arr(TEXT), 'execution_status': enum('planned')})),
 'R42': ('VerificationPlan', obj({'requirements_revision': ID,
     'matrix': arr(obj({'requirement_id': ID, 'purpose': enum('verification', 'validation'),
         'method': enum('inspection', 'analysis', 'demonstration', 'test'), 'criterion': TEXT,
         'configuration': TEXT, 'evidence_status': enum('none', 'planned'), 'evidence_refs': REFS}), 1),
     'validation_questions': arr(TEXT), 'uncovered_requirements': arr(ID), 'execution_status': enum('planned')})),
}

META = {
 'R48': {'purpose': '澄清对象、目标、需求和约束', 'requires': [], 'stage': 'frame', 'next': ['R14'],
         'stop': '关键对象或使用边界未知时先澄清；愿望不能伪装成已批准要求。'},
 'R14': {'purpose': '把任务转成必要功能与作用接口', 'requires': ['ProblemBrief'], 'stage': 'model', 'next': ['R17'],
         'stop': '未经证实的作用关系不得写成已确认根因。'},
 'R17': {'purpose': '从子功能选项组合候选概念', 'requires': ['ProblemBrief', 'FunctionModel'], 'stage': 'generate', 'next': ['R36'],
         'stop': '成对相容不代表整体可行；矛盾或条件未知要保留。'},
 'R36': {'purpose': '用硬门槛和相对判断筛选概念', 'requires': ['ProblemBrief', 'ConceptSet'], 'stage': 'compare', 'next': ['R44'],
         'stop': '硬门槛未知或失败的候选不能作为已通过的推荐。'},
 'R44': {'purpose': '将关键假设转为原型学习计划', 'requires': ['ProblemBrief', 'ConceptSet', 'ComparisonRecord'], 'stage': 'prototype', 'next': ['R42'],
         'stop': '未执行计划不能含实测结果；外观原型不证明寿命。'},
 'R42': {'purpose': '建立要求验证和预期使用确认的证据计划', 'requires': ['ProblemBrief', 'PrototypePlan'], 'stage': 'verify', 'next': [],
         'stop': 'verification与validation分开；计划就绪不代表产品通过。'},
}

INPUT_BINDINGS = {
 'R48': {'initial_request':'task', 'stakeholder_evidence':'evidence', 'constraints_context':'task.boundary', 'decision_authority':'task.decision_authority'},
 'R14': {'requirements':'artifact:ProblemBrief.payload.requirements', 'conops':'task'},
 'R17': {'task':'artifact:ProblemBrief', 'functions':'artifact:FunctionModel.payload.functions', 'options':'task.known_options', 'conditions':'artifact:ProblemBrief.payload.conditions'},
 'R36': {'problem_requirements':'artifact:ProblemBrief.payload.requirements', 'concepts':'artifact:ConceptSet.payload', 'evidence':'evidence', 'decision_preferences':'task.preferences'},
 'R44': {'design_intent':'artifact:ProblemBrief', 'assumptions':'artifact:ComparisonRecord.payload.unknowns', 'experiment_resources':'task.resources', 'prototype_evidence':'evidence'},
 'R42': {'requirements':'artifact:ProblemBrief.payload.requirements', 'intended_use':'task', 'product_configuration':'artifact:PrototypePlan.payload.scope', 'test_capabilities':'task.resources'},
}


def contract(rid):
    kind, payload = PAYLOADS[rid]
    schema = obj({'artifact_id': ID, 'revision': ID, 'task_id': ID, 'task_revision': ID,
                  'type': enum(kind), 'scope': TEXT, 'conditions': arr(CONDITION),
                  'evidence_refs': REFS, 'payload': payload})
    result = {'contract_version': CONTRACT_VERSION, 'research_id': rid, 'artifact_type': kind,
            'schema': deepcopy(schema), **deepcopy(META[rid]),
            'input_bindings': deepcopy(INPUT_BINDINGS[rid]),
            'status': 'platform_authored_not_expert_reviewed',
            'evidence_rule': '引用必须解析；字段存在不证明内容受证据支持。'}
    marker=OVERLAY/'发布冻结.json'
    if marker.exists():
        frozen=json.loads(marker.read_text())
        if hashlib.sha256(Path(__file__).read_bytes()).hexdigest()!=frozen['validator_module_sha256']:
            raise ValueError('contract_validator_code_changed_create_new_version')
        actual=hashlib.sha256(json.dumps(result,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
        if frozen['contract_hashes'].get(rid)!=actual:raise ValueError('contract_release_changed_create_new_version')
    return result


def semantic_issues(rid, artifact):
    """Only call after schema validation. Return declared consistency errors."""
    p, issues = artifact['payload'], []
    def unique(values, label):
        if len(values) != len(set(values)):
            issues.append('duplicate:'+label)
    if rid == 'R48':
        unique([x['id'] for x in p['requirements']], 'requirement')
        if any(x['status'] == 'confirmed' and not x['evidence_refs'] for x in p['requirements']):
            issues.append('confirmed_requirement_without_evidence')
    if rid == 'R14':
        ids = [x['id'] for x in p['functions']]; unique(ids, 'function')
        for f in p['flows']:
            if f['from_function'] not in ids or f['to_function'] not in ids:
                issues.append('flow_unknown_function:'+f['id'])
    if rid == 'R17':
        unique(p['function_ids'], 'function'); unique([x['id'] for x in p['options']], 'option')
        options = {x['id']: x for x in p['options']}
        for option in options.values():
            if option['function_id'] not in p['function_ids']:
                issues.append('option_unknown_function:'+option['id'])
        for row in p['compatibility']:
            if not set(row['option_ids']) <= set(options):
                issues.append('compatibility_unknown_option')
        for c in p['combinations']:
            selected = c['option_ids']; unique(selected, 'combination_option')
            if not set(selected) <= set(options):
                issues.append('combination_unknown_option:'+c['id']); continue
            functions = [options[x]['function_id'] for x in selected]
            if set(functions) != set(p['function_ids']) or len(functions) != len(set(functions)):
                issues.append('combination_incomplete_or_duplicate_function:'+c['id'])
            if c['status'] == 'candidate' and any(x['status'] == 'incompatible' and set(x['option_ids']) <= set(selected) for x in p['compatibility']):
                issues.append('candidate_contains_incompatibility:'+c['id'])
    if rid == 'R36':
        unique(p['candidate_ids'], 'candidate'); unique([x['id'] for x in p['criteria']], 'criterion')
        criteria = {x['id']: x for x in p['criteria']}
        keys = [(x['candidate_id'], x['criterion_id']) for x in p['judgments']]; unique(keys, 'judgment')
        for j in p['judgments']:
            if j['candidate_id'] not in p['candidate_ids'] or j['criterion_id'] not in criteria:
                issues.append('judgment_unknown_id')
            if j['value'] != 'unknown' and not j['evidence_refs']:
                issues.append('judgment_without_evidence')
        for candidate in p['recommendations']:
            if candidate not in p['candidate_ids']:
                issues.append('recommendation_unknown_candidate')
            for criterion in criteria.values():
                rows = [j for j in p['judgments'] if j['candidate_id'] == candidate and j['criterion_id'] == criterion['id']]
                if criterion['hard'] and (len(rows) != 1 or rows[0]['value'] != 'pass'):
                    issues.append('recommendation_hard_gate_not_passed:'+candidate)
        if p['baseline_id'] not in p['candidate_ids']:
            issues.append('baseline_not_in_candidates')
    if rid == 'R42':
        covered={x['requirement_id'] for x in p['matrix']}
        if covered.intersection(p['uncovered_requirements']):
            issues.append('uncovered_requirements_already_in_matrix')
        unique(p['uncovered_requirements'],'uncovered_requirement')
        if any(x['evidence_refs'] for x in p['matrix']):
            issues.append('plan_rows_cannot_contain_completed_verification_evidence_use_background_refs_at_envelope')
    return sorted(set(issues))
