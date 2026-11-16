import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILT = ROOT / 'output/inno-preview/gooddesign-site'
OUT = ROOT / 'output/release-165'
RELEASE = '20261117-165-interactive-apps'
FILES = (
    'playground.html',
    'inno/lab/index.html', 'inno/quest/index.html', 'inno/studio/index.html', 'inno/transfer/index.html',
    'inno/portal/interactive-apps.css', 'inno/portal/lab.js', 'inno/portal/quest.js',
    'inno/portal/studio.js', 'inno/portal/transfer.js',
    'inno/apps/index.html', 'inno/apps/registry.json', 'inno/about/index.html', 'inno/report/index.html',
    'nginx-inno-root.conf',
)


def main():
    OUT.mkdir(parents=True, exist_ok=False)
    manifest = {'release': RELEASE, 'files': {}}
    for name in FILES:
        source = ROOT / 'deploy/nginx-inno-root.conf' if name == 'nginx-inno-root.conf' else BUILT / name
        assert source.is_file() and source.stat().st_size > 0, name
        target = OUT / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        manifest['files'][name] = {'bytes': target.stat().st_size, 'sha256': hashlib.sha256(target.read_bytes()).hexdigest()}
    (OUT / 'release-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
