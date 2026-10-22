# coding: utf-8
"""047: inventory old material bytes, then explicitly map selected originals.
No content execution, automatic project assignment, ZIP extraction or fact claims.
"""
import argparse, hashlib, json, os, re, shutil, stat, struct, tempfile, zipfile
from collections import defaultdict
from pathlib import Path, PurePosixPath
import project_pipeline as pp
import project_ownership as own

VERSION='legacy-materials-1.0'
ROOTS=('01-原始资料','99-历史项目快照')
EXCLUDE={'项目投递箱','node_modules','.git','.runtime','.venv','venv','__pycache__','output','dist','build','.build','.cache','.pytest_cache','.mypy_cache','.playwright-cli','coverage','.next','产物','导出件'}
CODE={'.py','.js','.ts','.tsx','.jsx','.css','.scss','.sh','.command','.html','.htm','.json','.map','.vue','.svelte'}
MAX_FILE=512*1024*1024

def stable_digest(value):return pp.sha(json.dumps(value,ensure_ascii=False,sort_keys=True,allow_nan=False).encode())
def hash_file(path,max_bytes=MAX_FILE):
 if path.is_symlink():raise ValueError('不读取符号链接')
 if not stat.S_ISREG(path.lstat().st_mode):raise ValueError('仅登记普通文件')
 fd=os.open(path,os.O_RDONLY|getattr(os,'O_NOFOLLOW',0)|getattr(os,'O_NONBLOCK',0));digest=hashlib.sha256()
 with os.fdopen(fd,'rb')as stream:
  before=os.fstat(stream.fileno())
  if not stat.S_ISREG(before.st_mode)or before.st_size>max_bytes:raise ValueError('不是普通文件或超过登记大小上限')
  for block in iter(lambda:stream.read(1024*1024),b''):digest.update(block)
  after=os.fstat(stream.fileno())
  final=path.lstat()
  if (before.st_ino,before.st_dev,before.st_mtime_ns,before.st_size)!=(after.st_ino,after.st_dev,after.st_mtime_ns,after.st_size)or(final.st_ino,final.st_dev,final.st_mtime_ns,final.st_size)!=(before.st_ino,before.st_dev,before.st_mtime_ns,before.st_size):raise ValueError('文件在登记时发生变化')
 return digest.hexdigest()

def zip_inventory(path,max_entries=3000,max_central_bytes=8*1024*1024,max_unpacked=512*1024*1024,max_ratio=100):
 """Only inspect bounded central-directory metadata, never decompress members."""
 size=path.stat().st_size
 with path.open('rb')as stream:
  stream.seek(max(0,size-65557));tail=stream.read(65557)
 index=tail.rfind(b'PK\x05\x06')
 if index<0 or len(tail)-index<22:return dict(status='invalid',reason='未找到标准ZIP中央目录尾标记',entries=[])
 values=struct.unpack('<4s4H2LH',tail[index:index+22]);_,disk,cd_disk,count_disk,count,cd_size,cd_offset,comment=values
 if len(tail)-index!=22+comment:return dict(status='invalid',reason='ZIP尾标记长度不一致',entries=[])
 if disk or cd_disk or count_disk!=count:return dict(status='manual_review',reason='多卷ZIP不自动处理',entries=[])
 if count==65535 or cd_size==0xffffffff or cd_offset==0xffffffff:return dict(status='manual_review',reason='ZIP64需单独审核，不自动载入中央目录',entries=[])
 if count>max_entries or cd_size>max_central_bytes or cd_offset+cd_size>size:return dict(status='blocked_limits',reason='中央目录数量、大小或边界超限',entry_count=count,entries=[])
 entries=[];issues=[];total=0;seen=set()
 try:
  with zipfile.ZipFile(path)as archive:
   infos=archive.infolist()
   if len(infos)!=count:raise ValueError('ZIP实际中央目录条目数不一致')
   for info in infos:
    name=info.filename;normalized=name.replace('\\','/');parts=PurePosixPath(normalized).parts;flags=[]
    if normalized.startswith('/')or re.match(r'^[A-Za-z]:',normalized)or '..'in parts or '\x00'in name:flags.append('unsafe_path')
    if stat.S_ISLNK(info.external_attr>>16):flags.append('symlink')
    if info.flag_bits&1:flags.append('encrypted')
    if normalized.casefold()in seen:flags.append('duplicate_normalized_name')
    seen.add(normalized.casefold());total+=info.file_size
    if info.file_size>64*1024*1024 or(info.file_size and(info.compress_size==0 or info.file_size/info.compress_size>max_ratio)):flags.append('expansion_limit')
    if set(parts)&EXCLUDE:flags.append('excluded_directory')
    if Path(name).suffix.lower()in ('.zip','.tar','.gz','.7z','.rar'):flags.append('nested_archive_not_opened')
    if flags:issues.append(dict(name=name,flags=flags))
    entries.append(dict(name=name,bytes=info.file_size,compressed_bytes=info.compress_size,crc32='%08x'%info.CRC,compression=info.compress_type,flags=flags))
 except (OSError,ValueError,zipfile.BadZipFile,NotImplementedError)as exc:return dict(status='invalid',reason=type(exc).__name__+': '+str(exc),entries=[])
 if total>max_unpacked:issues.append(dict(name=None,flags=['total_expansion_limit']))
 return dict(status='metadata_only',entry_count=len(entries),declared_unpacked_bytes=total,issues=issues,entries=entries,extracted=False,content_trust='untrusted_unread')

