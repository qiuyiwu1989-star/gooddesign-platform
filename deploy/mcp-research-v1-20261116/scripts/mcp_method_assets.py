"""Explicit method profiles; no routing/execution, registration or deployment."""
import hashlib
import json
from pathlib import Path
import method_library_catalog as catalog
from method_engine_contracts import META

ROOT = Path(__file__).resolve().parents[1]
DEEP = ROOT/'02-研究/ML-021-内容质量深化'
BENCHMARK = ROOT/'04-知识库/创新方法库/标杆方法-v0.1'


def _sha(raw):return hashlib.sha256(raw).hexdigest()


def _safe(base, relative):
    if not isinstance(relative,str) or not relative or Path(relative).is_absolute() or '..' in Path(relative).parts or '\\' in relative or 'private-sources' in Path(relative).parts:
        raise ValueError('unsafe_asset_path')
    base=Path(base).resolve();p=base/relative
    if not p.resolve().is_relative_to(base):raise ValueError('asset_outside_scope')
    for node in [p,*p.parents]:
        if node==base:break
        if node.is_symlink():raise ValueError('symlink_asset_forbidden')
    return p


def _checked(base, relative, expected):
    raw=_safe(base,relative).read_bytes()
    if _sha(raw)!=expected:raise ValueError('asset_checksum_mismatch')
    return raw


def read_asset(method_id, profile='frozen'):
    if profile not in {'frozen','deep','benchmark'}:raise ValueError('unknown_asset_profile')
    row=next((r for r in catalog.catalog()['methods'] if method_id in (r['research_id'],r['method_id'])),None)
    if not row:raise ValueError('unknown_method_id')
    rid=row['research_id'];result=dict(method_id=rid,profile=profile,status='available',expert_certified=False,engineering_validated=False,execution_available=rid in META,execution_scope='existing_frozen_contract_only' if rid in META else 'content_only',partial_ratings={})
    if profile=='frozen':
        base=catalog.BASE if row['collection']=='frozen_0.1.0' else catalog.SUPPLEMENT
        raw=_checked(base,row['path'],row['sha256']);data=json.loads(raw)
        result.update(version=data['version'],sha256=_sha(raw),asset=data,review_scope='frozen_catalog_content_not_deep_profile')
    elif profile=='deep':
        index_raw=_safe(DEEP,'64项最终内容索引.json').read_bytes();index=json.loads(index_raw)
        entry=next((r for r in index['methods'] if r['method_id']==rid),None)
        if not entry:return dict(result,status='profile_unavailable',gaps=['no_reviewed_deep_entry'])
        path=_safe(ROOT,entry['candidate_path'])
        if not path.resolve().is_relative_to(DEEP.resolve()) or path.suffix!='.md' or path.parent.name!='稿件':raise ValueError('deep_manuscript_not_authorized')
        raw=path.read_bytes()
        if _sha(raw)!=entry['sha256']:raise ValueError('asset_checksum_mismatch')
        ratings={k:{'assessment':v.get('assessment',v.get('rating')),'reason':v.get('reason',v.get('scope',''))} for k,v in entry['seven_dimensions'].items()}
        result.update(version=entry.get('version',entry.get('candidate_version',None)),sha256=_sha(raw),index_sha256=_sha(index_raw),content=raw.decode(),ratings=ratings,partial_ratings={k:v for k,v in ratings.items() if v['assessment']=='局部'},review_scope=entry.get('scope','independent_agent_content_candidate'))
    else:
        index_raw=_safe(BENCHMARK,'目录.json').read_bytes();index=json.loads(index_raw)
        if index.get('schema_version')!='method-benchmark-catalog-0.1':raise ValueError('unknown_benchmark_schema')
        entry=next((r for r in index['methods'] if r['research_id']==rid),None)
        if not entry:return dict(result,status='profile_unavailable',gaps=['no_benchmark_for_method'])
        files=entry['files']
        # Verify every declared benchmark artifact, but return only public asset metadata.
        for name,h in files.items():_checked(BENCHMARK,f'{rid}/{name}',h)
        raw=_checked(BENCHMARK,f'{rid}/asset.json',files['asset.json']);data=json.loads(raw)
        if data.get('research_id')!=rid or data.get('asset_schema_version')!='method-asset-0.1':raise ValueError('benchmark_identity_or_schema_mismatch')
        result.update(version=data['benchmark_version'],sha256=_sha(raw),index_sha256=_sha(index_raw),asset=data,review_scope=index['scope'],candidate_contract_activated=False,isolated_effect_established=data.get('isolated_effect_established',False))
    return result


PROMPTS={
 'evidence_review':'固定项目与研究版本；读取主张及冻结引文，分开原文陈述、AI解释和目标假设；检查支持范围、反例与缺口，不将可追溯视为真实或目标适用。',
 'method_application':'显式选择frozen/deep/benchmark方法版本，核输入与停止条件；列中间产物、失败回返和下一步取证；没有执行契约不声明已执行算法或工程通过。',
 'transfer_review':'对照源问题、作用机制、条件、取舍与目标需求；将相同、不同、未知逐项列出，只提出结构迁移候选，不复制源参数为客户规格。'}


def workflow_prompt(name):
    if name not in PROMPTS:raise ValueError('unknown_workflow_prompt')
    return dict(name=name,version='1.0',text=PROMPTS[name],user_selected_template=True,executed=False)


def schema_resource(name):
    resources={
      'method_profiles':{'profiles':['frozen','deep','benchmark'],'default':'frozen','profile_selection':'explicit_no_fallback','execution':'existing_frozen_contract_only'},
      'quality_states':{'content_nature':['source_statement','ai_interpretation','ai_hypothesis'],'review_state':['unknown','not_assessed','reviewed_with_scope'],'rule':'traceability_does_not_imply_semantic_support_or_engineering_validation'}}
    if name not in resources:raise ValueError('unknown_public_schema')
    return dict(name=name,version='1.0',data=resources[name])
