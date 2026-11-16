import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tarfile
import urllib.request
from pathlib import Path

RELEASE = '20261104-093e'


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
    run('cp', '-a', str(source), str(target))


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

    static_base = Path('/var/www/gooddesign-site')
    methods_base = Path('/var/www/gooddesign-methods')
    runtime_base = Path('/var/www/innovation-design')
    mcp_base = Path('/var/www/innovation-mcp')
    snapshot = Path('/var/lib/innovation-design/snapshots') / RELEASE / 'library'
    backup = Path('/var/lib/innovation-design/release-backups') / RELEASE
    backup.mkdir(parents=True, exist_ok=False)
    links = {
        'static': static_base / 'current',
        'methods': methods_base / 'current',
        'runtime': runtime_base / 'current',
        'mcp': mcp_base / 'current',
    }
    previous = {name: str(path.resolve()) for name, path in links.items()}
    (backup / 'previous-current.json').write_text(json.dumps(previous, indent=2))
    nginx = Path('/etc/nginx/snippets/inno-readonly.conf')
    needs_nginx = Path('/etc/nginx/snippets/needs-research.conf')
    shutil.copy2(nginx, backup / 'inno-readonly.conf')
    shutil.copy2(needs_nginx, backup / 'needs-research.conf')
    had_loop = subprocess.run(['systemctl', 'is-active', '--quiet', 'innovation-loop']).returncode == 0
    (backup / 'loop-was-active').write_text(str(had_loop))

    public_release = static_base / 'releases' / RELEASE
    methods_release = methods_base / 'releases' / RELEASE
    runtime_release = runtime_base / 'releases' / RELEASE
    mcp_release = mcp_base / 'releases' / RELEASE
    old_library = (runtime_base / 'current/04-知识库/项目库').resolve()

    try:
        extract(stage / 'public-site.tar.gz', public_release)
        extract(stage / 'methods-site.tar.gz', methods_release)
        clone(runtime_base / 'current', runtime_release)
        clone(mcp_base / 'current', mcp_release)
        with tarfile.open(stage / 'runtime-overlay.tar.gz') as archive:
            archive.extractall(runtime_release, filter='data')
        with tarfile.open(stage / 'runtime-overlay.tar.gz') as archive:
            archive.extractall(mcp_release, filter='data')

        snapshot.parent.mkdir(parents=True, exist_ok=False)
        run('cp', '-al', str(old_library), str(snapshot))
        unpacked = stage / 'research-unpacked'
        unpacked.mkdir(exist_ok=False)
        with tarfile.open(stage / 'research-snapshot.tar.gz') as archive:
            archive.extractall(unpacked, filter='data')
        for source in unpacked.rglob('*'):
            if not source.is_file():
                continue
            target = snapshot / source.relative_to(unpacked)
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists() or target.is_symlink():
                target.unlink()
            shutil.copy2(source, target)

        for release in (runtime_release, mcp_release):
            library_link = release / '04-知识库/项目库'
            if library_link.exists() or library_link.is_symlink():
                library_link.unlink()
            library_link.symlink_to(snapshot, target_is_directory=True)
        inbox = Path('/var/lib/innovation-design/inbox')
        for release in (runtime_release, mcp_release):
            link = release / '01-原始资料/项目投递箱'
            link.parent.mkdir(parents=True, exist_ok=True)
            if link.exists() or link.is_symlink():
                link.unlink()
            link.symlink_to(inbox, target_is_directory=True)

        loop_data = Path('/var/lib/innovation-loop')
        loop_data.mkdir(parents=True, exist_ok=True)
        loop_db = loop_data / 'loop.sqlite3'
        if not loop_db.exists():
            shutil.copy2(runtime_release / 'output/innovation-loop-024/integration/loop.sqlite3', loop_db)
        shutil.chown(loop_db, 'ubuntu', 'ubuntu')

        switch(links['static'], public_release)
        switch(links['methods'], methods_release)
        switch(links['runtime'], runtime_release)
        switch(links['mcp'], mcp_release)
        shutil.copy2(runtime_release / 'deploy/innovation-loop.service', '/etc/systemd/system/innovation-loop.service')
        run('systemctl', 'daemon-reload')
        run('systemctl', 'enable', '--now', 'innovation-loop')
        run('systemctl', 'restart', 'innovation-readonly', 'innovation-mcp', 'innovation-loop')
        shutil.copy2(runtime_release / 'deploy/nginx-inno-readonly.conf', nginx)
        shutil.copy2(runtime_release / 'deploy/nginx-needs-research.conf', needs_nginx)
        run('nginx', '-t')
        run('systemctl', 'reload', 'nginx')

        for url in ('http://127.0.0.1:18776/api/health', 'http://127.0.0.1:18784/api/bundle'):
            request = urllib.request.Request(url, headers={'Host': url.split('/')[2]})
            with urllib.request.urlopen(request, timeout=30) as response:
                assert response.status == 200, url
        result = {'release': RELEASE, 'current': {name: str(path.resolve()) for name, path in links.items()}, 'library': str(snapshot), 'research_projects': manifest['research_project_count'], 'backup': str(backup)}
        (stage / 'activation-result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except BaseException:
        for name, target in previous.items():
            switch(links[name], Path(target))
        shutil.copy2(backup / 'inno-readonly.conf', nginx)
        shutil.copy2(backup / 'needs-research.conf', needs_nginx)
        run('systemctl', 'daemon-reload')
        if had_loop:
            run('systemctl', 'restart', 'innovation-loop', check=False)
        else:
            run('systemctl', 'disable', '--now', 'innovation-loop', check=False)
        run('systemctl', 'restart', 'innovation-readonly', 'innovation-mcp', check=False)
        run('nginx', '-t', check=False)
        run('systemctl', 'reload', 'nginx', check=False)
        raise


if __name__ == '__main__':
    main()
