from pathlib import Path
import json,hashlib,shutil,runpy,copy
P=Path(__file__).resolve().parent;R=P.parents[1];SRC=R/'修订版';C=P/'隔离副本';C.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files=[]
for name in ['MD-001-R48-v0.1.1','MD-002-R08-v0.1.1']:
 s=SRC/name;t=C/name
 shutil.copytree(s,t,dirs_exist_ok=True,ignore=shutil.ignore_patterns('private-sources','__pycache__'))
 m=json.loads((s/'manifest.json').read_text())
 for f in m['files']:
  assert sha(s/f['path'])==f['sha256'];files.append({'package':name,'path':f['path'],'verified':True})
a=runpy.run_path(str(C/'MD-001-R48-v0.1.1/构建教学包.py'));validate=a['validate_r08'];base=[a['EV'],a['RAW'],a['CODING']];args=[a['SHARED_EXPECT'],a['SP'],a['RP'],a['CP']];checks=[]
def probe(n,i,mut,expected):
 ds=copy.deepcopy(base)
 if mut:mut(ds[i])
 try:r=validate(*ds,*args);state='accepted'
 except(ValueError,KeyError,TypeError)as e:r=str(e);state='rejected'
 checks.append({'name':n,'expected':expected,'actual':state,'expected_matched':state==expected,'result':r})
probe('positive',0,None,'accepted')
probe('replay-crossproblem',0,lambda d:d['source_binding'].update(problem_id='OTHER'),'rejected')
probe('replay-version',0,lambda d:d['source_binding'].update(version='9'),'rejected')
probe('replay-retired-ID-deleted',0,lambda d:d.update(hypotheses=[h for h in d['hypotheses']if h['id']!='H-T01']),'rejected')
probe('unseen-package-missing',0,lambda d:d.pop('package_version'),'rejected')
probe('unseen-counter-duplicated',0,lambda d:d['hypotheses'][0]['counter_note_ids'].append(d['hypotheses'][0]['counter_note_ids'][0]),'rejected')
probe('unseen-withdrawal-wider-scope',0,lambda d:d['hypotheses'][0].update(scope='all_real_world_cases'),'rejected')
probe('unseen-hypothesis-proposition',0,lambda d:d['hypotheses'][0].update(proposition='暂停必然导致残留'),'rejected')
probe('unseen-coding-event-drift',2,lambda d:d['coding'][0].update(event_id='EV-OTHER'),'rejected')
probe('unseen-raw-real-participant',1,lambda d:d.update(real_participants=1),'rejected')
# R48 check requires explicit states and exact source body; these do not write the reviewed package.
for n,mut in [('unknowns-delete',lambda d:d.update(unknowns=[])),('need-delete',lambda d:d.update(source_needs=[])),('actor-delete',lambda d:d.update(actors=[])),('direction-promote',lambda d:d['candidates'][0].update(direction='le')),('retired-extra',lambda d:d['retired_hypotheses'].append('GHOST'))]:
 d=copy.deepcopy(a['draft']);mut(d)
 try:r=a['check'](d);state='accepted'
 except(ValueError,KeyError,TypeError)as e:r=str(e);state='rejected'
 checks.append({'name':n,'expected':'rejected','actual':state,'expected_matched':state=='rejected','result':r})
(P/'实际复核结果.json').write_text(json.dumps({'source_manifest_sha256':{n:sha(SRC/n/'manifest.json')for n in ['MD-001-R48-v0.1.1','MD-002-R08-v0.1.1']},'manifest_files':files,'probes':checks,'scope':'independent agent fixed closure review, not domain expert certification'},ensure_ascii=False,indent=2)+'\n')
assert all(x['expected_matched']for x in checks)
print(len(files),'hashes',len(checks),'probes matched')
