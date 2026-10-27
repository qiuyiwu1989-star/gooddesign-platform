# -*- coding: utf-8 -*-
from pathlib import Path
import hashlib,json,shutil,runpy,copy,contextlib,io
D=Path(__file__).resolve().parent;ROOT=D.parents[3];BASE=ROOT/'02-研究/方法深化执行'
names=['MD-026-R28','MD-027-R29','MD-028-R18','MD-029-R49']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def snap():return {str(p.relative_to(ROOT)):sha(p) for n in names for p in (BASE/n).rglob('*') if p.is_file()}
before=snap();S=D/'sandbox/02-研究/方法深化执行';S.mkdir(parents=True,exist_ok=True)
for n in names+['MD-001-R48']:shutil.copytree(BASE/n,S/n,dirs_exist_ok=True)
f=io.StringIO()
with contextlib.redirect_stdout(f):m=runpy.run_path(str(S/names[0]/'教学与反例.py'))
rows=[]
probes=[('ARIZ-version-drift','R28',lambda x:x.update(version='99.0')),('ARIZ-unknown-selected','R28',lambda x:x.update(selected_conflict=99)),('TESE-erase-specific-counterevidence','R29',lambda x:x.update(counterevidence='irrelevant')),('BIO-three-empty-controls','R18',lambda x:x.update(test_plan=['','',''])),('BIO-cross-problem','R18',lambda x:x['context'].update(problem_version='99')),('FBS-fake-measurement','R49',lambda x:x.update(actual_measurement=20)),('FBS-unknown-to-zero','R49',lambda x:x['Be'].update(target=0))]
for name,rid,mut in probes:
 original,fn=m['FIX'][rid];q=copy.deepcopy(original);mut(q)
 try:out=fn(q);state='accepted'
 except Exception as e:out={'error':type(e).__name__+': '+str(e)};state='rejected'
 rows.append({'name':name,'method':rid,'actual':state,'input':q,'output':out})
assert before==snap()
(D/'.gitignore').write_text('sandbox/\n')
(D/'复核实际结果.json').write_text(json.dumps({'unchanged_files':len(before),'replayed_stdout':f.getvalue(),'probes':rows},ensure_ascii=False,indent=2))
print(json.dumps({'unchanged':len(before),'replayed':f.getvalue(),'probes':[(r['name'],r['actual']) for r in rows]}))
