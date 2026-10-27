from pathlib import Path
import copy,shutil,runpy,hashlib,json,contextlib,io,statistics
import numpy as np
P=Path(__file__).resolve().parent;R=P.parents[1];C=P/'隔离副本';C.mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();mods={};verified=[]
for n,script in [('MD-038-R37','教学计算.py'),('MD-039-R38','教学复算.py'),('MD-040-R39','教学复算.py'),('MD-041-R40','教学检查.py')]:
 s=R/n;t=C/n;shutil.copytree(s,t,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'));m=json.loads((s/'manifest.json').read_text());meta=json.loads((s/'来源与主张.json').read_text())
 for f in m['files']:assert sha(s/f['path'])==f['sha256']
 fingerprints=meta.get('source_fingerprints',[])
 for f in fingerprints:
  candidates=list((s/'private-sources').glob(f['id']+'.*'));assert any(sha(q)==f['sha256']for q in candidates),f
 with contextlib.redirect_stdout(io.StringIO()):mods[n]=runpy.run_path(str(t/script))
 verified.append({'package':n,'manifest_sha256':sha(s/'manifest.json'),'files':len(m['files']),'baseline_checks':len(mods[n]['cases']),'primary_fingerprints':len(fingerprints)})
rows=[]
def probe(n,label,mut):
 a=mods[n];d=copy.deepcopy(a['base']);mut(d)
 try:r=a['check'](d);state='accepted'
 except Exception as e:r={'error':type(e).__name__+': '+str(e)};state='rejected'
 rows.append({'package':n,'probe':label,'actual':state,'output_summary':{k:v for k,v in r.items()if k not in['residuals','coefficients','rows']}})
probe('MD-038-R37','new-string-additive-false',lambda d:d.update(additive_separability_assumption='false'))
probe('MD-038-R37','new-A-hard-fail',lambda d:d['alternatives'][0].update(hard_status='fail_within_fixture'))
probe('MD-038-R37','new-nan-weight',lambda d:d.update(weight_first_range=[float('nan'),.8]))
probe('MD-039-R38','new-bool-model-order',lambda d:d.update(model_order=True))
probe('MD-039-R38','new-source-row-value-drift',lambda d:d['rows'][0].__setitem__(5,d['rows'][0][5]+1))
probe('MD-039-R38','new-saturated-variance-not-estimated',lambda d:d.update(model_order=5))
probe('MD-040-R39','new-field-distribution-invention',lambda d:d.update(field_noise_distribution=[.25]*4))
probe('MD-040-R39','new-laboratory-noise-as-control',lambda d:d.update(service_controllable_noise=True))
probe('MD-041-R40','new-scale-revision-drift',lambda d:d['scale_reference'].update(revision='2026'))
probe('MD-041-R40','new-action-owner-boolean',lambda d:d['actions'][0].update(owner_role=True))
probe('MD-041-R40','new-action-control-wrong',lambda d:d['actions'][0].update(control='NONE'))
# Independent closed-form checks, separate expressions from source scripts.
r38=mods['MD-039-R38'];a=np.array(r38['rows']);x=a[:,:5];y=a[:,5];cols=[np.ones(32)]+[np.prod(x[:,idx],axis=1)for k in (1,2,3)for idx in __import__('itertools').combinations(range(5),k)];X=np.array(cols).T;b=np.linalg.solve(X.T@X,X.T@y);rmse=float(np.sqrt(np.sum((y-X@b)**2)/6));assert abs(rmse-r38['out']['residual_rmse'])<1e-9
r39=mods['MD-040-R39'];sd=[statistics.stdev(row)for row in r39['VALUES']];assert min(range(8),key=lambda k:sd[k])+1==7
(P/'实际复核.json').write_text(json.dumps({'verified_packages':verified,'independent_probes':rows,'independent_recalculation':{'R38_normal_equations_rmse':rmse,'R39_min_sd_row':7,'R37_crossing_manual':.5},'scope':'Agent checks, not domain certification'},ensure_ascii=False,indent=2,allow_nan=False)+'\n')
print(len(rows),'probes;',rmse,'independent RMSE')
