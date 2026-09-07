"""Build provenance-preserving public metadata from the original archive."""
import json, hashlib
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / '99-历史项目快照/good-design/public'
EMPTY = {'', '无', '待补充', '暂无', '暂无资料', '无。'}
def meaningful(value):
    return isinstance(value, str) and value.strip() not in EMPTY

def build(output):
    awards = json.loads((SRC / 'awards.json').read_text())
    rows = []
    for a in awards:
        pid = a['slug']; path = SRC / f'cases/detail/{pid}.json'
        d = json.loads(path.read_text()) if path.exists() else {}
        rows.append({'id': pid, 'name': a['name'], 'year': a['year'], 'award': a['level'],
            'unit': a.get('unit', ''), 'description_status': 'archive_text' if meaningful(d.get('desc')) else 'missing',
            'review_status': 'unverified_archive', 'project_url': f'/project/{pid}.html',
            'knowledge_url': f'/atom/{pid}.html', 'source_url': f'/cases/detail/{pid}.json' if path.exists() else None})
    demo = json.loads((ROOT / 'extensions/public/industry-demo/data.json').read_text())
    mechanisms = []
    for c, keyword in zip(demo['cases'], ['接口', '工程约束', '过抛']):
        path = SRC / f"cases/detail/{c['id']}.json"; raw = path.read_bytes(); d = json.loads(raw)
        field = next(k for k in ['desc', 'features'] if keyword in d.get(k, ''))
        value = d[field]; paragraphs = value.split('\n'); paragraph = next(p for p in paragraphs if keyword in p)
        start = value.index(paragraph)
        mechanisms.append({'id': 'mechanism-' + c['id'], 'project_id': c['id'],
            'source': {'url': f"/cases/detail/{c['id']}.json", 'field': field, 'start': start,
                       'end': start + len(paragraph), 'sha256': hashlib.sha256(raw).hexdigest()},
            'excerpt': paragraph, 'analysis': c['insight'], 'analysis_status': 'platform_hypothesis',
            'review_status': 'pending_expert_review', 'triz_mapping': None, 'validation_result': None})
    output.mkdir(parents=True, exist_ok=True)
    result = {'schema_version': '0.1', 'projects': rows, 'mechanisms': mechanisms,
              'coverage': {'projects': len(rows), 'descriptions_missing': sum(r['description_status']=='missing' for r in rows),
                           'mechanism_samples': len(mechanisms), 'expert_reviewed_mechanisms': 0}}
    (output / 'project-index.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    return result
if __name__ == '__main__':
    print(json.dumps(build(ROOT/'original-app/public/knowledge-data')['coverage'], ensure_ascii=False))
