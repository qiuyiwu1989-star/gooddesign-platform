"""Bounded reproduction: NIST 32-row ceramics data; no physical experiment."""
from pathlib import Path
import hashlib,itertools,json,urllib.request
import numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent/'教学复算';OUT.mkdir(exist_ok=True)
URL='https://www.itl.nist.gov/div898/handbook/datasets/CERAMIC.DAT'
p=Path(__file__).resolve().parent/'教学复算/CERAMIC.DAT'
if not p.exists():p=OUT/'CERAMIC.DAT'
if not p.exists():
 with urllib.request.urlopen(urllib.request.Request(URL,headers={"User-Agent":"Mozilla/5.0"}),timeout=20) as f:p.write_bytes(f.read())
rows=[]
for line in p.read_text().splitlines():
 try:r=[float(x) for x in line.split()]
 except ValueError:continue
 if len(r)==7:rows.append(r)
a=np.array(rows);assert a.shape==(32,7)
x,y,order=a[:,:5],a[:,5],a[:,6]
assert set(x.ravel())=={-1.,1.} and len(set(map(tuple,x)))==32
assert set(order)==set(range(1,33))
terms=[c for k in range(4) for c in itertools.combinations(range(5),k)]
X=np.column_stack([np.prod(x[:,t],axis=1) if t else np.ones(32) for t in terms])
beta,_,rank,_=np.linalg.lstsq(X,y,rcond=None);res=y-X@beta
df=len(y)-rank;sse=float(res@res);rmse=float(np.sqrt(sse/df));r2=1-sse/float(((y-y.mean())**2).sum())
assert rank==26 and df==6
assert abs(y.mean()-546.8959)<.0001 and abs(rmse-17.81632)<.00002
assert abs(r2-.995127)<.000001
full=np.column_stack([np.prod(x[:,t],axis=1) if t else np.ones(32) for k in range(6) for t in itertools.combinations(range(5),k)])
fullrank=int(np.linalg.matrix_rank(full));assert fullrank==32
out={'scope':'public_modified_dataset_bounded_recalculation_not_new_experiment','source_url':URL,'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'rows':32,'response':'published mean strength per design point; 15 underlying repetitions unavailable individually','model':'coded ±1 factors; intercept and all interactions up to order 3','rank':int(rank),'residual_df':int(df),'mean_response':float(y.mean()),'r_squared':r2,'rmse':rmse,'residuals_are_pure_error':False,'error_assumption':'order-4/5 interactions pooled as error; not independent replicate error','coefficients':[{'term':'intercept' if not t else '*'.join('X'+str(i+1)for i in t),'coefficient':float(v),'effect_difference':None if not t else float(2*v)} for t,v in zip(terms,beta)],'residuals':[{'standard_row':i+1,'randomized_order':int(o),'fitted':float(f),'residual':float(r)}for i,(o,f,r)in enumerate(zip(order,X@beta,res))],'negative_case':{'saturated_model_rank':fullrank,'residual_df':32-fullrank,'rmse':None,'reason':'zero residual degrees of freedom: cannot estimate residual variance despite perfect interpolation'},'reproduced':'first 26-parameter raw-response model only','not_reproduced':['Box-Cox transformed final model','raw individual repeated measurements','new confirmation experiment'],'engineering_validated':False}
(OUT/'R38-NIST复算.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
print(json.dumps({k:out[k]for k in ['rows','rank','residual_df','mean_response','r_squared','rmse','negative_case']},ensure_ascii=False))
