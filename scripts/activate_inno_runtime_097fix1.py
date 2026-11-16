import hashlib
import json
import os
import subprocess
import tarfile
import time
import urllib.request
from pathlib import Path

RELEASE = '20261105-097-fix1'
STAGE = Path('/var/lib/innovation-design/staging-20261105-097')


def run(*args, check=True):
    return subprocess.run(args, check=check)


def switch(link, target):
    temporary = link.with_name(link.name + '.tmp-' + RELEASE)
    if temporary.exists() or temporary.is_symlink():
        temporary.unlink()
    temporary.symlink_to(target, target_is_directory=True)
    os.replace(temporary, link)


def main():
    manifest = json.loads((STAGE / 'release-manifest.json').read_text())
    record = manifest['packages']['runtime-overlay.tar.gz']
    package = STAGE / 'runtime-overlay.tar.gz'
    assert package.stat().st_size == record['bytes']
    assert hashlib.sha256(package.read_bytes()).hexdigest() == record['sha256']
    current = Path('/var/www/innovation-design/current')
    previous = current.resolve()
    release = Path('/var/www/innovation-design/releases') / RELEASE
    backup = Path('/var/lib/innovation-design/release-backups') / RELEASE
    backup.mkdir(parents=True, exist_ok=False)
    (backup / 'previous-current.json').write_text(json.dumps({'runtime': str(previous)}, indent=2))
    try:
        run('cp', '-al', str(previous), str(release))
        for name in manifest['runtime_files']:
            target = release / name
            if target.exists() or target.is_symlink():
                target.unlink()
        with tarfile.open(package) as archive:
            archive.extractall(release, filter='data')
        switch(current, release)
        run('systemctl', 'restart', 'innovation-readonly')
        request = urllib.request.Request('http://127.0.0.1:18776/api/health', headers={'Host': '127.0.0.1:18776'})
        for attempt in range(30):
            try:
                with urllib.request.urlopen(request, timeout=2) as response:
                    assert response.status == 200
                break
            except Exception:
                if attempt == 29:
                    raise
                time.sleep(1)
        result = {'release': RELEASE, 'runtime': str(current.resolve()), 'backup': str(backup)}
        (STAGE / 'activation-result-097-fix1.json').write_text(json.dumps(result, indent=2))
        print(json.dumps(result, indent=2))
    except BaseException:
        switch(current, previous)
        run('systemctl', 'restart', 'innovation-readonly', check=False)
        raise


if __name__ == '__main__':
    main()
