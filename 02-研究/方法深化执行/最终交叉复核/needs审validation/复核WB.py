# -*- coding: utf-8 -*-
from pathlib import Path
import json,hashlib,copy,shutil,runpy,contextlib,io
D=Path(__file__).resolve().parent;B=D.parents[1];names=['MD-060-WB08','MD-061-WB09','MD-062-WB10','MD-063-WB11','MD-064-WB12']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
before={str(p):sha(p)for n in names for p in(B/n).rglob('*')if p.is_file()};S=D/'sandboxWB';S.mkdir(exist_ok=True)
for n in names:shutil.copytree(B/n,S/n,dirs_exist_ok=True)
f=io.StringIO()
with contextlib.redirect_stdout(f):m=runpy.run_path(str(S/names[0]/'教学与反例.py'))
probes=[('WB08-hide-travel-change','WB08',lambda x:x.update(change_reason='')),('WB08-task-claim','WB08',lambda x:x.update(dynamic_or_safety_claim=True)),('WB09-bool-mass','WB09',lambda x:x['parameters'].update(m=True)),('WB09-global-claim','WB09',lambda x:x.update(global_stability_claim=True)),('WB10-bool-data','WB10',lambda x:x['data'][0].__setitem__(0,True)),('WB10-hard-as-soft','WB10',lambda x:x.update(hard_status=['pass']*3)),('WB11-domain-activate','WB11',lambda x:x['rules'][2].update(executable=True)),('WB11-fact-invented','WB11',lambda x:x.update(facts={'measurement_evidence_missing':False})),('WB12-fake-alias','WB12',lambda x:x.update(auto_same_as=[['THREEA-2006','FIVEA-2019']])),('WB12-unknown-to-seven','WB12',lambda x:x.update(author_seven_category_table=['A']*7))]
rows=[]
for name,r,mut in probes:
 q=copy.deepcopy(m['BASES'][r]);mut(q)
 try:o=m['check'](r,q);state='accepted'
 except Exception as e:o={'error':str(e)};state='rejected'
 rows.append({'name':name,'input':q,'actual':state,'output':o})
assert all(sha(Path(p))==h for p,h in before.items());(D/'.gitignore').write_text('sandbox*/\n');(D/'WB实际复核.json').write_text(json.dumps({'original_files_unchanged':len(before),'manifests':{n:sha(B/n/'manifest.json')for n in names},'replayed':f.getvalue(),'probes':rows},ensure_ascii=False,indent=2));print([(r['name'],r['actual'])for r in rows])
