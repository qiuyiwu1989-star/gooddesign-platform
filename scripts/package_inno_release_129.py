import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RELEASE = '20261115-129'
OUT = ROOT / 'output/deploy-129'
APPS = ROOT / 'output/inno-preview/gooddesign-site/inno/apps'
FILES = ['index.html', 'registry.json', 'application.schema.json']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    stage = OUT / 'apps'
    stage.mkdir(parents=True)
    manifest = {'release': RELEASE, 'scope': 'static inno/apps only', 'files': {}}
    for name in FILES:
        source = APPS / name
        target = stage / name
        shutil.copy2(source, target)
        manifest['files'][name] = {'bytes': target.stat().st_size, 'sha256': sha(target)}
    (OUT / 'release-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
