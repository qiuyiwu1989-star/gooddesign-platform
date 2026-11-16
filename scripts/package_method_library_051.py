"""Freeze a portable original-content package; third-party reading originals stay internal."""
import hashlib
import html
import json
import os
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT/'04-知识库/创新方法库/深度方法库-v0.1.0'
DEST = ROOT/'output/handoff/ML-001-方法库交付-20261023'


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')


def package():
    DEST.mkdir(parents=True, exist_ok=True)
    archive = DEST/'产品与机械创新方法库-v0.1.0.zip'
    if archive.exists():
        raise ValueError('交付包已存在，不覆盖已发布版本')
    for name in ['最终全量验收.json', '完整性验证.json']:
        source = ROOT/'output/051-browser'/name
        assert json.loads(source.read_text())['status'] == 'passed'
        shutil.copy2(source, DEST/name)
    shutil.copy2(LIB/'复核与验收/浏览验收.json', DEST/'浏览验收.json')
    shutil.copy2(ROOT/'output/051-browser/单元测试.txt', DEST/'单元测试.txt')
    prefix = '产品与机械创新方法库-v0.1.0'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for path in sorted(LIB.rglob('*')):
            if path.is_file():
                z.write(path, prefix+'/'+str(path.relative_to(LIB)))
    manifest = json.loads((LIB/'manifest.json').read_text())['files']
    with zipfile.ZipFile(archive) as z:
        expected = {prefix+'/'+name for name in manifest} | {prefix+'/manifest.json'}
        assert set(z.namelist()) == expected
        bad = [name for name, sha in manifest.items()
               if hashlib.sha256(z.read(prefix+'/'+name)).hexdigest() != sha]
        assert not bad
        report = {'status': 'passed', 'archive_files': len(expected), 'manifest_files': len(manifest),
                  'changed_or_missing': bad, 'zip_crc_test': z.testzip(),
                  'sha256': hashlib.sha256(archive.read_bytes()).hexdigest(), 'bytes': archive.stat().st_size}
        assert report['zip_crc_test'] is None
    dump(DEST/'ZIP验证.json', report)
    index = {'task': 'ML-001', 'release': '0.1.0', 'status': 'completed_research_content_release',
             'library': str(LIB), 'reader': str(LIB/'index.html'), 'explanation': str(LIB/'00-交付说明.md'),
             'zip': str(archive), 'zip_sha256': report['sha256'],
             'scope': {'methods': 48, 'wen_topics': 12, 'categories': 7, 'steps': 317,
                       'source_entries': 149, 'source_urls': 120, 'method_relations': 188},
             'validation': {'structure': 'passed', 'unit_tests': 9, 'browser_checks': 18,
                            'runtime_frozen_files_unchanged': 7, 'html_pages_without_local_broken_links': 61},
             'limitations': ['未专家审定', '工程效果未验证', '部分原典只核读公开摘要或目录',
                             '未注册既有运行器', 'WB12历史分类对应及WB10公式差异待核']}
    dump(DEST/'交付索引.json', index)
    reader = html.escape(os.path.relpath(LIB/'index.html', DEST))
    explanation = html.escape(os.path.relpath(LIB/'00-交付说明.md', DEST))
    links = [('最终全量验收.json', '全量验收'), ('浏览验收.json', '浏览验收'),
             ('完整性验证.json', '文件完整性'), ('ZIP验证.json', 'ZIP验证与指纹'), ('交付索引.json', '交付索引')]
    evidence = ''.join(f'<li><a href="{path}">{name}</a></li>' for path, name in links)
    (DEST/'验收入口.html').write_text(f'''<!doctype html><html lang="zh-CN">
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>方法库交付与验收</title><style>
body{{font-family:system-ui,sans-serif;background:#f4f5f8;color:#16181f;max-width:840px;margin:60px auto;padding:24px;line-height:1.9}}
a{{color:#5a4fe6}}section{{background:white;border:1px solid #dde0e9;border-radius:18px;padding:28px;margin:20px 0}}h1{{font-size:30px}}li{{margin:8px 0}}
</style><h1>产品与机械创新方法库</h1>
<p>内容版0.1.0 · 48项方法 + 12个闻邦椿体系专题 · 7个任务分类</p>
<section><h2>开始阅读</h2><ul>
<li><a href="{reader}">打开分类与检索入口</a></li>
<li><a href="{explanation}">交付说明与边界</a></li>
<li><a href="{archive.name}">离线ZIP包</a>（解压后打开index.html）</li>
</ul></section><section><h2>验收证据</h2>
<p>60个身份与指定步骤实读；61个HTML本地链接检查；9项单元测试；18项浏览检查；既有7个运行文件指纹一致。</p>
<ul>{evidence}</ul></section>
<p>当前为研究内容版，未专家审定、未工程效果验证，后续引擎集成另行进行。
部分原典、历史分类对应和评价公式差异逐项保留。12专题不算12项独立原创方法。</p></html>''')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(DEST)


if __name__ == '__main__':
    package()