def scan(root=pp.ROOT,registry_dir=None,max_files=30000,max_file_bytes=MAX_FILE,max_total_bytes=2*1024*1024*1024):
 root=Path(root).resolve();registry_dir=Path(registry_dir)if registry_dir else root/'04-知识库/历史素材登记'
 if not 1<=max_files<=100000 or not 1<=max_file_bytes<=MAX_FILE or not 1<=max_total_bytes<=8*1024*1024*1024:raise ValueError('扫描预算超限')
 entries=[];skipped=[];total=0;visited_files=0;visited_dirs=0
 def walk_error(error):
  path=Path(error.filename)
  skipped.append(dict(path=path.relative_to(root).as_posix()if path.is_relative_to(root)else str(path),reason=type(error).__name__))
 for folder in ROOTS:
  base=root/folder
  if not base.exists():skipped.append(dict(path=folder,reason='root_missing'));continue
  if base.is_symlink():skipped.append(dict(path=folder,reason='symlink'));continue
  for current,dirs,files in os.walk(base,followlinks=False,onerror=walk_error):
   visited_dirs+=1
   if visited_dirs>max_files:raise ValueError('扫描目录数超过上限，未写入不完整登记')
   current=Path(current);kept=[]
   for name in sorted(dirs):
    child=current/name
    if name in EXCLUDE or child.is_symlink():skipped.append(dict(path=child.relative_to(root).as_posix(),reason='excluded_directory'if name in EXCLUDE else'symlink'))
    else:kept.append(name)
   dirs[:]=kept
   for name in sorted(files):
    visited_files+=1
    if visited_files>max_files:raise ValueError('扫描文件数超过上限，未写入不完整登记，请缩小素材范围')
    path=current/name;relative=path.relative_to(root).as_posix()
    if path.is_symlink()or name in ('.DS_Store','.git'):skipped.append(dict(path=relative,reason='symlink_or_system_metadata'));continue
    try:
     before=path.stat();size=before.st_size
     if size>max_file_bytes or total+size>max_total_bytes:skipped.append(dict(path=relative,reason='byte_budget',bytes=size));continue
     digest=hash_file(path,max_file_bytes);total+=size
     item=dict(relative_path=relative,sha256=digest,extension=path.suffix.lower(),bytes=size,scope='platform_reference'if folder=='99-历史项目快照'else'unassigned',project_id=None,material_kind='historical_code_or_generated_page'if path.suffix.lower()in CODE else'original_material_unreviewed',read_status='unread',fact_status='not_research_evidence')
     if path.suffix.lower()=='.zip':item['zip']=zip_inventory(path)
     after=path.stat()
     if (before.st_ino,before.st_dev,before.st_mtime_ns,before.st_size)!=(after.st_ino,after.st_dev,after.st_mtime_ns,after.st_size):raise ValueError('登记期间文件改变')
     entries.append(item)
    except (OSError,ValueError)as exc:skipped.append(dict(path=relative,reason=type(exc).__name__+': '+str(exc)))
 groups=defaultdict(list)
 for item in entries:groups[item['sha256']].append(item['relative_path'])
 duplicates={sha:paths for sha,paths in groups.items()if len(paths)>1}
 body=dict(version=VERSION,roots=list(ROOTS),policy=dict(excluded_directories=sorted(EXCLUDE),max_files=max_files,max_file_bytes=max_file_bytes,max_total_bytes=max_total_bytes,zip_extraction=False,automatic_project_assignment=False),entries=entries,duplicates=duplicates,skipped=skipped,total_hashed_bytes=total)
 identity=stable_digest(body);body['registry_id']=identity;target=registry_dir/'snapshots'/('registry-'+identity+'.json')
 if target.exists():
  if pp.load(target)!=body:raise ValueError('登记快照身份冲突')
 else:pp.save(target,body)
 pp.save(registry_dir/'最新登记.json',body)
 return dict(registry_path=str(target),registry_id=identity,files=len(entries),duplicate_groups=len(duplicates),skipped=len(skipped),total_hashed_bytes=total)

