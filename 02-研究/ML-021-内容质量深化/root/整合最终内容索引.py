"""Merge independently reviewed manuscripts; integrity checks do not judge content."""
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
REPO = BASE.parents[1]
REVIEWS = [
    BASE / 'needs/独立审核-function/final-review.json',
    BASE / 'function/独立审核-validation/final-review.json',
    BASE / 'validation/独立审核-needs/final-review.json',
]
EXPECTED = {f'R{i:02}' for i in range(1, 53)} | {f'WB{i:02}' for i in range(1, 13)}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def main():
    entries = {}
    reports = []
    for review in REVIEWS:
        data = json.loads(review.read_text())
        reports.append({'path': str(review.relative_to(REPO)), 'sha256': sha(review)})
        raw_items = data.get('items', data.get('methods', []))
        for raw in raw_items:
            if 'seven_dimensions' in raw:
                item = dict(raw)
            else:
                assert raw['review_status'] == 'independent_content_review_passed_with_explicit_scope'
                assert not raw['blocking_findings']
                item = {**raw, 'sha256': raw['candidate_sha256'],
                        'version': raw['candidate_version'],
                        'seven_dimensions': {d['dimension']: d for d in raw['dimensions']},
                        'disposition': 'content_candidate_pass'}
            if isinstance(item['seven_dimensions'], list):
                item['seven_dimensions'] = {d['dimension']: d for d in item['seven_dimensions']}
            method = item['method_id']
            assert method not in entries, method
            p = Path(item['candidate_path'])
            if not p.is_absolute():
                p = REPO / p
            assert sha(p) == item['sha256'], f'stale content review: {method}'
            assert item['disposition'] == 'content_candidate_pass', f'open blocker: {method}'
            assert len(item['seven_dimensions']) == 7, method
            entries[method] = {**item, 'candidate_path': str(p.relative_to(REPO)),
                               'independent_review': str(review.relative_to(REPO)),
                               'online_published': False}
    assert set(entries) == EXPECTED
    gaps = json.loads((BASE / '64项内容缺口台账.json').read_text())
    names = {m['method_id']: m['name'] for m in gaps['methods']}
    ordered = [entries[k] for k in sorted(entries)]
    partial = [{'method_id': e['method_id'], 'dimension': k,
                'assessment': v.get('assessment', v.get('rating')), 'details': v}
               for e in ordered for k, v in e['seven_dimensions'].items()
               if v.get('assessment', v.get('rating')) == '局部']
    partial_ids = {p['method_id'] for p in partial}
    result = {
        'round': 'ML-021', 'count': len(entries), 'status': 'independent_agent_content_candidates',
        'scope': '在各篇明确来源与教学范围内通过独立Agent内容审；不是领域专家认证、工程实测、客户批准或部署验收',
        'reviews': reports, 'partial_dimensions_not_closed': partial,
        'content_review_counts': {'all_seven_dimensions_sufficient_within_scope': len(entries) - len(partial_ids),
                                  'limited_teaching_candidate_with_partial_dimension': len(partial_ids),
                                  'unresolved_reported_editorial_blockers': 0},
        'methods': [{**e, 'name': names[e['method_id']]} for e in ordered],
    }
    save(BASE / '64项最终内容索引.json', result)
    lines = ['# 64项方法深化阅读索引', '',
             '以下指向本轮经独立内容审核及修订复核的最终稿。初审中的待修结论以各组 final-review.json 为准。', '',
             '本轮完成正文深化；尚未替换线上内容。教学例、公开资料与真实工程证据在正文中分别标明。', '',
             'WB01、WB02、WB04、WB05、WB06的原著专章机制仍评为局部：可阅读明确署名的平台教学，不能当作原法深层细则已补全。', '',
             '| 方法 | 名称 | 最终正文 | 独立审核 |', '|---|---|---|---|']
    for e in ordered:
        p = REPO / e['candidate_path']
        r = REPO / e['independent_review']
        lines.append(f"| {e['method_id']} | {names[e['method_id']]} | [阅读]({p.relative_to(BASE).as_posix()}) | [审核]({r.relative_to(BASE).as_posix()}) |")
    (BASE / '03-64项最终阅读索引.md').write_text('\n'.join(lines) + '\n')
    for m in gaps['methods']:
        e = entries[m['method_id']]
        m.update(candidate_path=e['candidate_path'], content_accepted=True,
                 acceptance_scope=result['scope'], independent_review=e['independent_review'],
                 candidate_sha256=e['sha256'], online_published=False,
                 substantive_deepening_complete_within_scope=m['method_id'] not in partial_ids)
    save(BASE / '64项内容缺口台账.json', gaps)
    task_path = REPO / '00-项目管理/ML-021-内容质量深化/任务台账.json'
    tasks = json.loads(task_path.read_text())
    for t in tasks['tasks']:
        e = entries[t['method_id']]
        group = e['candidate_path'].split('/')[2]
        external = {'needs': ['needs/未解决项.json'],
                    'function': ['function/尚需外部材料.md'],
                    'validation': ['validation/实际外部缺口.json', 'validation/R49外部缺口勘误.json']}[group]
        t.update(status=('limited_teaching_candidate_with_source_gap' if t['method_id'] in partial_ids
                         else 'independent_agent_content_candidate_pass'), content_accepted=True,
                 substantive_deepening_complete_within_scope=t['method_id'] not in partial_ids,
                 acceptance_scope=result['scope'], candidate_path=e['candidate_path'],
                 candidate_sha256=e['sha256'], dimensions=e['seven_dimensions'],
                 independent_review=e['independent_review'], online_published=False,
                 external_gaps=[{'source': str((BASE / x).relative_to(REPO)),
                                 'scope': '按方法ID核对；原典完整实施和真实工程/客户结论仍受外部材料限制'} for x in external])
    save(task_path, tasks)
    print(json.dumps({'methods': len(entries), 'reviewed_sha_matches': True,
                      'scope': 'integrity check only; substantive decisions reside in three independent reviews'}, ensure_ascii=False))

if __name__ == '__main__':
    main()
