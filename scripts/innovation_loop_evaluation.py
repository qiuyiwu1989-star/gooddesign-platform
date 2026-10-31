"""ML024 private evaluation planning; no model/network/filesystem side effects."""
import copy
import hashlib
import json

ARMS = {'A': [], 'B': ['experience'], 'C': ['methods'], 'D': ['experience', 'methods']}

def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False).encode()).hexdigest()

def validate_protocol(protocol):
    if not isinstance(protocol, dict) or protocol.get('schema_version') != '0.1.0':
        raise ValueError('schema_version must be 0.1.0')
    for key in ('id', 'revision', 'missing_reason'):
        if key not in protocol:
            raise ValueError('missing ' + key)
    if not isinstance(protocol['id'], str) or not protocol['id'].strip() or type(protocol['revision']) is not int or protocol['revision'] < 1:
        raise ValueError('nonempty id and positive integer revision required')
    tasks = protocol.get('tasks')
    if not isinstance(tasks, list) or len(tasks) != 3:
        raise ValueError('exactly three task descriptors required')
    ids = [t.get('id') for t in tasks if isinstance(t, dict)]
    if len(ids) != 3 or any(not isinstance(i, str) or not i for i in ids) or len(set(ids)) != 3:
        raise ValueError('unique nonempty task IDs required')
    if protocol.get('arms') != ARMS or type(protocol.get('replicates')) is not int or protocol['replicates'] != 2:
        raise ValueError('four fixed arms and two replicates required')
    if protocol.get('failure_policy') != 'retain_all_no_best_of' or protocol.get('network_allowed') is not False:
        raise ValueError('retain failures; offline comparison required')
    if protocol.get('status') not in ('draft', 'frozen'):
        raise ValueError('draft or frozen status required')
    blockers = []
    for key in ('model', 'budget', 'reviewers', 'business_effect_threshold', 'randomization_seed'):
        if protocol.get(key) is None:
            blockers.append(key)
    model = protocol.get('model')
    budget = protocol.get('budget')
    reviewers = protocol.get('reviewers')
    if not isinstance(model, dict) or not all(isinstance(model.get(k), str) and model[k].strip() for k in ('id', 'version')):
        blockers.append('model_details')
    if not isinstance(budget, dict) or any(type(budget.get(k)) is not int or budget[k] < 1 for k in ('max_output_chars', 'max_seconds', 'max_tokens')):
        blockers.append('budget_details')
    if not isinstance(reviewers, list) or len(reviewers) < 2 or any(not isinstance(r, dict) or not all(isinstance(r.get(k), str) and r[k].strip() for k in ('id','role','independence_statement')) for r in reviewers):
        blockers.append('reviewer_details')
    if isinstance(reviewers, list) and all(isinstance(r,dict) for r in reviewers):
        reviewer_ids = [r.get('id') for r in reviewers]
        if any(not isinstance(i,str) for i in reviewer_ids) or len(set(reviewer_ids)) != len(reviewer_ids):
            blockers.append('reviewer_ids_unique')
        if any(r.get('is_author') is not False for r in reviewers):
            blockers.append('reviewer_author_independence')
    if type(protocol.get('randomization_seed')) is not int:
        blockers.append('randomization_seed_type')
    if not isinstance(protocol.get('business_effect_threshold'), str) or not protocol['business_effect_threshold'].strip():
        blockers.append('business_threshold_details')
    for task in tasks:
        sha = task.get('input_sha256')
        if sha is not None and (not isinstance(sha,str) or len(sha)!=64 or any(c not in '0123456789abcdef' for c in sha)):
            raise ValueError('invalid input_sha256')
        if not task.get('input_sha256') or task.get('input_status') not in ('research_proposal', 'customer_confirmed', 'constructed'):
            blockers.append('task:' + task['id'])
    if blockers and not protocol['missing_reason']:
        raise ValueError('pending inputs require missing_reason')
    if protocol['status'] == 'frozen' and blockers:
        raise ValueError('cannot freeze unresolved protocol: ' + ', '.join(blockers))
    return {'valid': True, 'execution_ready': not blockers and protocol['status'] == 'frozen', 'blockers': blockers}

def build_run_matrix(protocol):
    validation = validate_protocol(protocol)
    return {'schema_version': '0.1.0', 'protocol_sha256': _digest(protocol),
            'execution_ready': validation['execution_ready'], 'runs': [
                {'run_id': f"{protocol['id']}:{t['id']}:{arm}:{rep}", 'task_id': t['id'],
                 'arm': arm, 'replicate': rep, 'additional_materials': copy.deepcopy(materials),
                 'status': 'planned', 'output_sha256': None}
                for t in protocol['tasks'] for arm, materials in ARMS.items() for rep in (1, 2)]}

