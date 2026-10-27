from pathlib import Path
import json,copy,runpy,shutil,hashlib,re,contextlib,io
P=Path(__file__).resolve().parent;R=P.parents[1];C=P/'隔离副本';C.mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();sp=C/'修订版/MD-001-R48-v0.1.1/教学包';sp.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/'修订版/MD-001-R48-v0.1.1/教学包/00-共享教学输入-v0.1.0.json',sp/'00-共享教学输入-v0.1.0.json');mods={};ver=[]
for n,raw in [('MD-030-R30','MIT-AXIOM.html'),('MD-031-R31','DSM-INTRO.html'),('MD-032-R32','MIT-MECHANISMS.pdf')]:
 s=R/n;d=C/n;shutil.copytree(s,d,dirs_exist_ok=True,ignore=shutil.ignore_patterns('private-sources','__pycache__'));m=json.loads((s/'manifest.json').read_text());meta=json.loads((s/'来源与主张.json').read_text())
 for f in m['files']:assert sha(s/f['path'])==f['sha256']
 assert sha(s/'private-sources'/raw)==meta['source_raw_sha256']
 with contextlib.redirect_stdout(io.StringIO()):mods[n]=runpy.run_path(str(d/'教学计算.py'))
 ver.append({'package':n,'manifest_sha256':sha(s/'manifest.json'),'files':len(m['files']),'primary_raw_sha_verified':True,'baseline_checks':len(mods[n]['checks'])})
rows=[]
def probe(n,label,mut):
 a=mods[n];q=copy.deepcopy(a['base']);mut(q)
 try:r=a['examine'](q);state='accepted'
 except(ValueError,TypeError,KeyError)as e:r={'error':str(e)};state='rejected'
 if 'scan'in r:r={k:v for k,v in r.items()if k!='scan'}
 rows.append({'method':n,'probe':label,'actual':state,'result':r})
probe('MD-030-R30','new-workpoint-coordinate',lambda d:d['workpoint'].update(DP1_mm=1))
probe('MD-030-R30','new-target-bool',lambda d:d.update(delta_target=[True,4]))
probe('MD-030-R30','new-unit-drift',lambda d:d['DP'][1].update(unit='m'))
probe('MD-031-R31','new-unknown-edge-not-full-order',lambda d:d['matrix'][3].__setitem__(0,None))
probe('MD-031-R31','new-edge-direction-mismatch',lambda d:d['edge_evidence'][2].update(**{'from':2,'to':1}))
probe('MD-031-R31','new-evidence-bool-index',lambda d:d['edge_evidence'][1].update(**{'from':True}))
probe('MD-032-R32','new-nan-pose-angle',lambda d:d['poses'][0].update(input_deg=float('nan')))
probe('MD-032-R32','new-branch-switch-fractional',lambda d:d.update(switch_at_deg=90.5))
probe('MD-032-R32','new-subdegree-scan-not-certificate',lambda d:d.update(scan_step_deg=.5))
(P/'实际复核.json').write_text(json.dumps({'packages':ver,'probes':rows,'scope':'isolated fixed-model calculations and primary raw fingerprints; Agent review not engineering certificate'},ensure_ascii=False,indent=2,allow_nan=False)+'\n')
print(len(rows),'independent probes')
