from pathlib import Path
import shutil,runpy,copy,json,hashlib,re
P=Path(__file__).resolve().parent;R=P.parents[1];C=P/'隔离副本';C.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sp=C/'MD-001-R48/教学包';sp.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/'MD-001-R48/教学包/00-共享教学输入-v0.1.0.json',sp/'00-共享教学输入-v0.1.0.json')
checks=[];verified=[];sources=[]
mods={}
for n in ['MD-017-R19','MD-018-R20','MD-019-R21','MD-020-R22']:
 src=R/n;dst=C/n;shutil.copytree(src,dst,dirs_exist_ok=True,ignore=shutil.ignore_patterns('private-sources','__pycache__'))
 manifest=json.loads((src/'manifest.json').read_text())
 for x in manifest['files']:assert sha(src/x['path'])==x['sha256']
 verified.append({'package':n,'manifest_sha256':sha(src/'manifest.json'),'verified_files':len(manifest['files'])})
 meta=json.loads((src/'来源与主张.json').read_text())
 for s in meta['sources']:
  assert sha(src/s['raw_file'])==s['raw_sha256'];assert sha(src/s['text_file'])==s['text_sha256']
 for claim in meta['claims']:
  s=next(s for s in meta['sources']if s['id']==claim['source_id']);text=re.sub(r'\s+',' ',(src/s['text_file']).read_text());i=claim['text_anchor_start'];assert text[i:i+len(claim['short_anchor'])]==claim['short_anchor'];sources.append({'package':n,'claim':claim['id'],'source_hash_and_anchor':True})
 mods[n]=runpy.run_path(str(dst/'构建教学包.py'))
def probe(pkg,label,mut):
 a=mods[pkg];d=copy.deepcopy(a.get('data',a.get('base')));mut(d)
 try:r=a.get('check',a.get('route'))(d);state='accepted'
 except (ValueError,TypeError,KeyError)as e:r=str(e);state='rejected'
 checks.append({'package':pkg,'name':label,'actual':state,'output':r})
probe('MD-017-R19','unseen-graph-only-foreign-node',lambda d:d['variants'][0]['edges'].append(['alien','other','imaginary']))
probe('MD-017-R19','hard-pass-promotion',lambda d:d['variants'][0].update(declared_hard_state='pass'))
probe('MD-018-R20','no-ambiguity-does-not-confirm-whole',lambda d:d['additional_model_objects'][1].update(surface='different'))
probe('MD-018-R20','target-unknowns-erased',lambda d:d.update(unknowns=[]))
probe('MD-019-R21','unseen-direction-boolean',lambda d:d.update(technical_contradiction={**mods['MD-019-R21']['tc'],'THEN':{**mods['MD-019-R21']['tc']['THEN'],'direction':True}}))
probe('MD-019-R21','same-condition-drift',lambda d:d.update(technical_contradiction={**mods['MD-019-R21']['tc'],'BUT':{**mods['MD-019-R21']['tc']['BUT'],'condition':'OTHER'}}))
probe('MD-020-R22','unseen-cell-injection',lambda d:d['matrix'].update(cell='1:2'))
probe('MD-020-R22','unseen-matrix-version-claim',lambda d:d['matrix'].update(version='classical39'))
probe('MD-020-R22','unseen-zero-direction',lambda d:d['native_parameters']['P-SLIP'].update(direction=0))
(P/'实际复核结果.json').write_text(json.dumps({'manifests':verified,'source_claims':sources,'independent_probes':checks,'baseline_original_tests':{n:len(a.get('checks',a.get('cases',[])))for n,a in mods.items()},'scope':'fixed model/route and selected source review; not expert or target validation'},ensure_ascii=False,indent=2)+'\n')
print(len(sources),'source anchors;',len(checks),'probes')
