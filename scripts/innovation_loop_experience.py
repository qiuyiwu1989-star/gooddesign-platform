"""ML024 private, read-only design experience adapter; no semantic approval."""
import copy
import json
import hashlib
from pathlib import Path


def validate_experience(record):
    if not isinstance(record, dict) or record.get('schema_version') != '0.1.0':
        raise ValueError('unsupported experience schema')
    for key in ('id', 'object_scope', 'limitations'):
        if not isinstance(record.get(key), str) or not record[key].strip():
            raise ValueError('missing ' + key)
    if type(record.get('revision')) is not int or record['revision'] < 1:
        raise ValueError('positive integer revision required')
    if record.get('visibility') != 'internal_research':
        raise ValueError('experience is private research only')
    for key in ('problem', 'constraints', 'mechanism', 'tradeoffs', 'validation_context'):
        claim = record.get(key)
        if not isinstance(claim, dict) or claim.get('nature') not in ('source_statement', 'inferred', 'hypothesized'):
            raise ValueError('invalid claim ' + key)
        if claim.get('value') is None:
            if not claim.get('missing_reason'):
                raise ValueError('unknown requires missing_reason')
        elif not isinstance(claim['value'], str) or not claim['value'].strip():
            raise ValueError('claim value must be nonempty text or null')
        elif not claim.get('evidence_ids'):
            raise ValueError('claim requires evidence')
    refs = record.get('evidence_refs', [])
    ids = set()
    for ref in refs:
        if not isinstance(ref, dict):
            raise ValueError('evidence reference must be object')
        auth = ref.get('authorization')
        if not isinstance(auth, dict) or set(auth) != {'purpose', 'status', 'origin_kind', 'basis'}:
            raise ValueError('explicit evidence authorization required')
        if auth['purpose'] != 'internal_research' or auth['status'] not in ('unknown', 'granted', 'denied') or auth['origin_kind'] not in ('public_excerpt', 'private_material', 'unknown'):
            raise ValueError('invalid authorization scope')
        if not isinstance(auth['basis'], str) or not auth['basis'].strip():
            raise ValueError('authorization basis or missing explanation required')
        if auth['status'] == 'granted' and auth['origin_kind'] == 'unknown':
            raise ValueError('unknown origin cannot establish permission')
        if 'permission' in ref:
            raise ValueError('use explicit authorization, not ambiguous permission')
        if ref.get('id') in ids:
            raise ValueError('duplicate evidence id')
        ids.add(ref.get('id'))
        for key in ('id','project_id','research_revision','record_id','field','source_id','chunk_id','quote','chunks_sha256','source_sha256','dataset_path','dataset_sha256','object_scope','read_scope'):
            if not ref.get(key):
                raise ValueError('missing evidence ' + key)
        for key in ('chunks_sha256','source_sha256','dataset_sha256'):
            if len(ref[key]) != 64 or any(c not in '0123456789abcdef' for c in ref[key]):
                raise ValueError('invalid sha')
    if not refs:
        raise ValueError('missing evidence')
    for key in ('problem','constraints','mechanism','tradeoffs','validation_context'):
        if not set(record[key].get('evidence_ids', [])).issubset(ids):
            raise ValueError('dangling evidence')
    return copy.deepcopy(record)


def load_experiences(path):
    data = json.loads(Path(path).read_text())
    if not isinstance(data, list):
        raise ValueError('expected list')
    records = [validate_experience(r) for r in data]
    if len({r['id'] for r in records}) != len(records):
        raise ValueError('duplicate experience id')
    return records


def search_experiences(records, query, limit=5):
    if not isinstance(query, str) or not query.strip() or isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 50:
        raise ValueError('query and limit 1..50 required')
    words = query.casefold().split()
    hits = []
    for record in records:
        r = validate_experience(record)
        if any(ref['authorization']['status'] != 'granted' for ref in r['evidence_refs']):
            continue
        # Only search visible explanatory fields, never file paths or SHA values.
        hay = json.dumps({k:r[k] for k in ('object_scope','problem','constraints','mechanism','tradeoffs','validation_context','limitations')},ensure_ascii=False).casefold()
        matched = [w for w in words if w in hay]
        if matched:
            hits.append({'experience':r,'match':{'kind':'literal_terms','terms':matched,'semantic_similarity':None}})
    return {'results':hits[:limit],'total':len(hits),'query':query,'notice':'Unauthorized or permission-unknown samples are excluded. Literal retrieval over private bounded samples; empty does not mean no knowledge; not migration approval.'}
