"""Freeze original candidates byte-for-byte and assign anonymous review labels."""
import hashlib
import json
import secrets
from pathlib import Path
from method_engine import ROOT


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    base = ROOT / '02-研究/ML-023-割胶机器人对照评审'
    private = base / 'private'
    if (private / 'label-map.json').exists():
        raise ValueError('already_frozen_do_not_replace_candidates')
    pre = json.loads((base / '00-预注册方案.json').read_text())
    assert sha(private / '共同资料.json') == pre['common_bundle_sha256']
    for arm, expected in pre['protocol_sha256'].items():
        assert sha(private / f'protocol-{arm}.txt') == expected
    order = ['u', 'v']
    secrets.SystemRandom().shuffle(order)
    manifest, mapping = [], {}
    for label, arm in zip(['甲', '乙'], order):
        source = private / f'arm-{arm}/output.md'
        report = private / f'arm-{arm}/run.json'
        body = source.read_text()
        assert 0 < len(body) <= 5000, (arm, len(body))
        assert report.exists(), arm
        json.loads(report.read_text())
        dest = base / f'结果/方案{label}.md'
        dest.write_bytes(source.read_bytes())
        mapping[label] = {'arm': arm, 'original_sha256': sha(source), 'run_log_sha256': sha(report)}
        manifest.append({'label': label, 'file': str(dest.relative_to(base)),
                         'sha256': sha(dest), 'characters': len(body)})
    (private / 'label-map.json').write_text(json.dumps(mapping, ensure_ascii=False, indent=2) + '\n')
    (base / '02-匿名稿冻结.json').write_text(json.dumps({
        'common_bundle_sha256': pre['common_bundle_sha256'], 'candidates': manifest,
        'source_bytes_preserved': True, 'labels_randomly_assigned_after_generation': True,
        'not_strict_double_blind': True}, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'candidates_frozen': len(manifest), 'characters': [m['characters'] for m in manifest]}, ensure_ascii=False))


if __name__ == '__main__':
    main()
