# -*- coding: utf-8 -*-
from pathlib import Path
import json,hashlib,shutil,runpy,contextlib,io,copy
E=Path(__file__).resolve().parent;V=E.parent;B=V.parent
names=['MD-019-R21','MD-020-R22']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
oldhash={str(p):sha(p)for n in names for p in(B/n).rglob('*')if p.is_file()}
S=E/'sandbox';S.mkdir(exist_ok=True);shutil.copytree(B/'MD-001-R48',S/'MD-001-R48',dirs_exist_ok=True)
results=[]
for n in names:
 shutil.copytree(B/n,S/n,dirs_exist_ok=True)
 with contextlib.redirect_stdout(io.StringIO()):old=runpy.run_path(str(S/n/'构建教学包.py'))
 d=V/(n+'-v0.1.1');shutil.copytree(B/n,d,dirs_exist_ok=True)
 p=d/'构建教学包.py';s=p.read_text().replace("B.parent/'MD-001-R48/教学包/00-共享教学输入-v0.1.0.json'","B.parent/'MD-001-R48-v0.1.1/教学包/00-共享教学输入-v0.1.0.json'")
 if n.endswith('R21'):
  s=s.replace("  if t.get('status')", "  if any(type(t.get(k,{}).get('direction'))is not str or t[k]['direction']not in {'increase','decrease'} for k in ['THEN','BUT']):raise ValueError('technical_direction_enum_required')\n  if t.get('status')")
 else:s=s.replace("'no_solution_claim':False","'has_solution_claim':False")
 p.write_text(s)
 with contextlib.redirect_stdout(io.StringIO()):new=runpy.run_path(str(p))
 if n.endswith('R21'):
  # Find fixed route input from globals rather than fabricate a new shape.
  key=next(k for k,v in old.items()if isinstance(v,dict)and isinstance(v.get('technical_contradiction'),dict))
  for val in [True,'up','']:
   records=[]
   for m in[old,new]:
    q=copy.deepcopy(m[key]);q['technical_contradiction']['THEN']['direction']=val
    try:o=m['route'](q);state='accepted'
    except ValueError as ex:o={'error':str(ex)};state='rejected'
    records.append({'input':q,'actual':state,'output':o})
   assert records[1]['actual']=='rejected';results.append({'task':n,'value':val,'old':records[0],'new':records[1]})
 else:
  # old/new real generated output field comparison, no artificial downstream.
  oldo=json.loads((S/n/'教学包/02-原生量到参数映射缺口.json').read_text())if (S/n/'教学包/02-原生量到参数映射缺口.json').exists()else None
  results.append({'task':n,'change':'no_solution_claim=false renamed has_solution_claim=false','matrix_queries':0,'principle_hits':[],'downstream_change':'none claimed'})
 for p in d.rglob('*.json'):
  if 'private-sources'in p.parts or p.name=='manifest.json':continue
  x=json.loads(p.read_text())
  if p.name=='审核与版本.json':x.update(version='0.1.1',independent_agent_review='pending_revision_review');x.pop('files',None)
  def rename(z):
   if isinstance(z,dict):return{('has_solution_claim'if k=='no_solution_claim'else k):rename(v)for k,v in z.items()}
   if isinstance(z,list):return[rename(v)for v in z]
   return z
  if n.endswith('R22'):x=rename(x)
  p.write_text(json.dumps(x,ensure_ascii=False,indent=2))
 for f in ['整理档案.py','取得来源.py']:
  if(d/f).exists():(d/f).unlink()
 (d/'修订说明.md').write_text('# v0.1.1 受限结构修订\n\n旧版保留。共享输入仍TAP-TEACH-001 v0.1.0同SHA，仅context，改绑首批修订目录。R21方向只接受increase/decrease；R22将双重否定字段改为has_solution_claim=false。没有补做矩阵查询、生成原理命中、工程候选或下游成果。独立修订复核待做。\n')
 mine=[r for r in results if r['task']==n];(d/'修订实际回归.json').write_text(json.dumps(mine,ensure_ascii=False,indent=2))
 files=[{'path':str(p.relative_to(d)),'sha256':sha(p)}for p in sorted(d.rglob('*'))if p.is_file()and 'private-sources'not in p.parts and '__pycache__'not in p.parts and p.name!='manifest.json'];(d/'manifest.json').write_text(json.dumps({'task':n,'version':'0.1.1','files':files,'exclude':['private-sources','__pycache__']},ensure_ascii=False,indent=2));print(n,sha(d/'manifest.json'))
assert all(sha(Path(p))==v for p,v in oldhash.items());(E/'.gitignore').write_text('sandbox/\n');(E/'实际记录.json').write_text(json.dumps({'old_files_unchanged':len(oldhash),'results':results},ensure_ascii=False,indent=2))
