# -*- coding: utf-8 -*-
from pathlib import Path
import copy,json,shutil,hashlib,runpy,io,contextlib,math
E=Path(__file__).resolve().parent;V=E.parent;B=V.parent
TASKS=[('修订版/MD-002-R08-v0.1.1','MD-002-R08-v0.1.2','构建教学包.py','raw','check'),('MD-031-R31','MD-031-R31-v0.1.1','教学计算.py','base','examine'),('MD-032-R32','MD-032-R32-v0.1.1','教学计算.py','base','examine'),('MD-038-R37','MD-038-R37-v0.1.1','教学计算.py','base','check'),('MD-041-R40','MD-041-R40-v0.1.1','教学检查.py','base','check')]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
before={str(p):sha(p)for n,*_ in TASKS for p in(B/n).rglob('*')if p.is_file()};S=E/'sandbox';S.mkdir(exist_ok=True)
# All old execution is isolated while preserving each script's sibling context.
shutil.copytree(V/'MD-001-R48-v0.1.1',S/'修订版/MD-001-R48-v0.1.1',dirs_exist_ok=True)
oldmods={};newmods={}
for oldn,newn,script,key,fn in TASKS:
 olddir=B/oldn;tmp=S/oldn;shutil.copytree(olddir,tmp,dirs_exist_ok=True)
 with contextlib.redirect_stdout(io.StringIO()):oldmods[newn]=runpy.run_path(str(tmp/script))
 d=V/newn;assert not d.exists(),d;shutil.copytree(olddir,d);p=d/script;s=p.read_text()
 if 'R08'in newn:s=s.replace('def check(d):\n',"def check(d):\n if type(d.get('package_version'))is not str or d['package_version']!='0.1.1':raise ValueError('standalone_artifact_package_version_mismatch')\n")
 if 'R31'in newn:s=s.replace(" E={(r,c)"," if any(type(e.get(k))is not int or not 0<=e[k]<N for e in i['edge_evidence']for k in ['from','to']):raise ValueError('edge_endpoint_strict_integer_id_required')\n E={(r,c)")
 if 'R32'in newn:s=s.replace("if type(p.get('input_deg'))not in(int,float)or", "if type(p.get('input_deg'))not in(int,float)or not math.isfinite(p['input_deg'])or")
 if 'R37'in newn:
  s=s.replace(" if not i['additive_separability_assumption']", " if type(i.get('additive_separability_assumption'))is not bool:raise ValueError('additive_assumption_boolean_required')\n if not i['additive_separability_assumption']")
  s=s.replace(" scores=[]\n", " if not valid:return {'state':'no_candidate','excluded':excluded,'ranking':None,'customer_decision':None}\n scores=[]\n")
  start=s.index(" A=next(a for a in valid if a['id']=='A')");end=s.index("\n return {'state':'preference_sensitive'",start)
  s=s[:start]+" byid={a['id']:a['values']for a in valid};cross=None\n if 'A'in byid and 'B'in byid:\n  A=byid['A'];B=byid['B'];den=(A[0]-A[1])-(B[0]-B[1]);cross=(B[1]-A[1])/den if den else None"+s[end:]
  s=s.replace("return {'state':'preference_sensitive','excluded'", "return {'state':'remaining_feasible_only'if len(valid)==1 else'preference_sensitive','excluded'")
 if 'R40'in newn:
  s=s.replace("if len(ids)!=len(i['controls'])or", "if any(type(c.get('id'))is not str or not c['id'].strip()for c in i['controls']):raise ValueError('control_id_required')\n if len({a.get('id')for a in i['actions']})!=len(i['actions'])or any(type(a.get('id'))is not str or not a['id'].strip()or type(a.get('owner_role'))is not str or not a['owner_role'].strip()for a in i['actions']):raise ValueError('action_identity_or_owner_role_string_required')\n if len(ids)!=len(i['controls'])or")
 p.write_text(s)
 with contextlib.redirect_stdout(io.StringIO()):newmods[newn]=runpy.run_path(str(p))
