# -*- coding: utf-8 -*-
from pathlib import Path
import json,hashlib,copy,shutil,runpy,contextlib,io,math
D=Path(__file__).resolve().parent;B=D.parents[1];V=B/'修订版';S=D/'sandbox修订/02-研究/方法深化执行/修订版';S.mkdir(parents=True,exist_ok=True)
names=['MD-036-R05-v0.1.1','MD-037-R47-v0.1.1','MD-006-R44-v0.1.2','MD-007-R42-v0.1.2'];deps=['MD-001-R48-v0.1.1','MD-002-R08-v0.1.1','MD-003-R14-v0.1.1','MD-004-R17-v0.1.1','MD-005-R36-v0.1.1']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
before={str(p):sha(p)for n in names for p in(V/n).rglob('*')if p.is_file()}
for n in names+deps:shutil.copytree(V/n,S/n,dirs_exist_ok=True)
replays=[];modules={}
for n,script in [('MD-036-R05-v0.1.1','教学与反例.py'),('MD-006-R44-v0.1.2','生成与检查.py')]:
 f=io.StringIO()
 with contextlib.redirect_stdout(f):modules[n]=runpy.run_path(str(S/n/script))
 replays.append({'entry':n,'stdout':f.getvalue()})
a=modules['MD-036-R05-v0.1.1'];b=modules['MD-006-R44-v0.1.2']
probes=[('old-bool-command',a,'base05','check05',lambda x:x['command'].update(software_value=True)),('old-NaN-command',a,'base05','check05',lambda x:x['command'].update(software_value=float('nan'))),('new-inf-command',a,'base05','check05',lambda x:x['command'].update(software_value=float('inf'))),('old-bool-grid',a,'base47','check47',lambda x:x['mass_grid'].__setitem__(0,True)),('old-duplicate-hypothesis',b,'r44input','check_r44',lambda x:x['hypotheses'].append(copy.deepcopy(x['hypotheses'][0]))),('old-r36-path-drift',b,'r44input','check_r44',lambda x:x['source_r36'].update(path='unrelated.json')),('old-duplicate-item',b,'r42input','check_r42',lambda x:x['items'].append(copy.deepcopy(x['items'][0]))),('new-duplicate-coverage-label',b,'r42input','check_r42',lambda x:x['coverage']['planned'].append(x['coverage']['planned'][0])),('new-r44-path-drift',b,'r42input','check_r42',lambda x:x['source_r44'].update(path='unrelated.json'))]
rows=[]
for n,m,key,fn,mut in probes:
 q=copy.deepcopy(m[key]);mut(q)
 try:o=m[fn](q);state='accepted'
 except Exception as e:o={'error':str(e)};state='rejected'
 rows.append({'name':n,'input':q,'actual':state,'output':o})
def clean(z):
 if type(z)is float and not math.isfinite(z):return {'native_python_nonfinite':str(z)}
 if isinstance(z,list):return[clean(v)for v in z]
 if isinstance(z,dict):return{k:clean(v)for k,v in z.items()}
 return z
assert all(sha(Path(p))==h for p,h in before.items());man=[]
for n in names:
 m=json.loads((V/n/'manifest.json').read_text());assert all(sha(V/n/f['path'])==f['sha256']for f in m['files']);man.append({'task':n,'sha256':sha(V/n/'manifest.json'),'entries':len(m['files'])})
(D/'修订实际复核.json').write_text(json.dumps(clean({'unchanged_files':len(before),'manifests':man,'replays':replays,'probes':rows}),ensure_ascii=False,indent=2,allow_nan=False));print([(r['name'],r['actual'])for r in rows])
