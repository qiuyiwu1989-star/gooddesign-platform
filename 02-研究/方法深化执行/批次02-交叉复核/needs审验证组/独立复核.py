from pathlib import Path
import copy,hashlib,json,runpy,shutil,contextlib,io
PROJECT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent;SOURCE=PROJECT/'02-研究/方法深化执行'
TASKS=['MD-014-R13','MD-015-R15','MD-016-R16'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def snapshot():return {str(p.relative_to(PROJECT)):sha(p)for t in TASKS for p in (SOURCE/t).rglob('*')if p.is_file()}
before=snapshot();man=[];claims=[]
for task in TASKS:
 b=SOURCE/task;j=json.loads((b/'manifest.json').read_text())
 for x in j['files']:assert sha(b/x['path'])==x['sha256']
 man.append({'task':task,'manifest_files':len(j['files'])})
 for c in json.loads((b/'来源与主张.json').read_text())['claims']:
  raw=PROJECT/c['raw_path_private'];txt=PROJECT/c['text_path_private'];t=txt.read_text();p=t.find(c['short_anchor']);assert sha(raw)==c['raw_sha256']and sha(txt)==c['text_sha256']and p==c['anchor_start']
  claims.append({'task':task,'claim_id':c['claim_id'],'hashes_and_anchor_verified':True,'short_anchor':c['short_anchor'],'selected_context_support':'supports bounded source claim; platform model distinguished','source_scope':'selected captured context, not full standard validation'})
root=HERE/'sandbox';dest=root/'02-研究/方法深化执行';dest.mkdir(parents=True,exist_ok=True)
for task in ['MD-001-R48','MD-005-R36','MD-006-R44','MD-007-R42']+TASKS:shutil.copytree(SOURCE/task,dest/task,dirs_exist_ok=True)
out=io.StringIO()
with contextlib.redirect_stdout(out):ns=runpy.run_path(str(dest/'MD-014-R13/教学与反例.py'))
results=[]
def probe(name,key,fn,mut):
 d=copy.deepcopy(ns[key]);mut(d)
 try:r=ns[fn](d);status='accepted'
 except Exception as e:r={'error':type(e).__name__+': '+str(e)};status='rejected'
 (HERE/(name+'-input.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2))
 results.append({'name':name,'input_sha256':hashlib.sha256(json.dumps(d,ensure_ascii=False,sort_keys=True).encode()).hexdigest(),'actual':status,'output':r})
probe('P01-R13-empty-representations','base13','check13',lambda x:x.update(representations={}))
probe('P02-R13-one-variant-only','base13','check13',lambda x:x['representations'].pop('A'))
probe('C01-R15-edge-support-swap','base15','check15',lambda x:x['edges'][0].update(means='S1'))
probe('C02-R15-support-omitted','base15','check15',lambda x:x.update(support=[]))
probe('C03-R16-counterevidence-loss','base16','check16',lambda x:x['hypotheses'][0].update(counterevidence=[]))
probe('C04-R16-noncomparable-success','base16','check16',lambda x:x['post_action'].update(benefit_claim='无再发，证明已有效'))
probe('C05-R13-body-dimension-invented','base13','check13',lambda x:x['population'].update(anthropometric_parameters={'reach_mm':700}))
probe('C06-R16-boolean-exposure','base16','check16',lambda x:x['post_action'].update(comparable_exposures=True))
after=snapshot();assert before==after
(HERE/'被审文件指纹.json').write_text(json.dumps(before,ensure_ascii=False,indent=2))
(HERE/'来源复核.json').write_text(json.dumps(claims,ensure_ascii=False,indent=2))
(HERE/'复核实际结果.json').write_text(json.dumps({'reviewer':'needs_deepening independent Agent not domain expert','original_files_unchanged':len(before),'original_fixed_checks_replayed':len(ns['records']),'original_stdout':out.getvalue(),'manifest_checks':man,'independent_probes':results,'engineering_validation':False},ensure_ascii=False,indent=2))
print(json.dumps({'unchanged_files':len(before),'original_cases':len(ns['records']),'claims':len(claims),'probes':[(x['name'],x['actual'])for x in results]},ensure_ascii=False))
