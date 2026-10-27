"""Original Q4 quadrature implementation; not copied DTU top.m. Density-filter SIMP variant.
All units normalized. This is not a final CAD, manufacturing or safety strength assessment.
"""
from pathlib import Path
import numpy as np,json,math
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve
P=Path(__file__).resolve().parent

def element(hx,hy,nu=.3):
 D=np.array([[1,nu,0],[nu,1,0],[0,0,(1-nu)/2]])/(1-nu*nu);K=np.zeros((8,8));Bs=[]
 for r in [-1/math.sqrt(3),1/math.sqrt(3)]:
  for s in [-1/math.sqrt(3),1/math.sqrt(3)]:
   dx=np.array([-(1-s),1-s,1+s,-(1+s)])/(2*hx);dy=np.array([-(1-r),-(1+r),1+r,1-r])/(2*hy)
   B=np.zeros((3,8));B[0,0::2]=dx;B[1,1::2]=dy;B[2,0::2]=dy;B[2,1::2]=dx;K+=B.T@D@B*hx*hy/4;Bs.append(B)
 return K,D,Bs

def setup(cfg):
 if cfg.get('mode')!='normalized_constructed_education':raise ValueError('not engineering input')
 if any(cfg.get(k)!=v for k,v in {'E0':1.,'Emin':1e-6,'nu':.3,'penalty':3.,'thickness':1.,'load_amplitude':-1.}.items()):raise ValueError('unsupported constitutive/load constants')
 if cfg.get('load_case')not in ['right_middle_down','right_top_down']:raise ValueError('unsupported load case')
 if any(type(cfg.get(k))is not int or cfg[k]<2 for k in ['nx','ny']):raise ValueError('invalid mesh')
 if any(type(cfg.get(k))not in (int,float)or not math.isfinite(cfg[k])or cfg[k]<=0 for k in ['L','H','filter_radius','volume_limit']):raise ValueError('invalid dimension/volume/filter')
 if cfg['boundary']!='left_edge_clamped':raise ValueError('unverified support configuration')
 if not 0<cfg['volume_limit']<1 or cfg['filter_radius']<=0:raise ValueError('invalid volume/filter')
 nx,ny=cfg['nx'],cfg['ny'];L,H=cfg['L'],cfg['H'];hx,hy=L/nx,H/ny;ke,D,Bs=element(hx,hy);ed=[];cent=[]
 for y in range(ny):
  for x in range(nx):
   ns=[y*(nx+1)+x,y*(nx+1)+x+1,(y+1)*(nx+1)+x+1,(y+1)*(nx+1)+x];ed.append([j for n in ns for j in [2*n,2*n+1]]);cent.append([(x+.5)*hx,(y+.5)*hy])
 ed=np.array(ed);cent=np.array(cent);N=nx*ny;ndof=2*(nx+1)*(ny+1);F=np.zeros(ndof);yn=ny//2 if cfg['load_case']=='right_middle_down'else ny;F[2*(yn*(nx+1)+nx)+1]=-1
 fixed=np.array([j for y in range(ny+1)for j in [2*y*(nx+1),2*y*(nx+1)+1]]);free=np.setdiff1d(np.arange(ndof),fixed)
 dist=np.linalg.norm(cent[:,None,:]-cent[None,:,:],axis=2);W=np.maximum(0,cfg['filter_radius']-dist);W/=W.sum(axis=1)[:,None]
 ii=np.repeat(ed,8,axis=1).ravel();jj=np.tile(ed,(1,8)).ravel()
 return ke,D,Bs,ed,F,free,W,ii,jj