def audit_completeness(protocol, records):
    matrix = build_run_matrix(protocol)
    if not isinstance(records, list):
        raise ValueError('records must be list')
    expected = {r['run_id'] for r in matrix['runs']}
    seen, errors, completed, failed = set(), [], [], []
    for record in records:
        rid = record.get('run_id')
        if rid not in expected:
            errors.append({'run_id': rid, 'error': 'unknown_run'})
        if rid in seen:
            errors.append({'run_id': rid, 'error': 'duplicate_run'})
        seen.add(rid)
        if record.get('protocol_sha256') != matrix['protocol_sha256']:
            errors.append({'run_id': rid, 'error': 'protocol_mismatch'})
        if record.get('status') == 'succeeded' and record.get('output_sha256') and record.get('output_ref'):
            completed.append(rid)
        elif record.get('status') == 'failed' and record.get('failure_reason'):
            failed.append(rid)
        else:
            errors.append({'run_id': rid, 'error': 'missing_output_or_failure'})
    missing = sorted(expected - seen)
    return {'expected': len(expected), 'succeeded': len(completed), 'failed': len(failed),
            'missing': missing, 'errors': errors, 'complete': not missing and not errors,
            'effectiveness_established': False, 'execution_ready': matrix['execution_ready'],
            'artifact_bytes_verified': False, 'audit_scope': 'structure_only'}

def build_anonymous_package(records, seed):
    """Return separate JSON reviewer/private objects; caller persists separately.

    Reject known labels/paths in body rather than silently rewriting research text.
    Randomized identifiers reproducible for a fixed seed; seed stays private.
    """
    import random
    import re
    if not isinstance(records, list) or not records or type(seed) is not int:
        raise ValueError('nonempty records and integer seed required')
    rng = random.Random(seed)
    rows = copy.deepcopy(records)
    rng.shuffle(rows)
    seen, public, mapping = set(), [], []
    for row in rows:
        rid, body = row.get('run_id'), row.get('text')
        if not isinstance(rid, str) or not rid or rid in seen or not isinstance(body, str) or not body.strip():
            raise ValueError('unique run_id and nonempty text required')
        seen.add(rid)
        forbidden = [rid] + [row[k] for k in ('source_path','source_filename') if row.get(k)]
        if any(not isinstance(s,str) for s in forbidden):
            raise ValueError('path labels must be strings')
        if any(s in body for s in forbidden) or re.search(r'(?:/Volumes/|/Users/|file://|[A-Za-z]:\\)',body):
            raise ValueError('body leaks source metadata; explicit human review required')
        anon='P-'+format(rng.getrandbits(128),'032x')
        public.append({'anonymous_id':anon,'text':body,'text_sha256':hashlib.sha256(body.encode()).hexdigest()})
        mapping.append({'anonymous_id':anon,'run_id':rid,'source_path':row.get('source_path'),
                        'source_filename':row.get('source_filename'),'text_sha256':public[-1]['text_sha256']})
    return {'reviewer_package':{'schema_version':'0.1.0','papers':public,
             'notice':'Limited blinding: prose may reveal treatment; no effectiveness conclusion.'},
            'private_mapping':{'seed':seed,'mapping':mapping},'permission_enforcement':False}


def audit_artifacts(protocol, records, artifact_root):
    """Read-only byte audit under explicit caller root; no path escape or symlinks."""
    from pathlib import Path
    structural = audit_completeness(protocol, records)
    root = Path(artifact_root).resolve(strict=True)
    if not root.is_dir():
        raise ValueError('artifact_root must be directory')
    errors, checked = [], []
    for record in records:
        if record.get('status') != 'succeeded':
            continue
        rid = record.get('run_id')
        ref = record.get('output_ref')
        digest = record.get('output_sha256')
        try:
            if not isinstance(ref,str) or not ref or Path(ref).is_absolute() or '..' in Path(ref).parts:
                raise ValueError('relative output_ref without traversal required')
            relative = Path(ref)
            if any((root.joinpath(*relative.parts[:i])).is_symlink() for i in range(1,len(relative.parts)+1)):
                raise ValueError('symlinks rejected')
            path = (root / relative).resolve(strict=True)
            path.relative_to(root)
            if not path.is_file():
                raise ValueError('not regular file')
            if not isinstance(digest,str) or len(digest)!=64 or any(c not in '0123456789abcdef' for c in digest):
                raise ValueError('invalid output_sha256')
            raw = path.read_bytes()
            if not raw or hashlib.sha256(raw).hexdigest()!=digest:
                raise ValueError('empty output or SHA mismatch')
            checked.append(rid)
        except (OSError,ValueError) as exc:
            errors.append({'run_id':rid,'error':str(exc)})
    return {'structural_audit':structural,'artifact_errors':errors,'checked_outputs':checked,
            'artifact_bytes_verified':not errors, 'complete':structural['complete'] and not errors,
            'effectiveness_established':False,'audit_scope':'structure_and_bytes'}
