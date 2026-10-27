from pathlib import Path
import copy,hashlib,json,runpy,shutil,sys
from fractions import Fraction as F
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
(OUT/'.gitignore').write_text('copies/\nprivate-review-images/\n__pycache__/\n')
SNAP=OUT/'copies/project';SNAP.mkdir(parents=True,exist_ok=True)
folders=['MD-011-R10','MD-012-R11','MD-013-R12'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(n,d):p=OUT/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2))
origfiles=[p for n in folders for p in (ROOT/'02-研究/方法深化执行'/n).rglob('*')if p.is_file()]
before={str(p.relative_to(ROOT)):sha(p)for p in origfiles}
man=[]
for n in folders:
 src=ROOT/'02-研究/方法深化执行'/n;dst=SNAP/'02-研究/方法深化执行'/n
 if dst.exists():shutil.rmtree(dst)
 shutil.copytree(src,dst,ignore=shutil.ignore_patterns('private-sources','__pycache__'))
 (dst/'private-sources').symlink_to(src/'private-sources',target_is_directory=True)
 m=json.loads((src/'manifest.json').read_text());bad=[x['path']for x in m['files']if sha(src/x['path'])!=x['sha256']];assert not bad
 man.append({'package':n,'checked':len(m['files']),'mismatches':bad})
context=Path('02-研究/方法深化执行/MD-001-R48/教学包/00-共享教学输入-v0.1.0.json');(SNAP/context).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/context,SNAP/context)
mods={}
for n in folders:
 script=SNAP/'02-研究/方法深化执行'/n/'构建教学包.py';mods[n[-3:]]=runpy.run_path(str(script))
runpy.run_path(str(SNAP/'02-研究/方法深化执行/MD-013-R12/公开案例局部复算.py'))
records=[]
for n,f in [('MD-011-R10','04-实际检查记录.json'),('MD-012-R11','05-反例与迁移实际检查.json'),('MD-013-R12','05-实际检查记录.json')]:
 j=json.loads((SNAP/'02-研究/方法深化执行'/n/'教学包'/f).read_text());records.append({'package':n,'actual_replayed_tests':j['passed'],'failure_count':j.get('failure_count',0)})
probes=[]
def probe(name,data,mut):
 rid=name[:3]
 d=copy.deepcopy(data);mut(d)
 try:r=mods[rid]['classify'if rid=='R11'else'check'](d);status='accepted'
 except Exception as e:r={'error':str(e)};status='rejected'
 put('独立探针/'+name+'-输入.json',d);put('独立探针/'+name+'-输出.json',{'status':status,'output':r});probes.append({'case':name,'status':status,'output':r})
# Explicit profile definition: changing self-development must not change two-trait qualification.
p10=mods['R10']['case'];probe('R10-no-innovation-still-match',p10,lambda d:d['profiles'][1]['self_developed_solution'].update(value=False))
probe('R10-ahead-unknown-not-qualified',p10,lambda d:d['profiles'][1]['ahead_of_named_trend'].update(value=None,state='unknown'))
probe('R10-no-trait-evidence',p10,lambda d:d['profiles'][1]['high_expected_benefit'].update(assumption_refs=[]))
probe('R10-claim-contacted-real-user',p10,lambda d:d['profiles'][1].update(outreach_performed=True))
probe('R10-text-evidence-contradicts-declared-trait',p10,lambda d:d['assumptions'][2].update(text='构造B在该趋势不领先且没有显著收益'))
p11=mods['R11']['fixture'];probe('R11-transposed-orientation',p11,lambda d:d.update(orientation={'rows':'dysfunctional/absence','columns':'functional/presence'}))
probe('R11-questionable-still-preserved',p11,lambda d:d.update(pairs=[d['pairs'][0],d['pairs'][-1]]))
probe('R11-unknown-answer-not-neutral',p11,lambda d:d['pairs'][0].update(functional=None))
probe('R11-wrong-matrix-hash',p11,lambda d:d.update(matrix_sha256='0'*64))
p12=mods['R12']['case'];probe('R12-fabricated-importance',p12,lambda d:d['importance'][0].update(value=9))
probe('R12-cell-unknown-to-zero',p12,lambda d:d['relationships'][0].update(strength=0))
probe('R12-hide-source-unknowns',p12,lambda d:d.update(source_unknowns=[]))
probe('R12-approved-acceptance-label',p12,lambda d:d['response_actions'][0].update(acceptance_status='customer_accepted'))
probe('R12-promote-response-type',p12,lambda d:d['response_actions'][0].update(type='customer_confirmed_requirement'))
# Independent exact-rational reconstruction, not copied normalize function.
A=[[F(1),F(9,5),F(5,4)],[F(5,9),F(1),F(5,9)],[F(4,5),F(9,5),F(1)]]
cs=[sum(row[c]for row in A)for c in range(3)];w=[sum(row[c]/cs[c]for c in range(3))/3 for row in A]
orig=json.loads((ROOT/'02-研究/方法深化执行/MD-013-R12/教学包/07-公开案例局部复算与敏感性.json').read_text());wf=orig['base']['normalized_column_row_average'];assert all(abs(float(a)-b)<1e-12 for a,b in zip(w,wf))
assert max(abs(float(a)-b)for a,b in zip(w,orig['reported_displayed_row_averages']))<.002
k=json.loads((ROOT/'02-研究/方法深化执行/MD-012-R11/教学包/00-分类矩阵版本.json').read_text());expected=[['Q','A','A','A','O'],['R','I','I','I','M'],['R','I','I','I','M'],['R','I','I','I','M'],['R','R','R','R','Q']];assert k['cells']==expected
assert sum(x=='Q'for row in k['cells']for x in row)==2
for n in folders:
 for s in json.loads((ROOT/'02-研究/方法深化执行'/n/'来源取得记录.json').read_text()):
  if s.get('status')=='machine_acquired_unreviewed':assert sha(ROOT/'02-研究/方法深化执行'/n/s['raw'])==s['sha256']
after={str(p.relative_to(ROOT)):sha(p)for p in origfiles};assert before==after
put('原包指纹.json',{'before':before,'unchanged':True})
put('复核结果.json',{'original_manifests':man,'replayed':records,'probes':probes,'QFD_exact_rational_weights':[str(x)for x in w],'QFD_decimal_weights':[float(x)for x in w],'Kano_table_entries':25,'Kano_Q_entries':2,'original_packages_unchanged':True,'scope':'independent_agent_source_and_fixed_fixture_audit_not_expert_or_field_validation'})
print(json.dumps({'replayed':records,'independent_probes':len(probes),'accepted_probe_ids':[x['case']for x in probes if x['status']=='accepted'],'weights':[float(x)for x in w]},ensure_ascii=False))
