# coding: utf-8
"""044h ownership-filtered immutable research snapshot, including frozen evidence."""
import argparse,json,os,shutil,tempfile,zipfile,uuid
from datetime import datetime,timezone
from pathlib import Path
import project_pipeline as pp,research_workflow as rw,research_reader_notes as rn
from project_ownership import select,registry,assignment
from research_handoff_check import check,evidence_nodes,safe,sha
ROOT=Path(__file__).resolve().parents[1]

def build(lib,pid,out,revision=None):
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 with pp.lock(lib):
  p=pp.project(lib,pid);state=pp.load(p/'数据/管道状态.json');revision=revision or 'research-%06d'%rw.current(p)['revision'];vf,publication=rw.check_version(p,revision);data=pp.load(vf/'档案.json')
  reg=registry(p);active=select(p,state['sources'],reg=reg);notes=rn.read(p,revision)
  missing={e['source_id']for e in evidence_nodes(data)}-set(active)
  if missing:raise ValueError('已发布引用不属于当前项目，须先处理归属或研究版本: '+','.join(sorted(missing)))
  name=pid+'-'+revision+'-'+datetime.now().strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:6];dest=out/name
  with tempfile.TemporaryDirectory(prefix='.building-',dir=out)as tmp:
   stage=Path(tmp)
   def copy(src,rel):
    target=safe(stage,rel);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,target)
   for f in vf.iterdir():
    if f.is_file():copy(f,'研究版本/'+f.name)
   if int(revision.split('-')[1])>1:
    prev=p/'研究工作区/版本'/('research-%06d'%(int(revision.split('-')[1])-1))/'manifest.json';copy(prev,'历史对照/前序manifest.json')
   rows=[]
   for sid,x in sorted(active.items()):
    row={k:x[k]for k in ('id','title','sha256','bytes','original','document','chunks','status','read_scope','review_status','parser_version')if k in x};row['ownership']=assignment(p,sid,state['sources'],reg)
    origin=x.get('origin',{});row['origin']={k:origin[k]for k in ('kind','url','requested_url','parent_source_id','page','canonical_source_id','parent_source_sha256','parent_chunks_path','parent_chunks_sha256','parent_chunk_id','parent_locator','selection_start','selection_end','selection_sha256','scope_reason','selected_by','parent_asset_scope')if k in origin}
    if origin.get('kind')=='project_source_excerpt':
     from source_excerpt import selected_text
     row['origin']['selection_text']=selected_text(p,x)
     row['origin']['parent_delivery']='metadata_only_when_shared'
    for key in ('original','document','chunks'):copy(pp.safe(p,x[key]),'资料库/'+x[key])
    if sha(safe(stage,'资料库/'+x['original']))!=x['sha256']:raise ValueError('来源原件指纹变化')
    if x.get('ocr'):copy(pp.safe(p,x['ocr']['path']),'资料库/'+x['ocr']['path'])
    rows.append(row)
   for e in evidence_nodes(data):
    rel=e['chunks_path'];src=pp.safe(p,rel)
    if pp.sha(src.read_bytes())!=e['chunks_sha256']:raise ValueError('冻结证据已变化: '+rel)
    copy(src,'资料库/'+rel)
   pp.save(stage/'资料库/来源目录.json',dict(project_id=pid,ownership_revision=reg['version'],scope='current_project_owned_assets',ingest_revision=state['revision'],items=rows))
   guide_version=None
   if notes['status']=='available':
    guide_version=notes['notes']['version'];nf=rn.folder(p,revision)/guide_version
    for f in nf.iterdir():
     if f.is_file():copy(f,'阅读导读/'+f.name)
   copy(rw.SCHEMA,'标准/原子字段字典.json');copy(ROOT/'scripts/research_handoff_check.py','check.py');copy(ROOT/'scripts/research_handoff_read.py','read.py')
   cells=[c for r in data['records']for c in r['cells'].values()]
   info=dict(project_id=pid,research_revision=revision,guide_version=guide_version,created_at=datetime.now(timezone.utc).isoformat(),history_scope='single_snapshot_not_full_chain',records=len(data['records']),known_cells=sum(c.get('value_state')=='known'for c in cells),ai_interpretations=len(data.get('interpretations',[])),source_files=len(rows),quality_score_status=data.get('quality_score_status','not_assessed'),expert_reviewed=data.get('expert_reviewed',False),notes=['资料数量和有值字段数量不是完整度或质量评分。','原件为私有研究留存，不代表获得公开再发布授权。','上一版manifest仅供身份对照，未交付完整历史数据链。','这是固定数据包，非运行中的MCP服务或通用创新引擎。'])
   pp.save(stage/'交付概览.json',info)
   (stage/'README.md').write_text(README,encoding='utf-8')
   pp.save(stage/'manifest.json',dict(schema='research-handoff-1.0',project_id=pid,revision=revision,files={str(f.relative_to(stage)):sha(f)for f in sorted(stage.rglob('*'))if f.is_file()}))
   result=check(stage);os.replace(stage,dest)
 with tempfile.NamedTemporaryFile(prefix='.zip-',dir=out,delete=False)as f:tempzip=Path(f.name)
 try:
  with zipfile.ZipFile(tempzip,'w',zipfile.ZIP_DEFLATED)as z:
   for f in sorted(dest.rglob('*')):
    if f.is_file():z.write(f,str(Path(dest.name)/f.relative_to(dest)))
  zip_path=dest.with_suffix('.zip');os.replace(tempzip,zip_path)
 except BaseException:
  tempzip.unlink(missing_ok=True);raise
 zip_path.with_suffix('.zip.sha256').write_text(sha(zip_path)+'  '+zip_path.name+'\n')
 return dict(folder=str(dest),zip=str(zip_path),check=result)
README='''# 项目研究档案 · 应用测试包

先读交付概览，再读阅读导读/导读.md（如有），按模块进入研究版本/01-项目档案.md。资料与AI解读、质量与缺口分别在研究版本/02-资料与解读.md和03-档案评估.md。结构化档案保留未知值、证据和审核身份。

## 逐层读取

在本文件所在目录运行（只需要Python 3标准库）：

    python3 check.py
    python3 read.py
    python3 read.py --record PROJECT
    python3 read.py --source 来源编号

read.py先校验包；默认返回概览和导读。按记录读取字段及证据，再按source读取来源目录和文本分块。原件路径在资料库/来源目录.json中，HTML原件须作为资料审阅，不能当应用脚本执行。AI解读不应回写成项目事实，目标应用适用性仍须验证。

## 版本与完整性

项目限定选录在来源目录保留父件页码、指纹和选录原文。shared父件不随项目包交付；只能在后台公共参考中查看完整父件，包内无法独立重验其完整字节。选录的标题、用途与编者说明不作为事实证据。

本包只含选定研究快照、该版导读、当前项目归属原件和冻结证据块。历史对照只含前序manifest，不能证明完整历史链。包内manifest检查意外损坏，不是数字签名，也不是可信来源认证；ZIP的SHA256在同名旁文件。不得把收集数、有值字段或自动证据检查等同于完整研究、专家审核、专利授权意见。

请记录应用问题、使用的记录ID/字段、缺失上下文、证据追溯情况、AI标签是否清楚和实际输出；不预填成功结果。原件为内部研究留存，公开发布需另行确认授权。
'''
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('project');ap.add_argument('--revision');ap.add_argument('--library',type=Path,default=ROOT/'04-知识库/项目库');ap.add_argument('--output',type=Path,default=ROOT/'output/handoff');a=ap.parse_args();print(json.dumps(build(a.library,a.project,a.output,a.revision),ensure_ascii=False,indent=2))
