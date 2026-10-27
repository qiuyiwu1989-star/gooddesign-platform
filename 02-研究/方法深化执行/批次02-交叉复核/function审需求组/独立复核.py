from pathlib import Path
import copy,hashlib,json,shutil,runpy,io,contextlib
P=Path(__file__).resolve().parent;ROOT=P.parents[3];BASE=ROOT/'02-研究/方法深化执行';ISO=P/'隔离副本';ISO.mkdir(exist_ok=True)
NAMES=['MD-008-R02','MD-009-R03','MD-010-R09']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def snapshot():return {str(p.relative_to(BASE)):sha(p)for n in NAMES for p in(BASE/n).rglob('*')if p.is_file()}
before=snapshot();record=[];env={}
# Every rebuild targets the isolated sibling tree, including the shared context copy.
s=ISO/'MD-001-R48/教学包';s.mkdir(parents=True,exist_ok=True);shutil.copy2(BASE/'MD-001-R48/教学包/00-共享教学输入-v0.1.0.json',s/'00-共享教学输入-v0.1.0.json')
for n in NAMES:
 b=BASE/n;entries=json.loads((b/'manifest.json').read_text())['files']
 for x in entries:assert sha(b/x['path'])==x['sha256'],(n,x['path'])
 claims=json.loads((b/'来源与主张.json').read_text());source_checks=[]
 for x in claims['sources']:
  assert sha(b/x['raw_file'])==x['raw_sha256'];assert sha(b/x['text_file'])==x['text_sha256']
  source_checks.append(x['id'])
 for c in claims['claims']:
  t=next(x for x in claims['sources']if x['id']==c['source_id']);text=(b/t['text_file']).read_text();a=c['anchor_in_text'];assert text[a:a+len(c['short_anchor'])]==c['short_anchor'],(n,c['id'])
 shutil.copytree(b,ISO/n,dirs_exist_ok=True,ignore=shutil.ignore_patterns('private-sources','__pycache__'));buf=io.StringIO()
 with contextlib.redirect_stdout(buf):env[n]=runpy.run_path(str(ISO/n/'构建教学包.py'))
 record.append({'package':n,'manifest_sha256':sha(b/'manifest.json'),'files_verified':len(entries),'source_bytes_and_anchors_verified':source_checks,'isolated_rebuild_stdout':buf.getvalue()})
probes=[]
def probe(n,name,base,mut):
 x=copy.deepcopy(base);mut(x);fn=env[n]['examine']if n=='MD-008-R02'else env[n]['check']
 try:o=fn(x);status='accepted'
 except Exception as e:o={'error':str(e)};status='rejected'
 probes.append({'package':n,'id':name,'input':x,'status':status,'output':o})
e=env[NAMES[0]];probe(NAMES[0],'R02-boolean-quantity',e['updated'],lambda x:x.update(totals=[True],segments=[{'normal':True,'recovery':False}]))
probe(NAMES[0],'R02-missing-explicit-approval',e['brief'],lambda x:x.pop('customer_approved'))
probe(NAMES[0],'R02-without-votes-still-no-inference',e['brief'],lambda x:x.pop('team_votes'))
e=env[NAMES[1]];probe(NAMES[1],'R03-missing-observation-and-results',e['plan'],lambda x:(x.pop('observations'),x.pop('results')))
probe(NAMES[1],'R03-code-text-semantic-not-checked',e['plan'],lambda x:x['variants'][0].update(label='构造攻击：该标签已证明刀具安全'))
e=env[NAMES[2]];probe(NAMES[2],'R09-nonsensical-job-with-valid-note-ids',e['base'],lambda x:x['coding'][0].update(functional_progress_hypothesis='构造攻击：因此真实市场确定会购买机器人'))
probe(NAMES[2],'R09-actor-instance-deleted',e['base'],lambda x:x['raw']['stories'][0].pop('actor_id'))
probe(NAMES[2],'R09-text-change-not-recode',e['base'],lambda x:x['raw']['stories'][0]['notes'][1].update(text='构造攻击：负责人并不担心支援，只在意颜色'))
probe(NAMES[2],'R09-operator-role-negative',e['base'],lambda x:x['coding'][0].update(job_actor_role='ACT-OP'))
assert before==snapshot(),'source packages changed during review'
(P/'实际复核结果.json').write_text(json.dumps({'reviewer':'function_deepening independent Agent not domain expert','verified':record,'shared_sha256':sha(s/'00-共享教学输入-v0.1.0.json'),'probes':probes,'original_packages_unchanged':True},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'verified':[(x['package'],x['files_verified'])for x in record],'probes':[(x['id'],x['status'])for x in probes],'source_unchanged':True},ensure_ascii=False))