probes={
'MD-002-R08-v0.1.2':[('wrong_artifact_version',lambda x:x.update(package_version='99')),('missing_artifact_version',lambda x:x.pop('package_version')),('bool_artifact_version',lambda x:x.update(package_version=True))],
'MD-031-R31-v0.1.1':[('bool_from',lambda x:x['edge_evidence'][1].update(**{'from':True})),('float_from',lambda x:x['edge_evidence'][1].update(**{'from':1.0}))],
'MD-032-R32-v0.1.1':[('nan_input_angle',lambda x:x['poses'][0].update(input_deg=float('nan'))),('inf_input_angle',lambda x:x['poses'][0].update(input_deg=float('inf')))],
'MD-038-R37-v0.1.1':[('string_false',lambda x:x.update(additive_separability_assumption='false')),('A_hard_fail',lambda x:x['alternatives'][0].update(hard_status='fail_within_fixture')),('all_hard_fail',lambda x:[a.update(hard_status='fail_within_fixture')for a in x['alternatives']])],
'MD-041-R40-v0.1.1':[('owner_bool',lambda x:x['actions'][0].update(owner_role=True)),('owner_blank',lambda x:x['actions'][0].update(owner_role=' ')),('duplicate_action_id',lambda x:x['actions'][1].update(id='A1'))]}
def clean(x):
 if type(x)is float and not math.isfinite(x):return {'native_python_nonfinite':str(x)}
 if isinstance(x,list):return[clean(v)for v in x]
 if isinstance(x,dict):return{k:clean(v)for k,v in x.items()}
 return x
for oldn,newn,script,key,fn in TASKS:
 rows=[]
 for label,mut in probes[newn]:
  states=[]
  for m in[oldmods[newn],newmods[newn]]:
   q=copy.deepcopy(m[key]);mut(q)
   try:o=m[fn](q);state='accepted'
   except Exception as ex:o={'error_type':type(ex).__name__,'error':str(ex)};state='rejected'if isinstance(ex,(ValueError,KeyError,TypeError))else'crashed'
   states.append({'actual':state,'input':q,'output':o})
  new=states[1];assert new['actual']=='rejected'or(new['actual']=='accepted'and new['output'].get('state')in['remaining_feasible_only','no_candidate']),(newn,label,new)
  rows.append({'name':label,'old':states[0],'new':new})
 d=V/newn
 (d/'修订实际回归.json').write_text(json.dumps(clean({'cases':rows,'scope':'strict structure/finite checks and safe feasible-set return; not semantic generalization'}),ensure_ascii=False,indent=2,allow_nan=False))
 allold=sorted(p.name for p in(B/oldn/'教学包').glob('*.json'));same={n:sha(B/oldn/'教学包'/n)==sha(d/'教学包'/n)for n in allold if(d/'教学包'/n).exists()}
 if 'R08'in newn:assert all(same.values()),same
 (d/'产物前后SHA对照.json').write_text(json.dumps({'original_teaching_artifacts_byte_identical':same,'old_chain_rebound':False,'R08_artifact_version':'0.1.1'if 'R08'in newn else None,'helper_package_version':'0.1.2'if 'R08'in newn else'0.1.1'},ensure_ascii=False,indent=2))
 (d/'修订说明.md').write_text('# 收口结构修订\n\n只增强严格类型/有限值/ID或可行集安全返回，原正常固定检查与迁移重放完成。旧包不改，未新增现场数据或通用语义能力。R08如适用：helper包v0.1.2验证仍为v0.1.1的冻结artifact，教学输入仍v0.1.0；产物逐字节SHA对照证明未变，旧依赖链不自动改绑。\n')
 for f in ['整理档案.py','取得来源.py']:
  if(d/f).exists():(d/f).unlink()
 meta=json.loads((d/'审核与版本.json').read_text());meta.pop('files',None);meta.update(version='0.1.2'if'R08'in newn else'0.1.1',status='pending_independent_revision_review',independent_Agent_review='pending',regression_cases=len(rows));(d/'审核与版本.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
 files=[{'path':str(p.relative_to(d)),'sha256':sha(p)}for p in sorted(d.rglob('*'))if p.is_file()and'private-sources'not in p.parts and'__pycache__'not in p.parts and p.name!='manifest.json'];(d/'manifest.json').write_text(json.dumps({'task':newn,'version':meta['version'],'exclude':['private-sources','__pycache__'],'files':files},ensure_ascii=False,indent=2));print(newn,sha(d/'manifest.json'),[(r['name'],r['old']['actual'],r['new']['actual'])for r in rows])
assert all(sha(Path(p))==h for p,h in before.items());(E/'.gitignore').write_text('sandbox/\n')
