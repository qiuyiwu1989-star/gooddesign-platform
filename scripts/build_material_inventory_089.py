# coding: utf-8
import csv
import datetime
import json
from pathlib import Path

import agent_intake
import research_workflow as rw

ROOT = agent_intake.ROOT
LIB = ROOT / '04-知识库/项目库'
OUT = ROOT / 'output/research-089'
BATCHES = ('20261103-doubao-full-01', '20261103-doubao-patents-01')
REQUIRED = (
    '01-素材总览.md', '02-新闻报道.md', '03-论文与专利.md', '04-图片素材',
    '05-来源清单.md', '06-技术参数与对标.md', '07-专利与论文明细.md',
    '08-企业与市场数据.md', '09-时间线与荣誉.md',
)
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.svg', '.bmp', '.tif', '.tiff'}
FIELDS = (
    'project_id', 'project_name', 'year', 'award', 'material_bytes',
    'raw_source_files', 'raw_source_bytes', 'image_files', 'image_bytes',
    'full_sources', 'full_claims', 'full_queries', 'full_status',
    'patents_sources', 'patents_claims', 'patents_queries', 'patents_status',
    'native_revision', 'gaps',
)


def files(folder, extensions=None):
    if not folder.is_dir():
        return []
    result = []
    for path in folder.rglob('*'):
        if path.is_symlink() or not path.is_file() or path.name == '.DS_Store':
            continue
        if extensions and path.suffix.lower() not in extensions:
            continue
        result.append(path)
    return result


def main():
    projects = json.loads((LIB / '项目索引.json').read_text())['projects']
    rows = []
    totals = {
        'material_bytes': 0, 'raw_source_files': 0, 'raw_source_bytes': 0,
        'image_files': 0, 'image_bytes': 0, 'full_sources': 0, 'patents_sources': 0,
        'native_projects': 0,
    }
    gap_counts = {}
    for project in projects:
        pid = project['id']
        material = LIB / pid / '04-深研素材'
        material_files = files(material)
        raw_files = files(material / '原始信息')
        image_files = files(material / '04-图片素材', IMAGE_EXTENSIONS)
        material_bytes = sum(path.stat().st_size for path in material_files)
        raw_bytes = sum(path.stat().st_size for path in raw_files)
        image_bytes = sum(path.stat().st_size for path in image_files)
        row = {
            'project_id': pid,
            'project_name': project['name'],
            'year': project['year'],
            'award': project['award'],
            'material_bytes': material_bytes,
            'raw_source_files': len(raw_files),
            'raw_source_bytes': raw_bytes,
            'image_files': len(image_files),
            'image_bytes': image_bytes,
        }
        gaps = []
        missing_required = [name for name in REQUIRED if not (material / name).exists()]
        if missing_required:
            gaps.append('缺文档:' + '/'.join(missing_required))
        if not raw_files:
            gaps.append('无原始来源文件')
        if not image_files:
            gaps.append('无图片素材')
        for bid, prefix in zip(BATCHES, ('full', 'patents')):
            batch = material / '外部投递' / bid
            if not batch.is_dir():
                row[prefix + '_sources'] = 0
                row[prefix + '_claims'] = 0
                row[prefix + '_queries'] = 0
                row[prefix + '_status'] = 'missing'
                gaps.append('缺' + prefix + '标准批')
                continue
            result = agent_intake.validate(batch)
            row[prefix + '_sources'] = len(agent_intake.rows(batch / 'sources.jsonl'))
            row[prefix + '_claims'] = len(agent_intake.rows(batch / 'claims.jsonl'))
            row[prefix + '_queries'] = len(agent_intake.rows(batch / 'queries.jsonl'))
            row[prefix + '_status'] = result['status']
            if result['status'] != 'mechanical_pass_pending_content_review':
                gaps.append(prefix + '校验异常')
            if prefix == 'patents':
                claims = agent_intake.rows(batch / 'claims.jsonl')
                if any(claim.get('kind') == 'lead' for claim in claims):
                    gaps.append('专利仅lead待核')
        revision = rw.current(LIB / pid)['revision']
        row['native_revision'] = 'research-%06d' % revision if revision else ''
        if not revision:
            gaps.append('未生成原生研究版')
        if pid == '2025-00':
            gaps.append('旧底稿证据绑定异常')
        row['gaps'] = '；'.join(gaps)
        rows.append(row)
        for key in ('material_bytes', 'raw_source_files', 'raw_source_bytes', 'image_files', 'image_bytes'):
            totals[key] += row[key]
        for key in ('full_sources', 'patents_sources'):
            totals[key] += row[key]
        totals['native_projects'] += int(bool(revision))
        for gap in gaps:
            gap_counts[gap] = gap_counts.get(gap, 0) + 1
    summary = {
        'schema': 'gooddesign-material-inventory-1.0',
        'generated_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'projects': len(rows),
        'totals': totals,
        'gap_counts': dict(sorted(gap_counts.items())),
        'meaning': '文件和条目盘点，不代表独立来源、全文核读、研究完整度或质量分。full/patents按JSONL实际条目分开计数，不因校验失败归零；raw_source_files是原始信息目录文件数，image_files是图片文件数。',
    }
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / 'material-inventory.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    (OUT / 'material-inventory.json').write_text(json.dumps({'summary': summary, 'projects': rows}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (OUT / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


if __name__ == '__main__':
    main()
