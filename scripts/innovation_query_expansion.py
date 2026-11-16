"""Opt-in vocabulary hypotheses, not semantic equivalence or fact creation."""
import copy
import re
import innovation_knowledge as ik

VERSION = 'query-expansion-0.1'
# Explicit directional retrieval hints. Broad analogies are deliberately excluded.
RULES = [
    ('energy-recovery', ['制动能量回收', '刹车回收能量'], ['再生制动', '能量回馈']),
    ('variable-speed', ['电机调速', '调整电机转速'], ['变频调速']),
    ('linear-motion', ['旋转运动变直线运动', '转动转换成直线移动'], ['旋转运动转化为往复直线运动']),
    ('low-friction', ['降低摩擦', '减少摩擦', '降低管壁摩擦'], ['润滑层', '润滑剂']),
    ('dual-beam', ['激光双束', '两束激光'], ['双光束']),
    ('vibration', ['vibration compensation', '振动补偿'], ['compensate for the vibration', '振动抑制']),
]


def expand(query):
    if not isinstance(query, str) or not 1 <= len(query.strip()) <= 200:
        raise ValueError('query_must_be_1_to_200_characters')
    # No automatic expansion under negation; polarity needs semantic judgement.
    if re.search(r'不|无需|禁止|避免使用|without|\bnot\b', query, re.I):
        return {'query': query, 'expansions': [], 'reason': 'negation_requires_review', 'version': VERSION}
    rows = []
    for ident, triggers, terms in RULES:
        if any(ik._norm(t) in ik._norm(query) for t in triggers):
            rows.extend(dict(term=t, rule_id=ident, relation='directional_retrieval_hint_not_equivalence') for t in terms)
    return {'query': query, 'expansions': rows, 'version': VERSION,
            'scope': 'hand_authored_development_vocabulary_not_general_semantic_retrieval'}


def search(index, query, limit=8):
    if type(limit) is not int or not 1 <= limit <= 30:
        raise ValueError('limit_must_be_1_to_30')
    plan = expand(query)
    # Keep all literal hits ahead of expansions; rank changes remain explicit.
    direct = ik.search(index, functions=[query], limit=30)
    rows = [dict(**m, retrieval_route='literal') for m in direct['matches']]
    seen = {m['node']['id'] for m in rows}
    for hint in plan['expansions']:
        result = ik.search(index, functions=[hint['term']], limit=30)
        for m in result['matches']:
            if m['node']['id'] in seen:
                continue
            seen.add(m['node']['id'])
            rows.append(dict(**copy.deepcopy(m), retrieval_route='vocabulary_expansion',
                             expansion_basis=hint, target_applicability='unverified'))
    return {'project_id': index['project_id'], 'revision': index['revision'],
            'index_sha256': index['index_sha256'], 'query_plan': plan,
            'matches': rows[:limit], 'pooled_candidates': len(rows),
            'literal_total_matches': direct['total_matches'],
            'candidate_pool_per_term_limit': 30, 'returned_limit': limit,
            'limitations': ['受控词汇扩展不证明同义、机制等价或目标适用',
                            '每词最多30候选，完整性仍受库覆盖和上限限制',
                            '原逐字检索接口与历史结果不被替换']}
