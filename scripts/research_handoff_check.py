# coding: utf-8
"""Portable standard-library validator for a private pinned research snapshot."""
import hashlib,json,re
from pathlib import Path

def load(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def safe(root,name):
 if not isinstance(name,str)or not name or '\\' in name or Path(name).is_absolute()or '..' in Path(name).parts:raise ValueError('不安全的包路径')
 path=root/name
 if any(x.is_symlink()for x in [path,*path.parents]if x!=root.parent):raise ValueError('包内不允许符号链接')
 path.resolve().relative_to(root.resolve())
 return path

def evidence_nodes(value):
 if isinstance(value,dict):
  if all(k in value for k in ('source_id','chunk_id','quote','chunks_path','chunks_sha256','source_sha256','quote_sha256')):yield value
  for v in value.values():yield from evidence_nodes(v)
 elif isinstance(value,list):
  for v in value:yield from evidence_nodes(v)

def check(root):
 root=Path(root).resolve();manifest=load(root/'manifest.json')
 if manifest.get('schema')!='research-handoff-1.0':raise ValueError('未知包规范')
 
 if any(p.is_symlink()for p in root.rglob('*')):raise ValueError('包内不允许符号链接')
 files=manifest['files'];actual={str(p.relative_to(root))for p in root.rglob('*')if p.is_file()}
 if actual!=set(files)|{'manifest.json'}:raise ValueError('文件清单不一致')
 for name,h in files.items():
  if sha(safe(root,name))!=h:raise ValueError('文件指纹不符: '+name)
 info=load(root/'交付概览.json');data=load(root/'研究版本/档案.json');pub=load(root/'研究版本/manifest.json')
 pid=info['project_id'];revision=info['research_revision']
 if not re.fullmatch(r'research-\d{6}',revision)or data['project_id']!=pid or data['publication_revision']!=revision or pub['revision']!=revision:raise ValueError('研究身份不一致')
 for name,h in pub['files'].items():
  if sha(safe(root,'研究版本/'+name))!=h:raise ValueError('研究版本指纹不符')
 if int(revision.split('-')[1])>1 and sha(root/'历史对照/前序manifest.json')!=pub['previous_manifest_sha256']:raise ValueError('前序对照指纹不符')
 sources=load(root/'资料库/来源目录.json')['items'];byid={x['id']:x for x in sources}
 if len(byid)!=len(sources):raise ValueError('来源身份重复')
 for x in sources:
  if x['ownership']['scope']!='project':raise ValueError('混入非项目原件')
  if sha(safe(root,'资料库/'+x['original']))!=x['sha256']:raise ValueError('原件身份不符')
  for key in ('document','chunks'):safe(root,'资料库/'+x[key]).read_bytes()
 count=0
 for e in evidence_nodes(data):
  x=byid.get(e['source_id'])
  if not x:raise ValueError('缺少引用来源: '+e['source_id'])
  if e['source_sha256']!=x['sha256']:raise ValueError('引用原件身份不符')
  o=x.get('origin',{})
  if o.get('kind')=='project_source_excerpt':
   text=o.get('selection_text','')
   if not text or hashlib.sha256(text.encode()).hexdigest()!=o.get('selection_sha256')or e['quote']not in text:raise ValueError('选录原文边界不符')
  chunks=safe(root,'资料库/'+e['chunks_path'])
  if sha(chunks)!=e['chunks_sha256']:raise ValueError('引用证据块指纹不符')
  block=next((b for b in load(chunks)if b['id']==e['chunk_id']),None)
  if not block or not e['quote']or e['quote']not in block['text']or hashlib.sha256(e['quote'].encode()).hexdigest()!=e['quote_sha256']:raise ValueError('引用摘录不符')
  count+=1
 for r in data['records']:
  if r['project_id']!=pid:raise ValueError('记录项目不符')
  for c in r['cells'].values():
   if c.get('value_state')=='known'and c.get('content_nature')!='source_statement':raise ValueError('事实层混入推断')
 for i in data.get('interpretations',[]):
  if i.get('content_nature')not in ('ai_interpretation','ai_hypothesis'):raise ValueError('AI内容标签缺失')
 if info['guide_version']:
  notes=load(root/'阅读导读/导读.json');m=load(root/'阅读导读/manifest.json')
  if notes['project_id']!=pid or notes['research_revision']!=revision or notes['version']!=info['guide_version']or notes['content_nature']!='ai_reading_guide' or notes['dataset_sha256']!=sha(root/'研究版本/档案.json'):raise ValueError('导读绑定不符')
  if sha(root/'阅读导读/导读.json')!=m['sha256']or sha(root/'阅读导读/导读.md')!=m['markdown_sha256']:raise ValueError('导读指纹不符')
  if [x['module_id']for x in notes['modules']]!=list(range(1,9)):raise ValueError('导读模块不完整')
  ids={x['id']for x in data['records']}
  if any(set(x['record_ids'])-ids for x in notes['modules']):raise ValueError('导读引用缺失')
 if info.get('review_version'):
  report=load(root/'研究评估/评估.json');j=report['judgment'];m=load(root/'研究评估/manifest.json')
  for name,h in m['files'].items():
   if sha(safe(root,'研究评估/'+name))!=h:raise ValueError('研究评估指纹不符')
  if j['project_id']!=pid or j['research_revision']!=revision or j['version']!=info['review_version']or j['dataset_sha256']!=sha(root/'研究版本/档案.json')or j['content_nature']!='ai_research_review'or report.get('quality_score')is not None or report.get('expert_reviewed')is not False:raise ValueError('研究评估绑定不符')
 return dict(project_id=pid,revision=revision,files=len(files),sources=len(sources),records=len(data['records']),evidence=count,history_scope='single_snapshot_not_full_chain',expert_reviewed=data.get('expert_reviewed',False))
if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('folder',nargs='?',default=str(Path(__file__).resolve().parent));args=ap.parse_args();print(json.dumps(check(args.folder),ensure_ascii=False,indent=2))
