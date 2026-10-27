# -*- coding: utf-8 -*-
from pathlib import Path
import copy,json,hashlib,shutil,math
O=Path(__file__).parent;ROOT=O.parents[3];B=ROOT/'02-研究/方法深化执行';C=O/'private-copies';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();nsmap={};before={}
for name,script in [('MD-033-R33','复算教学.py'),('MD-034-R34','复算教学.py'),('MD-035-R35','教育模型复算.py')]:
 d=B/name;before.update({str(p):sha(p)for p in d.rglob('*')if p.is_file()and'private-sources'not in p.parts});shutil.copytree(d,C/name,dirs_exist_ok=True,ignore=shutil.ignore_patterns('private-sources','__pycache__'));p=C/name/script;ns={'__file__':str(p.resolve()),'__name__':'review'};exec(compile(p.read_text(),str(p),'exec'),ns);nsmap[name[-3:]]=ns
rows=[]
def probe(r,n,mut):
 ns=nsmap[r];q=copy.deepcopy(ns['base']);mut(q)
 try:v=ns['calc'](q);err=None
 except Exception as e:v=None;err=str(e)
 rows.append({'method':r,'name':n,'result':v,'error':err})
probe('R33','unknown-material-no-rank',lambda x:x['materials'][0].update(E_Pa=None))
probe('R33','temperature-NaN',lambda x:x.update(max_service_C=float('nan')))
probe('R34','negative-BOM-quantity',lambda x:x['bom'][0].update(qty=-1))
probe('R34','boolean-service-policy',lambda x:x.update(service_requires_replaceable_seal='false'))
# Independent dimensional/arithmetic verification, not the author's assertion alone.
s=nsmap['R33'];a=s['calc'](s['base']);b=s['calc']({**s['base'],'model':'square_cantilever'})
for result in [a,b]:
 for rr,mat in zip(result['rows'],s['base']['materials']):
  if 'area_m2'in rr['geometry']:
   A=rr['geometry']['area_m2'];stress=100/A;delta=100*.3/(mat['E_Pa']*A);mass=mat['rho_kg_m3']*.3*A
  else:
   h=rr['geometry']['square_side_m'];I=h**4/12;stress=100*.3*(h/2)/I;delta=100*.3**3/(3*mat['E_Pa']*I);mass=mat['rho_kg_m3']*.3*h*h
  assert math.isclose(stress,rr['stress_Pa'],rel_tol=1e-12)and math.isclose(delta,rr['deflection_m'],rel_tol=1e-12)and math.isclose(mass,rr['mass_kg'],rel_tol=1e-12)
# Q4 rigid modes and PSD, normalized density-filter variant, small independent mesh.
n=nsmap['R35'];np=n['np'];K,_,_=n['element'](.25,.1);eig=np.linalg.eigvalsh(K);assert np.max(np.abs(K-K.T))<1e-12 and sum(abs(eig)<1e-10)==3 and eig.min()>-1e-10
cfg={**n['base'],'nx':8,'ny':4};v=n['solve'](cfg,maxiter=30);assert v['final']['selected_derivative_relative_error']<1e-3 and v['final']['free_equilibrium_relative_residual']<1e-6
stored=json.loads((B/'MD-035-R35/教学包/02-迭代敏感性与几何重分析.json').read_text());originalruns=[{'label':x['label'],'converged':x['result']['final']['converged_design_change'],'iterations':x['result']['final']['iterations'],'change':x['result']['final']['last_max_change']}for x in stored['cases']]
assert all(sha(Path(p))==v for p,v in before.items());result={'R33_independent_closed_form_match':True,'R33_axial_rank':a['ranking_by_mass'],'R33_square_bending_rank':b['ranking_by_mass'],'R35_element_eigenvalues':eig.tolist(),'R35_independent_small_mesh':v['final'],'R35_original_runs':originalruns,'probes':rows,'original_packages_unchanged':True};(O/'复核结果.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False))
