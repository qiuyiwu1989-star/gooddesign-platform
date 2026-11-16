# -*- coding: utf-8 -*-
from pathlib import Path
import json,hashlib,shutil,copy,runpy,contextlib,io
V=Path(__file__).resolve().parent;BASE=V.parent;ROOT=BASE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
names=['MD-008-R02','MD-009-R03','MD-010-R09']
before={str(p):sha(p)for n in names for p in (BASE/n).rglob('*')if p.is_file()}
# Execute originals in a disposable external-drive sandbox only.
S=V/'第二批修订证据/sandbox';S.mkdir(parents=True,exist_ok=True)
shutil.copytree(BASE/'MD-001-R48',S/'MD-001-R48',dirs_exist_ok=True)
old={}
for n in names:
 shutil.copytree(BASE/n,S/n,dirs_exist_ok=True)
 with contextlib.redirect_stdout(io.StringIO()):old[n]=runpy.run_path(str(S/n/'构建教学包.py'))
new={}
for n in names:
 d=V/(n+'-v0.1.1');shutil.copytree(BASE/n,d,dirs_exist_ok=True)
 p=d/'构建教学包.py';s=p.read_text()
 s='# -*- coding: utf-8 -*-\n'+s.replace("B.parent/'MD-001-R48/教学包/00-共享教学输入-v0.1.0.json'","B.parent/'MD-001-R48-v0.1.1/教学包/00-共享教学输入-v0.1.0.json'")
 s=s.replace("'first_batch_pending_revision_context_only'","'first_batch_revised_context_only_not_customer_approved'")
 if n.endswith('R02'):s=s.replace('not isinstance(v,(int,float))','type(v)not in(int,float)')
 if n.endswith('R03'):s=s.replace("def check(i):\n","def check(i):\n if any(k not in i or type(i[k])is not list for k in ['observations','results']):raise ValueError('required_state_array_missing_or_wrong_type')\n")
 if n.endswith('R09'):s=s.replace(" for s in ss:\n"," for s in ss:\n  if type(s.get('actor_id'))is not str or not s['actor_id'].strip():raise ValueError('actor_instance_missing')\n")
 p.write_text(s)
 with contextlib.redirect_stdout(io.StringIO()):new[n]=runpy.run_path(str(p))
rows=[]
for n in names:
 a=old[n];b=new[n]
 if n.endswith('R02'):
  probes=[('bool_total',lambda x:x.update(totals=[True],segments=None)),('bool_phase',lambda x:x.update(totals=[1],segments=[{'normal':True,'recovery':0}]))];key='brief';fn='examine'
 elif n.endswith('R03'):
  probes=[('missing_observations',lambda x:x.pop('observations')),('missing_results',lambda x:x.pop('results')),('wrong_observations_type',lambda x:x.update(observations=''))];key='plan';fn='check'
 else:
  probes=[('missing_actor',lambda x:x['raw']['stories'][0].pop('actor_id')),('blank_actor',lambda x:x['raw']['stories'][0].update(actor_id=' ')),('bool_actor',lambda x:x['raw']['stories'][0].update(actor_id=True))];key='base';fn='check'
 for label,mut in probes:
  outputs=[]
  for m in [a,b]:
   q=copy.deepcopy(m[key]);mut(q)
   try:out=m[fn](q);state='accepted'
   except Exception as e:out={'error':str(e)};state='rejected'
   outputs.append({'state':state,'input':q,'output':out})
  assert outputs[0]['state']=='accepted' and outputs[1]['state']=='rejected'
  rows.append({'method':n,'probe':label,'old':outputs[0],'new':outputs[1]})
 d=V/(n+'-v0.1.1');mine=[x for x in rows if x['method']==n]
 (d/'修订实际回归.json').write_text(json.dumps({'package_version':'0.1.1','input_version':'0.1.0','probes':mine,'scope':'fixed input structure checks; not field validation'},ensure_ascii=False,indent=2))
 (d/'修订说明.md').write_text('# v0.1.1 输入结构修订\n\n旧包保留。输入仍为构造 TAP-TEACH-001 v0.1.0；包版本改为0.1.1。来源与方法论解释承接旧版，未新增现场证据、客户批准或方法有效性证明。旧绕过及新拒绝的完整输入和返回见修订实际回归.json。共享输入重新绑定首批修订目录，相同SHA；不将Agent复核视作专家认证。\n')
 meta=json.loads((d/'审核与版本.json').read_text());meta.pop('files',None);meta.update(version='0.1.1',problem_version='0.1.0',independent_agent_review='pending_revision_review',regression_count=len(mine));(d/'审核与版本.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
 # Remove old archive/source download scripts that target old siblings and keep authoritative source notes.
 for f in ['整理档案.py','取得来源.py']:
  if (d/f).exists():(d/f).unlink()
 files=[{'path':str(p.relative_to(d)),'sha256':sha(p)}for p in sorted(d.rglob('*'))if p.is_file()and 'private-sources'not in p.parts and '__pycache__'not in p.parts and p.name!='manifest.json']
 (d/'manifest.json').write_text(json.dumps({'task':n,'version':'0.1.1','input_version':'0.1.0','exclude':['private-sources','__pycache__'],'files':files},ensure_ascii=False,indent=2))
 print(n,sha(d/'manifest.json'))
assert all(sha(Path(p))==h for p,h in before.items())
E=V/'第二批修订证据';(E/'.gitignore').write_text('sandbox/\n');(E/'实际回归.json').write_text(json.dumps({'old_files_unchanged':len(before),'probes':rows},ensure_ascii=False,indent=2))
