# -*- coding: utf-8 -*-
from pathlib import Path
import copy,json,hashlib,shutil,subprocess,sys
O=Path(__file__).parent;ROOT=O.parents[3];B=ROOT/'02-研究/方法深化执行';C=O/'private-copies';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
nsmap={};replays=[];finger={}
for n in ['MD-021-R23','MD-022-R24','MD-023-R25','MD-024-R26','MD-025-R27']:
 d=B/n;finger.update({str(p):sha(p)for p in d.rglob('*')if p.is_file()and'private-sources'not in p.parts});shutil.copytree(d,C/n,dirs_exist_ok=True,ignore=shutil.ignore_patterns('private-sources','__pycache__'))
 p=C/n/('复核教学.py'if n.endswith('R27')else'复算教学.py');ns={'__name__':'independent_review','__file__':str(p.resolve())};exec(compile(p.read_text(),str(p),'exec'),ns);nsmap[n[-3:]]=ns
 manifest=json.loads((d/'manifest.json').read_text());assert all(sha(d/x['path'])==x['sha256']for x in manifest['files'])
 replays.append({'method':n,'isolated_replay':'passed'})
rows=[]
def probe(r,name,mut):
 ns=nsmap[r];x=copy.deepcopy(ns['base']);mut(x);fn=ns.get('assess')or ns.get('route')or ns['check']
 try:y=fn(x);err=None
 except(Exception)as e:y=None;err=str(e)
 row={'method':r,'name':name,'output':y,'error':err};rows.append(row);(O/(r+'-'+name+'.json')).write_text(json.dumps({'input':x,**row},ensure_ascii=False,indent=2))
probe('R23','arbitrary-directions',lambda x:[a.update(direction=b)for a,b in zip(x['demands'],['banana','orange'])])
probe('R23','negative-switch-time',lambda x:x.update(switch_time_s=-100))
probe('R23','reversed-interval',lambda x:x['demands'][0].update(interval_s=[4,0]))
probe('R24','negative-mass',lambda x:x.update(mass_kg=-1))
probe('R24','NaN-budget',lambda x:x.update(efficiency=float('nan')))
probe('R25','blank-existing-role',lambda x:x['elements'].update(S1=''))
probe('R25','nonrole-element',lambda x:x.update(elements=['unrelated-item']))
probe('R26','duplicate-function-declared',lambda x:x['original_functions'].append(copy.deepcopy(x['original_functions'][0])))
probe('R26','invent-validation',lambda x:x['redistribution'][0].update(engineering_validated=True))
probe('R27','erase-target-unknown-registry',lambda x:x.update(target_properties={}))
probe('R27','fictitious-query-id',lambda x:x.update(query_log=['NO_SUCH_QUERY']))
probe('R27','caller-numeric-latex',lambda x:x['target_properties'].update(viscosity_Pa_s=.1))
assert all(sha(Path(p))==s for p,s in finger.items())
(O/'复核结果.json').write_text(json.dumps({'isolated_replays':replays,'independent_probes':rows,'source_packages_unchanged':True,'scope':'fixed teaching and declared metadata only; not expert certification'},ensure_ascii=False,indent=2));print(json.dumps(rows,ensure_ascii=False))
