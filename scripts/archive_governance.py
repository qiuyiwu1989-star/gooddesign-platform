# coding: utf-8
"""100: build and validate version-bound MVA projections without changing research truth."""
import argparse
import copy
import datetime
import hashlib
import json
import os
import tempfile
from pathlib import Path

import jsonschema

import project_pipeline as pp
import project_ownership as own
import research_assessment
import research_workflow as rw

ROOT = pp.ROOT
LIB = pp.LIB
STANDARD = ROOT / '04-知识库/项目档案标准-v1/档案治理-v1'
SCHEMAS = {name: json.loads((STANDARD / f'{name}.schema.json').read_text())
           for name in ('mva', 'source-asset', 'claim')}
GENERATOR = 'archive_governance.py/1.0'
EVIDENCE_FIELDS = (
    'source_id', 'source_sha256', 'chunk_id', 'chunks_path', 'chunks_sha256',
    'locator', 'quote', 'quote_sha256', 'source_read_scope',
)


def sha_bytes(value):
    return hashlib.sha256(value).hexdigest()


def schema_errors(schema_name, value, prefix):
    validator = jsonschema.validators.validator_for(SCHEMAS[schema_name])(SCHEMAS[schema_name])
    return [f'{prefix}{"/" + "/".join(map(str, error.path)) if error.path else ""}: {error.message}'
            for error in validator.iter_errors(value)]


def claim_schema_errors(claim):
    validator = jsonschema.validators.validator_for(SCHEMAS['claim'])(SCHEMAS['claim'])
    missing = {}
    errors = []
    for error in validator.iter_errors(claim):
        path = list(error.path)
        if len(path) >= 2 and path[0] == 'evidence' and error.validator == 'required':
            field = error.message.split("'")[1]
            missing.setdefault(path[1], []).append(field)
        else:
            location = '/'.join(map(str, path))
            errors.append(f'claim/{claim.get("identity_key", "?")}{"/" + location if location else ""}: {error.message}')
    for index, fields in sorted(missing.items()):
        errors.append(f'claim/{claim.get("identity_key", "?")}/evidence/{index}: 冻结证据缺字段 {", ".join(sorted(fields))}')
    return errors


def project_row(project_id):
    projects = json.loads((LIB / '项目索引.json').read_text())['projects']
    row = next((item for item in projects if item['id'] == project_id), None)
    if not row:
        raise ValueError('未知项目：' + project_id)
    return row


def source_projection(p):
    state = pp.state(p)
    registry = own.registry(p)
    selected = own.select(p, state['sources'], reg=registry)
    rows = []
    errors = []
    warnings = []
    for sid, source in sorted(selected.items()):
        assignment = own.assignment(p, sid, state['sources'], registry)
        assets = []
        hashes = {}
        for role, key in (('original', 'original'), ('readable', 'document'), ('chunks', 'chunks')):
            relative = source.get(key)
            if not relative:
                if role == 'original':
                    errors.append(f'source/{sid}: 缺登记原文件')
                continue
            try:
                path = pp.safe(p, relative)
                digest = pp.sha(path.read_bytes())
                assets.append({'role': role, 'path': relative, 'sha256': digest})
                hashes[role] = digest
                if role == 'original' and digest != source.get('sha256'):
                    errors.append(f'source/{sid}: 原文件指纹与登记不符')
                if role == 'chunks' and source.get('chunks_sha256') and digest != source['chunks_sha256']:
                    errors.append(f'source/{sid}: 证据块指纹与登记不符')
            except (OSError, ValueError) as exc:
                errors.append(f'source/{sid}/{role}: {exc}')
        if 'original' in hashes and hashes['original'] == hashes.get('readable'):
            warnings.append(f'source/{sid}: 原文件与可读件同指纹，只按一个证据来源计数')
        rows.append({
            'schema': 'gooddesign-source-asset-1.0',
            'source_id': sid,
            'project_id': p.name,
            'title': source.get('title') or sid,
            'read_scope': source.get('read_scope') or 'unread',
            'review_status': source.get('review_status') or 'unreviewed',
            'project_relation': 'project_source',
            'relation_basis': assignment.get('reason') or '当前项目归属已登记，语义关系待核',
            'original_verified': False,
            'origin': source.get('origin'),
            'assets': assets,
        })
    return rows, errors, warnings


def claim_id(project_id, record_id, field):
    identity = f'{project_id}/{record_id}/{field}'.encode()
    return 'CLAIM-' + sha_bytes(identity)[:16]


