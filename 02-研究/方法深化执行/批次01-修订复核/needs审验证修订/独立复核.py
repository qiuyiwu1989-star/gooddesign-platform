# -*- coding: utf-8 -*-
from pathlib import Path
import copy,hashlib,json,runpy,shutil,contextlib,io
ROOT=Path(__file__).resolve().parents[4];H=Path(__file__).resolve().parent;S=ROOT/'02-研究/方法深化执行/修订版'
TASKS=['MD-005-R36-v0.1.1','MD-006-R44-v0.1.1','MD-007-R42-v0.1.1'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def snap():return {str(p.relative_to(ROOT)):sha(p)for t in TASKS for p in (S/t).rglob('*')if p.is_file()}
before=snap();man=[]
for t in TASKS:
 j=json.loads((S/t/'manifest.json').read_text())
 for r in j['files']:assert sha(S/t/r['path'])==r['sha256']
 man.append({'task':t,'manifest_sha256':sha(S/t/'manifest.json'),'entries':len(j['files'])})
u=json.loads((S/TASKS[0]/'上游冻结绑定.json').read_text());up=[]
for key,v in u.items():
 if isinstance(v,dict)and 'path'in v and'sha256'in v:
  p=ROOT/v['path'];assert sha(p)==v['sha256'],key;up.append({'key':key,'path':v['path'],'sha256':v['sha256']})
D=H/'sandbox/02-研究/方法深化执行/修订版';D.mkdir(parents=True,exist_ok=True)
for t in ['MD-001-R48-v0.1.1','MD-002-R08-v0.1.1','MD-003-R14-v0.1.1','MD-004-R17-v0.1.1']+TASKS:shutil.copytree(S/t,D/t,dirs_exist_ok=True)
buf=io.StringIO()
with contextlib.redirect_stdout(buf):n=runpy.run_path(str(D/TASKS[0]/'生成与检查.py'))
probes=[]
def probe(name,base,fn,mut):
 x=copy.deepcopy(n[base]);mut(x)
 try:o=n[fn](x);a='accepted'
 except Exception as e:o={'error':type(e).__name__+': '+str(e)};a='rejected'
 (H/(name+'-input.json')).write_text(json.dumps(x,ensure_ascii=False,indent=2));probes.append({'name':name,'actual':a,'output':o})
probe('OLD01-criterion-drift','main','check_r36',lambda x:x['criteria'][0].update(need='N-T04',target=9,unit='s',direction='higher'))
probe('OLD02-hard-state-empty','main','check_r36',lambda x:x.update(hard_status={}))
probe('OLD03-capability-disguise','r44input','check_r44',lambda x:(x['hypotheses'][0].update(prototype_id='P-PAPER'),x['capability_needed'].update({'H-R44-01':'state_comprehension'})))
probe('OLD04-pair-swap','r42input','check_r42',lambda x:(x['items'][0].update(source_requirement_candidate='RQ-T02'),x['items'][1].update(source_requirement_candidate='RQ-T01')))
probe('OLD05-candidate-states-empty','main','check_r36',lambda x:x.update(candidate_states={}))
probe('NEW01-duplicate-hypothesis','r44input','check_r44',lambda x:x['hypotheses'].append(x['hypotheses'][0]))
probe('NEW02-duplicate-coverage-item','r42input','check_r42',lambda x:x['items'].append(x['items'][0]))
probe('NEW03-reference-path-metadata-drift','r44input','check_r44',lambda x:x['source_r36'].update(path='unrelated-package.json'))
probe('CONTROL01-actual-trial-invented','r44input','check_r44',lambda x:x.update(participant_count=3))
assert before==snap()
(H/'被审指纹.json').write_text(json.dumps(before,ensure_ascii=False,indent=2));(H/'复核实际结果.json').write_text(json.dumps({'scope':'independent Agent bounded review, not expert certification','original_files_unchanged':len(before),'manifests':man,'upstream_artifact_hashes_checked':up,'original_replayed':len(n['checks']),'stdout':buf.getvalue(),'probes':probes},ensure_ascii=False,indent=2));(H/'.gitignore').write_text('sandbox/\n__pycache__/\n')
print(json.dumps({'original_replayed':len(n['checks']),'unchanged':len(before),'probes':[(p['name'],p['actual'])for p in probes]},ensure_ascii=False))
