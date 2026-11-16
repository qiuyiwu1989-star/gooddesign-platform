import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import urllib.parse
import urllib.request
from pathlib import Path

RELEASE = '20261116-157-museum-apps'
BASE = Path('/var/www/gooddesign-site')
FILES = ('inno/museum/index.html', 'categories.html', 'inno/apps/index.html',
         'inno/portal/museum-polish.css', 'inno/portal/museum-polish.js',
         'inno/needs-v2/index.html', 'inno/portal/needs-workspace.css',
         'inno/portal/needs-workspace.js', 'inno/portal/needs-live-demo.css',
         'inno/model/index.html', 'inno/about/index.html', 'inno/portal/model-official.css',
         'inno/apps/registry.json', 'inno/apps/application.schema.json',
         'inno/cases/x-ray/index.html', 'inno/cases/chang-e/index.html',
         'x-ray.html', 'playground.html', 'inno/portal/museum-learning.css',
         'laureates.html', 'inno/report/index.html', 'nginx-inno-root.conf')


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
            replace_file(args.stage / name, release_dir / name)
        for directory in ('project', 'atom'):
            source = args.stage / directory
            expected = manifest['directories'][directory]
            pages = list(source.glob('*.html'))
            assert len(pages) == expected == 560, directory
            for page in pages:
                replace_file(page, release_dir / directory / page.name)
        nginx_config = Path('/etc/nginx/snippets/inno-root.conf')
        shutil.copy2(nginx_config, backup / 'nginx-inno-root.conf')
        shutil.copy2(args.stage / 'nginx-inno-root.conf', nginx_config)
        subprocess.run(['nginx', '-t'], check=True)
        switch(link, release_dir)
        subprocess.run(['systemctl', 'reload', 'nginx'], check=True)
        status, museum = fetch('/museum/')
        assert status == 200 and museum.count('class="museum-exhibit"') == 6, 'museum exhibits'
        assert '<base href="/inno/legacy/">' in museum and '找项目、读方法、核证据' in museum, 'museum base and guide'
        for src in re.findall(r'<img[^>]+src="([^"]+)"', museum)[:8]:
            status, _ = fetch(urllib.parse.urljoin('/inno/legacy/', src))
            assert status == 200, src
        status, categories = fetch('/museum/zones')
        assert status == 200 and '<base href="/inno/legacy/">' in categories, 'categories base'
        status, apps = fetch('/apps/')
        assert status == 200 and '选择合适的应用' in apps and 'id="app-empty"' in apps, 'apps layout and empty state'
        assert 'function applyFilters(updateUrl=true)' in apps and 'grid-column:1/-1' in apps, 'apps filters and feature'
        status, css = fetch('/inno/portal/museum-polish.css?v=20261116-157')
        assert status == 200 and '.museum-exhibits' in css, 'museum css'
        status, js = fetch('/inno/portal/museum-polish.js?v=20261116-157')
        assert status == 200 and 'data-exhibit-filter' in js, 'museum js'
        status, needs = fetch('/needs/')
        assert status == 200 and '从一个真实问题开始' in needs and 'id="live-demo-start"' in needs, 'needs workspace'
        workspace_version = re.search(r'needs-workspace\.css\?v=([0-9a-f]{8})', needs).group(1)
        live_version = re.search(r'needs-live-demo\.css\?v=([0-9a-f]{8})', needs).group(1)
        status, workspace_css = fetch('/inno/portal/needs-workspace.css?v=' + workspace_version)
        assert status == 200 and '.gd-needs-unknown-more' in workspace_css, 'needs css'
        status, workspace_js = fetch('/inno/portal/needs-workspace.js')
        assert status == 200 and '查看全部 ${rows.length} 项待确认' in workspace_js, 'needs unknowns'
        status, live_css = fetch('/inno/portal/needs-live-demo.css?v=' + live_version)
        assert status == 200 and 'grid-template-columns:minmax(0,1fr)' in live_css, 'live mobile grid'
        status, model = fetch('/model/')
        assert status == 200 and '让真实项目经验，参与下一次创新' in model and '<dt>MCP 只读工具</dt><dd>12</dd>' in model, 'model content and tools'
        status, about = fetch('/about/')
        assert status == 200 and 'class="about-section about-model"' in about and 'href="/model/"' in about, 'about model section'
        status, model_css = fetch('/inno/portal/model-official.css')
        assert status == 200 and '.mo-architecture-map' in model_css and '.mo-app-branches' in model_css, 'model css'
        assert 'mo-architecture-map' in model and 'mo-app-branches' in model, 'model visual architecture'
        status, registry = fetch('/apps/registry.json')
        assert status == 200 and registry.count('"id": "xray"') == 1 and registry.count('"id": "x-ray"') >= 1, 'xray registry'
        status, xray_case = fetch('/cases/x-ray/')
        assert status == 200 and '拆解一件国之重器' in xray_case, 'xray case'
        status, xray = fetch('/museum/x-ray?slug=2015-02')
        assert status == 200 and '<base href="/inno/legacy/">' in xray and 'id="partList"' in xray, 'xray base'
        status, _ = fetch('/inno/legacy/dismantle/2015-02.json')
        assert status == 200, 'xray parts json'
        status, playground = fetch('/museum/playground')
        assert status == 200 and '结果不代表工程精确或实际验证' in playground, 'playground boundary'
        for directory in ('project', 'atom'):
            links = [page for page in (release_dir / directory).glob('*.html') if page.name != 'index.html']
            assert len(links) == 560, directory
            for filename in ('2015-02.html', '2025-00.html'):
                content = (release_dir / directory / filename).read_text()
                assert '/museum/x-ray?slug=' in content and '/museum/playground?slug=' in content, directory / filename
        for route in ('/projects/', '/report/', '/mcp/', '/expo/'):
            status, _ = fetch(route)
            assert status == 200, route
        status, projects_page = fetch('/museum/laureates?level=%E9%87%91%E5%A5%96&year=2015')
        assert status == 200 and 'id="collection"' in projects_page, 'laureates merged project library'
        print(json.dumps({'release': RELEASE, 'current': str(link.resolve()), 'backup': str(backup),
                          'files': manifest['files']}, ensure_ascii=False, indent=2))
    except BaseException:
        switch(link, previous)
        shutil.copy2(backup / 'nginx-inno-root.conf', Path('/etc/nginx/snippets/inno-root.conf'))
        subprocess.run(['nginx', '-t'], check=True)
        subprocess.run(['systemctl', 'reload', 'nginx'], check=True)
        raise


if __name__ == '__main__':
    main()
