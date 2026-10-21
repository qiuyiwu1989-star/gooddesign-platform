# coding: utf-8
"""044i exact contiguous source excerpts; classification is not fact approval."""
import re,tempfile
from pathlib import Path
import project_pipeline as pp
from project_ownership import assignment,registry

def create(lib,pid,sid,chunk_id,text,title,reason,actor):
 if not all(isinstance(x,str)and x.strip()for x in (sid,chunk_id,text,title,reason,actor))or len(title)>200:raise ValueError('选录参数不完整')
 with pp.lock(lib):
  p=pp.project(lib,pid);s=pp.state(p);x=s['sources'].get(sid)
  if not x:raise ValueError('父来源不存在')
  reg=registry(p);scope=assignment(p,sid,s['sources'],reg)['scope']
  if scope not in ('project','shared'):raise ValueError('待定或其他项目资料不能直接选录')
  if pp.sha(pp.safe(p,x['original']).read_bytes())!=x['sha256']:raise ValueError('父原件指纹不符')
  chunks=pp.safe(p,x['chunks']);block=next((b for b in pp.load(chunks)if b['id']==chunk_id),None)
  if not block or text not in block['text']:raise ValueError('选录必须是同一块中未经改写的连续原文')
  if x.get('origin',{}).get('kind')=='project_source_excerpt'and text not in selected_text(p,x):raise ValueError('再次选录仍只能取父件原文，不得选编者说明')
  if block['text'].count(text)!=1:raise ValueError('选录位置不唯一，请扩大范围')
  provenance=dict(kind='project_source_excerpt',parent_source_id=sid,parent_source_sha256=x['sha256'],parent_chunks_path=x['chunks'],parent_chunks_sha256=pp.sha(chunks.read_bytes()),parent_chunk_id=chunk_id,parent_locator=block['locator'],selection_start=block['text'].index(text),selection_end=block['text'].index(text)+len(text),selection_sha256=pp.sha(text.encode()),scope_reason=reason,selected_by=actor,parent_asset_scope=scope,url=x.get('origin',{}).get('url')or x.get('origin',{}).get('requested_url'))
  content='# '+title+'\n\n项目限定原文选录 · 非全文\n父来源：'+sid+'\n父原件SHA256：'+x['sha256']+'\n原文位置：'+block['locator']+'\n用途：'+reason+'\n\n以下仅为连续原文，相关事实仍须提炼审核：\n\n'+text+'\n'
  # No timestamp in identity: repeating a selection is byte-stable.
  (p/'衍生').mkdir(parents=True,exist_ok=True)
  with tempfile.TemporaryDirectory(prefix='excerpt-',dir=p/'衍生')as tmp:
   f=Path(tmp)/(re.sub(r'[/\\\x00-\x1f]','_',title[:60])+'.txt');f.write_text(content,encoding='utf-8');result=pp.ingest(p,f,provenance)
  child=result['source_id'];reg=registry(p);prior=reg['assignments'].get(child)
  own=dict(scope='project',relation='exact_source_excerpt_pending_fact_review',owner_project=pid,reason=reason)
  if prior and prior!=own:raise ValueError('选录已有其他归属，禁止覆盖')
  if not prior:
   reg['assignments'][child]=own;reg['version']+=1;pp.save(p/'资料归属.json',reg)
  proof=p/'衍生/项目选录'/child/'provenance.json'
  if proof.exists()and pp.load(proof)!=provenance:raise ValueError('已有选录溯源不能覆盖')
  pp.save(proof,provenance)
  return dict(**result,parent_source_id=sid,parent_scope=scope,scope='project',expert_reviewed=False,original_unchanged=True)

def selected_text(p,x):
 """Validate the parent chain, returning only quoted source text, never editorial context."""
 o=x.get('origin',{})
 if o.get('kind')!='project_source_excerpt':raise ValueError('不是项目限定选录')
 parent=pp.state(p)['sources'].get(o['parent_source_id'])
 if not parent or parent['sha256']!=o['parent_source_sha256']or pp.sha(pp.safe(p,parent['original']).read_bytes())!=o['parent_source_sha256']:raise ValueError('选录父原件身份不符')
 chunks=pp.safe(p,o['parent_chunks_path'])
 if pp.sha(chunks.read_bytes())!=o['parent_chunks_sha256']:raise ValueError('选录父证据块指纹不符')
 b=next((b for b in pp.load(chunks)if b['id']==o['parent_chunk_id']),None);start=o['selection_start'];end=o['selection_end']
 if not b or type(start)is not int or type(end)is not int or not 0<=start<end<=len(b['text']):raise ValueError('选录父位置无效')
 text=b['text'][start:end]
 if pp.sha(text.encode())!=o['selection_sha256']:raise ValueError('选录范围指纹不符')
 return text
