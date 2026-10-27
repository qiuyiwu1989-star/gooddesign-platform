# -*- coding: utf-8 -*-
from pathlib import Path
import numpy as np,json
D=Path(__file__).resolve().parent
x=np.repeat(np.arange(1,21),2);amp=np.where(x<=10,0.01,0.3);y=10*x+amp*np.tile([-1,1],20);X=np.column_stack([np.ones(len(x)),x]);b=np.linalg.lstsq(X,y,rcond=None)[0];r=y-X@b;r2=1-float(r@r)/float(((y-y.mean())**2).sum());lo=float(np.mean(r[x<=10]**2));hi=float(np.mean(r[x>10]**2));assert r2>.99 and hi/lo>100
(D/'教学包/05-高R平方不保证方差齐性.json').write_text(json.dumps({'origin':'independent_synthetic_counterexample_not_NIST_observation','x':x.tolist(),'y':y.tolist(),'r_squared':r2,'residual_mse_low_group':lo,'residual_mse_high_group':hi,'ratio':hi/lo,'actual_conclusion':'high R2 coexists with declared heteroscedastic residual pattern','not_claimed':'formal variance test or NIST data heteroscedasticity finding'},ensure_ascii=False,indent=2))
print('independent synthetic heteroscedastic counterexample passed')
