# -*- coding: utf-8 -*-
from pathlib import Path
import copy,json,hashlib,shutil,cmath,math
O=Path(__file__).parent;ROOT=O.parents[3];B=ROOT/'02-研究/方法深化执行';C=O/'private-copies';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before={};nsmap={};runs=[]
for name,script in [('MD-055-WB03','教学检查.py'),('MD-056-WB04','教学复算.py'),('MD-057-WB05','教学检查.py'),('MD-058-WB06','教学复算.py'),('MD-059-WB07','教学检查.py')]:
 d=B/name;before.update({str(p):sha(p)for p in d.rglob('*')if p.is_file()});shutil.copytree(d,C/name,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'));p=C/name/script;ns={'__file__':str(p.resolve()),'__name__':'review'};exec(compile(p.read_text(),str(p),'exec'),ns);nsmap[name[-4:]]=ns;runs.append({'method':name,'checks':len(ns['cases']),'manifest_sha256':sha(d/'manifest.json')})
rows=[]
def probe(r,n,mut,operation=False):
 ns=nsmap[r];x=copy.deepcopy(ns['base'])
 if operation:x.update(branch='product_operation',goal='study availability of state for use',artifact_kind='control_research_record',control_proxy=copy.deepcopy(ns['proxy']))
 mut(x);fn=ns.get('calc')or ns['check']
 try:y=fn(x);err=None
 except Exception as e:y=None;err=str(e)
 rows.append({'method':r,'name':n,'out':y,'error':err});(O/(r+'-'+n+'.json')).write_text(json.dumps({'input':x,'out':y,'error':err},ensure_ascii=False,indent=2))
probe('WB03','erase-relations',lambda x:x.update(relations=[]));probe('WB03','substitute-field-validation',lambda x:x.update(validation_plan_context='lab'));probe('WB03','semantically-contradict-free-text',lambda x:x['domains'].update(DA='all goals already certified in cleanroom'))
probe('WB04','X-source-erased',lambda x:x['X'].update(need_id=None));probe('WB04','summed-independent-optima',lambda x:x.update(separate_optima_summed=True));probe('WB04','actual-evidence-injected',lambda x:x.update(actual_function_evidence='measured'))
probe('WB05','remove-necessary-auxiliary',lambda x:x.update(functions=[f for f in x['functions']if f['id']!='FS']));probe('WB05','claimed-takeover',lambda x:x.update(takeovers=[{'function_id':'FC','new_owner_role':'operator','evidence':'verified','user_burden':0}]))
probe('WB06','nonlinear-regime',lambda x:x.update(known_nonlinear_contact=True));probe('WB06','unbound-installation',lambda x:x.update(configuration='other'))
probe('WB07','fake-control-benefit',lambda x:x.update(product_operation_improved=True));probe('WB07','duplicate-sample-id',lambda x:x['control_proxy']['samples'][1].update(id='S1'),True);probe('WB07','NaN-time',lambda x:x['control_proxy'].update(now=float('nan')),True)
# independent harmonic response via complex impedance, not same hypot expression.
for r in ['WB04','WB06']:
 ns=nsmap[r];x=copy.deepcopy(ns['base']);v=ns['calc'](x)
 if r=='WB04':a=x['candidate'];e=x['excitation'];m,k,c,F,w=a['mass_kg'],a['stiffness_N_m'],a['damping_Ns_m'],e['force_N'],e['omega_rad_s'];actual=v['response_m']
 else:m,k,c,F,w=[x[k]for k in ['mass_kg','stiffness_N_m','damping_Ns_m','force_N','omega_rad_s']];actual=v['response_at_declared_excitation_m']
 assert math.isclose(abs(F/complex(k-m*w*w,c*w)),actual,rel_tol=1e-12)
assert all(sha(Path(p))==v for p,v in before.items());(O/'WB复核结果.json').write_text(json.dumps({'isolated_runs':runs,'probes':rows,'independent_complex_response_match':True,'original_bytes_unchanged':True,'source_scope':'selected article/author self-report/publisher introduction only; no full books certified'},ensure_ascii=False,indent=2));print(json.dumps(rows,ensure_ascii=False))
