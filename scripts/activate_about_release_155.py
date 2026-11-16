import argparse
import hashlib
import json
import os
import shutil
import subprocess
import urllib.request
from pathlib import Path

RELEASE = '20261116-155-about'
BASE = Path('/var/www/gooddesign-site')


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
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.status, response.read().decode('utf-8', 'ignore')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage', required=True, type=Path)
    args = parser.parse_args()
    manifest = json.loads((args.stage / 'release-manifest.json').read_text())
    assert manifest['release'] == RELEASE
    source = args.stage / 'about/index.html'
    record = manifest['files']['index.html']
    assert source.stat().st_size == record['bytes']
    assert hashlib.sha256(source.read_bytes()).hexdigest() == record['sha256']

    link = BASE / 'current'
    previous = link.resolve()
    backup = Path('/var/lib/innovation-design/release-backups') / RELEASE
    backup.mkdir(parents=True, exist_ok=False)
    (backup / 'previous-current.json').write_text(json.dumps({'static': str(previous)}, indent=2))
    release_dir = BASE / 'releases' / RELEASE
    subprocess.run(['cp', '-al', str(previous), str(release_dir)], check=True)
    try:
        target = release_dir / 'inno/about/index.html'
        if target.exists() or target.is_symlink():
            target.unlink()
        shutil.copy2(source, target)
        switch(link, release_dir)
        status, body = fetch('/about/')
        assert status == 200 and '让真实创新' in body and 'about-case-layout' in body, 'about content'
        assert 'href="/expo/"' in body and '好设计奖官方发布' in body, 'about routes and boundary'
        for route in ('/projects/', '/methods/', '/apps/', '/museum/', '/expo/'):
            status, _ = fetch(route)
            assert status == 200, route
        result = {'release': RELEASE, 'current': str(link.resolve()), 'backup': str(backup),
                  'about_sha256': record['sha256']}
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except BaseException:
        switch(link, previous)
        raise


if __name__ == '__main__':
    main()
