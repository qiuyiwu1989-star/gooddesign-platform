# coding: utf-8
import collections
import json
from pathlib import Path

import agent_intake
import project_pipeline as pp
import research_assessment as ra
import research_workflow as rw

ROOT = pp.ROOT
LIB = ROOT / '04-知识库/项目库'
OUT = ROOT / 'output/research-088'
BATCHES = ('20261103-doubao-full-01', '20261103-doubao-patents-01')


def main():
    projects = json.loads((LIB / '项目索引.json').read_text())['projects']
    summary = {
        'schema': 'gooddesign-research-round-audit-1.0',
        'index_projects': len(projects),
        'unique_project_ids': len({row['id'] for row in projects}),
        'missing_project_directories': [],
        'missing_material_directories': [],
        'standard_batch_coverage': {},
        'standard_batch_validation': {},
        'standard_batch_counts': {},
        'native_research': {},
        'dimension_stages': {},
        'exceptions': [],
        'official_ingestion': False,
        'semantic_review_completed': False,
        'quality_score_assigned': False,
    }
    revision_counts = collections.Counter()
    batch_counts = collections.Counter()
    native_counts = collections.Counter()
    dimension_counts = collections.Counter()
    native_rows = []
    queue_rows = {'A_no_standard_no_native': [], 'B_standard_no_native': [], 'C_standard_with_native': [], 'D_no_standard_with_native': []}
    for row in projects:
        pid = row['id']
        p = LIB / pid
        if not p.is_dir():
            summary['missing_project_directories'].append(pid)
        if not (p / '04-深研素材').is_dir():
            summary['missing_material_directories'].append(pid)
        has_standard = (p / '04-深研素材/外部投递' / BATCHES[0]).is_dir()
        work = rw.current(p)
        has_native = work['revision'] > 0
        revision_counts[work['revision']] += 1
        key = 'C_standard_with_native' if has_standard and has_native else 'B_standard_no_native' if has_standard else 'D_no_standard_with_native' if has_native else 'A_no_standard_no_native'
        queue_rows[key].append({'id': pid, 'name': row['name'], 'year': row['year'], 'award': row['award']})
        if has_native:
            revision = 'research-%06d' % work['revision']
            data = rw.dataset(p, work)
            audit = ra.audit(p, data)
            native_counts['projects'] += 1
            native_counts['records'] += len(data['records'])
            native_counts['known_fact_cells'] += audit['known_cells']
            native_counts['ai_items'] += audit['ai_items']
            native_counts['traceable_known_cells'] += audit['traceable_known_cells']
            native_counts['traceable_bounded_ai_items'] += audit['traceable_bounded_ai_items']
            native_counts['registered_cells'] += audit['registered_cells']
            native_counts['issues'] += len(audit['issues'])
            native_counts['audit_' + audit['status']] += 1
            native_rows.append({'id': pid, 'name': row['name'], 'facts': audit['known_cells'], 'ai_items': audit['ai_items'], 'status': audit['status'], 'issues': len(audit['issues'])})
            try:
                judgment = ra.read(p, revision)['report']['judgment']
                for dimension in judgment['dimensions']:
                    dimension_counts[(dimension['key'], dimension['stage'])] += 1
            except (ValueError, KeyError, OSError):
                native_counts['assessment_unavailable'] += 1
    for bid in BATCHES:
        summary['standard_batch_coverage'][bid] = 0
        summary['standard_batch_validation'][bid] = {}
        summary['standard_batch_counts'][bid] = {}
    for pid in sorted(row['id'] for row in projects):
        for bid in BATCHES:
            batch = LIB / pid / '04-深研素材/外部投递' / bid
            if not batch.is_dir():
                continue
            summary['standard_batch_coverage'][bid] += 1
            result = agent_intake.validate(batch)
            status = result['status']
            summary['standard_batch_validation'][bid][status] = summary['standard_batch_validation'][bid].get(status, 0) + 1
            for key, value in result.get('counts', {}).items():
                summary['standard_batch_counts'][bid][key] = summary['standard_batch_counts'][bid].get(key, 0) + value
            if status != 'mechanical_pass_pending_content_review':
                summary['exceptions'].append({'project_id': pid, 'batch_id': bid, 'errors': result['errors'], 'kind': 'batch_reference_integrity'})
    summary['revision_distribution'] = dict(sorted(revision_counts.items()))
    summary['native_research'] = dict(native_counts)
    summary['dimension_stages'] = {f'{key}/{stage}': count for (key, stage), count in sorted(dimension_counts.items())}
    summary['queue_counts'] = {key: len(value) for key, value in queue_rows.items()}
    summary['lowest_native_fact_projects'] = sorted(native_rows, key=lambda item: item['facts'])[:20]
    summary['baseline_evidence_exception'] = {
        'project_id': '2025-00',
        'kind': 'legacy_baseline_missing_frozen_evidence_objects',
        'explanation': '旧人工底稿主要以source_ids引用，缺少当前审计器要求的逐字段冻结evidence对象；不是简单原文丢失，但不得直接当作新版证据链完整。',
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'audit-summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (OUT / 'queues.json').write_text(json.dumps({'schema': 'gooddesign-research-queues-1.0', 'counts': summary['queue_counts'], 'queues': queue_rows}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'index_projects': summary['index_projects'], 'standard_batch_coverage': summary['standard_batch_coverage'], 'standard_batch_validation': summary['standard_batch_validation'], 'native_research': summary['native_research'], 'queue_counts': summary['queue_counts'], 'exceptions': summary['exceptions']}, ensure_ascii=False, indent=2))
    return summary


if __name__ == '__main__':
    main()
