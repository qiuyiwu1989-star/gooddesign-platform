# coding: utf-8
"""044b preserve HTML table cell boundaries in a new immutable source derivative."""
import argparse,shutil,tempfile
from pathlib import Path
import project_pipeline as pp
import research_workflow as rw
RECIPE='html-table-boundaries-1.0'
class TableText(pp.PageText):
 def handle_endtag(self,tag):
  if not self.skip and tag in ('td','th'):self.parts.append(' | ')
  super().handle_endtag(tag)
def reclean(lib,pid,sid):
 with pp.lock(lib):
  p=pp.project(lib,pid);x=rw.source(p,sid);raw=pp.safe(p,x['original'])
  if raw.suffix.lower()not in ('.html','.htm'):raise ValueError('此修订只处理HTML原件')
  if pp.sha(raw.read_bytes())!=x['sha256']:raise ValueError('原件指纹不符')
  parser=TableText();parser.feed(pp.decode(raw.read_bytes()));blocks=pp.chunks([('网页正文（保留表格单元格边界）',''.join(parser.parts))])
  if not blocks:raise ValueError('没有可读正文')
  folder=raw.parent/'清洗修订'/RECIPE
  newpath=(folder/'chunks.json').relative_to(p).as_posix()
  if folder.exists():
   manifest=pp.load(folder/'manifest.json')
   if manifest['source_sha256']!=x['sha256']or any(pp.sha((folder/name).read_bytes())!=digest for name,digest in manifest['files'].items()):raise ValueError('已有清洗修订指纹不符，禁止覆盖')
   if x['chunks']==newpath:return dict(status='no_changes',source_id=sid,recipe=RECIPE)
   if x['chunks']!=manifest['previous_chunks']or pp.sha(pp.safe(p,x['chunks']).read_bytes())!=manifest['previous_chunks_sha256']:raise ValueError('已有其他清洗修订，请显式选择，不自动回退')
   return adopt(lib,p,sid,folder,blocks,'恢复已保存的HTML清洗修订')
  folder.parent.mkdir(parents=True,exist_ok=True)
  temp=Path(tempfile.mkdtemp(prefix='.reclean-',dir=str(folder.parent)))
  try:
   pp.save(temp/'chunks.json',blocks)
   doc='# 表格边界清洗修订\n\n机器转换，非人工核读。单元格分隔符由清洗器添加；公式图片仍须读原件。\n\n'+''.join('## '+b['id']+' · '+b['locator']+'\n\n'+b['text']+'\n\n'for b in blocks)
   (temp/'可读来源.md').write_text(doc,encoding='utf-8')
   pp.save(temp/'manifest.json',dict(recipe=RECIPE,source_sha256=x['sha256'],previous_chunks=x['chunks'],previous_chunks_sha256=pp.sha(pp.safe(p,x['chunks']).read_bytes()),created_at=pp.now(),files={name:pp.sha((temp/name).read_bytes())for name in ['chunks.json','可读来源.md']}))
   temp.rename(folder)
  finally:
   if temp.exists():shutil.rmtree(temp)
  return adopt(lib,p,sid,folder,blocks,'新增HTML表格清洗修订，原件与旧证据块保留')
def adopt(lib,p,sid,folder,blocks,reason):
  newpath=(folder/'chunks.json').relative_to(p).as_posix();s=pp.state(p);current=s['sources'][sid];current.update(chunks=newpath,document=(folder/'可读来源.md').relative_to(p).as_posix(),chunk_count=len(blocks),chunks_sha256=pp.sha((folder/'chunks.json').read_bytes()),parser_version=RECIPE,read_scope='machine_table_boundaries_not_human_read',status='text_extracted')
  revision=pp.commit(p,s,reason)
  pp.save(pp.safe(p,current['original']).parent/'metadata.json',current)
  return dict(status='text_extracted',source_id=sid,recipe=RECIPE,revision=revision,chunks=len(blocks))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('project');ap.add_argument('source');a=ap.parse_args();import json;print(json.dumps(reclean(pp.LIB,a.project,a.source),ensure_ascii=False))
if __name__=='__main__':main()
