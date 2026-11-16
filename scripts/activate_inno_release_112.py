import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tarfile
import urllib.request
from pathlib import Path

RELEASE = '20261106-112'


def run(*args, check=True):
    return subprocess.run(args, check=check)


def switch(link, target):
    temporary = link.with_name(link.name + '.tmp-' + RELEASE)
    if temporary.exists() or temporary.is_symlink():
        temporary.unlink()
    temporary.symlink_to(target, target_is_directory=True)
    os.replace(temporary, link)


def extract(name, target):
    target.mkdir(parents=True, exist_ok=False)
    with tarfile.open(name) as archive:
        archive.extractall(target, filter='data')


def clone(source, target):
    source = source.resolve()
    assert source.is_dir() and not target.exists() and not target.is_symlink()
    run('cp', '-al', str(source), str(target))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage', required=True, type=Path)
    args = parser.parse_args()
    stage = args.stage
    manifest = json.loads((stage / 'release-manifest.json').read_text())
    assert manifest['release'] == RELEASE
    for name, record in manifest['packages'].items():
        path = stage / name
        assert path.stat().st_size == record['bytes'], name
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record['sha256'], name

    bases = {
        'static': Path('/var/www/gooddesign-site'),
        'methods': Path('/var/www/gooddesign-methods'),
        'runtime': Path('/var/www/innovation-design'),
    }
    backup = Path('/var/lib/innovation-design/release-backups') / RELEASE
    backup.mkdir(parents=True, exist_ok=False)
    links = {name: base / 'current' for name, base in bases.items()}
    previous = {name: str(path.resolve()) for name, path in links.items()}
    (backup / 'previous-current.json').write_text(json.dumps(previous, indent=2))

    releases = {name: base / 'releases' / RELEASE for name, base in bases.items()}
    try:
        extract(stage / 'public-site.tar.gz', releases['static'])
        extract(stage / 'methods-site.tar.gz', releases['methods'])
        clone(links['runtime'], releases['runtime'])
        for name in manifest['runtime_files']:
            target = releases['runtime'] / name
            if target.exists() or target.is_symlink():
                target.unlink()
        with tarfile.open(stage / 'runtime-overlay.tar.gz') as archive:
            archive.extractall(releases['runtime'], filter='data')

        for name in ('static', 'methods', 'runtime'):
            switch(links[name], releases[name])
        run('systemctl', 'restart', 'innovation-readonly')
        run('nginx', '-t')
        run('systemctl', 'reload', 'nginx')
        request = urllib.request.Request('http://127.0.0.1:18776/api/health', headers={'Host': '127.0.0.1:18776'})
        with urllib.request.urlopen(request, timeout=30) as response:
            assert response.status == 200
        result = {'release': RELEASE, 'current': {name: str(path.resolve()) for name, path in links.items()}, 'backup': str(backup)}
        (stage / 'activation-result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except BaseException:
        for name, target in previous.items():
            switch(links[name], Path(target))
        run('systemctl', 'restart', 'innovation-readonly', check=False)
        run('nginx', '-t', check=False)
        run('systemctl', 'reload', 'nginx', check=False)
        raise


if __name__ == '__main__':
    main()
