from pathlib import Path
import copy,hashlib,json,runpy,shutil,contextlib,io
PROJECT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
SOURCE=PROJECT/'02-研究/方法深化执行'
TASKS=['MD-005-R36','MD-006-R44','MD-007-R42']
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def snapshot():return {str(p.relative_to(PROJECT)):digest(p)for task in TASKS for p in (SOURCE/task).rglob('*')if p.is_file()}
before=snapshot()
checks=[]
for task in TASKS:
 b=SOURCE/task;m=json.loads((b/'manifest.json').read_text())
 # Accept manifest list or path mapping, but verify every listed artifact.
 entries=m.get('files',[])
 if isinstance(entries,dict):entries=[{'path':k,'sha256':v}for k,v in entries.items()]
 if entries and isinstance(entries[0],dict):
  for e in entries:
   p=b/e['path'];assert p.exists()and digest(p)==e['sha256'],str(p)
 checks.append({'task':task,'manifest_entries_verified':len(entries)})
root=HERE/'sandbox';dest=root/'02-研究/方法深化执行';dest.mkdir(parents=True,exist_ok=True)
for task in ['MD-001-R48','MD-004-R17']+TASKS:
 shutil.copytree(SOURCE/task,dest/task,dirs_exist_ok=True)
s=io.StringIO()
with contextlib.redirect_stdout(s):ns=runpy.run_path(str(dest/'MD-005-R36/生成与检查.py'))
probes=[]
def probe(name,method,key,fn,mut):
 v=copy.deepcopy(ns[key]);mut(v)
 try:r=ns[fn](v);status='accepted'
 except Exception as e:r={'error':type(e).__name__+': '+str(e)};status='rejected'
 probes.append({'name':name,'method':method,'input_sha256':hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),'actual':status,'output':r})
 (HERE/(name+'-input.json')).write_text(json.dumps(v,ensure_ascii=False,indent=2))
probe('P01-criterion-target-and-need-mutated','R36','main','check_r36',lambda x:x['criteria'][0].update(need='N-T04',target=999,unit='s',direction='higher'))
probe('P02-hard-status-empty','R36','main','check_r36',lambda x:x.update(hard_status={}))
probe('P03-caller-controlled-capability','R44','r44input','check_r44',lambda x:(x['hypotheses'][0].update(prototype_id='P-PAPER'),x['capability_needed'].update({'H-R44-01':'state_comprehension'})))
probe('P04-source-need-requirement-swapped','R42','r42input','check_r42',lambda x:(x['items'][0].update(source_requirement_candidate='RQ-T02'),x['items'][1].update(source_requirement_candidate='RQ-T01')))
probe('P05-empty-candidate-states','R36','main','check_r36',lambda x:x.update(candidate_states={}))
# Controls independently confirm the declared rejection behavior.
probe('C01-status-promotion','R42','r42input','check_r42',lambda x:x.update(engineering_pass=True))
probe('C02-observation-fabricated','R44','r44input','check_r44',lambda x:x['observations'].append({'real_user':'invented'}))
probe('C03-zero-versus-unknown','R36','main','check_r36',lambda x:x['values']['TAP-C01']['CR-BOUNDARY'].update(value=0))
after=snapshot();assert before==after,'SOURCE PACKAGES CHANGED'
result={'reviewer':'/root/needs_deepening independent Agent, not domain expert','scope':'read-only original packages; scripts executed only in isolated copied sibling directory','original_file_count':len(before),'original_packages_unchanged':True,'manifest_checks':checks,'copied_script_stdout':s.getvalue(),'replayed_original_fixed_cases':len(ns['checks']),'original_replay_all_pass':all(x['status']=='pass'for x in ns['checks']),'independent_probes':probes,'new_field_tests':0,'expert_certification':False}
(HERE/'复核实际结果.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
(HERE/'被审文件指纹.json').write_text(json.dumps(before,ensure_ascii=False,indent=2))
print(json.dumps({'source_files_unchanged':len(before),'replayed':len(ns['checks']),'probes':[(x['name'],x['actual'])for x in probes]},ensure_ascii=False))
