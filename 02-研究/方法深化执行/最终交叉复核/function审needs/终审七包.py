from pathlib import Path
import json,shutil,copy,runpy,hashlib,contextlib,io
P=Path(__file__).resolve().parent;R=P.parents[1];ROOT=R.parents[1];C=P/'隔离副本/好设计平台';RR=C/'02-研究/方法深化执行';RR.mkdir(parents=True,exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();results=[];mods={};prior=[]
for rel in ['output/method-reader-review/upgrades/R01-v0.2.1-proposal','output/method-reader-review/upgrades/R04-v0.2.1-proposal']:
 s=ROOT/rel;m=json.loads((s/'manifest.json').read_text())
 for f in m['files']:assert sha(s/f['path'])==f['sha256']
 for n in ['case.json','verification.json','manifest.json']:
  (C/rel).mkdir(parents=True,exist_ok=True);shutil.copyfile(s/n,C/rel/n)
 prior.append({'path':rel,'manifest_sha256':sha(s/'manifest.json'),'entries_verified':len(m['files']),'bound_sha256':{n:sha(s/n)for n in ['case.json','verification.json','manifest.json']}})
sp=RR/'修订版/MD-001-R48-v0.1.1/教学包';sp.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/'修订版/MD-001-R48-v0.1.1/教学包/00-共享教学输入-v0.1.0.json',sp/'00-共享教学输入-v0.1.0.json')
items=[('MD-050-R01','教学补充.py'),('MD-051-R04','教学补充.py'),('MD-052-R06','教学检查.py'),('MD-053-WB01','谱系教学.py'),('MD-054-WB02','调研教学.py'),('修订版/MD-019-R21-v0.1.1','构建教学包.py'),('修订版/MD-020-R22-v0.1.1','构建教学包.py')]
for rel,script in items:
 s=R/rel;t=RR/rel;shutil.copytree(s,t,dirs_exist_ok=True,ignore=shutil.ignore_patterns('private-sources','__pycache__'));m=json.loads((s/'manifest.json').read_text())
 for f in m['files']:assert sha(s/f['path'])==f['sha256']
 meta=json.loads((s/'来源与主张.json').read_text());hashes=meta.get('source_hashes',meta.get('source_fingerprints',[]))
 if 'sources'in meta:
  for x in meta['sources']:
   if 'raw_file'in x:assert sha(s/x['raw_file'])==x['raw_sha256']
 for h in hashes:
  assert any(sha(f)==h['sha256']for f in(s/'private-sources').glob(h['id']+'.*')if f.is_file()),h
 with contextlib.redirect_stdout(io.StringIO()):mods[rel]=runpy.run_path(str(t/script))
 a=mods[rel];results.append({'package':rel,'manifest_sha256':sha(s/'manifest.json'),'entries':len(m['files']),'original_fixed_checks':len(a.get('cases',a.get('checks',[]))),'source_originals_read_in_place_not_copied':True})
probes=[]
def probe(rel,label,mut):
 a=mods[rel];q=copy.deepcopy(a.get('base',a.get('data')));mut(q)
 try:r=a.get('check',a.get('route'))(q);state='returned'
 except Exception as e:r={'error':type(e).__name__+': '+str(e)};state='rejected'
 probes.append({'package':rel,'name':label,'actual':state,'output':r})
probe('MD-050-R01','new-prior-case-sha-drift',lambda q:q['prior_package']['sha256'].update(**{'case.json':'0'*64}))
probe('MD-050-R01','new-NaN-release-gap',lambda q:q['layouts'][0].update(gap_mm=float('nan')))
probe('MD-051-R04','new-drift-evidence-sensor',lambda q:q['evidence'].update(sensor='SENSOR-B'))
probe('MD-051-R04','new-architecture-dependent-rule',lambda q:q['architectures']['ARCH-B'].update(budget_ms=300))
probe('MD-052-R06','new-Go-still-no-resource-authorization',lambda q:q.update(hard_safety='pass_in_fixture',evidence_state='sufficient_in_fixture'))
probe('MD-052-R06','new-real-owner-appointment',lambda q:q['resource_proposal'].update(owner_role='actual_authorized_manager'))
probe('MD-053-WB01','new-unread-year-confirmation',lambda q:q['nodes'][1].update(year=2008,source='verified_book'))
probe('MD-053-WB01','new-third-party-efficacy',lambda q:q.update(efficacy_confirmed=True))
probe('MD-054-WB02','new-third-I-renaming',lambda q:q['known_chinese_roles'].__setitem__(2,'Innovation'))
probe('MD-054-WB02','new-priority-selected-with-no-evidence',lambda q:q.update(priority_rank=1))
probe('修订版/MD-019-R21-v0.1.1','old-direction-bool',lambda q:q.update(technical_contradiction={**mods['修订版/MD-019-R21-v0.1.1']['tc'],'THEN':{**mods['修订版/MD-019-R21-v0.1.1']['tc']['THEN'],'direction':True}}))
probe('修订版/MD-019-R21-v0.1.1','new-direction-string-nonsense',lambda q:q.update(technical_contradiction={**mods['修订版/MD-019-R21-v0.1.1']['tc'],'THEN':{**mods['修订版/MD-019-R21-v0.1.1']['tc']['THEN'],'direction':'banana'}}))
probe('修订版/MD-020-R22-v0.1.1','new-matrix-cell-without-lookup',lambda q:q['matrix'].update(cell='1,2'))
probe('修订版/MD-020-R22-v0.1.1','new-official-parameter-mapping-claim',lambda q:q['parameter_mapping'].update(official_parameter_ids=[1,2]))
(P/'七包实际终审.json').write_text(json.dumps({'packages':results,'prior055_full_manifest_verification':prior,'independent_probes':probes,'scope':'independent Agent fixed/provenance review, original raw sources read only in place'},ensure_ascii=False,indent=2,allow_nan=False)+'\n')
assert all(x['actual']=='rejected'for x in probes if x['name']!='new-Go-still-no-resource-authorization')
go=next(x['output']for x in probes if x['name']=='new-Go-still-no-resource-authorization');assert go['advisory_outcome']=='Go'and go['authorized_resource']is None and go['actual_gate_decision']is None
print(len(probes),'probes; prior055',sum(x['entries_verified']for x in prior),'entries')
