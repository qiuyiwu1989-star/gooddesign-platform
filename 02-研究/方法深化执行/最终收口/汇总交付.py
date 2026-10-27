"""Inventory authored packages and revisions. Integrity is never expert certification."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'02-研究/方法深化执行';OUT=Path(__file__).resolve().parent
TASKS=ROOT/'00-项目管理/ML-018-逐法深化任务/任务台账.json'
def inspect(folder):
 p=folder/'manifest.json'
 if not p.exists():return {'manifest_present':False,'integrity':'not_frozen'}
 try:
  m=json.loads(p.read_text());items=m.get('files',[])
  if isinstance(items,dict):items=[{'path':k,'sha256':v}for k,v in items.items()]
  errors=[];private=[]
  for e in items:
   f=folder/e['path']
   if not f.resolve().is_relative_to(folder.resolve()):errors.append(e['path']+':escape');continue
   if any(k in e['path']for k in ['private-sources','核读原件','隔离副本']):private.append(e['path'])
   if not f.is_file()or hashlib.sha256(f.read_bytes()).hexdigest()!=e['sha256']:errors.append(e['path'])
  required=['研究说明.md','来源与主张.json','反例与迁移.md','调用说明.json','审核与版本.json']
  missing=[n for n in required if not(folder/n).is_file()]
  meta=json.loads((folder/'审核与版本.json').read_text())if(folder/'审核与版本.json').exists()else{}
  return {'manifest_present':True,'integrity':'verified'if not errors else'mismatch_or_author_writing','manifest_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'files':len(items),'hash_errors':errors,'private_entries':private,'missing_required':missing,'authored_metadata':meta,'expert_certification_inferred':False}
 except Exception as e:return {'manifest_present':True,'integrity':'unreadable_or_author_writing','error':str(e)}
def main():
 ts=json.loads(TASKS.read_text())['tasks'];rows=[]
 for t in ts:
  ident=t['task_id']+'-'+t['method_id'];folder=BASE/ident
  revisions=[]
  for rev in sorted((BASE/'修订版').glob(ident+'-v*')):
   revisions.append({'path':str(rev.relative_to(ROOT)),**inspect(rev)})
  rows.append({'task_id':t['task_id'],'sequence':t['sequence'],'method_id':t['method_id'],'name':t['name'],'batch':t['batch'],'path':str(folder.relative_to(ROOT)),**inspect(folder),'revisions':revisions})
 summary={'date':'2026-10-27','scope':'authored_package_inventory_and_hash_checks_not_semantic_or_professional_approval','planned':64,'authored_manifests':sum(r.get('integrity')=='verified'for r in rows),'complete_required_files':sum(r.get('integrity')=='verified'and not r.get('missing_required')for r in rows),'revision_packages':sum(len(r['revisions'])for r in rows),'revision_integrity_errors':sum(x.get('integrity')!='verified'for r in rows for x in r['revisions']),'all_expert_certified':False,'online_content_replaced':False,'methods':rows}
 (OUT/'64项交付核对.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
 print(json.dumps({k:v for k,v in summary.items()if k!='methods'},ensure_ascii=False))
if __name__=='__main__':main()
