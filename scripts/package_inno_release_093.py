import hashlib
import json
import re
import shutil
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RELEASE = '20261104-093e'
OUT = ROOT / 'output/deploy-093'
STATIC = ROOT / 'output/inno-preview/gooddesign-site'
METHODS = ROOT / 'output/method-site-release/site'
LIBRARY = ROOT / '04-知识库/项目库'


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


def make_tar(name, sources, base=ROOT):
    path = OUT / name
    def safe_member(item):
        if '__pycache__' in item.name or item.name.endswith('.pyc') or 'private-sources' in item.name or item.issym() or item.islnk():
            return None
        return item
    with tarfile.open(path, 'w:gz') as archive:
        for source in sources:
            archive.add(source, arcname=str(source.relative_to(base)), filter=safe_member)
    return path


def research_files():
    files = [LIBRARY / '项目索引.json', LIBRARY / '2025-04/01-项目档案.md']
    projects = []
    for project in sorted(LIBRARY.iterdir()):
        workspace = project / '研究工作区'
        if not workspace.is_dir():
            continue
        projects.append(project.name)
        files.extend(path for path in workspace.rglob('*') if path.is_file())
        data = project / '数据'
        if data.is_dir():
            files.extend(path for path in data.rglob('*') if path.is_file())
        for pattern in ('来源/*/chunks.json', '来源/*/metadata.json', '资料归属.json'):
            files.extend(path for path in project.glob(pattern) if path.is_file())
    experience_originals = []
    experiences = json.loads((ROOT / 'output/innovation-loop-024/experience/active-experience-catalog-v1.json').read_text())
    for record in experiences:
        for evidence in record['evidence_refs']:
            project = LIBRARY / evidence['project_id']
            state = json.loads((project / '数据/管道状态.json').read_text())
            original = project / state['sources'][evidence['source_id']]['original']
            files.append(original)
            experience_originals.append(str(original.relative_to(LIBRARY)))
    return projects, files, sorted(set(experience_originals))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    public = production_static()
    public_tar = make_tar('public-site.tar.gz', list(public.iterdir()), base=public)
    methods_tar = make_tar('methods-site.tar.gz', list(METHODS.iterdir()), base=METHODS)
    runtime_sources = [ROOT / name for name in ('scripts', 'extensions', 'deploy', '04-知识库/创新方法库', '04-知识库/标杆案例', '02-研究/ML-021-内容质量深化', 'output/innovation-loop-024', 'output/rubber-tapping-pilot/需求包.json', '00-项目管理/061-统一MCP使用说明.md')]
    runtime_tar = make_tar('runtime-overlay.tar.gz', runtime_sources)
    projects, files, experience_originals = research_files()
    research_tar = make_tar('research-snapshot.tar.gz', files, base=LIBRARY)
    packages = [public_tar, methods_tar, runtime_tar, research_tar]
    manifest = {
        'release': RELEASE,
        'research_projects': projects,
        'research_project_count': len(projects),
        'public_html_pages': len(list(public.rglob('*.html'))),
        'method_files': len([path for path in METHODS.rglob('*') if path.is_file()]),
        'experience_source_originals': experience_originals,
        'private_originals_in_research_snapshot': False,
        'packages': {path.name: {'bytes': path.stat().st_size, 'sha256': sha(path)} for path in packages},
    }
    (OUT / 'release-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
