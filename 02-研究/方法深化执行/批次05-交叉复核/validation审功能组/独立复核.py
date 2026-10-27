# -*- coding: utf-8 -*-
from pathlib import Path
import copy,json,hashlib,shutil
O=Path(__file__).parent;ROOT=O.parents[3];B=ROOT/'02-研究/方法深化执行';C=O/'private-copies';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before={};nsmap={};replays=[]
for name,script in [('MD-042-R41','教学检查.py'),('MD-043-R43','教学复算.py'),('MD-044-R45','教学复算.py'),('MD-045-R46','教学核查.py')]:
 d=B/name;before.update({str(p):sha(p)for p in d.rglob('*')if p.is_file()});shutil.copytree(d,C/name,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'));p=C/name/script;ns={'__file__':str(p.resolve()),'__name__':'review'};exec(compile(p.read_text(),str(p),'exec'),ns);nsmap[name[-3:]]=ns;replays.append({'method':name,'count':len(ns['cases'])})
rows=[]
def probe(r,name,mut):
 ns=nsmap[r];x=copy.deepcopy(ns['base']);mut(x);fn=ns.get('calc')or ns['check']
 try:y=fn(x);err=None
 except Exception as e:y=None;err=str(e)
 row={'method':r,'name':name,'output':y,'error':err};rows.append(row);(O/(r+'-'+name+'.json')).write_text(json.dumps({'input':x,**row},ensure_ascii=False,indent=2))
probe('R41','erase-information-tier',lambda x:[h.pop('information_review')for h in x['hazards']]);probe('R41','fake-safety-approval',lambda x:x.update(safety_approved=True))
probe('R43','empty-alternatives',lambda x:x.update(alternatives=[]));probe('R43','duplicate-alternative-id',lambda x:x['alternatives'][1].update(id='A'));probe('R43','NaN-lifetime',lambda x:x['alternatives'][0].update(service_life_years=float('nan')))
probe('R45','delete-necessary-function',lambda x:x.update(necessary_functions=[]));probe('R45','fake-currency',lambda x:x.update(cost_unit='CNY'));probe('R45','empty-alternatives',lambda x:x.update(alternatives=[]))
probe('R46','invent-query-id',lambda x:x.update(query_ids=['NO']));probe('R46','duplicate-query-id',lambda x:x.update(query_ids=['Q01','Q01']));probe('R46','falsify-official-status',lambda x:x['documents'][0].update(legal_status='active_verified'))
# Separate independent arithmetic, not just author tests.
r43=nsmap['R43']['calc'](nsmap['R43']['base']);assert [r['total_constructed_BU']for r in r43['rows']]==[200,300]
r45=nsmap['R45']['calc'](nsmap['R45']['base']);assert [r['total_cost_arithmetic_CU']for r in r45['rows']]==[200,230]
r46=nsmap['R46']['check'](nsmap['R46']['base']);assert r46['group_count']==2 and r46['selected_publications']==3
assert all(sha(Path(p))==v for p,v in before.items());(O/'复核结果.json').write_text(json.dumps({'author_replays':replays,'independent_probes':rows,'R43_independent_BU':[200,300],'R45_independent_CU':[200,230],'R46_groups':r46['domestic_application_groups'],'original_bytes_unchanged':True,'scope':'limited independent agent audit, not legal/safety/environmental certification'},ensure_ascii=False,indent=2));print(json.dumps(rows,ensure_ascii=False))
