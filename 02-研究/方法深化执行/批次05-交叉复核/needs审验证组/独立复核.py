# -*- coding: utf-8 -*-
from pathlib import Path
import json,hashlib,copy,shutil,runpy,contextlib,io
D=Path(__file__).resolve().parent;B=D.parents[1];names=['MD-046-R50','MD-047-R51','MD-048-R52','MD-049-R07']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
before={str(p):sha(p)for n in names for p in(B/n).rglob('*')if p.is_file()};S=D/'sandbox';S.mkdir(exist_ok=True)
for n in names:shutil.copytree(B/n,S/n,dirs_exist_ok=True)
f=io.StringIO()
with contextlib.redirect_stdout(f):m=runpy.run_path(str(S/names[0]/'教学与反例.py'))
probes=[('VOI-no-info','voi','check52',lambda x:x.update(signal_positive_likelihood=[.5,.5])),('VOI-impossible-signal','voi','check52',lambda x:x.update(signal_positive_likelihood=[0,0])),('VOI-invalid-prior','voi','check52',lambda x:x.update(prior=[1,1])),('VOI-bool-likelihood','voi','check52',lambda x:x.update(signal_positive_likelihood=[True,False])),('VOI-missing-prior-and-invalid-likelihood','voi','check52',lambda x:x.update(prior=None,signal_positive_likelihood=[2,-1])),('STPA-swap-context','stpa','check51',lambda x:x['ucas'][0].update(context='unrelated')),('STPA-delete-one-class','stpa','check51',lambda x:x['ucas'].pop()),('DFSS-fake-12readings','dfss','check07',lambda x:x['measurement_plan'].update(raw_observations=[0]*12)),('DFSS-repeat-bool','dfss','check07',lambda x:x['measurement_plan'].update(repeats=True)),('BLUE-zero-wait','blue','check50',lambda x:x['steps'][0].update(wait_s=0))]
rows=[]
for name,key,fn,mut in probes:
 q=copy.deepcopy(m[key]);mut(q)
 try:out=m[fn](q);actual='accepted'
 except Exception as e:out={'error':str(e)};actual='rejected'
 rows.append({'name':name,'input':q,'actual':actual,'output':out})
v=m['check52'](m['voi']);assert v['EVPI']==20 and abs(v['EVSI']-6)<1e-10 and abs(v['net_sample_value']-3)<1e-10
z=m['check07'](m['dfss']);assert len(z['planned_reading_cells'])==12 and all(t['value']is None for t in z['planned_reading_cells'])
assert all(sha(Path(p))==h for p,h in before.items());(D/'.gitignore').write_text('sandbox/\n');(D/'实际复核.json').write_text(json.dumps({'unchanged_files':len(before),'manifests':{n:sha(B/n/'manifest.json')for n in names},'replayed':f.getvalue(),'VOI_independent_algebra':{'current_risk':20,'expected_sample_risk':14,'EVSI':6,'EVPI':20,'net':3},'twelve_cells_all_null':True,'probes':rows},ensure_ascii=False,indent=2,allow_nan=False));print([(r['name'],r['actual'])for r in rows])
