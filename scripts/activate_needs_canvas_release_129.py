import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tarfile
import urllib.request
from pathlib import Path

RELEASE = '20261115-129'
STATIC_BASE = Path('/var/www/gooddesign-site')
CANVAS_BASE = Path('/var/www/innovation-design')
STATIC_TARGET = STATIC_BASE / 'releases' / '20261115-129-needs'
CANVAS_TARGET = CANVAS_BASE / 'releases' / '20261115-129-canvas'
BACKUP = CANVAS_BASE / 'release-backups' / RELEASE
SERVICE = Path('/etc/systemd/system/innovation-canvas.service')
STATIC_FILES = [
    'inno/needs-v2/index.html',
    'inno/portal/needs-workspace.css',
    'inno/portal/needs-workspace.js',
    'inno/portal/needs-live-demo.css',
    'inno/portal/needs-live-demo.js',
]
CANVAS_FILES = [
    'extensions/reasoning-canvas/index.html',
    'extensions/reasoning-canvas/reasoning-canvas.css',
    'extensions/reasoning-canvas/reasoning-canvas.js',
    'extensions/reasoning-canvas/state.js',
    'extensions/reasoning-canvas/data.js',
    'scripts/canvas_gdrp_mapper.py',
]


def run(*args, check=True, **kwargs):
    return subprocess.run(args, check=check, **kwargs)


def switch(link, target):
    temporary = link.with_name(link.name + '.tmp-' + RELEASE)
    if temporary.exists() or temporary.is_symlink():
        temporary.unlink()
    temporary.symlink_to(target, target_is_directory=True)
    os.replace(temporary, link)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, new_url):
        return None


def fetch(path, https=False):
    url = ('https://' if https else 'http://') + '127.0.0.1' + path
    request = urllib.request.Request(url, headers={'Host': 'haoshejiguan.com', 'X-Requested-With': 'XMLHttpRequest'})
    handlers = [NoRedirect()]
    if https:
        import ssl
        handlers.append(urllib.request.HTTPSHandler(context=ssl._create_unverified_context()))
    opener = urllib.request.build_opener(*handlers)
    try:
        with opener.open(request, timeout=20) as response:
            return response.status, response.read().decode('utf-8', 'ignore')
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode('utf-8', 'ignore')


def replace_files(target, payload, names):
    for name in names:
        destination = target / name
        if destination.exists() or destination.is_symlink():
            destination.unlink()
        shutil.copy2(payload / name, destination)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage', required=True, type=Path)
    args = parser.parse_args()
    manifest = json.loads((args.stage / 'release-manifest.json').read_text())
    assert manifest['release'] == RELEASE
    package = args.stage / manifest['package']['name']
    assert package.stat().st_size == manifest['package']['bytes']
    assert hashlib.sha256(package.read_bytes()).hexdigest() == manifest['package']['sha256']
    payload = args.stage / 'payload'
    payload.mkdir(exist_ok=True)
    with tarfile.open(package) as archive:
        archive.extractall(payload, filter='data')
    for name, record in manifest['files'].items():
        path = payload / name
        assert path.stat().st_size == record['bytes'], name
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record['sha256'], name

    static_link = STATIC_BASE / 'current'
    previous_static = static_link.resolve()
    assert previous_static.is_dir()
    unit_before = SERVICE.read_text(encoding='utf-8')
    marker = 'WorkingDirectory='
    previous_canvas = Path(next(line[len(marker):] for line in unit_before.splitlines() if line.startswith(marker)))
    assert previous_canvas.is_dir()
    for target in (STATIC_TARGET, CANVAS_TARGET):
        if target.exists() or target.is_symlink():
            raise RuntimeError(f'release already exists: {target}')
    BACKUP.mkdir(parents=True, exist_ok=False)
    (BACKUP / 'previous-targets.json').write_text(json.dumps({'static': str(previous_static), 'canvas': str(previous_canvas)}, indent=2))
    (BACKUP / 'innovation-canvas.service.before').write_text(unit_before, encoding='utf-8')

    static_switched = False
    try:
        run('cp', '-al', str(previous_static), str(STATIC_TARGET))
        replace_files(STATIC_TARGET, payload, STATIC_FILES)
        run('cp', '-al', str(previous_canvas), str(CANVAS_TARGET))
        replace_files(CANVAS_TARGET, payload, CANVAS_FILES)
        updated_unit = unit_before.replace(f'WorkingDirectory={previous_canvas}', f'WorkingDirectory={CANVAS_TARGET}', 1)
        assert updated_unit != unit_before
        SERVICE.write_text(updated_unit, encoding='utf-8')
        run('systemctl', 'daemon-reload')
        run('systemctl', 'restart', 'innovation-canvas.service')
        switch(static_link, STATIC_TARGET)
        static_switched = True

        status, body = fetch('/needs/', https=True)
        assert status == 200 and '全程 0 次模型调用' in body, 'needs page check'
        status, body = fetch('/inno/portal/needs-workspace.js', https=True)
        assert status == 200 and 'gooddesign-canvas-handoff-1.0' in body, 'needs script check'
        status, body = fetch('/apps/', https=True)
        assert status == 200 and '推理画布' in body, 'apps preserved check'
        status, _ = fetch('/projects/', https=True)
        assert status == 200, 'projects spot check'
        status, _ = fetch('/', https=True)
        assert status == 200, 'home spot check'
        status, body = fetch('/api/rc/engine_candidates', https=True)
        assert status == 302, 'canvas API remains protected'
        status, body = fetch('/canvas/', https=True)
        assert status == 302, 'canvas page remains protected'
        result = {
            'release': RELEASE,
            'static': str(static_link.resolve()),
            'canvas': str(CANVAS_TARGET),
            'backup': str(BACKUP),
            'needs': 200,
            'canvas_anonymous': 302,
        }
        (args.stage / 'activation-result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except BaseException:
        if static_switched:
            switch(static_link, previous_static)
        SERVICE.write_text(unit_before, encoding='utf-8')
        run('systemctl', 'daemon-reload', check=False)
        run('systemctl', 'restart', 'innovation-canvas.service', check=False)
        raise


if __name__ == '__main__':
    main()
