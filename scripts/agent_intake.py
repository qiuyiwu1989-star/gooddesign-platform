"""065 batch initialization and read-only mechanical checks; no ingestion or approval."""
import argparse,json,re,hashlib,datetime,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
LIB=ROOT/'04-知识库/项目库'
DOC=ROOT/'04-知识库/项目档案标准-v1/外部Agent协作-v1'
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rows(p):
 out=[]
 for n,line in enumerate(p.read_text(encoding='utf-8').splitlines(),1):
  if line.strip():
   v=json.loads(line)
   if not isinstance(v,dict):raise ValueError(f'{p.name}:{n} must be object')
   out.append(v)
 return out
def catalog():return {x['id']:x for x in json.loads((LIB/'项目索引.json').read_text())['projects']}
def batch_path(pid,bid):
 if pid not in catalog():raise ValueError('unknown project_id')
 if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9-]{2,95}',bid):raise ValueError('batch_id must be unique ASCII letters/digits/hyphen, 3..96 chars')
 return LIB/pid/'04-深研素材/外部投递'/bid
def init(pid,bid,agent,topic):
 p=batch_path(pid,bid)
 # Do not follow symlinked parents or overwrite another batch.
 if any(x.is_symlink()for x in [p,*p.parents]if x!=ROOT.parent):raise ValueError('symlink parent refused')
 p.mkdir(parents=True,exist_ok=False)
 for name in ['原件','可读件','图片']:(p/name).mkdir()
 row=catalog()[pid]
 dump(p/'batch.json',dict(schema='agent-intake-1.0',project_id=pid,project_name=row.get('name')or row.get('title'),batch_id=bid,agent=agent,topic=topic,created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='draft'))
 for name in ['sources.jsonl','claims.jsonl','queries.jsonl']:(p/name).write_text('',encoding='utf-8')
 (p/'交接说明.md').write_text('# 本轮交接\n\n状态：草稿，尚未收集。\n\n## 实际新增与重复\n\n## 范围、冲突与缺口\n\n## 访问失败与下一步\n',encoding='utf-8')
 return {'created':str(p),'status':'empty_draft_not_collected'}
