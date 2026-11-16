import json
import os
import shutil
import subprocess
import tarfile
import urllib.request
from pathlib import Path

RELEASE = '20261104-095'
STAGE = Path('/var/lib/innovation-design/staging-20261104-095')
BACKUP = Path('/var/lib/innovation-design/release-backups/20261104-095')
STATIC_CURRENT = Path('/var/www/gooddesign-site/current')
RUNTIME_CURRENT = Path('/var/www/innovation-design/current')
STATIC_RELEASE = Path('/var/www/gooddesign-site/releases') / RELEASE
RUNTIME_RELEASE = Path('/var/www/innovation-design/releases') / RELEASE


def run(*args):
    subprocess.run(args, check=True)


def switch(link, target):
    temporary = link.with_name(link.name + '.tmp-' + RELEASE)
    if temporary.exists() or temporary.is_symlink():
        temporary.unlink()
    temporary.symlink_to(target, target_is_directory=True)
    os.replace(temporary, link)


def main():
    previous_static = STATIC_CURRENT.resolve()
    previous_runtime = RUNTIME_CURRENT.resolve()
    BACKUP.mkdir(parents=True, exist_ok=False)
    (BACKUP / 'previous.json').write_text(json.dumps({'static': str(previous_static), 'runtime': str(previous_runtime)}, indent=2))
    nginx = Path('/etc/nginx/snippets/inno-readonly.conf')
    shutil.copy2(nginx, BACKUP / 'inno-readonly.conf')
    shutil.copy2('/etc/nginx/snippets/needs-research.conf', BACKUP / 'needs-research.conf')
    try:
        STATIC_RELEASE.mkdir(parents=True, exist_ok=False)
        with tarfile.open(STAGE / 'public-site.tar.gz') as archive:
            archive.extractall(STATIC_RELEASE, filter='data')
        run('cp', '-a', str(previous_runtime), str(RUNTIME_RELEASE))
        for name in ('gooddesign_chrome.py', 'steward_dossier_ui.py', 'opendesign_readonly.py', 'info_pages_095.py', 'innovation_auth.py'):
            shutil.copy2(STAGE / name, RUNTIME_RELEASE / 'scripts' / name)
        shutil.copytree(STAGE / 'application-center', RUNTIME_RELEASE / 'extensions/application-center', dirs_exist_ok=True)
        shutil.copy2(STAGE / 'nginx-inno-readonly.conf', RUNTIME_RELEASE / 'deploy/nginx-inno-readonly.conf')
        shutil.copy2(STAGE / 'innovation-auth.service', '/etc/systemd/system/innovation-auth.service')
        auth_dir = Path('/etc/innovation-auth')
        auth_dir.mkdir(parents=True, exist_ok=True)
        auth_dir.chmod(0o700)
        shutil.chown(auth_dir, 'ubuntu', 'ubuntu')
        key = auth_dir / 'session.key'
        if not key.exists():
            run('sh', '-c', 'openssl rand -hex 32 > /etc/innovation-auth/session.key')
        key.chmod(0o600)
        shutil.chown(key, 'ubuntu', 'ubuntu')
        switch(STATIC_CURRENT, STATIC_RELEASE)
        switch(RUNTIME_CURRENT, RUNTIME_RELEASE)
        shutil.copy2(RUNTIME_RELEASE / 'deploy/nginx-inno-readonly.conf', nginx)
        run('systemctl', 'daemon-reload')
        run('systemctl', 'enable', '--now', 'innovation-auth')
        run('systemctl', 'restart', 'innovation-readonly', 'innovation-auth')
        run('nginx', '-t')
        run('systemctl', 'reload', 'nginx')
        for url in ('http://127.0.0.1:18776/api/health', 'http://127.0.0.1:18785/health', 'http://127.0.0.1:18784/api/bundle'):
            request = urllib.request.Request(url, headers={'Host': url.split('/')[2]})
            with urllib.request.urlopen(request, timeout=30) as response:
                assert response.status == 200, url
        result = {'release': RELEASE, 'static': str(STATIC_CURRENT.resolve()), 'runtime': str(RUNTIME_CURRENT.resolve()), 'backup': str(BACKUP)}
        (STAGE / 'activation-result.json').write_text(json.dumps(result, indent=2))
        print(json.dumps(result, indent=2))
    except BaseException:
        switch(STATIC_CURRENT, previous_static)
        switch(RUNTIME_CURRENT, previous_runtime)
        shutil.copy2(BACKUP / 'inno-readonly.conf', nginx)
        shutil.copy2(BACKUP / 'needs-research.conf', '/etc/nginx/snippets/needs-research.conf')
        run('systemctl', 'restart', 'innovation-readonly')
        run('systemctl', 'disable', '--now', 'innovation-auth')
        run('nginx', '-t')
        run('systemctl', 'reload', 'nginx')
        raise


if __name__ == '__main__':
    main()
