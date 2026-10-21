# coding: utf-8
"""044k archive an exact official catalogue row without importing other projects."""
import json,tempfile
from pathlib import Path
import project_pipeline as pp,project_ownership as own

def digest(row):return pp.sha(json.dumps(row,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
def parent_row(p,source_id,row_id):
 s=pp.state(p);parent=s['sources'].get(source_id)
 if not parent or pp.sha(pp.safe(p,parent['original']).read_bytes())!=parent['sha256']:raise ValueError('目录父件身份不符')
 data=pp.load(pp.safe(p,parent['original']));rows=data.get('data',{}).get('rows',[])
 if data.get('status')is not True or not isinstance(rows,list):raise ValueError('目录响应无有效行列表')
 matches=[r for r in rows if isinstance(r,dict)and r.get('id')==row_id]
 if len(matches)!=1:raise ValueError('目录行不存在或身份不唯一')
 return parent,matches[0]

def create(lib,pid,parent_id,row_id,actor):
 if not isinstance(actor,str)or not actor.strip():raise ValueError('须记录选录人')
 with pp.lock(lib):
  p=pp.project(lib,pid);s=pp.state(p);reg=own.registry(p);parent,row=parent_row(p,parent_id,row_id);scope=own.assignment(p,parent_id,s['sources'],reg)['scope']
  if scope not in ('project','shared'):raise ValueError('父目录不在允许研究范围')
  if row.get('opusName')!=s['project']['name']or type(row.get('matchYear'))is not int or row['matchYear']!=s['project']['year']:raise ValueError('目录行与当前项目名称或年份不符')
  origin=dict(kind='project_json_row',parent_source_id=parent_id,parent_source_sha256=parent['sha256'],parent_pointer='data.rows',row_id=row_id,row_sha256=digest(row),parent_asset_scope=scope,url=parent.get('origin',{}).get('url'),selected_by=actor)
  (p/'衍生').mkdir(parents=True,exist_ok=True)
  with tempfile.TemporaryDirectory(prefix='json-row-',dir=p/'衍生')as temp:
   path=Path(temp)/'官方目录项目条目.json';pp.save(path,row);result=pp.ingest(p,path,origin)
  child=result['source_id'];old=reg['assignments'].get(child);assignment=dict(scope='project',owner_project=pid,relation='official_catalog_exact_row_pending_fact_review',reason='严格匹配当前项目名称、matchYear与唯一条目id；仅本项目原行，不代表正式完成人名单')
  if old and old!=assignment:raise ValueError('单行原件已存在其他归属，禁止覆盖')
  if not old:reg['assignments'][child]=assignment;reg['version']+=1;pp.save(p/'资料归属.json',reg)
  # Byte-idempotent repeated ingestion must not silently replace provenance.
  stored=pp.state(p)['sources'][child]['origin']
  if stored!=origin:raise ValueError('单行原件已有不同溯源，禁止覆盖')
  return dict(**result,parent_source_id=parent_id,row_id=row_id)

def validate(p,x):
 o=x.get('origin',{})
 if o.get('kind')!='project_json_row'or o.get('parent_pointer')!='data.rows':raise ValueError('单行目录溯源无效')
 parent,row=parent_row(p,o['parent_source_id'],o['row_id'])
 if parent['sha256']!=o['parent_source_sha256']or digest(row)!=o['row_sha256']:raise ValueError('单行目录父件或行哈希不符')
 if pp.sha(pp.safe(p,x['original']).read_bytes())!=x['sha256']:raise ValueError('单行原件指纹不符')
 if pp.load(pp.safe(p,x['original']))!=row:raise ValueError('单行内容不是父目录原行')
 return row
