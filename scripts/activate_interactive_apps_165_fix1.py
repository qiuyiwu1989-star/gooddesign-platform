import argparse
import hashlib
import json
import os
import shutil
import subprocess
import time
import urllib.request
from pathlib import Path

RELEASE = '20261117-165-interactive-apps-fix1'
BASE = Path('/var/www/gooddesign-site')
FILES = (
    'playground.html',
    'inno/lab/index.html', 'inno/quest/index.html', 'inno/studio/index.html', 'inno/transfer/index.html',
    'inno/portal/interactive-apps.css', 'inno/portal/lab.js', 'inno/portal/quest.js',
    'inno/portal/studio.js', 'inno/portal/transfer.js',
    'inno/apps/index.html', 'inno/apps/registry.json', 'inno/about/index.html', 'inno/report/index.html',
    'nginx-inno-root.conf',
)


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
    result = subprocess.run([
        'curl', '-ksS', '-L', '--resolve', 'haoshejiguan.com:443:127.0.0.1',
        '-H', 'X-Requested-With: XMLHttpRequest', '-o', '-', '-w', '\n%{http_code}',
        'https://haoshejiguan.com' + path,
    ], capture_output=True, text=True, timeout=30, check=False)
    body, status = result.stdout.rsplit('\n', 1)
    return int(status), body


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
    nginx_config = Path('/etc/nginx/snippets/inno-root.conf')
    try:
        subprocess.run(['cp', '-al', str(previous), str(release)], check=True)
        for name in FILES:
            replace_file(args.stage / name, release / name)
        shutil.copy2(nginx_config, backup / 'nginx-inno-root.conf')
        shutil.copy2(args.stage / 'nginx-inno-root.conf', nginx_config)
        subprocess.run(['nginx', '-t'], check=True)
        switch(link, release)
        subprocess.run(['systemctl', 'reload', 'nginx'], check=True)
        time.sleep(3)
        for app in ('lab', 'quest', 'studio', 'transfer'):
            status, page = fetch(f'/{app}/')
            assert status == 200 and 'data-gd-chrome="navigation"' in page, app
            assert fetch(f'/inno/portal/{app}.js?v=165')[0] == 200, app + ' js'
        status, playground = fetch('/museum/playground')
        assert status == 200 and playground.count('class="ia-app-choices"') == 1
        for app in ('lab', 'quest', 'studio', 'transfer'):
            assert f'href="/{app}/"' in playground
        status, apps = fetch('/apps/')
        assert status == 200 and apps.count('class="app-card"') == 12
        status, registry = fetch('/apps/registry.json')
        assert status == 200 and registry.count('"id":') >= 12
        for route in ('/about/', '/report/'):
            status, page = fetch(route)
            assert status == 200 and '<strong>12</strong>' in page, route
        for route in ('/museum/', '/projects/', '/mcp/', '/dossier/?project=2025-00', '/inno/portal/interactive-apps.css?v=165', '/inno/legacy/js/play-data.js'):
            assert fetch(route)[0] == 200, route
        result = {'release': RELEASE, 'current': str(link.resolve()), 'backup': str(backup), 'files': manifest['files']}
        (backup / 'activation-result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except BaseException:
        switch(link, previous)
        if (backup / 'nginx-inno-root.conf').exists():
            shutil.copy2(backup / 'nginx-inno-root.conf', nginx_config)
            subprocess.run(['nginx', '-t'], check=False)
            subprocess.run(['systemctl', 'reload', 'nginx'], check=False)
        raise


if __name__ == '__main__':
    main()
