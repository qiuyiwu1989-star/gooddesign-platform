"""Package review-ready material separately from the already frozen technical pilot."""
import hashlib
import json
import zipfile
from method_engine import ROOT


def package():
    base=ROOT/'output/method-engine-ML003'
    paired=json.loads((base/'paired-comparison/status.json').read_text())
    verified=json.loads((base/'paired-comparison/execution-verification.json').read_text())
    if paired['paired_count']!=12 or verified['paired_tasks']!=12 or not verified['all_pair_configurations_equal']:
        raise ValueError('paired_execution_not_complete')
    technical=ROOT/'output/handoff/ML-003-方法引擎技术试用-v0.2.0'
    proof=json.loads((technical/'package-verification.json').read_text())
    archive=technical/'method-engine-pilot-v0.2.0.zip'
    if hashlib.sha256(archive.read_bytes()).hexdigest()!=proof['sha256']:raise ValueError('technical_archive_changed')
    files={}
    for pattern in ['03-平台规划/专家级质量标准与提升-v1-20261025/*',
                    '03-平台规划/方法调用引擎架构-v1-20261025/*',
                    '00-项目管理/ML-003*.md',
                    '04-知识库/创新方法库/来源主张复核工作区-v0.1/*',
                    'output/method-engine-ML003/six-node-review/*',
                    'output/method-engine-ML003/paired-comparison/review/*']:
        for p in ROOT.glob(pattern):
            if p.is_file():files[str(p.relative_to(ROOT))]=p
    for relative in ['paired-comparison/status.json','paired-comparison/execution-verification.json','browser-check.json']:
        p=base/relative;files[str(p.relative_to(ROOT))]=p
    for script in ['compare_method_engine_pilot.py','summarize_method_comparison.py','export_method_engine_review.py','build_method_source_review_index.py','package_method_review_handoff.py']:
        p=ROOT/'scripts'/script;files['scripts/'+script]=p
    files['技术包/method-engine-pilot-v0.2.0.zip']=archive
    files['技术包/package-verification.json']=technical/'package-verification.json'
    readme='''# 方法库、调用引擎与专家质量交付

版本：技术试用v0.2.0，专家级验收仍待完成。

1. 技术包中的ZIP含60份方法/谱系档案、六方法执行契约、18工具MCP、代码与测试证据。它是既有项目的覆盖包，需兼容项目工作副本及固定Python运行环境；不是新机器一键安装器。已实做恢复运行验证。
2. 先读平台规划中的专家级标准、指标口径和引擎架构，再读项目管理的运行与评审说明。
3. six-node-review提供实际六节点模型草稿及独立评审空表；paired-comparison/review提供12题的匿名配对提案。双方均待领域专家评判，不能当专家参照答案。
4. 来源主张复核工作区包含60档、149来源记录对应的283条作者支持范围陈述。这里只完成抽取、定位与分派准备，语义支持及关键程度仍待核对。

验收事实：64项方法相关测试、16项双服务SDK检查通过；技术包588文件恢复指纹检查通过，恢复后18工具和六节点计划可用；12题×两条件共24次新模型调用形成配对材料，调用配置逐对相同。不能由此推导专家级达标率或工程可行性。

未完成：独立领域专家评审、真实客户试点、专家参照和留出任务、相关工程计算或实测。没有以AI自评代替这些环节。外部案例原文、运行数据库、私有模型日志、匿名条件映射和凭证均不在本包；证据支持评审须通过授权案例MCP重读指定版本。
'''
    index='''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>方法库与方法引擎交付</title><style>body{font:16px/1.9 system-ui;max-width:850px;margin:40px auto;padding:24px;background:#f4f5f8;color:#17212b}section{background:white;border-radius:16px;padding:24px;margin:18px 0}a{color:#4944ce}strong{color:#87500e}</style><h1>方法库与方法引擎</h1><p><strong>技术试用版已交付；专家级验收待完成。</strong></p><section><h2>已形成的资产</h2><p>60份档案 · 六节点执行契约 · 18个MCP工具 · 64项方法相关测试 · 16项双服务联调检查。</p><p>技术包588文件已恢复校验；12组方法引擎与普通Agent提案已形成，尚未由专家判优。</p><a href="method-engine-complete-handoff-v0.2.0.zip">下载完整交付包</a> · <a href="阅读说明.md">阅读说明</a> · <a href="handoff-verification.json">包指纹与范围</a></section><section><h2>专家质量如何验收</h2><p>先检查关键错误与证据边界，再按八维锚点评审。独立评审、真实客户任务、留出题和工程证据各自记录，尚未完成的项保持待核。283条来源支持范围陈述已经整理为复核队列，未被当成已证实结论。</p></section>'''
    dest=ROOT/'output/handoff/ML-003-完整交付-v0.2.0';dest.mkdir(parents=True,exist_ok=True)
    target=dest/'method-engine-complete-handoff-v0.2.0.zip'
    if target.exists():raise ValueError('frozen_handoff_already_exists')
    manifest={'type':'technical_pilot_plus_review_material','expert_certified':False,
              'files':{name:hashlib.sha256(path.read_bytes()).hexdigest() for name,path in files.items()},
              'exclusions':['case source bodies','SQLite','model inputs and event logs','blind condition mapping','credentials']}
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,path in sorted(files.items()):z.write(path,name)
        z.writestr('阅读说明.md',readme)
        z.writestr('HANDOFF-MANIFEST.json',json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
        for name,sha in manifest['files'].items():assert hashlib.sha256(z.read(name)).hexdigest()==sha
    verification={'status':'passed_zip_crc_and_file_hashes','archive_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
                  'files':len(files),'technical_restore':proof['restore'],'expert_certified':False,'paired_expert_scores':None}
    (dest/'阅读说明.md').write_text(readme);(dest/'index.html').write_text(index)
    (dest/'handoff-verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'archive':str(target),'files':len(files),'expert_certified':False},ensure_ascii=False))


if __name__=='__main__':package()
