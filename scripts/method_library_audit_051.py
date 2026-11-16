"""Read-only full release audit for ML-001; does not certify engineering outcomes."""
import argparse
import hashlib
import json
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import method_library_051 as lib


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.ids = [], set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'):
            self.ids.add(attrs['id'])
        for key in ('href', 'src'):
            if attrs.get(key):
                self.links.append(attrs[key])


def audit(output=lib.DEFAULT_OUTPUT, work=lib.WORK):
    output, work = Path(output), Path(work)
    checks, errors = [], []

    def check(name, ok, detail):
        checks.append({'name': name, 'passed': bool(ok), 'detail': detail})
        if not ok:
            errors.append(name)

    records, structure = lib.inspect(work)
    check('exact_scope_and_structure', structure['methods'] == 48 and structure['topics'] == 12
          and not structure['read_errors'] and not structure['duplicate_ids']
          and not structure['duplicate_method_ids'] and not structure['unexpected_ids']
          and not any(r['errors'] for r in structure['results']),
          {'methods': structure['methods'], 'topics': structure['topics']})
    catalog = lib.load(output/'目录.json')['methods']
    check('catalog_identity_uniqueness', len(catalog) == len({r['research_id'] for r in catalog}) == 60
          and len({r['method_id'] for r in catalog}) == 60, len(catalog))
    mismatches, templates, read_failures = [], [], []
    for _, d in records:
        rid = d['research_id']
        folder = output/'档案'/rid
        if lib.load(folder/'档案.json') != d:
            mismatches.append(rid)
        for name in ['深度说明.md', '操作指南.md', '方法结构.md', '来源核读.md']:
            if not (folder/name).is_file() or not (folder/name).stat().st_size:
                mismatches.append(rid+'/'+name)
        inp, out = lib.load(folder/'输入模板.json'), lib.load(folder/'产物字段模板.json')
        if set(inp['inputs']) != {i['key'] for i in d['inputs']} or any(i['value'] is not None for i in inp['inputs'].values()):
            templates.append(rid)
        for o in d['outputs']:
            if set(out['outputs'][o['key']]['fields']) != set(o['required_fields']) or any(v is not None for v in out['outputs'][o['key']]['fields'].values()):
                templates.append(rid)
        proc = subprocess.run([sys.executable, str(output/'library_cli.py'), 'read', '--id', d['method_id'], '--level', 'steps',
                               '--step-id', d['steps'][0]['step_id']], capture_output=True, text=True)
        if proc.returncode or json.loads(proc.stdout)['steps'][0]['step_id'] != d['steps'][0]['step_id']:
            read_failures.append(rid)
    check('source_to_release_identical', not mismatches, mismatches)
    check('all_templates_unfilled_and_correct', not templates, templates)
    check('portable_cli_all_60_ids_and_steps', not read_failures, read_failures)
    parsed = {}
    for path in output.rglob('*.html'):
        parsed[path.resolve()] = parser = Links()
        parser.feed(path.read_text())
    broken = []
    for path, parser in parsed.items():
        for href in parser.links:
            ref = urlsplit(href)
            if ref.scheme or ref.netloc:
                continue
            target = (path.parent/unquote(ref.path)).resolve() if ref.path else path
            if not target.is_relative_to(output.resolve()) or not target.is_file():
                broken.append({'page': str(path.relative_to(output)), 'href': href})
            elif ref.fragment and target in parsed and unquote(ref.fragment) not in parsed[target].ids:
                broken.append({'page': str(path.relative_to(output)), 'href': href})
    check('all_local_html_links_and_anchors', not broken, {'html_pages': len(parsed), 'broken': broken})
    manifest = lib.load(output/'manifest.json')['files']
    actual_files = {str(p.relative_to(output)) for p in output.rglob('*') if p.is_file() and p.name != 'manifest.json'}
    bad_hashes = [p for p, h in manifest.items() if not (output/p).is_file() or lib.sha(output/p) != h]
    check('manifest_covers_all_files_and_hashes', not bad_hashes and actual_files == set(manifest),
          {'files': len(manifest), 'bad_hashes': bad_hashes, 'missing_from_manifest': sorted(actual_files-set(manifest))})
    frozen = lib.load(work/'既有方法冻结指纹.json')
    runtime = work.parent
    changed = [name for name, expected in frozen.items() if lib.sha(runtime/name) != expected]
    check('existing_runtime_cards_unchanged', not changed, {'files': len(frozen), 'changed': changed})
    return {'task': 'ML-001', 'status': 'passed' if not errors else 'failed', 'checks': checks,
            'nonblocking_length_warnings': [r['research_id'] for r in structure['results'] if r['warnings']],
            'scope': 'content_structure_integrity_reader_not_expert_or_engineering_certification'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=lib.DEFAULT_OUTPUT)
    args = parser.parse_args()
    report = audit(args.output)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    sys.exit(0 if report['status'] == 'passed' else 1)
