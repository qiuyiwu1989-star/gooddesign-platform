import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tarfile
import tempfile
import urllib.request
from pathlib import Path

RELEASE = '20261116-162-research-sync'
RUNTIME_BASE = Path('/var/www/innovation-design')
MCP_BASE = Path('/var/www/innovation-mcp')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def fetch(url):
    with urllib.request.urlopen(url, timeout=30) as response:
        return response.status, response.read().decode('utf-8', 'ignore')


def public_fetch(path):
    request = urllib.request.Request('http://127.0.0.1' + path, headers={'Host': 'haoshejiguan.com', 'X-Requested-With': 'XMLHttpRequest'})
    return fetch(request)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage', required=True, type=Path)
    args = parser.parse_args()
    manifest = json.loads((args.stage / 'release-manifest.json').read_text())
    assert manifest['release'] == RELEASE
    package = args.stage / 'research-snapshot.tar.gz'
    assert package.stat().st_size == manifest['package']['bytes']
    assert sha(package) == manifest['package']['sha256']

    links = {'runtime': RUNTIME_BASE / 'current', 'mcp': MCP_BASE / 'current'}
    previous = {name: path.resolve() for name, path in links.items()}
    old_library = (previous['runtime'] / '04-知识库/项目库').resolve()
    assert (previous['mcp'] / '04-知识库/项目库').resolve() == old_library
    backup = Path('/var/lib/innovation-design/release-backups') / RELEASE
    backup.mkdir(parents=True, exist_ok=False)
    (backup / 'previous-current.json').write_text(json.dumps({name: str(path) for name, path in previous.items()}, indent=2))
    (backup / 'previous-library.json').write_text(json.dumps({'library': str(old_library)}, indent=2))

    snapshot = Path('/var/lib/innovation-design/snapshots') / RELEASE / 'library'
    releases = {'runtime': RUNTIME_BASE / 'releases' / RELEASE, 'mcp': MCP_BASE / 'releases' / RELEASE}
    try:
        snapshot.parent.mkdir(parents=True, exist_ok=False)
        subprocess.run(['cp', '-al', str(old_library), str(snapshot)], check=True)
        for name, target in releases.items():
            subprocess.run(['cp', '-al', str(previous[name]), str(target)], check=True)
        changed_files = 0
        with tempfile.TemporaryDirectory(prefix='research-sync-162-') as temporary:
            unpacked = Path(temporary)
            with tarfile.open(package) as archive:
                archive.extractall(unpacked, filter='data')
            for relative, record in manifest['files'].items():
                source = unpacked / relative
                assert source.is_file() and not source.is_symlink(), relative
                assert source.stat().st_size == record['bytes'] and sha(source) == record['sha256'], relative
                target = snapshot / relative
                if target.is_file() and target.stat().st_size == record['bytes'] and sha(target) == record['sha256']:
                    continue
                replace_file(source, target)
                changed_files += 1
        for target in releases.values():
            library_link = target / '04-知识库/项目库'
            if library_link.exists() or library_link.is_symlink():
                library_link.unlink()
            library_link.symlink_to(snapshot, target_is_directory=True)

        index = json.loads((snapshot / '项目索引.json').read_text())
        projects = [project for project in index['projects'] if (snapshot / project['id'] / '研究工作区').is_dir()]
        versions = [path for project in projects for path in (snapshot / project['id'] / '研究工作区/版本').glob('research-*') if path.is_dir()]
        assert len(index['projects']) == manifest['catalog_count'] == 560
        assert len(projects) == manifest['research_project_count'] == 103
        assert len(versions) == manifest['research_version_count'] == 221

        for name, target in releases.items():
            switch(links[name], target)
        subprocess.run(['systemctl', 'restart', 'innovation-readonly', 'innovation-mcp'], check=True)
        assert fetch('http://127.0.0.1:18776/api/health')[0] == 200
        assert fetch('http://127.0.0.1:18784/api/bundle')[0] == 200
        status, dossier = public_fetch('/dossier/?project=2025-00')
        assert status == 200 and 'research-000008' in dossier, '2025-00 research-000008'
        for project in ('2019-s19', '2015-02', '2021-00'):
            assert public_fetch('/dossier/?project=' + project)[0] == 200, project
        result = {
            'release': RELEASE,
            'current': {name: str(path.resolve()) for name, path in links.items()},
            'library': str(snapshot),
            'catalog_count': 560,
            'research_projects': 103,
            'research_versions': 221,
            'files': len(manifest['files']),
            'changed_files': changed_files,
            'backup': str(backup),
        }
        (backup / 'activation-result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except BaseException:
        for name, target in previous.items():
            switch(links[name], target)
        subprocess.run(['systemctl', 'restart', 'innovation-readonly', 'innovation-mcp'], check=False)
        raise


if __name__ == '__main__':
    main()
