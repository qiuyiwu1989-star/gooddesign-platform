from pathlib import Path
import copy,hashlib,json,runpy,shutil,contextlib,io
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
SRC=ROOT/'02-研究/方法深化执行';ISO=HERE/'隔离副本';ISO.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def snapshot():return {str(p.relative_to(SRC)):sha(p)for name in ['MD-001-R48','MD-002-R08']for p in (SRC/name).rglob('*')if p.is_file()}
before=snapshot();manifest_results=[]
for name in ['MD-001-R48','MD-002-R08']:
 b=SRC/name;m=json.loads((b/'manifest.json').read_text());good=0
 for x in m['files']:
  assert sha(b/x['path'])==x['sha256'],(name,x['path']);good+=1
 manifest_results.append({'package':name,'manifest_sha256':sha(b/'manifest.json'),'files_verified':good})
 shutil.copytree(b,ISO/name,dirs_exist_ok=True)
logs={};envs={}
# R08 before R48 preserves the expected sibling evidence file.
for name in ['MD-002-R08','MD-001-R48']:
 stream=io.StringIO()
 with contextlib.redirect_stdout(stream):envs[name]=runpy.run_path(str(ISO/name/'构建教学包.py'))
 logs[name]=stream.getvalue()
probes=[]
def probe(name,method,data):
 e=envs[method];d=copy.deepcopy(data)
 try:r=e['check'](d);status='accepted'
 except Exception as x:r={'error':type(x).__name__+': '+str(x)};status='rejected'
 probes.append({'id':name,'method':method,'status':status,'input':d,'result':r})
r48=envs['MD-001-R48']['draft'];r08=envs['MD-002-R08']['raw']
a=copy.deepcopy(r48);a['candidates'][0]['text']='构造攻击：保证无须测量即可绝对安全自动切割';probe('R48-unsupported-text-with-valid-labels','MD-001-R48',a)
a=copy.deepcopy(r48);a['retired_hypotheses'].append('NO-SUCH-HYPOTHESIS');probe('R48-dangling-retired-hypothesis','MD-001-R48',a)
a=copy.deepcopy(r08);a['records'][0]['text']='构造攻击：未暂停且未观察到残留';probe('R08-text-encoding-disagreement','MD-002-R08',a)
a=copy.deepcopy(r08);a['records'][3].update(pause_before=True,residue_observed=False);probe('R08-remove-H01-counterexample-in-fields','MD-002-R08',a)
a=copy.deepcopy(r08);a['records'][0]['actor']='ACT-MISSING';probe('R08-actor-closure-negative','MD-002-R08',a)
a=copy.deepcopy(r48);a['candidates'][0]['direction']='le';probe('R48-direction-still-incomplete-negative','MD-001-R48',a)
# Actual rebuild with mismatched R08 lineage in the isolated sibling file.
p=ISO/'MD-002-R08/教学包/03-竞争解释与修订.json';a=json.loads(p.read_text());a['source_binding']['problem_id']='OTHER-PROBLEM';p.write_text(json.dumps(a,ensure_ascii=False,indent=2));stream=io.StringIO()
try:
 with contextlib.redirect_stdout(stream):rebuilt=runpy.run_path(str(ISO/'MD-001-R48/构建教学包.py'))
 lineage={'status':'accepted','stdout':stream.getvalue(),'resulting_evidence_binding':rebuilt['draft']['evidence_binding'],'wrong_source_binding':a['source_binding']}
except Exception as e:lineage={'status':'rejected','error':str(e)}
assert before==snapshot(),'review mutated source package'
result={'reviewer':'function_deepening independent Agent (not domain expert)','manifest_verification':manifest_results,'shared_sha256':sha(SRC/'MD-001-R48/教学包/00-共享教学输入-v0.1.0.json'),'isolated_original_rebuild_logs':logs,'probes':probes,'mismatched_sibling_source_binding_rebuild':lineage,'originals_unchanged':True,'source_http_bytes_available_for_hash_recheck':False}
(HERE/'实际复核结果.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'manifest_results':manifest_results,'probes':[(p['id'],p['status'])for p in probes],'wrong_sibling_lineage_rebuild':lineage['status'],'originals_unchanged':True},ensure_ascii=False))
