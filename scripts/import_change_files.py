# coding: utf-8
from pathlib import Path
import sys,json,urllib.request
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));import project_pipeline as pipe
p=pipe.project(pipe.LIB,'2025-00');case=ROOT/'04-知识库/标杆案例/2025-00-嫦娥钻取采样';d=pipe.load(case/'档案数据.json')
with pipe.lock(pipe.LIB):
 pipe.save(p/'资料关联.json',dict(source_titles={s['url']:s['title'] for s in d['sources']}))
 for s in d['sources']:
  content=(case/'来源卡'/(s['id']+'.md')).read_bytes();target=pipe.INBOX/'2025-00'/('source-note-'+s['id']+'.md');origin=dict(kind='source_reference',filename=s['id']+'-'+s['title']+'-来源说明.md',url=s['url'],canonical_source_id=s['id'],note='来源说明与引用索引，非下载原文或全文')
  pipe.save(target.with_name(target.name+'.origin.json'),origin);target.write_bytes(content);pipe.ingest(p,target,origin)
# Real URL tasks are visible in the same backend; use the existing already-downloaded originals where possible.
base='http://127.0.0.1:8776';token=json.load(urllib.request.urlopen(base+'/api/projects'))['token'];jobs=[]
existing={x.get('origin',{}).get('url')for x in pipe.state(p)['sources'].values()if x.get('origin',{}).get('kind')!='source_reference'}
for s in d['sources']:
 if s['url']in existing or s['id']in ['S09','S23']:continue
 req=urllib.request.Request(base+'/api/fetch?project=2025-00',data=json.dumps({'url':s['url']}).encode(),headers={'Origin':base,'X-CSRF-Token':token,'Content-Type':'application/json'},method='POST')
 try:jobs.append(json.load(urllib.request.urlopen(req,timeout=15)))
 except Exception as e:print(s['id'],type(e).__name__,str(e)[:160])
(ROOT/'tmp').mkdir(exist_ok=True)
print('source_notes',len(d['sources']),'network_jobs',len(jobs));(ROOT/'tmp/admin033-jobids.json').write_text(json.dumps(jobs,ensure_ascii=False,indent=2))
