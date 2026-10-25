"""Package project-relative pilot overlay, then restore and exercise MCP without customer data."""
import asyncio
import hashlib
import io
import json
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
from method_engine import ROOT
from method_engine_contracts import CONTRACT_VERSION


def selected_files():
    files=set()
    patterns=['scripts/method_engine*.py','scripts/method_case_adapter.py','scripts/method_application_adapter.py','scripts/method_quality_gate.py',
              'scripts/method_library_051.py','scripts/method_library_assets_051/*',
              'scripts/*method_engine*.py','tests/test_method_engine*.py','tests/method_engine_fixtures.py',
              'tests/test_method_quality_gate.py','tests/test_method_library_051.py','tests/test_method_application_adapter.py',
              'requirements-method-engine.txt','specs/ML-003*','00-项目管理/ML-003*',
              '04-知识库/创新方法库/执行契约-v'+CONTRACT_VERSION+'/**/*','04-知识库/创新方法库/深度方法库-v0.1.0/**/*']
    for pattern in patterns:files.update(p for p in ROOT.glob(pattern) if p.is_file())
    base=ROOT/'output/method-engine-ML003'
    for name in ['index.html','mcp-integration.json','live-model-mcp.json','adversarial-review.json','quality-passport.json',
                 'live-quality-packet.json','mcp-config.local.json','all-method-tests.txt','engine-tests.txt','browser-check.json']:
        if (base/name).is_file():files.add(base/name)
    for pattern in ['expert-review-pack/**/checked-result.json','expert-review-pack/*.json','expert-review-pack/*.md',
                    'live-chain/*/report.json','live-chain/*/post-review-recheck.json','live-revision/*/report.json',
                    'v'+CONTRACT_VERSION+'/*.json','v'+CONTRACT_VERSION+'/*/report.json','v'+CONTRACT_VERSION+'/*.txt','v'+CONTRACT_VERSION+'/*.md','v'+CONTRACT_VERSION+'/*.html']:
        files.update(p for p in base.glob(pattern) if p.is_file())
    return sorted(files)


async def restore_check(archive):
    with tempfile.TemporaryDirectory(prefix='method-engine-restore-',dir=ROOT/'output') as temp:
        temp=Path(temp)
        baseline=subprocess.check_output(['git','archive','--format=tar','HEAD','scripts'],cwd=ROOT)
        with tarfile.open(fileobj=io.BytesIO(baseline)) as tar:tar.extractall(temp,filter='data')
        with zipfile.ZipFile(archive) as z:
            names=z.namelist()
            if any(Path(n).is_absolute() or '..' in Path(n).parts for n in names):raise ValueError('unsafe_archive_path')
            z.extractall(temp)
            manifest=json.loads(z.read('PILOT-MANIFEST.json'))
        for name,expected in manifest['files'].items():
            if hashlib.sha256((temp/name).read_bytes()).hexdigest()!=expected:raise ValueError('restored_hash_mismatch:'+name)
        async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(temp/'scripts/method_engine_mcp.py')])) as (r,w):
            async with ClientSession(r,w) as session:
                init=await session.initialize()
                tools=await session.list_tools()
                result=await session.call_tool('method_get',{'method_id':'R17'})
                if result.isError:raise ValueError(str(result.content))
                data=result.structuredContent or json.loads(result.content[0].text)
                assert data['contract']['artifact_type']=='ConceptSet'
                task={'task_id':'RESTORE','revision':'t1','object':'fixture','desired_outcome':'study','boundary':'teaching only'}
                result=await session.call_tool('method_plan',{'task':task})
                if result.isError:raise ValueError(str(result.content))
                plan=result.structuredContent or json.loads(result.content[0].text)
                assert len(plan['nodes'])==6
        return {'status':'passed','files_verified':len(manifest['files']),'mcp_tools':len(tools.tools),
                'protocol':init.protocolVersion,'plan_nodes':len(plan['nodes']),
                'scope':'restored_overlay_plus_existing_tracked_scripts_and_existing_python_runtime_not_new_machine_install_or_expert_test'}


def main():
    dest=ROOT/('output/handoff/ML-003-方法引擎技术试用-v'+CONTRACT_VERSION);dest.mkdir(parents=True,exist_ok=True)
    archive=dest/('method-engine-pilot-v'+CONTRACT_VERSION+'.zip')
    if archive.exists():raise ValueError('frozen_pilot_package_exists_do_not_overwrite')
    files=selected_files();manifest={'type':'project_overlay_not_standalone_installer','version':CONTRACT_VERSION,
        'base_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        'excluded':['case originals','SQLite databases','model input/event logs','credentials'],
        'expert_certified':False}
    readme=('Method engine technical pilot overlay '+CONTRACT_VERSION+'. Extract into an existing compatible gooddesign project checkout. '
            'Requires its tracked helper scripts, pinned project Python runtime and configured Codex authentication for optional model calls. '
            'Case MCP data is separate and not bundled. Host config paths are local examples and must be adjusted when moved. '
            'Read output/method-engine-ML003/v'+CONTRACT_VERSION+'/README.md and 00 management guide first; root proof pages may describe historical runs. '
            'Tests/real model calls prove bounded operation, not expert-level or engineering validation. No auto publication.\n')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for path in files:z.write(path,str(path.relative_to(ROOT)))
        z.writestr('PILOT-MANIFEST.json',json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
        z.writestr('PILOT-README.txt',readme)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for name,sha in manifest['files'].items():assert hashlib.sha256(z.read(name)).hexdigest()==sha
    restored=asyncio.run(restore_check(archive))
    report={'status':'passed','archive':str(archive),'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),
            'bytes':archive.stat().st_size,'files':len(files),'restore':restored,'expert_certified':False}
    (dest/'package-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    (dest/'README.txt').write_text(readme)
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
