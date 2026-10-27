# -*- coding: utf-8 -*-
from pathlib import Path
import json,copy,hashlib,shutil
O=Path(__file__).parent;ROOT=O.parents[3];REL=Path('02-研究/方法深化执行/修订版');B=ROOT/REL;C=O/'private-copies/closing-project';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before={};nsmap={};runs=[]
packages=[('MD-013-R12-v0.1.2','R12','构建教学包.py','08155b3b3738638a6e816601e5b674345bea297a5e779313887cd10ac1e8f2e4'),('MD-021-R23-v0.1.2','R23','复算教学.py','6a343cf494c14c04070b02d29095d7aa459f810dedb4f55a3b5f480a597d2ffc'),('MD-025-R27-v0.1.2','R27','复核教学.py','8fd0aaee5e53917001c42d6e24b74d0efad0ce5299ee66722a05adf306521c02'),('MD-034-R34-v0.1.2','R34','复算教学.py','2b79d1ec38683960fdddd3bc52cbc759df1770b71c1e4ea1da319f2b6bd1e49f'),('MD-059-WB07-v0.1.1','WB07','教学检查.py','3c4e34bd0e8f4ddc4ff9882f1124ac059d81183557855d6eb6f5e5754a7e35cf'),('MD-056-WB04-v0.1.1','WB04','教学复算.py','870cab10aa00605eff22fcf555b3190fb851371d82e9603ba8095cd2da56aef4')]
shared=Path('02-研究/方法深化执行/MD-001-R48/教学包/00-共享教学输入-v0.1.0.json');(C/shared).parent.mkdir(exist_ok=True,parents=True);shutil.copy2(ROOT/shared,C/shared)
for name,rid,script,expected in packages:
 d=B/name;assert sha(d/'manifest.json')==expected;manifest=json.loads((d/'manifest.json').read_text());assert all(sha(d/x['path'])==x['sha256']for x in manifest['files']);before.update({str(p):sha(p)for p in d.rglob('*')if p.is_file()});shutil.copytree(d,C/REL/name,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'));p=C/REL/name/script;ns={'__file__':str(p.resolve()),'__name__':'independent_review'};exec(compile(p.read_text(),str(p),'exec'),ns);nsmap[rid]=ns;cases=ns['tests']if rid=='R12'else ns['cases'];runs.append({'method':rid,'package':name,'manifest_sha256':expected,'replayed_author_cases':len(cases),'all_author_assertions_passed':True,'manifest_files_verified':len(manifest['files'])})
rows=[]
def probe(rid,name,mut=None,operation=False):
 ns=nsmap[rid];x=copy.deepcopy(ns['case']if rid=='R12'else ns['base'])
 if operation:x.update(branch='product_operation',goal='study availability of state for use',artifact_kind='control_research_record',control_proxy=copy.deepcopy(ns['proxy']))
 if mut:mut(x)
 fn=ns.get('assess')or ns.get('calc')or ns['check']
 try:y=fn(x);accepted=True
 except Exception as e:y={'error':str(e)};accepted=False
 assert accepted==(mut is None),(rid,name,y)
 record={'method':rid,'name':name,'accepted':accepted,'expected_accept':mut is None,'pass':True,'output':y};rows.append(record);(O/('终审-'+rid+'-'+name+'.json')).write_text(json.dumps({'input':x,**record},ensure_ascii=False,indent=2))
for _,rid,_,_ in packages:probe(rid,'normal-control')
probe('R12','empty-text',lambda x:x['response_actions'][0].update(text=''));probe('R12','whitespace-text',lambda x:x['response_actions'][0].update(text='   '))
for k in ['object','parameter','unit']:probe('R23','empty-'+k,lambda x,k=k:[a.update({k:''})for a in x['demands']])
probe('R27','empty-difference-item',lambda x:x.update(transfer_differences=['']));probe('R27','whitespace-difference-item',lambda x:x.update(transfer_differences=['  ']))
probe('R34','duplicate-BOM-id',lambda x:x['bom'][1].update(id=x['bom'][0]['id']));probe('R34','empty-BOM-id',lambda x:x['bom'][0].update(id=''))
probe('WB07','duplicate-sample-id',lambda x:x['control_proxy']['samples'][1].update(id='S1'),True);probe('WB07','empty-sample-id',lambda x:x['control_proxy']['samples'][0].update(id=''),True)
probe('WB04','unsupported-actual-evidence',lambda x:x.update(actual_function_evidence='measured'));probe('WB04','missing-evidence-field',lambda x:x.pop('actual_function_evidence'));probe('WB04','unsupported-manufacturing-cost',lambda x:x.update(manufacturing_cost=123))
assert all(sha(Path(p))==v for p,v in before.items());result={'packages':runs,'author_cases_total':sum(r['replayed_author_cases']for r in runs),'independent_controls_and_attacks':rows,'all_expected':True,'original_file_count':len(before),'original_bytes_unchanged':True,'review_scope':'only listed mechanical shape/identity closures and normal controls; no new semantic/engineering certification'};(O/'六机械修订终审记录.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps({'author_cases':result['author_cases_total'],'independent_controls_and_attacks':len(rows),'all_expected':True,'original_files_unchanged':len(before)}))
