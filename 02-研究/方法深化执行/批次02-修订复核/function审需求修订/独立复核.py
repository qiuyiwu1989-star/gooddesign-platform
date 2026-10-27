from pathlib import Path
import copy,shutil,runpy,hashlib,json,contextlib,io
P=Path(__file__).resolve().parent;R=P.parents[1];V=R/'修订版';C=P/'隔离副本';C.mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();mods={};manifests=[]
s=C/'MD-001-R48-v0.1.1/教学包';s.mkdir(parents=True,exist_ok=True);shutil.copyfile(V/'MD-001-R48-v0.1.1/教学包/00-共享教学输入-v0.1.0.json',s/'00-共享教学输入-v0.1.0.json')
for n in ['MD-008-R02','MD-009-R03','MD-010-R09']:
 a=V/(n+'-v0.1.1');b=C/(n+'-v0.1.1');shutil.copytree(a,b,dirs_exist_ok=True,ignore=shutil.ignore_patterns('private-sources','__pycache__'))
 m=json.loads((a/'manifest.json').read_text())
 for f in m['files']:assert sha(a/f['path'])==f['sha256']
 manifests.append({'package':n,'manifest_sha256':sha(a/'manifest.json'),'files':len(m['files'])})
 with contextlib.redirect_stdout(io.StringIO()):mods[n]=runpy.run_path(str(b/'构建教学包.py'))
rows=[]
def test(n,label,mut,expected='rejected'):
 a=mods[n];key='brief'if n.endswith('R02')else'plan'if n.endswith('R03')else'base';fn='examine'if n.endswith('R02')else'check';d=copy.deepcopy(a[key]);mut(d)
 try:r=a[fn](d);state='accepted'
 except(ValueError,KeyError,TypeError)as e:r=str(e);state='rejected'
 rows.append({'method':n,'probe':label,'expected':expected,'actual':state,'matched':state==expected,'result':r})
for label,mut in [('old-bool-total',lambda d:d.update(totals=[True],segments=None)),('old-bool-phase',lambda d:d.update(totals=[1],segments=[{'normal':True,'recovery':0}])),('new-nan-total',lambda d:d.update(totals=[float('nan')])),('new-negative-phase',lambda d:d.update(segments=[{'normal':-1,'recovery':101}])),('new-synthetic-unit-as-seconds',lambda d:d.update(unit='s'))]:test('MD-008-R02',label,mut)
for label,mut in [('old-missing-observations',lambda d:d.pop('observations')),('old-missing-results',lambda d:d.pop('results')),('old-observations-empty-string',lambda d:d.update(observations='')),('new-result-dict',lambda d:d.update(results={})),('new-two-variable-change',lambda d:d['variants'][1].update(shape='other'))]:test('MD-009-R03',label,mut)
for label,mut in [('old-missing-actor',lambda d:d['raw']['stories'][0].pop('actor_id')),('old-blank-actor',lambda d:d['raw']['stories'][0].update(actor_id=' ')),('old-bool-actor',lambda d:d['raw']['stories'][0].update(actor_id=True)),('new-actor-container',lambda d:d['raw']['stories'][0].update(actor_id={})),('new-role-mismatch',lambda d:d['coding'][0].update(job_actor_role='ACT-OP'))]:test('MD-010-R09',label,mut)
test('MD-008-R02','known-independent-missing-customer-flag',lambda d:d.pop('customer_approved'),'accepted')
assert all(r['matched']for r in rows)
(P/'实际复核.json').write_text(json.dumps({'manifests':manifests,'baseline_checks':{k:len(v['cases'])for k,v in mods.items()},'probes':rows,'scope':'fixed helper input/state guards; not semantic or field validity'},ensure_ascii=False,indent=2)+'\n')
print(len(rows),'independent probes')
