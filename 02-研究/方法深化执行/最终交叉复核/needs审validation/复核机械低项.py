# -*- coding: utf-8 -*-
from pathlib import Path
import copy,json,hashlib,shutil,runpy,contextlib,io
D=Path(__file__).resolve().parent;B=D.parents[1];V=B/'修订版';S=D/'sandbox最后机械/02-研究/方法深化执行';(S/'修订版').mkdir(parents=True,exist_ok=True)
names=['MD-014-R13-v0.1.2','MD-007-R42-v0.1.3','MD-061-WB09-v0.1.1','MD-062-WB10-v0.1.1','MD-048-R52-v0.1.1'];expected=['8810ae4a433d0c5fcae21bde00ccda0f2384b8363406fa4648d10643c36b8557','efac7d7a52eb84b777aff59d49951388fe198591233ffdc1d449eab99b52affb','239097f0bf6d99ab7155b0701d37aa8db4f9f8905c82a43d41de621a556156d3','0d3142c508bf9791ed83b8f99aceef41ebefd1f327a73705dac6a0cfd3bbc522','aab2c7de9b2ea21ad84e10382bfdaa7ca0e05ede0177c756339c9137e16dfafc']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
before={str(p):sha(p)for n in names for p in(V/n).rglob('*')if p.is_file()}
for n in names+['MD-001-R48-v0.1.1','MD-002-R08-v0.1.1','MD-003-R14-v0.1.1','MD-004-R17-v0.1.1','MD-005-R36-v0.1.1','MD-006-R44-v0.1.2']:shutil.copytree(V/n,S/'修订版'/n,dirs_exist_ok=True)
for n in ['MD-001-R48','MD-005-R36','MD-006-R44','MD-007-R42']:shutil.copytree(B/n,S/n,dirs_exist_ok=True)
mods={};replays=[]
for n,script in [(names[0],'教学与反例.py'),(names[1],'生成与检查.py'),(names[2],'教学与反例.py'),(names[4],'教学与反例.py')]:
 f=io.StringIO()
 with contextlib.redirect_stdout(f):mods[n]=runpy.run_path(str(S/'修订版'/n/script))
 replays.append({'entry':n,'stdout':f.getvalue()})
a=mods[names[0]];b=mods[names[1]];w=mods[names[2]];v=mods[names[4]]
checks=[('R13-normal',a,'base13',lambda m,x:m['check13'](x),lambda x:None,'accepted'),('R13-empty-encoding',a,'base13',lambda m,x:m['check13'](x),lambda x:x['representations'].update(B={'S-CURRENT':'','S-STALE':''}),'rejected'),('R42-normal',b,'r42input',lambda m,x:m['check_r42'](x),lambda x:None,'accepted'),('R42-source-path',b,'r42input',lambda m,x:m['check_r42'](x),lambda x:x['source_r44'].update(path='unrelated.json'),'rejected'),('WB09-normal',w,'b',lambda m,x:m['check']('WB09',x),lambda x:None,'accepted'),('WB09-bool-mass',w,'b',lambda m,x:m['check']('WB09',x),lambda x:x['parameters'].update(m=True),'rejected'),('WB10-normal',w,'c',lambda m,x:m['check']('WB10',x),lambda x:None,'accepted'),('WB10-bool-data',w,'c',lambda m,x:m['check']('WB10',x),lambda x:x['data'][0].__setitem__(0,True),'rejected'),('R52-normal',v,'voi',lambda m,x:m['check52'](x),lambda x:None,'accepted'),('R52-missing-prior-invalid-likelihood',v,'voi',lambda m,x:m['check52'](x),lambda x:x.update(prior=None,signal_positive_likelihood=[2,-1]),'rejected'),('R52-missing-prior-valid-likelihood',v,'voi',lambda m,x:m['check52'](x),lambda x:x.update(prior=None),'accepted')]
rows=[]
for n,m,key,fn,mut,expect in checks:
 q=copy.deepcopy(m[key]);mut(q)
 try:o=fn(m,q);state='accepted'
 except Exception as e:o={'error_type':type(e).__name__,'error':str(e)};state='rejected'
 assert state==expect,(n,state,o)
 if n=='R52-missing-prior-valid-likelihood':assert o['EVPI']is None and o['EVSI']is None
 rows.append({'name':n,'input':q,'actual':state,'expected':expect,'output':o,'pass':True})
assert all(sha(Path(p))==h for p,h in before.items());man=[]
for n,h in zip(names,expected):
 d=V/n;assert sha(d/'manifest.json')==h;x=json.loads((d/'manifest.json').read_text());assert all(sha(d/i['path'])==i['sha256']for i in x['files']);man.append({'task':n,'manifest_sha256':h,'entries':len(x['files'])})
(D/'机械低项实际复核.json').write_text(json.dumps({'unchanged_files':len(before),'manifests':man,'replayed':replays,'independent_cases':11,'passed':11,'probes':rows},ensure_ascii=False,indent=2,allow_nan=False));print(json.dumps({'unchanged_files':len(before),'independent_cases':11,'passed':11,'replays':replays},ensure_ascii=False))
