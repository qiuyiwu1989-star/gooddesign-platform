"""ML-002: necessary-condition screening, never an expert certification service."""
DIMENSIONS = ('problem', 'principle', 'evidence', 'reasoning', 'coverage', 'value', 'usability', 'reproducibility')


def assess(packet):
    issues = []
    def require(condition, code):
        if not condition:
            issues.append(code)
    require(packet.get('level') in {'research', 'concept', 'engineering', 'validated'}, 'invalid_delivery_level')
    require(all(packet.get(k) for k in ('task_revision', 'method_versions', 'scope', 'author_id')), 'missing_provenance')
    claims = packet.get('claims', [])
    require(bool(claims), 'missing_claims')
    evidence = packet.get('evidence', [])
    ids = [e.get('id') for e in evidence]
    require(all(ids) and len(ids) == len(set(ids)), 'duplicate_or_empty_evidence_id')
    refs = {e.get('id'): e for e in evidence}
    for claim in claims:
        kind = claim.get('kind')
        require(kind in {'fact', 'inference', 'hypothesis'}, 'invalid_claim_kind')
        require(bool(claim.get('text')), 'empty_claim')
        if kind == 'hypothesis':
            require(bool(claim.get('verification_question')), 'hypothesis_without_test')
        if claim.get('critical') and kind in {'fact', 'inference'}:
            cited = claim.get('evidence_refs', [])
            require(bool(cited), 'critical_claim_without_evidence')
            for rid in cited:
                e = refs.get(rid, {})
                require(bool(e.get('source_revision') and e.get('locator')), 'unresolved_evidence')
                require(e.get('support_review') == 'supported', 'evidence_support_not_reviewed')
            if kind == 'inference':
                require(bool(claim.get('reasoning') and claim.get('assumptions') is not None), 'inference_without_chain')
    require(packet.get('hard_constraints_checked') is True, 'hard_constraints_unchecked')
    require(not packet.get('hard_constraint_violations'), 'hard_constraint_violation')
    require(not any(x.get('severity') in {'critical', 'major'} and x.get('status') != 'closed'
                    for x in packet.get('issues', [])), 'unclosed_serious_issue')
    reviews = packet.get('reviews', [])
    independent = [r for r in reviews if r.get('reviewer_id') and r['reviewer_id'] != packet.get('author_id')
                   and r.get('scope') == packet.get('scope') and r.get('qualification_checked') is True
                   and r.get('packet_revision') == packet.get('revision') and r.get('revision') is not None
                   and r.get('outcome') == 'accept']
    require(bool(independent), 'missing_current_independent_domain_review')
    for dimension in DIMENSIONS:
        item = packet.get('ratings', {}).get(dimension, {})
        score = item.get('score')
        if score == 'not_applicable':
            require(dimension == 'value' and bool(item.get('reason')), 'invalid_not_applicable')
        else:
            require(type(score) is int and 3 <= score <= 4 and bool(item.get('basis')), 'insufficient_dimension:'+dimension)
    if packet.get('level') in {'engineering', 'validated'}:
        require(bool(packet.get('engineering_records')), 'missing_engineering_records')
        require(packet.get('engineering_review') == 'accepted', 'engineering_not_reviewed')
    if packet.get('level') == 'validated':
        require(packet.get('verification_coverage') == 'complete' and bool(packet.get('validation_records')), 'validation_incomplete')
    return {'status': 'blocked' if issues else 'eligible_for_controlled_release',
            'issues': sorted(set(issues)), 'expert_certified': False,
            'scope': 'checks_declared_records_only_not_truth_or_credentials',
            'note': '通过必要条件检查不验证外部评审身份、证据真实性、语义支持或工程结果；发布责任仍在应用流程。'}
