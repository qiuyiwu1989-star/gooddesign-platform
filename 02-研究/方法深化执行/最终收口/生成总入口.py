from pathlib import Path
import json,os,re
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'02-研究/方法深化执行';OUT=Path(__file__).resolve().parent
inv=json.loads((OUT/'64项交付核对.json').read_text())
task_by_id={x['task_id']:x for x in json.loads((ROOT/'00-项目管理/ML-018-逐法深化任务/任务台账.json').read_text())['tasks']}
def link(p):return os.path.relpath(p,OUT)
def version(p):return tuple(map(int,re.search(r'-v([\d.]+)$',p.name).group(1).split('.')))
rows=[];records=[]
for r in inv['methods']:
 original=ROOT/r['path'];revs=[ROOT/x['path']for x in r['revisions']if x.get('integrity')=='verified'and not x.get('missing_required')];latest=max(revs,key=version)if revs else original
 rid=r['method_id'];published=False
 records.append({'task_id':r['task_id'],'method_id':rid,'name':r['name'],'kind':'lineage_topic'if rid.startswith('WB')else'method_dossier','preferred_authored_path':str(latest.relative_to(ROOT)),'preferred_manifest_sha256':__import__('hashlib').sha256((latest/'manifest.json').read_bytes()).hexdigest(),'original_path':r['path'],'version_role':'latest_integrity_checked_package_not_automatic_professional_approval','reviewer':task_by_id[r['task_id']].get('independent_reviewer'),'review_status':task_by_id[r['task_id']].get('status'),'review_level':'independent_agent_not_domain_expert','research_document':str((latest/'研究说明.md').relative_to(ROOT)),'source_claims':str((latest/'来源与主张.json').relative_to(ROOT)),'suggested_calling_document':str((latest/'调用说明.json').relative_to(ROOT)),'teaching_artifacts_directory':str((latest/'教学包').relative_to(ROOT)),'new_runtime_contract_implemented':False,'engineering_validated':False,'expert_certified':False,'online_published':published})
 rows.append(f"|{r['sequence']:02d}|{rid}|[{r['name']}]({link(latest/'研究说明.md')})|[来源]({link(latest/'来源与主张.json')}) · [调用建议]({link(latest/'调用说明.json')})|{'修订版'if revs else'作者版'}|")
(OUT/'方法深化库索引.json').write_text(json.dumps({'schema':'method-deepening-research-catalog-1','scope':'64 bounded research/teaching packages; not 64 new runtime solvers','methods':records,'private_originals_not_exported':True,'review_evidence_is_separate':True},ensure_ascii=False,indent=2))
(OUT/'64项阅读索引.md').write_text('# 64项方法深化阅读索引\n\n按排期排列，包含52方法档案与12闻邦椿谱系专题。优先链接已核指纹的最新作者修订版；这不是自动批准或专家评级。终审与未决项见总报告及独立报告。\n\n|序号|方法ID|深入研究说明|依据与调用|版本|\n|---|---|---|---|---|\n'+'\n'.join(rows)+'\n')
print('64 human links and version-bound research catalog generated; no runtime tools registered.')
