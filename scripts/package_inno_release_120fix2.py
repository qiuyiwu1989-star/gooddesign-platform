import hashlib
import json
import re
import shutil
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RELEASE = '20261113-120-fix2'
OUT = ROOT / 'output/deploy-120-fix2'
STATIC = ROOT / 'output/inno-preview/gooddesign-site'
RUNTIME_FILES = [
    'extensions/application-center/apps.json',
]
MCP_FILES = []


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def production_static():
    target = OUT / 'public-site'
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(STATIC, target)
    for path in target.rglob('*.html'):
        relative = path.relative_to(target)
        text = path.read_text(encoding='utf-8')
        if relative.parts[0] != 'inno' and relative.name != 'site-index.html':
            if re.search(r'<base\b[^>]*>', text, re.I):
                text = re.sub(r'<base\b[^>]*href=["\'][^"\']*["\'][^>]*>', '<base href="/inno/legacy/">', text, count=1, flags=re.I)
            else:
                text = text.replace('<head>', '<head><base href="/inno/legacy/">', 1)
            text = re.sub(r'((?:href|src)=["\'])/(?!inno/|api/)', r'\1inno/legacy/', text)
        elif relative.as_posix() == 'inno/museum/index.html':
            text = re.sub(r'<base\b[^>]*href=["\'][^"\']*["\'][^>]*>', '<base href="/inno/legacy/">', text, count=1, flags=re.I)
        path.write_text(text, encoding='utf-8')
    return target


def make_tar(name, sources, base):
    path = OUT / name
    def safe_member(item):
        if '__pycache__' in item.name or item.name.endswith('.pyc') or 'private-sources' in item.name or item.issym() or item.islnk():
            return None
        return item
    with tarfile.open(path, 'w:gz') as archive:
        for source in sources:
            archive.add(source, arcname=str(source.relative_to(base)), filter=safe_member)
    return path


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    public = production_static()
    public_tar = make_tar('public-site.tar.gz', list(public.iterdir()), public)
    methods = STATIC / 'inno/methods'
    methods_tar = make_tar('methods-site.tar.gz', list(methods.rglob('*')), methods)
    runtime_tar = make_tar('runtime-overlay.tar.gz', [ROOT / name for name in RUNTIME_FILES], ROOT)
    packages = [public_tar, methods_tar, runtime_tar]
    if MCP_FILES:
        packages.append(make_tar('mcp-overlay.tar.gz', [ROOT / name for name in MCP_FILES], ROOT))
    manifest = {
        'release': RELEASE,
        'public_html_pages': len(list(public.rglob('*.html'))),
        'method_files': len([path for path in methods.rglob('*') if path.is_file()]),
        'runtime_files': RUNTIME_FILES,
        'mcp_files': MCP_FILES,
        'research_data_changed': False,
        'credentials_changed': False,
        'packages': {path.name: {'bytes': path.stat().st_size, 'sha256': sha(path)} for path in packages},
    }
    (OUT / 'release-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
