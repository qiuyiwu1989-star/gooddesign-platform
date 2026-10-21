# coding: utf-8
"""044e immutable AI reading guides bound to one research dataset, never fact cells."""
import json,re,os,tempfile
from pathlib import Path
import project_pipeline as pp
import research_workflow as rw
SCHEMA='research-reader-notes-1.0'
def markdown(payload):
 lines=['# 项目阅读导读','',f"AI整理 · {payload['version']} · 绑定 {payload['research_revision']}",'','本文件是阅读辅助，不是新增事实、工程结论或专家评分。','',payload['overview'],'']
 for m in payload['modules']:
  lines.extend([f"## {m['module_id']:02d} {pp.MODULES[m['module_id']-1]}",'',m['summary'],'','待补充：',''])
  lines.extend('- '+g for g in m['gaps']);lines.extend(['','记录索引：'+('、'.join(m['record_ids'])or'当前没有已入档的独立事实记录。'),''])
 return '\n'.join(lines)
def folder(p,revision):
 if not re.fullmatch(r'research-\d{6}',revision):raise ValueError('研究版本无效')
 return rw.workspace(p)/'阅读导读'/revision
def validate(p,payload):
 if not isinstance(payload,dict)or payload.get('schema')!=SCHEMA or payload.get('project_id')!=p.name or payload.get('content_nature')!='ai_reading_guide':raise ValueError('导读身份或性质无效')
 version=payload.get('version','')
 if not re.fullmatch(r'\d{1,3}\.\d{1,3}\.\d{1,3}',version):raise ValueError('导读版本无效')
 revision=payload.get('research_revision','');vf,_=rw.check_version(p,revision);data=pp.load(vf/'档案.json')
 if payload.get('dataset_sha256')!=pp.sha((vf/'档案.json').read_bytes()):raise ValueError('导读与研究档案版本不符')
 def text(s,limit):
  if not isinstance(s,str)or not s.strip()or len(s)>limit:raise ValueError('导读文字为空或过长')
 text(payload.get('overview'),280)
 modules=payload.get('modules',[])
 if not isinstance(modules,list)or len(modules)!=8 or not all(isinstance(m,dict)and type(m.get('module_id'))is int for m in modules)or [m.get('module_id')for m in modules]!=list(range(1,9)):raise ValueError('导读必须按顺序包含八模块')
 ids={x['id']for x in data['records']}
 from steward_dossier_ui import MODULE_ENTITIES
 for m in modules:
  text(m.get('summary'),280);refs=m.get('record_ids',[]);gaps=m.get('gaps',[])
  if not isinstance(refs,list)or len(refs)>8 or not all(isinstance(r,str)for r in refs)or len(refs)!=len(set(refs))or set(refs)-ids:raise ValueError('导读记录引用无效')
  allowed={x['id']for x in data['records']if x['entity']in MODULE_ENTITIES[m['module_id']-1]}
  if set(refs)-allowed:raise ValueError('导读引用跨越模块')
  if not isinstance(gaps,list)or not 1<=len(gaps)<=4:raise ValueError('每模块须明确1至4项待补内容')
  for gap in gaps:text(gap,180)
 return payload
def freeze(lib,pid,payload,actor):
 with pp.lock(lib):
  p=pp.project(lib,pid);validate(p,payload);dest=folder(p,payload['research_revision'])/payload['version']
  if dest.exists():
   existing=read(p,payload['research_revision'],payload['version'])
   if existing['notes']!=payload:raise ValueError('导读版本已存在，禁止覆盖')
   return existing
  dest.parent.mkdir(parents=True,exist_ok=True)
  with tempfile.TemporaryDirectory(prefix='.building-',dir=dest.parent)as temp:
   stage=Path(temp)
   pp.save(stage/'导读.json',payload)
   (stage/'导读.md').write_text(markdown(payload),encoding='utf-8')
   pp.save(stage/'manifest.json',dict(schema=SCHEMA,sha256=pp.sha((stage/'导读.json').read_bytes()),markdown_sha256=pp.sha((stage/'导读.md').read_bytes()),actor=actor,created_at=pp.now(),content_nature='ai_reading_guide',expert_reviewed=False,quality_score_changed=False))
   os.replace(stage,dest)
 return read(p,payload['research_revision'],payload['version'])
def read(p,revision,version=None):
 base=folder(p,revision)
 if not base.exists():return dict(status='not_available',notes=None)
 versions=[x.name for x in base.iterdir()if x.is_dir()and re.fullmatch(r'\d{1,3}\.\d{1,3}\.\d{1,3}',x.name)]
 if not versions:return dict(status='not_available',notes=None)
 if version is None:version=max(versions,key=lambda v:tuple(map(int,v.split('.'))))
 if version not in versions:raise ValueError('导读版本不存在')
 dest=base/version;manifest=pp.load(dest/'manifest.json');path=dest/'导读.json'
 if manifest.get('sha256')!=pp.sha(path.read_bytes()):raise ValueError('导读指纹不符')
 if manifest.get('markdown_sha256')and manifest['markdown_sha256']!=pp.sha((dest/'导读.md').read_bytes()):raise ValueError('导读文档指纹不符')
 notes=validate(p,pp.load(path))
 if notes['version']!=version or notes['research_revision']!=revision:raise ValueError('导读路径与声明不符')
 return dict(status='available',notes=notes,manifest=manifest)
def safe_read(p,revision):
 try:return read(p,revision)
 except (ValueError,KeyError,TypeError,OSError,json.JSONDecodeError):return dict(status='invalid',notes=None)