def solve(cfg,maxiter=160):
 ke,D,Bs,ed,F,free,W,ii,jj=setup(cfg);N=len(ed);x=np.full(N,cfg['volume_limit']);emin=1e-6;p=3.;history=[];dv=W.sum(axis=0)/N
 def fe(xp):
  mod=emin+(1-emin)*xp**p;K=coo_matrix((np.einsum('i,jk->ijk',mod,ke).ravel(),(ii,jj)),shape=(len(F),len(F))).tocsr();K=(K+K.T)*.5;u=np.zeros(len(F));u[free]=spsolve(K[free][:,free],F[free]);ce=np.einsum('ij,jk,ik->i',u[ed],ke,u[ed]);comp=float(F@u);res=np.linalg.norm((K@u-F)[free])/np.linalg.norm(F[free]);grad=np.einsum('ij,j->i',W.T,(-p*(1-emin)*xp**(p-1)*ce));return comp,float(res),grad,u
 for it in range(maxiter):
  xp=np.einsum('ij,j->i',W,x);comp,res,grad,u=fe(xp);lo,hi=1e-12,1e8
  for _ in range(70):
   mid=(lo+hi)/2;trial=np.maximum(.001,np.maximum(x-.1,np.minimum(1,np.minimum(x+.1,x*np.sqrt(np.maximum(0,-grad/(mid*dv)))))))
   if np.mean(np.einsum('ij,j->i',W,trial))>cfg['volume_limit']:lo=mid
   else:hi=mid
  change=float(np.max(np.abs(trial-x)));history.append({'iteration':it+1,'compliance':comp,'mean_physical_density':float(xp.mean()),'relative_free_equilibrium_residual':res,'max_design_change':change});x=trial
  if change<.005:break
 xp=np.einsum('ij,j->i',W,x);comp,res,grad,u=fe(xp)
 # Finite difference checks the implemented physical density chain, not the original 99-line sensitivity filter.
 idx=N//2;eps=1e-5;xx=x.copy();xx[idx]+=eps;cp=fe(np.einsum('ij,j->i',W,xx))[0];xx[idx]-=2*eps;cm=fe(np.einsum('ij,j->i',W,xx))[0];fd=(cp-cm)/(2*eps);gerr=abs(fd-grad[idx])/max(1,abs(fd))
 binary=(xp>=.5).astype(float);bc,br,_,bu=fe(binary);stress=[]
 for e in range(N):
  if binary[e]:
   for B in Bs:
    sx,sy,tau=D@B@bu[ed[e]];stress.append(math.sqrt(sx*sx-sx*sy+sy*sy+3*tau*tau))
 return {'input':cfg,'formulation':'platform-density-filter-SIMP-volume-inequality-v0.1.0','history':history,'final':{'iterations':len(history),'converged_design_change':history[-1]['max_design_change']<.005,'compliance':comp,'mean_physical_density':float(xp.mean()),'volume_limit_residual':float(xp.mean()-cfg['volume_limit']),'free_equilibrium_relative_residual':res,'selected_derivative_relative_error':float(gerr),'last_max_change':history[-1]['max_design_change']},'physical_density':xp.reshape(cfg['ny'],cfg['nx']).tolist(),'thresholded_reanalysis':{'threshold':.5,'volume_fraction':float(binary.mean()),'compliance':bc,'equilibrium_relative_residual':br,'max_gauss_von_mises_normalized':max(stress)if stress else None,'strength_pass':None,'reason':'no real material allowable/load/fatigue evidence; ersatz residual material remains; threshold geometry is not CAD or independent engineering solver'},'engineering_validated':False}
base={'id':'R35-CANTILEVER-TEACH-001','mode':'normalized_constructed_education','nx':20,'ny':8,'L':2.,'H':.8,'boundary':'left_edge_clamped','load_case':'right_middle_down','volume_limit':.45,'filter_radius':.18,'E0':1.,'Emin':1e-6,'nu':.3,'penalty':3.,'thickness':1.,'load_amplitude':-1.,'numerical_origin':'normalized educational inputs; no material/robot meaning','boundary_dofs':'both translations at every left-edge node','excluded':['stress constraint','fatigue','buckling','manufacturing','multiple real loads']}
if __name__=='__main__':
 cases=[]
 for label,patch in [('baseline',{}),('mesh_refined',{'nx':30,'ny':12}),('filter_changed',{'filter_radius':.26}),('other_context_corner_load',{'id':'DISPLAY-BRACKET-TEACH','load_case':'right_top_down'})]:
  cfg={**base,**patch};r=solve(cfg);assert r['final']['free_equilibrium_relative_residual']<1e-6;assert abs(r['final']['volume_limit_residual'])<1e-5;assert r['final']['selected_derivative_relative_error']<1e-3;cases.append({'label':label,'result':r});print(label,r['final'])
 checks=[]
 for label,patch in [('missing-support',{'boundary':None}),('zero-volume',{'volume_limit':0}),('no-filter',{'filter_radius':0}),('claim-real-part',{'mode':'validated_part'}),('ignored-material-injection',{'E0':200e9}),('unknown-load-case',{'load_case':'real_robot_load'})]:
  try:setup({**base,**patch});raise AssertionError(label+' accepted')
  except ValueError as e:checks.append({'name':label,'actual':'rejected','reason':str(e)})
 (P/'教学包/01-固定模型输入.json').write_text(json.dumps(base,ensure_ascii=False,indent=2)+'\n');(P/'教学包/02-迭代敏感性与几何重分析.json').write_text(json.dumps({'cases':cases,'checks':checks,'claim_boundary':'actual numerical runs, not CAD strength or manufacturing validation'},ensure_ascii=False,indent=2)+'\n')