def claim_projection(p, data, revision):
    claims = []
    platform_entries = []
    for record in data.get('records', []):
        for field, cell in record.get('cells', {}).items():
            if cell.get('value_state') != 'known' or cell.get('value') is None:
                continue
            nature = cell.get('content_nature')
            if nature in ('platform_metadata', 'platform_analysis'):
                platform_entries.append({
                    'record_id': record['id'], 'field': field,
                    'content_nature': nature, 'value': cell['value'],
                })
                continue
            if nature != 'source_statement':
                continue
            raw_evidence = cell.get('evidence') or {}
            evidence = ({key: raw_evidence[key] for key in EVIDENCE_FIELDS if key in raw_evidence}
                        if isinstance(raw_evidence, dict) else {})
            if 'locator' not in evidence and cell.get('locator'):
                evidence['locator'] = cell['locator']
            claims.append({
                'schema': 'gooddesign-claim-1.0',
                'claim_id': claim_id(p.name, record['id'], field),
                'identity_key': f'{record["id"]}/{field}',
                'project_id': p.name,
                'research_revision': revision,
                'record_id': record['id'],
                'field': field,
                'title': record.get('title') or record['id'],
                'value': cell['value'],
                'content_nature': 'source_statement',
                'verification_state': cell.get('verification_state') or 'unspecified',
                'evidence': [evidence],
                'conditions': cell.get('conditions') or '',
                'limitations': cell.get('limitations') or '',
                'human_read': False,
                'expert_reviewed': False,
                'engineering_validated': False,
            })
    return claims, platform_entries


def assessment_state(p, revision, dataset_sha256):
    result = research_assessment.safe_read(p, revision)
    if result['status'] != 'available':
        return {'status': result['status'], 'current': False}
    judgment = result['report']['judgment']
    current = judgment.get('dataset_sha256') == dataset_sha256
    return {
        'status': 'available_current' if current else 'stale',
        'current': current,
        'version': judgment.get('version'),
        'research_revision': judgment.get('research_revision'),
        'dataset_sha256': judgment.get('dataset_sha256'),
    }


def build_mva(p):
    revision = 'research-%06d' % rw.current(p)['revision']
    folder, _ = rw.check_version(p, revision)
    archive_path = folder / '档案.json'
    data = json.loads(archive_path.read_text())
    dataset_sha256 = pp.sha(archive_path.read_bytes())
    sources, source_errors, source_warnings = source_projection(p)
    claims, platform_entries = claim_projection(p, data, revision)
    row = project_row(p.name)
    original_hashes = {
        asset['sha256'] for source in sources for asset in source['assets'] if asset['role'] == 'original'
    }
    doc = {
        'schema': 'gooddesign-mva-1.0',
        'project': {'id': p.name, 'name': row.get('name') or row.get('title'),
                    'year': row.get('year'), 'award': row.get('award') or ''},
        'research_revision': revision,
        'dataset_sha256': dataset_sha256,
        'sources': sources,
        'claims': claims,
        'platform_entries': platform_entries,
        'review': {
            'agent_assessment': assessment_state(p, revision, dataset_sha256),
            'human_read': False,
            'expert_reviewed': False,
            'engineering_validated': False,
            'full_research_complete': False,
            'official_ingestion': False,
            'semantic_review': False,
            'quality_score': None,
        },
        'metrics': {
            'records': len(data.get('records', [])),
            'known_cells': len(claims) + len(platform_entries),
            'source_statement_claims': len(claims),
            'platform_metadata_cells': sum(x['content_nature'] == 'platform_metadata' for x in platform_entries),
            'platform_analysis_cells': sum(x['content_nature'] == 'platform_analysis' for x in platform_entries),
            'project_sources': len(sources),
            'unique_original_files': len(original_hashes),
            'traceable_claims': 0,
        },
        'status': {'mva_ready': False, 'blockers': source_errors, 'warnings': source_warnings},
        'gaps': source_errors.copy(),
        'provenance': {
            'generator': GENERATOR,
            'source_archive_path': f'研究工作区/版本/{revision}/档案.json',
            'generated_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'derived_not_hand_edited': True,
        },
    }
    return doc


