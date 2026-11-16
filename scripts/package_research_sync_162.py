import hashlib
import json
import tarfile
from pathlib import Path

from package_inno_release_093 import research_files

ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / '04-知识库/项目库'
OUT = ROOT / 'output/research-sync-162'
RELEASE = '20261116-162-research-sync'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    projects, sources, experience_originals = research_files()
    sources = sorted(set(sources))
    records = {}
    for source in sources:
        assert source.is_file() and not source.is_symlink(), source
        relative = source.relative_to(LIBRARY)
        assert 'private-sources' not in relative.parts and '__pycache__' not in relative.parts, relative
        records[relative.as_posix()] = {'bytes': source.stat().st_size, 'sha256': sha(source)}
    versions = []
    for project in projects:
        versions.extend(path for path in (LIBRARY / project / '研究工作区/版本').glob('research-*') if path.is_dir())
    assert len(projects) == 103 and len(versions) == 221
    index = json.loads((LIBRARY / '项目索引.json').read_text())
    assert len(index['projects']) == 560

    OUT.mkdir(parents=True, exist_ok=False)
    package = OUT / 'research-snapshot.tar.gz'
    with tarfile.open(package, 'w:gz') as archive:
        for source in sources:
            archive.add(source, arcname=source.relative_to(LIBRARY).as_posix())
    manifest = {
        'release': RELEASE,
        'catalog_count': 560,
        'research_project_count': len(projects),
        'research_version_count': len(versions),
        'research_projects': projects,
        'experience_source_originals': experience_originals,
        'private_originals_in_research_snapshot': False,
        'files': records,
        'package': {'bytes': package.stat().st_size, 'sha256': sha(package)},
    }
    (OUT / 'release-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({key: value for key, value in manifest.items() if key not in ('files', 'research_projects')}, ensure_ascii=False, indent=2))
    print('files', len(records), 'bytes', sum(record['bytes'] for record in records.values()))


if __name__ == '__main__':
    main()
