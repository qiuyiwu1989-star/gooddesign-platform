import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import urllib.request
from pathlib import Path

RELEASE = '20261116-156-report'
BASE = Path('/var/www/gooddesign-site')
FILES = ('report/index.html', 'portal/data-report.css', 'portal/data-report.js')


def switch(link, target):
    temporary = link.with_name(link.name + '.tmp-' + RELEASE)
    if temporary.exists() or temporary.is_symlink():
        temporary.unlink()
    temporary.symlink_to(target, target_is_directory=True)
    os.replace(temporary, link)


def fetch(path):
    request = urllib.request.Request('http://127.0.0.1' + path, headers={'Host': 'haoshejiguan.com', 'X-Requested-With': 'XMLHttpRequest'})
    with urllib.request.urlopen(request, timeout=20) as response:
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
    release_dir = BASE / 'releases' / RELEASE
    subprocess.run(['cp', '-al', str(previous), str(release_dir)], check=True)
    try:
        for name in FILES:
            target = release_dir / 'inno' / name
            if target.exists() or target.is_symlink():
                target.unlink()
            shutil.copy2(args.stage / name, target)
        switch(link, release_dir)
        status, body = fetch('/report/')
        assert status == 200 and '看见设计知识' in body and '<strong>103</strong>' in body, 'report value view'
        assert '研究质量与证据工作视图' in body and '<strong>24</strong>' in body, 'report quality view'
        version = re.search(r'data-report\.js\?v=([0-9a-f]{8})', body).group(1)
        status, css = fetch('/inno/portal/data-report.css?v=' + version)
        assert status == 200 and '.dr-core-facts' in css, 'report css'
        status, js = fetch('/inno/portal/data-report.js?v=' + version)
        assert status == 200 and 'function renderAssetFilters' in js, 'report js'
        for route in ('/projects/', '/about/', '/apps/', '/expo/'):
            status, _ = fetch(route)
            assert status == 200, route
        print(json.dumps({'release': RELEASE, 'current': str(link.resolve()), 'backup': str(backup),
                          'asset_version': version, 'files': manifest['files']}, ensure_ascii=False, indent=2))
    except BaseException:
        switch(link, previous)
        raise


if __name__ == '__main__':
    main()