def plan_imports(registry,mapping,lib=pp.LIB,root=pp.ROOT):
 root=Path(root).resolve();lib=Path(lib);data=pp.load(Path(registry))if not isinstance(registry,dict)else registry
 if data.get('version')!=VERSION or stable_digest({k:v for k,v in data.items()if k!='registry_id'})!=data.get('registry_id'):raise ValueError('素材注册表指纹无效')
 mapping=pp.load(Path(mapping))if not isinstance(mapping,dict)else mapping
 if mapping.get('version')!='legacy-map-1'or not isinstance(mapping.get('items'),list):raise ValueError('需要显式legacy-map-1映射清单')
 if len(mapping['items'])>50:raise ValueError('每批最多显式映射50份原件，请分批处理')
 by_path={x['relative_path']:x for x in data['entries']};selected=[];seen=set()
 for entry in mapping['items']:
  relative=entry.get('relative_path');item=by_path.get(relative)
  if not item or relative in seen:raise ValueError('映射路径不在登记中或重复')
  parts=PurePosixPath(relative).parts
  if not parts or parts[0]not in ROOTS or '..'in parts or set(parts)&EXCLUDE:raise ValueError('映射路径不在许可的旧素材范围')
  seen.add(relative)
  if entry.get('scope')not in ('project','shared')or not entry.get('reason')or not entry.get('mapped_by'):raise ValueError('映射须明确项目/共享范围、复核人及归属依据')
  p=pp.project(lib,entry.get('project_id',''));path=pp.safe(root,relative)
  if path.is_symlink()or not path.is_file()or hash_file(path)!=item['sha256']or entry.get('expected_sha256')!=item['sha256']:raise ValueError('素材已改变、链接或映射SHA不匹配')
  if item['bytes']>pp.MAX_BYTES:raise ValueError('选定原件超过现有管线30MB上限，不能自动导入')
  if item['extension']=='.zip':raise ValueError('ZIP仅登记中央目录，不导入为项目文本，也不自动解压')
  sid='S'+item['sha256'][:16];sources=pp.state(p)['sources'];existing=sources.get(sid)
  if existing and existing['sha256']!=item['sha256']:raise ValueError('来源ID冲突')
  related=[source for source in sources.values()if source['sha256']==item['sha256']]
  if related:sid=related[-1]['id'];existing=related[-1]
  if existing and own.assignment(p,sid,sources)['scope']!=entry['scope']:raise ValueError('已有来源范围与映射冲突，需单独治理，不能因重复导入改变范围')
  assigned=own.registry(p).get('assignments',{}).get(sid)
  if assigned and(assigned['scope']!=entry['scope']or assigned.get('owner_project',p.name)!=p.name):raise ValueError('已有明确归属与映射冲突，需单独治理，不能覆盖')
  selected.append(dict(relative_path=relative,project_id=p.name,scope=entry['scope'],reason=str(entry['reason']),mapped_by=str(entry['mapped_by']),sha256=item['sha256'],source_id=sid,material_kind=item['material_kind'],existing=bool(existing)))
 return dict(version=VERSION,registry_id=data['registry_id'],plan_id=stable_digest(selected),items=selected,apply=False,read_status='unread',originals_moved=False)

