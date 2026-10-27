# -*- coding: utf-8 -*-
from pathlib import Path
import copy,json,hashlib,shutil
O=Path(__file__).parent;ROOT=O.parents[3];B=ROOT/'02-研究/方法深化执行/修订版';C=O/'private-copies';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before={};nsmap={};replays=[]
for name in ['MD-021-R23-v0.1.1','MD-023-R25-v0.1.1','MD-025-R27-v0.1.1','MD-033-R33-v0.1.1','MD-034-R34-v0.1.1']:
 d=B/name;before.update({str(p):sha(p)for p in d.rglob('*')if p.is_file()});shutil.copytree(d,C/name,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'));p=C/name/('复核教学.py'if'R27'in name else'复算教学.py');ns={'__file__':str(p.resolve()),'__name__':'review'};exec(compile(p.read_text(),str(p),'exec'),ns);nsmap[name[7:10]]=ns;replays.append({'method':name,'count':len(ns['cases']),'manifest_sha256':sha(d/'manifest.json')})
rows=[]
def probe(r,n,mut):
 ns=nsmap[r];x=copy.deepcopy(ns['base']);mut(x);fn=ns.get('assess')or ns.get('route')or ns['calc']
 try:y=fn(x);err=None
 except Exception as e:y=None;err=str(e)
 rows.append({'method':r,'name':n,'out':y,'error':err});(O/(r+'-'+n+'.json')).write_text(json.dumps({'input':x,'out':y,'error':err},ensure_ascii=False,indent=2))
probe('R23','old-arbitrary-directions',lambda x:[a.update(direction=v)for a,v in zip(x['demands'],['banana','orange'])]);probe('R23','old-negative-switch',lambda x:x.update(switch_time_s=-100));probe('R23','old-reversed-interval',lambda x:x['demands'][0].update(interval_s=[4,0]));probe('R23','new-empty-object',lambda x:[a.update(object='')for a in x['demands']])
probe('R25','old-empty-role',lambda x:x['elements'].update(S1=''));probe('R25','old-nonmapping',lambda x:x.update(elements=['bad']))
probe('R27','old-fake-query',lambda x:x.update(query_log=['NO']));probe('R27','old-erased-unknowns',lambda x:x.update(target_properties={}));probe('R27','old-numeric-latex',lambda x:x['target_properties'].update(viscosity_Pa_s=.1));probe('R27','new-empty-differences-content',lambda x:x.update(transfer_differences=['']))
probe('R33','old-NaN-temperature',lambda x:x.update(max_service_C=float('nan')));probe('R33','new-bool-temperature',lambda x:x.update(max_service_C=True))
probe('R34','old-negative-qty',lambda x:x['bom'][0].update(qty=-1));probe('R34','old-string-service',lambda x:x.update(service_requires_replaceable_seal='false'));probe('R34','new-duplicate-BOM-ID',lambda x:x['bom'][1].update(id=x['bom'][0]['id']))
assert all(sha(Path(p))==v for p,v in before.items());(O/'修订复核结果.json').write_text(json.dumps({'replayed':replays,'probes':rows,'original_bytes_unchanged':True,'scope':'independent bounded audit, not expert certification'},ensure_ascii=False,indent=2));print(json.dumps(rows,ensure_ascii=False))