def validate_mva(p, doc, check_files=True):
    errors = list(doc.get('status', {}).get('blockers', []))
    warnings = list(doc.get('status', {}).get('warnings', []))
    errors += schema_errors('mva', doc, 'mva')
    for source in doc.get('sources', []):
        errors += schema_errors('source-asset', source, f'source/{source.get("source_id", "?")}')
    for claim in doc.get('claims', []):
        errors += claim_schema_errors(claim)
    revision = 'research-%06d' % rw.current(p)['revision']
    folder, _ = rw.check_version(p, revision)
    current_sha = pp.sha((folder / '档案.json').read_bytes())
    if doc.get('research_revision') != revision or doc.get('dataset_sha256') != current_sha:
        errors.append('mva: 投影已偏离当前研究版本')
    claim_ids = [claim.get('claim_id') for claim in doc.get('claims', [])]
    if len(claim_ids) != len(set(claim_ids)):
        errors.append('mva: claim_id 不唯一')
    sources = {source.get('source_id'): source for source in doc.get('sources', [])}
    if check_files:
        for sid, source in sources.items():
            for asset in source.get('assets', []):
                try:
                    path = pp.safe(p, asset['path'])
                    if pp.sha(path.read_bytes()) != asset['sha256']:
                        errors.append(f'source/{sid}/{asset["role"]}: 文件指纹不符')
                except (OSError, ValueError, KeyError) as exc:
                    errors.append(f'source/{sid}: {exc}')
    traceable = 0
    unique_evidence = set()
    for claim in doc.get('claims', []):
        evidence_rows = claim.get('evidence') or []
        claim_ok = bool(evidence_rows)
        for evidence in evidence_rows:
            sid = evidence.get('source_id')
            if sid not in sources:
                if sid is not None:
                    errors.append(f'claim/{claim["identity_key"]}: 来源不在当前项目来源表')
                claim_ok = False
                continue
            if not all(field in evidence for field in EVIDENCE_FIELDS):
                claim_ok = False
                continue
            if check_files:
                try:
                    rw.evidence(p, evidence)
                    unique_evidence.add((sid, evidence['chunk_id'], evidence['quote_sha256']))
                except (ValueError, KeyError, TypeError, OSError) as exc:
                    errors.append(f'claim/{claim["identity_key"]}: {exc}')
                    claim_ok = False
        traceable += int(claim_ok)
    doc['metrics']['traceable_claims'] = traceable
    doc['metrics']['unique_frozen_evidence'] = len(unique_evidence)
    doc['status'] = {
        'mva_ready': not errors,
        'blockers': sorted(set(errors)),
        'warnings': sorted(set(warnings)),
    }
    doc['gaps'] = doc['status']['blockers'].copy()
    return doc['status']


def audit(p):
    doc = build_mva(p)
    validate_mva(p, doc)
    return {
        'schema': 'gooddesign-mva-audit-1.0',
        'project_id': p.name,
        'research_revision': doc['research_revision'],
        'dataset_sha256': doc['dataset_sha256'],
        'mva_ready': doc['status']['mva_ready'],
        'metrics': doc['metrics'],
        'review': doc['review'],
        'blockers': doc['status']['blockers'],
        'warnings': doc['status']['warnings'],
    }


def write_mva(p):
    with pp.lock(LIB):
        doc = build_mva(p)
        status = validate_mva(p, doc)
        if not status['mva_ready']:
            raise ValueError(f'MVA 门禁未通过：{len(status["blockers"])} 个阻断项；请先运行 audit')
        destination = rw.workspace(p) / '治理/mva' / f'{doc["research_revision"]}.json'
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            old = json.loads(destination.read_text())
            old_compare = copy.deepcopy(old)
            new_compare = copy.deepcopy(doc)
            old_compare['provenance']['generated_at'] = ''
            new_compare['provenance']['generated_at'] = ''
            if old_compare == new_compare:
                return {'status': 'no_changes', 'path': str(destination), 'metrics': doc['metrics']}
            raise ValueError('同一研究版本的 MVA 已存在且内容不同，禁止覆盖')
        with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=destination.parent,
                                         prefix='.mva-', delete=False) as stream:
            temp = Path(stream.name)
            json.dump(doc, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
        os.replace(temp, destination)
        return {'status': 'written', 'path': str(destination), 'metrics': doc['metrics']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('audit', 'write'))
    parser.add_argument('project_id')
    parser.add_argument('--out', type=Path, help='audit 可选输出路径；不会写入研究真源')
    args = parser.parse_args()
    p = pp.project(LIB, args.project_id)
    result = audit(p) if args.action == 'audit' else write_mva(p)
    if args.action == 'audit' and args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
