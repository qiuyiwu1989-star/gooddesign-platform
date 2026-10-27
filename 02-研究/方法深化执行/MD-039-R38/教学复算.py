# -*- coding: utf-8 -*-
from pathlib import Path
import json,hashlib,itertools,copy
import numpy as np
D=Path(__file__).resolve().parent;P=D/'教学包';P.mkdir(exist_ok=True)
def put(n,x):(P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False))
DATA=D/'private-sources/CERAMIC.dat';rows=[]
for line in DATA.read_text().splitlines():
 try:r=[float(x)for x in line.split()]
 except ValueError:continue
 if len(r)==7:rows.append(r)
assert len(rows)==32
base={'source':'NIST CERAMIC.DAT modified illustrative dataset','source_sha256':hashlib.sha256(DATA.read_bytes()).hexdigest(),'rows':rows,'response':'mean strength over 15 repetitions; individual raw responses unavailable','model_order':3,'claim_pure_error':False,'claim_curvature':False,'confirmation_results':[],'transfer_to_tapping':False}
def check(i):
 if i['source']!=base['source']or i['source_sha256']!=base['source_sha256']or i['response']!=base['response']:raise ValueError('source_binding')
 if i['claim_pure_error']or i['claim_curvature']or i['confirmation_results']or i['transfer_to_tapping']:raise ValueError('unsupported_error_curvature_or_confirmation')
 if i['model_order']not in[3,5]or type(i['model_order'])is not int:raise ValueError('unsupported_order')
 a=np.array(i['rows'],dtype=float)
 if a.shape!=(32,7)or not np.isfinite(a).all():raise ValueError('shape_or_finite')
 if i['rows']!=rows:raise ValueError('frozen_source_row_changed')
 x=a[:,:5];y=a[:,5];order=a[:,6]
 if len(set(map(tuple,x)))!=32 or set(order)!=set(range(1,33)):raise ValueError('design_or_randomization_identity')
 terms=[c for k in range(i['model_order']+1)for c in itertools.combinations(range(5),k)]
 X=np.column_stack([np.prod(x[:,t],axis=1)if t else np.ones(32)for t in terms]);beta,_,rank,_=np.linalg.lstsq(X,y,rcond=None);fitted=X@beta;res=y-fitted;df=len(y)-rank;sse=float(res@res)
 std=None if df==0 else float(np.sqrt(sse/df));r2=1-sse/float(((y-y.mean())**2).sum())
 groups={str(int(v)):float(np.mean(res[x[:,3]==v]**2))for v in[-1,1]}
 return {'rank':int(rank),'residual_df':int(df),'r_squared':r2,'residual_rmse':std,'coefficients':[{'term':'intercept'if not t else '*'.join('X'+str(v+1)for v in t),'coefficient':float(v),'effect':None if not t else float(2*v)}for t,v in zip(terms,beta)],'residuals':[{'standard_row':k+1,'random_order':int(o),'predicted':float(f),'residual':float(r)}for k,(o,f,r)in enumerate(zip(order,fitted,res))],'residual_mean_square_by_direction':groups,'randomization':'published order is a permutation; actual execution not re-observed','pure_error_estimable_from_these_rows':False,'error_basis':'pooled omitted order4/5 effects, not separately estimated replicate noise'if df else'zero df: no residual variance estimate','curvature_estimable':False,'independent_confirmation':False,'engineering_validated':False}
put('01-公开输入及来源绑定.json',base);out=check(base);assert out['rank']==26 and out['residual_df']==6 and abs(out['residual_rmse']-17.81632)<2e-5;put('02-模型系数残差与误差界限.json',out)
cases=[]
def t(name,kind,mut,expected):
 q=copy.deepcopy(base);mut(q)
 try:o=check(q);state='no_residual_df'if o['residual_df']==0 else'accepted'
 except(ValueError,KeyError,TypeError)as e:o={'error':str(e)};state='rejected'
 cases.append({'name':name,'class':kind,'input':q,'summary':{k:v for k,v in o.items()if k not in['coefficients','residuals']},'actual':state,'expected':expected,'pass':state==expected})
t('normal','正常',lambda x:None,'accepted');t('saturated','边界',lambda x:x.update(model_order=5),'no_residual_df');t('missing_row','缺材料',lambda x:x['rows'].pop(),'rejected');t('call_residual_pure_error','冲突',lambda x:x.update(claim_pure_error=True),'rejected');t('infer_curvature','不适用',lambda x:x.update(claim_curvature=True),'rejected');t('invent_confirmation','冲突',lambda x:x['confirmation_results'].append('passed'),'rejected');t('random_order_drift','冲突',lambda x:x['rows'][0].__setitem__(6,1),'rejected');t('transfer_parameters_to_tree','不适用',lambda x:x.update(transfer_to_tapping=True),'rejected')
assert all(x['pass']for x in cases);put('03-实际检查.json',cases)
put('04-迁移与确认计划.json',{'context':'tapping research contact/relative movement study','actual_data':[],'proposed_factors':['bounded test-fixture contact setting','relative movement setting'],'noise_to_block_or_randomize':['surface surrogate batch','tool wear/order'],'required':['safe test envelope','raw replicates','randomized run order with seed recorded','center points if quantitative curvature is in question','independent confirmation under declared configuration'],'decision_rule':'do not transfer ceramic coefficients; stop if safety or measurement capability unresolved','scope':'desk experimental planning only'})
print(json.dumps({'checks':8,'rank':out['rank'],'residual_df':out['residual_df'],'r_squared':out['r_squared'],'rmse':out['residual_rmse']}))
