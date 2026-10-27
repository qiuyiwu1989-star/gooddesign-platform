from pathlib import Path
import json,hashlib,math,statistics
import numpy as np
root=Path(__file__).resolve().parents[2];src=root/'validation';dst=Path(__file__).parent
m=json.loads((src/'manifest.json').read_text());checks=[]
for f in m['files']:
 actual=hashlib.sha256((src/f['path']).read_bytes()).hexdigest();assert actual==f['sha256'],f
checks.append({'case':'all frozen author files','result':len(m['files']),'identity':'fingerprint_only_not_content_quality'})
rows=json.loads((src/'教学附件/R38-构造CCD与诊断.json').read_text())['rows'];X=np.array([[1,r['x1'],r['x2'],r['x1']*r['x2'],r['x1']**2,r['x2']**2] for r in rows]);y=np.array([r['y'] for r in rows]);coef=np.linalg.lstsq(X,y,rcond=None)[0];assert np.allclose(coef,[10,2,-2,0,-2,-2]);assert np.linalg.matrix_rank(X)==6
checks.append({'case':'R38 independent least-squares','coef':coef.tolist(),'rank':6,'residual_df':7,'pure_error_ss':sum((v-10)**2 for v in [9.8,9.9,10,10.1,10.2]),'result':'consistent'})
checks.append({'case':'R37 w=.6','A':.3+.6*.6,'B':.8-.4*.6,'break_even_w':.5})
checks.append({'case':'R39 spread only not probability','A_s':statistics.stdev([120,90,120,90]),'B_s':statistics.stdev([99,101,99,101])})
checks.append({'case':'R43 boundary sums','A':2*100+10+30+20+4,'B':5*60+25+20+10+10,'B_new_life':2*60+10+20+10+4})
checks.append({'case':'R45 cost crossing','A_n5':100+5*20,'B_n5':80+5*30,'cross_n':2})
feasible=[(m,p) for m in [1,2,3] for p in [10,20,30] if m<=2 and p<=20 and m*p<=30];assert feasible==[(1,10),(1,20),(2,10)]
checks.append({'case':'R47 independent enumeration','before':feasible,'after_response':[(m,p) for m,p in feasible if 2*m+p/10>=4]})
checks.append({'case':'R49 force calculations','A_hold':8*2*.3,'B_hold':10*2*.3,'B_new_mu':10*2*.2,'k14_N':28,'k14_hold':5.6})
L=[[0,100],[40,0]];prior=[.5,.5]
def risk(p):return min(sum(l*q for l,q in zip(a,p)) for a in L)
def evsi(sens,spec):
 r=0;branches=[]
 for ly in [[sens,1-spec],[1-sens,spec]]:
  py=sum(a*b for a,b in zip(prior,ly));post=[a*b/py for a,b in zip(prior,ly)] if py else [0,0];v=risk(post);r+=py*v;branches.append({'p_signal':py,'posterior':post,'risk':v})
 return risk(prior)-r,branches
v,b=evsi(.8,.8);assert math.isclose(v,6);weak,_=evsi(.6,.6);assert math.isclose(weak,0)
checks.append({'case':'R52 independent Bayes branches','EVSI':v,'branches':b,'weak_EVSI':weak,'net':v-2-1})
# new sensitivity probes to ensure text interpretation depends on assumptions, not coding mistakes
checks.append({'case':'unseen R52 signal .7/.7','EVSI':evsi(.7,.7)[0],'interpretation':'posterior .7 below5/7, no action switch, zero value'})
checks.append({'case':'unseen R47 f threshold6','survivors':[(m,p) for m,p in feasible if 2*m+p/10>=6],'interpretation':'empty set calls research/relaxation authority, not hidden champion'})
checks.append({'case':'unseen R43 B lifetime4 years','reference_flow':math.ceil(10/4),'interpretation':'discrete replacement requires explicit service boundary; do not linear-fraction device without model'})
(dst/'独立复算记录.json').write_text(json.dumps({'source_manifest_sha256':hashlib.sha256((src/'manifest.json').read_bytes()).hexdigest(),'checks':checks,'scope':'independent arithmetic and source-file integrity; not complete method proof'},ensure_ascii=False,indent=2))
print('independent calculations complete',len(checks))
