import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILT = ROOT / 'output/inno-preview/gooddesign-site'
OUT = ROOT / 'output/release-164'
FILES = ('hall.html', 'inno/portal/heavy-exhibition.css', 'inno/portal/heavy-exhibition.js')
RELEASE = '20261117-164-immersive-exhibition'


def main():
    OUT.mkdir(parents=True, exist_ok=False)
    manifest = {'release': RELEASE, 'files': {}}
    for name in FILES:
        source = BUILT / name
        assert source.is_file() and source.stat().st_size > 0, name
        target = OUT / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        manifest['files'][name] = {'bytes': target.stat().st_size, 'sha256': hashlib.sha256(target.read_bytes()).hexdigest()}
    (OUT / 'release-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
