import argparse
import hashlib
import json
import os
import shutil
import subprocess
import urllib.request
from pathlib import Path

RELEASE = '20261115-128'
BASE = Path('/var/www/gooddesign-site')
FILES = ['index.html', 'registry.json', 'application.schema.json']


def run(*args, check=True):
    return subprocess.run(args, check=check)


def switch(link, target):
    temporary = link.with_name(link.name + '.tmp-' + RELEASE)
    if temporary.exists() or temporary.is_symlink():
        temporary.unlink()
    temporary.symlink_to(target, target_is_directory=True)
    os.replace(temporary, link)


def fetch(path):
    request = urllib.request.Request(
        'http://127.0.0.1' + path,
        headers={'Host': 'haoshejiguan.com', 'X-Requested-With': 'XMLHttpRequest'})
    with urllib.request.urlopen(request, timeout=15) as response:
        return response.status, response.read().decode('utf-8', 'ignore')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage', required=True, type=Path)
    args = parser.parse_args()
    stage = args.stage
    manifest = json.loads((stage / 'release-manifest.json').read_text())
    assert manifest['release'] == RELEASE
    for name, record in manifest['files'].items():
        path = stage / 'apps' / name
        assert path.stat().st_size == record['bytes'], name
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record['sha256'], name

    link = BASE / 'current'
    previous = link.resolve()
    backup = Path('/var/lib/innovation-design/release-backups') / RELEASE
    backup.mkdir(parents=True, exist_ok=False)
    (backup / 'previous-current.json').write_text(json.dumps({'static': str(previous)}, indent=2))

    release_dir = BASE / 'releases' / RELEASE
    run('cp', '-al', str(previous), str(release_dir))
    try:
        for name in FILES:
            target = release_dir / 'inno/apps' / name
            if target.exists() or target.is_symlink():
                target.unlink()
            shutil.copy2(stage / 'apps' / name, target)
        switch(link, release_dir)

        status, body = fetch('/apps/')
        assert status == 200 and '产业创新 Agent' in body and '推理画布' in body, 'apps page check'
        status, body = fetch('/apps/registry.json')
        assert status == 200 and 'server_workspace_pilot' in body, 'registry check'
        status, body = fetch('/apps/application.schema.json')
        assert status == 200 and 'gd-app-0.1' in body, 'schema check'
        status, _ = fetch('/projects/')
        assert status == 200, 'projects spot check'
        status, _ = fetch('/')
        assert status == 200, 'home spot check'
        result = {'release': RELEASE, 'current': str(link.resolve()), 'backup': str(backup)}
        (stage / 'activation-result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except BaseException:
        switch(link, previous)
        raise


if __name__ == '__main__':
    main()
