import argparse
import hashlib
import json
import os
import shutil
import subprocess
import urllib.request
from pathlib import Path

RELEASE = '20261117-164-immersive-exhibition'
BASE = Path('/var/www/gooddesign-site')
FILES = ('hall.html', 'inno/portal/heavy-exhibition.css', 'inno/portal/heavy-exhibition.js')


def switch(link, target):
    temporary = link.with_name(link.name + '.tmp-' + RELEASE)
    if temporary.exists() or temporary.is_symlink():
        temporary.unlink()
    temporary.symlink_to(target, target_is_directory=True)
    os.replace(temporary, link)


def replace_file(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() or target.is_symlink():
        target.unlink()
    shutil.copy2(source, target)
    os.chmod(target, 0o644)


def fetch(path):
    request = urllib.request.Request('http://127.0.0.1' + path, headers={'Host': 'haoshejiguan.com', 'X-Requested-With': 'XMLHttpRequest'})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.status, response.read().decode('utf-8', 'ignore')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage', required=True, type=Path)
    args = parser.parse_args()
    manifest = json.loads((args.stage / 'release-manifest.json').read_text())
    assert manifest['release'] == RELEASE
    for name in FILES:
        source = args.stage / name
        record = manifest['files'][name]
        assert source.stat().st_size == record['bytes']
        assert hashlib.sha256(source.read_bytes()).hexdigest() == record['sha256']

    link = BASE / 'current'
    previous = link.resolve()
    backup = Path('/var/lib/innovation-design/release-backups') / RELEASE
    backup.mkdir(parents=True, exist_ok=False)
    (backup / 'previous-current.json').write_text(json.dumps({'static': str(previous)}, indent=2))
    release = BASE / 'releases' / RELEASE
    try:
        subprocess.run(['cp', '-al', str(previous), str(release)], check=True)
        for name in FILES:
            replace_file(args.stage / name, release / name)
        switch(link, release)
        status, hall = fetch('/museum/hall')
        assert status == 200
        assert hall.count('class="heavy-project"') == 8
        assert hall.count('class="heavy-step"') == 24
        assert hall.count('class="heavy-evidence-link"') == 8
        assert 'id="heavy-browser"' in hall and 'data-heavy-present' in hall
        assert '十年编年' not in hall and '互动乐园' not in hall
        for name in FILES[1:]:
            assert fetch('/' + name + '?v=164')[0] == 200, name
        for route in ('/museum/', '/apps/', '/projects/', '/mcp/', '/dossier/?project=2025-00', '/inno/portal/xiaohao-bot-20261115.png'):
            assert fetch(route)[0] == 200, route
        result = {'release': RELEASE, 'current': str(link.resolve()), 'backup': str(backup), 'files': manifest['files']}
        (backup / 'activation-result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except BaseException:
        switch(link, previous)
        raise


if __name__ == '__main__':
    main()
