"""Read-only source package audit; all new outputs remain in this review directory."""
from pathlib import Path
import copy,hashlib,itertools,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
D14=ROOT/'02-研究/方法深化执行/MD-003-R14';D17=ROOT/'02-研究/方法深化执行/MD-004-R17'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(name,obj):
 p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,ensure_ascii=False,indent=2))
files=[p for d in [D14,D17]for p in d.rglob('*')if p.is_file()]
before={str(p.relative_to(ROOT)):sha(p)for p in files}
manifest_checks=[]
for d in [D14,D17]:
 m=json.loads((d/'manifest.json').read_text());bad=[x['path']for x in m['files']if sha(d/x['path'])!=x['sha256']]
 assert not bad,(d,bad)
 manifest_checks.append({'package':d.name,'entries':len(m['files']),'bad':bad})
ns={'__name__':'independent_read_only_audit','__file__':str(D14/'核查教学模型.py')}
exec(compile((D14/'核查教学模型.py').read_text(),str(D14/'核查教学模型.py'),'exec'),ns)
base=json.loads((D14/'教学包/01-功能与接口输入-v0.1.0.json').read_text());records=[]
record14=json.loads((D14/'教学包/05-实际结构检查.json').read_text())
for t in record14['cases']:
 p=D14/t['input'];assert sha(p)==t['input_sha256'];data=json.loads(p.read_text())
 try:o=ns['check'](data);actual='accepted'
 except ns['Reject']as e:o={'reason':str(e)};actual=str(e)
 assert actual==t['expected'];records.append({'package':'R14','case':t['id'],'actual':actual,'match_author':True,'output':o})
# Direct use of old read-only evaluator verified by source inspection. -B avoids pycache writes.
old=ROOT/'output/method-reader-review/upgrades/R17-v0.2.2/run_case.py'
python=str(ROOT/'.runtime/pipeline/bin/python')if(ROOT/'.runtime/pipeline/bin/python').exists()else sys.executable
record17=json.loads((D17/'教学包/07-反例与迁移实际记录.json').read_text())
for t in record17['cases']:
 p=D17/t['input'];assert sha(p)==t['input_sha256']
 r=subprocess.run([python,'-B',str(old),str(p)],capture_output=True,text=True);o=json.loads(r.stdout)
 assert r.returncode==t['exit_code']
 if t['expected_counts']is not None:assert o['counts']==t['expected_counts']
 if t['expected_error_contains']:assert t['expected_error_contains']in o['error']
 put('R17重跑/'+t['id']+'.json',o);records.append({'package':'R17','case':t['id'],'exit_code':r.returncode,'match_author':True,'output_sha256':hashlib.sha256(r.stdout.encode()).hexdigest()})
# Independently calculate resource example without calling author's arithmetic routine.
a=json.loads((D17/'教学包/06-独立构造资源反例.json').read_text());powers=a['assumed_powers_W'];cap=a['assumed_limit_W']
model=json.loads((D17/'教学包/01-形态矩阵输入-v0.1.0.json').read_text());dims=[x['option_ids']for x in model['dimensions']]
pairs=[sum(powers[i]for i in z)for d1,d2 in itertools.combinations(dims,2)for z in itertools.product(d1,d2)]
wholes=[sum(powers[i]for i in z)for z in itertools.product(*dims)]
assert len(pairs)==12 and max(pairs)<=cap and len(wholes)==8 and sum(x>cap for x in wholes)==1
# Source trace and downstream status checks.
hand=json.loads((D17/'教学包/03-交给R36的候选-v0.1.0.json').read_text())
assert len(hand['candidates'])==8 and all(x['state']=='conditional_research'and not x['satisfied_requirements']and not x['engineering_validated'] for x in hand['candidates'])
assert hand['source_input']['sha256']==sha(D17/'教学包'/hand['source_input']['file'])
assert hand['source_output']['sha256']==sha(D17/'教学包'/hand['source_output']['file'])
assert hand['source_R14']['sha256']==sha(ROOT/hand['source_R14']['path'])
assert base['upstream']['sha256']==sha(ROOT/base['upstream']['path'])
probes=[]
def probe(name,mutator):
 d=copy.deepcopy(base);mutator(d)
 try:o=ns['check'](d);status='accepted'
 except ns['Reject']as e:o={'reason':str(e)};status='rejected'
 put('独立探针/'+name+'-输入.json',d);put('独立探针/'+name+'-输出.json',{'status':status,'output':o});probes.append({'id':name,'status':status,'output':o})
probe('R14-erase-shared-unknowns',lambda d:d.update(unknowns=[]))
probe('R14-tamper-source-version',lambda d:d['upstream'].update(version='99.0.0'))
def dropneed(d):
 d['coverage']=[x for x in d['coverage']if x['need_id']!='N-T04']
 for f in d['functions']:f['parent_need_ids']=[n for n in f['parent_need_ids']if n!='N-T04']
probe('R14-drop-shared-need',dropneed)
def dropunits(d):
 for i in d['interfaces']:i.pop('representation_units',None)
probe('R14-drop-all-unit-representations',dropunits)
# All reviewed source package bytes must be unchanged.
after={str(p.relative_to(ROOT)):sha(p)for p in files};assert before==after
put('原包只读指纹.json',{'before':before,'after_equal':True})
put('复核结果.json',{'manifest_checks':manifest_checks,'replayed_cases':records,'independent_probes':probes,'resource_recalculation':{'pairs':len(pairs),'max_pair_W':max(pairs),'wholes':len(wholes),'max_whole_W':max(wholes),'cap_W':cap,'whole_over':sum(x>cap for x in wholes)},'all_8_candidates_conditional':True,'upstream_bindings_match':True,'source_packages_unchanged':True,'scope':'independent_agent_desktop_and_fixed_fixture_audit_not_domain_expert_or_engineering_validation'})
print(json.dumps({'replayed':len(records),'all_author_expectations_match':True,'new_probes':[(x['id'],x['status'])for x in probes],'source_packages_unchanged':True},ensure_ascii=False))
