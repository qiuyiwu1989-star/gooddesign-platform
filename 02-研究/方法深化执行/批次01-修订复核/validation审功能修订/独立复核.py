# -*- coding: utf-8 -*-
from pathlib import Path
import copy,json,hashlib,shutil,subprocess,sys,importlib.util
OUT=Path(__file__).parent;ROOT=OUT.parents[3];CLONE=OUT/'private-copies/project';PREF=Path('02-研究/方法深化执行/修订版');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
packages=['MD-003-R14-v0.1.1','MD-004-R17-v0.1.1'];before={str(p.relative_to(ROOT)):sha(p)for n in packages for p in(ROOT/PREF/n).rglob('*')if p.is_file()and'private-sources'not in p.parts}
for n in ['MD-001-R48-v0.1.1','MD-002-R08-v0.1.1']+packages:
 shutil.copytree(ROOT/PREF/n,CLONE/PREF/n,dirs_exist_ok=True,ignore=shutil.ignore_patterns('private-sources','__pycache__'))
old=Path('output/method-reader-review/upgrades/R17-v0.2.2');shutil.copytree(ROOT/old,CLONE/old,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
d=CLONE/PREF/packages[0];spec=importlib.util.spec_from_file_location('review_r14',d/'核查教学模型.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
base=json.loads((d/'教学包/01-功能与接口输入-v0.1.1.json').read_text());m.check(base)
r=subprocess.run([sys.executable,'-B',str(d/'运行修订检查.py')],capture_output=True,text=True);assert r.returncode==0,r.stderr
r17=CLONE/PREF/packages[1];r=subprocess.run([sys.executable,'-B',str(r17/'反例与迁移复算.py')],capture_output=True,text=True);assert r.returncode==0,r.stderr
probes=[]
def run(name,change):
 x=copy.deepcopy(base);change(x)
 try:result=m.check(x);accepted=True
 except(ValueError,KeyError,TypeError)as e:accepted=False;result=str(e)
 probes.append({'name':name,'accepted':accepted,'result':result});(OUT/(name+'.json')).write_text(json.dumps({'input':x,'accepted':accepted,'result':result},ensure_ascii=False,indent=2))
run('重放-未知清空',lambda x:x.update(unknowns=[]));run('重放-版本漂移',lambda x:x['upstream'].update(version='99.0.0'))
def drop(x):
 x['coverage']=[c for c in x['coverage']if c['need_id']!='N-T04']
 for f in x['functions']:f['parent_need_ids']=[n for n in f['parent_need_ids']if n!='N-T04']
run('重放-需求覆盖删除',drop)
run('新-需求正文改写',lambda x:x['source_needs'][0].update(text='invented approved need'))
run('新-反向引用不闭合',lambda x:x['functions'][0].update(parent_need_ids=['N-T04']))
run('新-共享未知正文漂移',lambda x:x['source_unknowns'][0].update(text='already measured'))
assert not any(p['accepted']for p in probes)
lock=json.loads((d/'上游锁定.json').read_text());bindings=[{'path':x['path'],'sha_matches':sha(ROOT/x['path'])==x['sha256']}for x in lock['method_artifacts']];assert all(x['sha_matches']for x in bindings)
h=json.loads((r17/'教学包/03-交给R36的候选-v0.1.1.json').read_text());assert len(h['candidates'])==8 and all(c['state']=='conditional_research'and not c['satisfied_requirements']for c in h['candidates']);assert h['source_R14']['sha256']==sha(ROOT/h['source_R14']['path'])
after={p:sha(ROOT/p)for p in before};assert before==after
result={'source_packages_unchanged':True,'R14_author_replay_checks':17,'R17_author_replay_checks':8,'independent_attacks':probes,'bindings':bindings,'all_8_conditional':True,'scope':'isolated fixed-fixture audit, not expert certification'}
(OUT/'复核结果.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False))
