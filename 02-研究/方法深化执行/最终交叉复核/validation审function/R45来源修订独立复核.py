# -*- coding: utf-8 -*-
from pathlib import Path
import json,hashlib,shutil
O=Path(__file__).parent;ROOT=O.parents[3];D=ROOT/'02-研究/方法深化执行/修订版/MD-044-R45-v0.1.1';C=O/'private-copies/MD-044-R45-v0.1.1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before={str(p):sha(p)for p in D.rglob('*')if p.is_file()};m=json.loads((D/'manifest.json').read_text());assert all(sha(D/x['path'])==x['sha256']for x in m['files'])
s=json.loads((D/'来源与主张.json').read_text());p=s['primary_source'];raw=D/p['raw_file'];text=(D/p['text_file']).read_text();html=raw.read_text();assert sha(raw)==p['raw_sha256'];assert sha(D/p['text_file'])==p['text_sha256'];assert p['identity_checks']['title']in text;assert'Federal Highway Administration'in text and'CN110696008B'not in html
anchors=[]
for c in p['claims']:
 pos=text.find(c['anchor']);assert pos==c['offset'];anchors.append({'anchor':c['anchor'],'actual_offset':pos,'match':True})
old=ROOT/'02-研究/方法深化执行/MD-044-R45/private-sources/SAVE官方检索摘要.json';assert 'CN110696008B'in old.read_text();assert sha(old)==s['correction']['old_bad_sha256'];assert'主张已撤回'in(D/'研究说明.md').read_text()
shutil.copytree(D,C,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'));q=C/'教学复算.py';ns={'__file__':str(q.resolve()),'__name__':'review'};exec(compile(q.read_text(),str(q),'exec'),ns);v=ns['calc'](ns['base']);assert v['value_recommendation']is None and[r['total_cost_arithmetic_CU']for r in v['rows']]==[200,230]
assert all(sha(Path(p))==v for p,v in before.items());(O/'R45来源修订复核结果.json').write_text(json.dumps({'manifest_sha256':sha(D/'manifest.json'),'new_source_identity':'FHWA official VE Process and Job Plan body, not SAVE standard','patent_content_absent':True,'anchors':anchors,'old_error_identity_confirmed_and_retracted':True,'replayed_checks':len(ns['cases']),'CU_math':[200,230],'value_recommendation':None,'original_new_and_old_sources_not_modified':True,'scope':'selected body identity and bounded teaching review only'},ensure_ascii=False,indent=2));print('R45 source identity and10 replay checks verified')
