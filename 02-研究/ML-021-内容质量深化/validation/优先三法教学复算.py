# -*- coding: utf-8 -*-
from pathlib import Path
import json,itertools,math
import numpy as np
P=Path(__file__).parent;D=P/'教学附件';D.mkdir(exist_ok=True)
def put(n,x):(D/n).write_text(json.dumps(x,ensure_ascii=False,indent=2))
# Independently constructed CCD, not NIST chemical or ceramic measurements.
pts=list(itertools.product([-1.,1.],repeat=2))+[(-1.,0.),(1.,0.),(0.,-1.),(0.,1.)]+[(0.,0.)]*5
noise=[0.]*8+[-.2,-.1,0.,.1,.2]
def mean(x,z):return 10+2*x-2*z-2*x*x-2*z*z
X=np.array([[1,x,z,x*z,x*x,z*z]for x,z in pts]);Y=np.array([mean(x,z)+e for (x,z),e in zip(pts,noise)]);coef=np.linalg.lstsq(X,Y,rcond=None)[0];res=Y-X@coef
sspe=sum((v-10)**2 for v in Y[-5:]);ssres=float(res@res);B=np.array([[coef[4],coef[3]/2],[coef[3]/2,coef[5]]]);stat=-.5*np.linalg.solve(B,coef[1:3]);pred=float(np.array([1,*stat,stat[0]*stat[1],stat[0]**2,stat[1]**2])@coef)
assert np.linalg.matrix_rank(X)==6 and np.allclose(stat,[.5,-.5])and math.isclose(pred,11)and math.isclose(sspe,.1,abs_tol=1e-12)
put('R38-构造CCD与诊断.json',{'identity':'constructed teaching data, not actual experiments','design':'face_centered_CCD_not_rotatable','factors':{'x1':'(pressure_kPa-20)/5','x2':'(speed_mm_s-50)/10'},'rows':[{'x1':x,'x2':z,'y':float(y)}for(x,z),y in zip(pts,Y)],'coef_order':['intercept','x1','x2','x1x2','x1_squared','x2_squared'],'coefficients':coef.tolist(),'rank':int(np.linalg.matrix_rank(X)),'residual_df':7,'pure_error_SS':sspe,'pure_error_df':4,'lack_of_fit_SS':max(0,ssres-sspe),'lack_of_fit_df':3,'stationary_coded':stat.tolist(),'stationary_physical':{'pressure_kPa':22.5,'speed_mm_s':45},'Hessian_eigenvalues':np.linalg.eigvalsh(2*B).tolist(),'predicted_y':pred,'constructed_independent_confirmation':[10.9,11,11.1],'confirmation_mean':11.,'interpretation':'choose proposal for confirmation within assumed safe cube; not field optimum or proof of adequacy'})
r49=[]
for cid,k,mu in [('A',8,.3),('B',10,.3),('B-reinterpreted',10,.2),('C-overstiff',14,.2)]:
 N=k*2;holding=mu*N;passes=holding>=5 and N<=22;r49.append({'structure':cid,'k_N_mm':k,'x_mm':2,'mu_assumed':mu,'N_N':N,'holding_N':holding,'Be_hold_min_N':5,'Be_contact_max_N':22,'within_toy_model':passes})
assert not r49[0]['within_toy_model']and r49[1]['within_toy_model']and not r49[2]['within_toy_model']and not r49[3]['within_toy_model']
put('R49-构造FBS设计记录.json',{'identity':'independent synthetic mechanism not real tree/contact study','records':r49,'first_decision':'B for conditional model study','reformulation':'at mu=.2 increasing k to14 breaks N<=22, investigate contact mechanism/assumptions not relax requirement silently','actual_experiment':False})
def voi(p,lik,cost=2,delay=1):
 prior=[p,1-p];loss={'A':[0.,100.],'B':[40.,0.]};risks={a:sum(v*l for v,l in zip(prior,ll))for a,ll in loss.items()};base=min(risks.values());perfect=0.;branches=[];after=0
 for name,L in [('positive',lik),('negative',[1-v for v in lik])]:
  joint=[v*l for v,l in zip(prior,L)];prob=sum(joint)
  if not prob:continue
  posterior=[v/prob for v in joint];rr={a:sum(v*l for v,l in zip(posterior,ll))for a,ll in loss.items()};a=min(rr,key=rr.get);after+=prob*rr[a];branches.append({'signal':name,'probability':prob,'posterior_good':posterior[0],'risks':rr,'action':a})
 return {'prior_good':p,'likelihood_positive_given_good_bad':lik,'current_risks':risks,'branches':branches,'risk_after_sample':after,'EVPI':base-perfect,'EVSI':base-after,'net_value':base-after-cost-delay}
vs=[voi(.5,[.8,.2]),voi(.5,[.6,.4]),voi(.5,[.5,.5]),voi(.5,[1,0]),voi(.2,[.8,.2]),voi(.8,[.8,.2])];assert math.isclose(vs[0]['EVSI'],6)and math.isclose(vs[1]['EVSI'],0,abs_tol=1e-12)
put('R52-行动阈值与信息结构复算.json',{'identity':'all probabilities/losses synthetic; no client estimates','action_switch_good_probability':5/7,'scenarios':vs})
print('R38 rank/curvature/LOF decomposition, R49 decisions and R52 action-dependent information value computed')