def validate(p):
 errors=[];warnings=[]
 p=Path(p).absolute()
 def check(ok,msg):
  if not ok:errors.append(msg)
 def resource(rel):
  if not isinstance(rel,str)or not rel or Path(rel).is_absolute()or '..'in Path(rel).parts:raise ValueError('unsafe relative file path')
  f=p/rel
  if any(x.is_symlink()for x in [f,*f.parents]):raise ValueError('symlink refused')
  f.resolve().relative_to(p.resolve())
  if not f.is_file():raise ValueError('missing file: '+rel)
  return f
 try:
  b=json.loads((p/'batch.json').read_text());check(b.get('schema')=='agent-intake-1.0','schema unsupported')
  expected=batch_path(b.get('project_id'),b.get('batch_id'));check(p==expected,'batch is not under its declared project/batch path')
  check(b.get('status')=='submitted','batch must be submitted, not draft');check(bool(b.get('agent'))and bool(b.get('topic'))and bool(b.get('created_at')),'batch agent/topic/time missing')
  check(not any(x.is_symlink()for x in [p,*p.parents]),'batch parent symlink refused')
  ss=rows(p/'sources.jsonl');cs=rows(p/'claims.jsonl');qs=rows(p/'queries.jsonl');check(bool(ss),'sources empty');check(bool(qs),'actual query log empty');resource('交接说明.md')
  sources={};total_files=0
  for s in ss:
   sid=s.get('source_id');check(isinstance(sid,str)and bool(re.fullmatch(r'[A-Za-z0-9_-]{1,80}',sid)),'invalid source_id');check(sid not in sources,'duplicate source_id');sources[sid]=s
   for k in ['title','publisher','retrieved_at','source_type','access_status','read_scope','project_relation','relation_basis','rights_status']:check(bool(s.get(k)),f'{sid}: missing {k}')
   check(bool(re.match(r'https?://\S+$',s.get('url',''))),f'{sid}: invalid URL')
   check(s.get('access_status')in ['downloaded','link_only','blocked','failed'],f'{sid}: access_status invalid')
   check(s.get('read_scope')in ['metadata','abstract','excerpt','fulltext','ocr_unchecked','unread'],f'{sid}: read_scope invalid')
   check(s.get('project_relation')in ['project_source','related_technology','shared_reference','unresolved'],f'{sid}: relation invalid')
   files=s.get('files',[]);check(isinstance(files,list),f'{sid}: files must be list');roles=set()
   for item in files:
    f=resource(item['path']);roles.add(item.get('role'));total_files+=1
    check(item.get('role')in ['original','readable','image'],f'{sid}: file role invalid')
    check(hashlib.sha256(f.read_bytes()).hexdigest()==item.get('sha256'),f'{sid}: file SHA mismatch: {item["path"]}')
   if s.get('access_status')=='downloaded':check('original'in roles or 'image'in roles,f'{sid}: downloaded without original bytes')
   if s.get('read_scope')=='fulltext':check({'original','readable'}<=roles,f'{sid}: fulltext requires original and readable; semantic extent still needs review')
   if not files:warnings.append(f'{sid}: lead only, no saved source bytes')
  seen=set()
  for c in cs:
   cid=c.get('claim_id');check(bool(cid)and cid not in seen,'missing/duplicate claim_id');seen.add(cid)
   for k in ['module','statement','object','limitations']:check(bool(c.get(k)),f'{cid}: missing {k}')
   kind=c.get('kind');check(kind in ['source_statement','ai_analysis','lead'],f'{cid}: kind invalid')
   evs=c.get('evidence',[]);check(isinstance(evs,list),f'{cid}: evidence must be list')
   if kind=='source_statement':check(bool(evs),f'{cid}: source_statement has no evidence')
   for e in evs:
    sid=e.get('source_id');check(sid in sources,f'{cid}: unknown source_id')
    if sid not in sources:continue
    source=sources[sid];check(source.get('read_scope')not in ['metadata','unread','ocr_unchecked'],f'{cid}: cannot substantiate claim from unread/unchecked material')
    files=source.get('files',[]);check(any(f.get('path')==e.get('readable_path')and f.get('role')=='readable'for f in files),f'{cid}: readable file not declared in source')
    text=resource(e.get('readable_path')).read_text(encoding='utf-8');quote=e.get('quote')
    check(isinstance(quote,str)and bool(quote)and quote in text,f'{cid}: quote not verbatim in readable file');check(bool(e.get('locator')),f'{cid}: locator missing')
  for q in qs:
   for k in ['query','site_or_engine','searched_at','outcome']:check(bool(q.get(k)),'query log missing '+k)
   check(q.get('outcome')in ['found','no_result','blocked','failed'],'query outcome invalid; planned is not executed')
   check(isinstance(q.get('source_ids',[]),list)and all(sid in sources for sid in q.get('source_ids',[])),'query references unknown source')
  if not cs:warnings.append('no claims submitted; discovery-only batch')
  counts={'sources':len(ss),'claims':len(cs),'queries':len(qs),'referenced_files':total_files}
 except (ValueError,KeyError,TypeError,OSError,AttributeError)as exc:errors.append(str(exc));counts={}
 return dict(status='mechanical_pass_pending_content_review'if not errors else 'needs_correction',errors=errors,warnings=warnings,counts=counts,semantic_review=False,official_ingestion=False,score_assigned=False)
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);sub=ap.add_subparsers(dest='action',required=True)
 a=sub.add_parser('init');a.add_argument('project_id');a.add_argument('batch_id');a.add_argument('--agent',required=True);a.add_argument('--topic',required=True)
 a=sub.add_parser('validate');a.add_argument('batch_dir',type=Path)
 args=ap.parse_args()
 try:r=init(args.project_id,args.batch_id,args.agent,args.topic)if args.action=='init'else validate(args.batch_dir)
 except (ValueError,OSError)as e:r={'status':'needs_correction','errors':[str(e)]}
 print(json.dumps(r,ensure_ascii=False,indent=2));sys.exit(1 if r['status']=='needs_correction'else 0)
