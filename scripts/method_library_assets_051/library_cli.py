"""Portable, read-only access to this released research library (Python 3.9+)."""
import argparse
import hashlib
import json
import re
from pathlib import Path


def load(path):
    return json.loads(path.read_text(encoding='utf-8'), parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['search', 'read', 'verify'])
    parser.add_argument('--library', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--query', default='')
    parser.add_argument('--id', default='')
    parser.add_argument('--level', choices=['overview', 'steps', 'sources', 'full'], default='overview')
    parser.add_argument('--step-id')
    args = parser.parse_args()
    rows = load(args.library / '目录.json')['methods']
    if args.command == 'verify':
        manifest = load(args.library/'manifest.json')['files']
        bad = []
        root = args.library.resolve()
        for name, expected in manifest.items():
            path = (root/name).resolve()
            if not path.is_relative_to(root) or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
                bad.append(name)
        actual = {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() and p.name != 'manifest.json'}
        extras = sorted(actual-set(manifest))
        result = {'status': 'passed' if not bad and not extras else 'failed', 'files': len(manifest),
                  'changed_or_missing': bad, 'unlisted_files': extras,
                  'scope': 'file_integrity_not_source_authenticity_or_engineering_validation'}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        raise SystemExit(0 if result['status'] == 'passed' else 1)
    elif args.command == 'search':
        tokens = args.query.casefold().split()
        matches = [r for r in rows if all(t in json.dumps(r, ensure_ascii=False).casefold() for t in tokens)]
        result = {'search_type': 'catalog_keywords_not_semantic', 'total': len(matches), 'data': matches}
    else:
        if not re.fullmatch(r'(R\d{2}|WB\d{2}|IM-[A-Z]{2}-\d{3})', args.id):
            parser.error('档案ID格式无效')
        row = next((r for r in rows if args.id in {r['research_id'], r['method_id']}), None)
        if row is None:
            parser.error('档案不存在')
        if not re.fullmatch(r'(R\d{2}|WB\d{2})', row['research_id']):
            parser.error('目录研究ID格式无效')
        path = args.library / '档案' / row['research_id'] / '档案.json'
        if hashlib.sha256(path.read_bytes()).hexdigest() != row['sha256']:
            parser.error('档案自目录发布后已改变')
        dossier = load(path)
        if args.level == 'full':
            result = dossier
        elif args.level == 'overview':
            keys = ['research_id', 'method_id', 'version', 'name', 'summary', 'kind', 'category',
                    'inputs', 'outputs', 'execution_status', 'review_status', 'validation_status']
            result = {k: dossier[k] for k in keys}
        elif args.level == 'sources':
            result = {'research_id': row['research_id'], 'sources': dossier['sources'], 'gaps': dossier['sections']['gaps']}
        else:
            steps = [s for s in dossier['steps'] if not args.step_id or s['step_id'] == args.step_id]
            if not steps:
                parser.error('步骤不存在')
            result = {'research_id': row['research_id'], 'method_id': dossier['method_id'], 'version': dossier['version'],
                      'execution_status': dossier['execution_status'], 'review_status': dossier['review_status'],
                      'validation_status': dossier['validation_status'], 'steps': steps, 'sources': dossier['sources'],
                      'adaptation': dossier['sections']['adaptation']}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
