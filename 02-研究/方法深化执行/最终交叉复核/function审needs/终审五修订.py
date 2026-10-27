from pathlib import Path
import json,shutil,copy,runpy,hashlib,contextlib,io
P=Path(__file__).resolve().parent;R=P.parents[1];C=P/'机械修订隔离';C.mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();mods={};records=[]
sp=C/'MD-001-R48-v0.1.1/教学包';sp.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/'修订版/MD-001-R48-v0.1.1/教学包/00-共享教学输入-v0.1.0.json',sp/'00-共享教学输入-v0.1.0.json')
for n,script in [('MD-002-R08-v0.1.2','构建教学包.py'),('MD-031-R31-v0.1.1','教学计算.py'),('MD-032-R32-v0.1.1','教学计算.py'),('MD-038-R37-v0.1.1','教学计算.py'),('MD-041-R40-v0.1.1','教学检查.py')]:
 s=R/'修订版'/n;t=C/n;shutil.copytree(s,t,dirs_exist_ok=True,ignore=shutil.ignore_patterns('private-sources','__pycache__'));m=json.loads((s/'manifest.json').read_text())
 for f in m['files']:assert sha(s/f['path'])==f['sha256']
 with contextlib.redirect_stdout(io.StringIO()):mods[n]=runpy.run_path(str(t/script))
 records.append({'package':n,'manifest_sha256':sha(s/'manifest.json'),'files_verified':len(m['files']),'baseline_count':len(mods[n].get('cases',mods[n].get('checks',[])))})
rows=[]
def probe(n,name,mut):
 a=mods[n];d=copy.deepcopy(a['raw']if'raw'in a else a['base']);mut(d)
 try:r=a.get('check',a.get('examine'))(d);state='returned'
 except Exception as e:r={'error':type(e).__name__+': '+str(e)};state='rejected'
 if 'scan'in r:r={k:v for k,v in r.items()if k!='scan'}
 rows.append({'package':n,'name':name,'actual':state,'result':r})
probe('MD-002-R08-v0.1.2','old-package-version-deletion',lambda d:d.pop('package_version'))
probe('MD-002-R08-v0.1.2','new-artifact-version-mixed-as-helper',lambda d:d.update(package_version='0.1.2'))
probe('MD-031-R31-v0.1.1','old-bool-edge',lambda d:d['edge_evidence'][1].update(**{'from':True}))
probe('MD-031-R31-v0.1.1','new-float-edge-index',lambda d:d['edge_evidence'][1].update(**{'from':1.0}))
probe('MD-032-R32-v0.1.1','old-NaN-input-angle',lambda d:d['poses'][0].update(input_deg=float('nan')))
probe('MD-032-R32-v0.1.1','new-inf-input-angle',lambda d:d['poses'][0].update(input_deg=float('inf')))
probe('MD-038-R37-v0.1.1','old-string-false',lambda d:d.update(additive_separability_assumption='false'))
probe('MD-038-R37-v0.1.1','old-A-fail-safe-return',lambda d:d['alternatives'][0].update(hard_status='fail_within_fixture'))
probe('MD-038-R37-v0.1.1','new-all-fail-safe-return',lambda d:[a.update(hard_status='fail_within_fixture')for a in d['alternatives']])
probe('MD-041-R40-v0.1.1','old-bool-owner',lambda d:d['actions'][0].update(owner_role=True))
probe('MD-041-R40-v0.1.1','new-owner-list',lambda d:d['actions'][0].update(owner_role=['control']))
kept=[]
for f in sorted((R/'修订版/MD-002-R08-v0.1.1/教学包').glob('0[1-5]-*.json')):
 same=sha(f)==sha(R/'修订版/MD-002-R08-v0.1.2/教学包'/f.name);assert same;kept.append({'file':f.name,'sha256':sha(f),'identical':same})
assert all(r['actual']=='rejected'for r in rows if r['name']not in['old-A-fail-safe-return','new-all-fail-safe-return'])
assert next(r['result']['state']for r in rows if r['name']=='old-A-fail-safe-return')=='remaining_feasible_only'
assert next(r['result']['state']for r in rows if r['name']=='new-all-fail-safe-return')=='no_candidate'
(P/'机械五修订实际终审.json').write_text(json.dumps({'packages':records,'probes':rows,'R08_artifacts_v011_unchanged':kept,'raw_originals':'not copied or modified','expert_certification':False},ensure_ascii=False,indent=2,allow_nan=False)+'\n');print(len(rows),'probes matched;',len(kept),'R08 artifacts unchanged')