def apply_imports(registry,mapping,lib=pp.LIB,root=pp.ROOT,registry_dir=None):
 root=Path(root).resolve();lib=Path(lib);registry_dir=Path(registry_dir)if registry_dir else root/'04-知识库/历史素材登记'
 with pp.lock(lib):
  plan=plan_imports(registry,mapping,lib,root);results=[]
  for item in plan['items']:
   p=pp.project(lib,item['project_id']);path=pp.safe(root,item['relative_path']);record=dict(item,at=pp.now())
   try:
    # Reserve explicit ownership before ingest so a shared original is never briefly project-scoped.
    reg=own.registry(p)
    if item['source_id']not in reg['assignments']:
     reg['version']=reg.get('version',0)+1;reg['assignments'][item['source_id']]=dict(scope=item['scope'],owner_project=p.name,relation='explicit_legacy_mapping_unreviewed_content',reason=item['reason'],mapped_by=item['mapped_by'],registry_id=plan['registry_id']);pp.save(p/'资料归属.json',reg)
    staging=registry_dir/'导入暂存';staging.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=staging)as folder:
     staged=Path(folder)/path.name;shutil.copyfile(path,staged)
     if hash_file(staged)!=item['sha256']:raise ValueError('导入暂存与已复核素材指纹不同，未导入')
     result=pp.ingest(p,staged,dict(kind='legacy_original_import',relative_path=item['relative_path'],original_sha256=item['sha256'],registry_id=plan['registry_id'],mapping_plan_id=plan['plan_id'],material_kind=item['material_kind'],mapped_by=item['mapped_by'],reason=item['reason'],content_review='unreviewed_original_not_verified_claim'))
    record.update(status=result['status'],result=result)
   except Exception as exc:record.update(status='failed',error=type(exc).__name__+': '+str(exc))
   registry_dir.mkdir(parents=True,exist_ok=True)
   with (registry_dir/'导入日志.jsonl').open('a',encoding='utf-8')as log:log.write(json.dumps(record,ensure_ascii=False)+'\n')
   results.append(record)
 return dict(plan_id=plan['plan_id'],apply=True,results=results,originals_moved=False,read_status='unread')

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',type=Path,default=pp.ROOT);parser.add_argument('--registry-dir',type=Path);parser.add_argument('--library',type=Path,default=pp.LIB);parser.add_argument('--registry',type=Path);parser.add_argument('--mapping',type=Path);parser.add_argument('--apply',action='store_true');args=parser.parse_args()
 if args.apply and not(args.registry and args.mapping):parser.error('--apply需要--registry和--mapping')
 if args.mapping:
  if not args.registry:parser.error('--mapping需要--registry')
  out=apply_imports(args.registry,args.mapping,args.library,args.root,args.registry_dir)if args.apply else plan_imports(args.registry,args.mapping,args.library,args.root)
 else:out=scan(args.root,args.registry_dir)
 print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
