import hashlib
import json
import shutil
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RELEASE = '20261115-129'
OUT = ROOT / 'output/deploy-129'
PACKAGE = OUT / 'needs-canvas-129.tar.gz'
FILES = [
    'inno/needs-v2/index.html',
    'inno/portal/needs-workspace.css',
    'inno/portal/needs-workspace.js',
    'inno/portal/needs-live-demo.css',
    'inno/portal/needs-live-demo.js',
    'extensions/reasoning-canvas/index.html',
    'extensions/reasoning-canvas/reasoning-canvas.css',
    'extensions/reasoning-canvas/reasoning-canvas.js',
    'extensions/reasoning-canvas/state.js',
    'extensions/reasoning-canvas/data.js',
    'scripts/canvas_gdrp_mapper.py',
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source(name):
    built = ROOT / 'output/inno-preview/gooddesign-site' / name
    return built if name.startswith('inno/') else ROOT / name


def safe_member(item):
    if item.issym() or item.islnk() or '__pycache__' in item.name or item.name.endswith('.pyc'):
        return None
    return item


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    records = {}
    for name in FILES:
        path = source(name)
        if not path.is_file() or not path.stat().st_size:
            raise SystemExit(f'missing or empty: {name}')
        records[name] = {'bytes': path.stat().st_size, 'sha256': sha(path)}
    with tarfile.open(PACKAGE, 'w:gz') as archive:
        for name in FILES:
            archive.add(source(name), arcname=name, filter=safe_member)
    manifest = {
        'release': RELEASE,
        'scope': 'needs-v2 and reasoning-canvas handoff only',
        'package': {'name': PACKAGE.name, 'bytes': PACKAGE.stat().st_size, 'sha256': sha(PACKAGE)},
        'files': records,
    }
    (OUT / 'release-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
