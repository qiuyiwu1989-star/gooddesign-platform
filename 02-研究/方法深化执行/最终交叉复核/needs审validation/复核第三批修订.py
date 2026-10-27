# -*- coding: utf-8 -*-
from pathlib import Path
import json,hashlib,copy,shutil,runpy,contextlib,io
D=Path(__file__).resolve().parent;B=D.parents[1];V=B/'修订版';names=['MD-026-R28-v0.1.1','MD-028-R18-v0.1.1'];S=D/'sandbox第三批/02-研究/方法深化执行/修订版';S.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
before={str(p):sha(p)for n in names for p in(V/n).rglob('*')if p.is_file()}
for n in names:shutil.copytree(V/n,S/n,dirs_exist_ok=True)
shutil.copytree(B/'MD-001-R48',S.parent/'MD-001-R48',dirs_exist_ok=True)
f=io.StringIO()
with contextlib.redirect_stdout(f):m=runpy.run_path(str(S/names[0]/'教学与反例.py'))
probes=[('R28-old-version-drift','R28',lambda x:x.update(version='99')),('R18-old-three-empty','R18',lambda x:x.update(test_plan=['','',''])),('R18-whitespace','R18',lambda x:x.update(test_plan=[' ','\t','\n'])),('R18-nonstr','R18',lambda x:x.update(test_plan=[1,2,3])),('R18-three-duplicate-nonempty','R18',lambda x:x.update(test_plan=['x','x','x'])),('R28-source-version-change','R28',lambda x:x.update(source_version='ARIZ-other')),('R28-no-full-claim','R28',lambda x:x['implemented_scope'].append('full_ARIZ')),('R18-invent-gain','R18',lambda x:x.update(engineering_gain=.5)),('R18-context-version','R18',lambda x:x['context'].update(problem_version='99'))]
rows=[]
for n,r,mut in probes:
 base,fn=m['FIX'][r];q=copy.deepcopy(base);mut(q)
 try:o=fn(q);state='accepted'
 except Exception as e:o={'error':str(e)};state='rejected'
 rows.append({'name':n,'input':q,'actual':state,'output':o})
assert all(sha(Path(p))==h for p,h in before.items());man=[]
for n in names:
 d=V/n;x=json.loads((d/'manifest.json').read_text());assert all(sha(d/i['path'])==i['sha256']for i in x['files']);man.append({'task':n,'manifest_sha256':sha(d/'manifest.json'),'entries_checked':len(x['files'])})
(D/'第三批修订实际复核.json').write_text(json.dumps({'original_files_unchanged':len(before),'manifests':man,'replayed':f.getvalue(),'probes':rows},ensure_ascii=False,indent=2,allow_nan=False));print([(r['name'],r['actual'])for r in rows]);print(man)
