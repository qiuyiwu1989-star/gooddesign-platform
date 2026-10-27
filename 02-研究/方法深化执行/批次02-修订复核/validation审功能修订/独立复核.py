# -*- coding: utf-8 -*-
from pathlib import Path
import copy,json,hashlib,shutil
O=Path(__file__).parent;ROOT=O.parents[3];C=O/'private-copies/project';REL=Path('02-研究/方法深化执行/修订版/MD-013-R12-v0.1.1');D=ROOT/REL;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before={str(p):sha(p)for p in D.rglob('*')if p.is_file()and'private-sources'not in p.parts}
shutil.copytree(D,C/REL,dirs_exist_ok=True,ignore=shutil.ignore_patterns('private-sources','__pycache__'));shared=Path('02-研究/方法深化执行/MD-001-R48/教学包/00-共享教学输入-v0.1.0.json');(C/shared).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/shared,C/shared)
p=C/REL/'构建教学包.py';ns={'__file__':str(p.resolve()),'__name__':'review'};exec(compile(p.read_text(),str(p),'exec'),ns);rows=[]
for name,key,val in [('approval','acceptance_status','customer_accepted'),('type','type','customer_confirmed_requirement'),('bool-approval','customer_approved',True),('bool-engineering','engineering_validated',True),('new-false-flag','approved',False),('blank-text','text',''),('fake-role','responsibility_role','appointed actual engineer Alice')]:
 q=copy.deepcopy(ns['case']);q['response_actions'][0][key]=val
 try:out=ns['check'](q);accepted=True
 except Exception as e:out=str(e);accepted=False
 rows.append({'name':name,'accepted':accepted,'out':out});(O/(name+'.json')).write_text(json.dumps({'input':q,'accepted':accepted,'out':out},ensure_ascii=False,indent=2))
assert all(sha(Path(p))==v for p,v in before.items());(O/'复核结果.json').write_text(json.dumps({'author_cases':20,'probes':rows,'original_unchanged':True},ensure_ascii=False,indent=2));print(rows)
