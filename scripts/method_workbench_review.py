"""ML-009: deterministic declared-record review; never an engineering verdict."""
import hashlib
import itertools
import json


def review(state, evidence):
    artifacts = [s['artifact'] for s in state.get('submissions', [])]
    payloads = {a['type']: a.get('payload', {}) for a in artifacts}
    concept = payloads.get('ConceptSet', {})
    comparison = payloads.get('ComparisonRecord', {})
    options = {o['id']: o for o in concept.get('options', [])}
    known_refs = {e['id'] for e in evidence}
    anomalies = []
    records = {}
    for record in concept.get('compatibility', []):
        ids = record.get('option_ids', [])
        if len(ids) != 2 or len(set(ids)) != 2 or any(x not in options for x in ids):
            anomalies.append({'kind': 'invalid_pair', 'record': record})
            continue
        records.setdefault(tuple(sorted(ids)), []).append(record)
    candidates = []
    for combo in concept.get('combinations', []):
        ids = combo.get('option_ids', [])
        missing = [x for x in ids if x not in options]
        if missing or len(ids) != len(set(ids)):
            anomalies.append({'kind': 'invalid_combination', 'candidate_id': combo['id'], 'missing': missing})
        pairs = list(itertools.combinations(sorted(set(ids) & set(options)), 2))
        counts = dict(unreviewed=0, unknown=0, compatible=0, incompatible=0, disputed=0)
        examined = []
        for pair in pairs:
            rows = records.get(pair, [])
            statuses = {r.get('status', 'unknown') for r in rows}
            status = ('unreviewed' if not rows else 'disputed' if len(statuses) > 1 else next(iter(statuses)))
            if status not in counts:
                status = 'unknown'
            counts[status] += 1
            if rows:
                examined.append({'option_ids': list(pair), 'status': status, 'records': rows})
        judgments = []
        for criterion in comparison.get('criteria', []):
            rows = [j for j in comparison.get('judgments', []) if j.get('candidate_id') == combo['id'] and j.get('criterion_id') == criterion['id']]
            judgments.append({'criterion': criterion, 'records': rows, 'unresolved': len(rows) != 1 or rows[0].get('value') in (None, 'unknown')})
        candidates.append({'id': combo['id'], 'reason': combo.get('reason', ''), 'options': [options[x] for x in ids if x in options], 'pair_count': len(pairs), 'pair_counts': counts, 'examined_pairs': examined, 'judgments': judgments, 'hard_unresolved': sum(j['unresolved'] and j['criterion'].get('hard') is not False for j in judgments)})
    def scan(value, path='artifacts'):
        if isinstance(value, dict):
            for ref in value.get('evidence_refs', []):
                if ref not in known_refs:
                    anomalies.append({'kind': 'reference_not_in_run_evidence', 'ref': ref, 'path': path})
            for key, child in value.items():
                scan(child, path+'.'+key)
        elif isinstance(value, list):
            for i, child in enumerate(value):
                scan(child, path+'['+str(i)+']')
    scan(artifacts)
    stamp = hashlib.sha256(json.dumps({'artifacts': artifacts, 'evidence': evidence}, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    return {'version': 'declared-review-1', 'input_sha256': stamp, 'scope': 'declared_records_only_not_expert_or_engineering_verification', 'available': bool(concept), 'comparison_available': bool(comparison), 'candidates': candidates, 'anomalies': anomalies, 'unknowns': concept.get('unknowns', []), 'recommendations': comparison.get('recommendations', []), 'expert_certified': False}
